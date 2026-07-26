import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../config.dart';

/// What the AI made of a photo.
class AiIdentification {
  final bool identified;
  final double confidence;
  final String detectedText;
  final String reasoning;
  final String advice;

  /// True when the answer came from the shared cache — someone already had
  /// this part identified, so it cost nothing and arrived instantly.
  final bool cached;

  /// Catalog-shaped component: pins, per-board wiring (with SVG) and code.
  final Map<String, dynamic> component;

  const AiIdentification({
    required this.identified,
    required this.confidence,
    required this.component,
    this.detectedText = '',
    this.reasoning = '',
    this.advice = '',
    this.cached = false,
  });

  String get componentId => component['id'] as String? ?? '';
  String get name => component['name'] as String? ?? 'Unidentified part';

  factory AiIdentification.fromJson(Map<String, dynamic> json) =>
      AiIdentification(
        identified: json['identified'] == true,
        confidence: (json['confidence'] as num?)?.toDouble() ?? 0,
        detectedText: json['detected_text'] as String? ?? '',
        reasoning: json['reasoning'] as String? ?? '',
        advice: json['advice'] as String? ?? '',
        cached: json['cached'] == true,
        component: (json['component'] as Map?)?.cast<String, dynamic>() ?? {},
      );
}

/// Whether the server can identify unknown parts, and how many it has learned.
class AiStatus {
  final bool available;
  final String model;
  final int cachedComponents;

  const AiStatus({
    required this.available,
    this.model = '',
    this.cachedComponents = 0,
  });

  static const AiStatus offline = AiStatus(available: false);

  factory AiStatus.fromJson(Map<String, dynamic> json) => AiStatus(
        available: json['available'] == true,
        model: json['model'] as String? ?? '',
        cachedComponents: (json['cached_components'] as num?)?.toInt() ?? 0,
      );
}

class AiException implements Exception {
  final String message;

  /// True when the server refused because the account isn't Pro.
  final bool requiresPro;

  AiException(this.message, {this.requiresPro = false});

  @override
  String toString() => message;
}

/// Identifies components the bundled catalog doesn't know.
///
/// The on-device scanner handles the parts we shipped; when it comes up empty,
/// the photo (plus whatever OCR read) goes to the backend, which asks Claude's
/// vision model to write a full entry — pinout, wiring and code — for whatever
/// the part actually is. Results are cached server-side, so the catalog grows
/// with use instead of being fixed at build time.
class AiIdentifyService {
  AiIdentifyService({http.Client? client, String? baseUrl})
      : _client = client ?? http.Client(),
        _baseUrl = baseUrl ?? AppConfig.apiBaseUrl;

  final http.Client _client;
  final String _baseUrl;

  static const Duration _statusTimeout = Duration(seconds: 8);
  // Identification runs a vision model — it is slow by design.
  static const Duration _identifyTimeout = Duration(minutes: 3);

  Uri _uri(String path) => Uri.parse('$_baseUrl/api/v1/ai$path');

  Future<AiStatus> status() async {
    try {
      final res = await _client.get(_uri('/status')).timeout(_statusTimeout);
      if (res.statusCode != 200) return AiStatus.offline;
      return AiStatus.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
    } catch (_) {
      return AiStatus.offline;
    }
  }

  Future<AiIdentification> identify({
    required File image,
    String ocrText = '',
    String hint = '',
    String idToken = '',
    String premiumToken = '',
  }) async {
    final request = http.MultipartRequest('POST', _uri('/identify'))
      ..fields['ocr_text'] = ocrText
      ..fields['hint'] = hint
      ..files.add(await http.MultipartFile.fromPath('image', image.path));
    if (idToken.isNotEmpty) {
      request.headers['Authorization'] = 'Bearer $idToken';
    }
    if (premiumToken.isNotEmpty) {
      request.headers['X-Premium-Token'] = premiumToken;
    }

    http.Response res;
    try {
      final streamed = await _client.send(request).timeout(_identifyTimeout);
      res = await http.Response.fromStream(streamed);
    } catch (e) {
      throw AiException(
          'Could not reach the AI service — check your connection and try '
          'again. ($e)');
    }

    if (res.statusCode == 200) {
      return AiIdentification.fromJson(
          jsonDecode(res.body) as Map<String, dynamic>);
    }

    String detail;
    try {
      detail = (jsonDecode(res.body) as Map<String, dynamic>)['detail']
              ?.toString() ??
          'Identification failed (${res.statusCode}).';
    } catch (_) {
      detail = 'Identification failed (${res.statusCode}).';
    }
    throw AiException(detail, requiresPro: res.statusCode == 402);
  }
}
