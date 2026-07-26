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

  List<Component> _filtered(List<Component> all) {
    var items = all;
    if (_typeFilter != null) {
      items = items.where((c) => c.type == _typeFilter).toList();
    }
    if (_query.isNotEmpty) {
      final q = _query.toLowerCase();
      items = items
          .where((c) =>
              c.name.toLowerCase().contains(q) ||
              c.aliases.any((a) => a.toLowerCase().contains(q)) ||
              c.tags.any((t) => t.toLowerCase().contains(q)))
          .toList();
    }
    return items;
  }

  @override
  Widget build(BuildContext context) {
    final app = context.watch<AppState>();
    final all = app.components;
    final types = all.map((c) => c.type).toSet().toList()..sort();
    final filtered = _filtered(all);

    return Scaffold(
      appBar: AppBar(title: const Text('Component catalog')),
      body: !app.initialised
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                TextField(
                  decoration: InputDecoration(
                    hintText: 'Search components…',
                    prefixIcon: const Icon(Icons.search),
                    border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(14)),
                    isDense: true,
                  ),
                  onChanged: (v) => setState(() => _query = v),
                ),
                const SizedBox(height: 12),
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: [
                      Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: FilterChip(
                          label: const Text('All'),
                          selected: _typeFilter == null,
                          onSelected: (_) =>
                              setState(() => _typeFilter = null),
                        ),
                      ),
                      for (final t in types)
                        Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: FilterChip(
                            label: Text(t),
                            selected: _typeFilter == t,
                            onSelected: (_) => setState(() =>
                                _typeFilter = _typeFilter == t ? null : t),
                          ),
                        ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                for (final c in filtered)
                  Card(
                    child: ListTile(
                      leading: TypeBadge(type: c.type),
                      title: Text(c.name,
                          style:
                              const TextStyle(fontWeight: FontWeight.w600)),
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
                  ),
                if (filtered.isEmpty)
                  const Padding(
                    padding: EdgeInsets.all(32),
                    child: Center(child: Text('No components match.')),
                  ),
              ],
            ),
    );
  }
}
