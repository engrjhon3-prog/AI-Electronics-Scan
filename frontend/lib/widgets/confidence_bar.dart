import 'package:flutter/material.dart';

/// A labelled confidence meter (0.0 - 1.0).
class ConfidenceBar extends StatelessWidget {
  final double confidence;
  const ConfidenceBar({super.key, required this.confidence});

  Color _color() {
    if (confidence >= 0.75) return const Color(0xFF2E7D32);
    if (confidence >= 0.45) return const Color(0xFFF9A825);
    return const Color(0xFFC62828);
  }

  String _label() {
    if (confidence >= 0.75) return 'High confidence';
    if (confidence >= 0.45) return 'Medium confidence';
    return 'Low confidence';
  }

  @override
  Widget build(BuildContext context) {
    final pct = (confidence.clamp(0.0, 1.0) * 100).round();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(_label(),
                style: TextStyle(
                    color: _color(), fontWeight: FontWeight.w600, fontSize: 13)),
            Text('$pct%',
                style: TextStyle(
                    color: _color(), fontWeight: FontWeight.w700, fontSize: 13)),
          ],
        ),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(6),
          child: LinearProgressIndicator(
            value: confidence.clamp(0.0, 1.0),
            minHeight: 8,
            backgroundColor: _color().withValues(alpha: 0.15),
            valueColor: AlwaysStoppedAnimation(_color()),
          ),
        ),
      ],
    );
  }
}
