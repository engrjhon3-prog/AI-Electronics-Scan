import 'dart:io';

import 'package:flutter/foundation.dart';

import '../models/history_entry.dart';
import '../models/scan_result.dart';
import '../services/api_client.dart';
import '../services/history_service.dart';
import '../services/subscription_service.dart';

/// Central application state, exposed via Provider.
class AppState extends ChangeNotifier {
  AppState({
    ApiClient? api,
    HistoryService? history,
    SubscriptionService? subscription,
  })  : api = api ?? ApiClient(),
        _history = history ?? HistoryService(),
        subscription = subscription ?? SubscriptionService();

  final ApiClient api;
  final HistoryService _history;
  final SubscriptionService subscription;

  bool _initialised = false;
  bool get initialised => _initialised;

  bool? _serverReachable;
  bool? get serverReachable => _serverReachable;

  List<HistoryEntry> _historyEntries = [];
  List<HistoryEntry> get history => List.unmodifiable(_historyEntries);

  Future<void> init() async {
    await subscription.load();
    api.premiumToken = subscription.premiumToken;
    _historyEntries = await _history.load();
    _initialised = true;
    notifyListeners();
    // Fire-and-forget connectivity probe.
    checkServer();
  }

  Future<void> checkServer() async {
    _serverReachable = await api.ping();
    notifyListeners();
  }

  bool get isPremium => subscription.isPremium;
  bool get canScan => subscription.canScan;
  int get freeScansRemaining => subscription.freeScansRemaining;

  /// Perform a scan and record it in history. Returns the result.
  Future<ScanResult> scan(File image) async {
    final result = await api.scan(image);
    await subscription.recordScan();
    if (result.bestMatch != null) {
      final m = result.bestMatch!;
      final entry = HistoryEntry(
        id: result.scanId,
        componentId: m.componentId,
        componentName: m.name,
        type: m.type,
        confidence: m.confidence,
        detectedValue: m.detectedValue,
        timestamp: DateTime.now(),
        imagePath: image.path,
      );
      await _history.add(entry);
      _historyEntries = await _history.load();
    }
    notifyListeners();
    return result;
  }

  Future<void> deleteHistory(String id) async {
    await _history.remove(id);
    _historyEntries = await _history.load();
    notifyListeners();
  }

  Future<void> clearHistory() async {
    await _history.clear();
    _historyEntries = [];
    notifyListeners();
  }

  Future<void> activatePremium() async {
    await subscription.activatePremium();
    api.premiumToken = subscription.premiumToken;
    notifyListeners();
  }

  Future<void> cancelPremium() async {
    await subscription.cancelPremium();
    api.premiumToken = subscription.premiumToken;
    notifyListeners();
  }

  @override
  void dispose() {
    api.dispose();
    super.dispose();
  }
}
