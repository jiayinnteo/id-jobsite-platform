import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/jobs_repository.dart';
import '../../widgets/app_button.dart';
import '../../widgets/states.dart';
import '../../widgets/status_chip.dart';
import '../jobs/jobs_providers.dart';
import 'accept_reject_bar.dart';

/// Full defect view: status, history, and role-aware actions
/// (status advance for the firm/contractor, Accept/Reject for the client).
class DefectDetailScreen extends ConsumerWidget {
  const DefectDetailScreen({super.key, required this.defectId});
  final String defectId;

  static const _nextStatus = {
    'ASSIGNED': 'IN_PROGRESS',
    'IN_PROGRESS': 'RECTIFIED',
  };

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final defect = ref.watch(defectProvider(defectId));
    final history = ref.watch(defectHistoryProvider(defectId));

    return Scaffold(
      appBar: AppBar(title: const Text('Defect')),
      body: defect.when(
        loading: () => const LoadingState(),
        error: (_, __) => const EmptyState(
          icon: Icons.error_outline,
          title: 'Could not load this defect',
        ),
        data: (d) {
          final advance = _nextStatus[d.status];
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
                              d.title,
                              style: Theme.of(context)
                                  .textTheme
                                  .titleLarge
                                  ?.copyWith(fontWeight: FontWeight.w800),
                            ),
                          ),
                          StatusChip(status: d.status),
                        ],
                      ),
                      if (d.location != null) ...[
                        const SizedBox(height: 6),
                        Text(d.location!),
                      ],
                      if (d.description != null) ...[
                        const SizedBox(height: 8),
                        Text(d.description!),
                      ],
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Firm / contractor: advance the status along the state machine.
              if (advance != null)
                AppButton(
                  label: 'Mark as ${advance.replaceAll('_', ' ').toLowerCase()}',
                  icon: Icons.arrow_forward_rounded,
                  onPressed: () async {
                    await ref.read(jobsRepositoryProvider).updateDefectStatus(
                          defectId,
                          toStatus: advance,
                        );
                    ref.invalidate(defectProvider(defectId));
                    ref.invalidate(defectHistoryProvider(defectId));
                  },
                ),

              // Client: accept/reject once work is rectified.
              if (d.status == 'RECTIFIED' && d.rectificationId != null) ...[
                const SizedBox(height: 8),
                Text('Is this work complete?',
                    style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                AcceptRejectBar(
                  onDecision: ({required accept, reason}) async {
                    await ref.read(jobsRepositoryProvider).decideRectification(
                          d.rectificationId!,
                          accept: accept,
                          reason: reason,
                        );
                    ref.invalidate(defectProvider(defectId));
                    ref.invalidate(defectHistoryProvider(defectId));
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(accept
                              ? 'Accepted — your designer has been notified.'
                              : 'Rejected — the team will take another look.'),
                        ),
                      );
                    }
                  },
                ),
              ],

              const SizedBox(height: 20),
              Text('History', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 8),
              history.when(
                loading: () => const Padding(
                  padding: EdgeInsets.all(16),
                  child: Center(child: CircularProgressIndicator()),
                ),
                error: (_, __) => const Text('Could not load history.'),
                data: (entries) => Column(
                  children: [
                    for (final h in entries)
                      ListTile(
                        dense: true,
                        leading: const Icon(Icons.history, size: 20),
                        title: Text(
                          h.fromStatus == null
                              ? 'Created (${h.toStatus})'
                              : '${h.fromStatus} → ${h.toStatus}',
                        ),
                        subtitle: h.reason != null ? Text(h.reason!) : null,
                      ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
