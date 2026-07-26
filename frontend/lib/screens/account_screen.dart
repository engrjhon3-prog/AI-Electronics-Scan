import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../services/auth_service.dart';
import '../services/cloud_uploads_service.dart';
import '../state/app_state.dart';
import 'paywall_screen.dart';

/// Account: sign in / sign up, plan status, cloud uploads, and (for admins)
/// the panel that grants Pro to customers after they subscribe.
class AccountScreen extends StatelessWidget {
  const AccountScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final app = context.watch<AppState>();
    return Scaffold(
      appBar: AppBar(title: const Text('Account')),
      body: !app.auth.isAvailable
          ? const Center(
              child: Padding(
                padding: EdgeInsets.all(24),
                child: Text(
                    'Accounts are not available in this build. '
                    'Scanning still works fully offline.',
                    textAlign: TextAlign.center),
              ),
            )
          : app.signedIn
              ? const _ProfileView()
              : const _AuthForm(),
    );
  }
}

// ---------------------------------------------------------------- sign in/up

class _AuthForm extends StatefulWidget {
  const _AuthForm();

  @override
  State<_AuthForm> createState() => _AuthFormState();
}

class _AuthFormState extends State<_AuthForm> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _busy = false;
  bool _creating = false;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final app = context.read<AppState>();
    setState(() => _busy = true);
    try {
      if (_creating) {
        await app.auth.signUp(_email.text, _password.text);
      } else {
        await app.auth.signIn(_email.text, _password.text);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(AuthService.describeError(e))));
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _resetPassword() async {
    final app = context.read<AppState>();
    if (_email.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Enter your email first.')));
      return;
    }
    try {
      await app.auth.sendPasswordReset(_email.text);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Password reset email sent.')));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(AuthService.describeError(e))));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Icon(Icons.account_circle, size: 72, color: scheme.primary),
          const SizedBox(height: 12),
          Text(
            _creating ? 'Create your account' : 'Welcome back',
            textAlign: TextAlign.center,
            style: Theme.of(context)
                .textTheme
                .headlineSmall
                ?.copyWith(fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 6),
          Text(
            'An account saves your scan photos to the cloud and unlocks Pro '
            'once subscribed.',
            textAlign: TextAlign.center,
            style: TextStyle(color: scheme.onSurfaceVariant, fontSize: 13),
          ),
          const SizedBox(height: 24),
          TextField(
            controller: _email,
            keyboardType: TextInputType.emailAddress,
            autocorrect: false,
            decoration: const InputDecoration(
              labelText: 'Email',
              prefixIcon: Icon(Icons.mail_outline),
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _password,
            obscureText: true,
            decoration: const InputDecoration(
              labelText: 'Password',
              prefixIcon: Icon(Icons.lock_outline),
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 20),
          FilledButton(
            onPressed: _busy ? null : _submit,
            style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(52)),
            child: _busy
                ? const SizedBox(
                    width: 20, height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2))
                : Text(_creating ? 'Create account' : 'Sign in'),
          ),
          TextButton(
            onPressed: () => setState(() => _creating = !_creating),
            child: Text(_creating
                ? 'Already have an account? Sign in'
                : 'New here? Create an account'),
          ),
          if (!_creating)
            TextButton(
              onPressed: _resetPassword,
              child: const Text('Forgot password?'),
            ),
        ],
      ),
    );
  }
}

// ------------------------------------------------------------------- profile

class _ProfileView extends StatelessWidget {
  const _ProfileView();

  /// "Pro Yearly — renews Mar 3, 2027" / "Free plan".
  String _planLine(AppState app) {
    if (app.isAdmin) return 'Admin • Pro plan';
    if (!app.isPremium) return 'Free plan';
    final plan = app.planName.isEmpty ? 'Pro plan' : app.planName;
    final until = app.premiumUntil;
    if (until == null) return '$plan — all features unlocked';
    return '$plan — active until ${DateFormat('MMM d, y').format(until)}';
  }

  @override
  Widget build(BuildContext context) {
    final app = context.watch<AppState>();
    final scheme = Theme.of(context).colorScheme;
    final email = app.user?.email ?? '';

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          child: ListTile(
            leading: Icon(
              app.isPremium ? Icons.workspace_premium : Icons.person_outline,
              color: app.isPremium ? scheme.secondary : scheme.primary,
              size: 34,
            ),
            title: Text(email,
                style: const TextStyle(fontWeight: FontWeight.w700)),
            subtitle: Text(_planLine(app)),
            trailing: IconButton(
              tooltip: 'Refresh subscription status',
              icon: const Icon(Icons.refresh),
              onPressed: () async {
                await app.refreshEntitlement();
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                      content: Text(app.isPremium
                          ? 'Pro is active on this account.'
                          : 'No active subscription yet.')));
                }
              },
            ),
          ),
        ),
        if (!app.isPremium)
          Card(
            child: ListTile(
              leading: Icon(Icons.workspace_premium, color: scheme.secondary),
              title: const Text('Upgrade to Pro'),
              subtitle: const Text(
                  'Pay with GCash — unlocks instantly, no waiting for approval'),
              trailing: FilledButton(
                onPressed: () => Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const PaywallScreen())),
                child: const Text('Go Pro'),
              ),
            ),
          )
        else if (app.premiumUntil != null)
          Card(
            child: ListTile(
              leading: Icon(Icons.event_repeat, color: scheme.secondary),
              title: const Text('Renew with GCash'),
              subtitle: Text(
                  'Renews to ${DateFormat('MMM d, y').format(app.premiumUntil!)} '
                  '— pay early and the days stack.'),
              trailing: OutlinedButton(
                onPressed: () => Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const PaywallScreen())),
                child: const Text('Renew'),
              ),
            ),
          ),
        const SizedBox(height: 8),
        _CloudUploadsSection(uid: app.user!.uid),
        if (app.isAdmin) ...[
          const SizedBox(height: 8),
          const _AdminPanel(),
        ],
        const SizedBox(height: 8),
        Card(
          child: ListTile(
            leading: Icon(Icons.logout, color: scheme.error),
            title: const Text('Sign out'),
            onTap: () => context.read<AppState>().signOut(),
          ),
        ),
      ],
    );
  }
}

