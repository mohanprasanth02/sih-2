// LabelGuard AI - Offline Queue Database
import 'dart:async';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../models/inspection.dart';

class OfflineQueueService {
  static final OfflineQueueService instance = OfflineQueueService._init();
  static Database? _database;

  OfflineQueueService._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB('labelguard_offline.db');
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);

    return await openDatabase(
      path,
      version: 1,
      onCreate: _createDB,
    );
  }

  Future _createDB(Database db, int version) async {
    await db.execute('''
      CREATE TABLE offline_inspections (
        id TEXT PRIMARY KEY,
        product_name TEXT NOT NULL,
        brand TEXT,
        category_code TEXT NOT NULL,
        status TEXT NOT NULL,
        latitude REAL,
        longitude REAL,
        address TEXT,
        created_at TEXT NOT NULL,
        is_synced INTEGER NOT NULL
      )
    ''');

    await db.execute('''
      CREATE TABLE offline_images (
        id TEXT PRIMARY KEY,
        inspection_id TEXT NOT NULL,
        surface_type TEXT NOT NULL,
        local_path TEXT NOT NULL,
        quality_status TEXT NOT NULL,
        blur_score REAL,
        brightness_score REAL
      )
    ''');
  }

  Future<void> saveInspection(MobileInspection inspection, List<MobileImage> images) async {
    final db = await instance.database;
    await db.insert('offline_inspections', inspection.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
    for (final img in images) {
      await db.insert('offline_images', img.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
    }
  }

  Future<List<MobileInspection>> getPendingSyncInspections() async {
    final db = await instance.database;
    final result = await db.query('offline_inspections', where: 'is_synced = ?', whereArgs: [0]);
    return result.map((json) => MobileInspection.fromMap(json)).toList();
  }

  Future<List<MobileImage>> getImagesForInspection(String inspectionId) async {
    final db = await instance.database;
    final result = await db.query('offline_images', where: 'inspection_id = ?', whereArgs: [inspectionId]);
    return result.map((json) => MobileImage.fromMap(json)).toList();
  }

  Future<void> markInspectionSynced(String inspectionId) async {
    final db = await instance.database;
    await db.update('offline_inspections', {'is_synced': 1}, where: 'id = ?', whereArgs: [inspectionId]);
  }
}
