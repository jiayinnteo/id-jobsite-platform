import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

import 'package:id_jobsite/app/home_shell.dart';
import 'package:id_jobsite/app/user_role.dart';
import 'package:id_jobsite/data/auth_repository.dart';
import 'package:id_jobsite/features/auth/login_screen.dart';
import 'package:id_jobsite/theme/app_theme.dart';

/// Auth repo stub that reports "signed out" instantly — no HTTP, so tests
/// don't leave pending network timers.
class _StubAuthRepository implements AuthRepository {
  @override
  Future<UserRole?> currentRole() async => null;
  @override
  Future<void> login(String email, String password) async {}
  @override
  Future<void> register({
    required String email,
    required String password,
    required String fullName,
    required UserRole role,
    String? phone,
  }) async {}
  @override
  Future<void> logout() async {}
}

Widget _wrap(Widget child) {
  final router = GoRouter(
    initialLocation: '/',
    routes: [GoRoute(path: '/', builder: (_, __) => child)],
  );
  return ProviderScope(
    overrides: [
      authRepositoryProvider.overrideWithValue(_StubAuthRepository()),
    ],
    child: MaterialApp.router(
      theme: AppTheme.light,
      routerConfig: router,
    ),
  );
}

void main() {
  testWidgets('Login screen renders sign-in form', (tester) async {
    await tester.pumpWidget(_wrap(const LoginScreen()));
    await tester.pump();

    expect(find.text('Welcome back'), findsOneWidget);
    expect(find.text('Sign in'), findsOneWidget);
    expect(find.text('Email'), findsOneWidget);
  });

  // Nav structure is tested via the pure label source of truth, so these tests
  // don't mount data-fetching screens (which would leave pending timers).
  test('ID shell nav exposes Jobs, AI Inbox and Alerts', () {
    final labels = navLabelsFor(UserRole.id);
    expect(labels, containsAll(['Jobs', 'AI Inbox', 'Alerts']));
  });

  test('ID_BOSS shell nav exposes Firm Jobs and AI Inbox', () {
    final labels = navLabelsFor(UserRole.idBoss);
    expect(labels, containsAll(['Firm Jobs', 'AI Inbox', 'Alerts']));
  });

  test('Client shell nav exposes My Project and Alerts', () {
    expect(navLabelsFor(UserRole.client), containsAll(['My Project', 'Alerts']));
  });

  test('Contractor shell nav exposes Work and Jobs', () {
    expect(navLabelsFor(UserRole.contractor), containsAll(['Work', 'Jobs']));
  });

  test('Worker shell nav exposes Visits and Jobs', () {
    expect(navLabelsFor(UserRole.worker), containsAll(['Visits', 'Jobs']));
  });

  test('Every role has an Alerts destination (max 5)', () {
    for (final role in UserRole.values) {
      final labels = navLabelsFor(role);
      expect(labels, contains('Alerts'));
      expect(labels.length, lessThanOrEqualTo(5));
    }
  });
}
