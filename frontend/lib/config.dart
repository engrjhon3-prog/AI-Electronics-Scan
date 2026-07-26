/// App-wide configuration.
///
/// The backend URL can be overridden at build time without editing code:
///   flutter build apk --dart-define=API_BASE_URL=https://my-vast-ai-host:8000
class AppConfig {
  /// Base URL of the Python backend. Point this at your Vast.ai deployment.
  /// Defaults to a placeholder that you should override for a real build.
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000', // Android emulator -> host machine
  );

  /// Monthly price shown on the paywall (display only).
  static const String subscriptionPrice = r'$3.99/mo';

  static const String appName = 'AI Electronics Scanner';

  /// Free tier scan allowance per calendar month.
  static const int freeScansPerMonth = 20;
}
