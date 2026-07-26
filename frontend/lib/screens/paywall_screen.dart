import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';

import '../config.dart';
import '../services/payment_service.dart';
import '../state/app_state.dart';
import 'account_screen.dart';

/// The upgrade screen.
///
/// Pay with GCash and Pro switches on by itself: the gateway confirms the
/// payment to our backend, the backend writes the entitlement, and the app
/// picks it up. Nobody has to approve anything.
class PaywallScreen extends StatefulWidget {
  const PaywallScreen({super.key});

  static const String contactEmail = AppConfig.supportEmail;

  @override
  State<PaywallScreen> createState() => _PaywallScreenState();
}

class _PaywallScreenState extends State<PaywallScreen> {
  static const _features = [
    (Icons.cable, 'Wiring diagrams', 'Board-specific, colour-coded connections'),
    (Icons.code, 'Code generation', 'Ready-to-flash Arduino & ESP32 sketches'),
    (Icons.all_inclusive, 'Unlimited scans', 'No monthly scan cap'),
    (Icons.cloud_done, '7-day cloud storage',
        'Scan photos kept a full week (free: 3 slots, 12 hours)'),
    (Icons.history, 'Full scan history', 'Every scan saved on your device'),
  ];

  PaymentConfig? _config;
  bool _loadingConfig = true;
  String? _selectedPlanId;

  Checkout? _checkout;
  String _payStatus = '';
  bool _starting = false;
  StreamSubscription<PaymentStatus>? _watch;

  @override
  void initState() {
    super.initState();
    _loadConfig();
  }

  @override
  void dispose() {
    _watch?.cancel();
    super.dispose();
  }

  Future<void> _loadConfig() async {
    final app = context.read<AppState>();
    final config = await app.payments.loadConfig(refresh: true);
    if (!mounted) return;
    setState(() {
      _config = config;
      _loadingConfig = false;
      _selectedPlanId ??= config.plans.isEmpty
          ? null
          : (config.plans.firstWhere((p) => p.badge.isNotEmpty,
                  orElse: () => config.plans.first))
              .id;
    });
  }

  PaymentPlan? get _selectedPlan {
    final plans = _config?.plans ?? const <PaymentPlan>[];
    if (plans.isEmpty) return null;
    return plans.firstWhere((p) => p.id == _selectedPlanId,
        orElse: () => plans.first);
  }

  // ------------------------------------------------------------- checkout
  Future<void> _payWithGCash() async {
    final app = context.read<AppState>();
    final plan = _selectedPlan;
    final email = app.user?.email;
    if (plan == null) return;
    if (email == null) {
      _openAccount();
      return;
    }

    setState(() {
      _starting = true;
      _payStatus = 'Opening GCash checkout…';
    });
    try {
      final checkout = await app.payments.startCheckout(
        planId: plan.id,
        email: email,
        uid: app.user?.uid ?? '',
        idToken: await app.auth.idToken(),
      );
      if (!mounted) return;
      setState(() {
        _checkout = checkout;
        _payStatus = 'Waiting for your GCash payment…';
      });
      _listenForPayment(checkout.reference);

      final opened = await launchUrl(
        Uri.parse(checkout.checkoutUrl),
        mode: LaunchMode.externalApplication,
      );
      if (!opened && mounted) {
        setState(() => _payStatus =
            'Could not open the checkout page — copy the link below instead.');
      }
    } on PaymentException catch (e) {
      if (mounted) setState(() => _payStatus = e.message);
    } finally {
      if (mounted) setState(() => _starting = false);
    }
  }

  void _listenForPayment(String reference) {
    final app = context.read<AppState>();
    _watch?.cancel();
    _watch = app.payments.watch(reference).listen((status) async {
      if (!mounted) return;
      if (status.isPaid) {
        await app.applyPaidPayment(
          premiumUntil: status.premiumUntil,
          planName: _selectedPlan?.name ?? 'Pro',
        );
        if (!mounted) return;
        setState(() {
          _checkout = null;
          _payStatus = '';
        });
        _showPaidDialog();
      } else if (status.isFailed) {
        setState(() {
          _checkout = null;
          _payStatus = 'That payment did not go through. Nothing was charged — '
              'you can try again.';
        });
      }
    });
  }

  Future<void> _simulatePayment() async {
    final app = context.read<AppState>();
    final reference = _checkout?.reference;
    if (reference == null) return;
    try {
      await app.payments.simulatePayment(reference);
    } on PaymentException catch (e) {
      if (mounted) setState(() => _payStatus = e.message);
    }
  }

