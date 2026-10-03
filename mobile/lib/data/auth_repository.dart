import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../app/user_role.dart';
import 'api_client.dart';

final authRepositoryProvider = Provider(
  (ref) => AuthRepository(
    ref.read(apiClientProvider),
    ref.read(secureStorageProvider),
  ),
);

/// Maps the backend role string (e.g. "ID_BOSS") to the Flutter enum.
UserRole roleFromApi(String value) {
  switch (value) {
    case 'ID_BOSS':
      return UserRole.idBoss;
    case 'ID':
      return UserRole.id;
    case 'CLIENT':
      return UserRole.client;
    case 'CONTRACTOR':
      return UserRole.contractor;
    case 'WORKER':
      return UserRole.worker;
    default:
      return UserRole.client;
  }
}

/// Maps the Flutter enum back to the backend role string.
String roleToApi(UserRole role) {
  switch (role) {
    case UserRole.idBoss:
      return 'ID_BOSS';
    case UserRole.id:
      return 'ID';
    case UserRole.client:
      return 'CLIENT';
    case UserRole.contractor:
      return 'CONTRACTOR';
    case UserRole.worker:
      return 'WORKER';
  }
}

class AuthRepository {
  AuthRepository(this._dio, this._storage);
  final Dio _dio;
  final FlutterSecureStorage _storage;

  Future<void> _saveTokens(Map<String, dynamic> data) async {
    await _storage.write(key: 'access_token', value: data['access_token']);
    await _storage.write(key: 'refresh_token', value: data['refresh_token']);
  }

  Future<void> login(String email, String password) async {
    final res = await _dio.post('/auth/login',
        data: {'email': email, 'password': password});
    await _saveTokens(res.data as Map<String, dynamic>);
  }

  Future<void> register({
    required String email,
    required String password,
    required String fullName,
    required UserRole role,
    String? phone,
  }) async {
    await _dio.post('/auth/register', data: {
      'email': email,
      'password': password,
      'full_name': fullName,
      'role': roleToApi(role),
      'phone': phone,
    });
    await login(email, password);
  }

  Future<UserRole?> currentRole() async {
    final token = await _storage.read(key: 'access_token');
    if (token == null) return null;
    try {
      final res = await _dio.get('/auth/me');
      return roleFromApi(res.data['role'] as String);
    } catch (_) {
      return null;
    }
  }

  Future<void> logout() async {
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
  }
}
