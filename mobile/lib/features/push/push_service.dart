import 'dart:io' show Platform;

import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/push_repository.dart';

/// Handles FCM: requests permission, captures the device token, registers it
/// with the backend, and keeps it fresh. Degrades gracefully when Firebase is
/// not configured on the device (no native config files yet) so the app still
/// runs — real pushes simply don't flow until a Firebase project is wired.
class PushService {
  PushService(this._ref);
  final Ref _ref;

  String? _lastToken;
  bool _initialized = false;

  String get _platform {
    if (kIsWeb) return 'WEB';
    if (Platform.isIOS) return 'IOS';
    return 'ANDROID';
  }

  /// Call after the user signs in. Safe to call more than once.
  Future<void> start() async {
    if (_initialized) return;
    try {
      await Firebase.initializeApp();
    } catch (_) {
      // Firebase not configured on this device yet — skip silently.
      return;
    }
    _initialized = true;

    final messaging = FirebaseMessaging.instance;
    try {
      await messaging.requestPermission();
      final token = await messaging.getToken();
      if (token != null) await _register(token);

      // Keep the backend in sync when the OS rotates the token.
      messaging.onTokenRefresh.listen(_register);
    } catch (_) {
      // Token retrieval can fail without APNs/FCM setup; ignore.
    }
  }

  Future<void> _register(String token) async {
    _lastToken = token;
    try {
      await _ref.read(pushRepositoryProvider).register(token, _platform);
    } catch (_) {
      // Backend unreachable / not signed in — will retry on next start().
    }
  }

  /// Call on sign-out so the device stops receiving this user's pushes.
  Future<void> stop() async {
    final token = _lastToken;
    if (token == null) return;
    try {
      await _ref.read(pushRepositoryProvider).unregister(token);
    } catch (_) {/* best-effort */}
    _lastToken = null;
  }
}

final pushServiceProvider = Provider((ref) => PushService(ref));
