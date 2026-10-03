import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../widgets/states.dart';
import '../../widgets/status_chip.dart';
import '../jobs/jobs_providers.dart';

/// A worker's assigned site visits, soonest first.
class WorkerVisitsScreen extends ConsumerWidget {
  const WorkerVisitsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final visits = ref.watch(workerVisitsProvider);
    return visits.when(
      loading: () => const LoadingState(message: 'Loading your visits…'),
      error: (_, __) => const EmptyState(
        icon: Icons.wifi_off_rounded,
        title: 'Could not load visits',
      ),
      data: (items) {
        if (items.isEmpty) {
          return const EmptyState(
            icon: Icons.event_available_outlined,
            title: 'No site visits scheduled',
            message: 'Visits your boss schedules for you will appear here.',
          );
        }
        return RefreshIndicator(
          onRefresh: () async => ref.invalidate(workerVisitsProvider),
          child: ListView.builder(
            padding: const EdgeInsets.all(12),
            itemCount: items.length,
            itemBuilder: (context, i) {
              final v = items[i];
              final time = v['scheduled_time']?.toString();
              return Card(
                child: ListTile(
                  leading: const CircleAvatar(
                    child: Icon(Icons.handyman_outlined),
                  ),
                  title: Text('Visit on ${v['scheduled_date']}'),
                  subtitle: time != null ? Text('at $time') : null,
                  trailing: StatusChip(
                    status: v['status']?.toString() ?? 'SCHEDULED',
                  ),
                ),
              );
            },
          ),
        );
      },
    );
  }
}
