import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/jobs_repository.dart';
import '../../widgets/states.dart';
import 'jobs_providers.dart';

IconData _iconFor(String type) {
  switch (type) {
    case 'QUOTATION':
      return Icons.request_quote_outlined;
    case 'DRAWING_2D':
      return Icons.architecture_outlined;
    case 'DRAWING_3D':
      return Icons.view_in_ar_outlined;
    case 'SCHEDULE':
      return Icons.event_note_outlined;
    default:
      return Icons.insert_drive_file_outlined;
  }
}

class DocumentsTab extends ConsumerWidget {
  const DocumentsTab({super.key, required this.jobId});
  final String jobId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final docs = ref.watch(documentsProvider(jobId));
    return docs.when(
      loading: () => const LoadingState(),
      error: (_, __) => const EmptyState(
        icon: Icons.wifi_off_rounded,
        title: 'Could not load documents',
      ),
      data: (items) {
        if (items.isEmpty) {
          return const EmptyState(
            icon: Icons.folder_open_outlined,
            title: 'No documents yet',
            message: 'Quotations, 2D & 3D drawings and schedules appear here.',
          );
        }
        return RefreshIndicator(
          onRefresh: () async => ref.invalidate(documentsProvider(jobId)),
          child: ListView.builder(
            padding: const EdgeInsets.all(12),
            itemCount: items.length,
            itemBuilder: (context, i) {
              final d = items[i];
              return Card(
                child: ListTile(
                  leading: Icon(_iconFor(d.type)),
                  title: Text(d.title),
                  subtitle: Text(
                    '${d.type.replaceAll('_', ' ')} · v${d.currentVersionNo}',
                  ),
                  trailing: const Icon(Icons.download_outlined),
                  onTap: () async {
                    final url = await ref
                        .read(jobsRepositoryProvider)
                        .documentDownloadUrl(d.id);
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Download link ready: $url')),
                      );
                    }
                  },
                ),
              );
            },
          ),
        );
      },
    );
  }
}
