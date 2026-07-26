import 'package:shared_preferences/shared_preferences.dart';

import '../config.dart';
import '../models/entitlement.dart';

/// Tracks the user's freemium entitlement and free-scan usage.
///
/// Premium status comes from Firebase — a custom claim, or the
/// `entitlements/{email}` document the payment backend writes as soon as a
/// GCash payment clears — and is cached locally here so Pro keeps working
/// offline between sessions. The cached copy carries the expiry date, so a
/// lapsed subscription also lapses offline.
class SubscriptionService {
  static const _premiumKey = 'is_premium_v1';
  static const _expiryKey = 'premium_expires_at';
  static const _planKey = 'premium_plan_name';
  static const _scanCountKey = 'scan_count';
  static const _scanMonthKey = 'scan_month';

  bool _premiumGranted = false;
  DateTime? _premiumUntil;
  String _planName = '';
  int _scansThisMonth = 0;

  /// True while the subscription is granted *and* unexpired.
  bool get isPremium =>
      _premiumGranted &&
      (_premiumUntil == null || _premiumUntil!.isAfter(DateTime.now()));

  /// When Pro lapses — `null` on a lifetime plan (or when not subscribed).
  DateTime? get premiumUntil => _premiumUntil;

  String get planName => _planName;

  bool get isLifetime => isPremium && _premiumUntil == null;

  int get scansThisMonth => _scansThisMonth;
  int get freeScansRemaining =>
      (AppConfig.freeScansPerMonth - _scansThisMonth).clamp(0, 1 << 30);

  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    _premiumGranted = prefs.getBool(_premiumKey) ?? false;
    final expiry = prefs.getString(_expiryKey);
    _premiumUntil = expiry == null ? null : DateTime.tryParse(expiry);
    _planName = prefs.getString(_planKey) ?? '';
    final month = _currentMonthKey();
    if (prefs.getString(_scanMonthKey) != month) {
      // New month — reset the free counter.
      await prefs.setString(_scanMonthKey, month);
      await prefs.setInt(_scanCountKey, 0);
      _scansThisMonth = 0;
    } else {
      _scansThisMonth = prefs.getInt(_scanCountKey) ?? 0;
    }
  }

  /// Whether the user may perform another free scan this month.
  bool get canScan => isPremium || freeScansRemaining > 0;

  Future<void> recordScan() async {
    if (isPremium) return;
    final prefs = await SharedPreferences.getInstance();
    _scansThisMonth += 1;
    await prefs.setInt(_scanCountKey, _scansThisMonth);
  }

  /// Persist the entitlement decided by the cloud (claims / entitlement doc).
  Future<void> setEntitlement(Entitlement entitlement) async {
    final prefs = await SharedPreferences.getInstance();
    _premiumGranted = entitlement.premium;
    _premiumUntil = entitlement.expiresAt;
    _planName = entitlement.planName;
    await prefs.setBool(_premiumKey, _premiumGranted);
    await prefs.setString(_planKey, _planName);
    if (_premiumUntil == null) {
      await prefs.remove(_expiryKey);
    } else {
      await prefs.setString(_expiryKey, _premiumUntil!.toIso8601String());
    }
  }

  /// Grant/revoke Pro with no expiry (custom claim, or signing out).
  Future<void> setPremium(bool value) =>
      setEntitlement(value ? const Entitlement(premium: true) : Entitlement.none);

  String _currentMonthKey() {
    final now = DateTime.now();
    return '${now.year}-${now.month.toString().padLeft(2, '0')}';
  }
}
