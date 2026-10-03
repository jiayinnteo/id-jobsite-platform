import 'package:flutter/material.dart';

import '../../widgets/app_button.dart';
import '../../widgets/review_tag.dart';

/// Bottom sheet for a client to leave a star rating + comment on a job.
/// Returns a (rating, comment) record on submit, or null if cancelled.
Future<({int rating, String? comment})?> showLeaveReviewSheet(
  BuildContext context,
) {
  return showModalBottomSheet<({int rating, String? comment})>(
    context: context,
    isScrollControlled: true,
    showDragHandle: true,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
    ),
    builder: (context) => const _LeaveReviewForm(),
  );
}

class _LeaveReviewForm extends StatefulWidget {
  const _LeaveReviewForm();

  @override
  State<_LeaveReviewForm> createState() => _LeaveReviewFormState();
}

class _LeaveReviewFormState extends State<_LeaveReviewForm> {
  int _rating = 5;
  final _comment = TextEditingController();

  @override
  void dispose() {
    _comment.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final bottom = MediaQuery.of(context).viewInsets.bottom;
    return Padding(
      padding: EdgeInsets.fromLTRB(24, 8, 24, 24 + bottom),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('How was your experience?',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w800,
                  )),
          const SizedBox(height: 4),
          Text('Your feedback helps your design team improve.',
              style: Theme.of(context).textTheme.bodyMedium),
          const SizedBox(height: 12),
          Center(
            child: StarRatingInput(
              value: _rating,
              onChanged: (v) => setState(() => _rating = v),
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _comment,
            maxLines: 4,
            decoration: const InputDecoration(
              hintText: 'Share a few words (optional)',
            ),
          ),
          const SizedBox(height: 20),
          AppButton(
            label: 'Submit review',
            icon: Icons.send_rounded,
            onPressed: () => Navigator.of(context).pop(
              (
                rating: _rating,
                comment: _comment.text.trim().isEmpty
                    ? null
                    : _comment.text.trim(),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
