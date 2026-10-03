import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:id_jobsite/features/schedule/schedule_visit_sheet.dart';
import 'package:id_jobsite/theme/app_theme.dart';
import 'package:id_jobsite/widgets/review_tag.dart';

Widget _wrap(Widget child) => ProviderScope(
      child: MaterialApp(theme: AppTheme.light, home: Scaffold(body: child)),
    );

void main() {
  testWidgets('ReviewTag shows the rating', (tester) async {
    await tester.pumpWidget(_wrap(const ReviewTag(rating: 4.5)));
    await tester.pumpAndSettle();
    expect(find.text('Reviewed'), findsOneWidget);
    expect(find.text('4.5'), findsOneWidget);
  });

  testWidgets('StarRatingInput reports taps', (tester) async {
    int picked = 0;
    await tester.pumpWidget(_wrap(
      StarRatingInput(value: 3, onChanged: (v) => picked = v),
    ));
    await tester.pumpAndSettle();
    // 5 star buttons rendered.
    expect(find.byType(IconButton), findsNWidgets(5));
    await tester.tap(find.byType(IconButton).last);
    expect(picked, 5);
  });

  testWidgets('Schedule sheet mentions Google Calendar auto-link',
      (tester) async {
    await tester.pumpWidget(_wrap(
      Builder(
        builder: (context) => ElevatedButton(
          onPressed: () => showScheduleVisitSheet(context),
          child: const Text('open'),
        ),
      ),
    ));
    await tester.tap(find.text('open'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Google Calendar'), findsOneWidget);
    expect(find.text('Schedule a site visit'), findsOneWidget);
  });
}
