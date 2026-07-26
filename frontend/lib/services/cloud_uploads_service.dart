import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:image/image.dart' as img;

/// Cloud storage for scan photos, kept in Firestore as compressed JPEG
/// (base64) so the whole product stays on Firebase's free tier — Cloud
/// Storage buckets would require the paid Blaze plan.
///
/// Retention policy (also enforced by Firestore security rules and a
/// scheduled cleanup workflow):
///   Free  : up to [freeSlots] active uploads, each kept 12 hours.
///   Pro   : uploads kept 7 days.
class CloudUpload {
  final String id;
  final String name;
  final String? componentId;
  final DateTime createdAt;
  final DateTime expiresAt;
  final Uint8List imageBytes;

  const CloudUpload({
    required this.id,
    required this.name,
    required this.componentId,
    required this.createdAt,
    required this.expiresAt,
    required this.imageBytes,
  });

  Duration get remaining => expiresAt.difference(DateTime.now());
}

class UploadQuotaExceeded implements Exception {
  final String message;
  UploadQuotaExceeded(this.message);
  @override
  String toString() => message;
}

class CloudUploadsService {
  static const int freeSlots = 3;
  static const Duration freeRetention = Duration(hours: 12);
  static const Duration proRetention = Duration(days: 7);

  /// Firestore documents are capped at ~1MB; keep well under it.
  static const int _maxSide = 640;
  static const int _jpegQuality = 72;

  CollectionReference<Map<String, dynamic>> _col(String uid) =>
      FirebaseFirestore.instance
          .collection('users')
          .doc(uid)
          .collection('uploads');

  /// Compress + store a scan photo. Throws [UploadQuotaExceeded] when a free
  /// user already has [freeSlots] active uploads.
  Future<void> upload({
    required String uid,
    required File image,
    required bool premium,
    String name = 'Scan',
    String? componentId,
  }) async {
    if (!premium) {
      final active = await _activeCount(uid);
      if (active >= freeSlots) {
        throw UploadQuotaExceeded(
            'Free cloud storage is full ($freeSlots images). Old images free '
            'up 12 hours after upload — or go Pro for 7-day storage.');
      }
    }

    final raw = await image.readAsBytes();
    var decoded = img.decodeImage(raw);
    if (decoded == null) {
      throw Exception('Could not read that image.');
    }
    if (decoded.width > _maxSide || decoded.height > _maxSide) {
      decoded = img.copyResize(decoded,
          width: decoded.width >= decoded.height ? _maxSide : null,
          height: decoded.height > decoded.width ? _maxSide : null);
    }
    final jpeg = img.encodeJpg(decoded, quality: _jpegQuality);

    final now = DateTime.now();
    final expires = now.add(premium ? proRetention : freeRetention);
    await _col(uid).add({
      'name': name,
      'componentId': componentId,
      'imageB64': base64Encode(jpeg),
      'createdAt': Timestamp.fromDate(now),
      'expiresAt': Timestamp.fromDate(expires),
    });
  }

  Future<int> _activeCount(String uid) async {
    final snap = await _col(uid)
        .where('expiresAt', isGreaterThan: Timestamp.now())
        .count()
        .get();
    return snap.count ?? 0;
  }

  /// Live list of the user's active (non-expired) uploads, newest first.
  Stream<List<CloudUpload>> stream(String uid) => _col(uid)
          .where('expiresAt', isGreaterThan: Timestamp.now())
          .orderBy('expiresAt', descending: true)
          .snapshots()
          .map((snap) {
        final items = <CloudUpload>[];
        for (final doc in snap.docs) {
          final d = doc.data();
          try {
            items.add(CloudUpload(
              id: doc.id,
              name: d['name'] as String? ?? 'Scan',
              componentId: d['componentId'] as String?,
              createdAt: (d['createdAt'] as Timestamp).toDate(),
              expiresAt: (d['expiresAt'] as Timestamp).toDate(),
              imageBytes: base64Decode(d['imageB64'] as String),
            ));
          } catch (_) {
            // Skip malformed docs rather than break the whole list.
          }
        }
        return items;
      });

  Future<void> delete(String uid, String id) => _col(uid).doc(id).delete();

  /// Opportunistically remove the caller's own expired uploads. The scheduled
  /// GitHub Actions job is the backstop for users who never reopen the app.
  Future<void> purgeExpired(String uid) async {
    final snap = await _col(uid)
        .where('expiresAt', isLessThanOrEqualTo: Timestamp.now())
        .get();
    for (final doc in snap.docs) {
      await doc.reference.delete();
    }
  }
}
