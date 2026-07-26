import 'package:flutter/material.dart';

/// App theme — a clean "maker / electronics" palette with a teal-green primary
/// evoking a PCB, warm amber accents, and full light + dark support.
class AppTheme {
  static const Color _seed = Color(0xFF00897B); // teal
  static const Color _accent = Color(0xFFFFB300); // amber

  static ThemeData light() => _build(Brightness.light);
  static ThemeData dark() => _build(Brightness.dark);

  static ThemeData _build(Brightness brightness) {
    final scheme = ColorScheme.fromSeed(
      seedColor: _seed,
      brightness: brightness,
      secondary: _accent,
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor:
          brightness == Brightness.dark ? const Color(0xFF0F1416) : const Color(0xFFF6F8F8),
      appBarTheme: AppBarTheme(
        centerTitle: false,
        elevation: 0,
        backgroundColor: scheme.surface,
        foregroundColor: scheme.onSurface,
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(color: scheme.outlineVariant),
        ),
        clipBehavior: Clip.antiAlias,
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
        ),
      ),
      chipTheme: ChipThemeData(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }

  /// Colour used to badge a component type.
  static Color typeColor(String type, ColorScheme scheme) {
    switch (type) {
      case 'resistor':
        return const Color(0xFFEF6C00);
      case 'capacitor':
        return const Color(0xFF5E35B1);
      case 'led':
        return const Color(0xFFD81B60);
      case 'ic':
        return const Color(0xFF1E88E5);
      case 'sensor':
        return const Color(0xFF00897B);
      case 'module':
        return const Color(0xFF3949AB);
      case 'actuator':
        return const Color(0xFF6D4C41);
      case 'diode':
      case 'transistor':
        return const Color(0xFF00ACC1);
      case 'display':
        return const Color(0xFF7B1FA2);
      case 'board':
        return const Color(0xFF2E7D32);
      case 'power':
        return const Color(0xFFC62828);
      case 'wireless':
        return const Color(0xFF0277BD);
      case 'audio':
        return const Color(0xFFAD1457);
      case 'switch':
        return const Color(0xFF546E7A);
      case 'connector':
        return const Color(0xFF795548);
      case 'inductor':
        return const Color(0xFF8D6E63);
      default:
        return scheme.primary;
    }
  }

  static IconData typeIcon(String type) {
    switch (type) {
      case 'resistor':
        return Icons.horizontal_rule;
      case 'led':
        return Icons.lightbulb_outline;
      case 'ic':
        return Icons.memory;
      case 'sensor':
        return Icons.sensors;
      case 'module':
        return Icons.developer_board;
      case 'actuator':
        return Icons.settings_input_component;
      case 'capacitor':
        return Icons.battery_full;
      case 'display':
        return Icons.tv;
      case 'board':
        return Icons.dashboard_customize;
      case 'power':
        return Icons.bolt;
      case 'wireless':
        return Icons.wifi_tethering;
      case 'audio':
        return Icons.volume_up;
      case 'switch':
        return Icons.toggle_on;
      case 'connector':
        return Icons.cable;
      case 'inductor':
        return Icons.waves;
      case 'diode':
        return Icons.change_history;
      case 'transistor':
        return Icons.hub_outlined;
      default:
        return Icons.category_outlined;
    }
  }
}
