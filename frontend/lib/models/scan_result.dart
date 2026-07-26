class DetectionCandidate {
  final String componentId;
  final String name;
  final String type;
  final double confidence;
  final String? detectedValue;
  final String detectionMethod;
  final String reason;

  const DetectionCandidate({
    required this.componentId,
    required this.name,
    required this.type,
    required this.confidence,
    this.detectedValue,
    this.detectionMethod = '',
    this.reason = '',
  });

  factory DetectionCandidate.fromJson(Map<String, dynamic> json) =>
      DetectionCandidate(
        componentId: json['component_id'] as String,
        name: json['name'] as String? ?? '',
        type: json['type'] as String? ?? 'unknown',
        confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
        detectedValue: json['detected_value'] as String?,
        detectionMethod: json['detection_method'] as String? ?? '',
        reason: json['reason'] as String? ?? '',
      );
}

class ScanResult {
  final String scanId;
  final DetectionCandidate? bestMatch;
  final List<DetectionCandidate> candidates;
  final List<String> notes;
  final int imageWidth;
  final int imageHeight;

  const ScanResult({
    required this.scanId,
    this.bestMatch,
    this.candidates = const [],
    this.notes = const [],
    this.imageWidth = 0,
    this.imageHeight = 0,
  });

  factory ScanResult.fromJson(Map<String, dynamic> json) => ScanResult(
        scanId: json['scan_id'] as String? ?? '',
        bestMatch: json['best_match'] == null
            ? null
            : DetectionCandidate.fromJson(
                json['best_match'] as Map<String, dynamic>),
        candidates: (json['candidates'] as List?)
                ?.map((e) =>
                    DetectionCandidate.fromJson(e as Map<String, dynamic>))
                .toList() ??
            [],
        notes: (json['notes'] as List?)?.map((e) => e.toString()).toList() ?? [],
        imageWidth: json['image_width'] as int? ?? 0,
        imageHeight: json['image_height'] as int? ?? 0,
      );

  bool get hasMatch => bestMatch != null;
}
