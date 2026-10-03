import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/chat_repository.dart';
import '../../widgets/app_button.dart';
import '../../widgets/states.dart';

final pendingDraftsProvider =
    FutureProvider.autoDispose<List<Map<String, dynamic>>>((ref) async {
  return ref.read(chatRepositoryProvider).pendingDrafts();
});

/// Human-in-the-loop review inbox: AI drafts are edited/approved/rejected here.
/// Nothing is ever sent without an explicit approval.
class AiInboxScreen extends ConsumerWidget {
  const AiInboxScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final drafts = ref.watch(pendingDraftsProvider);
    return drafts.when(
      loading: () => const LoadingState(message: 'Loading drafts…'),
      error: (_, __) => const EmptyState(
        icon: Icons.wifi_off_rounded,
        title: 'Could not load drafts',
      ),
      data: (items) {
        if (items.isEmpty) {
          return const EmptyState(
            icon: Icons.smart_toy_outlined,
            title: 'No drafts to review',
            message: 'AI-suggested replies will appear here for your approval '
                'before anything is sent.',
          );
        }
        return RefreshIndicator(
          onRefresh: () async => ref.invalidate(pendingDraftsProvider),
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: items.length,
            itemBuilder: (context, i) =>
                _DraftCard(draft: items[i], onChanged: () {
              ref.invalidate(pendingDraftsProvider);
            }),
          ),
        );
      },
    );
  }
}

class _DraftCard extends ConsumerStatefulWidget {
  const _DraftCard({required this.draft, required this.onChanged});
  final Map<String, dynamic> draft;
  final VoidCallback onChanged;

  @override
  ConsumerState<_DraftCard> createState() => _DraftCardState();
}

class _DraftCardState extends ConsumerState<_DraftCard> {
  late final TextEditingController _controller = TextEditingController(
    text: (widget.draft['edited_text'] ?? widget.draft['draft_text'] ?? '')
        .toString(),
  );
  bool _busy = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  String get _id => widget.draft['id'].toString();

  Future<void> _run(Future<void> Function() action) async {
    setState(() => _busy = true);
    try {
      await action();
      widget.onChanged();
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final repo = ref.read(chatRepositoryProvider);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.smart_toy_outlined,
                    size: 18, color: Theme.of(context).colorScheme.primary),
                const SizedBox(width: 6),
                Text('AI suggested reply',
                    style: Theme.of(context).textTheme.labelLarge),
              ],
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _controller,
              maxLines: null,
              decoration: const InputDecoration(
                labelText: 'Edit before sending',
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: AppButton(
                    label: 'Reject',
                    kind: AppButtonKind.secondary,
                    loading: _busy,
                    onPressed: () => _run(() => repo.rejectDraft(_id)),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: AppButton(
                    label: 'Approve & send',
                    icon: Icons.send_rounded,
                    loading: _busy,
                    onPressed: () => _run(() async {
                      await repo.editDraft(_id, _controller.text.trim());
                      await repo.approveDraft(_id);
                    }),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
