"""
LabelGuard AI - Inspection Management Router
Full lifecycle: Creation, Image Ingestion, AI Processing, Field Correction, Verification & Reporting.
"""
import os
import uuid
import shutil
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from services.api.database import get_db
from services.api.models import (
    Inspection, InspectionImage, ExtractedField, RuleResult, ConflictItem,
    InspectionReport, AuditLog, User
)
from services.api.schemas import InspectionCreate, FieldCorrectionRequest, VerificationRequest
from services.api.routers.auth import get_current_user
from services.api.routers.websocket import manager
from services.ai.orchestrator import AIOrchestrator
from services.ai.quality import OpenCVQualityProvider
from reports.generator import PDFReportGenerator

router = APIRouter(prefix="/inspections", tags=["Inspections"])
orchestrator = AIOrchestrator()
quality_checker = OpenCVQualityProvider()
report_gen = PDFReportGenerator()

UPLOAD_DIR = "uploads/inspections"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("")
def list_inspections(
    status: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Inspection)

    # Role check: field inspector sees own inspections, supervisor/admin sees all
    if current_user.role == "inspector":
        # allow inspector to see own or seeded demo items
        query = query.filter((Inspection.inspector_id == current_user.id) | (Inspection.is_demo == True))

    if status and status != "ALL":
        query = query.filter(Inspection.status == status)
    if category and category != "ALL":
        query = query.filter(Inspection.category_code == category)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (Inspection.id.ilike(search_fmt)) |
            (Inspection.product_name.ilike(search_fmt)) |
            (Inspection.brand.ilike(search_fmt))
        )

    total = query.count()
    inspections = query.order_by(desc(Inspection.created_at)).offset(offset).limit(limit).all()

    items = []
    for insp in inspections:
        items.append({
            "id": insp.id,
            "product_name": insp.product_name,
            "brand": insp.brand,
            "category_code": insp.category_code,
            "status": insp.status,
            "created_at": insp.created_at.isoformat() if insp.created_at else None,
            "address": insp.address,
            "is_demo": insp.is_demo,
            "image_count": len(insp.images),
            "findings_count": len(insp.rule_results),
            "conflicts_count": len(insp.conflicts)
        })

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items
    }

