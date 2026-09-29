// LabelGuard AI - Mobile API Service
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../models/inspection.dart';

class ApiService {
  static const String baseUrl = 'http://10.0.2.2:8000/api/v1'; // standard Android emulator host
  static const String wsUrl = 'ws://10.0.2.2:8000/ws/inspections';

  final Dio _dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: const Duration(seconds: 15),
    receiveTimeout: const Duration(seconds: 30),
  ));
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  ApiService() {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _storage.read(key: 'jwt_token');
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
    ));
  }

  Future<bool> login(String email, String password) async {
    try {
      final response = await _dio.post('/auth/login', data: {
        'email': email,
        'password': password,
      });
      if (response.statusCode == 200) {
        final token = response.data['access_token'];
        await _storage.write(key: 'jwt_token', value: token);
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  Future<String?> createInspection({
    required String productName,
    String? brand,
    required String categoryCode,
    double? latitude,
    double? longitude,
    String? address,
  }) async {
    try {
      final response = await _dio.post('/inspections', data: {
        'product_name': productName,
        'brand': brand,
        'category_code': categoryCode,
        'latitude': latitude,
        'longitude': longitude,
        'address': address,
      });
      if (response.statusCode == 200) {
        return response.data['id'];
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  Future<bool> uploadSurfaceImage({
    required String inspectionId,
    required String surfaceType,
    required String filePath,
  }) async {
    try {
      final formData = FormData.fromMap({
        'surface_type': surfaceType,
        'file': await MultipartFile.fromFile(filePath, filename: '$surfaceType.jpg'),
      });
      final response = await _dio.post('/inspections/$inspectionId/images', data: formData);
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  Future<Map<String, dynamic>?> triggerAnalysis(String inspectionId) async {
    try {
      final response = await _dio.post('/inspections/$inspectionId/analyze');
      if (response.statusCode == 200) {
        return response.data;
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  Future<Map<String, dynamic>?> getInspectionDetails(String inspectionId) async {
    try {
      final response = await _dio.get('/inspections/$inspectionId');
      if (response.statusCode == 200) {
        return response.data;
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  WebSocketChannel connectInspectionStream(String inspectionId) {
    return WebSocketChannel.connect(Uri.parse('$wsUrl/$inspectionId'));
  }
}
