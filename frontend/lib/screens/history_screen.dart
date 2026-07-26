import 'dart:io';

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../state/app_state.dart';
import '../widgets/type_badge.dart';
import 'component_detail_screen.dart';
import 'paywall_screen.dart';

/// Scan history. Free users see their most recent 3 scans; Pro keeps all.
class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key});

  static const int _freeVisible = 3;

  @override
  Widget build(BuildContext context) {
    final app = context.watch<AppState>();
    final entries = app.history;
    final visible =
        app.isPremium ? entries : entries.take(_freeVisible).toList();
    final hiddenCount = entries.length - visible.length;
    final fmt = DateFormat('MMM d, y • HH:mm');

    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan history'),
        actions: [
          if (entries.isNotEmpty)
            IconButton(
              tooltip: 'Clear history',
              icon: const Icon(Icons.delete_sweep_outlined),
              onPressed: () async {
                final ok = await showDialog<bool>(
                  context: context,
                  builder: (ctx) => AlertDialog(
                    title: const Text('Clear all history?'),
                    content: const Text('This cannot be undone.'),
                    actions: [
                      TextButton(
                          onPressed: () => Navigator.pop(ctx, false),
                          child: const Text('Cancel')),
                      FilledButton(
                          onPressed: () => Navigator.pop(ctx, true),
                          child: const Text('Clear')),
                    ],
                  ),
                );
                if (ok == true && context.mounted) {
                  await context.read<AppState>().clearHistory();
                }
              },
            ),
        ],
      ),
      body: entries.isEmpty
          ? const _EmptyHistory()
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                for (final e in visible)
                  Dismissible(
                    key: ValueKey(e.id),
                    direction: DismissDirection.endToStart,
                    background: Container(
                      alignment: Alignment.centerRight,
                      padding: const EdgeInsets.only(right: 20),
                      decoration: BoxDecoration(
                        color: Colors.red.shade400,
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: const Icon(Icons.delete, color: Colors.white),
                    ),
                    onDismissed: (_) =>
                        context.read<AppState>().deleteHistory(e.id),
                    child: Card(
                      child: ListTile(
                        leading: _Thumb(path: e.imagePath, type: e.type),
                        title: Text(e.componentName,
                            style:
                                const TextStyle(fontWeight: FontWeight.w600)),
                        subtitle: Text(
                            '${fmt.format(e.timestamp)}\n'
                            '${(e.confidence * 100).round()}% confidence'),
                        isThreeLine: true,
                        trailing: const Icon(Icons.chevron_right),
                        onTap: () => Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) => ComponentDetailScreen(
                                componentId: e.componentId),
                          ),
                        ),
                      ),
                    ),
                  ),
                if (hiddenCount > 0)
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        children: [
                          Text(
                            '$hiddenCount older scan${hiddenCount == 1 ? '' : 's'} hidden',
                            style:
                                const TextStyle(fontWeight: FontWeight.w600),
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            'Upgrade to Pro to keep your full project history.',
                            textAlign: TextAlign.center,
                            style: TextStyle(fontSize: 13),
                          ),
                          const SizedBox(height: 12),
                          FilledButton(
                            onPressed: () => Navigator.of(context).push(
                                MaterialPageRoute(
                                    builder: (_) => const PaywallScreen())),
                            child: const Text('Unlock full history'),
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

class _Thumb extends StatelessWidget {
  final String? path;
  final String type;
  const _Thumb({required this.path, required this.type});

  @override
  Widget build(BuildContext context) {
    if (path != null && File(path!).existsSync()) {
      return ClipRRect(
        borderRadius: BorderRadius.circular(8),
        child: Image.file(File(path!),
            width: 48, height: 48, fit: BoxFit.cover),
      );
    }
    return TypeBadge(type: type);
  }
}

class _EmptyHistory extends StatelessWidget {
  const _EmptyHistory();

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.history, size: 56, color: scheme.onSurfaceVariant),
          const SizedBox(height: 12),
          const Text('No scans yet',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
          const SizedBox(height: 4),
          Text('Your identified components will appear here.',
              style: TextStyle(color: scheme.onSurfaceVariant)),
        ],
      ),
    );
  }
}