// ------------------------------------------------------------- cloud uploads

class _CloudUploadsSection extends StatelessWidget {
  final String uid;
  const _CloudUploadsSection({required this.uid});

  String _remaining(Duration d) {
    if (d.inDays >= 1) return '${d.inDays}d ${d.inHours % 24}h left';
    if (d.inHours >= 1) return '${d.inHours}h ${d.inMinutes % 60}m left';
    return '${d.inMinutes}m left';
  }

  @override
  Widget build(BuildContext context) {
    final app = context.watch<AppState>();
    final scheme = Theme.of(context).colorScheme;
    final fmt = DateFormat('MMM d, HH:mm');

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.cloud_outlined, size: 20, color: scheme.primary),
                const SizedBox(width: 8),
                const Text('Cloud uploads',
                    style: TextStyle(fontWeight: FontWeight.w700)),
                const Spacer(),
                Text(
                  app.isPremium ? 'kept 7 days' : '3 slots • 12h each',
                  style: TextStyle(
                      fontSize: 12, color: scheme.onSurfaceVariant),
                ),
              ],
            ),
            const SizedBox(height: 8),
            StreamBuilder<List<CloudUpload>>(
              stream: app.uploads.stream(uid),
              builder: (context, snap) {
                if (snap.hasError) {
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    child: Text('Could not load uploads.',
                        style: TextStyle(color: scheme.onSurfaceVariant)),
                  );
                }
                final items = snap.data ?? [];
                if (items.isEmpty) {
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    child: Text(
                        'No cloud uploads yet — scan a component while '
                        'signed in and the photo is saved here.',
                        style: TextStyle(
                            fontSize: 13, color: scheme.onSurfaceVariant)),
                  );
                }
                return Column(
                  children: [
                    for (final u in items)
                      ListTile(
                        contentPadding: EdgeInsets.zero,
                        leading: ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: Image.memory(u.imageBytes,
                              width: 48, height: 48, fit: BoxFit.cover),
                        ),
                        title: Text(u.name,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style:
                                const TextStyle(fontWeight: FontWeight.w600)),
                        subtitle: Text(
                            '${fmt.format(u.createdAt)} • ${_remaining(u.remaining)}'),
                        trailing: IconButton(
                          icon: const Icon(Icons.delete_outline),
                          onPressed: () =>
                              app.uploads.delete(uid, u.id),
                        ),
                      ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

// --------------------------------------------------------------- admin panel

class _AdminPanel extends StatefulWidget {
  const _AdminPanel();

  @override
  State<_AdminPanel> createState() => _AdminPanelState();
}

class _AdminPanelState extends State<_AdminPanel> {
  final _customerEmail = TextEditingController();
  bool _busy = false;

  @override
  void dispose() {
    _customerEmail.dispose();
    super.dispose();
  }

  Future<void> _set(bool premium) async {
    final app = context.read<AppState>();
    final email = _customerEmail.text.trim();
    if (email.isEmpty || !email.contains('@')) {
      ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Enter the customer\'s email.')));
      return;
    }
    setState(() => _busy = true);
    try {
      if (premium) {
        await app.auth.grantPremium(email);
      } else {
        await app.auth.revokePremium(email);
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text(premium
                ? 'Pro granted to $email'
                : 'Pro revoked for $email')));
        _customerEmail.clear();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('Failed: $e')));
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.admin_panel_settings,
                    size: 20, color: scheme.secondary),
                const SizedBox(width: 8),
                const Text('Admin — manage subscriptions',
                    style: TextStyle(fontWeight: FontWeight.w700)),
              ],
            ),
            const SizedBox(height: 6),
            Text(
              'After a customer pays, grant Pro to their account email. '
              'It activates the next time their app refreshes.',
              style:
                  TextStyle(fontSize: 12.5, color: scheme.onSurfaceVariant),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _customerEmail,
              keyboardType: TextInputType.emailAddress,
              autocorrect: false,
              decoration: const InputDecoration(
                labelText: 'Customer email',
                prefixIcon: Icon(Icons.mail_outline),
                border: OutlineInputBorder(),
                isDense: true,
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    onPressed: _busy ? null : () => _set(true),
                    icon: const Icon(Icons.check),
                    label: const Text('Grant Pro'),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _busy ? null : () => _set(false),
                    icon: const Icon(Icons.close),
                    label: const Text('Revoke'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
