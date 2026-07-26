import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config.dart';

/// A subscription plan offered on the paywall, priced in pesos.
class PaymentPlan {
  final String id;
  final String name;
  final int price;
  final String currency;
  final int? days; // null = lifetime
  final String description;
  final String badge;
  final String displayPrice;

  const PaymentPlan({
    required this.id,
    required this.name,
    required this.price,
    required this.currency,
    required this.days,
    this.description = '',
    this.badge = '',
    this.displayPrice = '',
  });

  factory PaymentPlan.fromJson(Map<String, dynamic> json) => PaymentPlan(
        id: json['id'] as String,
        name: json['name'] as String? ?? '',
        price: (json['price'] as num?)?.toInt() ?? 0,
        currency: json['currency'] as String? ?? 'PHP',
        days: (json['days'] as num?)?.toInt(),
        description: json['description'] as String? ?? '',
        badge: json['badge'] as String? ?? '',
        displayPrice: json['display_price'] as String? ?? '',
      );

  String get priceLabel =>
      displayPrice.isNotEmpty ? displayPrice : '₱$price';

  /// "30 days of Pro" / "Lifetime access".
  String get lengthLabel {
    if (days == null) return 'Lifetime access';
    if (days == 30) return '1 month of Pro';
    if (days == 365) return '12 months of Pro';
    return '$days days of Pro';
  }
}

/// What the backend can currently sell, and how.
class PaymentConfig {
  final bool enabled;
  final String provider;
  final List<String> methods;
  final bool sandbox;
  final List<PaymentPlan> plans;

  const PaymentConfig({
    required this.enabled,
    required this.provider,
    required this.methods,
    required this.sandbox,
    required this.plans,
  });

  static const PaymentConfig unavailable = PaymentConfig(
    enabled: false,
    provider: 'none',
    methods: [],
    sandbox: false,
    plans: [],
  );

  factory PaymentConfig.fromJson(Map<String, dynamic> json) => PaymentConfig(
        enabled: json['enabled'] == true,
        provider: json['provider'] as String? ?? 'none',
        methods: (json['methods'] as List? ?? [])
            .map((e) => e.toString())
            .toList(),
        sandbox: json['sandbox'] == true,
        plans: (json['plans'] as List? ?? [])
            .map((e) => PaymentPlan.fromJson(e as Map<String, dynamic>))
            .toList(),
      );

  bool get supportsGCash => methods.contains('gcash');
}

/// A checkout the customer must open and pay in GCash.
class Checkout {
  final String reference;
  final String checkoutUrl;
  final String planId;
  final String planName;
  final int amount;
  final String currency;

  const Checkout({
    required this.reference,
    required this.checkoutUrl,
    required this.planId,
    required this.planName,
    required this.amount,
    required this.currency,
  });

  factory Checkout.fromJson(Map<String, dynamic> json) => Checkout(
        reference: json['reference'] as String,
        checkoutUrl: json['checkout_url'] as String,
        planId: json['plan_id'] as String? ?? '',
        planName: json['plan_name'] as String? ?? '',
        amount: (json['amount'] as num?)?.toInt() ?? 0,
        currency: json['currency'] as String? ?? 'PHP',
      );
}

/// Live state of a payment. `paid` means Pro is already switched on.
class PaymentStatus {
  final String reference;
  final String status;
  final bool premium;
  final String? premiumUntil;
  final String message;

  const PaymentStatus({
    required this.reference,
    required this.status,
    required this.premium,
    this.premiumUntil,
    this.message = '',
  });

  bool get isPaid => status == 'paid';
  bool get isPending => status == 'pending';
  bool get isFailed => status == 'failed' || status == 'expired';

  factory PaymentStatus.fromJson(Map<String, dynamic> json) => PaymentStatus(
        reference: json['reference'] as String? ?? '',
        status: json['status'] as String? ?? 'pending',
        premium: json['premium'] == true,
        premiumUntil: json['premium_until'] as String?,
        message: json['message'] as String? ?? '',
      );
}

