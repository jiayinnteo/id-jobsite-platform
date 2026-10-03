import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/chat_repository.dart';
import '../../widgets/states.dart';
import 'chat_screen.dart';

/// Resolves the job's conversation, then shows the live chat screen.
final conversationIdProvider =
    FutureProvider.autoDispose.family<String, String>((ref, jobId) async {
  final convo = await ref.read(chatRepositoryProvider).conversationForJob(jobId);
  return convo['id'] as String;
});

class JobChatTab extends ConsumerWidget {
  const JobChatTab({super.key, required this.jobId});
  final String jobId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final convo = ref.watch(conversationIdProvider(jobId));
    return convo.when(
      loading: () => const LoadingState(message: 'Opening chat…'),
      error: (_, __) => const EmptyState(
        icon: Icons.wifi_off_rounded,
        title: 'Could not open chat',
      ),
      data: (conversationId) => ChatScreen(conversationId: conversationId),
    );
  }
}
