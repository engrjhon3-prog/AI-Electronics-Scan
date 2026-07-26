import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../config.dart';
import '../state/app_state.dart';
import 'account_screen.dart';
import 'paywall_screen.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final app = context.watch<AppState>();
    final scheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Column(
              children: [
                ListTile(
                  leading: Icon(
                    app.signedIn
                        ? Icons.account_circle
                        : Icons.account_circle_outlined,
                    color: scheme.primary,
                  ),
                  title: Text(
                      app.signedIn
                          ? (app.user?.email ?? 'Account')
                          : 'Sign in / Create account',
                      style: const TextStyle(fontWeight: FontWeight.w700)),
                  subtitle: Text(app.signedIn
                      ? 'Manage your account & cloud uploads'
                      : 'Save scans to the cloud and unlock Pro'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => Navigator.of(context).push(MaterialPageRoute(
                      builder: (_) => const AccountScreen())),
                ),
                const Divider(height: 1),
                ListTile(
                  leading: Icon(
                    app.isPremium
                        ? Icons.workspace_premium
                        : Icons.bolt_outlined,
                    color:
                        app.isPremium ? scheme.secondary : scheme.primary,
                  ),
                  title: Text(app.isPremium ? 'Pro plan' : 'Free plan',
                      style: const TextStyle(fontWeight: FontWeight.w700)),
                  subtitle: Text(app.isPremium
                      ? 'All features unlocked'
                      : '${app.freeScansRemaining} free scans left this month'),
                  trailing: app.isPremium
                      ? null
                      : FilledButton(
                          onPressed: () => Navigator.of(context).push(
                              MaterialPageRoute(
                                  builder: (_) => const PaywallScreen())),
                          child: const Text('Upgrade'),
                        ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          Card(
            child: ListTile(
              leading: Icon(Icons.offline_bolt_outlined,
                  color: scheme.primary),
              title: const Text('Works fully offline'),
              subtitle: Text(
                  'Recognition and the ${app.components.length}-component '
                  'database run on your phone — no internet needed.'),
            ),
          ),
          const SizedBox(height: 12),
          Card(
            child: Column(
              children: [
                const ListTile(
                  leading: Icon(Icons.info_outline),
                  title: Text('About'),
                  subtitle: Text(
                      '${AppConfig.appName}\nIdentify components, get pinouts, '
                      'wiring diagrams & code.'),
                  isThreeLine: true,
                ),
                ListTile(
                  leading: const Icon(Icons.science_outlined),
                  title: const Text('Version'),
                  subtitle: const Text('1.0.0'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.warning_amber_outlined,
                          size: 18, color: scheme.secondary),
                      const SizedBox(width: 8),
                      const Text('Safety note',
                          style: TextStyle(fontWeight: FontWeight.w700)),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Wiring suggestions are a starting point. Always double-check '
                    'voltage levels and polarity before powering a circuit, and '
                    'never work with mains voltage unless qualified.',
                    style: TextStyle(
                        fontSize: 13, color: scheme.onSurfaceVariant),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
