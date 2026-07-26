import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:provider/provider.dart';

import '../models/component.dart';
import '../models/wiring.dart';
import '../state/app_state.dart';
import '../widgets/code_block.dart';
import '../widgets/pinout_table.dart';
import '../widgets/premium_lock.dart';
import '../widgets/type_badge.dart';
import 'paywall_screen.dart';

/// Component detail: Overview (pinout) / Wiring / Code tabs.
/// All data comes from the bundled offline knowledge base; Wiring and Code
/// are Pro features gated locally through AppState.
class ComponentDetailScreen extends StatefulWidget {
  final String componentId;
  const ComponentDetailScreen({super.key, required this.componentId});

  @override
  State<ComponentDetailScreen> createState() => _ComponentDetailScreenState();
}

class _ComponentDetailScreenState extends State<ComponentDetailScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabs;
  String? _board;

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabs.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final app = context.watch<AppState>();
    final comp = app.getComponent(widget.componentId);

    if (comp == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Component')),
        body: const Center(child: Text('Component not found.')),
      );
    }

    final board = _board ??
        (comp.supportedBoards.isNotEmpty ? comp.supportedBoards.first : 'uno');

    return Scaffold(
      appBar: AppBar(
        title: Text(comp.name),
        bottom: TabBar(
          controller: _tabs,
          tabs: const [
            Tab(text: 'Overview'),
            Tab(text: 'Wiring'),
            Tab(text: 'Code'),
          ],
        ),
      ),
      body: Column(
        children: [
          if (comp.supportedBoards.length > 1)
            _BoardSelector(
              boards: comp.supportedBoards,
              selected: board,
              onChanged: (b) => setState(() => _board = b),
            ),
          Expanded(
            child: TabBarView(
              controller: _tabs,
              children: [
                _OverviewTab(component: comp),
                _WiringTab(componentId: comp.id, board: board),
                _CodeTab(componentId: comp.id, board: board),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _BoardSelector extends StatelessWidget {
  final List<String> boards;
  final String selected;
  final ValueChanged<String> onChanged;
  const _BoardSelector(
      {required this.boards, required this.selected, required this.onChanged});

  String _label(String b) {
    switch (b) {
      case 'uno':
        return 'Arduino Uno';
      case 'nano':
        return 'Arduino Nano';
      case 'esp32':
        return 'ESP32';
      case 'esp8266':
        return 'ESP8266';
      default:
        return b;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 12, 12, 0),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: [
            for (final b in boards)
              Padding(
                padding: const EdgeInsets.only(right: 8),
                child: ChoiceChip(
                  label: Text(_label(b)),
                  selected: b == selected,
                  onSelected: (_) => onChanged(b),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _OverviewTab extends StatelessWidget {
  final Component component;
  const _OverviewTab({required this.component});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Row(
          children: [
            TypeBadge(type: component.type, large: true),
            const SizedBox(width: 8),
            if (component.package.isNotEmpty)
              Chip(
                label: Text(component.package),
                visualDensity: VisualDensity.compact,
              ),
          ],
        ),
        const SizedBox(height: 16),
        if (component.description.isNotEmpty)
          Text(component.description,
              style: const TextStyle(fontSize: 15, height: 1.4)),
        const SizedBox(height: 24),
        Text('Pinout',
            style: Theme.of(context)
                .textTheme
                .titleLarge
                ?.copyWith(fontWeight: FontWeight.w700)),
        const SizedBox(height: 8),
        PinoutTable(pins: component.pins),
        if (component.datasheetUrl != null) ...[
          const SizedBox(height: 20),
          Row(
            children: [
              Icon(Icons.description_outlined,
                  size: 18, color: scheme.primary),
              const SizedBox(width: 8),
              Expanded(
                child: SelectableText(component.datasheetUrl!,
                    style: TextStyle(color: scheme.primary, fontSize: 12.5)),
              ),
            ],
          ),
        ],
        const SizedBox(height: 24),
      ],
    );
  }
}

class _WiringTab extends StatelessWidget {
  final String componentId;
  final String board;
  const _WiringTab({required this.componentId, required this.board});

  @override
  Widget build(BuildContext context) {
    final app = context.watch<AppState>();
    if (!app.isPremium) {
      return _ProGate(feature: 'Wiring diagrams');
    }
    final WiringDiagram? d = app.repo.getWiring(componentId, board);
    if (d == null) {
      return const Center(
          child: Text('No wiring diagram for this board yet.'));
    }
    final scheme = Theme.of(context).colorScheme;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (d.svg != null)
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: scheme.outlineVariant),
            ),
            child: SvgPicture.string(d.svg!, height: 260),
          ),
        const SizedBox(height: 20),
        Text('Connections',
            style: Theme.of(context)
                .textTheme
                .titleLarge
                ?.copyWith(fontWeight: FontWeight.w700)),
        const SizedBox(height: 8),
        for (final c in d.connections)
          Card(
            child: ListTile(
              dense: true,
              leading: const Icon(Icons.cable),
              title: Text('${c.fromPin}  →  ${c.toPin}',
                  style: const TextStyle(fontWeight: FontWeight.w600)),
              subtitle: c.note.isEmpty ? null : Text(c.note),
            ),
          ),
        if (d.notes.isNotEmpty) ...[
          const SizedBox(height: 12),
          for (final n in d.notes)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 3),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Icons.info_outline, size: 16, color: scheme.secondary),
                  const SizedBox(width: 8),
                  Expanded(
                      child: Text(n, style: const TextStyle(fontSize: 13))),
                ],
              ),
            ),
        ],
        const SizedBox(height: 24),
      ],
    );
  }
}

class _CodeTab extends StatelessWidget {
  final String componentId;
  final String board;
  const _CodeTab({required this.componentId, required this.board});

  @override
  Widget build(BuildContext context) {
    final app = context.watch<AppState>();
    if (!app.isPremium) {
      return _ProGate(feature: 'Code generation');
    }
    final CodeSnippet? s = app.repo.getCode(componentId, board);
    if (s == null) {
      return const Center(child: Text('No code snippet for this board yet.'));
    }
    final scheme = Theme.of(context).colorScheme;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(s.title,
            style: Theme.of(context)
                .textTheme
                .titleLarge
                ?.copyWith(fontWeight: FontWeight.w700)),
        if (s.libraries.isNotEmpty) ...[
          const SizedBox(height: 10),
          Text('Required libraries',
              style: TextStyle(
                  color: scheme.onSurfaceVariant,
                  fontWeight: FontWeight.w600,
                  fontSize: 12.5)),
          const SizedBox(height: 6),
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: [
              for (final lib in s.libraries)
                Chip(
                  label: Text(lib, style: const TextStyle(fontSize: 12)),
                  visualDensity: VisualDensity.compact,
                ),
            ],
          ),
        ],
        const SizedBox(height: 16),
        CodeBlock(code: s.code, title: 'Sketch ($board)'),
        const SizedBox(height: 24),
      ],
    );
  }
}

class _ProGate extends StatelessWidget {
  final String feature;
  const _ProGate({required this.feature});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: PremiumLock(
        feature: feature,
        onUnlock: () => Navigator.of(context).push(
            MaterialPageRoute(builder: (_) => const PaywallScreen())),
      ),
    );
  }
}
