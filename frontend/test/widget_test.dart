import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:electronics_scanner/main.dart';

void main() {
  testWidgets('App boots and shows the scan screen',
      (WidgetTester tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(const ElectronicsScannerApp());
    await tester.pump();

    expect(find.text('Identify a component'), findsOneWidget);
    expect(find.text('Scan with camera'), findsOneWidget);
  });
}
