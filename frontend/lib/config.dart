/// App-wide configuration.
///
/// Values can be overridden at build time without editing code:
///   flutter build apk --dart-define=API_BASE_URL=https://my-vast-ai-host:8000
///   flutter build apk --dart-define=PAYMENTS_BASE_URL=https://pay.example.com
class AppConfig {
  /// Base URL of the Python backend. Point this at your Vast.ai deployment.
  /// Defaults to a placeholder that you should override for a real build.
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000', // Android emulator -> host machine
  );

  /// Base URL of the payment service (GCash checkout + webhooks). Usually the
  /// same host as the backend; kept separate so payments can live on a stable
  /// public URL while the vision backend moves around.
  static const String _paymentsBaseUrlOverride =
      String.fromEnvironment('PAYMENTS_BASE_URL', defaultValue: '');

  static String get paymentsBaseUrl =>
      _paymentsBaseUrlOverride.isNotEmpty ? _paymentsBaseUrlOverride : apiBaseUrl;

  /// Fallback price shown before the live plan list loads.
  static const String subscriptionPrice = '₱199/mo';

  static const String appName = 'AI Electronics Scanner';

  /// Free tier scan allowance per calendar month.
  static const int freeScansPerMonth = 20;

  /// Support address, used when a customer needs a human after all.
  static const String supportEmail = 'jhonisaacalegre@gmail.com';
}
