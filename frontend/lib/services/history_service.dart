import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import '../models/history_entry.dart';

/// Persists scan history locally. Designed so a Firebase-backed
/// implementation can drop in behind the same interface later.
class HistoryService {
  static const _key = 'scan_history_v1';

  Future<List<HistoryEntry>> load() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_key);
    if (raw == null || raw.isEmpty) return [];
    try {
      final list = jsonDecode(raw) as List;
      final entries = list
          .map((e) => HistoryEntry.fromJson(e as Map<String, dynamic>))
          .toList();
      entries.sort((a, b) => b.timestamp.compareTo(a.timestamp));
      return entries;
    } catch (_) {
      return [];
    }
  }

  Future<void> add(HistoryEntry entry) async {
    final entries = await load();
    entries.insert(0, entry);
    await _save(entries);
  }

  Future<void> remove(String id) async {
    final entries = await load();
    entries.removeWhere((e) => e.id == id);
    await _save(entries);
  }

  Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_key);
  }

  Future<void> _save(List<HistoryEntry> entries) async {
    final prefs = await SharedPreferences.getInstance();
    final raw = jsonEncode(entries.map((e) => e.toJson()).toList());
    await prefs.setString(_key, raw);
  }
}
