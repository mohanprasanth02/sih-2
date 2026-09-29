export type UserRole = 'inspector' | 'supervisor' | 'admin' | 'viewer';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  organization: string;
}

export type InspectionStatus =
  | 'PENDING'
  | 'PROCESSING'
  | 'NEEDS_REVIEW'
  | 'COMPLIANT'
  | 'NON_COMPLIANT'
  | 'RESCAN_REQUESTED';

export interface InspectionImage {
  id: string;
  surface_type: string;
  file_path: string;
  url: string;
  blur_score: number;
  brightness_score: number;
  quality_status: 'SUFFICIENT' | 'INSUFFICIENT' | 'WARNING';
  quality_notes?: string;
  width: number;
  height: number;
}

export interface ExtractedField {
  id: string;
  field_name: string;
  detected_value: string | null;
  corrected_value: string | null;
  effective_value: string | null;
  confidence: number;
  bbox: [number, number, number, number] | null; // [x1, y1, x2, y2]
  status: 'DETECTED' | 'NOT_DETECTED' | 'LOW_CONFIDENCE';
  is_corrected: boolean;
  correction_reason?: string;
  image_id?: string;
}

export interface RuleResult {
  id?: string;
  rule_code: string;
  title: string;
  legal_reference: string;
  severity: 'CRITICAL' | 'MAJOR' | 'MINOR';
  status: 'PASS' | 'FAIL' | 'WARNING' | 'MANUAL_REVIEW' | 'NOT_APPLICABLE';
  reason: string;
  confidence: number;
  evidence_crops?: {
    bbox: [number, number, number, number];
    label: string;
  }[];
}

export interface ConflictItem {
  id?: string;
  field_name: string;
  surface_a: string;
  value_a: string;
  surface_b: string;
  value_b: string;
  reason: string;
}

export interface AuditLogItem {
  id: string;
  action: string;
  timestamp: string;
  old_state: any;
  new_state: any;
}

export interface InspectionDetail {
  id: string;
  product_name: string;
  brand?: string;
  category_code: string;
  status: InspectionStatus;
  latitude?: number;
  longitude?: number;
  address?: string;
  is_demo: boolean;
  supervisor_notes?: string;
  created_at: string;
  images: InspectionImage[];
  extracted_fields: ExtractedField[];
  rule_results: RuleResult[];
  conflicts: ConflictItem[];
  audit_logs: AuditLogItem[];
}

export interface InspectionListItem {
  id: string;
  product_name: string;
  brand?: string;
  category_code: string;
  status: InspectionStatus;
  created_at: string;
  address?: string;
  is_demo: boolean;
  image_count: number;
  findings_count: number;
  conflicts_count: number;
}

export interface OverviewKPI {
  total_inspections: number;
  compliant: number;
  potential_violations: number;
  manual_reviews: number;
  compliance_rate: number;
}

export interface ComplianceRuleItem {
  id: string;
  code: string;
  title: string;
  legal_reference: string;
  applicable_categories: string[];
  severity: string;
  version: string;
  description: string;
}

// ==========================================
// OIML R 76 Non-Automatic Weighing Instruments Types
// ==========================================

export type AccuracyClassType = 'Class I' | 'Class II' | 'Class III' | 'Class IIII';

export type NAWIEvaluationStatus =
  | 'DRAFT'
  | 'SUBMITTED'
  | 'UNDER_REVIEW'
  | 'CORRECTION_REQUIRED'
  | 'APPROVED_COMPLIANT'
  | 'FINALIZED'
  | 'REJECTED_NON_COMPLIANT'
  | 'TESTING_IN_PROGRESS';

export interface OIMLAuditLog {
  id: string;
  entity_type: string;
  entity_id: string;
  user_id?: string | null;
  action: string;
  old_value?: string | null;
  new_value?: string | null;
  ip_address?: string | null;
  timestamp: string;
}

export interface OIMLReportVersion {
  id: string;
  report_id: string;
  version?: number;
  version_number?: number;
  version_label?: string;
  generated_by?: string | null;
  generated_at: string;
  file_path?: string;
  file_location?: string | null;
  file_format?: string;
  checksum?: string | null;
}

export interface OIMLLaboratory {
  id: string;
  name: string;
  code: string;
  address: string;
  accreditation?: string;
  contact_email?: string;
  contact_phone?: string;
  is_active: boolean;
  created_at: string;
}

export interface OIMLManufacturer {
  id: string;
  name: string;
  address: string;
  country: string;
  contact_email?: string;
  contact_phone?: string;
  license_number?: string;
  created_at: string;
}

