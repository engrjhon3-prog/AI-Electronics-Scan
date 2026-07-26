class Connection {
  final String fromPin;
  final String toPin;
  final String note;

  const Connection({
    required this.fromPin,
    required this.toPin,
    this.note = '',
  });

  factory Connection.fromJson(Map<String, dynamic> json) => Connection(
        fromPin: json['from_pin'] as String? ?? '',
        toPin: json['to_pin'] as String? ?? '',
        note: json['note'] as String? ?? '',
      );
}

class WiringDiagram {
  final String componentId;
  final String board;
  final List<Connection> connections;
  final List<String> notes;
  final String? svg;

  const WiringDiagram({
    required this.componentId,
    required this.board,
    this.connections = const [],
    this.notes = const [],
    this.svg,
  });

  factory WiringDiagram.fromJson(Map<String, dynamic> json) => WiringDiagram(
        componentId: json['component_id'] as String? ?? '',
        board: json['board'] as String? ?? 'uno',
        connections: (json['connections'] as List?)
                ?.map((e) => Connection.fromJson(e as Map<String, dynamic>))
                .toList() ??
            [],
        notes: (json['notes'] as List?)?.map((e) => e.toString()).toList() ?? [],
        svg: json['svg'] as String?,
      );
}

class CodeSnippet {
  final String componentId;
  final String board;
  final String language;
  final String title;
  final String description;
  final List<String> libraries;
  final String code;

  const CodeSnippet({
    required this.componentId,
    required this.board,
    this.language = 'cpp',
    this.title = '',
    this.description = '',
    this.libraries = const [],
    this.code = '',
  });

  factory CodeSnippet.fromJson(Map<String, dynamic> json) => CodeSnippet(
        componentId: json['component_id'] as String? ?? '',
        board: json['board'] as String? ?? 'uno',
        language: json['language'] as String? ?? 'cpp',
        title: json['title'] as String? ?? '',
        description: json['description'] as String? ?? '',
        libraries:
            (json['libraries'] as List?)?.map((e) => e.toString()).toList() ??
                [],
        code: json['code'] as String? ?? '',
      );
}
