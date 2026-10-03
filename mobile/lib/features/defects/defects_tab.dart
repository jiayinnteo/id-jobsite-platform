import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/jobs_repository.dart';
import '../../widgets/app_button.dart';
import '../../widgets/states.dart';
import '../../widgets/status_chip.dart';
import '../jobs/jobs_providers.dart';

class DefectsTab extends ConsumerWidget {
  const DefectsTab({super.key, required this.jobId});
  final String jobId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final defects = ref.watch(defectsProvider(jobId));
    return Scaffold(
      body: defects.when(
        loading: () => const LoadingState(),
        error: (_, __) => const EmptyState(
          icon: Icons.wifi_off_rounded,
          title: 'Could not load defects',
        ),
        data: (items) {
          if (items.isEmpty) {
            return const EmptyState(
              icon: Icons.verified_outlined,
              title: 'No defects reported',
              message: 'Report an issue with a photo and the team will track it.',
            );
          }
          return RefreshIndicator(
            onRefresh: () async => ref.invalidate(defectsProvider(jobId)),
            child: ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: items.length,
              itemBuilder: (context, i) {
                final d = items[i];
                return Card(
                  child: ListTile(
                    title: Text(
                      d.title,
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                    subtitle: d.location != null ? Text(d.location!) : null,
                    trailing: StatusChip(status: d.status),
                    onTap: () => context.push('/defect/${d.id}'),
                  ),
                );
              },
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _createDefect(context, ref),
        icon: const Icon(Icons.add),
        label: const Text('Report defect'),
      ),
    );
  }

  Future<void> _createDefect(BuildContext context, WidgetRef ref) async {
    final titleCtrl = TextEditingController();
    final descCtrl = TextEditingController();
    final locCtrl = TextEditingController();

    final created = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) => Padding(
        padding: EdgeInsets.fromLTRB(
          24, 8, 24, 24 + MediaQuery.of(context).viewInsets.bottom,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Report a defect',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w800,
                    )),
            const SizedBox(height: 12),
            TextField(
              controller: titleCtrl,
              decoration: const InputDecoration(labelText: 'What is the issue?'),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: locCtrl,
              decoration: const InputDecoration(labelText: 'Location / room'),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: descCtrl,
              maxLines: 3,
              decoration: const InputDecoration(labelText: 'Details (optional)'),
            ),
            const SizedBox(height: 8),
            Text(
              'Tip: add photos from the Photos tab after creating the defect.',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 16),
            AppButton(
              label: 'Submit',
              icon: Icons.send_rounded,
              onPressed: () async {
                if (titleCtrl.text.trim().isEmpty) return;
                await ref.read(jobsRepositoryProvider).createDefect(
                      jobId,
                      title: titleCtrl.text.trim(),
                      description: descCtrl.text.trim().isEmpty
                          ? null
                          : descCtrl.text.trim(),
                      location: locCtrl.text.trim().isEmpty
                          ? null
                          : locCtrl.text.trim(),
                    );
                if (context.mounted) Navigator.pop(context, true);
              },
            ),
          ],
        ),
      ),
    );

    if (created == true) {
      ref.invalidate(defectsProvider(jobId));
    }
  }
}
