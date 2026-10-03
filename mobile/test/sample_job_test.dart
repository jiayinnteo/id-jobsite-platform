import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:id_jobsite/features/demo/sample_job_screen.dart';
import 'package:id_jobsite/theme/app_theme.dart';

Widget _wrap(Widget child) =>
    MaterialApp(theme: AppTheme.light, home: Scaffold(body: child));

void main() {
  testWidgets('Client sample job shows Accept/Reject and review action',
      (tester) async {
    await tester.pumpWidget(_wrap(const SampleJobScreen(mode: 'client')));
    await tester.pumpAndSettle();

    expect(find.text('Accept'), findsOneWidget);
    expect(find.text('Reject'), findsOneWidget);
    expect(find.text('Leave a review'), findsOneWidget);
  });

  testWidgets('Accepting a rectification updates the status chip',
      (tester) async {
    await tester.pumpWidget(_wrap(const SampleJobScreen(mode: 'client')));
    await tester.pumpAndSettle();

    expect(find.text('RECTIFIED'), findsOneWidget);
    await tester.tap(find.text('Accept'));
    await tester.pumpAndSettle();
    expect(find.text('ACCEPTED'), findsOneWidget);
  });

  testWidgets('Boss sample job shows the Review this job action',
      (tester) async {
    await tester.pumpWidget(_wrap(const SampleJobScreen(mode: 'boss')));
    await tester.pumpAndSettle();

    expect(find.text('Review this job'), findsOneWidget);
    expect(find.text('Accept'), findsNothing); // boss has no accept/reject
  });
}
