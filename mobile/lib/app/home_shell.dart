import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/chat_repository.dart';
import '../features/ai/ai_inbox_screen.dart';
import '../features/auth/auth_controller.dart';
import '../features/jobs/jobs_list_screen.dart';
import '../features/notifications/notifications_screen.dart';
import '../features/schedule/contractor_work_screen.dart';
import '../features/schedule/worker_visits_screen.dart';
import 'user_role.dart';

/// Unread notification count for the Alerts badge.
final unreadCountProvider = FutureProvider.autoDispose<int>((ref) async {
  return ref.read(chatRepositoryProvider).unreadCount();
});

/// A navigation destination for the per-role bottom bar.
class NavDest {
  const NavDest(this.icon, this.label, this.body);
  final IconData icon;
  final String label;
  final Widget body;
}

/// Per-role bottom-navigation shell. Every top-level area is one tap away
/// (max 5 destinations), per the design system.
class HomeShell extends ConsumerStatefulWidget {
  const HomeShell({super.key, required this.role});
  final UserRole role;

  @override
  ConsumerState<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends ConsumerState<HomeShell> {
  int _index = 0;

  List<NavDest> get _destinations {
    switch (widget.role) {
      case UserRole.idBoss:
        return const [
          NavDest(Icons.folder_open_outlined, 'Firm Jobs', JobsListScreen()),
          NavDest(Icons.smart_toy_outlined, 'AI Inbox', AiInboxScreen()),
          NavDest(Icons.notifications_none, 'Alerts', NotificationsScreen()),
        ];
      case UserRole.id:
        return const [
          NavDest(Icons.work_outline, 'Jobs', JobsListScreen()),
          NavDest(Icons.smart_toy_outlined, 'AI Inbox', AiInboxScreen()),
          NavDest(Icons.notifications_none, 'Alerts', NotificationsScreen()),
        ];
      case UserRole.client:
        return const [
          NavDest(Icons.work_outline, 'My Project', JobsListScreen()),
          NavDest(Icons.notifications_none, 'Alerts', NotificationsScreen()),
        ];
      case UserRole.contractor:
        return const [
          NavDest(Icons.assignment_outlined, 'Work', ContractorWorkScreen()),
          NavDest(Icons.work_outline, 'Jobs', JobsListScreen()),
          NavDest(Icons.notifications_none, 'Alerts', NotificationsScreen()),
        ];
      case UserRole.worker:
        return const [
          NavDest(Icons.event_available_outlined, 'Visits', WorkerVisitsScreen()),
          NavDest(Icons.work_outline, 'Jobs', JobsListScreen()),
          NavDest(Icons.notifications_none, 'Alerts', NotificationsScreen()),
        ];
    }
  }

  /// The index of the Alerts (notifications) tab, for the unread badge.
  int get _alertsIndex =>
      _destinations.indexWhere((d) => d.label == 'Alerts');

  @override
  Widget build(BuildContext context) {
    final dests = _destinations;
    final unread = ref.watch(unreadCountProvider).valueOrNull ?? 0;
    final alertsIndex = _alertsIndex;

    return Scaffold(
      appBar: AppBar(
        title: Text(dests[_index].label),
        actions: [
          IconButton(
            tooltip: 'Sign out',
            icon: const Icon(Icons.logout_rounded),
            onPressed: () =>
                ref.read(authControllerProvider.notifier).logout(),
          ),
        ],
      ),
      body: dests[_index].body,
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) {
          setState(() => _index = i);
          if (i == alertsIndex) ref.invalidate(unreadCountProvider);
        },
        destinations: [
          for (var i = 0; i < dests.length; i++)
            NavigationDestination(
              icon: (i == alertsIndex && unread > 0)
                  ? Badge(label: Text('$unread'), child: Icon(dests[i].icon))
                  : Icon(dests[i].icon),
              label: dests[i].label,
            ),
        ],
      ),
    );
  }
}
