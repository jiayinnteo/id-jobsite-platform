import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

/// "Reviewed" tag with a star rating, shown to firm members (ID / ID_BOSS)
/// on jobs a client has reviewed. See Requirement 16.
class ReviewTag extends StatelessWidget {
  const ReviewTag({super.key, required this.rating});

  /// 1..5
  final double rating;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: AppColors.secondary.withValues(alpha: 0.25),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.verified_outlined, size: 14, color: AppColors.textPrimary),
          const SizedBox(width: 4),
          const Text(
            'Reviewed',
            style: TextStyle(
              color: AppColors.textPrimary,
              fontWeight: FontWeight.w700,
              fontSize: 12,
            ),
          ),
          const SizedBox(width: 6),
          const Icon(Icons.star_rounded, size: 15, color: AppColors.primary),
          const SizedBox(width: 2),
          Text(
            rating.toStringAsFixed(1),
            style: const TextStyle(
              color: AppColors.textPrimary,
              fontWeight: FontWeight.w700,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }
}

/// Interactive 1–5 star selector for clients leaving a review.
class StarRatingInput extends StatelessWidget {
  const StarRatingInput({
    super.key,
    required this.value,
    required this.onChanged,
  });

  final int value;
  final ValueChanged<int> onChanged;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        for (var i = 1; i <= 5; i++)
          IconButton(
            iconSize: 36,
            onPressed: () => onChanged(i),
            icon: Icon(
              i <= value ? Icons.star_rounded : Icons.star_outline_rounded,
              color: AppColors.primary,
            ),
          ),
      ],
    );
  }
}
