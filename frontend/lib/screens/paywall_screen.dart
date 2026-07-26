import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import '../config.dart';
import '../state/app_state.dart';
import 'account_screen.dart';

/// The upgrade screen. Subscriptions are activated on your account by the
/// team after payment — the app then unlocks automatically.
class PaywallScreen extends StatelessWidget {
  const PaywallScreen({super.key});

  static const String contactEmail = 'jhonisaacalegre@gmail.com';

  static const _features = [
    (Icons.cable, 'Wiring diagrams', 'Board-specific, colour-coded connections'),
    (Icons.code, 'Code generation', 'Ready-to-flash Arduino & ESP32 sketches'),
    (Icons.all_inclusive, 'Unlimited scans', 'No monthly scan cap'),
    (Icons.cloud_done, '7-day cloud storage', 'Scan photos kept a full week (free: 3 slots, 12 hours)'),
    (Icons.history, 'Full scan history', 'Every scan saved on your device'),
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
                app.isPremium
                    ? 'All features are unlocked on this account.'
                    : 'From photo to working circuit in one tap — '
                        '${AppConfig.subscriptionPrice}.',
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
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('How to subscribe',
                            style: TextStyle(fontWeight: FontWeight.w700)),
                        const SizedBox(height: 10),
                        _Step(
                          n: 1,
                          text: app.signedIn
                              ? 'Account ready: ${app.user?.email}'
                              : 'Create your account (button below).',
                          done: app.signedIn,
                        ),
                        _Step(
                          n: 2,
                          text: 'Email us at $contactEmail with your account '
                              'email — we\'ll send payment options '
                              '(${AppConfig.subscriptionPrice}).',
                        ),
                        _Step(
                          n: 3,
                          text: 'Once payment is confirmed, Pro activates on '
                              'your account — pull refresh in Account.',
                        ),
                        const SizedBox(height: 8),
                        OutlinedButton.icon(
                          onPressed: () async {
                            await Clipboard.setData(
                                const ClipboardData(text: contactEmail));
                            if (context.mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                      content:
                                          Text('Email address copied')));
                            }
                          },
                          icon: const Icon(Icons.copy, size: 18),
                          label: const Text(contactEmail),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                FilledButton.icon(
                  onPressed: () => Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const AccountScreen())),
                  icon: Icon(app.signedIn
                      ? Icons.refresh
                      : Icons.account_circle_outlined),
                  label: Text(app.signedIn
                      ? 'Open my account'
                      : 'Create account / Sign in'),
                  style: FilledButton.styleFrom(
                      minimumSize: const Size.fromHeight(54)),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _Step extends StatelessWidget {
  final int n;
  final String text;
  final bool done;
  const _Step({required this.n, required this.text, this.done = false});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 24,
            height: 24,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: done
                  ? Colors.green.withValues(alpha: 0.18)
                  : scheme.primary.withValues(alpha: 0.12),
              shape: BoxShape.circle,
            ),
            child: done
                ? const Icon(Icons.check, size: 15, color: Colors.green)
                : Text('$n',
                    style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w800,
                        color: scheme.primary)),
          ),
          const SizedBox(width: 10),
          Expanded(
              child: Text(text, style: const TextStyle(fontSize: 13.5))),
        ],
      ),
    );
  }
}