class PaymentException implements Exception {
  final String message;
  PaymentException(this.message);
  @override
  String toString() => message;
}

/// Talks to the backend's `/api/v1/payments` endpoints.
///
/// The flow is deliberately hands-off: create a checkout, send the customer to
/// GCash, then poll until the gateway confirms. Pro is granted by the server —
/// nobody has to approve anything by hand.
class PaymentService {
  PaymentService({http.Client? client, String? baseUrl})
      : _client = client ?? http.Client(),
        _baseUrl = baseUrl ?? AppConfig.paymentsBaseUrl;

  final http.Client _client;
  final String _baseUrl;

  static const Duration _timeout = Duration(seconds: 20);

  PaymentConfig? _cachedConfig;

  Uri _uri(String path, [Map<String, String>? query]) =>
      Uri.parse('$_baseUrl/api/v1/payments$path')
          .replace(queryParameters: query);

  Map<String, dynamic> _decode(http.Response res) {
    final body = res.body.isEmpty
        ? <String, dynamic>{}
        : jsonDecode(res.body) as Map<String, dynamic>;
    if (res.statusCode >= 400) {
      throw PaymentException(
          body['detail']?.toString() ?? 'Payment service error (${res.statusCode}).');
    }
    return body;
  }

  /// Plans and gateway status. Returns [PaymentConfig.unavailable] when the
  /// backend can't be reached, so the paywall can fall back gracefully.
  Future<PaymentConfig> loadConfig({bool refresh = false}) async {
    if (!refresh && _cachedConfig != null) return _cachedConfig!;
    try {
      final res = await _client.get(_uri('/config')).timeout(_timeout);
      final config = PaymentConfig.fromJson(_decode(res));
      _cachedConfig = config;
      return config;
    } catch (_) {
      return PaymentConfig.unavailable;
    }
  }

  /// Start a GCash checkout for [planId] on [email]'s account.
  Future<Checkout> startCheckout({
    required String planId,
    required String email,
    String uid = '',
    String idToken = '',
  }) async {
    try {
      final res = await _client
          .post(
            _uri('/checkout'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'plan_id': planId,
              'email': email,
              'uid': uid,
              'id_token': idToken,
            }),
          )
          .timeout(_timeout);
      return Checkout.fromJson(_decode(res));
    } on PaymentException {
      rethrow;
    } catch (e) {
      throw PaymentException('Could not reach the payment service: $e');
    }
  }

  Future<PaymentStatus> checkStatus(String reference) async {
    try {
      final res = await _client.get(_uri('/status/$reference')).timeout(_timeout);
      return PaymentStatus.fromJson(_decode(res));
    } on PaymentException {
      rethrow;
    } catch (e) {
      throw PaymentException('Could not check the payment: $e');
    }
  }

  /// Poll until the payment is confirmed (or [timeout] elapses).
  ///
  /// Transient network errors are ignored — the customer may be off Wi-Fi
  /// inside the GCash app — and only a definite result ends the wait.
  Stream<PaymentStatus> watch(
    String reference, {
    Duration interval = const Duration(seconds: 3),
    Duration timeout = const Duration(minutes: 15),
  }) async* {
    final deadline = DateTime.now().add(timeout);
    while (DateTime.now().isBefore(deadline)) {
      await Future<void>.delayed(interval);
      PaymentStatus status;
      try {
        status = await checkStatus(reference);
      } catch (_) {
        continue;
      }
      yield status;
      if (status.isPaid || status.isFailed) return;
    }
  }

  /// Server-side entitlement for an email (used when Firebase isn't wired up).
  Future<bool> isPremium(String email) async {
    try {
      final res = await _client
          .get(_uri('/entitlement', {'email': email}))
          .timeout(_timeout);
      return _decode(res)['premium'] == true;
    } catch (_) {
      return false;
    }
  }

  /// Development helper: mark a mock-gateway payment as paid.
  Future<PaymentStatus> simulatePayment(String reference) async {
    final res = await _client.post(_uri('/mock/pay/$reference')).timeout(_timeout);
    return PaymentStatus.fromJson(_decode(res));
  }
}
