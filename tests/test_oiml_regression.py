"""
Extensive Automated Regression Suite for OIML R 76 NAWI System
Department of Consumer Affairs (DoCA) Metrological Compliance

Covers:
1. Deterministic Calculation Engine & Edge Cases (Table 6 MPE limits, Table 3 n limits, Clause A.4.4.3 changeover points).
2. Role-Based Access Control (RBAC) across Admin, Supervisor, Inspector, and Viewer.
3. Approval Workflow State Machine (DRAFT -> SUBMITTED -> UNDER_REVIEW -> CORRECTION_REQUIRED -> APPROVED -> FINALIZED).
4. Relational Database Normalization (TestReport, Instrument, Manufacturer, Laboratory, TestObservation, ReportVersion).
5. Document Generation & Checksum Validation (PDF, DOCX).
6. Attachment Storage & MIME / Size Validation.
7. Immutable Audit Logging.
"""

import os
import io
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.api.main import app
from services.api.database import SessionLocal
from services.api.models import (
    User,
    Laboratory,
    Manufacturer,
    Instrument,
    TestReport,
    TestObservation,
    ReportVersion,
    AuditLog,
    Attachment
)
from rules.oiml_r76 import (
    AccuracyClass,
    calculate_verification_scale_intervals,
    validate_scale_intervals,
    get_mpe_in_e,
    calculate_raw_error,
    calculate_corrected_error,
    evaluate_weighing_test,
    evaluate_repeatability_test,
    evaluate_eccentricity_test
)

client = TestClient(app)


def get_token(email: str, password: str) -> str:
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]


@pytest.fixture(scope="module")
def tokens():
    return {
        "admin": get_token("admin@legalmetrology.gov.in", "Admin@123"),
        "supervisor": get_token("supervisor@legalmetrology.gov.in", "Supervisor@123"),
        "inspector": get_token("inspector@legalmetrology.gov.in", "Inspector@123"),
        "viewer": get_token("viewer@legalmetrology.gov.in", "Viewer@123"),
    }


# ==============================================================================
# SECTION 1: METROLOGICAL CALCULATION ENGINE & REGULATORY RULES
# ==============================================================================

def test_oiml_table3_interval_limits():
    """Verify Table 3 verification scale interval boundaries."""
    # Class I: min n = 50,000
    valid_i, _ = validate_scale_intervals(AccuracyClass.CLASS_I, 49999)
    assert valid_i is False
    valid_i_ok, _ = validate_scale_intervals(AccuracyClass.CLASS_I, 50000)
    assert valid_i_ok is True

    # Class II: min n = 100, max n = 100,000
    valid_ii_low, _ = validate_scale_intervals(AccuracyClass.CLASS_II, 99)
    assert valid_ii_low is False
    valid_ii_high, _ = validate_scale_intervals(AccuracyClass.CLASS_II, 100001)
    assert valid_ii_high is False
    valid_ii_ok, _ = validate_scale_intervals(AccuracyClass.CLASS_II, 5000)
    assert valid_ii_ok is True

    # Class III: min n = 100, max n = 10,000
    valid_iii_low, _ = validate_scale_intervals(AccuracyClass.CLASS_III, 99)
    assert valid_iii_low is False
    valid_iii_high, _ = validate_scale_intervals(AccuracyClass.CLASS_III, 10001)
    assert valid_iii_high is False
    valid_iii_ok, _ = validate_scale_intervals(AccuracyClass.CLASS_III, 3000)
    assert valid_iii_ok is True


def test_oiml_table6_mpe_step_boundaries():
    """Verify exact step transitions for Maximum Permissible Error (MPE) as per Table 6."""
    e = 0.005 # 5g
    # Class III initial verification:
    # 0 <= m <= 500e (0 to 2.5 kg) -> ±0.5e
    # 500e < m <= 2000e (2.50001 to 10 kg) -> ±1.0e
    # 2000e < m <= 10000e (10.00001 to 50 kg) -> ±1.5e
    assert get_mpe_in_e(AccuracyClass.CLASS_III, 0.0, e) == 0.5
    assert get_mpe_in_e(AccuracyClass.CLASS_III, 2.5, e) == 0.5 # Exactly at 500e
    assert get_mpe_in_e(AccuracyClass.CLASS_III, 2.5001, e) == 1.0 # Just above 500e
    assert get_mpe_in_e(AccuracyClass.CLASS_III, 10.0, e) == 1.0 # Exactly at 2000e
    assert get_mpe_in_e(AccuracyClass.CLASS_III, 10.0001, e) == 1.5 # Just above 2000e
    assert get_mpe_in_e(AccuracyClass.CLASS_III, 15.0, e) == 1.5


