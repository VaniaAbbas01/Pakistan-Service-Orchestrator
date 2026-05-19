import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const PakistanServiceApp());
}

class PakistanServiceApp extends StatelessWidget {
  const PakistanServiceApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Pakistan Service Orchestrator',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF006600), // Pakistan Green
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        appBarTheme: const AppBarTheme(
          centerTitle: true,
          elevation: 2,
        ),
      ),
      home: const HomeScreen(),
    );
  }
}
