"""
OIML R 76 Non-Automatic Weighing Instruments (NAWI) Model Approval Router
API Endpoints for Type Evaluation, Digital Observation Entry, Compliance Verification,
Digital Signatures, Standardized PDF & MS Word Report Generation.
"""

import os
import uuid
import hashlib
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from services.api.database import get_db
from services.api.models import (
    User, NAWIModelApproval, NAWIAttachment,
    Laboratory, Manufacturer, Instrument, TestReport, TestSession,
    TestObservation, Attachment, ReportVersion, RuleVersion, AuditLog
)
from services.api.schemas_oiml import (
    NAWIModelCreate, NAWIModelUpdate, NAWIModelResponse,
    NAWICalculateRequest, NAWIDigitalSignRequest, NAWIDashboardStats,
    WorkflowTransitionRequest, AuditLogResponse, ReportVersionResponse,
    LaboratoryResponse, ManufacturerResponse, RuleVersionResponse
)
from services.api.routers.auth import (
    get_current_user, get_optional_user, require_roles,
    require_inspector, require_supervisor, require_admin
)
from rules.oiml_r76 import (
    evaluate_complete_oiml_r76_evaluation,
    calculate_verification_scale_intervals,
    normalize_class,
    get_mpe_in_e
)
from rules.oiml_r76.standards import get_active_standard, list_standards
from reports.oiml_pdf_generator import OIMLPDFReportGenerator
from reports.oiml_docx_generator import OIMLDocxReportGenerator

router = APIRouter(prefix="/oiml", tags=["OIML R 76 NAWI Model Approval"])

pdf_generator = OIMLPDFReportGenerator()
docx_generator = OIMLDocxReportGenerator()

UPLOAD_DIR = "uploads/oiml_evidence"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def calculate_data_hash(eval_obj: NAWIModelApproval) -> str:
    """Generate SHA-256 cryptographic hash of model approval test data for tamper evidence."""
    payload = f"{eval_obj.report_number}:{eval_obj.manufacturer_name}:{eval_obj.model_name}:" \
              f"{eval_obj.max_capacity}:{eval_obj.verification_scale_interval_e}:{eval_obj.status}:" \
              f"{eval_obj.is_fully_compliant}:{str(eval_obj.evaluation_summary)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sync_normalized_models(eval_obj: NAWIModelApproval, user_id: Optional[str], db: Session):
    """
    Synchronizes monolithic evaluation record into normalized relational entities:
    Laboratories, Manufacturers, Instruments, TestReports, TestSessions, TestObservations, ReportVersions.
    """
    # 1. Manufacturer
    mfg = db.query(Manufacturer).filter(Manufacturer.name == eval_obj.manufacturer_name).first()
    if not mfg:
        mfg = Manufacturer(
            name=eval_obj.manufacturer_name,
            address=eval_obj.manufacturer_address,
            country=eval_obj.country_of_origin or "India",
            contact_email=eval_obj.contact_email,
            contact_phone=eval_obj.contact_phone,
            license_number=eval_obj.license_number
        )
        db.add(mfg)
        db.flush()

    # 2. Laboratory
    lab = db.query(Laboratory).filter(Laboratory.name == eval_obj.lab_name).first()
    if not lab:
        lab_code = "LAB-" + uuid.uuid4().hex[:6].upper()
        lab = Laboratory(
            name=eval_obj.lab_name,
            code=lab_code,
            address="National Metrology Complex, New Delhi",
            accreditation=eval_obj.lab_accreditation or "NABL ISO/IEC 17025 Accredited & OIML Issuing Authority"
        )
        db.add(lab)
        db.flush()

    # 3. Instrument
    inst = db.query(Instrument).filter(
        Instrument.manufacturer_id == mfg.id,
        Instrument.model_name == eval_obj.model_name,
        Instrument.serial_number == eval_obj.serial_number
    ).first()
    if not inst:
        inst = Instrument(
            manufacturer_id=mfg.id,
            model_name=eval_obj.model_name,
            serial_number=eval_obj.serial_number or f"SN-{eval_obj.report_number}",
            instrument_type=eval_obj.instrument_type,
            accuracy_class=eval_obj.accuracy_class,
            max_capacity=eval_obj.max_capacity,
            min_capacity=eval_obj.min_capacity,
            verification_scale_interval_e=eval_obj.verification_scale_interval_e,
            scale_interval_d=eval_obj.scale_interval_d,
            units=eval_obj.units,
            n_intervals=eval_obj.n_intervals,
            tare_type=eval_obj.tare_type or "Subtractive",
            max_tare=eval_obj.max_tare,
            temp_range_min=eval_obj.temp_range_min,
            temp_range_max=eval_obj.temp_range_max,
            power_supply=eval_obj.power_supply,
            load_cell_details=eval_obj.load_cell_details,
            indicator_details=eval_obj.indicator_details,
            software_version=eval_obj.software_version,
            software_checksum=eval_obj.software_checksum
        )
        db.add(inst)
        db.flush()

    # 4. Active Rule Version
    rule_ver = db.query(RuleVersion).filter(RuleVersion.active == True).first()

    # 5. TestReport
    report = db.query(TestReport).filter(TestReport.report_number == eval_obj.report_number).first()
    if not report:
        report = TestReport(
            id=eval_obj.id,
            report_number=eval_obj.report_number,
            application_number=eval_obj.application_number,
            instrument_id=inst.id,
            laboratory_id=lab.id,
            rule_version_id=rule_ver.id if rule_ver else None,
            status=eval_obj.status,
            overall_result="PASS" if eval_obj.is_fully_compliant else "FAIL",
            evaluator_id=user_id,
            submission_date=eval_obj.submission_date,
            testing_date=eval_obj.testing_date,
            approval_date=eval_obj.approval_date,
            lab_temperature=eval_obj.lab_temperature,
            lab_humidity=eval_obj.lab_humidity,
            lab_pressure=eval_obj.lab_pressure,
            local_gravity_g=eval_obj.local_gravity_g,
            standard_weights_used=eval_obj.standard_weights_used,
            remarks=eval_obj.remarks,
            conditions_of_approval=eval_obj.conditions_of_approval,
            digital_signature=eval_obj.digital_signature
        )
        db.add(report)
        db.flush()
    else:
        report.status = eval_obj.status
        report.overall_result = "PASS" if eval_obj.is_fully_compliant else "FAIL"
        report.approval_date = eval_obj.approval_date
        report.digital_signature = eval_obj.digital_signature
        report.remarks = eval_obj.remarks

    # 6. Test Sessions and Observations (normalized)
    db.query(TestObservation).filter(TestObservation.report_id == report.id).delete()
    db.query(TestSession).filter(TestSession.report_id == report.id).delete()

    test_data = eval_obj.test_data or {}
    eval_summary = eval_obj.evaluation_summary or {}
    test_summaries = eval_summary.get("test_summaries", {})

    # Weighing Test Observations
    weighing_session = TestSession(
        report_id=report.id,
        test_type="WEIGHING",
        status=test_summaries.get("weighing_test", {}).get("overall_status", "COMPLETED"),
        notes="Weighing Performance Test (Clause A.4.4)"
    )
    db.add(weighing_session)
    db.flush()

    for idx, r in enumerate(test_summaries.get("weighing_test", {}).get("readings", test_data.get("weighing_test", []))):
        obs = TestObservation(
            report_id=report.id,
            session_id=weighing_session.id,
            test_type="WEIGHING",
            test_step=idx + 1,
            direction=r.get("direction", "INCR"),
            applied_load=float(r.get("load", 0.0)),
            indication=float(r.get("indication", 0.0)),
            delta_l=float(r["delta_l"]) if r.get("delta_l") is not None else None,
            raw_error=float(r.get("raw_error", 0.0)) if r.get("raw_error") is not None else None,
            zero_error=float(r.get("zero_error", 0.0)) if r.get("zero_error") is not None else None,
            corrected_error=float(r.get("corrected_error", 0.0)) if r.get("corrected_error") is not None else None,
            permissible_error=float(r.get("mpe_unit", 0.0)) if r.get("mpe_unit") is not None else None,
            result=r.get("status", "PASS")
        )
        db.add(obs)

    # Repeatability Test Observations
    rep_session = TestSession(
        report_id=report.id,
        test_type="REPEATABILITY",
        status=test_summaries.get("repeatability_test", {}).get("overall_status", "COMPLETED"),
        notes="Repeatability Test (Clause A.4.10)"
    )
    db.add(rep_session)
    db.flush()

    for s_idx, s in enumerate(test_data.get("repeatability_test", [])):
        load = float(s.get("load", 0.0))
        for r_idx, val in enumerate(s.get("readings", [])):
            obs = TestObservation(
                report_id=report.id,
                session_id=rep_session.id,
                test_type="REPEATABILITY",
                test_step=r_idx + 1,
                direction="INCR",
                applied_load=load,
                indication=float(val),
                observation_metadata={"series": s_idx + 1}
            )
            db.add(obs)

    # Eccentricity Test Observations
    ecc_session = TestSession(
        report_id=report.id,
        test_type="ECCENTRICITY",
        status=test_summaries.get("eccentricity_test", {}).get("overall_status", "COMPLETED"),
        notes="Eccentricity Test (Clause A.4.7)"
    )
    db.add(ecc_session)
    db.flush()

    ecc_data = test_data.get("eccentricity_test", {})
    ecc_load = float(ecc_data.get("test_load", eval_obj.max_capacity / 3.0))
    for p_idx, pos in enumerate(test_summaries.get("eccentricity_test", {}).get("positions", ecc_data.get("positions", []))):
        obs = TestObservation(
            report_id=report.id,
            session_id=ecc_session.id,
            test_type="ECCENTRICITY",
            test_step=p_idx + 1,
            applied_load=ecc_load,
            indication=float(pos.get("indication", 0.0)),
            delta_l=float(pos["delta_l"]) if pos.get("delta_l") is not None else None,
            corrected_error=float(pos.get("corrected_error", 0.0)) if pos.get("corrected_error") is not None else None,
            permissible_error=float(pos.get("mpe_unit", 0.0)) if pos.get("mpe_unit") is not None else None,
            result=pos.get("status", "PASS"),
            notes=pos.get("position", f"Position {p_idx+1}")
        )
        db.add(obs)

    # 7. Check or create initial ReportVersion if none exists
    has_ver = db.query(ReportVersion).filter(ReportVersion.report_id == report.id).first()
    if not has_ver:
        v1 = ReportVersion(
            report_id=report.id,
            version_number=1,
            version_label="Draft" if eval_obj.status == "DRAFT" else "Certified",
            generated_by=user_id,
            file_path=f"reports/generated/OIML_R76_{eval_obj.report_number.replace('/', '-')}.pdf",
            file_format="PDF",
            checksum=calculate_data_hash(eval_obj)
        )
        db.add(v1)

    db.commit()


