import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../widgets/app_button.dart';
import 'user_role.dart';

/// Warm, welcoming landing screen. Until auth (Phase 1) lands, this lets you
/// preview each role's navigation shell.
class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 32),
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: scheme.secondaryContainer,
                  borderRadius: BorderRadius.circular(24),
                ),
                child: Icon(Icons.home_work_rounded,
                    size: 56, color: scheme.primary),
              ),
              const SizedBox(height: 24),
              Text(
                'Welcome',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
              ),
              const SizedBox(height: 8),
              Text(
                'Manage your renovation projects and stay in touch with '
                'your designer, contractors and clients — all in one place.',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: scheme.onSurfaceVariant,
                    ),
              ),
              const Spacer(),
              Text(
                'Preview a role',
                style: Theme.of(context).textTheme.labelLarge,
              ),
              const SizedBox(height: 12),
              for (final role in UserRole.values) ...[
                AppButton(
                  label: role.label,
                  kind: role == UserRole.id
                      ? AppButtonKind.primary
                      : AppButtonKind.secondary,
                  onPressed: () => context.go('/home/${role.name}'),
                ),
                const SizedBox(height: 12),
              ],
              const SizedBox(height: 8),
            ],
          ),
        ),
      ),
    );
  }
}