  void _showPaidDialog() {
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        icon: const Icon(Icons.verified, size: 40, color: Colors.green),
        title: const Text('Payment received — you are Pro!'),
        content: const Text(
            'Wiring diagrams, code generation and unlimited scans are unlocked '
            'on this account right now.'),
        actions: [
          FilledButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Start building'),
          ),
        ],
      ),
    );
  }

  void _openAccount() => Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => const AccountScreen()));

  // ---------------------------------------------------------------- build
  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final app = context.watch<AppState>();
    final config = _config;
    final gcashReady = config != null && config.enabled && config.plans.isNotEmpty;

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
                    ? _activePlanLine(app)
                    : 'From photo to working circuit in one tap — pay with '
                        'GCash and unlock instantly.',
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
                if (_loadingConfig)
                  const Padding(
                    padding: EdgeInsets.all(24),
                    child: Center(child: CircularProgressIndicator()),
                  )
                else if (gcashReady)
                  _buildGCashSection(app, config)
                else
                  _buildManualSection(app),
              ] else if (app.premiumUntil != null && gcashReady) ...[
                Row(
                  children: [
                    Icon(Icons.event_available, color: scheme.primary),
                    const SizedBox(width: 8),
                    const Expanded(
                      child: Text(
                        'Renew early — extra time stacks on top of the days '
                        'you have left.',
                        style: TextStyle(fontSize: 13),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                _buildGCashSection(app, config),
              ],
            ],
          ),
        ),
      ),
    );
  }

  String _activePlanLine(AppState app) {
    final until = app.premiumUntil;
    final plan = app.planName.isEmpty ? 'Pro' : app.planName;
    if (until == null) return '$plan — all features unlocked on this account.';
    final days = until.difference(DateTime.now()).inDays;
    return '$plan — active for $days more day${days == 1 ? '' : 's'} '
        '(until ${until.year}-${until.month.toString().padLeft(2, '0')}-'
        '${until.day.toString().padLeft(2, '0')}).';
  }

  // ------------------------------------------------------------- sections
  Widget _buildGCashSection(AppState app, PaymentConfig config) {
    final scheme = Theme.of(context).colorScheme;
    final waiting = _checkout != null;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Icon(Icons.account_balance_wallet, color: scheme.primary),
            const SizedBox(width: 8),
            const Text('Choose a plan',
                style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
          ],
        ),
        const SizedBox(height: 10),
        for (final plan in config.plans)
          _PlanCard(
            plan: plan,
            selected: plan.id == _selectedPlanId,
            onTap: waiting
                ? null
                : () => setState(() => _selectedPlanId = plan.id),
          ),
        const SizedBox(height: 12),
        if (!app.signedIn)
          Card(
            color: scheme.errorContainer.withValues(alpha: 0.35),
            child: ListTile(
              leading: const Icon(Icons.account_circle_outlined),
              title: const Text('Sign in first'),
              subtitle: const Text(
                  'Pro is tied to your account email, so we know whose app to '
                  'unlock after payment.'),
            ),
          ),
        if (waiting) ...[
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(_payStatus,
                            style:
                                const TextStyle(fontWeight: FontWeight.w600)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Finish the payment in GCash, then come back here — this '
                    'screen unlocks by itself. Reference:',
                    style: TextStyle(fontSize: 12.5),
                  ),
                  const SizedBox(height: 4),
                  SelectableText(_checkout!.reference,
                      style: const TextStyle(
                          fontFamily: 'monospace', fontSize: 12.5)),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    children: [
                      OutlinedButton.icon(
                        onPressed: () => launchUrl(
                          Uri.parse(_checkout!.checkoutUrl),
                          mode: LaunchMode.externalApplication,
                        ),
                        icon: const Icon(Icons.open_in_new, size: 18),
                        label: const Text('Reopen checkout'),
                      ),
                      OutlinedButton.icon(
                        onPressed: () async {
                          await Clipboard.setData(
                              ClipboardData(text: _checkout!.checkoutUrl));
                          if (!mounted) return;
                          ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                  content: Text('Checkout link copied')));
                        },
                        icon: const Icon(Icons.copy, size: 18),
                        label: const Text('Copy link'),
                      ),
                      TextButton(
                        onPressed: () {
                          _watch?.cancel();
                          setState(() {
                            _checkout = null;
                            _payStatus = '';
                          });
                        },
                        child: const Text('Cancel'),
                      ),
                      if (config.sandbox)
                        TextButton.icon(
                          onPressed: _simulatePayment,
                          icon: const Icon(Icons.science, size: 18),
                          label: const Text('Simulate payment (dev)'),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ] else ...[
          FilledButton.icon(
            onPressed: _starting ? null : _payWithGCash,
            icon: _starting
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(
                        strokeWidth: 2, color: Colors.white),
                  )
                : const Icon(Icons.account_balance_wallet),
            label: Text(app.signedIn
                ? 'Pay ${_selectedPlan?.priceLabel ?? ''} with GCash'
                : 'Sign in to pay with GCash'),
            style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(54)),
          ),
          if (_payStatus.isNotEmpty) ...[
            const SizedBox(height: 10),
            Text(_payStatus,
                textAlign: TextAlign.center,
                style: TextStyle(color: scheme.error, fontSize: 13)),
          ],
          const SizedBox(height: 10),
          Text(
            config.sandbox
                ? 'Development gateway — no real money moves.'
                : 'Secure checkout hosted by ${config.provider}. Pro activates '
                    'automatically once GCash confirms the payment — no waiting '
                    'for approval.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 12, color: scheme.onSurfaceVariant),
          ),
        ],
        const SizedBox(height: 16),
        TextButton.icon(
          onPressed: _openAccount,
          icon: Icon(app.signedIn
              ? Icons.manage_accounts
              : Icons.account_circle_outlined),
          label: Text(app.signedIn
              ? 'Manage my account'
              : 'Create account / Sign in'),
        ),
      ],
    );
  }

  /// Shown when the payment service is unreachable or not configured yet.
  Widget _buildManualSection(AppState app) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Card / GCash checkout is offline',
                    style: TextStyle(fontWeight: FontWeight.w700)),
                const SizedBox(height: 8),
                const Text(
                  'The payment service could not be reached, so in-app GCash '
                  'checkout is unavailable right now. Retry in a moment, or '
                  'email us and we will sort it out.',
                  style: TextStyle(fontSize: 13.5),
                ),
                const SizedBox(height: 12),
                OutlinedButton.icon(
                  onPressed: () async {
                    await Clipboard.setData(const ClipboardData(
                        text: PaywallScreen.contactEmail));
                    if (!mounted) return;
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
                        content: Text('Email address copied')));
                  },
                  icon: const Icon(Icons.copy, size: 18),
                  label: const Text(PaywallScreen.contactEmail),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        FilledButton.icon(
          onPressed: () {
            setState(() => _loadingConfig = true);
            _loadConfig();
          },
          icon: const Icon(Icons.refresh),
          label: const Text('Retry'),
          style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(54)),
        ),
      ],
    );
  }
}

