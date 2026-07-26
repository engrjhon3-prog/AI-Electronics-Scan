import 'dart:async';
import 'dart:io';

import 'package:firebase_auth/firebase_auth.dart' show User;
import 'package:flutter/foundation.dart';

import '../models/component.dart';
import '../models/entitlement.dart';
import '../models/history_entry.dart';
import '../models/scan_result.dart';
import '../models/wiring.dart';
import '../services/ai_identify_service.dart';
import '../services/api_client.dart' show PremiumRequiredException;
import '../services/auth_service.dart';
import '../services/cloud_uploads_service.dart';
import '../services/history_service.dart';
import '../services/local_repository.dart';
import '../services/on_device_scanner.dart';
import '../services/payment_service.dart';
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
    AuthService? auth,
    PaymentService? payments,
    AiIdentifyService? ai,
  })  : repo = repository ?? LocalRepository(),
        _history = history ?? HistoryService(),
        subscription = subscription ?? SubscriptionService(),
        auth = auth ?? AuthService(),
        payments = payments ?? PaymentService(),
        ai = ai ?? AiIdentifyService() {
    _scanner = scanner ?? OnDeviceScanner(repo);
  }

  final LocalRepository repo;
  late final OnDeviceScanner _scanner;
  final HistoryService _history;
  final SubscriptionService subscription;
  final AuthService auth;
  final PaymentService payments;
  final AiIdentifyService ai;
  final CloudUploadsService uploads = CloudUploadsService();

  /// Whether the backend can identify parts outside the bundled catalog.
  AiStatus aiStatus = AiStatus.offline;

  /// Outcome of the most recent cloud save ("saved, expires in 12h" /
  /// quota message). Shown on the result screen.
  String? lastCloudNote;

  bool _initialised = false;
  bool get initialised => _initialised;

  String? _initError;
  String? get initError => _initError;

  List<HistoryEntry> _historyEntries = [];
  List<HistoryEntry> get history => List.unmodifiable(_historyEntries);

  StreamSubscription<User?>? _authSub;
  StreamSubscription<Entitlement>? _entitlementSub;
  bool _isAdmin = false;
  bool get isAdmin => _isAdmin;
  User? get user => auth.currentUser;
  bool get signedIn => user != null;

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
    refreshAiStatus();
    if (auth.isAvailable) {
      _authSub = auth.authStateChanges().listen(_onAuthChanged);
    }
  }

  Future<void> _onAuthChanged(User? user) async {
    await _entitlementSub?.cancel();
    _entitlementSub = null;
    if (user == null) {
      _isAdmin = false;
      await subscription.setPremium(false);
      notifyListeners();
      return;
    }
    await refreshEntitlement();
    // Tidy up this user's own expired cloud uploads in the background.
    uploads.purgeExpired(user.uid).catchError((_) {});
    final email = user.email;
    if (email != null) {
      // A confirmed GCash payment writes this document server-side, so Pro
      // switches on here within a second — no admin approval involved.
      _entitlementSub = auth.entitlementStream(email).listen((entitlement) async {
        final claims = await auth.readClaims();
        await subscription.setEntitlement(
            claims.premium ? _compedEntitlement : entitlement);
        notifyListeners();
      }, onError: (_) {});
    }
  }

  /// Pro granted by a custom claim (staff / comped accounts): never expires.
  static const Entitlement _compedEntitlement =
      Entitlement(premium: true, planName: 'Pro');

  /// Force-refresh claims + entitlement (e.g. right after paying with GCash).
  Future<void> refreshEntitlement() async {
    try {
      final claims = await auth.readClaims(refresh: true);
      _isAdmin = claims.admin;
      var entitlement = claims.premium ? _compedEntitlement : Entitlement.none;
      final email = user?.email;
      if (!entitlement.premium && email != null) {
        entitlement = await auth.fetchEntitlement(email);
      }
      await subscription.setEntitlement(entitlement);
    } catch (_) {
      // Offline: keep the cached entitlement.
    }
    notifyListeners();
  }

  /// Unlock Pro straight from a confirmed payment.
  ///
  /// The entitlement stream normally does this on its own; this covers builds
  /// without Firebase and the moment right after checkout, so the customer is
  /// never left waiting on a sync.
  Future<void> applyPaidPayment({String? premiumUntil, String planName = 'Pro'}) async {
    await subscription.setEntitlement(Entitlement(
      premium: true,
      planName: planName,
      source: 'gcash',
      expiresAt: premiumUntil == null ? null : DateTime.tryParse(premiumUntil),
    ));
    notifyListeners();
    await refreshEntitlement();
  }

  Future<void> signOut() async {
    await auth.signOut();
  }

  bool get isPremium => subscription.isPremium;
  bool get canScan => subscription.canScan;
  int get freeScansRemaining => subscription.freeScansRemaining;

  /// When the current subscription lapses (`null` = lifetime / not subscribed).
  DateTime? get premiumUntil => subscription.premiumUntil;
  String get planName => subscription.planName;

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

  // -------------------------------------------------------------------- ai
  /// Ask the backend whether AI identification is switched on.
  Future<void> refreshAiStatus() async {
    final status = await ai.status();
    if (status.available != aiStatus.available ||
        status.cachedComponents != aiStatus.cachedComponents) {
      aiStatus = status;
      notifyListeners();
    }
  }

  /// Identify a component the bundled catalog doesn't know.
  ///
  /// The photo and the OCR text go to the backend's vision model, which writes
  /// a full entry — pinout, wiring, code. The result is merged into the local
  /// catalog and saved on the device, so the part works offline from now on
  /// and shows up in search and history like any other component.
  Future<AiIdentification> identifyWithAi(
    File image, {
    String ocrText = '',
    String hint = '',
  }) async {
    final result = await ai.identify(
      image: image,
      ocrText: ocrText,
      hint: hint,
      idToken: await auth.idToken(),
    );
    if (result.component.isNotEmpty && result.componentId.isNotEmpty) {
      await repo.addLearned(result.component);
      notifyListeners();
    }
    return result;
  }

  /// How many components the AI has added to this device's catalog.
  int get learnedComponentCount => repo.learnedCount;

  bool isAiComponent(String id) => repo.isLearned(id);

  // ------------------------------------------------------------------ scan
  /// Run on-device recognition, record the scan in history, and (when signed
  /// in) save the photo to cloud storage with the tier's retention.
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

    lastCloudNote = null;
    final u = user;
    if (u != null) {
      try {
        await uploads.upload(
          uid: u.uid,
          image: image,
          premium: isPremium,
          name: result.bestMatch?.name ?? 'Unidentified scan',
          componentId: result.bestMatch?.componentId,
        );
        lastCloudNote = isPremium
            ? 'Photo saved to your cloud account (kept 7 days).'
            : 'Photo saved to your cloud account (kept 12 hours).';
      } on UploadQuotaExceeded catch (e) {
        lastCloudNote = e.message;
      } catch (_) {
        lastCloudNote = null; // Offline — silently skip cloud save.
      }
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

  @override
  void dispose() {
    _authSub?.cancel();
    _entitlementSub?.cancel();
    super.dispose();
  }
}