@router.get("/standards")
def get_oiml_standards():
    """Returns active OIML R 76 standard rules and revision registry."""
    return {
        "active_standard": get_active_standard(),
        "available_standards": list_standards()
    }


@router.post("/calculate")
def calculate_metrological_compliance(req: NAWICalculateRequest):
    """
    On-the-fly metrological calculation API for digital test data entry forms.
    Returns calculated errors, MPE, and pass/fail status for all observation points.
    """
    specs = {
        "accuracy_class": req.accuracy_class,
        "max_capacity": req.max_capacity,
        "min_capacity": req.min_capacity,
        "verification_scale_interval_e": req.verification_scale_interval_e,
        "scale_interval_d": req.scale_interval_d,
        "is_in_service_test": req.is_in_service_test
    }
    result = evaluate_complete_oiml_r76_evaluation(specs, req.test_data)
    return result


@router.get("/dashboard-stats", response_model=NAWIDashboardStats)
def get_oiml_dashboard_stats(db: Session = Depends(get_db)):
    """Retrieve statistical indicators and distribution metrics for NAWI testing activities."""
    evals = db.query(NAWIModelApproval).all()
    total = len(evals)

    approved = sum(1 for e in evals if e.status in ["APPROVED_COMPLIANT", "FINALIZED"])
    rejected = sum(1 for e in evals if e.status == "REJECTED_NON_COMPLIANT")
    in_progress = sum(1 for e in evals if e.status in ["TESTING_IN_PROGRESS", "SUBMITTED", "UNDER_REVIEW", "CORRECTION_REQUIRED"])
    draft = sum(1 for e in evals if e.status == "DRAFT")

    rate = round((approved / (approved + rejected) * 100), 1) if (approved + rejected) > 0 else 100.0

    class_dist = {"Class I": 0, "Class II": 0, "Class III": 0, "Class IIII": 0}
    type_dist = {}
    for e in evals:
        c = e.accuracy_class or "Class III"
        class_dist[c] = class_dist.get(c, 0) + 1
        t = e.instrument_type or "Electronic Scale"
        type_dist[t] = type_dist.get(t, 0) + 1

    recent = [
        {
            "id": e.id,
            "report_number": e.report_number,
            "manufacturer_name": e.manufacturer_name,
            "model_name": e.model_name,
            "accuracy_class": e.accuracy_class,
            "max_capacity": e.max_capacity,
            "units": e.units,
            "status": e.status,
            "is_fully_compliant": e.is_fully_compliant,
            "testing_date": str(e.testing_date)[:10],
        }
        for e in sorted(evals, key=lambda x: x.created_at, reverse=True)[:5]
    ]

    return NAWIDashboardStats(
        total_evaluations=total,
        approved_compliant=approved,
        rejected_non_compliant=rejected,
        testing_in_progress=in_progress,
        draft_applications=draft,
        compliance_rate_percent=rate,
        class_distribution=class_dist,
        instrument_type_distribution=type_dist,
        recent_evaluations=recent
    )


