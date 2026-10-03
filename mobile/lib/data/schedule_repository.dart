import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'api_client.dart';

final scheduleRepositoryProvider = Provider(
  (ref) => ScheduleRepository(ref.read(apiClientProvider)),
);

/// Contractor work queue + site-visit scheduling.
class ScheduleRepository {
  ScheduleRepository(this._dio);
  final Dio _dio;

  Future<List<Map<String, dynamic>>> contractorWork() async {
    final res = await _dio.get('/contractor/work');
    return (res.data as List).cast<Map<String, dynamic>>();
  }

  Future<List<Map<String, dynamic>>> jobVisits(String jobId) async {
    final res = await _dio.get('/jobs/$jobId/visits');
    return (res.data as List).cast<Map<String, dynamic>>();
  }

  /// Schedule a site visit. Date is YYYY-MM-DD, time is HH:MM:SS (optional).
  Future<Map<String, dynamic>> scheduleVisit(
    String jobId, {
    String? rectificationId,
    required String date,
    String? time,
    List<String> workerIds = const [],
  }) async {
    final res = await _dio.post('/jobs/$jobId/visits', data: {
      'rectification_id': rectificationId,
      'scheduled_date': date,
      'scheduled_time': time,
      'worker_ids': workerIds,
    });
    return res.data as Map<String, dynamic>;
  }

  Future<List<Map<String, dynamic>>> myWorkerVisits() async {
    final res = await _dio.get('/worker/visits');
    return (res.data as List).cast<Map<String, dynamic>>();
  }
}
