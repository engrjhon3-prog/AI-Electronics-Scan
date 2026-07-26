import 'dart:convert';

import 'package:flutter/services.dart' show rootBundle;

import '../models/component.dart';
import '../models/wiring.dart';

/// Offline component knowledge base, bundled with the app as an asset.
///
/// This is the exported twin of `backend/app/components/database.py`
/// (see `backend/scripts/export_assets.py`). It provides everything the app
/// needs — catalog, pinouts, wiring diagrams (pre-rendered SVG), and code
/// snippets — with no server and no network.
class LocalRepository {
  List<Component> _components = [];
  final Map<String, Map<String, dynamic>> _rawById = {};
  final Map<String, String> _aliasIndex = {};
  bool _loaded = false;

  bool get isLoaded => _loaded;

  Future<void> load() async {
    if (_loaded) return;
    final raw = await rootBundle.loadString('assets/components.json');
    final data = jsonDecode(raw) as Map<String, dynamic>;
    final list = (data['components'] as List).cast<Map<String, dynamic>>();
    _components = list.map(Component.fromJson).toList()
      ..sort((a, b) => a.name.compareTo(b.name));
    for (final item in list) {
      final id = item['id'] as String;
      _rawById[id] = item;
      _aliasIndex[id.toLowerCase()] = id;
      _aliasIndex[(item['name'] as String).toLowerCase()] = id;
      for (final alias in (item['aliases'] as List? ?? [])) {
        _aliasIndex[alias.toString().toLowerCase()] = id;
      }
    }
    _loaded = true;
  }

  List<Component> get components => List.unmodifiable(_components);

  Component? getComponent(String id) {
    final raw = _rawById[id];
    return raw == null ? null : Component.fromJson(raw);
  }

  /// Find a component whose name/alias appears in [text] (case-insensitive).
  /// Prefers the longest alias match, mirroring the backend logic.
  String? findByAlias(String text) {
    final t = text.toLowerCase();
    if (_aliasIndex.containsKey(t)) return _aliasIndex[t];
    String? best;
    var bestLen = 0;
    _aliasIndex.forEach((alias, id) {
      if (alias.length >= 3 && alias.length > bestLen && t.contains(alias)) {
        best = id;
        bestLen = alias.length;
      }
    });
    return best;
  }

  WiringDiagram? getWiring(String id, String board) {
    final raw = _rawById[id];
    if (raw == null) return null;
    final wiring = (raw['wiring'] as Map<String, dynamic>?)?[board];
    if (wiring == null) return null;
    return WiringDiagram(
      componentId: id,
      board: board,
      connections: (wiring['connections'] as List)
          .map((e) => Connection.fromJson(e as Map<String, dynamic>))
          .toList(),
      notes:
          (wiring['notes'] as List?)?.map((e) => e.toString()).toList() ?? [],
      svg: wiring['svg'] as String?,
    );
  }

  CodeSnippet? getCode(String id, String board) {
    final raw = _rawById[id];
    if (raw == null) return null;
    final code = (raw['code'] as Map<String, dynamic>?)?[board];
    if (code == null) return null;
    return CodeSnippet(
      componentId: id,
      board: board,
      title: code['title'] as String? ?? '',
      description: code['description'] as String? ?? '',
      libraries:
          (code['libraries'] as List?)?.map((e) => e.toString()).toList() ??
              [],
      code: code['code'] as String? ?? '',
    );
  }
}
