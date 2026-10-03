import 'package:flutter/material.dart';

import '../../widgets/app_button.dart';
import '../../widgets/review_tag.dart';
import '../../widgets/status_chip.dart';
import '../defects/accept_reject_bar.dart';
import '../oversight/oversight_review_sheet.dart';
import '../reviews/leave_review_sheet.dart';

/// A self-contained preview screen that exercises the new Phase 2 & 3 UI
/// (boss oversight review, client review, accept/reject) with sample data,
/// until auth + live data wiring lands. [mode] selects which actions show.
class SampleJobScreen extends StatefulWidget {
  const SampleJobScreen({super.key, required this.mode});

  /// 'client' | 'boss'
  final String mode;

  @override
  State<SampleJobScreen> createState() => _SampleJobScreenState();
}

class _SampleJobScreenState extends State<SampleJobScreen> {
  String _defectStatus = 'RECTIFIED';
  double? _reviewRating;
  String? _oversightFlag;

  void _snack(String msg) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(msg)));
  }

  @override
  Widget build(BuildContext context) {
    final isBoss = widget.mode == 'boss';
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Marina Bay Condo',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w800,
                            )),
                    if (_reviewRating != null) ReviewTag(rating: _reviewRating!),
                  ],
                ),
                const SizedBox(height: 4),
                Text('12 Marina Blvd, Singapore',
                    style: Theme.of(context).textTheme.bodyMedium),
                if (_oversightFlag != null) ...[
                  const SizedBox(height: 10),
                  Row(children: [
                    Icon(
                      _oversightFlag == 'APPROVED'
                          ? Icons.check_circle
                          : Icons.flag,
                      size: 18,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(width: 6),
                    Text('Boss review: ${_oversightFlag!.replaceAll('_', ' ')}'),
                  ]),
                ],
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),

        // Defect card with accept/reject for clients.
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Scratched kitchen countertop'),
                    StatusChip(status: _defectStatus),
                  ],
                ),
                const SizedBox(height: 12),
                if (!isBoss && _defectStatus == 'RECTIFIED')
                  AcceptRejectBar(
                    onDecision: ({required accept, reason}) {
                      setState(() => _defectStatus =
                          accept ? 'ACCEPTED' : 'REJECTED');
                      _snack(accept
                          ? 'Accepted — your designer has been notified.'
                          : 'Rejected — the team will take another look.');
                    },
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),

        if (isBoss)
          AppButton(
            label: 'Review this job',
            icon: Icons.rate_review_outlined,
            onPressed: () async {
              final result = await showOversightReviewSheet(context);
              if (result != null) {
                setState(() => _oversightFlag = result.flag);
                _snack('Oversight review saved — designer notified.');
              }
            },
          )
        else
          AppButton(
            label: 'Leave a review',
            icon: Icons.star_outline_rounded,
            onPressed: () async {
              final result = await showLeaveReviewSheet(context);
              if (result != null) {
                setState(() => _reviewRating = result.rating.toDouble());
                _snack('Thanks for your ${result.rating}★ review!');
              }
            },
          ),
      ],
    );
  }
}
