import 'package:flutter/material.dart';

import '../../widgets/app_button.dart';

/// Bottom sheet for a contractor to pick a date + time for a site visit.
/// Returns (date, time) where date is YYYY-MM-DD and time is HH:MM:SS or null.
Future<({String date, String? time})?> showScheduleVisitSheet(
  BuildContext context,
) {
  return showModalBottomSheet<({String date, String? time})>(
    context: context,
    isScrollControlled: true,
    showDragHandle: true,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
    ),
    builder: (context) => const _ScheduleForm(),
  );
}

class _ScheduleForm extends StatefulWidget {
  const _ScheduleForm();

  @override
  State<_ScheduleForm> createState() => _ScheduleFormState();
}

class _ScheduleFormState extends State<_ScheduleForm> {
  DateTime? _date;
  TimeOfDay? _time;

  String _fmtDate(DateTime d) =>
      '${d.year.toString().padLeft(4, '0')}-'
      '${d.month.toString().padLeft(2, '0')}-'
      '${d.day.toString().padLeft(2, '0')}';

  String _fmtTime(TimeOfDay t) =>
      '${t.hour.toString().padLeft(2, '0')}:${t.minute.toString().padLeft(2, '0')}:00';

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Schedule a site visit',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w800,
                  )),
          const SizedBox(height: 12),
          ListTile(
            contentPadding: EdgeInsets.zero,
            leading: const Icon(Icons.event_outlined),
            title: Text(_date == null ? 'Pick a date' : _fmtDate(_date!)),
            trailing: const Icon(Icons.chevron_right),
            onTap: () async {
              final now = DateTime.now();
              final picked = await showDatePicker(
                context: context,
                firstDate: now,
                lastDate: now.add(const Duration(days: 365)),
                initialDate: now,
              );
              if (picked != null) setState(() => _date = picked);
            },
          ),
          ListTile(
            contentPadding: EdgeInsets.zero,
            leading: const Icon(Icons.schedule_outlined),
            title: Text(_time == null
                ? 'Pick a time (optional)'
                : _time!.format(context)),
            trailing: const Icon(Icons.chevron_right),
            onTap: () async {
              final picked = await showTimePicker(
                context: context,
                initialTime: TimeOfDay.now(),
              );
              if (picked != null) setState(() => _time = picked);
            },
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Icon(Icons.event_available_outlined,
                  size: 16, color: scheme.tertiary),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  'This visit is added to everyone’s Google Calendar automatically.',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          AppButton(
            label: 'Confirm schedule',
            icon: Icons.check_rounded,
            onPressed: _date == null
                ? null
                : () => Navigator.of(context).pop(
                      (
                        date: _fmtDate(_date!),
                        time: _time == null ? null : _fmtTime(_time!),
                      ),
                    ),
          ),
        ],
      ),
    );
  }
}
