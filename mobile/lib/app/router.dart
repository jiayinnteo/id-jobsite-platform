import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/auth/auth_controller.dart';
import '../features/auth/login_screen.dart';
import '../features/auth/register_screen.dart';
import '../features/defects/defect_detail_screen.dart';
import '../features/jobs/job_detail_screen.dart';
import 'home_shell.dart';
import 'user_role.dart';

/// Auth-aware router. Redirects to /login when signed out and to the role's
/// home when signed in.
final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/login',
    redirect: (context, state) {
      final auth = ref.read(authControllerProvider).valueOrNull;
      final loc = state.matchedLocation;
      final onAuthPage = loc == '/login' || loc == '/register';

      if (auth is AuthSignedIn) {
        return onAuthPage ? '/home/${auth.role.name}' : null;
      }
      if (auth is AuthSignedOut) {
        return onAuthPage ? null : '/login';
      }
      return null; // AuthUnknown / loading: stay put
    },
    routes: [
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/register', builder: (_, __) => const RegisterScreen()),
      GoRoute(
        path: '/home/:role',
        builder: (context, state) =>
            HomeShell(role: _roleFromName(state.pathParameters['role'])),
      ),
      GoRoute(
        path: '/job/:id',
        builder: (context, state) =>
            JobDetailScreen(jobId: state.pathParameters['id']!),
      ),
      GoRoute(
        path: '/defect/:id',
        builder: (context, state) =>
            DefectDetailScreen(defectId: state.pathParameters['id']!),
      ),
    ],
  );
});

UserRole _roleFromName(String? name) {
  return UserRole.values.firstWhere(
    (r) => r.name == name,
    orElse: () => UserRole.client,
  );
}