export interface OIMLRuleVersion {
  id: string;
  rule_name: string;
  rule_version: string;
  effective_from: string;
  effective_to?: string | null;
  source_reference: string;
  configuration: Record<string, any>;
  active: boolean;
  created_at: string;
}

export interface NAWIAttachment {
  id: string;
  attachment_type: string;
  title: string;
  file_path: string;
  file_name: string;
  mime_type: string;
  file_size_bytes: number;
  uploaded_at: string;
}

export interface WeighingReading {
  index?: number;
  direction: 'INCR' | 'DECR';
  load: number;
  indication: number;
  delta_l?: number | null;
  raw_error?: number;
  corrected_error?: number;
  corrected_error_e?: number;
  mpe_e?: number;
  mpe_unit?: number;
  hysteresis?: number;
  hysteresis_status?: 'PASS' | 'FAIL';
  status?: 'PASS' | 'FAIL';
}

export interface RepeatabilityLoadSeries {
  load: number;
  readings: number[];
  readings_count?: number;
  min_indication?: number;
  max_indication?: number;
  max_difference?: number;
  mpe_unit?: number;
  mpe_e?: number;
  status?: 'PASS' | 'FAIL';
}

export interface EccentricityPosition {
  position: string;
  indication: number;
  delta_l?: number | null;
  raw_error?: number;
  corrected_error?: number;
  corrected_error_e?: number;
  mpe_unit?: number;
  mpe_e?: number;
  status?: 'PASS' | 'FAIL';
}

export interface NAWIModelEvaluation {
  id: string;
  application_number: string;
  report_number: string;
  status: NAWIEvaluationStatus;
  submission_date: string;
  testing_date: string;
  approval_date?: string | null;

  applicant_type: string;
  manufacturer_name: string;
  manufacturer_address: string;
  country_of_origin: string;
  contact_email?: string;
  contact_phone?: string;
  license_number?: string;

  instrument_type: string;
  model_name: string;
  serial_number?: string;
  year_of_manufacture: number;
  accuracy_class: AccuracyClassType;
  max_capacity: number;
  min_capacity: number;
  verification_scale_interval_e: number;
  scale_interval_d: number;
  units: string;
  n_intervals: number;
  tare_type: string;
  max_tare?: number;
  temp_range_min: number;
  temp_range_max: number;
  power_supply: string;
  load_cell_details?: string;
  indicator_details?: string;
  software_version: string;
  software_checksum?: string;

  lab_name: string;
  lab_accreditation: string;
  lab_temperature: number;
  lab_humidity: number;
  lab_pressure: number;
  local_gravity_g: number;
  standard_weights_used: string;

  testing_officer_name: string;
  approving_officer_name: string;

  test_data: {
    weighing_test?: WeighingReading[];
    repeatability_test?: RepeatabilityLoadSeries[];
    eccentricity_test?: {
      test_load: number;
      positions: EccentricityPosition[];
    };
    tare_zero_test?: Record<string, any>;
    discrimination_test?: any[];
    environmental_voltage_test?: Record<string, any>;
  };

  evaluation_summary: {
    accuracy_class?: string;
    n_intervals?: number;
    n_validation?: { is_valid: boolean; message: string };
    tests_evaluated_count?: number;
    tests_passed_count?: number;
    tests_failed_count?: number;
    is_fully_compliant?: boolean;
    final_verdict?: string;
    test_summaries?: Record<string, any>;
    max_error_ratio?: number;
  };

  is_fully_compliant: boolean;
  remarks?: string;
  conditions_of_approval?: string;
  digital_signature?: {
    signed_by: string;
    designation: string;
    timestamp: string;
    sha256_hash: string;
    signature_token: string;
    status: string;
  } | null;

  attachments: NAWIAttachment[];
  created_at: string;
  updated_at: string;
}

export interface NAWIDashboardStats {
  total_evaluations: number;
  approved_compliant: number;
  rejected_non_compliant: number;
  testing_in_progress: number;
  draft_applications: number;
  compliance_rate_percent: number;
  class_distribution: Record<string, number>;
  instrument_type_distribution: Record<string, number>;
  recent_evaluations: Array<{
    id: string;
    report_number: string;
    manufacturer_name: string;
    model_name: string;
    accuracy_class: string;
    max_capacity: number;
    units: string;
    status: string;
    is_fully_compliant: boolean;
    testing_date: string;
  }>;
}