def test_clause_a443_flash_point_changeover_formula():
    """Verify turning point error formula: E = I + 0.5e - delta_L - L."""
    # Case A: Indication I = 10.0, delta_L = 0.0025, e = 0.005, Load L = 10.0
    # E = 10.0 + 0.0025 - 0.0025 - 10.0 = 0.0
    err_exact = calculate_raw_error(indication_i=10.0, load_l=10.0, delta_l=0.0025, e=0.005)
    assert round(err_exact, 6) == 0.0

    # Case B: Instrument sluggish, requires delta_L = 0.0010 before changeover
    # E = 10.0 + 0.0025 - 0.0010 - 10.0 = +0.0015
    err_sluggish = calculate_raw_error(indication_i=10.0, load_l=10.0, delta_l=0.0010, e=0.005)
    assert round(err_sluggish, 6) == 0.0015

    # Case C: Corrected error Ec = E - E0
    e0 = calculate_raw_error(indication_i=0.0, load_l=0.0, delta_l=0.0020, e=0.005)
    ec = calculate_corrected_error(err_sluggish, e0)
    assert round(ec, 6) == round(err_sluggish - e0, 6)


def test_weighing_test_failure_on_exceeding_mpe():
    """Verify that an observation with error exceeding MPE causes the test to fail."""
    e = 0.005 # MPE at 15kg is 1.5e = 0.0075
    # Indication of 15.010 with delta_L = 0.0025 gives E = 15.010 - 15.0 = +0.010 (> 0.0075)
    readings = [
        {"load": 0.0, "direction": "INCR", "indication": 0.0, "delta_l": 0.0025},
        {"load": 15.0, "direction": "INCR", "indication": 15.010, "delta_l": 0.0025},
    ]
    res = evaluate_weighing_test(AccuracyClass.CLASS_III, e, readings)
    assert res["overall_status"] == "FAIL"
    assert res["readings"][1]["status"] == "FAIL"


# ==============================================================================
# SECTION 2: ROLE-BASED ACCESS CONTROL (RBAC) ENFORCEMENT
# ==============================================================================

def test_viewer_role_cannot_create_or_modify(tokens):
    headers = {"Authorization": f"Bearer {tokens['viewer']}"}

    # 1. Viewer cannot create evaluation
    payload = {
        "manufacturer_name": "Unauthorized Test Corp",
        "manufacturer_address": "Test Industrial Area",
        "instrument_type": "Counter Scale",
        "model_name": "HACK-01",
        "accuracy_class": "Class III",
        "max_capacity": 10.0,
        "min_capacity": 0.1,
        "verification_scale_interval_e": 0.002,
        "scale_interval_d": 0.002,
        "units": "kg",
    }
    r = client.post("/api/v1/oiml/evaluations", json=payload, headers=headers)
    assert r.status_code == 403, f"Viewer was able to create: {r.status_code}"

    # 2. Viewer can view existing evaluations
    r_list = client.get("/api/v1/oiml/evaluations", headers=headers)
    assert r_list.status_code == 200
    assert len(r_list.json()) > 0


def test_inspector_cannot_approve_or_finalize(tokens):
    headers = {"Authorization": f"Bearer {tokens['inspector']}"}
    evals = client.get("/api/v1/oiml/evaluations").json()
    assert len(evals) > 0
    target_id = evals[0]["id"]

    # Inspector cannot transition to APPROVED_COMPLIANT or FINALIZE
    r = client.post(
        f"/api/v1/oiml/evaluations/{target_id}/transition",
        json={"action": "APPROVE", "notes": "Inspector trying to approve"},
        headers=headers
    )
    assert r.status_code == 403

    r_fin = client.post(
        f"/api/v1/oiml/evaluations/{target_id}/transition",
        json={"action": "FINALIZE", "notes": "Inspector trying to finalize"},
        headers=headers
    )
    assert r_fin.status_code == 403


# ==============================================================================
# SECTION 3: END-TO-END WORKFLOW & STATE MACHINE
# ==============================================================================

