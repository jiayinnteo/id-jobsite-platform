import 'package:flutter/material.dart';
import 'package:flutter/material.dart';

import '../features/demo/sample_job_screen.dart';
import 'user_role.dart';

/// A navigation destination for the per-role bottom bar.
class NavDest {
  const NavDest(this.icon, this.label, this.body);
  final IconData icon;
  final String label;
  final Widget body;
}

/// Per-role bottom-navigation shell. Every top-level area is one tap away
/// (max 5 destinations), per the design system.
class HomeShell extends StatefulWidget {
  const HomeShell({super.key, required this.role});
  final UserRole role;

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int _index = 0;

  List<NavDest> get _destinations {
    switch (widget.role) {
      case UserRole.idBoss:
        return const [
          NavDest(Icons.insights_outlined, 'Overview', _Placeholder('Firm Overview')),
          NavDest(Icons.folder_open_outlined, 'Firm Jobs',
              SampleJobScreen(mode: 'boss')),
          NavDest(Icons.reviews_outlined, 'Reviews',
              _Placeholder('Client reviews & average ratings')),
          NavDest(Icons.chat_bubble_outline, 'Chat', _Placeholder('Chat')),
          NavDest(Icons.notifications_none, 'Alerts', _Placeholder('Notifications')),
        ];
      case UserRole.id:
        return const [
          NavDest(Icons.home_outlined, 'Home', _Placeholder('ID Dashboard')),
          NavDest(Icons.work_outline, 'Jobs', _Placeholder('Jobs')),
          NavDest(Icons.chat_bubble_outline, 'Chat', _Placeholder('Chat')),
          NavDest(Icons.smart_toy_outlined, 'AI Inbox', _Placeholder('AI Review Inbox')),
          NavDest(Icons.notifications_none, 'Alerts', _Placeholder('Notifications')),
        ];
      case UserRole.client:
        return const [
          NavDest(Icons.home_outlined, 'Home', _Placeholder('Client Dashboard')),
          NavDest(Icons.description_outlined, 'Project', _Placeholder('Documents & Drawings')),
          NavDest(Icons.report_problem_outlined, 'Defects', _Placeholder('Defects')),
          NavDest(Icons.star_outline, 'Review', SampleJobScreen(mode: 'client')),
          NavDest(Icons.chat_bubble_outline, 'Chat', _Placeholder('Chat')),
        ];
      case UserRole.contractor:
        return const [
          NavDest(Icons.home_outlined, 'Home', _Placeholder('Contractor Dashboard')),
          NavDest(Icons.assignment_outlined, 'Work', _Placeholder('Assigned Work')),
          NavDest(Icons.event_outlined, 'Schedule', _Placeholder('Schedule')),
          NavDest(Icons.chat_bubble_outline, 'Chat', _Placeholder('Chat')),
          NavDest(Icons.notifications_none, 'Alerts', _Placeholder('Notifications')),
        ];
      case UserRole.worker:
        return const [
          NavDest(Icons.home_outlined, 'Home', _Placeholder('Worker Dashboard')),
          NavDest(Icons.event_available_outlined, 'Visits', _Placeholder('My Site Visits')),
          NavDest(Icons.photo_camera_outlined, 'Photos', _Placeholder('Upload Photos')),
          NavDest(Icons.notifications_none, 'Alerts', _Placeholder('Notifications')),
        ];
    }
  }

  @override
  Widget build(BuildContext context) {
    final dests = _destinations;
    return Scaffold(
      appBar: AppBar(title: Text(dests[_index].label)),
      body: dests[_index].body,
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: [
          for (final d in dests)
            NavigationDestination(icon: Icon(d.icon), label: d.label),
        ],
      ),
    );
  }
}

class _Placeholder extends StatelessWidget {
  const _Placeholder(this.title);
  final String title;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Text(
          '$title\n\nComing soon',
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.titleMedium,
        ),
      ),
    );
  }
}
