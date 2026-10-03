import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

/// Color-coded chip for defect / rectification statuses.
class StatusChip extends StatelessWidget {
  const StatusChip({super.key, required this.status});

  final String status;

  Color get _color {
    switch (status.toUpperCase()) {
      case 'OPEN':
        return AppColors.error;
      case 'ASSIGNED':
      case 'IN_PROGRESS':
        return AppColors.secondary;
      case 'RECTIFIED':
        return AppColors.primary;
      case 'ACCEPTED':
      case 'CLOSED':
        return AppColors.tertiary;
      case 'REJECTED':
        return AppColors.error;
      default:
        return AppColors.textSecondary;
    }
  }

  @override
  Widget build(BuildContext context) {
    final label = status.replaceAll('_', ' ');
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: _color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: _color,
          fontWeight: FontWeight.w700,
          fontSize: 12,
        ),
      ),
    );
  }
}
