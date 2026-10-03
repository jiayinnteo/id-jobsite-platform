import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:id_jobsite/widgets/colour_swatch.dart';

void main() {
  test('colourFromHex parses #RRGGBB', () {
    expect(colourFromHex('#E07A5F'), const Color(0xFFE07A5F));
    expect(colourFromHex('E07A5F'), const Color(0xFFE07A5F));
  });

  test('colourFromHex returns null for invalid input', () {
    expect(colourFromHex(null), isNull);
    expect(colourFromHex('nope'), isNull);
  });

  testWidgets('ColourSwatch renders a tile', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: ColourSwatch(hex: '#81B29A'))),
    );
    expect(find.byType(ColourSwatch), findsOneWidget);
  });
}
