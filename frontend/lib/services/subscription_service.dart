import 'package:shared_preferences/shared_preferences.dart';

import '../config.dart';

/// Tracks the user's freemium entitlement and free-scan usage.
///
/// This reference implementation stores state locally. For production you would
/// back this with a real billing provider (Google Play Billing / RevenueCat)
/// and verify receipts server-side, then hand the verified token to ApiClient.
class SubscriptionService {
  static const _premiumKey = 'is_premium_v1';
  static const _scanCountKey = 'scan_count';
  static const _scanMonthKey = 'scan_month';

  /// The token handed to the backend to unlock premium endpoints.
  /// In production, replace with a verified receipt / Firebase claim token.
  static const String _devPremiumToken = 'premium-dev';

  bool _isPremium = false;
  int _scansThisMonth = 0;

  bool get isPremium => _isPremium;
  int get scansThisMonth => _scansThisMonth;
  int get freeScansRemaining =>
      (AppConfig.freeScansPerMonth - _scansThisMonth).clamp(0, 1 << 30);

  /// Null when not premium; the backend token when premium.
  String? get premiumToken => _isPremium ? _devPremiumToken : null;

  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    _isPremium = prefs.getBool(_premiumKey) ?? false;
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
  bool get canScan => _isPremium || freeScansRemaining > 0;

  Future<void> recordScan() async {
    if (_isPremium) return;
    final prefs = await SharedPreferences.getInstance();
    _scansThisMonth += 1;
    await prefs.setInt(_scanCountKey, _scansThisMonth);
  }

  /// Simulate a successful purchase. Wire this to real billing later.
  Future<void> activatePremium() async {
    final prefs = await SharedPreferences.getInstance();
    _isPremium = true;
    await prefs.setBool(_premiumKey, true);
  }

  Future<void> cancelPremium() async {
    final prefs = await SharedPreferences.getInstance();
    _isPremium = false;
    await prefs.setBool(_premiumKey, false);
  }

  String _currentMonthKey() {
    final now = DateTime.now();
    return '${now.year}-${now.month.toString().padLeft(2, '0')}';
  }
}
