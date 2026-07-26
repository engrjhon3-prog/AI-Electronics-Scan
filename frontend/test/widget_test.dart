import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:electronics_scanner/main.dart';
import 'package:electronics_scanner/services/ai_identify_service.dart';
import 'package:electronics_scanner/state/app_state.dart';

/// The real service asks the backend whether AI identification is switched on.
/// Tests run with no server, so answer "offline" without touching the network.
class _OfflineAi extends AiIdentifyService {
  @override
  Future<AiStatus> status() async => AiStatus.offline;

  @override
  Future<AiIdentification> identify({
    required File image,
    String ocrText = '',
    String hint = '',
    String idToken = '',
    String premiumToken = '',
  }) async =>
      throw AiException('offline');
}

void main() {
  testWidgets('App boots and shows the scan screen',
      (WidgetTester tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(
      ElectronicsScannerApp(state: AppState(ai: _OfflineAi())..init()),
    );
    await tester.pump();

    expect(find.text('Identify a component'), findsOneWidget);
    expect(find.text('Scan with camera'), findsOneWidget);
  });
}
