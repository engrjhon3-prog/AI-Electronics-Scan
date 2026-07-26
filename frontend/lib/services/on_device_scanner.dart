import 'dart:io';

import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';

import '../models/scan_result.dart';
import 'local_repository.dart';
import 'resistor_decoder.dart';

/// Fully on-device component recognition — no server, no cost, works offline.
///
/// Mirrors the backend pipeline (`backend/app/vision/pipeline.py`):
///  1. OCR the photo with ML Kit and match part-number tokens against the
///     bundled knowledge base (most reliable for ICs/modules).
///  2. Try the resistor colour-band decoder.
///  3. Rank candidates by confidence.
class OnDeviceScanner {
  OnDeviceScanner(this._repo);

  final LocalRepository _repo;
  final _tokenPattern = RegExp(r'[A-Za-z0-9\-]{3,}');

  Future<ScanResult> scan(File image) async {
    final notes = <String>[];
    final candidates = <DetectionCandidate>[];
    var ocrText = '';
    final scanId = DateTime.now().microsecondsSinceEpoch.toRadixString(16);

    // --- Signal 1: OCR part numbers. ---
    try {
      final recognizer = TextRecognizer(script: TextRecognitionScript.latin);
      final result =
          await recognizer.processImage(InputImage.fromFilePath(image.path));
      await recognizer.close();
      ocrText = result.text;

      final tokens = <String>{};
      for (final match in _tokenPattern.allMatches(result.text)) {
        final cleaned = match.group(0)!.toUpperCase().replaceAll(
            RegExp(r'^-+|-+$'), '');
        // Part numbers contain a digit or hyphen (NE555, HC-SR04, MPU6050…).
        if (cleaned.contains(RegExp(r'[0-9]')) || cleaned.contains('-')) {
          tokens.add(cleaned);
        }
      }
      if (tokens.isNotEmpty) {
        notes.add('Text read: ${tokens.take(6).join(', ')}');
      }
      for (final token in tokens) {
        final id = _repo.findByAlias(token);
        if (id != null) {
          final comp = _repo.getComponent(id);
          if (comp != null &&
              !candidates.any((c) => c.componentId == id)) {
            candidates.add(DetectionCandidate(
              componentId: comp.id,
              name: comp.name,
              type: comp.type,
              confidence: 0.85,
              detectedValue: token,
              detectionMethod: 'on-device OCR',
              reason: "Label text '$token' matched ${comp.name}",
            ));
          }
        }
      }
    } catch (e) {
      notes.add('Text recognition unavailable: $e');
    }

    // --- Signal 2: resistor colour bands. ---
    try {
      final reading = decodeResistor(await image.readAsBytes());
      if (reading != null && _repo.getComponent('resistor') != null) {
        notes.add('Colour bands: ${reading.bands.join(' / ')}');
        candidates.add(DetectionCandidate(
          componentId: 'resistor',
          name: 'Resistor ${reading.display}',
          type: 'resistor',
          confidence: reading.confidence,
          detectedValue: reading.display,
          detectionMethod: 'colour bands',
          reason: 'Decoded bands ${reading.bands} → ${reading.display}',
        ));
      }
    } catch (e) {
      notes.add('Resistor decode skipped: $e');
    }

    candidates.sort((a, b) => b.confidence.compareTo(a.confidence));
    if (candidates.isEmpty) {
      notes.add('No component recognised. Fill the frame with the part, use '
          'even lighting, and keep any printed label in focus.');
    }

    return ScanResult(
      scanId: scanId,
      bestMatch: candidates.isEmpty ? null : candidates.first,
      candidates: candidates,
      notes: notes,
      ocrText: ocrText,
    );
  }
}
