import 'dart:math' as math;
import 'dart:typed_data';

import 'package:image/image.dart' as img;

/// On-device resistor colour-band decoder.
///
/// Pure-Dart port of `backend/app/vision/resistor.py`: isolate the resistor
/// body via a saturation mask, sample colours along its long axis, classify
/// bands against the standard colour code, and compute the value.
class ResistorReading {
  final double valueOhms;
  final String display;
  final List<String> bands;
  final double? tolerance;
  final double confidence;

  const ResistorReading({
    required this.valueOhms,
    required this.display,
    required this.bands,
    required this.tolerance,
    required this.confidence,
  });
}

class _ColorDef {
  final int? digit;
  final int? mult;
  final double? tol;
  const _ColorDef({this.digit, this.mult, this.tol});
}

// Standard resistor colour code.
const Map<String, _ColorDef> _colorCode = {
  'black': _ColorDef(digit: 0, mult: 0),
  'brown': _ColorDef(digit: 1, mult: 1, tol: 1.0),
  'red': _ColorDef(digit: 2, mult: 2, tol: 2.0),
  'orange': _ColorDef(digit: 3, mult: 3),
  'yellow': _ColorDef(digit: 4, mult: 4),
  'green': _ColorDef(digit: 5, mult: 5, tol: 0.5),
  'blue': _ColorDef(digit: 6, mult: 6, tol: 0.25),
  'violet': _ColorDef(digit: 7, mult: 7, tol: 0.1),
  'grey': _ColorDef(digit: 8, mult: 8),
  'white': _ColorDef(digit: 9, mult: 9),
  'gold': _ColorDef(mult: -1, tol: 5.0),
  'silver': _ColorDef(mult: -2, tol: 10.0),
};

// Representative HSV centres. H in 0-180 (OpenCV convention), S/V in 0-255.
const Map<String, List<double>> _colorHsv = {
  'black': [0, 0, 25],
  'brown': [12, 150, 90],
  'red': [0, 200, 160],
  'orange': [13, 210, 210],
  'yellow': [26, 200, 210],
  'green': [60, 160, 140],
  'blue': [108, 180, 160],
  'violet': [140, 120, 150],
  'grey': [0, 10, 130],
  'white': [0, 8, 235],
  'gold': [22, 130, 165],
  'silver': [0, 8, 175],
};

List<double> _rgbToHsv(num r, num g, num b) {
  final rf = r / 255.0, gf = g / 255.0, bf = b / 255.0;
  final maxv = math.max(rf, math.max(gf, bf));
  final minv = math.min(rf, math.min(gf, bf));
  final d = maxv - minv;
  double h = 0;
  if (d != 0) {
    if (maxv == rf) {
      h = 60 * (((gf - bf) / d) % 6);
    } else if (maxv == gf) {
      h = 60 * (((bf - rf) / d) + 2);
    } else {
      h = 60 * (((rf - gf) / d) + 4);
    }
  }
  if (h < 0) h += 360;
  final s = maxv == 0 ? 0.0 : d / maxv;
  // Convert to OpenCV-style ranges to reuse the Python colour centres.
  return [h / 2.0, s * 255.0, maxv * 255.0];
}

(String, double) _classifyHsv(List<double> hsv) {
  final h = hsv[0], s = hsv[1], v = hsv[2];
  var bestName = 'black';
  var bestDist = double.infinity;
  _colorHsv.forEach((name, c) {
    final dh = math.min((h - c[0]).abs(), 180 - (h - c[0]).abs());
    final hueWeight = s > 60 ? 2.0 : 0.2;
    final dist = math.pow(hueWeight * dh, 2) +
        math.pow(0.5 * (s - c[1]), 2) +
        math.pow(0.6 * (v - c[2]), 2);
    if (dist < bestDist) {
      bestDist = dist.toDouble();
      bestName = name;
    }
  });
  final conf = (1.0 - math.sqrt(bestDist) / 220.0).clamp(0.0, 1.0);
  return (bestName, conf);
}

String _formatOhms(double value, double? tolerance) {
  String base;
  if (value >= 1000000) {
    base = '${_trim(value / 1000000)}MΩ';
  } else if (value >= 1000) {
    base = '${_trim(value / 1000)}kΩ';
  } else {
    base = '${_trim(value)}Ω';
  }
  return tolerance != null ? '$base ±${_trim(tolerance)}%' : base;
}

String _trim(double v) {
  final s = v.toStringAsFixed(2);
  return s.replaceFirst(RegExp(r'\.?0+$'), '');
}

