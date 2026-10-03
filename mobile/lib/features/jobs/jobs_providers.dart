import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/jobs_repository.dart';
import '../../data/models.dart';
import '../../data/schedule_repository.dart';

/// All jobs visible to the signed-in user.
final jobsListProvider = FutureProvider.autoDispose<List<Job>>((ref) async {
  return ref.read(jobsRepositoryProvider).listJobs();
});

/// A single job by id.
final jobProvider =
    FutureProvider.autoDispose.family<Job, String>((ref, jobId) async {
  return ref.read(jobsRepositoryProvider).getJob(jobId);
});

final documentsProvider = FutureProvider.autoDispose
    .family<List<Document>, String>((ref, jobId) async {
  return ref.read(jobsRepositoryProvider).listDocuments(jobId);
});

final defectsProvider =
    FutureProvider.autoDispose.family<List<Defect>, String>((ref, jobId) async {
  return ref.read(jobsRepositoryProvider).listDefects(jobId);
});

final defectProvider = FutureProvider.autoDispose
    .family<Defect, String>((ref, defectId) async {
  return ref.read(jobsRepositoryProvider).getDefect(defectId);
});

final defectHistoryProvider = FutureProvider.autoDispose
    .family<List<DefectHistoryEntry>, String>((ref, defectId) async {
  return ref.read(jobsRepositoryProvider).defectHistory(defectId);
});

final photosProvider =
    FutureProvider.autoDispose.family<List<Photo>, String>((ref, jobId) async {
  return ref.read(jobsRepositoryProvider).listPhotos(jobId);
});

final workerVisitsProvider =
    FutureProvider.autoDispose<List<Map<String, dynamic>>>((ref) async {
  return ref.read(scheduleRepositoryProvider).myWorkerVisits();
});
