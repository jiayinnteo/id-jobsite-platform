import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Base URL of the FastAPI backend. Override at build time with
/// --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
const String kApiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://10.0.2.2:8000/api/v1',
);

final secureStorageProvider = Provider((_) => const FlutterSecureStorage());

/// Dio client with a bearer-token interceptor and automatic refresh.
final apiClientProvider = Provider<Dio>((ref) {
  final storage = ref.read(secureStorageProvider);
  final dio = Dio(BaseOptions(baseUrl: kApiBaseUrl));

  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await storage.read(key: 'access_token');
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (err, handler) async {
        // On 401, try one refresh then replay the request.
        if (err.response?.statusCode == 401) {
          final refresh = await storage.read(key: 'refresh_token');
          if (refresh != null) {
            try {
              final res = await Dio(BaseOptions(baseUrl: kApiBaseUrl)).post(
                '/auth/refresh',
                data: {'refresh_token': refresh},
              );
              await storage.write(
                  key: 'access_token', value: res.data['access_token']);
              await storage.write(
                  key: 'refresh_token', value: res.data['refresh_token']);
              final req = err.requestOptions;
              req.headers['Authorization'] =
                  'Bearer ${res.data['access_token']}';
              final clone = await dio.fetch(req);
              return handler.resolve(clone);
            } catch (_) {
              // fall through to original error
            }
          }
        }
        handler.next(err);
      },
    ),
  );
  return dio;
});
