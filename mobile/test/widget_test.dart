import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

import 'package:id_jobsite/app/home_shell.dart';
import 'package:id_jobsite/app/user_role.dart';
import 'package:id_jobsite/features/auth/login_screen.dart';
import 'package:id_jobsite/theme/app_theme.dart';

Widget _wrap(Widget child) {
  final router = GoRouter(
    initialLocation: '/',
    routes: [GoRoute(path: '/', builder: (_, __) => child)],
  );
  return ProviderScope(
    child: MaterialApp.router(
      theme: AppTheme.light,
      routerConfig: router,
    ),
  );
}

void main() {
  testWidgets('Login screen renders sign-in form', (tester) async {
    await tester.pumpWidget(_wrap(const LoginScreen()));
    await tester.pumpAndSettle();

    expect(find.text('Welcome back'), findsOneWidget);
    expect(find.text('Sign in'), findsOneWidget);
    expect(find.text('Email'), findsOneWidget);
  });

  testWidgets('ID shell shows Jobs, AI Inbox and Alerts', (tester) async {
    await tester.pumpWidget(_wrap(const HomeShell(role: UserRole.id)));
    await tester.pump(); // nav bar renders synchronously

    expect(find.byType(NavigationBar), findsOneWidget);
    expect(find.text('Jobs'), findsWidgets);
    expect(find.text('AI Inbox'), findsWidgets);
    expect(find.text('Alerts'), findsWidgets);
  });

  testWidgets('ID_BOSS shell exposes Firm Jobs', (tester) async {
    await tester.pumpWidget(_wrap(const HomeShell(role: UserRole.idBoss)));
    await tester.pump();

    expect(find.text('Firm Jobs'), findsWidgets);
  });

  testWidgets('Contractor shell exposes Work', (tester) async {
    await tester.pumpWidget(_wrap(const HomeShell(role: UserRole.contractor)));
    await tester.pump();

    expect(find.text('Work'), findsWidgets);
  });

  testWidgets('Worker shell exposes Visits', (tester) async {
    await tester.pumpWidget(_wrap(const HomeShell(role: UserRole.worker)));
    await tester.pump();

    expect(find.text('Visits'), findsWidgets);
  });
}
