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
      default:
        return Icons.category_outlined;
    }
  }
}