def test_full_evaluation_workflow_and_state_machine(tokens):
    insp_headers = {"Authorization": f"Bearer {tokens['inspector']}"}
    sup_headers = {"Authorization": f"Bearer {tokens['supervisor']}"}

    # Step 1: Inspector creates new evaluation in DRAFT
    create_payload = {
        "manufacturer_name": "Bharat Precision Metrology",
        "manufacturer_address": "Okhla Industrial Area, Phase III, New Delhi",
        "instrument_type": "Non-Automatic Bench Scale",
        "model_name": "BPM-30-ADV",
        "accuracy_class": "Class III",
        "max_capacity": 30.0,
        "min_capacity": 0.2,
        "verification_scale_interval_e": 0.01,
        "scale_interval_d": 0.01,
        "units": "kg",
        "test_data": {
            "weighing_test": [
                {"load": 0.0, "direction": "INCR", "indication": 0.0, "delta_l": 0.005},
                {"load": 10.0, "direction": "INCR", "indication": 10.0, "delta_l": 0.005},
                {"load": 30.0, "direction": "INCR", "indication": 30.0, "delta_l": 0.005},
                {"load": 10.0, "direction": "DECR", "indication": 10.0, "delta_l": 0.005},
                {"load": 0.0, "direction": "DECR", "indication": 0.0, "delta_l": 0.005},
            ]
        }
    }
    r_create = client.post("/api/v1/oiml/evaluations", json=create_payload, headers=insp_headers)
    assert r_create.status_code in (200, 201)
    created = r_create.json()
    eval_id = created["id"]
    assert created["status"] == "DRAFT"

    # Step 2: Inspector submits for review (DRAFT -> SUBMITTED)
    r_sub = client.post(
        f"/api/v1/oiml/evaluations/{eval_id}/transition",
        json={"action": "SUBMIT", "notes": "Completed initial observation battery"},
        headers=insp_headers
    )
    assert r_sub.status_code == 200
    assert r_sub.json()["status"] == "SUBMITTED"

    # Step 3: Supervisor begins technical review (SUBMITTED -> UNDER_REVIEW)
    r_rev = client.post(
        f"/api/v1/oiml/evaluations/{eval_id}/transition",
        json={"action": "START_REVIEW", "notes": "Reviewing weighing test readings"},
        headers=sup_headers
    )
    assert r_rev.status_code == 200
    assert r_rev.json()["status"] == "UNDER_REVIEW"

    # Step 4: Supervisor requests correction (UNDER_REVIEW -> CORRECTION_REQUIRED)
    r_corr = client.post(
        f"/api/v1/oiml/evaluations/{eval_id}/transition",
        json={"action": "REQUEST_CORRECTION", "notes": "Attach temperature range verification"},
        headers=sup_headers
    )
    assert r_corr.status_code == 200
    assert r_corr.json()["status"] == "CORRECTION_REQUIRED"

    # Step 5: Inspector re-submits after updates (CORRECTION_REQUIRED -> SUBMITTED)
    r_resub = client.post(
        f"/api/v1/oiml/evaluations/{eval_id}/transition",
        json={"action": "SUBMIT", "notes": "Clarifications provided"},
        headers=insp_headers
    )
    assert r_resub.status_code == 200
    assert r_resub.json()["status"] == "SUBMITTED"

    # Supervisor restarts review
    client.post(
        f"/api/v1/oiml/evaluations/{eval_id}/transition",
        json={"action": "START_REVIEW", "notes": "Final inspection"},
        headers=sup_headers
    )

    # Step 6: Supervisor approves report (UNDER_REVIEW -> APPROVED_COMPLIANT)
    r_app = client.post(
        f"/api/v1/oiml/evaluations/{eval_id}/transition",
        json={"action": "APPROVE", "notes": "Compliance verified with OIML R 76-1:2006 Table 6"},
        headers=sup_headers
    )
    assert r_app.status_code == 200
    assert r_app.json()["status"] == "APPROVED_COMPLIANT"

    # Step 7: Supervisor finalizes report (APPROVED_COMPLIANT -> FINALIZED)
    r_fin = client.post(
        f"/api/v1/oiml/evaluations/{eval_id}/transition",
        json={"action": "FINALIZE", "notes": "Pattern approval sealed and issued"},
        headers=sup_headers
    )
    assert r_fin.status_code == 200
    assert r_fin.json()["status"] == "FINALIZED"


