/// A saved scan, persisted locally (and later syncable to Firebase).
class HistoryEntry {
  final String id;
  final String componentId;
  final String componentName;
  final String type;
  final double confidence;
  final String? detectedValue;
  final DateTime timestamp;
  final String? imagePath;

  const HistoryEntry({
    required this.id,
    required this.componentId,
    required this.componentName,
    required this.type,
    required this.confidence,
    this.detectedValue,
    required this.timestamp,
    this.imagePath,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'component_id': componentId,
        'component_name': componentName,
        'type': type,
        'confidence': confidence,
        'detected_value': detectedValue,
        'timestamp': timestamp.toIso8601String(),
        'image_path': imagePath,
      };

  factory HistoryEntry.fromJson(Map<String, dynamic> json) => HistoryEntry(
        id: json['id'] as String,
        componentId: json['component_id'] as String,
        componentName: json['component_name'] as String,
        type: json['type'] as String? ?? 'unknown',
        confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
        detectedValue: json['detected_value'] as String?,
        timestamp: DateTime.parse(json['timestamp'] as String),
        imagePath: json['image_path'] as String?,
      );
}
