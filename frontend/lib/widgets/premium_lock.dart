import 'package:flutter/material.dart';

/// A frosted "locked" overlay shown over premium features for free users.
class PremiumLock extends StatelessWidget {
  final String feature;
  final VoidCallback onUnlock;
  const PremiumLock({super.key, required this.feature, required this.onUnlock});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            scheme.secondary.withValues(alpha: 0.16),
            scheme.primary.withValues(alpha: 0.10),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: scheme.secondary.withValues(alpha: 0.4)),
      ),
      child: Column(
        children: [
          Icon(Icons.workspace_premium, size: 40, color: scheme.secondary),
          const SizedBox(height: 12),
          Text('$feature is a Pro feature',
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
          const SizedBox(height: 6),
          Text(
            'Unlock wiring diagrams, code generation, and unlimited scans.',
            textAlign: TextAlign.center,
            style: TextStyle(color: scheme.onSurfaceVariant, fontSize: 13),
          ),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: onUnlock,
            icon: const Icon(Icons.lock_open),
            label: const Text('Upgrade to Pro'),
          ),
        ],
      ),
    );
  }
}
