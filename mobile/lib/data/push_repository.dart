import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'api_client.dart';

final pushRepositoryProvider = Provider(
  (ref) => PushRepository(ref.read(apiClientProvider)),
);

/// Registers/unregisters this device's push token with the backend.
class PushRepository {
  PushRepository(this._dio);
  final Dio _dio;

  Future<void> register(String token, String platform) async {
    await _dio.post('/devices/register', data: {
      'token': token,
      'platform': platform,
    });
  }

  Future<void> unregister(String token) async {
    await _dio.post('/devices/unregister', data: {'token': token});
  }
}
