import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../widgets/states.dart';
import '../../widgets/status_chip.dart';
import 'jobs_providers.dart';

/// List of jobs the user belongs to (ID_BOSS sees the whole firm).
class JobsListScreen extends ConsumerWidget {
  const JobsListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final jobs = ref.watch(jobsListProvider);
    return jobs.when(
      loading: () => const LoadingState(message: 'Loading your jobs…'),
      error: (_, __) => const EmptyState(
        icon: Icons.wifi_off_rounded,
        title: 'Could not load jobs',
        message: 'Check your connection and pull to refresh.',
      ),
      data: (items) {
        if (items.isEmpty) {
          return const EmptyState(
            icon: Icons.work_outline_rounded,
            title: 'No jobs yet',
            message: 'Your projects will appear here.',
          );
        }
        return RefreshIndicator(
          onRefresh: () async => ref.invalidate(jobsListProvider),
          child: ListView.builder(
            padding: const EdgeInsets.all(12),
            itemCount: items.length,
            itemBuilder: (context, i) {
              final job = items[i];
              return Card(
                child: ListTile(
                  title: Text(
                    job.name,
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                  subtitle: Text(job.address),
                  trailing: StatusChip(status: job.status),
                  onTap: () => context.push('/job/${job.id}'),
                ),
              );
            },
          ),
        );
      },
    );
  }
}
