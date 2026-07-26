import 'package:shared_preferences/shared_preferences.dart';

import '../config.dart';

/// Tracks the user's freemium entitlement and free-scan usage.
///
/// Premium status is driven by Firebase (custom claim or an admin-granted
/// `entitlements/{email}` document) via AuthService, and cached locally here
/// so Pro features keep working offline between sessions.
class SubscriptionService {
  static const _premiumKey = 'is_premium_v1';
  static const _scanCountKey = 'scan_count';
  static const _scanMonthKey = 'scan_month';

  bool _isPremium = false;
  int _scansThisMonth = 0;

  bool get isPremium => _isPremium;
  int get scansThisMonth => _scansThisMonth;
  int get freeScansRemaining =>
      (AppConfig.freeScansPerMonth - _scansThisMonth).clamp(0, 1 << 30);

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

  /// Persist the entitlement decided by the cloud (claims / entitlement doc).
  Future<void> setPremium(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    _isPremium = value;
    await prefs.setBool(_premiumKey, value);
  }

  String _currentMonthKey() {
    final now = DateTime.now();
    return '${now.year}-${now.month.toString().padLeft(2, '0')}';
  }
}
