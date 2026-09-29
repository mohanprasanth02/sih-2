"""
LabelGuard AI - Legal Metrology Rule Management & Testing Router
Admin can view, configure, version, and test rules against arbitrary payloads.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from services.api.database import get_db
from services.api.models import ComplianceRule, User
from services.api.schemas import RuleTestRequest
from services.api.routers.auth import get_current_user
from rules.legal_metrology.engine import LegalMetrologyComplianceEngine

router = APIRouter(prefix="/rules", tags=["Compliance Rules"])
engine = LegalMetrologyComplianceEngine()

@router.get("")
def list_rules(db: Session = Depends(get_db)):
    rules = db.query(ComplianceRule).filter(ComplianceRule.is_active == True).all()
    return [
        {
            "id": r.id,
            "code": r.code,
            "title": r.title,
            "legal_reference": r.legal_reference,
            "applicable_categories": r.applicable_categories,
            "severity": r.severity,
            "version": r.version,
            "description": r.description,
            "condition": r.condition_json
        }
        for r in rules
    ]

@router.post("/test")
def test_rules_playground(
    data: RuleTestRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Rule Testing Tool:
    Allows administrators and inspectors to enter arbitrary field values and evaluate
    how the Legal Metrology rule engine evaluates them deterministically.
    """
    # Format input fields into engine structure
    formatted_fields = {}
    for k, v in data.fields.items():
        if isinstance(v, dict):
            formatted_fields[k] = v
        else:
            formatted_fields[k] = {
                "value": v if v else None,
                "confidence": 0.95 if v else 0.0,
                "status": "DETECTED" if v else "NOT_DETECTED",
                "bbox": [100, 100, 200, 300] if v else None
            }

    evaluation = engine.evaluate(
        category_code=data.category_code,
        fields=formatted_fields,
        conflicts=data.conflicts or [],
        quality_status="SUFFICIENT"
    )

    return {
        "input_category": data.category_code,
        "input_fields": data.fields,
        "overall_status": evaluation["overall_status"],
        "summary": evaluation["summary"],
        "evaluated_rules": evaluation["rule_results"]
    }
