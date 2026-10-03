import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'app/router.dart';
import 'features/auth/auth_controller.dart';
import 'theme/app_theme.dart';

void main() {
  runApp(const ProviderScope(child: IdJobsiteApp()));
}

class IdJobsiteApp extends ConsumerWidget {
  const IdJobsiteApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Rebuild the router when the auth session changes so redirects re-run.
    ref.watch(authControllerProvider);
    final router = ref.watch(appRouterProvider);

    return MaterialApp.router(
      title: 'ID Job-Site',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: ThemeMode.system,
      routerConfig: router,
    );
  }
}
