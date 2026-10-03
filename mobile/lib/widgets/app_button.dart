import 'package:flutter/material.dart';

enum AppButtonKind { primary, secondary, destructive }

/// Shared button. Use instead of raw buttons so styling stays consistent.
class AppButton extends StatelessWidget {
  const AppButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.kind = AppButtonKind.primary,
    this.icon,
    this.loading = false,
  });

  final String label;
  final VoidCallback? onPressed;
  final AppButtonKind kind;
  final IconData? icon;
  final bool loading;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final child = loading
        ? const SizedBox(
            height: 20,
            width: 20,
            child: CircularProgressIndicator(strokeWidth: 2.5),
          )
        : Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (icon != null) ...[Icon(icon, size: 20), const SizedBox(width: 8)],
              Text(label),
            ],
          );

    final onTap = loading ? null : onPressed;

    switch (kind) {
      case AppButtonKind.primary:
        return FilledButton(onPressed: onTap, child: child);
      case AppButtonKind.secondary:
        return OutlinedButton(onPressed: onTap, child: child);
      case AppButtonKind.destructive:
        return FilledButton(
          onPressed: onTap,
          style: FilledButton.styleFrom(
            backgroundColor: scheme.error,
            foregroundColor: scheme.onError,
          ),
          child: child,
        );
    }
  }
}
