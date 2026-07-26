import 'dart:io';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/scan_result.dart';
import '../services/ai_identify_service.dart';
import '../state/app_state.dart';
import '../widgets/confidence_bar.dart';
import '../widgets/type_badge.dart';
import 'component_detail_screen.dart';
import 'paywall_screen.dart';

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
          Builder(builder: (context) {
            final note = context.watch<AppState>().lastCloudNote;
            if (note == null) return const SizedBox.shrink();
            return Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Card(
                child: ListTile(
                  dense: true,
                  leading: Icon(Icons.cloud_outlined, color: scheme.primary),
                  title: Text(note, style: const TextStyle(fontSize: 13)),
                ),
              ),
            );
          }),
          if (result.hasMatch)
            _BestMatchCard(match: result.bestMatch!)
          else
            _NoMatchCard(notes: result.notes),
          if (context.watch<AppState>().aiStatus.available) ...[
            const SizedBox(height: 16),
            AiIdentifyCard(
              imagePath: imagePath,
              ocrText: result.ocrText,
              matched: result.hasMatch,
            ),
          ],
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


/// Hands the photo to the AI when the bundled catalog comes up short.
///
/// The on-device catalog covers the common parts; this covers everything else.
/// A successful identification is merged into the local catalog and saved on
/// the device, so the part is available offline from then on.
class AiIdentifyCard extends StatefulWidget {
  final String imagePath;
  final String ocrText;

  /// True when the on-device scanner already matched something — the AI is
  /// then offered as a second opinion rather than the main action.
  final bool matched;

  const AiIdentifyCard({
    super.key,
    required this.imagePath,
    required this.ocrText,
    required this.matched,
  });

  @override
  State<AiIdentifyCard> createState() => _AiIdentifyCardState();
}

class _AiIdentifyCardState extends State<AiIdentifyCard> {
  bool _busy = false;
  String? _error;
  AiIdentification? _result;

  Future<void> _identify() async {
    final app = context.read<AppState>();
    setState(() {
      _busy = true;
      _error = null;
      _result = null;
    });
    try {
      final result = await app.identifyWithAi(
        File(widget.imagePath),
        ocrText: widget.ocrText,
      );
      if (!mounted) return;
      setState(() => _result = result);
      if (result.identified && result.componentId.isNotEmpty) {
        Navigator.of(context).push(MaterialPageRoute(
          builder: (_) => ComponentDetailScreen(componentId: result.componentId),
        ));
      }
    } on AiException catch (e) {
      if (!mounted) return;
      if (e.requiresPro) {
        Navigator.of(context).push(
            MaterialPageRoute(builder: (_) => const PaywallScreen()));
      }
      setState(() => _error = e.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final app = context.watch<AppState>();
    final result = _result;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.auto_awesome, color: scheme.secondary),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    widget.matched
                        ? 'Not the right part?'
                        : 'Identify it with AI',
                    style: const TextStyle(
                        fontWeight: FontWeight.w800, fontSize: 15),
                  ),
                ),
                if (!app.isPremium)
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: scheme.secondary.withValues(alpha: 0.18),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text('PRO',
                        style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w800,
                            color: scheme.secondary)),
                  ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'The catalog on your phone covers the common parts. This sends '
              'the photo to our AI, which can work out almost any component — '
              'and writes its pinout, wiring and code. Once identified, it is '
              'saved on your device and works offline.',
              style: TextStyle(fontSize: 13, color: scheme.onSurfaceVariant),
            ),
            if (result != null && !result.identified) ...[
              const SizedBox(height: 12),
              Text(
                result.advice.isNotEmpty
                    ? result.advice
                    : "The AI couldn't name this part with confidence.",
                style: TextStyle(fontSize: 13, color: scheme.error),
              ),
            ],
            if (result != null && result.identified) ...[
              const SizedBox(height: 12),
              Text('${result.name} — ${result.reasoning}',
                  style: const TextStyle(fontSize: 13)),
            ],
            if (_error != null) ...[
              const SizedBox(height: 12),
              Text(_error!,
                  style: TextStyle(fontSize: 13, color: scheme.error)),
            ],
            const SizedBox(height: 14),
            FilledButton.icon(
              onPressed: _busy ? null : _identify,
              icon: _busy
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                          strokeWidth: 2, color: Colors.white),
                    )
                  : const Icon(Icons.auto_awesome),
              label: Text(_busy
                  ? 'Working it out…'
                  : result != null
                      ? 'Try again'
                      : 'Identify with AI'),
              style:
                  FilledButton.styleFrom(minimumSize: const Size.fromHeight(50)),
            ),
            if (_busy) ...[
              const SizedBox(height: 8),
              Text(
                'Reading the markings, package and pin layout — this takes '
                'up to a minute.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 12, color: scheme.onSurfaceVariant),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
