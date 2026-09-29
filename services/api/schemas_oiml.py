"""
Pydantic Schemas for OIML R 76 NAWI Type Evaluation & Model Approval
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class NAWIAttachmentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    attachment_type: str
    title: str
    file_path: str
    file_name: str
    mime_type: str
    file_size_bytes: int
    uploaded_at: datetime


class NAWIModelBase(BaseModel):
    applicant_type: str = "Manufacturer"
    manufacturer_name: str
    manufacturer_address: str
    country_of_origin: str = "India"
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    license_number: Optional[str] = None

    instrument_type: str # e.g. "Electronic Retail Scale"
    model_name: str
    serial_number: Optional[str] = None
    year_of_manufacture: int = 2026
    accuracy_class: str = "Class III" # Class I, Class II, Class III, Class IIII
    max_capacity: float
    min_capacity: float
    verification_scale_interval_e: float
    scale_interval_d: float
    units: str = "kg"
    tare_type: str = "Subtractive"
    max_tare: Optional[float] = None
    temp_range_min: float = -10.0
    temp_range_max: float = 40.0
    power_supply: str = "230V AC (+10% / -15%), 50Hz"
    load_cell_details: Optional[str] = None
    indicator_details: Optional[str] = None
    software_version: str = "v1.0.0"
    software_checksum: Optional[str] = None

    lab_name: str = "National Legal Metrology Type Evaluation Laboratory"
    lab_accreditation: str = "NABL ISO/IEC 17025 Accredited & OIML Issuing Authority"
    lab_temperature: float = 23.5
    lab_humidity: float = 52.0
    lab_pressure: float = 1013.2
    local_gravity_g: float = 9.7803
    standard_weights_used: str = "Class M1 & F2 Working Standards (Traceable to NPL India)"

    testing_officer_name: str = "Er. Rajesh Sharma (Senior Metrological Officer)"
    approving_officer_name: str = "Dr. Priya V. Iyer (Director of Legal Metrology)"

    test_data: Dict[str, Any] = Field(default_factory=dict)
    remarks: Optional[str] = None
    conditions_of_approval: Optional[str] = None


class NAWIModelCreate(NAWIModelBase):
    application_number: Optional[str] = None
    report_number: Optional[str] = None


class NAWIModelUpdate(BaseModel):
    status: Optional[str] = None
    manufacturer_name: Optional[str] = None
    manufacturer_address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    instrument_type: Optional[str] = None
    model_name: Optional[str] = None
    serial_number: Optional[str] = None
    accuracy_class: Optional[str] = None
    max_capacity: Optional[float] = None
    min_capacity: Optional[float] = None
    verification_scale_interval_e: Optional[float] = None
    scale_interval_d: Optional[float] = None
    units: Optional[str] = None
    tare_type: Optional[str] = None
    max_tare: Optional[float] = None
    temp_range_min: Optional[float] = None
    temp_range_max: Optional[float] = None
    power_supply: Optional[str] = None
    load_cell_details: Optional[str] = None
    indicator_details: Optional[str] = None
    software_version: Optional[str] = None
    software_checksum: Optional[str] = None
    lab_temperature: Optional[float] = None
    lab_humidity: Optional[float] = None
    lab_pressure: Optional[float] = None
    local_gravity_g: Optional[float] = None
    standard_weights_used: Optional[str] = None
    testing_officer_name: Optional[str] = None
    approving_officer_name: Optional[str] = None
    test_data: Optional[Dict[str, Any]] = None
    remarks: Optional[str] = None
    conditions_of_approval: Optional[str] = None


class NAWICalculateRequest(BaseModel):
    accuracy_class: str = "Class III"
    max_capacity: float
    min_capacity: float
    verification_scale_interval_e: float
    scale_interval_d: float
    is_in_service_test: bool = False
    test_data: Dict[str, Any] = Field(default_factory=dict)


class NAWIDigitalSignRequest(BaseModel):
    officer_name: str
    designation: str
    pin_or_token: Optional[str] = None
    signature_remarks: Optional[str] = None


class NAWIModelResponse(NAWIModelBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    application_number: str
    report_number: str
    status: str
    submission_date: datetime
    testing_date: datetime
    approval_date: Optional[datetime] = None
    n_intervals: int
    is_fully_compliant: bool
    evaluation_summary: Dict[str, Any]
    digital_signature: Optional[Dict[str, Any]] = None
    attachments: List[NAWIAttachmentSchema] = []
    created_at: datetime
    updated_at: datetime


class NAWIDashboardStats(BaseModel):
    total_evaluations: int
    approved_compliant: int
    rejected_non_compliant: int
    testing_in_progress: int
    draft_applications: int
    compliance_rate_percent: float
    class_distribution: Dict[str, int]
    instrument_type_distribution: Dict[str, int]
    recent_evaluations: List[Dict[str, Any]]


class WorkflowTransitionRequest(BaseModel):
    action: str # SUBMIT, START_REVIEW, REQUEST_CORRECTION, APPROVE, REJECT, FINALIZE
    notes: Optional[str] = None


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    entity_type: str
    entity_id: str
    user_id: Optional[str] = None
    action: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime


class ReportVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    report_id: str
    version_number: int
    version_label: str
    generated_by: Optional[str] = None
    generated_at: datetime
    file_path: str
    file_format: str
    checksum: Optional[str] = None


class LaboratoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    code: str
    address: str
    accreditation: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    is_active: bool
    created_at: datetime


class ManufacturerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    address: str
    country: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    license_number: Optional[str] = None
    created_at: datetime


class RuleVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    rule_name: str
    rule_version: str
    effective_from: datetime
    effective_to: Optional[datetime] = None
    source_reference: str
    configuration: Dict[str, Any]
    active: bool
    created_at: datetime

