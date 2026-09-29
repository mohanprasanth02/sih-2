// LabelGuard AI - Shared Type Definitions (SIH26034)

export type UserRole = 'inspector' | 'supervisor' | 'admin';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  organization: string;
  is_active: boolean;
  created_at: string;
}

export type InspectionStatus =
  | 'PENDING'
  | 'PROCESSING'
  | 'NEEDS_REVIEW'
  | 'COMPLIANT'
  | 'NON_COMPLIANT'
  | 'RESCAN_REQUESTED';

export type SurfaceType = 'front' | 'back' | 'side_a' | 'side_b' | 'top' | 'bottom';

export interface InspectionImage {
  id: string;
  inspection_id: string;
  surface_type: SurfaceType;
  file_path: string;
  url: string;
  blur_score: number;
  brightness_score: number;
  quality_status: 'SUFFICIENT' | 'INSUFFICIENT' | 'WARNING';
  quality_notes?: string;
  width: number;
  height: number;
  created_at: string;
}

export interface ExtractedField {
  id: string;
  inspection_id: string;
  image_id: string;
  field_name:
    | 'product_name'
    | 'net_quantity'
    | 'mrp'
    | 'unit_sale_price'
    | 'manufacturer_packer'
    | 'country_of_origin'
    | 'mfg_packing_date'
    | 'consumer_care'
    | 'batch_code';
  detected_value: string | null;
  corrected_value: string | null;
  effective_value: string | null;
  confidence: number;
  bbox: [number, number, number, number] | null; // [ymin, xmin, ymax, xmax] or [x1, y1, x2, y2]
  status: 'DETECTED' | 'NOT_DETECTED' | 'LOW_CONFIDENCE';
  is_corrected: boolean;
  corrected_by?: string;
  correction_reason?: string;
  source_image_surface: SurfaceType;
}

export type RuleSeverity = 'CRITICAL' | 'MAJOR' | 'MINOR';

export type RuleStatus =
  | 'PASS'
  | 'FAIL'
  | 'WARNING'
  | 'MANUAL_REVIEW'
  | 'NOT_APPLICABLE';

export interface ComplianceRule {
  id: string;
  code: string;
  title: string;
  legal_reference: string;
  applicable_category: string;
  severity: RuleSeverity;
  version: string;
  description: string;
  is_active: boolean;
}

export interface RuleResult {
  rule_id: string;
  rule_code: string;
  title: string;
  legal_reference: string;
  status: RuleStatus;
  reason: string;
  confidence: number;
  severity: RuleSeverity;
  evidence_crops: {
    image_id: string;
    surface: SurfaceType;
    bbox: [number, number, number, number];
    label: string;
  }[];
}

export interface ConflictItem {
  field_name: string;
  surface_a: SurfaceType;
  value_a: string;
  surface_b: SurfaceType;
  value_b: string;
  reason: string;
}

export interface Inspection {
  id: string; // e.g. LG-2026-09-000128
  inspector_id: string;
  inspector_name: string;
  product_name: string;
  brand?: string;
  category: string;
  status: InspectionStatus;
  created_at: string;
  updated_at: string;
  location?: {
    latitude: number;
    longitude: number;
    address: string;
  };
  summary: {
    total_fields: number;
    detected_fields: number;
    high_confidence_count: number;
    low_confidence_count: number;
    pass_rules_count: number;
    fail_rules_count: number;
    review_rules_count: number;
  };
  conflicts: ConflictItem[];
  images: InspectionImage[];
  extracted_fields: ExtractedField[];
  rule_results: RuleResult[];
  supervisor_notes?: string;
  is_demo: boolean;
}

export interface WebSocketEvent {
  event:
    | 'IMAGE_RECEIVED'
    | 'QUALITY_CHECKED'
    | 'OCR_STARTED'
    | 'OCR_COMPLETED'
    | 'EXTRACTION_STARTED'
    | 'EXTRACTION_COMPLETED'
    | 'RULE_VALIDATION_STARTED'
    | 'RULE_VALIDATION_COMPLETED'
    | 'EVIDENCE_GENERATED'
    | 'ANALYSIS_COMPLETED'
    | 'ANALYSIS_FAILED';
  inspection_id: string;
  message: string;
  timestamp: string;
  payload?: any;
}
