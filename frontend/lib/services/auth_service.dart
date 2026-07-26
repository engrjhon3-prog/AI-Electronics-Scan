import 'dart:async';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';

/// Firebase-backed accounts and Pro entitlements.
///
/// Entitlement model (see `firebase/firestore.rules`):
///  - Custom claims `admin` / `premium` on the ID token (set server-side).
///  - `entitlements/{email}` documents with `{premium: true}` that admins can
///    grant from the app or website after a customer subscribes.
///
/// The service is safe to use when Firebase isn't configured (e.g. tests):
/// every method no-ops and `isAvailable` is false.
class AuthService {
  bool get isAvailable => Firebase.apps.isNotEmpty;

  User? get currentUser =>
      isAvailable ? FirebaseAuth.instance.currentUser : null;

  Stream<User?> authStateChanges() =>
      isAvailable ? FirebaseAuth.instance.authStateChanges() : const Stream.empty();

  Future<UserCredential> signIn(String email, String password) =>
      FirebaseAuth.instance
          .signInWithEmailAndPassword(email: email.trim(), password: password);

  Future<UserCredential> signUp(String email, String password) =>
      FirebaseAuth.instance.createUserWithEmailAndPassword(
          email: email.trim(), password: password);

  Future<void> signOut() async {
    if (isAvailable) await FirebaseAuth.instance.signOut();
  }

  Future<void> sendPasswordReset(String email) => FirebaseAuth.instance
      .sendPasswordResetEmail(email: email.trim());

  /// Read `admin` / `premium` custom claims, optionally forcing a token
  /// refresh (needed right after an admin changes claims).
  Future<({bool admin, bool premium})> readClaims({bool refresh = false}) async {
    final user = currentUser;
    if (user == null) return (admin: false, premium: false);
    final token = await user.getIdTokenResult(refresh);
    final claims = token.claims ?? {};
    return (
      admin: claims['admin'] == true,
      premium: claims['premium'] == true,
    );
  }

  /// Live entitlement stream for the signed-in user's email.
  Stream<bool> entitlementStream(String email) => FirebaseFirestore.instance
      .collection('entitlements')
      .doc(email.toLowerCase())
      .snapshots()
      .map((snap) => snap.data()?['premium'] == true);

  /// One-shot entitlement read.
  Future<bool> fetchEntitlement(String email) async {
    final snap = await FirebaseFirestore.instance
        .collection('entitlements')
        .doc(email.toLowerCase())
        .get();
    return snap.data()?['premium'] == true;
  }

  // ------------------------------------------------------------- admin ops
  /// Grant Pro to a customer email. Requires the `admin` custom claim
  /// (enforced by Firestore rules).
  Future<void> grantPremium(String email) => FirebaseFirestore.instance
      .collection('entitlements')
      .doc(email.trim().toLowerCase())
      .set({
        'premium': true,
        'grantedBy': currentUser?.email,
        'grantedAt': FieldValue.serverTimestamp(),
      });

  Future<void> revokePremium(String email) => FirebaseFirestore.instance
      .collection('entitlements')
      .doc(email.trim().toLowerCase())
      .set({
        'premium': false,
        'revokedBy': currentUser?.email,
        'revokedAt': FieldValue.serverTimestamp(),
      }, SetOptions(merge: true));

  /// Human-readable message for common auth errors.
  static String describeError(Object e) {
    if (e is FirebaseAuthException) {
      switch (e.code) {
        case 'invalid-credential':
        case 'wrong-password':
        case 'user-not-found':
          return 'Wrong email or password.';
        case 'email-already-in-use':
          return 'An account with this email already exists — try signing in.';
        case 'weak-password':
          return 'Password is too weak (use at least 6 characters).';
        case 'invalid-email':
          return 'That email address looks invalid.';
        case 'network-request-failed':
          return 'No connection — accounts need internet (scanning works offline).';
        default:
          return e.message ?? 'Authentication failed (${e.code}).';
      }
    }
    return 'Something went wrong: $e';
  }
}
