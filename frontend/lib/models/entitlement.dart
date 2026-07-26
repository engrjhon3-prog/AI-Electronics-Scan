/// The Pro entitlement stored at `entitlements/{email}`.
///
/// It is written automatically by the backend the moment a GCash payment is
/// confirmed (see `backend/app/payments`), and read live by the app — so a
/// paid subscription unlocks without anyone approving it by hand.
class Entitlement {
  final bool premium;
  final String plan;
  final String planName;

  /// When Pro lapses. `null` means it never does (lifetime plan).
  final DateTime? expiresAt;

  /// How Pro was granted: `gcash`, or empty for a manual/admin grant.
  final String source;

  const Entitlement({
    this.premium = false,
    this.plan = '',
    this.planName = '',
    this.expiresAt,
    this.source = '',
  });

  static const Entitlement none = Entitlement();

  /// True when Pro is granted *and* has not lapsed.
  bool get isActive =>
      premium && (expiresAt == null || expiresAt!.isAfter(DateTime.now()));

  bool get isLifetime => premium && expiresAt == null;

  int? get daysRemaining => expiresAt?.difference(DateTime.now()).inDays;

  factory Entitlement.fromMap(Map<String, dynamic>? data) {
    if (data == null) return Entitlement.none;
    return Entitlement(
      premium: data['premium'] == true,
      plan: data['plan']?.toString() ?? '',
      planName: data['planName']?.toString() ?? '',
      expiresAt: parseDate(data['expiresAt']),
      source: data['source']?.toString() ?? '',
    );
  }

  /// Accepts a Firestore `Timestamp`, an ISO-8601 string, or a [DateTime].
  static DateTime? parseDate(dynamic value) {
    if (value == null) return null;
    if (value is DateTime) return value;
    if (value is String) return DateTime.tryParse(value);
    try {
      // Firestore Timestamp — read dynamically so this model stays plain Dart.
      return (value as dynamic).toDate() as DateTime;
    } catch (_) {
      return null;
    }
  }
}
