import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/component.dart';
import '../services/api_client.dart';
import '../state/app_state.dart';
import '../widgets/type_badge.dart';
import 'component_detail_screen.dart';

/// Browsable catalogue of every component in the knowledge base.
class CatalogScreen extends StatefulWidget {
  const CatalogScreen({super.key});

  @override
  State<CatalogScreen> createState() => _CatalogScreenState();
}

class _CatalogScreenState extends State<CatalogScreen> {
  List<Component>? _components;
  String? _error;
  String _query = '';
  String? _typeFilter;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _error = null);
    final api = context.read<AppState>().api;
    try {
      final items = await api.listComponents();
      items.sort((a, b) => a.name.compareTo(b.name));
      if (mounted) setState(() => _components = items);
    } on ApiException catch (e) {
      if (mounted) setState(() => _error = e.message);
    } catch (e) {
      if (mounted) setState(() => _error = '$e');
    }
  }

  List<Component> get _filtered {
    var items = _components ?? [];
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
    final types = (_components ?? [])
        .map((c) => c.type)
        .toSet()
        .toList()
      ..sort();

    return Scaffold(
      appBar: AppBar(title: const Text('Component catalog')),
      body: _error != null
          ? Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(_error!),
                  const SizedBox(height: 12),
                  OutlinedButton(
                      onPressed: _load, child: const Text('Retry')),
                ],
              ),
            )
          : _components == null
              ? const Center(child: CircularProgressIndicator())
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView(
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
                      for (final c in _filtered)
                        Card(
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
                        ),
                      if (_filtered.isEmpty)
                        const Padding(
                          padding: EdgeInsets.all(32),
                          child: Center(child: Text('No components match.')),
                        ),
                    ],
                  ),
                ),
    );
  }
}
