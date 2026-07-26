import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../config.dart';
import '../state/app_state.dart';

/// The upgrade screen. The purchase button currently activates a local
/// dev entitlement; wire it to Google Play Billing / RevenueCat for release.
class PaywallScreen extends StatelessWidget {
  const PaywallScreen({super.key});

  static const _features = [
    (Icons.cable, 'Wiring diagrams', 'Board-specific, colour-coded connections'),
    (Icons.code, 'Code generation', 'Ready-to-flash Arduino & ESP32 sketches'),
    (Icons.all_inclusive, 'Unlimited scans', 'No monthly scan cap'),
    (Icons.history, 'Full project history', 'Every scan saved, forever'),
  ];

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final app = context.watch<AppState>();

    return Scaffold(
      appBar: AppBar(title: const Text('Go Pro')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Icon(Icons.workspace_premium, size: 64, color: scheme.secondary),
              const SizedBox(height: 12),
              Text(
                app.isPremium ? 'You are Pro!' : 'Build faster with Pro',
                textAlign: TextAlign.center,
                style: Theme.of(context)
                    .textTheme
                    .headlineSmall
                    ?.copyWith(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 6),
              Text(
                'From photo to working circuit in one tap.',
                textAlign: TextAlign.center,
                style: TextStyle(color: scheme.onSurfaceVariant),
              ),
              const SizedBox(height: 24),
              for (final f in _features)
                Card(
                  child: ListTile(
                    leading: Icon(f.$1, color: scheme.primary),
                    title: Text(f.$2,
                        style: const TextStyle(fontWeight: FontWeight.w700)),
                    subtitle: Text(f.$3),
                  ),
                ),
              const SizedBox(height: 24),
              if (!app.isPremium) ...[
                FilledButton(
                  onPressed: () async {
                    await context.read<AppState>().activatePremium();
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                            content: Text('Pro activated. Happy building!')),
                      );
                      Navigator.of(context).pop();
                    }
                  },
                  style: FilledButton.styleFrom(
                      minimumSize: const Size.fromHeight(56)),
                  child: Text(
                      'Subscribe — ${AppConfig.subscriptionPrice}',
                      style: const TextStyle(
                          fontSize: 16, fontWeight: FontWeight.w700)),
                ),
                const SizedBox(height: 10),
                Text(
                  'Demo build: tapping Subscribe unlocks Pro locally without '
                  'charging. Production builds use Google Play Billing.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                      fontSize: 11.5, color: scheme.onSurfaceVariant),
                ),
              ] else
                OutlinedButton(
                  onPressed: () async {
                    await context.read<AppState>().cancelPremium();
                    if (context.mounted) Navigator.of(context).pop();
                  },
                  child: const Text('Deactivate Pro (demo)'),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
