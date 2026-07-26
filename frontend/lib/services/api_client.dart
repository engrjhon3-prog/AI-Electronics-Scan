import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../config.dart';
import '../models/component.dart';
import '../models/scan_result.dart';
import '../models/wiring.dart';

/// Thrown when the backend rejects a premium request (HTTP 402).
class PremiumRequiredException implements Exception {
  final String message;
  PremiumRequiredException([this.message = 'Premium subscription required']);
  @override
  String toString() => message;
}

/// Thrown for any other backend/network failure.
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  ApiException(this.message, {this.statusCode});
  @override
  String toString() => message;
}

/// Talks to the Python FastAPI backend.
class ApiClient {
  ApiClient({http.Client? client, String? baseUrl})
      : _client = client ?? http.Client(),
        _baseUrl = baseUrl ?? AppConfig.apiBaseUrl;

  final http.Client _client;
  final String _baseUrl;

  /// Premium token used to authorise gated endpoints. Set by SubscriptionService.
  String? premiumToken;

  static const Duration _timeout = Duration(seconds: 30);

  Map<String, String> get _premiumHeaders =>
      premiumToken == null ? {} : {'X-Premium-Token': premiumToken!};

  Uri _uri(String path, [Map<String, String>? query]) =>
      Uri.parse('$_baseUrl$path').replace(queryParameters: query);

  /// Simple connectivity check against the service.
  Future<bool> ping() async {
    try {
      final res = await _client
          .get(_uri('/health'))
          .timeout(const Duration(seconds: 8));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  /// Identify a component from an image file (free tier).
  Future<ScanResult> scan(File image) async {
    final request = http.MultipartRequest('POST', _uri('/api/v1/scan'))
      ..files.add(await http.MultipartFile.fromPath('image', image.path));
    try {
      final streamed = await _client.send(request).timeout(_timeout);
      final res = await http.Response.fromStream(streamed);
      if (res.statusCode == 200) {
        return ScanResult.fromJson(
            jsonDecode(res.body) as Map<String, dynamic>);
      }
      throw ApiException('Scan failed (${res.statusCode}).',
          statusCode: res.statusCode);
    } on SocketException {
      throw ApiException(
          'Could not reach the scanner service. Check your connection and the server URL.');
    }
  }

  /// Fetch the full component catalogue.
  Future<List<Component>> listComponents() async {
    final res = await _get('/api/v1/components');
    final list = jsonDecode(res.body) as List;
    return list
        .map((e) => Component.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<Component> getComponent(String id) async {
    final res = await _get('/api/v1/components/$id');
    return Component.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
  }

  /// PREMIUM: wiring diagram (includes inline SVG).
  Future<WiringDiagram> getWiring(String id, String board) async {
    final res = await _get('/api/v1/components/$id/wiring',
        query: {'board': board}, premium: true);
    return WiringDiagram.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
  }

  /// PREMIUM: generated code snippet.
  Future<CodeSnippet> getCode(String id, String board) async {
    final res = await _get('/api/v1/components/$id/code',
        query: {'board': board}, premium: true);
    return CodeSnippet.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
  }

  Future<http.Response> _get(
    String path, {
    Map<String, String>? query,
    bool premium = false,
  }) async {
    try {
      final res = await _client
          .get(_uri(path, query), headers: premium ? _premiumHeaders : null)
          .timeout(_timeout);
      if (res.statusCode == 200) return res;
      if (res.statusCode == 402) throw PremiumRequiredException();
      if (res.statusCode == 404) {
        throw ApiException('Not found.', statusCode: 404);
      }
      throw ApiException('Request failed (${res.statusCode}).',
          statusCode: res.statusCode);
    } on SocketException {
      throw ApiException('Could not reach the scanner service.');
    }
  }

  void dispose() => _client.close();
}
