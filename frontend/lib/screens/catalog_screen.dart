import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/component.dart';
import '../state/app_state.dart';
import '../widgets/type_badge.dart';
import 'component_detail_screen.dart';

/// Browsable catalogue of every component in the bundled knowledge base.
/// Fully offline — the database ships inside the APK.
class CatalogScreen extends StatefulWidget {
  const CatalogScreen({super.key});

  @override
  State<CatalogScreen> createState() => _CatalogScreenState();
}

class _CatalogScreenState extends State<CatalogScreen> {
  String _query = '';
  String? _typeFilter;
  String? _categoryFilter;

  /// Friendly labels for the catalog sections exported by the backend.
  static const _categoryLabels = {
    'passives': 'Passives',
    'semiconductors': 'Semiconductors',
    'ics': 'ICs',
    'sensors-environment': 'Environment',
    'sensors-motion': 'Motion & distance',
    'wireless': 'Wireless & IoT',
    'displays': 'Displays',
    'actuators': 'Motors & actuators',
    'power': 'Power',
    'boards': 'Boards',
    'audio': 'Audio',
    'interface': 'Storage & interface',
  };

  List<Component> _filtered(List<Component> all) {
    var items = all;
    if (_categoryFilter != null) {
      items = items.where((c) => c.category == _categoryFilter).toList();
    }
    if (_typeFilter != null) {
      items = items.where((c) => c.type == _typeFilter).toList();
    }
    if (_query.isNotEmpty) {
      final q = _query.toLowerCase();
      items = items
          .where((c) =>
              c.name.toLowerCase().contains(q) ||
              c.aliases.any((a) => a.toLowerCase().contains(q)) ||
              c.tags.any((t) => t.toLowerCase().contains(q)) ||
              c.description.toLowerCase().contains(q))
          .toList();
    }
    return items;
  }

  @override
  Widget build(BuildContext context) {
    final app = context.watch<AppState>();
    final scheme = Theme.of(context).colorScheme;
    final all = app.components;

    // Categories in the order the knowledge base defines them, then any extras.
    final present = all.map((c) => c.category).toSet()..remove('');
    final categories = [
      ..._categoryLabels.keys.where(present.contains),
      ...present.where((c) => !_categoryLabels.containsKey(c)),
    ];
    final types = all
        .where((c) => _categoryFilter == null || c.category == _categoryFilter)
        .map((c) => c.type)
        .toSet()
        .toList()
      ..sort();
    if (_typeFilter != null && !types.contains(_typeFilter)) _typeFilter = null;
    final filtered = _filtered(all);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Component catalog'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(18),
          child: Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Text(
              '${all.length} components • ${categories.length} categories',
              style: TextStyle(fontSize: 12, color: scheme.onSurfaceVariant),
            ),
          ),
        ),
      ),
      body: !app.initialised
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
                  child: TextField(
                    decoration: InputDecoration(
                      hintText: 'Search components, part numbers, tags…',
                      prefixIcon: const Icon(Icons.search),
                      border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(14)),
                      isDense: true,
                    ),
                    onChanged: (v) => setState(() => _query = v),
                  ),
                ),
                const SizedBox(height: 10),
                SizedBox(
                  height: 38,
                  child: ListView(
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    children: [
                      Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: FilterChip(
                          label: const Text('All'),
                          selected: _categoryFilter == null,
                          onSelected: (_) => setState(() {
                            _categoryFilter = null;
                            _typeFilter = null;
                          }),
                        ),
                      ),
                      for (final c in categories)
                        Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: FilterChip(
                            label: Text(_categoryLabels[c] ?? c),
                            selected: _categoryFilter == c,
                            onSelected: (_) => setState(() {
                              _categoryFilter = _categoryFilter == c ? null : c;
                              _typeFilter = null;
                            }),
                          ),
                        ),
                    ],
                  ),
                ),
                const SizedBox(height: 8),
                SizedBox(
                  height: 34,
                  child: ListView(
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    children: [
                      for (final t in types)
                        Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: ChoiceChip(
                            label: Text(t, style: const TextStyle(fontSize: 12)),
                            visualDensity: VisualDensity.compact,
                            selected: _typeFilter == t,
                            onSelected: (_) => setState(
                                () => _typeFilter = _typeFilter == t ? null : t),
                          ),
                        ),
                    ],
                  ),
                ),
                const SizedBox(height: 8),
                Expanded(
                  child: filtered.isEmpty
                      ? const Center(child: Text('No components match.'))
                      : ListView.builder(
                          padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                          itemCount: filtered.length,
                          itemBuilder: (context, index) {
                            final c = filtered[index];
                            return Card(
                              child: ListTile(
                                leading: TypeBadge(type: c.type),
                                title: Text(c.name,
                                    style: const TextStyle(
                                        fontWeight: FontWeight.w600)),
                                subtitle: Text(
                                  c.description,
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                trailing: const Icon(Icons.chevron_right),
                                onTap: () => Navigator.of(context).push(
                                  MaterialPageRoute(
                                    builder: (_) =>
                                        ComponentDetailScreen(componentId: c.id),
                                  ),
                                ),
                              ),
                            );
                          },
                        ),
                ),
              ],
            ),
    );
  }
}
