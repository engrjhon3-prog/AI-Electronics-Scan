import 'package:flutter/material.dart';

import '../models/component.dart';

/// Renders a component's pinout as a readable list with colour-coded pin types.
class PinoutTable extends StatelessWidget {
  final List<Pin> pins;
  const PinoutTable({super.key, required this.pins});

  static const Map<String, Color> _pinColors = {
    'power': Color(0xFFE53935),
    'ground': Color(0xFF424242),
    'digital': Color(0xFF1E88E5),
    'analog': Color(0xFF8E24AA),
    'pwm': Color(0xFF00897B),
    'i2c': Color(0xFFF4511E),
    'spi': Color(0xFF6D4C41),
    'uart': Color(0xFF3949AB),
    'signal': Color(0xFF546E7A),
    'nc': Color(0xFFBDBDBD),
  };

  @override
  Widget build(BuildContext context) {
    if (pins.isEmpty) {
      return const Text('No pinout data available.');
    }
    return Column(
      children: [
        for (final pin in pins) _PinRow(pin: pin, color: _pinColors[pin.type] ?? Colors.grey),
      ],
    );
  }
}

class _PinRow extends StatelessWidget {
  final Pin pin;
  final Color color;
  const _PinRow({required this.pin, required this.color});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 30,
            height: 30,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text('${pin.number}',
                style: TextStyle(fontWeight: FontWeight.w700, color: color)),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Flexible(
                      child: Text(pin.name,
                          style: const TextStyle(fontWeight: FontWeight.w700)),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding:
                          const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: color.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(pin.type.toUpperCase(),
                          style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w700,
                              color: color)),
                    ),
                  ],
                ),
                if (pin.description.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 2),
                    child: Text(pin.description,
                        style: TextStyle(
                            fontSize: 12.5,
                            color: scheme.onSurfaceVariant)),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
