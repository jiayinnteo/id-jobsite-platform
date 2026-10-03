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

  testWidgets('ID home shell renders a 5-item bottom nav', (tester) async {
    await tester.pumpWidget(_wrap(const HomeShell(role: UserRole.id)));
    await tester.pumpAndSettle();

    expect(find.byType(NavigationBar), findsOneWidget);
    expect(find.text('Jobs'), findsWidgets);
    expect(find.text('AI Inbox'), findsOneWidget);
  });

  testWidgets('ID_BOSS shell exposes firm oversight + reviews', (tester) async {
    await tester.pumpWidget(_wrap(const HomeShell(role: UserRole.idBoss)));
    await tester.pumpAndSettle();

    expect(find.text('Firm Jobs'), findsWidgets);
    expect(find.text('Reviews'), findsWidgets);
  });

  testWidgets('Contractor shell exposes Work and Schedule', (tester) async {
    await tester.pumpWidget(_wrap(const HomeShell(role: UserRole.contractor)));
    await tester.pumpAndSettle();

    expect(find.text('Work'), findsWidgets);
    expect(find.text('Schedule'), findsWidgets);
  });
}
