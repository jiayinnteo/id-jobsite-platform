import 'package:flutter/material.dart';

import '../../widgets/app_button.dart';

/// Accept / Reject action bar shown to a client when rectification work is
/// marked RECTIFIED. Reject requires a reason (per Requirement 5).
/// Returns a (accept, reason) record via [onDecision].
class AcceptRejectBar extends StatelessWidget {
  const AcceptRejectBar({super.key, required this.onDecision});

  final void Function({required bool accept, String? reason}) onDecision;

  Future<void> _reject(BuildContext context) async {
    final controller = TextEditingController();
    final reason = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Text('Why are you rejecting this?'),
        content: TextField(
          controller: controller,
          autofocus: true,
          maxLines: 3,
          decoration: const InputDecoration(
            hintText: 'Let the team know what still needs fixing',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          AppButton(
            label: 'Reject',
            kind: AppButtonKind.destructive,
            onPressed: () {
              if (controller.text.trim().isNotEmpty) {
                Navigator.of(context).pop(controller.text.trim());
              }
            },
          ),
        ],
      ),
    );
    if (reason != null && reason.isNotEmpty) {
      onDecision(accept: false, reason: reason);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: AppButton(
            label: 'Reject',
            kind: AppButtonKind.secondary,
            icon: Icons.close_rounded,
            onPressed: () => _reject(context),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: AppButton(
            label: 'Accept',
            icon: Icons.check_rounded,
            onPressed: () => onDecision(accept: true, reason: null),
          ),
        ),
      ],
    );
  }
}
