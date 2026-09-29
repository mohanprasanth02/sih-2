// LabelGuard AI - Mobile Inspection Data Models

class MobileInspection {
  final String id;
  final String productName;
  final String? brand;
  final String categoryCode;
  final String status;
  final double? latitude;
  final double? longitude;
  final String? address;
  final String createdAt;
  final bool isSynced;
  final List<MobileImage> images;

  MobileInspection({
    required this.id,
    required this.productName,
    this.brand,
    required this.categoryCode,
    required this.status,
    this.latitude,
    this.longitude,
    this.address,
    required this.createdAt,
    this.isSynced = true,
    this.images = const [],
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'product_name': productName,
      'brand': brand,
      'category_code': categoryCode,
      'status': status,
      'latitude': latitude,
      'longitude': longitude,
      'address': address,
      'created_at': createdAt,
      'is_synced': isSynced ? 1 : 0,
    };
  }

  factory MobileInspection.fromMap(Map<String, dynamic> map) {
    return MobileInspection(
      id: map['id'],
      productName: map['product_name'],
      brand: map['brand'],
      categoryCode: map['category_code'],
      status: map['status'] ?? 'PENDING',
      latitude: map['latitude'],
      longitude: map['longitude'],
      address: map['address'],
      createdAt: map['created_at'] ?? '',
      isSynced: (map['is_synced'] ?? 1) == 1,
    );
  }
}

class MobileImage {
  final String id;
  final String inspectionId;
  final String surfaceType;
  final String localPath;
  final String qualityStatus;
  final double blurScore;
  final double brightnessScore;

  MobileImage({
    required this.id,
    required this.inspectionId,
    required this.surfaceType,
    required this.localPath,
    this.qualityStatus = 'SUFFICIENT',
    this.blurScore = 120.0,
    this.brightnessScore = 130.0,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'inspection_id': inspectionId,
      'surface_type': surfaceType,
      'local_path': localPath,
      'quality_status': qualityStatus,
      'blur_score': blurScore,
      'brightness_score': brightnessScore,
    };
  }

  factory MobileImage.fromMap(Map<String, dynamic> map) {
    return MobileImage(
      id: map['id'],
      inspectionId: map['inspection_id'],
      surfaceType: map['surface_type'],
      localPath: map['local_path'],
      qualityStatus: map['quality_status'] ?? 'SUFFICIENT',
      blurScore: map['blur_score']?.toDouble() ?? 0.0,
      brightnessScore: map['brightness_score']?.toDouble() ?? 0.0,
    );
  }
}