/// Attempt to decode a resistor from raw image bytes (JPEG/PNG).
/// Returns null when the image doesn't look like a resistor.
ResistorReading? decodeResistor(List<int> bytes) {
  var im = img.decodeImage(Uint8List.fromList(bytes));
  if (im == null) return null;
  // Downscale for speed; keep enough width to resolve the bands.
  if (im.width > 800) {
    im = img.copyResize(im, width: 800);
  }

  // --- Locate the "body": bounding box of sufficiently saturated pixels. ---
  int minX = im.width, maxX = -1, minY = im.height, maxY = -1, count = 0;
  for (var y = 0; y < im.height; y += 2) {
    for (var x = 0; x < im.width; x += 2) {
      final p = im.getPixel(x, y);
      final hsv = _rgbToHsv(p.r, p.g, p.b);
      if (hsv[1] > 40) {
        count++;
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
    }
  }
  if (count < 50 || maxX - minX < 20 || maxY - minY < 6) return null;

  var roi = img.copyCrop(im,
      x: minX, y: minY, width: maxX - minX + 1, height: maxY - minY + 1);
  if (roi.height > roi.width) {
    roi = img.copyRotate(roi, angle: 90);
  }
  final rw = roi.width, rh = roi.height;
  if (rw < 30) return null;

  // --- Column-mean HSV through a middle strip. ---
  final y0 = (rh * 0.35).floor(), y1 = math.max(y0 + 1, (rh * 0.65).ceil());
  final colMeans = List<List<double>>.generate(rw, (_) => [0, 0, 0]);
  for (var x = 0; x < rw; x++) {
    double sh = 0, ss = 0, sv = 0;
    var n = 0;
    for (var y = y0; y < y1 && y < rh; y++) {
      final p = roi.getPixel(x, y);
      final hsv = _rgbToHsv(p.r, p.g, p.b);
      sh += hsv[0];
      ss += hsv[1];
      sv += hsv[2];
      n++;
    }
    if (n > 0) colMeans[x] = [sh / n, ss / n, sv / n];
  }

  // Body colour = per-channel median of the columns.
  List<double> channel(int i) =>
      (colMeans.map((c) => c[i]).toList()..sort());
  double median(List<double> v) => v[v.length ~/ 2];
  final body = [
    median(channel(0)),
    median(channel(1)),
    median(channel(2)),
  ];

  final diffs = List<double>.generate(rw, (x) {
    final c = colMeans[x];
    return math.sqrt(math.pow(c[0] - body[0], 2) +
        math.pow(c[1] - body[1], 2) +
        math.pow(c[2] - body[2], 2));
  });
  final sortedDiffs = [...diffs]..sort();
  final p70 = sortedDiffs[(sortedDiffs.length * 0.7).floor()];
  final threshold = math.max(35.0, p70);

  // --- Segment contiguous "band" runs and classify each. ---
  final bands = <String>[];
  final bandConfs = <double>[];
  var inBand = false;
  final acc = <List<double>>[];
  void flush() {
    if (acc.length >= 2) {
      final mean = [0.0, 0.0, 0.0];
      for (final c in acc) {
        mean[0] += c[0];
        mean[1] += c[1];
        mean[2] += c[2];
      }
      for (var i = 0; i < 3; i++) {
        mean[i] /= acc.length;
      }
      final (name, conf) = _classifyHsv(mean);
      bands.add(name);
      bandConfs.add(conf);
    }
    acc.clear();
  }

  for (var x = 0; x < rw; x++) {
    if (diffs[x] > threshold) {
      inBand = true;
      acc.add(colMeans[x]);
    } else {
      if (inBand) flush();
      inBand = false;
    }
  }
  if (inBand) flush();

  if (bands.length < 3) return null;

  final parsed = _bandsToValue(bands);
  if (parsed == null) return null;
  final (value, tol, used) = parsed;
  final avgConf = bandConfs.isEmpty
      ? 0.3
      : bandConfs.take(used.length).reduce((a, b) => a + b) /
          math.min(bandConfs.length, used.length);
  final confidence =
      (avgConf * (bands.length > 5 ? 0.85 : 1.0)).clamp(0.0, 0.9);
  return ResistorReading(
    valueOhms: value,
    display: _formatOhms(value, tol),
    bands: used,
    tolerance: tol,
    confidence: double.parse(confidence.toStringAsFixed(2)),
  );
}

(double, double?, List<String>)? _bandsToValue(List<String> bands) {
  final usable = bands.where(_colorCode.containsKey).toList();
  if (usable.length < 3) return null;

  (double, double?)? digitsAndMult(List<String> seq) {
    final digitBands = seq.sublist(0, seq.length - 1);
    final multBand = seq.last;
    final digits = StringBuffer();
    for (final b in digitBands) {
      final d = _colorCode[b]!.digit;
      if (d == null) return null;
      digits.write(d);
    }
    final mult = _colorCode[multBand]!.mult;
    if (mult == null) return null;
    final base = int.tryParse(digits.toString());
    if (base == null) return null;
    return (base * math.pow(10.0, mult).toDouble(), null);
  }

  for (final n in [5, 4]) {
    if (usable.length >= n) {
      final seq = usable.sublist(0, n);
      final tol = _colorCode[seq.last]!.tol;
      final core = tol != null ? seq.sublist(0, seq.length - 1) : seq;
      final res = digitsAndMult(core);
      if (res != null) return (res.$1, tol, seq);
    }
  }
  final seq = usable.sublist(0, 3);
  final res = digitsAndMult(seq);
  if (res != null) return (res.$1, null, seq);
  return null;
}

