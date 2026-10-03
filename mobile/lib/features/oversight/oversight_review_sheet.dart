import 'package:flutter/material.dart';

import '../../widgets/app_button.dart';

/// Bottom sheet for an ID_BOSS to record an internal oversight review on a job.
/// Returns a (flag, note) record, or null if cancelled.
Future<({String flag, String? note})?> showOversightReviewSheet(
  BuildContext context,
) {
  return showModalBottomSheet<({String flag, String? note})>(
    context: context,
    isScrollControlled: true,
    showDragHandle: true,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
    ),
    builder: (context) => const _OversightForm(),
  );
}

class _OversightForm extends StatefulWidget {
  const _OversightForm();

  @override
  State<_OversightForm> createState() => _OversightFormState();
}

class _OversightFormState extends State<_OversightForm> {
  String _flag = 'APPROVED';
  final _note = TextEditingController();

  @override
  void dispose() {
    _note.dispose();
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
          Text('Review this job',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w800,
                  )),
          const SizedBox(height: 4),
          Text('Internal note — visible to your firm, not to the client.',
              style: Theme.of(context).textTheme.bodyMedium),
          const SizedBox(height: 16),
          SegmentedButton<String>(
            segments: const [
              ButtonSegment(
                value: 'APPROVED',
                label: Text('Approved'),
                icon: Icon(Icons.check_circle_outline),
              ),
              ButtonSegment(
                value: 'NEEDS_ATTENTION',
                label: Text('Needs attention'),
                icon: Icon(Icons.flag_outlined),
              ),
            ],
            selected: {_flag},
            onSelectionChanged: (s) => setState(() => _flag = s.first),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _note,
            maxLines: 4,
            decoration: const InputDecoration(
              hintText: 'Add a note for the assigned designer (optional)',
            ),
          ),
          const SizedBox(height: 20),
          AppButton(
            label: 'Save review',
            icon: Icons.save_outlined,
            onPressed: () => Navigator.of(context).pop(
              (
                flag: _flag,
                note: _note.text.trim().isEmpty ? null : _note.text.trim(),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
