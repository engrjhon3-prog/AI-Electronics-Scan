import 'dart:io';

import 'package:flutter/foundation.dart';

import '../models/component.dart';
import '../models/history_entry.dart';
import '../models/scan_result.dart';
import '../models/wiring.dart';
import '../services/api_client.dart' show PremiumRequiredException;
import '../services/history_service.dart';
import '../services/local_repository.dart';
import '../services/on_device_scanner.dart';
import '../services/subscription_service.dart';

/// Central application state, exposed via Provider.
///
/// Offline-first: recognition runs on-device (ML Kit OCR + Dart resistor
/// decoder) and the knowledge base ships inside the APK, so the core app
/// needs no server at all.
class AppState extends ChangeNotifier {
  AppState({
    LocalRepository? repository,
    OnDeviceScanner? scanner,
    HistoryService? history,
    SubscriptionService? subscription,
  })  : repo = repository ?? LocalRepository(),
        _history = history ?? HistoryService(),
        subscription = subscription ?? SubscriptionService() {
    _scanner = scanner ?? OnDeviceScanner(repo);
  }

  final LocalRepository repo;
  late final OnDeviceScanner _scanner;
  final HistoryService _history;
  final SubscriptionService subscription;

  bool _initialised = false;
  bool get initialised => _initialised;

  String? _initError;
  String? get initError => _initError;

  List<HistoryEntry> _historyEntries = [];
  List<HistoryEntry> get history => List.unmodifiable(_historyEntries);

  Future<void> init() async {
    try {
      await repo.load();
    } catch (e) {
      _initError = 'Component database failed to load: $e';
    }
    await subscription.load();
    _historyEntries = await _history.load();
    _initialised = true;
    notifyListeners();
  }

  bool get isPremium => subscription.isPremium;
  bool get canScan => subscription.canScan;
  int get freeScansRemaining => subscription.freeScansRemaining;

  // ---------------------------------------------------------------- catalog
  List<Component> get components => repo.components;

  Component? getComponent(String id) => repo.getComponent(id);

  /// PRO: wiring diagram. Throws [PremiumRequiredException] on the free tier.
  WiringDiagram? getWiring(String id, String board) {
    if (!isPremium) throw PremiumRequiredException();
    return repo.getWiring(id, board);
  }

  /// PRO: code snippet. Throws [PremiumRequiredException] on the free tier.
  CodeSnippet? getCode(String id, String board) {
    if (!isPremium) throw PremiumRequiredException();
    return repo.getCode(id, board);
  }

  // ------------------------------------------------------------------ scan
  /// Run on-device recognition and record the scan in history.
  Future<ScanResult> scan(File image) async {
    final result = await _scanner.scan(image);
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

  // --------------------------------------------------------------- history
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

  // --------------------------------------------------------------- premium
  Future<void> activatePremium() async {
    await subscription.activatePremium();
    notifyListeners();
  }

  Future<void> cancelPremium() async {
    await subscription.cancelPremium();
    notifyListeners();
  }
}
