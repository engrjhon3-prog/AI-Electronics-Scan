import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../config.dart';
import '../state/app_state.dart';
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
                    app.isPremium
                        ? Icons.workspace_premium
                        : Icons.person_outline,
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
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.dns_outlined),
                  title: const Text('Backend server'),
                  subtitle: Text(AppConfig.apiBaseUrl),
                ),
                ListTile(
                  leading: Icon(
                    app.serverReachable == true
                        ? Icons.cloud_done_outlined
                        : Icons.cloud_off_outlined,
                    color: app.serverReachable == true
                        ? Colors.green
                        : scheme.error,
                  ),
                  title: Text(app.serverReachable == true
                      ? 'Connected'
                      : app.serverReachable == false
                          ? 'Unreachable'
                          : 'Checking…'),
                  trailing: IconButton(
                    icon: const Icon(Icons.refresh),
                    onPressed: () => context.read<AppState>().checkServer(),
                  ),
                ),
              ],
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
