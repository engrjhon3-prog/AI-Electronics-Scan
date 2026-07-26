import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:provider/provider.dart';

import '../models/component.dart';
import '../models/wiring.dart';
import '../services/api_client.dart';
import '../state/app_state.dart';
import '../widgets/code_block.dart';
import '../widgets/pinout_table.dart';
import '../widgets/premium_lock.dart';
import '../widgets/type_badge.dart';
import 'paywall_screen.dart';

class ComponentDetailScreen extends StatefulWidget {
  final String componentId;
  const ComponentDetailScreen({super.key, required this.componentId});

  @override
  State<ComponentDetailScreen> createState() => _ComponentDetailScreenState();
}

class _ComponentDetailScreenState extends State<ComponentDetailScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabs;
  Component? _component;
  String? _error;
  String _board = 'uno';

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 3, vsync: this);
    _load();
  }

  @override
  void dispose() {
    _tabs.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    final api = context.read<AppState>().api;
    try {
      final comp = await api.getComponent(widget.componentId);
      setState(() {
        _component = comp;
        if (comp.supportedBoards.isNotEmpty) {
          _board = comp.supportedBoards.first;
        }
      });
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } catch (e) {
      setState(() => _error = '$e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final comp = _component;
    return Scaffold(
      appBar: AppBar(
        title: Text(comp?.name ?? 'Component'),
        bottom: comp == null
            ? null
            : TabBar(
                controller: _tabs,
                tabs: const [
                  Tab(text: 'Overview'),
                  Tab(text: 'Wiring'),
                  Tab(text: 'Code'),
                ],
              ),
      ),
      body: _error != null
          ? _ErrorView(message: _error!, onRetry: _load)
          : comp == null
              ? const Center(child: CircularProgressIndicator())
              : Column(
                  children: [
                    if (comp.supportedBoards.length > 1)
                      _BoardSelector(
                        boards: comp.supportedBoards,
                        selected: _board,
                        onChanged: (b) => setState(() => _board = b),
                      ),
                    Expanded(
                      child: TabBarView(
                        controller: _tabs,
                        children: [
                          _OverviewTab(component: comp),
                          _WiringTab(componentId: comp.id, board: _board),
                          _CodeTab(componentId: comp.id, board: _board),
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

class _WiringTab extends StatefulWidget {
  final String componentId;
  final String board;
  const _WiringTab({required this.componentId, required this.board});

  @override
  State<_WiringTab> createState() => _WiringTabState();
}

class _WiringTabState extends State<_WiringTab> {
  WiringDiagram? _diagram;
  String? _error;
  bool _locked = false;
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void didUpdateWidget(covariant _WiringTab old) {
    super.didUpdateWidget(old);
    if (old.board != widget.board) _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
      _locked = false;
    });
    final app = context.read<AppState>();
    try {
      final d = await app.api.getWiring(widget.componentId, widget.board);
      if (mounted) setState(() => _diagram = d);
    } on PremiumRequiredException {
      if (mounted) setState(() => _locked = true);
    } on ApiException catch (e) {
      if (mounted) setState(() => _error = e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_locked) {
      return Padding(
        padding: const EdgeInsets.all(20),
        child: PremiumLock(
          feature: 'Wiring diagrams',
          onUnlock: () async {
            await Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const PaywallScreen()));
            _load();
          },
        ),
      );
    }
    if (_error != null) {
      return _ErrorView(message: _error!, onRetry: _load);
    }
    final d = _diagram;
    if (d == null) return const SizedBox.shrink();
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
                  Icon(Icons.info_outline,
                      size: 16, color: scheme.secondary),
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

class _CodeTab extends StatefulWidget {
  final String componentId;
  final String board;
  const _CodeTab({required this.componentId, required this.board});

  @override
  State<_CodeTab> createState() => _CodeTabState();
}

class _CodeTabState extends State<_CodeTab> {
  CodeSnippet? _snippet;
  String? _error;
  bool _locked = false;
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void didUpdateWidget(covariant _CodeTab old) {
    super.didUpdateWidget(old);
    if (old.board != widget.board) _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
      _locked = false;
    });
    final app = context.read<AppState>();
    try {
      final s = await app.api.getCode(widget.componentId, widget.board);
      if (mounted) setState(() => _snippet = s);
    } on PremiumRequiredException {
      if (mounted) setState(() => _locked = true);
    } on ApiException catch (e) {
      if (mounted) setState(() => _error = e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_locked) {
      return Padding(
        padding: const EdgeInsets.all(20),
        child: PremiumLock(
          feature: 'Code generation',
          onUnlock: () async {
            await Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const PaywallScreen()));
            _load();
          },
        ),
      );
    }
    if (_error != null) {
      return _ErrorView(message: _error!, onRetry: _load);
    }
    final s = _snippet;
    if (s == null) return const SizedBox.shrink();
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
        CodeBlock(code: s.code, title: 'Sketch (${widget.board})'),
        const SizedBox(height: 24),
      ],
    );
  }
}

class _ErrorView extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;
  const _ErrorView({required this.message, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.error_outline, size: 40, color: scheme.error),
            const SizedBox(height: 12),
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }
}
