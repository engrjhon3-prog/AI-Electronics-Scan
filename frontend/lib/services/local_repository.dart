import 'dart:convert';
import 'dart:io';

import 'package:flutter/services.dart' show rootBundle;
import 'package:path_provider/path_provider.dart';

import '../models/component.dart';
import '../models/wiring.dart';

/// Offline component knowledge base, bundled with the app as an asset.
///
/// This is the exported twin of `backend/app/components/database.py`
/// (see `backend/scripts/export_assets.py`). It provides everything the app
/// needs — catalog, pinouts, wiring diagrams (pre-rendered SVG), and code
/// snippets — with no server and no network.
///
/// Components the AI identifies are merged in on top and saved to the device,
/// so a part learned once behaves exactly like a bundled one from then on —
/// including offline.
class LocalRepository {
  List<Component> _components = [];
  final Map<String, Map<String, dynamic>> _rawById = {};
  final Map<String, String> _aliasIndex = {};

  /// Ids that came from AI identification rather than the bundled asset.
  final Set<String> _learnedIds = {};
  bool _loaded = false;

  bool get isLoaded => _loaded;

  /// Number of components the AI has added to this device's catalog.
  int get learnedCount => _learnedIds.length;

  bool isLearned(String id) => _learnedIds.contains(id);

  Future<void> load() async {
    if (_loaded) return;
    final raw = await rootBundle.loadString('assets/components.json');
    final data = jsonDecode(raw) as Map<String, dynamic>;
    final list = (data['components'] as List).cast<Map<String, dynamic>>();
    for (final item in list) {
      _index(item);
    }
    _resort();
    _loaded = true;
    await _loadLearned();
  }

  List<Component> get components => List.unmodifiable(_components);

  Component? getComponent(String id) {
    final raw = _rawById[id];
    return raw == null ? null : Component.fromJson(raw);
  }

  /// Add (or replace) a component identified by the AI and remember it on
  /// this device.
  Future<Component> addLearned(Map<String, dynamic> raw) async {
    _index(raw);
    _learnedIds.add(raw['id'] as String);
    _resort();
    await _saveLearned();
    return Component.fromJson(raw);
  }

  void _index(Map<String, dynamic> item) {
    final id = item['id'] as String;
    _rawById[id] = item;
    _aliasIndex[id.toLowerCase()] = id;
    _aliasIndex[(item['name'] as String? ?? '').toLowerCase()] = id;
    for (final alias in (item['aliases'] as List? ?? [])) {
      _aliasIndex[alias.toString().toLowerCase()] = id;
    }
  }

  void _resort() {
    _components = _rawById.values.map(Component.fromJson).toList()
      ..sort((a, b) => a.name.compareTo(b.name));
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

  // ------------------------------------------------------- device storage
  Future<File?> _learnedFile() async {
    try {
      final dir = await getApplicationDocumentsDirectory();
      return File('${dir.path}/ai_components.json');
    } catch (_) {
      // No filesystem (tests, unsupported platform) — stay in memory.
      return null;
    }
  }

  Future<void> _loadLearned() async {
    try {
      final file = await _learnedFile();
      if (file == null || !await file.exists()) return;
      final list = (jsonDecode(await file.readAsString()) as List)
          .cast<Map<String, dynamic>>();
      for (final item in list) {
        _index(item);
        _learnedIds.add(item['id'] as String);
      }
      _resort();
    } catch (_) {
      // A corrupt cache must never block the bundled catalog.
    }
  }

  Future<void> _saveLearned() async {
    try {
      final file = await _learnedFile();
      if (file == null) return;
      final items = _learnedIds.map((id) => _rawById[id]).whereType<Map>().toList();
      await file.writeAsString(jsonEncode(items));
    } catch (_) {
      // Not being able to persist is not worth failing the scan over.
    }
  }
}
