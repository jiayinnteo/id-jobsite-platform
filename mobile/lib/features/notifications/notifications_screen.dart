import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/chat_repository.dart';
import '../../widgets/states.dart';

final notificationsProvider =
    FutureProvider.autoDispose<List<Map<String, dynamic>>>((ref) async {
  return ref.read(chatRepositoryProvider).notifications();
});

class NotificationsScreen extends ConsumerWidget {
  const NotificationsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final notifs = ref.watch(notificationsProvider);
    return notifs.when(
      loading: () => const LoadingState(message: 'Loading notifications…'),
      error: (_, __) => const EmptyState(
        icon: Icons.wifi_off_rounded,
        title: 'Could not load notifications',
      ),
      data: (items) {
        if (items.isEmpty) {
          return const EmptyState(
            icon: Icons.notifications_none_rounded,
            title: 'You’re all caught up',
            message: 'New updates about your projects will show here.',
          );
        }
        return RefreshIndicator(
          onRefresh: () async => ref.invalidate(notificationsProvider),
          child: ListView.separated(
            padding: const EdgeInsets.all(12),
            itemCount: items.length,
            separatorBuilder: (_, __) => const SizedBox(height: 4),
            itemBuilder: (context, i) {
              final n = items[i];
              final unread = n['read_at'] == null;
              return Card(
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: Theme.of(context)
                        .colorScheme
                        .secondaryContainer,
                    child: Icon(
                      unread
                          ? Icons.notifications_active_outlined
                          : Icons.notifications_none,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                  title: Text(
                    n['title']?.toString() ?? '',
                    style: TextStyle(
                      fontWeight: unread ? FontWeight.w700 : FontWeight.w500,
                    ),
                  ),
                  subtitle: n['body'] != null ? Text(n['body'].toString()) : null,
                  onTap: () async {
                    await ref
                        .read(chatRepositoryProvider)
                        .markRead(n['id'].toString());
                    ref.invalidate(notificationsProvider);
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
