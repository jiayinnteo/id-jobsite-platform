import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/user_role.dart';
import '../../data/jobs_repository.dart';
import '../../widgets/app_button.dart';
import '../../widgets/states.dart';
import '../../widgets/status_chip.dart';
import '../auth/auth_controller.dart';
import '../chat/job_chat_tab.dart';
import '../defects/defects_tab.dart';
import '../materials/materials_tab.dart';
import '../model3d/model_viewer_screen.dart';
import '../oversight/oversight_review_sheet.dart';
import '../reviews/leave_review_sheet.dart';
import 'documents_tab.dart';
import 'jobs_providers.dart';
import 'photos_tab.dart';

/// Hub screen for a single job: Overview, Documents, Defects, Photos, Chat.
class JobDetailScreen extends ConsumerWidget {
  const JobDetailScreen({super.key, required this.jobId});
  final String jobId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final job = ref.watch(jobProvider(jobId));

    return DefaultTabController(
      length: 7,
      child: Scaffold(
        appBar: AppBar(
          title: job.when(
            loading: () => const Text('Job'),
            error: (_, __) => const Text('Job'),
            data: (j) => Text(j.name),
          ),
          bottom: const TabBar(
            isScrollable: true,
            tabs: [
              Tab(text: 'Overview'),
              Tab(text: 'Documents'),
              Tab(text: 'Materials'),
              Tab(text: '3D'),
              Tab(text: 'Defects'),
              Tab(text: 'Photos'),
              Tab(text: 'Chat'),
            ],
          ),
        ),
        body: job.when(
          loading: () => const LoadingState(),
          error: (_, __) => const EmptyState(
            icon: Icons.error_outline,
            title: 'Could not load this job',
          ),
          data: (j) => TabBarView(
            children: [
              _Overview(
                jobId: jobId,
                name: j.name,
                address: j.address,
                status: j.status,
              ),
              DocumentsTab(jobId: jobId),
              MaterialsTab(jobId: jobId),
              _Model3dTab(jobId: jobId),
              DefectsTab(jobId: jobId),
              PhotosTab(jobId: jobId),
              JobChatTab(jobId: jobId),
            ],
          ),
        ),
      ),
    );
  }
}

class _Overview extends ConsumerWidget {
  const _Overview({
    required this.jobId,
    required this.name,
    required this.address,
    required this.status,
  });
  final String jobId;
  final String name;
  final String address;
  final String status;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authControllerProvider).valueOrNull;
    final role = auth is AuthSignedIn ? auth.role : null;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        name,
                        style: Theme.of(context)
                            .textTheme
                            .titleLarge
                            ?.copyWith(fontWeight: FontWeight.w800),
                      ),
                    ),
                    StatusChip(status: status),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    const Icon(Icons.place_outlined, size: 18),
                    const SizedBox(width: 6),
                    Expanded(child: Text(address)),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),

        // ID_BOSS: internal oversight review.
        if (role == UserRole.idBoss)
          AppButton(
            label: 'Review this job',
            icon: Icons.rate_review_outlined,
            kind: AppButtonKind.secondary,
            onPressed: () async {
              final result = await showOversightReviewSheet(context);
              if (result != null) {
                await ref.read(jobsRepositoryProvider).addOversightReview(
                      jobId,
                      flag: result.flag,
                      note: result.note,
                    );
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Oversight review saved.')),
                  );
                }
              }
            },
          ),

        // Client: leave a review once the job is completed.
        if (role == UserRole.client && status == 'COMPLETED')
          AppButton(
            label: 'Leave a review',
            icon: Icons.star_outline_rounded,
            onPressed: () async {
              final result = await showLeaveReviewSheet(context);
              if (result != null) {
                await ref.read(jobsRepositoryProvider).submitReview(
                      jobId,
                      rating: result.rating,
                      comment: result.comment,
                    );
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Thanks for your ${result.rating}★ review!'),
                    ),
                  );
                }
              }
            },
          ),
      ],
    );
  }
}

/// Finds the job's uploaded 3D model (if any) and shows the in-app viewer.
class _Model3dTab extends ConsumerWidget {
  const _Model3dTab({required this.jobId});
  final String jobId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final docs = ref.watch(documentsProvider(jobId));
    return docs.when(
      loading: () => const LoadingState(),
      error: (_, __) => const ModelViewerBody(modelUrl: null),
      data: (items) {
        final models = items.where((d) => d.type == 'MODEL_3D').toList();
        if (models.isEmpty) {
          return const ModelViewerBody(modelUrl: null);
        }
        final model = models.first;
        return FutureBuilder<String>(
          future: ref.read(jobsRepositoryProvider).documentDownloadUrl(model.id),
          builder: (context, snap) {
            if (!snap.hasData) return const LoadingState();
            return ModelViewerBody(modelUrl: snap.data, title: model.title);
          },
        );
      },
    );
  }
}
