import 'dart:io';

import 'package:flutter/material.dart';

import '../models/scan_result.dart';
import '../widgets/confidence_bar.dart';
import '../widgets/type_badge.dart';
import 'component_detail_screen.dart';

/// Shows the outcome of a scan: best match, alternatives, and vision notes.
class ResultScreen extends StatelessWidget {
  final ScanResult result;
  final String imagePath;
  const ResultScreen(
      {super.key, required this.result, required this.imagePath});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(title: const Text('Scan result')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: Image.file(
              File(imagePath),
              height: 200,
              width: double.infinity,
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) => Container(
                height: 200,
                color: scheme.surfaceContainerHighest,
                child: const Center(child: Icon(Icons.image_not_supported)),
              ),
            ),
          ),
          const SizedBox(height: 20),
          if (result.hasMatch)
            _BestMatchCard(match: result.bestMatch!)
          else
            _NoMatchCard(notes: result.notes),
          if (result.candidates.length > 1) ...[
            const SizedBox(height: 20),
            Text('Other possibilities',
                style: Theme.of(context)
                    .textTheme
                    .titleMedium
                    ?.copyWith(fontWeight: FontWeight.w700)),
            const SizedBox(height: 8),
            for (final c in result.candidates.skip(1))
              _CandidateTile(candidate: c),
          ],
          if (result.notes.isNotEmpty && result.hasMatch) ...[
            const SizedBox(height: 20),
            _NotesCard(notes: result.notes),
          ],
        ],
      ),
    );
  }
}

class _BestMatchCard extends StatelessWidget {
  final DetectionCandidate match;
  const _BestMatchCard({required this.match});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                TypeBadge(type: match.type, large: true),
                const Spacer(),
                if (match.detectedValue != null)
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: scheme.primaryContainer,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(match.detectedValue!,
                        style: TextStyle(
                            color: scheme.onPrimaryContainer,
                            fontWeight: FontWeight.w700)),
                  ),
              ],
            ),
            const SizedBox(height: 12),
            Text(match.name,
                style: Theme.of(context)
                    .textTheme
                    .headlineSmall
                    ?.copyWith(fontWeight: FontWeight.w800)),
            const SizedBox(height: 4),
            Text('Detected via ${match.detectionMethod}',
                style: TextStyle(
                    color: scheme.onSurfaceVariant, fontSize: 12.5)),
            const SizedBox(height: 16),
            ConfidenceBar(confidence: match.confidence),
            const SizedBox(height: 20),
            FilledButton.icon(
              onPressed: () => Navigator.of(context).push(MaterialPageRoute(
                builder: (_) =>
                    ComponentDetailScreen(componentId: match.componentId),
              )),
              icon: const Icon(Icons.open_in_new),
              label: const Text('View pinout, wiring & code'),
              style:
                  FilledButton.styleFrom(minimumSize: const Size.fromHeight(50)),
            ),
          ],
        ),
      ),
    );
  }
}

class _CandidateTile extends StatelessWidget {
  final DetectionCandidate candidate;
  const _CandidateTile({required this.candidate});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      child: ListTile(
        leading: TypeBadge(type: candidate.type),
        title: Text(candidate.name,
            style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: Text('${(candidate.confidence * 100).round()}% • '
            '${candidate.detectionMethod}'),
        trailing: Icon(Icons.chevron_right, color: scheme.onSurfaceVariant),
        onTap: () => Navigator.of(context).push(MaterialPageRoute(
          builder: (_) =>
              ComponentDetailScreen(componentId: candidate.componentId),
        )),
      ),
    );
  }
}

class _NoMatchCard extends StatelessWidget {
  final List<String> notes;
  const _NoMatchCard({required this.notes});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          children: [
            Icon(Icons.search_off, size: 48, color: scheme.onSurfaceVariant),
            const SizedBox(height: 12),
            const Text("Couldn't identify this component",
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
            const SizedBox(height: 8),
            for (final n in notes)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Text(n,
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        color: scheme.onSurfaceVariant, fontSize: 13)),
              ),
          ],
        ),
      ),
    );
  }
}

class _NotesCard extends StatelessWidget {
  final List<String> notes;
  const _NotesCard({required this.notes});

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
                Icon(Icons.visibility_outlined,
                    size: 18, color: scheme.primary),
                const SizedBox(width: 8),
                const Text('What the scanner saw',
                    style: TextStyle(fontWeight: FontWeight.w700)),
              ],
            ),
            const SizedBox(height: 8),
            for (final n in notes)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Text('• $n',
                    style: TextStyle(
                        color: scheme.onSurfaceVariant, fontSize: 12.5)),
              ),
          ],
        ),
      ),
    );
  }
}