@router.post("")
def create_inspection(
    data: InspectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    now = datetime.now(timezone.utc)
    random_suffix = str(uuid.uuid4().int)[:6]
    generated_id = f"LG-{now.strftime('%Y-%m')}-{random_suffix}"

    inspection = Inspection(
        id=generated_id,
        inspector_id=current_user.id,
        product_name=data.product_name,
        brand=data.brand,
        category_code=data.category_code,
        status="PENDING",
        latitude=data.latitude,
        longitude=data.longitude,
        address=data.address,
        is_demo=False,
        created_at=now,
        updated_at=now
    )
    db.add(inspection)
    
    # Add audit log
    audit = AuditLog(
        entity_type="inspection",
        entity_id=generated_id,
        user_id=current_user.id,
        action="CREATED",
        new_state={"product_name": data.product_name, "category": data.category_code}
    )
    db.add(audit)
    db.commit()
    db.refresh(inspection)

    return {
        "id": inspection.id,
        "product_name": inspection.product_name,
        "status": inspection.status,
        "category_code": inspection.category_code,
        "created_at": inspection.created_at.isoformat()
    }

@router.get("/{inspection_id}")
def get_inspection_details(
    inspection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    insp = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection record not found")

    images_data = []
    for img in insp.images:
        images_data.append({
            "id": img.id,
            "surface_type": img.surface_type,
            "file_path": img.file_path,
            "url": f"/static/{os.path.basename(img.file_path)}",
            "blur_score": img.blur_score,
            "brightness_score": img.brightness_score,
            "quality_status": img.quality_status,
            "quality_notes": img.quality_notes,
            "width": img.width,
            "height": img.height
        })

    fields_data = []
    for f in insp.extracted_fields:
        fields_data.append({
            "id": f.id,
            "field_name": f.field_name,
            "detected_value": f.detected_value,
            "corrected_value": f.corrected_value,
            "effective_value": f.corrected_value if f.is_corrected else f.detected_value,
            "confidence": f.confidence,
            "bbox": f.bbox,
            "status": f.status,
            "is_corrected": f.is_corrected,
            "correction_reason": f.correction_reason,
            "image_id": f.image_id
        })

    rules_data = []
    for r in insp.rule_results:
        rules_data.append({
            "id": r.id,
            "rule_code": r.rule_code,
            "title": r.title,
            "legal_reference": r.legal_reference,
            "status": r.status,
            "severity": r.severity,
            "reason": r.reason,
            "confidence": r.confidence,
            "evidence_crops": r.evidence_crops
        })

    conflicts_data = []
    for c in insp.conflicts:
        conflicts_data.append({
            "id": c.id,
            "field_name": c.field_name,
            "surface_a": c.surface_a,
            "value_a": c.value_a,
            "surface_b": c.surface_b,
            "value_b": c.value_b,
            "reason": c.reason
        })

    audits_data = []
    audit_records = db.query(AuditLog).filter(AuditLog.entity_id == inspection_id).order_by(desc(AuditLog.timestamp)).all()
    for a in audit_records:
        audits_data.append({
            "id": a.id,
            "action": a.action,
            "timestamp": a.timestamp.isoformat() if a.timestamp else None,
            "old_state": a.old_state,
            "new_state": a.new_state
        })

    return {
        "id": insp.id,
        "product_name": insp.product_name,
        "brand": insp.brand,
        "category_code": insp.category_code,
        "status": insp.status,
        "latitude": insp.latitude,
        "longitude": insp.longitude,
        "address": insp.address,
        "is_demo": insp.is_demo,
        "supervisor_notes": insp.supervisor_notes,
        "created_at": insp.created_at.isoformat() if insp.created_at else None,
        "images": images_data,
        "extracted_fields": fields_data,
        "rule_results": rules_data,
        "conflicts": conflicts_data,
        "audit_logs": audits_data
    }

@router.post("/{inspection_id}/images")
async def upload_inspection_image(
    inspection_id: str,
    surface_type: str = Form("front"), # front, back, side_a, side_b, top, bottom
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    insp = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")

    # Validate file type
    valid_exts = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.jfif', '.heic')
    has_img_type = file.content_type and file.content_type.startswith("image/")
    has_img_ext = file.filename and file.filename.lower().endswith(valid_exts)
    if not has_img_type and not has_img_ext:
        raise HTTPException(status_code=400, detail="Only standard image formats (JPEG, PNG, WebP) are accepted")

    file_ext = os.path.splitext(file.filename)[1].lower() if file.filename else ".jpg"
    if not file_ext or file_ext not in valid_exts:
        file_ext = ".jpg"
    safe_filename = f"{inspection_id}_{surface_type}_{uuid.uuid4().hex[:8]}{file_ext}"
    saved_path = os.path.join(UPLOAD_DIR, safe_filename)

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Perform immediate CV quality check
    q_eval = quality_checker.evaluate_quality(saved_path)

    image_record = InspectionImage(
        inspection_id=inspection_id,
        surface_type=surface_type.lower(),
        file_path=saved_path,
        original_filename=file.filename,
        blur_score=q_eval["blur_score"],
        brightness_score=q_eval["brightness_score"],
        quality_status=q_eval["quality_status"],
        quality_notes=q_eval["notes"],
        width=q_eval["width"],
        height=q_eval["height"]
    )
    db.add(image_record)
    db.commit()
    db.refresh(image_record)

    # Broadcast image upload event
    await manager.broadcast_event(inspection_id, {
        "event": "IMAGE_RECEIVED",
        "inspection_id": inspection_id,
        "message": f"Surface '{surface_type}' uploaded successfully. Quality: {q_eval['quality_status']}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": {
            "image_id": image_record.id,
            "surface_type": surface_type,
            "quality": q_eval
        }
    })

    return {
        "id": image_record.id,
        "surface_type": image_record.surface_type,
        "quality_status": image_record.quality_status,
        "quality_notes": image_record.quality_notes,
        "blur_score": image_record.blur_score,
        "brightness_score": image_record.brightness_score,
        "file_path": image_record.file_path
    }

@router.post("/{inspection_id}/analyze")
async def trigger_inspection_analysis(
    inspection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    insp = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")

    images = insp.images
    if not images:
        raise HTTPException(status_code=400, detail="Please upload at least one package surface image before running analysis")

    insp.status = "PROCESSING"
    db.commit()

    images_payload = [
        {
            "id": img.id,
            "file_path": img.file_path,
            "surface_type": img.surface_type
        }
        for img in images
    ]

    async def ws_callback(event: str, message: str, payload: dict):
        await manager.broadcast_event(inspection_id, {
            "event": event,
            "inspection_id": inspection_id,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload
        })

    # Run AI pipeline
    pipeline_result = await orchestrator.run_pipeline(
        inspection_id=inspection_id,
        category_code=insp.category_code,
        images_info=images_payload,
        progress_callback=ws_callback
    )

    # Clear previous results if re-analyzing
    db.query(ExtractedField).filter(ExtractedField.inspection_id == inspection_id).delete()
    db.query(RuleResult).filter(RuleResult.inspection_id == inspection_id).delete()
    db.query(ConflictItem).filter(ConflictItem.inspection_id == inspection_id).delete()

    # Persist extracted fields
    for f_name, f_info in pipeline_result["extracted_fields"].items():
        db.add(ExtractedField(
            inspection_id=inspection_id,
            image_id=f_info.get("image_id"),
            field_name=f_name,
            detected_value=f_info.get("value"),
            confidence=f_info.get("confidence", 0.0),
            bbox=f_info.get("bbox"),
            status=f_info.get("status", "DETECTED")
        ))

    # Persist rule results
    for r in pipeline_result["rule_results"]:
        db.add(RuleResult(
            inspection_id=inspection_id,
            rule_code=r["rule_code"],
            title=r["title"],
            legal_reference=r["legal_reference"],
            severity=r["severity"],
            status=r["status"],
            reason=r["reason"],
            confidence=r["confidence"],
            evidence_crops=r.get("evidence_crops", [])
        ))

    # Persist conflicts
    for c in pipeline_result["conflicts"]:
        db.add(ConflictItem(
            inspection_id=inspection_id,
            field_name=c["field_name"],
            surface_a=c["surface_a"],
            value_a=c["value_a"],
            surface_b=c["surface_b"],
            value_b=c["value_b"],
            reason=c["reason"]
        ))

    insp.status = pipeline_result["overall_status"]
    
    # Auto-update generic commodity title with real AI-detected product name
    detected_pname = pipeline_result["extracted_fields"].get("product_name", {}).get("value")
    if detected_pname and (insp.product_name in ["Packaged Commodity", "Scanned Packaged Commodity", ""] or not insp.product_name):
        insp.product_name = detected_pname

    insp.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "status": insp.status,
        "summary": pipeline_result["summary"],
        "conflicts_count": len(pipeline_result["conflicts"])
    }

@router.patch("/{inspection_id}/fields/{field_id}")
def correct_field_value(
    inspection_id: str,
    field_id: str,
    data: FieldCorrectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    field = db.query(ExtractedField).filter(
        ExtractedField.id == field_id,
        ExtractedField.inspection_id == inspection_id
    ).first()
    if not field:
        raise HTTPException(status_code=404, detail="Extracted declaration not found")

    old_val = field.corrected_value if field.is_corrected else field.detected_value
    field.corrected_value = data.corrected_value
    field.is_corrected = True
    field.corrected_by = current_user.id
    field.correction_reason = data.reason

    # Audit Trail Entry
    audit = AuditLog(
        entity_type="extracted_field",
        entity_id=field_id,
        user_id=current_user.id,
        action="EDITED_FIELD",
        old_state={"field": field.field_name, "value": old_val},
        new_state={"field": field.field_name, "value": data.corrected_value, "reason": data.reason}
    )
    db.add(audit)
    db.commit()

    return {
        "id": field.id,
        "field_name": field.field_name,
        "original_value": field.detected_value,
        "corrected_value": field.corrected_value,
        "is_corrected": True,
        "reason": field.correction_reason
    }

@router.post("/{inspection_id}/verify")
def finalize_verification(
    inspection_id: str,
    data: VerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    insp = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")

    old_status = insp.status
    insp.status = data.decision
    if data.notes:
        insp.supervisor_notes = data.notes

    audit = AuditLog(
        entity_type="inspection",
        entity_id=inspection_id,
        user_id=current_user.id,
        action="OFFICIAL_VERIFICATION",
        old_state={"status": old_status},
        new_state={"status": data.decision, "notes": data.notes}
    )
    db.add(audit)
    db.commit()

    return {
        "inspection_id": inspection_id,
        "status": insp.status,
        "notes": insp.supervisor_notes
    }

@router.post("/{inspection_id}/reports")
def generate_pdf_report_endpoint(
    inspection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    insp = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")

    # Build report payload
    fields_list = [
        {
            "field_name": f.field_name,
            "detected_value": f.detected_value,
            "effective_value": f.corrected_value if f.is_corrected else f.detected_value,
            "confidence": f.confidence,
            "status": f.status
        }
        for f in insp.extracted_fields
    ]

    rules_list = [
        {
            "rule_code": r.rule_code,
            "title": r.title,
            "legal_reference": r.legal_reference,
            "status": r.status,
            "reason": r.reason
        }
        for r in insp.rule_results
    ]

    conflicts_list = [
        {
            "field_name": c.field_name,
            "surface_a": c.surface_a,
            "value_a": c.value_a,
            "surface_b": c.surface_b,
            "value_b": c.value_b,
            "reason": c.reason
        }
        for c in insp.conflicts
    ]

    report_payload = {
        "id": insp.id,
        "product_name": insp.product_name,
        "inspector_name": current_user.full_name,
        "category": insp.category_code,
        "status": insp.status,
        "created_at": insp.created_at.strftime("%Y-%m-%d %H:%M:%S UTC") if insp.created_at else None,
        "location": {"address": insp.address or "Inspection Site"},
        "extracted_fields": fields_list,
        "rule_results": rules_list,
        "conflicts": conflicts_list
    }

    pdf_path = report_gen.generate_inspection_report(report_payload)

    report_record = InspectionReport(
        inspection_id=inspection_id,
        file_path=pdf_path,
        format="PDF",
        generated_by=current_user.id
    )
    db.add(report_record)
    db.commit()
    db.refresh(report_record)

    return {
        "report_id": report_record.id,
        "inspection_id": inspection_id,
        "file_path": pdf_path,
        "download_url": f"/api/v1/inspections/{inspection_id}/reports/{report_record.id}/download"
    }

@router.get("/{inspection_id}/reports/{report_id}/download")
def download_pdf_report(
    inspection_id: str,
    report_id: str,
    db: Session = Depends(get_db)
):
    report = db.query(InspectionReport).filter(
        InspectionReport.id == report_id,
        InspectionReport.inspection_id == inspection_id
    ).first()
    if not report or not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        report.file_path,
        media_type="application/pdf",
        filename=f"{inspection_id}_Legal_Metrology_Report.pdf"
    )
