import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';

import '../config.dart';
import '../models/scan_result.dart';
import '../services/api_client.dart';
import '../state/app_state.dart';
import 'result_screen.dart';
import 'paywall_screen.dart';

/// The primary screen: capture a component photo and scan it.
class ScanHomeScreen extends StatefulWidget {
  const ScanHomeScreen({super.key});

  @override
  State<ScanHomeScreen> createState() => _ScanHomeScreenState();
}

class _ScanHomeScreenState extends State<ScanHomeScreen> {
  final _picker = ImagePicker();
  bool _busy = false;

  Future<void> _capture(ImageSource source) async {
    final app = context.read<AppState>();
    if (!app.canScan) {
      _showPaywall();
      return;
    }
    final XFile? file = await _picker.pickImage(
      source: source,
      maxWidth: 1600,
      imageQuality: 88,
    );
    if (file == null) return;
    if (!mounted) return;
    setState(() => _busy = true);
    try {
      final ScanResult result = await app.scan(File(file.path));
      if (!mounted) return;
      Navigator.of(context).push(MaterialPageRoute(
        builder: (_) => ResultScreen(result: result, imagePath: file.path),
      ));
    } on ApiException catch (e) {
      _snack(e.message);
    } catch (e) {
      _snack('Something went wrong: $e');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  void _showPaywall() {
    Navigator.of(context)
        .push(MaterialPageRoute(builder: (_) => const PaywallScreen()));
  }

  void _snack(String msg) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)
        .showSnackBar(SnackBar(content: Text(msg)));
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final app = context.watch<AppState>();

    return Scaffold(
      appBar: AppBar(
        title: const Text(AppConfig.appName),
        actions: [
          if (app.isPremium)
            Padding(
              padding: const EdgeInsets.only(right: 12),
              child: Chip(
                avatar: Icon(Icons.workspace_premium,
                    size: 18, color: scheme.secondary),
                label: const Text('Pro'),
                visualDensity: VisualDensity.compact,
              ),
            ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _ServerStatusBanner(reachable: app.serverReachable),
              const SizedBox(height: 20),
              _ScanTarget(busy: _busy),
              const SizedBox(height: 28),
              Text('Identify a component',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w700)),
              const SizedBox(height: 6),
              Text(
                'Point your camera at a resistor, IC, sensor, or module. '
                'Get its pinout, wiring, and ready-to-flash code.',
                style: TextStyle(color: scheme.onSurfaceVariant),
              ),
              const SizedBox(height: 24),
              FilledButton.icon(
                onPressed: _busy ? null : () => _capture(ImageSource.camera),
                icon: const Icon(Icons.camera_alt),
                label: const Text('Scan with camera'),
                style: FilledButton.styleFrom(
                    minimumSize: const Size.fromHeight(56)),
              ),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed:
                    _busy ? null : () => _capture(ImageSource.gallery),
                icon: const Icon(Icons.photo_library_outlined),
                label: const Text('Choose from gallery'),
                style: OutlinedButton.styleFrom(
                    minimumSize: const Size.fromHeight(52)),
              ),
              const SizedBox(height: 24),
              if (!app.isPremium) _FreeQuotaCard(remaining: app.freeScansRemaining),
              const SizedBox(height: 12),
              const _TipsCard(),
            ],
          ),
        ),
      ),
    );
  }
}

class _ScanTarget extends StatelessWidget {
  final bool busy;
  const _ScanTarget({required this.busy});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return AspectRatio(
      aspectRatio: 16 / 10,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          gradient: LinearGradient(
            colors: [
              scheme.primary.withValues(alpha: 0.14),
              scheme.secondary.withValues(alpha: 0.10),
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          border: Border.all(color: scheme.primary.withValues(alpha: 0.35)),
        ),
        child: Center(
          child: busy
              ? Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const CircularProgressIndicator(),
                    const SizedBox(height: 14),
                    Text('Analysing…',
                        style: TextStyle(color: scheme.onSurfaceVariant)),
                  ],
                )
              : Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.memory,
                        size: 64, color: scheme.primary.withValues(alpha: 0.8)),
                    const SizedBox(height: 8),
                    Text('Ready to scan',
                        style: TextStyle(
                            color: scheme.onSurfaceVariant,
                            fontWeight: FontWeight.w600)),
                  ],
                ),
        ),
      ),
    );
  }
}

class _ServerStatusBanner extends StatelessWidget {
  final bool? reachable;
  const _ServerStatusBanner({required this.reachable});

  @override
  Widget build(BuildContext context) {
    if (reachable == null || reachable == true) {
      return const SizedBox.shrink();
    }
    final scheme = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: scheme.errorContainer,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(Icons.cloud_off, color: scheme.onErrorContainer, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              'Scanner service unreachable. Set your server URL in Settings.',
              style: TextStyle(color: scheme.onErrorContainer, fontSize: 12.5),
            ),
          ),
        ],
      ),
    );
  }
}

class _FreeQuotaCard extends StatelessWidget {
  final int remaining;
  const _FreeQuotaCard({required this.remaining});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(Icons.bolt, color: scheme.secondary),
            const SizedBox(width: 12),
            Expanded(
              child: Text('$remaining free scans left this month',
                  style: const TextStyle(fontWeight: FontWeight.w600)),
            ),
            TextButton(
              onPressed: () => Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const PaywallScreen())),
              child: const Text('Go Pro'),
            ),
          ],
        ),
      ),
    );
  }
}

class _TipsCard extends StatelessWidget {
  const _TipsCard();

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    const tips = [
      'Fill the frame with the component.',
      'Use even lighting; avoid glare on the label.',
      'For ICs, keep the printed part number in focus.',
      'For resistors, lay the colour bands flat and sharp.',
    ];
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.tips_and_updates_outlined,
                    size: 18, color: scheme.primary),
                const SizedBox(width: 8),
                const Text('Tips for a good scan',
                    style: TextStyle(fontWeight: FontWeight.w700)),
              ],
            ),
            const SizedBox(height: 8),
            for (final t in tips)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('•  ',
                        style: TextStyle(color: scheme.onSurfaceVariant)),
                    Expanded(
                        child: Text(t,
                            style: TextStyle(
                                color: scheme.onSurfaceVariant, fontSize: 13))),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}