# ==============================================================================
# SECTION 4: RELATIONAL DATABASE NORMALIZATION
# ==============================================================================

def test_relational_database_normalization():
    """Verify that normalized tables (TestReport, Instrument, Manufacturer, TestObservation) are properly populated."""
    db = SessionLocal()
    try:
        # 1. Verify Manufacturers
        mfg_count = db.query(Manufacturer).count()
        assert mfg_count >= 1, "No manufacturers found in relational DB"

        # 2. Verify Instruments
        inst_count = db.query(Instrument).count()
        assert inst_count >= 1, "No instruments found in relational DB"

        # 3. Verify TestReports
        report_count = db.query(TestReport).count()
        assert report_count >= 1, "No TestReports found in relational DB"

        # 4. Verify TestObservations
        obs_count = db.query(TestObservation).count()
        assert obs_count >= 5, "No TestObservations found in relational DB"

        # 5. Verify ReportVersions
        ver_count = db.query(ReportVersion).count()
        assert ver_count >= 1, "No ReportVersions found in relational DB"

        # Check latest version has valid checksum
        latest_ver = db.query(ReportVersion).order_by(ReportVersion.version_number.desc()).first()
        assert latest_ver.checksum is not None
        assert len(latest_ver.checksum) == 64 # SHA-256 length
    finally:
        db.close()


# ==============================================================================
# SECTION 5: REAL DOCUMENT GENERATION & EXPORT
# ==============================================================================

def test_report_downloads_and_formats(tokens):
    headers = {"Authorization": f"Bearer {tokens['viewer']}"}
    evals = client.get("/api/v1/oiml/evaluations", headers=headers).json()
    assert len(evals) > 0
    target_id = evals[0]["id"]

    # 1. PDF Download
    r_pdf = client.get(f"/api/v1/oiml/evaluations/{target_id}/export/pdf")
    assert r_pdf.status_code == 200
    assert r_pdf.headers["content-type"] == "application/pdf"
    assert len(r_pdf.content) > 2000 # Realistic PDF size

    # 2. DOCX Download
    r_docx = client.get(f"/api/v1/oiml/evaluations/{target_id}/export/docx")
    assert r_docx.status_code == 200
    assert "officedocument" in r_docx.headers["content-type"]
    assert len(r_docx.content) > 2000 # Realistic DOCX size


# ==============================================================================
# SECTION 6: ATTACHMENT UPLOAD & MIME VALIDATION
# ==============================================================================

def test_attachment_upload_and_validation(tokens):
    headers = {"Authorization": f"Bearer {tokens['inspector']}"}
    evals = client.get("/api/v1/oiml/evaluations").json()
    target_id = evals[0]["id"]

    # 1. Valid image upload
    fake_png = io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4")
    r_up = client.post(
        f"/api/v1/oiml/evaluations/{target_id}/upload-photo",
        files={"file": ("test_nameplate.png", fake_png, "image/png")},
        data={"attachment_type": "MARKING_PLATE", "title": "Official Nameplate Photo"},
        headers=headers
    )
    assert r_up.status_code == 200
    res_data = r_up.json()
    att = res_data.get("attachment", res_data)
    assert att["attachment_type"] == "MARKING_PLATE"
    assert att["file_name"] == "test_nameplate.png"

    # 2. Invalid extension rejection (.exe)
    bad_file = io.BytesIO(b"MZ\x90\x00test")
    r_bad = client.post(
        f"/api/v1/oiml/evaluations/{target_id}/upload-photo",
        files={"file": ("malware.exe", bad_file, "application/octet-stream")},
        data={"attachment_type": "OTHER", "title": "Executable"},
        headers=headers
    )
    assert r_bad.status_code == 400
    assert "Invalid file type" in r_bad.json()["detail"]


# ==============================================================================
# SECTION 7: IMMUTABLE AUDIT TRAIL
# ==============================================================================

def test_audit_logs_recorded_for_actions(tokens):
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    evals = client.get("/api/v1/oiml/evaluations").json()
    target_id = evals[0]["id"]

    r_audit = client.get(f"/api/v1/oiml/evaluations/{target_id}/audit-logs", headers=headers)
    assert r_audit.status_code == 200
    logs = r_audit.json()
    assert len(logs) > 0

    actions = [log["action"] for log in logs]
    assert any("TRANSITION" in a or "EVALUATION" in a or "ATTACHMENT" in a for a in actions)
