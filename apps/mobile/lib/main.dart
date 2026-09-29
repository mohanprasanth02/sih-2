// LabelGuard AI - Field Inspector Mobile Application Entry Point
import 'package:flutter/material.dart';
import 'screens/home_screen.dart';
import 'screens/create_inspection_screen.dart';
import 'screens/camera_scan_screen.dart';
import 'screens/inspection_result_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const LabelGuardMobileApp());
}

class LabelGuardMobileApp extends StatelessWidget {
  const LabelGuardMobileApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LabelGuard AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: const Color(0xFF06B6D4),
        scaffoldBackgroundColor: const Color(0xFF0F172A),
        fontFamily: 'Inter',
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF06B6D4),
          secondary: Color(0xFF10B981),
          surface: Color(0xFF1E293B),
        ),
      ),
      initialRoute: '/',
      onGenerateRoute: (settings) {
        if (settings.name == '/scan') {
          final args = settings.arguments as Map<String, dynamic>? ?? {};
          return MaterialPageRoute(
            builder: (context) => CameraScanScreen(
              inspectionId: args['inspection_id'] ?? 'LG-2026-09-000001',
              productName: args['product_name'] ?? 'Sample Commodity',
              categoryCode: args['category_code'] ?? 'food',
            ),
          );
        }
        return null;
      },
      routes: {
        '/': (context) => const HomeScreen(),
        '/new_inspection': (context) => const CreateInspectionScreen(),
        '/results': (context) => const InspectionResultScreen(),
      },
    );
  }
}
