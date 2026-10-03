import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

import 'package:id_jobsite/app/home_shell.dart';
import 'package:id_jobsite/app/user_role.dart';
import 'package:id_jobsite/app/welcome_screen.dart';
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
  testWidgets('Welcome screen shows all roles', (tester) async {
    await tester.pumpWidget(_wrap(const WelcomeScreen()));
    await tester.pumpAndSettle();

    expect(find.text('Welcome'), findsOneWidget);
    for (final role in UserRole.values) {
      expect(find.text(role.label), findsOneWidget);
    }
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

  testWidgets('Client shell exposes a Review entry point', (tester) async {
    await tester.pumpWidget(_wrap(const HomeShell(role: UserRole.client)));
    await tester.pumpAndSettle();

    expect(find.text('Review'), findsWidgets);
  });
}
