import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'config.dart';
import 'state/app_state.dart';
import 'theme.dart';
import 'screens/home_shell.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  try {
    // Reads config from android/app/google-services.json. If it's absent
    // (tests, stripped builds) the app still runs — scanning is offline.
    await Firebase.initializeApp();
  } catch (_) {
    // Accounts unavailable; core features work without them.
  }
  runApp(const ElectronicsScannerApp());
}

class ElectronicsScannerApp extends StatelessWidget {
  const ElectronicsScannerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AppState()..init(),
      child: MaterialApp(
        title: AppConfig.appName,
        debugShowCheckedModeBanner: false,
        theme: AppTheme.light(),
        darkTheme: AppTheme.dark(),
        themeMode: ThemeMode.system,
        home: const HomeShell(),
      ),
    );
  }
}
