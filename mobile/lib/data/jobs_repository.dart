import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'api_client.dart';
import 'models.dart';

final jobsRepositoryProvider = Provider(
  (ref) => JobsRepository(ref.read(apiClientProvider)),
);

/// Talks to the jobs / defects / reviews endpoints.
class JobsRepository {
  JobsRepository(this._dio);
  final Dio _dio;

  Future<List<Job>> listJobs() async {
    final res = await _dio.get('/jobs');
    return (res.data as List)
        .map((e) => Job.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<Defect>> listDefects(String jobId) async {
    final res = await _dio.get('/jobs/$jobId/defects');
    return (res.data as List)
        .map((e) => Defect.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<Defect> createDefect(
    String jobId, {
    required String title,
    String? description,
    String? location,
  }) async {
    final res = await _dio.post('/jobs/$jobId/defects', data: {
      'title': title,
      'description': description,
      'location': location,
    });
    return Defect.fromJson(res.data as Map<String, dynamic>);
  }

  /// Client Accept/Reject on a rectification.
  Future<void> decideRectification(
    String rectificationId, {
    required bool accept,
    String? reason,
  }) async {
    await _dio.post('/rectifications/$rectificationId/decision', data: {
      'decision': accept ? 'ACCEPTED' : 'REJECTED',
      'reason': reason,
    });
  }

  /// ID_BOSS oversight review.
  Future<void> addOversightReview(
    String jobId, {
    required String flag, // NEEDS_ATTENTION | APPROVED
    String? note,
  }) async {
    await _dio.post('/jobs/$jobId/oversight-reviews', data: {
      'flag': flag,
      'note': note,
    });
  }

  /// Client review/rating of a completed job.
  Future<void> submitReview(
    String jobId, {
    required int rating,
    String? comment,
  }) async {
    await _dio.post('/jobs/$jobId/review', data: {
      'rating': rating,
      'comment': comment,
    });
  }
}
