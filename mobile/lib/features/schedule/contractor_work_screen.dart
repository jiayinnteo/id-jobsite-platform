import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/schedule_repository.dart';
import '../../widgets/app_button.dart';
import '../../widgets/states.dart';
import '../../widgets/status_chip.dart';
import 'schedule_visit_sheet.dart';

/// Contractor's assigned rectification work, each with a "Schedule visit" action.
final contractorWorkProvider =
    FutureProvider.autoDispose<List<Map<String, dynamic>>>((ref) async {
  return ref.read(scheduleRepositoryProvider).contractorWork();
});

class ContractorWorkScreen extends ConsumerWidget {
  const ContractorWorkScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final work = ref.watch(contractorWorkProvider);

    return work.when(
      loading: () => const LoadingState(message: 'Loading your work…'),
      error: (_, __) => const EmptyState(
        icon: Icons.wifi_off_rounded,
        title: 'Could not load work',
        message: 'Check your connection and pull to refresh.',
      ),
      data: (items) {
        if (items.isEmpty) {
          return const EmptyState(
            icon: Icons.assignment_turned_in_outlined,
            title: 'No work assigned yet',
            message: 'Rectification jobs assigned to you will appear here.',
          );
        }
        return RefreshIndicator(
          onRefresh: () async => ref.invalidate(contractorWorkProvider),
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: items.length,
            itemBuilder: (context, i) {
              final item = items[i];
              return Card(
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
                              item['defect_title']?.toString() ?? 'Rectification',
                              style: Theme.of(context)
                                  .textTheme
                                  .titleMedium
                                  ?.copyWith(fontWeight: FontWeight.w700),
                            ),
                          ),
                          StatusChip(
                            status: item['defect_status']?.toString() ?? 'OPEN',
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      AppButton(
                        label: 'Schedule a visit',
                        icon: Icons.event_outlined,
                        kind: AppButtonKind.secondary,
                        onPressed: () async {
                          final result = await showScheduleVisitSheet(context);
                          if (result == null) return;
                          await ref
                              .read(scheduleRepositoryProvider)
                              .scheduleVisit(
                                item['job_id'].toString(),
                                rectificationId:
                                    item['rectification_id']?.toString(),
                                date: result.date,
                                time: result.time,
                              );
                          if (context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text(
                                  'Visit scheduled — added to calendars & team notified.',
                                ),
                              ),
                            );
                          }
                        },
                      ),
                    ],
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
