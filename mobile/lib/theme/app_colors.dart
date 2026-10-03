import 'package:flutter/material.dart';

/// Warm, welcoming palette for the ID job-site platform.
/// See .kiro/steering/ui-design-system.md for rationale.
class AppColors {
  AppColors._();

  static const Color primary = Color(0xFFE07A5F); // warm terracotta
  static const Color secondary = Color(0xFFF2CC8F); // soft amber
  static const Color tertiary = Color(0xFF81B29A); // muted sage (success)

  static const Color background = Color(0xFFFBF7F2); // warm off-white
  static const Color surface = Color(0xFFFFFFFF);
  static const Color surfaceWarm = Color(0xFFFFF9F3);

  static const Color error = Color(0xFFC1554B); // warm red
  static const Color textPrimary = Color(0xFF3D3A36); // warm charcoal
  static const Color textSecondary = Color(0xFF7A736B);

  /// Seed used to derive the full Material 3 color scheme (light + dark).
  static const Color seed = primary;
}
