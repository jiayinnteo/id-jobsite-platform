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

  Future<Job> getJob(String jobId) async {
    final res = await _dio.get('/jobs/$jobId');
    return Job.fromJson(res.data as Map<String, dynamic>);
  }

  // --- Documents ---
  Future<List<Document>> listDocuments(String jobId) async {
    final res = await _dio.get('/jobs/$jobId/documents');
    return (res.data as List)
        .map((e) => Document.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<String> documentDownloadUrl(String documentId) async {
    final res = await _dio.get('/documents/$documentId/download');
    return res.data['url'] as String;
  }

  // --- Defects ---
  Future<List<Defect>> listDefects(String jobId) async {
    final res = await _dio.get('/jobs/$jobId/defects');
    return (res.data as List)
        .map((e) => Defect.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<Defect> getDefect(String defectId) async {
    final res = await _dio.get('/defects/$defectId');
    return Defect.fromJson(res.data as Map<String, dynamic>);
  }

  Future<List<DefectHistoryEntry>> defectHistory(String defectId) async {
    final res = await _dio.get('/defects/$defectId/history');
    return (res.data as List)
        .map((e) => DefectHistoryEntry.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<void> updateDefectStatus(
    String defectId, {
    required String toStatus,
    String? reason,
  }) async {
    await _dio.patch('/defects/$defectId/status', data: {
      'to_status': toStatus,
      'reason': reason,
    });
  }

  // --- Photos ---
  Future<List<Photo>> listPhotos(String jobId) async {
    final res = await _dio.get('/jobs/$jobId/photos');
    return (res.data as List)
        .map((e) => Photo.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  /// Requests a pre-signed upload target for a photo, then (caller) PUTs bytes.
  Future<Map<String, dynamic>> createPhoto(
    String jobId, {
    required String filename,
    required String mimeType,
    required int sizeBytes,
    String? caption,
    String? defectId,
  }) async {
    final res = await _dio.post('/jobs/$jobId/photos', data: {
      'filename': filename,
      'mime_type': mimeType,
      'size_bytes': sizeBytes,
      'caption': caption,
      'defect_id': defectId,
    });
    return res.data as Map<String, dynamic>;
  }

  /// Uploads raw bytes to a pre-signed URL (no auth header).
  Future<void> uploadToPresignedUrl(
    String url,
    List<int> bytes,
    String mimeType,
  ) async {
    if (url.startsWith('mock://')) return; // dev/mock storage: nothing to PUT
    await Dio().put(
      url,
      data: Stream.fromIterable([bytes]),
      options: Options(
        headers: {
          'Content-Type': mimeType,
          Headers.contentLengthHeader: bytes.length,
        },
      ),
    );
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
