import 'package:flutter/material.dart';

import '../theme.dart';

/// A small coloured chip showing a component's type with an icon.
class TypeBadge extends StatelessWidget {
  final String type;
  final bool large;
  const TypeBadge({super.key, required this.type, this.large = false});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final color = AppTheme.typeColor(type, scheme);
    return Container(
      padding: EdgeInsets.symmetric(
          horizontal: large ? 12 : 8, vertical: large ? 6 : 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.14),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(AppTheme.typeIcon(type), size: large ? 18 : 14, color: color),
          const SizedBox(width: 6),
          Text(
            type.isEmpty ? 'unknown' : type,
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.w600,
              fontSize: large ? 14 : 12,
            ),
          ),
        ],
      ),
    );
  }
}