class _PlanCard extends StatelessWidget {
  final PaymentPlan plan;
  final bool selected;
  final VoidCallback? onTap;

  const _PlanCard({required this.plan, required this.selected, this.onTap});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      elevation: selected ? 2 : 0,
      color: selected ? scheme.primaryContainer.withValues(alpha: 0.45) : null,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
        side: BorderSide(
          color: selected ? scheme.primary : scheme.outlineVariant,
          width: selected ? 2 : 1,
        ),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              Icon(
                selected ? Icons.radio_button_checked : Icons.radio_button_off,
                color: selected ? scheme.primary : scheme.outline,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Flexible(
                          child: Text(plan.name,
                              style: const TextStyle(
                                  fontWeight: FontWeight.w800, fontSize: 15)),
                        ),
                        if (plan.badge.isNotEmpty) ...[
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: scheme.secondary.withValues(alpha: 0.18),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Text(plan.badge,
                                style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w700,
                                    color: scheme.secondary)),
                          ),
                        ],
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text(plan.lengthLabel,
                        style: TextStyle(
                            fontSize: 12.5, color: scheme.onSurfaceVariant)),
                    if (plan.description.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(plan.description,
                          style: const TextStyle(fontSize: 12.5)),
                    ],
                  ],
                ),
              ),
              const SizedBox(width: 10),
              Text(plan.priceLabel,
                  style: TextStyle(
                      fontWeight: FontWeight.w900,
                      fontSize: 16,
                      color: scheme.primary)),
            ],
          ),
        ),
      ),
    );
  }
}
