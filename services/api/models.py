"""
LabelGuard AI - SQLAlchemy Database Models (SIH26034)
Structured Relational Schema for Legal Metrology Inspections, Rules, Evidence, and Audits
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, Float, Integer, Text, DateTime, ForeignKey, Enum, JSON
)
from sqlalchemy.orm import relationship
from services.api.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="inspector") # inspector, supervisor, admin
    organization = Column(String(255), default="Department of Legal Metrology")
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    inspections = relationship("Inspection", back_populates="inspector", foreign_keys="[Inspection.inspector_id]")
    audit_logs = relationship("AuditLog", back_populates="user")

class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(50), unique=True, nullable=False, index=True) # food, cosmetics, household, etc.
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    required_fields = Column(JSON, default=list) # List of required field names
    is_active = Column(Boolean, default=True)

    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, index=True)
    brand = Column(String(255), nullable=True)
    category_code = Column(String(50), ForeignKey("product_categories.code"), nullable=False)
    barcode = Column(String(100), nullable=True, index=True)
    manufacturer_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    category = relationship("ProductCategory", back_populates="products")
    inspections = relationship("Inspection", back_populates="product")

class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(String(50), primary_key=True) # e.g. LG-2026-09-000128
    inspector_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=True)
    product_name = Column(String(255), nullable=False)
    brand = Column(String(255), nullable=True)
    category_code = Column(String(50), nullable=False, default="food")
    status = Column(String(50), default="PENDING", index=True) # PENDING, PROCESSING, NEEDS_REVIEW, COMPLIANT, NON_COMPLIANT, RESCAN_REQUESTED
    
    # Location
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address = Column(String(500), nullable=True)
    
    supervisor_notes = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now, index=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    inspector = relationship("User", foreign_keys=[inspector_id], back_populates="inspections")
    product = relationship("Product", back_populates="inspections")
    images = relationship("InspectionImage", back_populates="inspection", cascade="all, delete-orphan")
    extracted_fields = relationship("ExtractedField", back_populates="inspection", cascade="all, delete-orphan")
    rule_results = relationship("RuleResult", back_populates="inspection", cascade="all, delete-orphan")
    conflicts = relationship("ConflictItem", back_populates="inspection", cascade="all, delete-orphan")
    reports = relationship("InspectionReport", back_populates="inspection", cascade="all, delete-orphan")

class InspectionImage(Base):
    __tablename__ = "inspection_images"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    inspection_id = Column(String(50), ForeignKey("inspections.id"), nullable=False, index=True)
    surface_type = Column(String(50), nullable=False) # front, back, side_a, side_b, top, bottom
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=True)
    blur_score = Column(Float, default=0.0)
    brightness_score = Column(Float, default=0.0)
    quality_status = Column(String(50), default="SUFFICIENT") # SUFFICIENT, INSUFFICIENT, WARNING
    quality_notes = Column(Text, nullable=True)
    width = Column(Integer, default=0)
    height = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)

    inspection = relationship("Inspection", back_populates="images")
    extracted_fields = relationship("ExtractedField", back_populates="source_image")

class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    inspection_id = Column(String(50), ForeignKey("inspections.id"), nullable=False, index=True)
    image_id = Column(String(36), ForeignKey("inspection_images.id"), nullable=True)
    field_name = Column(String(100), nullable=False) # product_name, net_quantity, mrp, etc.
    detected_value = Column(Text, nullable=True)
    corrected_value = Column(Text, nullable=True)
    confidence = Column(Float, default=0.0)
    bbox = Column(JSON, nullable=True) # [x1, y1, x2, y2]
    status = Column(String(50), default="DETECTED") # DETECTED, NOT_DETECTED, LOW_CONFIDENCE
    is_corrected = Column(Boolean, default=False)
    corrected_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    correction_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    inspection = relationship("Inspection", back_populates="extracted_fields")
    source_image = relationship("InspectionImage", back_populates="extracted_fields")

class ComplianceRule(Base):
    __tablename__ = "compliance_rules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(50), unique=True, nullable=False, index=True) # LM-RULE-001
    title = Column(String(255), nullable=False)
    legal_reference = Column(String(100), nullable=False) # Rule 6(1)(a)
    applicable_categories = Column(JSON, default=list)
    severity = Column(String(50), default="CRITICAL") # CRITICAL, MAJOR, MINOR
    version = Column(String(50), default="2011.1")
    description = Column(Text, nullable=False)
    condition_json = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)

class RuleResult(Base):
    __tablename__ = "rule_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    inspection_id = Column(String(50), ForeignKey("inspections.id"), nullable=False, index=True)
    rule_id = Column(String(36), ForeignKey("compliance_rules.id"), nullable=True)
    rule_code = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    legal_reference = Column(String(100), nullable=False)
    severity = Column(String(50), default="CRITICAL")
    status = Column(String(50), nullable=False) # PASS, FAIL, WARNING, MANUAL_REVIEW, NOT_APPLICABLE
    reason = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0)
    evidence_crops = Column(JSON, default=list) # List of image_id, bbox, label
    created_at = Column(DateTime, default=utc_now)

    inspection = relationship("Inspection", back_populates="rule_results")

class ConflictItem(Base):
    __tablename__ = "conflict_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    inspection_id = Column(String(50), ForeignKey("inspections.id"), nullable=False, index=True)
    field_name = Column(String(100), nullable=False)
    surface_a = Column(String(50), nullable=False)
    value_a = Column(String(255), nullable=False)
    surface_b = Column(String(50), nullable=False)
    value_b = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    inspection = relationship("Inspection", back_populates="conflicts")

class InspectionReport(Base):
    __tablename__ = "inspection_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    inspection_id = Column(String(50), ForeignKey("inspections.id"), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    format = Column(String(20), default="PDF")
    generated_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    inspection = relationship("Inspection", back_populates="reports")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    entity_type = Column(String(50), nullable=False, index=True) # inspection, extracted_field, rule
    entity_id = Column(String(100), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False) # CREATED, EDITED_FIELD, APPROVED, RESCAN_REQUESTED
    old_state = Column(JSON, nullable=True)
    new_state = Column(JSON, nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=utc_now, index=True)

    user = relationship("User", back_populates="audit_logs")

class AIModelTelemetry(Base):
    __tablename__ = "ai_model_telemetry"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    model_name = Column(String(100), nullable=False)
    model_type = Column(String(50), nullable=False) # OCR, QUALITY, EXTRACTION
    version = Column(String(50), nullable=False)
    latency_ms = Column(Float, default=0.0)
    status = Column(String(50), default="SUCCESS") # SUCCESS, FAILURE, TIMEOUT
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=utc_now)


class NAWIModelApproval(Base):
    __tablename__ = "nawi_model_approvals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_number = Column(String(100), unique=True, index=True, nullable=False)
    report_number = Column(String(100), unique=True, index=True, nullable=False)
    status = Column(String(50), default="DRAFT", index=True) # DRAFT, TESTING_IN_PROGRESS, UNDER_REVIEW, APPROVED_COMPLIANT, REJECTED_NON_COMPLIANT
    submission_date = Column(DateTime, default=utc_now)
    testing_date = Column(DateTime, default=utc_now)
    approval_date = Column(DateTime, nullable=True)

    # Applicant / Manufacturer Details
    applicant_type = Column(String(50), default="Manufacturer") # Manufacturer, Importer, Dealer
    manufacturer_name = Column(String(255), nullable=False, index=True)
    manufacturer_address = Column(Text, nullable=False)
    country_of_origin = Column(String(100), default="India")
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    license_number = Column(String(100), nullable=True)

    # Instrument Specifications
    instrument_type = Column(String(100), nullable=False) # e.g., Electronic Retail Scale, Platform Scale, Weighbridge
    model_name = Column(String(255), nullable=False, index=True)
    serial_number = Column(String(100), nullable=True)
    year_of_manufacture = Column(Integer, default=2026)
    accuracy_class = Column(String(50), nullable=False, default="Class III") # Class I, Class II, Class III, Class IIII
    max_capacity = Column(Float, nullable=False)
    min_capacity = Column(Float, nullable=False)
    verification_scale_interval_e = Column(Float, nullable=False)
    scale_interval_d = Column(Float, nullable=False)
    units = Column(String(20), default="kg")
    n_intervals = Column(Integer, nullable=False)
    tare_type = Column(String(50), default="Subtractive")
    max_tare = Column(Float, nullable=True)
    temp_range_min = Column(Float, default=-10.0)
    temp_range_max = Column(Float, default=40.0)
    power_supply = Column(String(255), default="230V AC (+10% / -15%), 50Hz / 6V DC Rechargeable Battery")
    load_cell_details = Column(Text, nullable=True)
    indicator_details = Column(Text, nullable=True)
    software_version = Column(String(100), default="v1.0.0")
    software_checksum = Column(String(100), nullable=True)

    # Laboratory and Environmental Conditions
    lab_name = Column(String(255), default="National Legal Metrology Type Evaluation Laboratory")
    lab_accreditation = Column(String(255), default="NABL ISO/IEC 17025 Accredited & OIML Issuing Authority")
    lab_temperature = Column(Float, default=23.5) # deg C
    lab_humidity = Column(Float, default=52.0) # % RH
    lab_pressure = Column(Float, default=1013.2) # hPa
    local_gravity_g = Column(Float, default=9.7803) # m/s^2
    standard_weights_used = Column(String(255), default="Class M1 & F2 Working Standards (Traceable to NPL India)")

    # Testing & Review Personnel
    testing_officer_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    testing_officer_name = Column(String(255), default="Er. Rajesh Sharma (Senior Metrological Officer)")
    approving_officer_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    approving_officer_name = Column(String(255), default="Dr. Priya V. Iyer (Director of Legal Metrology)")

    # Test Observations and Metrological Results
    test_data = Column(JSON, default=dict)
    evaluation_summary = Column(JSON, default=dict)
    is_fully_compliant = Column(Boolean, default=False)
    remarks = Column(Text, nullable=True)
    conditions_of_approval = Column(Text, nullable=True)

    # Digital Signature Block
    digital_signature = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    attachments = relationship("NAWIAttachment", back_populates="evaluation", cascade="all, delete-orphan")


class NAWIAttachment(Base):
    __tablename__ = "nawi_attachments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    evaluation_id = Column(String(36), ForeignKey("nawi_model_approvals.id"), nullable=False, index=True)
    attachment_type = Column(String(50), nullable=False) # INSTRUMENT_PHOTO, NAMEPLATE, LOAD_CELL, SEALING, SCHEMATIC, CALIBRATION_CERT
    title = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    mime_type = Column(String(100), default="image/jpeg")
    file_size_bytes = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=utc_now)

    evaluation = relationship("NAWIModelApproval", back_populates="attachments")


# ============================================================================
# NORMALIZED RELATIONAL SCHEMA FOR OIML R 76 NAWI LABORATORY MANAGEMENT
# ============================================================================

class Laboratory(Base):
    __tablename__ = "laboratories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False)
    address = Column(Text, nullable=False)
    accreditation = Column(String(255), default="NABL ISO/IEC 17025 Accredited & OIML Issuing Authority")
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    reports = relationship("TestReport", back_populates="laboratory")


class Manufacturer(Base):
    __tablename__ = "manufacturers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, index=True)
    address = Column(Text, nullable=False)
    country = Column(String(100), default="India")
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    license_number = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, default=utc_now)

    instruments = relationship("Instrument", back_populates="manufacturer")


class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    manufacturer_id = Column(String(36), ForeignKey("manufacturers.id"), nullable=True, index=True)
    model_name = Column(String(255), nullable=False, index=True)
    serial_number = Column(String(100), nullable=False, index=True)
    instrument_type = Column(String(100), nullable=False) # e.g. Electronic Retail Scale, Platform Scale
    accuracy_class = Column(String(50), nullable=False, default="Class III") # Class I, Class II, Class III, Class IIII
    max_capacity = Column(Float, nullable=False)
    min_capacity = Column(Float, nullable=False)
    verification_scale_interval_e = Column(Float, nullable=False)
    scale_interval_d = Column(Float, nullable=False)
    units = Column(String(20), default="kg")
    n_intervals = Column(Integer, nullable=False)
    tare_type = Column(String(50), default="Subtractive")
    max_tare = Column(Float, nullable=True)
    temp_range_min = Column(Float, default=-10.0)
    temp_range_max = Column(Float, default=40.0)
    power_supply = Column(String(255), default="230V AC (+10% / -15%), 50Hz / 6V DC Rechargeable Battery")
    load_cell_details = Column(Text, nullable=True)
    indicator_details = Column(Text, nullable=True)
    software_version = Column(String(100), default="v1.0.0")
    software_checksum = Column(String(100), nullable=True)
    technical_specifications = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    manufacturer = relationship("Manufacturer", back_populates="instruments")
    reports = relationship("TestReport", back_populates="instrument")


class RuleVersion(Base):
    __tablename__ = "rule_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    rule_name = Column(String(255), nullable=False, index=True) # OIML R 76-1:2006, Legal Metrology Rules 2011
    rule_version = Column(String(50), nullable=False, index=True) # 2006.1, 2011.1
    effective_from = Column(DateTime, default=utc_now)
    effective_to = Column(DateTime, nullable=True)
    source_reference = Column(String(255), nullable=False) # OIML R 76-1 Edition 2006 (E) / Gazette of India
    configuration = Column(JSON, default=dict) # MPE thresholds, class limits, formula configs
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)


class TestReport(Base):
    __tablename__ = "test_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_number = Column(String(100), unique=True, index=True, nullable=False)
    application_number = Column(String(100), unique=True, index=True, nullable=False)
    instrument_id = Column(String(36), ForeignKey("instruments.id"), nullable=True, index=True)
    laboratory_id = Column(String(36), ForeignKey("laboratories.id"), nullable=True, index=True)
    rule_version_id = Column(String(36), ForeignKey("rule_versions.id"), nullable=True, index=True)
    status = Column(String(50), default="DRAFT", index=True) # DRAFT, SUBMITTED, UNDER_REVIEW, CORRECTION_REQUIRED, APPROVED, FINALIZED, REJECTED_NON_COMPLIANT
    overall_result = Column(String(50), default="PENDING") # PASS, FAIL, PENDING
    evaluator_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    reviewer_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    submission_date = Column(DateTime, default=utc_now)
    testing_date = Column(DateTime, default=utc_now)
    approval_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Environmental Conditions
    lab_temperature = Column(Float, default=23.0)
    lab_humidity = Column(Float, default=50.0)
    lab_pressure = Column(Float, default=1013.25)
    local_gravity_g = Column(Float, default=9.7803)
    standard_weights_used = Column(String(255), default="Class M1 & F2 Working Standards (Traceable to NPL India)")

    remarks = Column(Text, nullable=True)
    conditions_of_approval = Column(Text, nullable=True)
    digital_signature = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=utc_now, index=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    instrument = relationship("Instrument", back_populates="reports")
    laboratory = relationship("Laboratory", back_populates="reports")
    evaluator = relationship("User", foreign_keys=[evaluator_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    rule_version = relationship("RuleVersion")
    sessions = relationship("TestSession", back_populates="report", cascade="all, delete-orphan")
    observations = relationship("TestObservation", back_populates="report", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="report", cascade="all, delete-orphan")
    versions = relationship("ReportVersion", back_populates="report", cascade="all, delete-orphan")


class TestSession(Base):
    __tablename__ = "test_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_id = Column(String(36), ForeignKey("test_reports.id"), nullable=False, index=True)
    test_type = Column(String(100), nullable=False, index=True) # WEIGHING, REPEATABILITY, ECCENTRICITY, TARE_ZERO, DISCRIMINATION, TEMPERATURE, VOLTAGE
    started_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="COMPLETED") # IN_PROGRESS, COMPLETED, FAILED
    notes = Column(Text, nullable=True)

    report = relationship("TestReport", back_populates="sessions")
    observations = relationship("TestObservation", back_populates="session", cascade="all, delete-orphan")


class TestObservation(Base):
    __tablename__ = "test_observations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_id = Column(String(36), ForeignKey("test_reports.id"), nullable=False, index=True)
    session_id = Column(String(36), ForeignKey("test_sessions.id"), nullable=True, index=True)
    test_type = Column(String(100), nullable=False, index=True)
    test_step = Column(Integer, default=1)
    direction = Column(String(20), default="INCR") # INCR, DECR
    applied_load = Column(Float, nullable=False)
    indication = Column(Float, nullable=False)
    delta_l = Column(Float, nullable=True)
    raw_error = Column(Float, nullable=True)
    zero_error = Column(Float, nullable=True)
    corrected_error = Column(Float, nullable=True)
    permissible_error = Column(Float, nullable=True)
    result = Column(String(20), default="PASS") # PASS, FAIL, WARNING
    notes = Column(Text, nullable=True)
    observation_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)

    report = relationship("TestReport", back_populates="observations")
    session = relationship("TestSession", back_populates="observations")


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_id = Column(String(36), ForeignKey("test_reports.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False) # INSTRUMENT_PHOTO, NAMEPLATE, LOAD_CELL, SEALING, SCHEMATIC, CALIBRATION_CERT
    storage_key = Column(String(500), nullable=False)
    file_path = Column(String(500), nullable=False)
    mime_type = Column(String(100), default="image/jpeg")
    file_size_bytes = Column(Integer, default=0)
    uploaded_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    report = relationship("TestReport", back_populates="attachments")
    uploader = relationship("User")


class ReportVersion(Base):
    __tablename__ = "report_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_id = Column(String(36), ForeignKey("test_reports.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False, default=1) # 1, 2, 3...
    version_label = Column(String(50), default="Draft") # Draft, Submitted, Under Review, Corrected, Final
    generated_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    generated_at = Column(DateTime, default=utc_now)
    file_path = Column(String(500), nullable=False)
    file_format = Column(String(20), default="PDF") # PDF, DOCX
    checksum = Column(String(64), nullable=True) # SHA-256

    report = relationship("TestReport", back_populates="versions")


