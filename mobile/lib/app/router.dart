import 'package:go_router/go_router.dart';

import 'home_shell.dart';
import 'user_role.dart';
import 'welcome_screen.dart';

UserRole _roleFromName(String? name) {
  return UserRole.values.firstWhere(
    (r) => r.name == name,
    orElse: () => UserRole.id,
  );
}

final appRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const WelcomeScreen(),
    ),
    GoRoute(
      path: '/home/:role',
      builder: (context, state) =>
          HomeShell(role: _roleFromName(state.pathParameters['role'])),
    ),
  ],
);
