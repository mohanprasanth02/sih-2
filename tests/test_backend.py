"""
LabelGuard AI - Comprehensive Backend & Rule Engine Test Suite
Tests authentication, Legal Metrology rule validation, conflict detection, and PDF generation.
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.api.main import app
from packages.validation.legal_metrology import (
    validate_net_quantity, validate_mrp_declaration, validate_unit_sale_price
)
from rules.legal_metrology.engine import LegalMetrologyComplianceEngine
from services.ai.cross_image import PackageConsistencyDetector
from reports.generator import PDFReportGenerator

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["database"] == "CONNECTED"

def test_auth_login_inspector():
    response = client.post("/api/v1/auth/login", json={
        "email": "inspector@legalmetrology.gov.in",
        "password": "Inspector@123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "inspector"

def test_auth_bad_password():
    response = client.post("/api/v1/auth/login", json={
        "email": "inspector@legalmetrology.gov.in",
        "password": "WrongPassword!999"
    })
    assert response.status_code == 401

def test_validation_net_quantity_standard_units():
    valid, msg, parsed = validate_net_quantity("500 g")
    assert valid is True
    assert parsed["numeric_value"] == 500.0
    assert parsed["unit"] == "g"

    valid2, msg2, parsed2 = validate_net_quantity("1.5 kg")
    assert valid2 is True
    assert parsed2["numeric_value"] == 1.5

def test_validation_net_quantity_prohibited_units():
    # 'gms' or 'ltrs' is non-standard and prohibited under Rule 11
    valid, msg, parsed = validate_net_quantity("500 gms")
    assert valid is False
    assert "Non-standard unit 'gms' detected" in msg

def test_validation_mrp_statutory_taxes():
    # Valid with taxes clause
    valid, msg, parsed = validate_mrp_declaration("MRP Rs. 99.00 incl. of all taxes")
    assert valid is True
    assert parsed["price"] == 99.0

    # Non-compliant when taxes clause is absent
    valid2, msg2, parsed2 = validate_mrp_declaration("MRP Rs. 99.00")
    assert valid2 is False
    assert "inclusive of all taxes" in msg2

def test_validation_unit_sale_price():
    net_qty = {"numeric_value": 200, "unit": "g"}
    mrp = {"price": 40.0}
    # Expected USP: 40 / 200 = 0.20 per g
    valid, msg, parsed = validate_unit_sale_price(net_qty, mrp, "₹0.20 per g")
    assert valid is True

    # Mismatched declared USP
    valid_bad, msg_bad, _ = validate_unit_sale_price(net_qty, mrp, "₹0.50 per g")
    assert valid_bad is False
    assert "does not match calculated USP" in msg_bad

def test_cross_image_conflict_detector():
    detector = PackageConsistencyDetector()
    surface_fields = {
        "front": {
            "net_quantity": {"value": "500 g"},
            "mrp": {"value": "₹100"}
        },
        "back": {
            "net_quantity": {"value": "450 g"}, # Conflict!
            "mrp": {"value": "₹100"}
        }
    }
    conflicts = detector.detect_conflicts(surface_fields)
    assert len(conflicts) == 1
    assert conflicts[0]["field_name"] == "net_quantity"
    assert conflicts[0]["value_a"] == "500 g"
    assert conflicts[0]["value_b"] == "450 g"

def test_compliance_rule_engine_deterministic():
    engine = LegalMetrologyComplianceEngine()
    fields = {
        "product_name": {"value": "Parle-G Glucose Biscuits", "confidence": 0.98, "status": "DETECTED"},
        "manufacturer_packer": {"value": "Parle Products Pvt Ltd, Mumbai, Maharashtra", "confidence": 0.95, "status": "DETECTED"},
        "net_quantity": {"value": "800 g", "confidence": 0.97, "status": "DETECTED"},
        "mrp": {"value": "MRP Rs. 40.00 incl. of all taxes", "confidence": 0.96, "status": "DETECTED"},
        "unit_sale_price": {"value": "₹0.05 per g", "confidence": 0.92, "status": "DETECTED"},
        "mfg_packing_date": {"value": "PKD 08/2026", "confidence": 0.94, "status": "DETECTED"},
        "consumer_care": {"value": "Consumer Helpline: 1800-222-211 feedback@parle.biz", "confidence": 0.95, "status": "DETECTED"}
    }
    res = engine.evaluate(category_code="food", fields=fields, conflicts=[])
    assert res["overall_status"] == "COMPLIANT"
    assert res["summary"]["fail"] == 0

def test_pdf_report_generator():
    generator = PDFReportGenerator(output_dir="reports/generated")
    sample_data = {
        "id": "LG-TEST-001",
        "product_name": "Test Package Product",
        "inspector_name": "Rajesh Sharma",
        "category": "Food",
        "status": "COMPLIANT",
        "created_at": "2026-09-09 20:00:00 UTC",
        "extracted_fields": [
            {"field_name": "product_name", "detected_value": "Test Biscuit", "confidence": 0.99, "status": "DETECTED"},
            {"field_name": "net_quantity", "detected_value": "100 g", "confidence": 0.98, "status": "DETECTED"}
        ],
        "rule_results": [
            {"rule_code": "LM-RULE-001", "legal_reference": "Rule 6(1)(a)", "title": "Commodity Name", "status": "PASS", "reason": "Declared"}
        ]
    }
    pdf_file = generator.generate_inspection_report(sample_data, "test_report.pdf")
    assert os.path.exists(pdf_file)
    assert os.path.getsize(pdf_file) > 1000
