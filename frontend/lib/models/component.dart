// Data models mirroring the Python backend's JSON contract
// (see `backend/app/models.py`). Keep field names in sync.

class Pin {
  final int number;
  final String name;
  final String type;
  final String description;

  const Pin({
    required this.number,
    required this.name,
    required this.type,
    required this.description,
  });

  factory Pin.fromJson(Map<String, dynamic> json) => Pin(
        number: json['number'] as int,
        name: json['name'] as String? ?? '',
        type: json['type'] as String? ?? 'signal',
        description: json['description'] as String? ?? '',
      );
}

class Component {
  final String id;
  final String type;
  final String name;
  final List<String> aliases;
  final String description;
  final String package;
  final String? datasheetUrl;
  final List<Pin> pins;
  final List<String> supportedBoards;
  final List<String> tags;

  /// Catalog section the part is filed under ("wireless", "sensors-motion" …).
  final String category;

  const Component({
    required this.id,
    required this.type,
    required this.name,
    this.aliases = const [],
    this.description = '',
    this.package = '',
    this.datasheetUrl,
    this.pins = const [],
    this.supportedBoards = const [],
    this.tags = const [],
    this.category = '',
  });

  factory Component.fromJson(Map<String, dynamic> json) => Component(
        id: json['id'] as String,
        type: json['type'] as String? ?? 'unknown',
        name: json['name'] as String? ?? '',
        aliases:
            (json['aliases'] as List?)?.map((e) => e.toString()).toList() ?? [],
        description: json['description'] as String? ?? '',
        package: json['package'] as String? ?? '',
        datasheetUrl: json['datasheet_url'] as String?,
        pins: (json['pins'] as List?)
                ?.map((e) => Pin.fromJson(e as Map<String, dynamic>))
                .toList() ??
            [],
        supportedBoards:
            (json['supported_boards'] as List?)?.map((e) => e.toString()).toList() ??
                [],
        tags: (json['tags'] as List?)?.map((e) => e.toString()).toList() ?? [],
        category: json['category'] as String? ?? '',
      );
}