@router.get("/evaluations", response_model=List[NAWIModelResponse])
def list_evaluations(
    search: Optional[str] = Query(None, description="Search by model, manufacturer, report no"),
    status: Optional[str] = Query(None, description="Filter by status"),
    accuracy_class: Optional[str] = Query(None, description="Filter by class"),
    instrument_type: Optional[str] = Query(None, description="Filter by instrument type"),
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List NAWI evaluations with search, filtering, and pagination."""
    query = db.query(NAWIModelApproval)

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            or_(
                NAWIModelApproval.model_name.ilike(s),
                NAWIModelApproval.manufacturer_name.ilike(s),
                NAWIModelApproval.report_number.ilike(s),
                NAWIModelApproval.application_number.ilike(s),
            )
        )

    if status and status != "ALL":
        query = query.filter(NAWIModelApproval.status == status)

    if accuracy_class and accuracy_class != "ALL":
        query = query.filter(NAWIModelApproval.accuracy_class == accuracy_class)

    if instrument_type and instrument_type != "ALL":
        query = query.filter(NAWIModelApproval.instrument_type == instrument_type)

    evals = query.order_by(desc(NAWIModelApproval.created_at)).offset(offset).limit(limit).all()
    return evals


@router.get("/evaluations/{evaluation_id}", response_model=NAWIModelResponse)
def get_evaluation(evaluation_id: str, db: Session = Depends(get_db)):
    """Retrieve full details of a specific NAWI model evaluation."""
    evaluation = db.query(NAWIModelApproval).filter(NAWIModelApproval.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="NAWI evaluation record not found.")
    return evaluation


@router.post("/evaluations", response_model=NAWIModelResponse, status_code=201)
def create_evaluation(
    payload: NAWIModelCreate,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Create a new NAWI type evaluation submission and evaluate compliance."""
    if user and user.role.lower() == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role has read-only access and cannot create evaluations.")

    user_id = user.id if user else None

    # Generate sequential identifiers if not provided
    year = datetime.now().year
    count = db.query(NAWIModelApproval).count() + 1
    app_no = payload.application_number or f"APP-NAWI-{year}-{count:04d}"
    rep_no = payload.report_number or f"OIML-R76-{year}-IND-{count:04d}"

    # Calculate verification scale intervals n
    n = calculate_verification_scale_intervals(payload.max_capacity, payload.verification_scale_interval_e)

    # Perform metrological evaluation
    specs = {
        "accuracy_class": payload.accuracy_class,
        "max_capacity": payload.max_capacity,
        "min_capacity": payload.min_capacity,
        "verification_scale_interval_e": payload.verification_scale_interval_e,
        "scale_interval_d": payload.scale_interval_d,
    }
    eval_result = evaluate_complete_oiml_r76_evaluation(specs, payload.test_data or {})

    is_compliant = eval_result["is_fully_compliant"]
    initial_status = "DRAFT"

    eval_obj = NAWIModelApproval(
        application_number=app_no,
        report_number=rep_no,
        status=initial_status,
        applicant_type=payload.applicant_type,
        manufacturer_name=payload.manufacturer_name,
        manufacturer_address=payload.manufacturer_address,
        country_of_origin=payload.country_of_origin,
        contact_email=payload.contact_email,
        contact_phone=payload.contact_phone,
        license_number=payload.license_number,
        instrument_type=payload.instrument_type,
        model_name=payload.model_name,
        serial_number=payload.serial_number or f"SN-{year}-{count:05d}",
        year_of_manufacture=payload.year_of_manufacture,
        accuracy_class=payload.accuracy_class,
        max_capacity=payload.max_capacity,
        min_capacity=payload.min_capacity,
        verification_scale_interval_e=payload.verification_scale_interval_e,
        scale_interval_d=payload.scale_interval_d,
        units=payload.units,
        n_intervals=n,
        tare_type=payload.tare_type,
        max_tare=payload.max_tare or payload.max_capacity,
        temp_range_min=payload.temp_range_min,
        temp_range_max=payload.temp_range_max,
        power_supply=payload.power_supply,
        load_cell_details=payload.load_cell_details,
        indicator_details=payload.indicator_details,
        software_version=payload.software_version,
        software_checksum=payload.software_checksum,
        lab_name=payload.lab_name,
        lab_accreditation=payload.lab_accreditation,
        lab_temperature=payload.lab_temperature,
        lab_humidity=payload.lab_humidity,
        lab_pressure=payload.lab_pressure,
        local_gravity_g=payload.local_gravity_g,
        standard_weights_used=payload.standard_weights_used,
        testing_officer_name=payload.testing_officer_name,
        approving_officer_name=payload.approving_officer_name,
        test_data=payload.test_data or {},
        evaluation_summary=eval_result,
        is_fully_compliant=is_compliant,
        remarks=payload.remarks,
        conditions_of_approval=payload.conditions_of_approval or "Instrument subject to mandatory initial verification before commercial use."
    )

    db.add(eval_obj)
    db.commit()
    db.refresh(eval_obj)

    # Sync to normalized entities
    sync_normalized_models(eval_obj, user_id, db)

    # Immutable Audit Log
    audit = AuditLog(
        entity_type="test_report",
        entity_id=eval_obj.id,
        user_id=user_id,
        action="REPORT_CREATED",
        new_value=f"Created report {eval_obj.report_number} for {eval_obj.model_name}",
        timestamp=datetime.now(timezone.utc)
    )
    db.add(audit)
    db.commit()

    return eval_obj


@router.put("/evaluations/{evaluation_id}", response_model=NAWIModelResponse)
def update_evaluation(
    evaluation_id: str,
    payload: NAWIModelUpdate,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Update evaluation test data, observations, or specifications and recalculate compliance."""
    if user and user.role.lower() == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role has read-only access and cannot edit evaluations.")

    evaluation = db.query(NAWIModelApproval).filter(NAWIModelApproval.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="NAWI evaluation record not found.")

    if evaluation.status == "FINALIZED":
        raise HTTPException(status_code=400, detail="Finalized reports are locked and cannot be modified.")

    update_dict = payload.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(evaluation, field, val)

    # Re-calculate n and metrological results if relevant fields changed
    if evaluation.verification_scale_interval_e > 0:
        evaluation.n_intervals = calculate_verification_scale_intervals(
            evaluation.max_capacity, evaluation.verification_scale_interval_e
        )

    specs = {
        "accuracy_class": evaluation.accuracy_class,
        "max_capacity": evaluation.max_capacity,
        "min_capacity": evaluation.min_capacity,
        "verification_scale_interval_e": evaluation.verification_scale_interval_e,
        "scale_interval_d": evaluation.scale_interval_d,
    }
    eval_result = evaluate_complete_oiml_r76_evaluation(specs, evaluation.test_data or {})
    evaluation.evaluation_summary = eval_result
    evaluation.is_fully_compliant = eval_result["is_fully_compliant"]

    if payload.status:
        evaluation.status = payload.status

    evaluation.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(evaluation)

    # Sync to normalized entities
    sync_normalized_models(evaluation, user.id if user else None, db)

    # Audit Log
    audit = AuditLog(
        entity_type="test_report",
        entity_id=evaluation.id,
        user_id=user.id if user else None,
        action="REPORT_UPDATED",
        new_value=f"Updated test data/specs. Status: {evaluation.status}, Compliant: {evaluation.is_fully_compliant}",
        timestamp=datetime.now(timezone.utc)
    )
    db.add(audit)
    db.commit()

    return evaluation


@router.post("/evaluations/{evaluation_id}/transition")
def transition_workflow(
    evaluation_id: str,
    payload: WorkflowTransitionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enforces real approval state machine transitions:
    DRAFT -> SUBMITTED -> UNDER_REVIEW -> CORRECTION_REQUIRED -> APPROVED -> FINALIZED
    """
    evaluation = db.query(NAWIModelApproval).filter(NAWIModelApproval.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation record not found.")

    action = payload.action.upper()
    role = (user.role or "").lower()
    old_status = evaluation.status

    if role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role cannot perform workflow transitions.")

    if action == "SUBMIT":
        if role not in ["inspector", "admin"]:
            raise HTTPException(status_code=403, detail="Only Test Engineers or Admins can submit reports for review.")
        if old_status not in ["DRAFT", "CORRECTION_REQUIRED", "TESTING_IN_PROGRESS"]:
            raise HTTPException(status_code=400, detail=f"Cannot submit report in status '{old_status}'.")
        evaluation.status = "SUBMITTED"

    elif action == "START_REVIEW":
        if role not in ["supervisor", "admin"]:
            raise HTTPException(status_code=403, detail="Only Reviewers/Supervisors can begin report reviews.")
        if old_status != "SUBMITTED":
            raise HTTPException(status_code=400, detail=f"Cannot start review on report in status '{old_status}'. Must be SUBMITTED.")
        evaluation.status = "UNDER_REVIEW"

    elif action == "REQUEST_CORRECTION":
        if role not in ["supervisor", "admin"]:
            raise HTTPException(status_code=403, detail="Only Reviewers/Supervisors can request report corrections.")
        if old_status != "UNDER_REVIEW":
            raise HTTPException(status_code=400, detail=f"Cannot request corrections in status '{old_status}'. Must be UNDER_REVIEW.")
        if not payload.notes or not payload.notes.strip():
            raise HTTPException(status_code=400, detail="Notes explaining required corrections are mandatory.")
        evaluation.status = "CORRECTION_REQUIRED"
        evaluation.remarks = (evaluation.remarks or "") + f"\n[CORRECTION REQUESTED by {user.full_name}]: {payload.notes}"

    elif action == "APPROVE":
        if role not in ["supervisor", "admin"]:
            raise HTTPException(status_code=403, detail="Only Reviewers/Supervisors can approve reports.")
        if old_status != "UNDER_REVIEW":
            raise HTTPException(status_code=400, detail=f"Cannot approve report in status '{old_status}'. Must be UNDER_REVIEW.")
        if not evaluation.is_fully_compliant:
            raise HTTPException(status_code=400, detail="Cannot approve non-compliant evaluation. All metrological tests must pass.")
        evaluation.status = "APPROVED_COMPLIANT"
        evaluation.approval_date = datetime.now(timezone.utc)
        if payload.notes:
            evaluation.remarks = (evaluation.remarks or "") + f"\n[APPROVAL NOTES]: {payload.notes}"

    elif action == "REJECT":
        if role not in ["supervisor", "admin"]:
            raise HTTPException(status_code=403, detail="Only Reviewers/Supervisors can reject reports.")
        if old_status != "UNDER_REVIEW":
            raise HTTPException(status_code=400, detail=f"Cannot reject report in status '{old_status}'. Must be UNDER_REVIEW.")
        if not payload.notes or not payload.notes.strip():
            raise HTTPException(status_code=400, detail="Notes explaining reason for rejection are mandatory.")
        evaluation.status = "REJECTED_NON_COMPLIANT"
        evaluation.remarks = (evaluation.remarks or "") + f"\n[REJECTION REASON]: {payload.notes}"

    elif action == "FINALIZE":
        if role not in ["supervisor", "admin"]:
            raise HTTPException(status_code=403, detail="Only Reviewers/Supervisors can finalize reports.")
        if old_status not in ["APPROVED_COMPLIANT", "UNDER_REVIEW"]:
            raise HTTPException(status_code=400, detail=f"Cannot finalize report in status '{old_status}'. Must be APPROVED.")
        if not evaluation.is_fully_compliant:
            raise HTTPException(status_code=400, detail="Cannot finalize non-compliant evaluation.")

        evaluation.status = "FINALIZED"
        evaluation.updated_at = datetime.now(timezone.utc)

        # Generate official report version
        curr_ver_count = db.query(ReportVersion).filter(ReportVersion.report_id == evaluation.id).count()
        new_ver = curr_ver_count + 1
        checksum = calculate_data_hash(evaluation)

        version_rec = ReportVersion(
            report_id=evaluation.id,
            version_number=new_ver,
            version_label=f"v{new_ver} Final Certified",
            generated_by=user.id,
            file_path=f"reports/generated/OIML_R76_{evaluation.model_name}_{evaluation.report_number.replace('/', '-')}_v{new_ver}.pdf",
            file_format="PDF",
            checksum=checksum
        )
        db.add(version_rec)

    else:
        raise HTTPException(status_code=400, detail=f"Unknown transition action '{action}'.")

    evaluation.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(evaluation)

    # Sync to normalized entities
    sync_normalized_models(evaluation, user.id, db)

    # Record Audit Log
    audit = AuditLog(
        entity_type="test_report",
        entity_id=evaluation.id,
        user_id=user.id,
        action=f"STATUS_TRANSITION_{action}",
        old_value=old_status,
        new_value=evaluation.status,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(audit)
    db.commit()

    return {
        "message": f"Report transitioned from {old_status} to {evaluation.status}",
        "status": evaluation.status,
        "evaluation": evaluation
    }


@router.post("/evaluations/{evaluation_id}/upload-photo")
async def upload_instrument_attachment(
    evaluation_id: str,
    attachment_type: str = Form("INSTRUMENT_PHOTO"),
    title: str = Form("Instrument Photo"),
    file: UploadFile = File(...),
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Upload instrument photograph, nameplate image, or technical diagram."""
    if user and user.role.lower() == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role cannot upload attachments.")

    evaluation = db.query(NAWIModelApproval).filter(NAWIModelApproval.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found.")

    allowed_exts = [".jpg", ".jpeg", ".png", ".webp", ".pdf", ".docx"]
    ext = os.path.splitext(file.filename)[1].lower() or ".jpg"
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {', '.join(allowed_exts)}")

    unique_fn = f"{evaluation_id}_{uuid.uuid4().hex[:8]}{ext}"
    dest_path = os.path.join(UPLOAD_DIR, unique_fn)

    content = await file.read()
    if len(content) > 15 * 1024 * 1024: # 15 MB
        raise HTTPException(status_code=400, detail="Attachment file size exceeds 15 MB limit.")

    with open(dest_path, "wb") as f:
        f.write(content)

    clean_file_path = dest_path.replace("\\", "/")

    # Create in nawi_attachments
    attachment = NAWIAttachment(
        evaluation_id=evaluation_id,
        attachment_type=attachment_type,
        title=title,
        file_path=clean_file_path,
        file_name=file.filename,
        mime_type=file.content_type or "image/jpeg",
        file_size_bytes=len(content)
    )
    db.add(attachment)

    # Create in normalized attachments
    norm_attachment = Attachment(
        report_id=evaluation_id,
        filename=file.filename,
        file_type=attachment_type,
        storage_key=unique_fn,
        file_path=clean_file_path,
        mime_type=file.content_type or "image/jpeg",
        file_size_bytes=len(content),
        uploaded_by=user.id if user else None
    )
    db.add(norm_attachment)

    audit = AuditLog(
        entity_type="test_report",
        entity_id=evaluation_id,
        user_id=user.id if user else None,
        action="ATTACHMENT_UPLOADED",
        new_value=f"Uploaded {title} ({file.filename})",
        timestamp=datetime.now(timezone.utc)
    )
    db.add(audit)
    db.commit()
    db.refresh(attachment)

    return {
        "message": "Attachment uploaded successfully",
        "attachment_id": attachment.id,
        "id": attachment.id,
        "attachment_type": attachment.attachment_type,
        "title": attachment.title,
        "file_path": attachment.file_path,
        "file_name": attachment.file_name,
        "file_size_bytes": attachment.file_size_bytes
    }


@router.get("/evaluations/{evaluation_id}/attachments")
def list_evaluation_attachments(evaluation_id: str, db: Session = Depends(get_db)):
    """List all attachments associated with a specific NAWI evaluation."""
    attachments = db.query(NAWIAttachment).filter(NAWIAttachment.evaluation_id == evaluation_id).all()
    return attachments


@router.get("/evaluations/{evaluation_id}/audit-logs", response_model=List[AuditLogResponse])
def get_evaluation_audit_logs(evaluation_id: str, db: Session = Depends(get_db)):
    """Retrieve immutable audit trail records for a specific NAWI test report."""
    logs = db.query(AuditLog).filter(
        AuditLog.entity_id == evaluation_id
    ).order_by(desc(AuditLog.timestamp)).all()
    return logs


@router.get("/evaluations/{evaluation_id}/versions", response_model=List[ReportVersionResponse])
def get_evaluation_versions(evaluation_id: str, db: Session = Depends(get_db)):
    """Retrieve version history for a specific NAWI test report."""
    versions = db.query(ReportVersion).filter(
        ReportVersion.report_id == evaluation_id
    ).order_by(desc(ReportVersion.version_number)).all()
    return versions


@router.get("/laboratories", response_model=List[LaboratoryResponse])
def list_laboratories(db: Session = Depends(get_db)):
    """List all accredited Legal Metrology testing laboratories."""
    return db.query(Laboratory).filter(Laboratory.is_active == True).all()


@router.get("/manufacturers", response_model=List[ManufacturerResponse])
def list_manufacturers(db: Session = Depends(get_db)):
    """List all registered weighing instrument manufacturers."""
    return db.query(Manufacturer).order_by(Manufacturer.name).all()


@router.get("/rule-versions", response_model=List[RuleVersionResponse])
def list_rule_versions(db: Session = Depends(get_db)):
    """List all codified metrological rule versions."""
    return db.query(RuleVersion).order_by(desc(RuleVersion.created_at)).all()


@router.post("/evaluations/{evaluation_id}/sign")
def digitally_sign_evaluation(
    evaluation_id: str,
    payload: NAWIDigitalSignRequest,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Digitally sign evaluation report with cryptographic SHA-256 integrity hash."""
    if user and user.role.lower() not in ["supervisor", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Only Reviewers/Supervisors or Administrators can digitally sign and certify reports."
        )

    evaluation = db.query(NAWIModelApproval).filter(NAWIModelApproval.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found.")

    if not evaluation.is_fully_compliant:
        raise HTTPException(status_code=400, detail="Cannot digitally certify non-compliant instrument evaluation.")

    data_hash = calculate_data_hash(evaluation)
    now_str = datetime.now(timezone.utc).isoformat()

    sig_block = {
        "signed_by": payload.officer_name,
        "designation": payload.designation,
        "timestamp": now_str,
        "sha256_hash": data_hash,
        "signature_token": f"GOV-IN-LM-CERT-{uuid.uuid4().hex[:12].upper()}",
        "status": "VERIFIED_AUTHENTIC",
        "remarks": payload.signature_remarks or "Digitally signed under Section 22 of the Legal Metrology Act, 2009."
    }

    evaluation.digital_signature = sig_block
    evaluation.status = "APPROVED_COMPLIANT"
    evaluation.approval_date = datetime.now(timezone.utc)
    evaluation.updated_at = datetime.now(timezone.utc)

    # Sync normalized models
    sync_normalized_models(evaluation, user.id if user else None, db)

    # Audit log
    audit = AuditLog(
        entity_type="test_report",
        entity_id=evaluation.id,
        user_id=user.id if user else None,
        action="REPORT_DIGITALLY_SIGNED",
        new_value=f"Digitally signed by {payload.officer_name} ({payload.designation}) with SHA-256 seal {data_hash[:16]}...",
        timestamp=datetime.now(timezone.utc)
    )
    db.add(audit)
    db.commit()
    db.refresh(evaluation)

    return {"message": "Report digitally signed successfully", "digital_signature": sig_block}



@router.get("/evaluations/{evaluation_id}/export/pdf")
def export_evaluation_pdf(evaluation_id: str, db: Session = Depends(get_db)):
    """Generate and download official standardized OIML R 76 PDF Test Report."""
    evaluation = db.query(NAWIModelApproval).filter(NAWIModelApproval.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found.")

    eval_data = {
        "report_number": evaluation.report_number,
        "application_number": evaluation.application_number,
        "status": evaluation.status,
        "testing_date": evaluation.testing_date,
        "manufacturer_name": evaluation.manufacturer_name,
        "manufacturer_address": evaluation.manufacturer_address,
        "instrument_type": evaluation.instrument_type,
        "model_name": evaluation.model_name,
        "serial_number": evaluation.serial_number,
        "accuracy_class": evaluation.accuracy_class,
        "max_capacity": evaluation.max_capacity,
        "min_capacity": evaluation.min_capacity,
        "verification_scale_interval_e": evaluation.verification_scale_interval_e,
        "scale_interval_d": evaluation.scale_interval_d,
        "units": evaluation.units,
        "n_intervals": evaluation.n_intervals,
        "max_tare": evaluation.max_tare,
        "temp_range_min": evaluation.temp_range_min,
        "temp_range_max": evaluation.temp_range_max,
        "power_supply": evaluation.power_supply,
        "load_cell_details": evaluation.load_cell_details,
        "software_version": evaluation.software_version,
        "software_checksum": evaluation.software_checksum,
        "lab_name": evaluation.lab_name,
        "lab_accreditation": evaluation.lab_accreditation,
        "lab_temperature": evaluation.lab_temperature,
        "lab_humidity": evaluation.lab_humidity,
        "lab_pressure": evaluation.lab_pressure,
        "local_gravity_g": evaluation.local_gravity_g,
        "standard_weights_used": evaluation.standard_weights_used,
        "testing_officer_name": evaluation.testing_officer_name,
        "approving_officer_name": evaluation.approving_officer_name,
        "is_fully_compliant": evaluation.is_fully_compliant,
        "test_data": evaluation.test_data,
        "evaluation_summary": evaluation.evaluation_summary,
        "digital_signature": evaluation.digital_signature,
    }

    pdf_file = pdf_generator.generate_report(eval_data)
    clean_fn = f"OIML_R76_{evaluation.model_name}_{evaluation.report_number.replace('/', '_')}.pdf"
    return FileResponse(pdf_file, media_type="application/pdf", filename=clean_fn)


@router.get("/evaluations/{evaluation_id}/export/docx")
def export_evaluation_docx(evaluation_id: str, db: Session = Depends(get_db)):
    """Generate and download editable standardized MS Word (.docx) Test Report."""
    evaluation = db.query(NAWIModelApproval).filter(NAWIModelApproval.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found.")

    eval_data = {
        "report_number": evaluation.report_number,
        "application_number": evaluation.application_number,
        "status": evaluation.status,
        "testing_date": evaluation.testing_date,
        "manufacturer_name": evaluation.manufacturer_name,
        "manufacturer_address": evaluation.manufacturer_address,
        "instrument_type": evaluation.instrument_type,
        "model_name": evaluation.model_name,
        "serial_number": evaluation.serial_number,
        "accuracy_class": evaluation.accuracy_class,
        "max_capacity": evaluation.max_capacity,
        "min_capacity": evaluation.min_capacity,
        "verification_scale_interval_e": evaluation.verification_scale_interval_e,
        "scale_interval_d": evaluation.scale_interval_d,
        "units": evaluation.units,
        "n_intervals": evaluation.n_intervals,
        "max_tare": evaluation.max_tare,
        "temp_range_min": evaluation.temp_range_min,
        "temp_range_max": evaluation.temp_range_max,
        "power_supply": evaluation.power_supply,
        "load_cell_details": evaluation.load_cell_details,
        "software_version": evaluation.software_version,
        "software_checksum": evaluation.software_checksum,
        "lab_name": evaluation.lab_name,
        "lab_accreditation": evaluation.lab_accreditation,
        "lab_temperature": evaluation.lab_temperature,
        "lab_humidity": evaluation.lab_humidity,
        "lab_pressure": evaluation.lab_pressure,
        "local_gravity_g": evaluation.local_gravity_g,
        "standard_weights_used": evaluation.standard_weights_used,
        "testing_officer_name": evaluation.testing_officer_name,
        "approving_officer_name": evaluation.approving_officer_name,
        "is_fully_compliant": evaluation.is_fully_compliant,
        "test_data": evaluation.test_data,
        "evaluation_summary": evaluation.evaluation_summary,
        "digital_signature": evaluation.digital_signature,
    }

    docx_file = docx_generator.generate_report(eval_data)
    clean_fn = f"OIML_R76_{evaluation.model_name}_{evaluation.report_number.replace('/', '_')}.docx"
    return FileResponse(
        docx_file,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=clean_fn
    )


@router.get("/user-manual")
def download_user_manual():
    """Download the official comprehensive PDF User Operating Manual with scenario data."""
    manual_path = "docs/NAWI_OIML_R76_Application_User_Manual.pdf"
    if not os.path.exists(manual_path):
        manual_path = "reports/generated/NAWI_OIML_R76_Application_User_Manual.pdf"
    if not os.path.exists(manual_path):
        raise HTTPException(status_code=404, detail="User manual PDF not found on server.")
    return FileResponse(
        manual_path,
        media_type="application/pdf",
        filename="NAWI_OIML_R76_Application_User_Manual.pdf"
    )


@router.post("/seed-demo")
def seed_demo_evaluations(db: Session = Depends(get_db)):
    """Seed comprehensive realistic OIML R 76 evaluation records for demonstration."""
    existing = db.query(NAWIModelApproval).count()
    if existing > 0:
        return {"message": f"Database already has {existing} NAWI evaluations. Seeding skipped."}

    # Demo 1: Class III Retail Price-Computing Scale (Compliant, Approved)
    demo1_test_data = {
        "weighing_test": [
            {"load": 0.0, "direction": "INCR", "indication": 0.0, "delta_l": 0.0025},
            {"load": 0.1, "direction": "INCR", "indication": 0.1, "delta_l": 0.0025},
            {"load": 2.5, "direction": "INCR", "indication": 2.5, "delta_l": 0.0024},
            {"load": 5.0, "direction": "INCR", "indication": 5.0, "delta_l": 0.0025},
            {"load": 7.5, "direction": "INCR", "indication": 7.5, "delta_l": 0.0026},
            {"load": 10.0, "direction": "INCR", "indication": 10.0, "delta_l": 0.0027},
            {"load": 15.0, "direction": "INCR", "indication": 15.0, "delta_l": 0.0025},
            # Decreasing
            {"load": 10.0, "direction": "DECR", "indication": 10.0, "delta_l": 0.0026},
            {"load": 5.0, "direction": "DECR", "indication": 5.0, "delta_l": 0.0025},
            {"load": 2.5, "direction": "DECR", "indication": 2.5, "delta_l": 0.0025},
            {"load": 0.1, "direction": "DECR", "indication": 0.1, "delta_l": 0.0025},
            {"load": 0.0, "direction": "DECR", "indication": 0.0, "delta_l": 0.0025},
        ],
        "repeatability_test": [
            {"load": 7.5, "readings": [7.500, 7.500, 7.505, 7.500, 7.500, 7.505, 7.500, 7.500, 7.505, 7.500]},
            {"load": 15.0, "readings": [15.000, 15.005, 15.000, 15.005, 15.000, 15.000, 15.005, 15.000, 15.005, 15.000]}
        ],
        "eccentricity_test": {
            "test_load": 5.0,
            "positions": [
                {"position": "Position 1 (Center)", "indication": 5.000, "delta_l": 0.0025, "zero_error": 0.0},
                {"position": "Position 2 (Front-Left)", "indication": 5.000, "delta_l": 0.0026, "zero_error": 0.0},
                {"position": "Position 3 (Rear-Left)", "indication": 5.005, "delta_l": 0.0024, "zero_error": 0.0},
                {"position": "Position 4 (Rear-Right)", "indication": 5.000, "delta_l": 0.0025, "zero_error": 0.0},
                {"position": "Position 5 (Front-Right)", "indication": 5.000, "delta_l": 0.0025, "zero_error": 0.0}
            ]
        },
        "tare_zero_test": {
            "zero_setting_indication": 0.000,
            "zero_delta_l": 0.0025,
            "tare_load": 5.0,
            "tare_indication": 5.000,
            "tare_delta_l": 0.0025,
            "net_load": 10.0,
            "net_indication": 10.000,
            "net_delta_l": 0.0025
        },
        "discrimination_test": [
            {"load_level": "Min (0.1kg)", "load": 0.1, "initial_indication": 0.1, "extra_load": 0.007, "new_indication": 0.105},
            {"load_level": "Half-Max (7.5kg)", "load": 7.5, "initial_indication": 7.5, "extra_load": 0.007, "new_indication": 7.505},
            {"load_level": "Max (15.0kg)", "load": 15.0, "initial_indication": 15.0, "extra_load": 0.007, "new_indication": 15.005}
        ],
        "environmental_voltage_test": {
            "temperatures": [
                {"temperature_c": 20.0, "load": 15.0, "corrected_error": 0.001},
                {"temperature_c": 40.0, "load": 15.0, "corrected_error": 0.002},
                {"temperature_c": -10.0, "load": 15.0, "corrected_error": 0.002}
            ],
            "voltages": [
                {"condition": "Nominal 230V AC", "load": 15.0, "corrected_error": 0.001},
                {"condition": "Mains High +10% (253V)", "load": 15.0, "corrected_error": 0.002},
                {"condition": "Mains Low -15% (187V)", "load": 15.0, "corrected_error": 0.002}
            ]
        }
    }

    eval1_specs = {
        "accuracy_class": "Class III",
        "max_capacity": 15.0,
        "min_capacity": 0.1,
        "verification_scale_interval_e": 0.005,
        "scale_interval_d": 0.005,
    }
    eval1_summary = evaluate_complete_oiml_r76_evaluation(eval1_specs, demo1_test_data)

    eval1 = NAWIModelApproval(
        application_number="APP-NAWI-2026-0012",
        report_number="OIML-R76-2026-IND-0012",
        status="APPROVED_COMPLIANT",
        submission_date=datetime(2026, 8, 10, 10, 0, 0),
        testing_date=datetime(2026, 8, 14, 15, 30, 0),
        approval_date=datetime(2026, 8, 16, 12, 0, 0),
        applicant_type="Manufacturer",
        manufacturer_name="Metler Precision Weighing Systems India Pvt Ltd",
        manufacturer_address="Plot 44-46, Electronics City Phase II, Bangalore, Karnataka - 560100",
        country_of_origin="India",
        contact_email="regulatory@metlerprecision.in",
        contact_phone="+91 80 4123 9988",
        license_number="LM-IND-MFG-KA-4491",
        instrument_type="Electronic Retail Counter Scale",
        model_name="MPS-Retail-3000",
        serial_number="SN-2026-MPS-04891",
        year_of_manufacture=2026,
        accuracy_class="Class III",
        max_capacity=15.0,
        min_capacity=0.1,
        verification_scale_interval_e=0.005,
        scale_interval_d=0.005,
        units="kg",
        n_intervals=3000,
        tare_type="Subtractive",
        max_tare=15.0,
        temp_range_min=-10.0,
        temp_range_max=40.0,
        power_supply="230V AC (+10% / -15%), 50Hz with 6V 4.5Ah Backup Battery",
        load_cell_details="Zemic L6E3 Aluminum Single Point C3 Load Cell (OIML R60 Certified)",
        indicator_details="7-Segment Red LED Dual Customer & Operator Display, 24-bit Sigma-Delta ADC",
        software_version="v2.1.0-IND",
        software_checksum="CRC32: 0x9B41F0A2",
        lab_name="National Legal Metrology Type Evaluation Laboratory",
        lab_accreditation="NABL ISO/IEC 17025 Accredited & OIML Issuing Authority",
        lab_temperature=23.4,
        lab_humidity=51.0,
        lab_pressure=1012.8,
        local_gravity_g=9.7803,
        standard_weights_used="Class M1 Calibrated Working Standards (Traceability: NPL-M1-2026-092)",
        testing_officer_name="Er. Rajesh Sharma (Senior Metrological Officer)",
        approving_officer_name="Dr. Priya V. Iyer (Director of Legal Metrology)",
        test_data=demo1_test_data,
        evaluation_summary=eval1_summary,
        is_fully_compliant=True,
        remarks="All metrological tests fully compliant with OIML R 76-1:2006. Pattern recommended for approval.",
        conditions_of_approval="Model approved for trade transactions under Section 22. Verification stamping required prior to installation.",
        digital_signature={
            "signed_by": "Er. Rajesh Sharma",
            "designation": "Senior Metrological Officer",
            "timestamp": "2026-08-16T11:45:00Z",
            "sha256_hash": "a4d8c910398fbe8c7d9e1029348bac1928374650192837465abc123def456789",
            "signature_token": "GOV-IN-LM-CERT-MPS3000-OK",
            "status": "VERIFIED_AUTHENTIC"
        }
    )
    db.add(eval1)

    # Demo 2: Class II High Accuracy Laboratory Balance (Compliant, Approved)
    demo2_test_data = {
        "weighing_test": [
            {"load": 0.0, "direction": "INCR", "indication": 0.0, "delta_l": 0.005},
            {"load": 0.02, "direction": "INCR", "indication": 0.02, "delta_l": 0.005},
            {"load": 50.0, "direction": "INCR", "indication": 50.0, "delta_l": 0.005},
            {"load": 200.0, "direction": "INCR", "indication": 200.0, "delta_l": 0.006},
            {"load": 300.0, "direction": "INCR", "indication": 300.0, "delta_l": 0.005},
            # Decreasing
            {"load": 200.0, "direction": "DECR", "indication": 200.0, "delta_l": 0.005},
            {"load": 50.0, "direction": "DECR", "indication": 50.0, "delta_l": 0.005},
            {"load": 0.0, "direction": "DECR", "indication": 0.0, "delta_l": 0.005},
        ],
        "repeatability_test": [
            {"load": 150.0, "readings": [150.000, 150.010, 150.000, 150.000, 150.010, 150.000, 150.000, 150.010, 150.000, 150.000]},
            {"load": 300.0, "readings": [300.000, 300.010, 300.010, 300.000, 300.010, 300.000, 300.010, 300.000, 300.010, 300.000]}
        ],
        "eccentricity_test": {
            "test_load": 100.0,
            "positions": [
                {"position": "Position 1 (Center)", "indication": 100.000, "delta_l": 0.005, "zero_error": 0.0},
                {"position": "Position 2 (Front-Left)", "indication": 100.010, "delta_l": 0.005, "zero_error": 0.0},
                {"position": "Position 3 (Rear-Left)", "indication": 100.000, "delta_l": 0.005, "zero_error": 0.0},
                {"position": "Position 4 (Rear-Right)", "indication": 100.010, "delta_l": 0.005, "zero_error": 0.0},
                {"position": "Position 5 (Front-Right)", "indication": 100.000, "delta_l": 0.005, "zero_error": 0.0}
            ]
        },
        "tare_zero_test": {
            "zero_setting_indication": 0.000,
            "zero_delta_l": 0.005,
            "tare_load": 100.0,
            "tare_indication": 100.000,
            "tare_delta_l": 0.005,
            "net_load": 200.0,
            "net_indication": 200.000,
            "net_delta_l": 0.005
        }
    }
    eval2_specs = {
        "accuracy_class": "Class II",
        "max_capacity": 300.0,
        "min_capacity": 0.02,
        "verification_scale_interval_e": 0.01,
        "scale_interval_d": 0.001,
    }
    eval2_summary = evaluate_complete_oiml_r76_evaluation(eval2_specs, demo2_test_data)

    eval2 = NAWIModelApproval(
        application_number="APP-NAWI-2026-0018",
        report_number="OIML-R76-2026-IND-0018",
        status="APPROVED_COMPLIANT",
        submission_date=datetime(2026, 8, 20, 11, 0, 0),
        testing_date=datetime(2026, 8, 25, 14, 0, 0),
        approval_date=datetime(2026, 8, 28, 10, 0, 0),
        applicant_type="Manufacturer",
        manufacturer_name="Optima Analytical Instruments LLP",
        manufacturer_address="Tech Park Sector 62, Noida, Uttar Pradesh - 201301",
        country_of_origin="India",
        contact_email="standards@optimabalance.com",
        contact_phone="+91 120 499 1122",
        license_number="LM-IND-MFG-UP-7812",
        instrument_type="Precision Laboratory Balance",
        model_name="Optima-Precise-300G",
        serial_number="SN-2026-OPT-99120",
        year_of_manufacture=2026,
        accuracy_class="Class II",
        max_capacity=300.0,
        min_capacity=0.02,
        verification_scale_interval_e=0.01,
        scale_interval_d=0.001,
        units="g",
        n_intervals=30000,
        tare_type="Subtractive",
        max_tare=300.0,
        temp_range_min=10.0,
        temp_range_max=30.0,
        power_supply="12V DC Adapter (via 230V AC Mains 50Hz)",
        load_cell_details="Electromagnetic Force Restoration (EMFR) Monolithic Sensor",
        indicator_details="High-Contrast Graphic LCD with Touchpad, Internal Auto-Calibration Motor",
        software_version="v3.4.1",
        software_checksum="SHA1: e5fa901238471c9d8e7",
        lab_name="National Legal Metrology Type Evaluation Laboratory",
        lab_accreditation="NABL ISO/IEC 17025 Accredited & OIML Issuing Authority",
        lab_temperature=21.2,
        lab_humidity=48.0,
        lab_pressure=1014.1,
        local_gravity_g=9.7803,
        standard_weights_used="Class E2 & F1 Mass Standards (Traceable to NPL India)",
        testing_officer_name="Er. Rajesh Sharma (Senior Metrological Officer)",
        approving_officer_name="Dr. Priya V. Iyer (Director of Legal Metrology)",
        test_data=demo2_test_data,
        evaluation_summary=eval2_summary,
        is_fully_compliant=True,
        remarks="High accuracy Class II balance with automatic internal calibration meets all OIML criteria.",
        conditions_of_approval="Approved for jewellery, precious metals and pharmaceutical laboratory applications.",
        digital_signature={
            "signed_by": "Er. Rajesh Sharma",
            "designation": "Senior Metrological Officer",
            "timestamp": "2026-08-28T09:30:00Z",
            "sha256_hash": "c8b1a9402837461928374619283746abcde9912384756192837465abcdef1234",
            "signature_token": "GOV-IN-LM-CERT-OPT300G-OK",
            "status": "VERIFIED_AUTHENTIC"
        }
    )
    db.add(eval2)

    # Demo 3: Class III Heavy-Duty Pitless Electronic Weighbridge (In Testing)
    demo3_test_data = {
        "weighing_test": [
            {"load": 0.0, "direction": "INCR", "indication": 0.0, "delta_l": 5.0},
            {"load": 1000.0, "direction": "INCR", "indication": 1000.0, "delta_l": 5.0},
            {"load": 10000.0, "direction": "INCR", "indication": 10000.0, "delta_l": 6.0},
            {"load": 20000.0, "direction": "INCR", "indication": 20000.0, "delta_l": 5.0},
            {"load": 40000.0, "direction": "INCR", "indication": 40000.0, "delta_l": 8.0},
            {"load": 60000.0, "direction": "INCR", "indication": 60000.0, "delta_l": 5.0},
        ],
        "eccentricity_test": {
            "test_load": 15000.0,
            "positions": [
                {"position": "Support 1 (Front Left)", "indication": 15000.0, "delta_l": 5.0, "zero_error": 0.0},
                {"position": "Support 2 (Front Right)", "indication": 15000.0, "delta_l": 5.0, "zero_error": 0.0},
                {"position": "Support 3 (Mid Left)", "indication": 15010.0, "delta_l": 5.0, "zero_error": 0.0},
                {"position": "Support 4 (Mid Right)", "indication": 15000.0, "delta_l": 5.0, "zero_error": 0.0},
                {"position": "Support 5 (Rear Left)", "indication": 15010.0, "delta_l": 5.0, "zero_error": 0.0},
                {"position": "Support 6 (Rear Right)", "indication": 15000.0, "delta_l": 5.0, "zero_error": 0.0}
            ]
        }
    }
    eval3_specs = {
        "accuracy_class": "Class III",
        "max_capacity": 60000.0,
        "min_capacity": 400.0,
        "verification_scale_interval_e": 20.0,
        "scale_interval_d": 20.0,
    }
    eval3_summary = evaluate_complete_oiml_r76_evaluation(eval3_specs, demo3_test_data)

    eval3 = NAWIModelApproval(
        application_number="APP-NAWI-2026-0027",
        report_number="OIML-R76-2026-IND-0027",
        status="TESTING_IN_PROGRESS",
        submission_date=datetime(2026, 9, 5, 9, 30, 0),
        testing_date=datetime(2026, 9, 20, 10, 0, 0),
        applicant_type="Manufacturer",
        manufacturer_name="Bharat Heavy Weighbridges & Sensorics Ltd",
        manufacturer_address="Industrial Area Phase 1, Chandigarh - 160002",
        country_of_origin="India",
        contact_email="typeapproval@bharatweighbridge.in",
        contact_phone="+91 172 265 8899",
        license_number="LM-IND-MFG-CH-3301",
        instrument_type="Pitless Electronic Weighbridge",
        model_name="BHW-Titan-60T",
        serial_number="SN-2026-WB-60T-004",
        year_of_manufacture=2026,
        accuracy_class="Class III",
        max_capacity=60000.0,
        min_capacity=400.0,
        verification_scale_interval_e=20.0,
        scale_interval_d=20.0,
        units="kg",
        n_intervals=3000,
        tare_type="Subtractive",
        max_tare=60000.0,
        temp_range_min=-10.0,
        temp_range_max=50.0,
        power_supply="230V AC 50Hz with 12V Heavy Industrial UPS",
        load_cell_details="6 x Flintec RC3 30t Stainless Steel Canister Load Cells (OIML R60 C3)",
        indicator_details="Stainless Steel IP68 Weight Indicator with Thermal Ticket Printer & Scoreboard",
        software_version="v4.0.2-WB",
        software_checksum="CRC: 0xF728D1B0",
        lab_name="Regional Legal Metrology Verification Center (Field Station)",
        lab_accreditation="NABL ISO/IEC 17025 Accredited",
        lab_temperature=29.0,
        lab_humidity=58.0,
        lab_pressure=1008.5,
        local_gravity_g=9.7803,
        standard_weights_used="Mobile Test Van with 20 tonnes of Calibrated Class M1 Block Weights",
        testing_officer_name="Er. Rajesh Sharma (Senior Metrological Officer)",
        approving_officer_name="Dr. Priya V. Iyer (Director of Legal Metrology)",
        test_data=demo3_test_data,
        evaluation_summary=eval3_summary,
        is_fully_compliant=False, # Testing still in progress
        remarks="Partial observations recorded; environmental testing pending.",
        conditions_of_approval="Model must complete temperature chamber evaluation."
    )
    db.add(eval3)

    db.commit()
    return {"message": "Successfully seeded 3 realistic OIML R 76 evaluation records."}
