"""
Unit & Integration Tests for OIML R 76 NAWI Model Approval System
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.api.main import app
from rules.oiml_r76 import (
    AccuracyClass,
    normalize_class,
    calculate_verification_scale_intervals,
    validate_scale_intervals,
    get_mpe_in_e,
    calculate_raw_error,
    calculate_corrected_error,
    evaluate_weighing_test,
    evaluate_repeatability_test,
    evaluate_eccentricity_test,
    evaluate_tare_and_zero_test,
    evaluate_discrimination_test,
    evaluate_complete_oiml_r76_evaluation
)
from reports.oiml_pdf_generator import OIMLPDFReportGenerator
from reports.oiml_docx_generator import OIMLDocxReportGenerator


client = TestClient(app)


def test_oiml_class_normalization_and_intervals():
    assert normalize_class("Class III") == AccuracyClass.CLASS_III
    assert normalize_class("class 3") == AccuracyClass.CLASS_III
    assert normalize_class("Class II") == AccuracyClass.CLASS_II
    assert normalize_class("Class I") == AccuracyClass.CLASS_I
    assert normalize_class("Class IIII") == AccuracyClass.CLASS_IIII

    # Verification scale intervals n = Max / e
    n = calculate_verification_scale_intervals(15.0, 0.005)
    assert n == 3000
    valid, msg = validate_scale_intervals(AccuracyClass.CLASS_III, n)
    assert valid is True
    assert "3000" in msg

    # Class III max n is 10,000. 15,000 should fail
    valid_fail, msg_fail = validate_scale_intervals(AccuracyClass.CLASS_III, 15000)
    assert valid_fail is False


def test_oiml_mpe_steps():
    # Class III:
    # 0 <= m <= 500 e -> 0.5 e
    # 500 e < m <= 2000 e -> 1.0 e
    # 2000 e < m <= 10000 e -> 1.5 e
    e = 0.005
    assert get_mpe_in_e(AccuracyClass.CLASS_III, 0.1, e) == 0.5 # 20 e
    assert get_mpe_in_e(AccuracyClass.CLASS_III, 2.5, e) == 0.5 # 500 e
    assert get_mpe_in_e(AccuracyClass.CLASS_III, 5.0, e) == 1.0 # 1000 e
    assert get_mpe_in_e(AccuracyClass.CLASS_III, 15.0, e) == 1.5 # 3000 e

    # In service verification doubles MPE
    assert get_mpe_in_e(AccuracyClass.CLASS_III, 15.0, e, in_service=True) == 3.0


def test_oiml_error_calculations():
    # Direct indication error
    raw = calculate_raw_error(indication_i=10.000, load_l=10.000)
    assert raw == 0.0

    # Flash point changeover: E = I + 0.5 e - delta_L - L
    # If e = 0.005, delta_L = 0.0025, I = 10.0, L = 10.0:
    # E = 10.0 + 0.0025 - 0.0025 - 10.0 = 0.0
    flash_err = calculate_raw_error(indication_i=10.0, load_l=10.0, delta_l=0.0025, e=0.005)
    assert flash_err == 0.0

    # Corrected error: Ec = E - E0
    ec = calculate_corrected_error(0.002, 0.001)
    assert ec == 0.001


def test_weighing_test_evaluation():
    e = 0.005
    readings = [
        {"load": 0.0, "direction": "INCR", "indication": 0.0, "delta_l": 0.0025},
        {"load": 5.0, "direction": "INCR", "indication": 5.0, "delta_l": 0.0025},
        {"load": 15.0, "direction": "INCR", "indication": 15.0, "delta_l": 0.0025},
        {"load": 5.0, "direction": "DECR", "indication": 5.0, "delta_l": 0.0025},
        {"load": 0.0, "direction": "DECR", "indication": 0.0, "delta_l": 0.0025},
    ]
    res = evaluate_weighing_test(AccuracyClass.CLASS_III, e, readings)
    assert res["overall_status"] == "PASS"
    assert len(res["readings"]) == 5
    assert res["readings"][3]["hysteresis_status"] == "PASS"


def test_repeatability_and_eccentricity():
    e = 0.005
    # Repeatability: readings within MPE (for Class III at 15kg / 3000e, MPE is 1.5e = 0.0075)
    rep_levels = [
        {"load": 15.0, "readings": [15.000, 15.005, 15.000, 15.000, 15.005]}
    ]
    rep_res = evaluate_repeatability_test(AccuracyClass.CLASS_III, e, rep_levels)
    assert rep_res["overall_status"] == "PASS"

    # Eccentricity: at 5kg (1000e), MPE is 1.0e = 0.0050
    positions = [
        {"position": "Center", "indication": 5.000, "delta_l": 0.0025},
        {"position": "Front-Left", "indication": 5.000, "delta_l": 0.0025},
        {"position": "Rear-Right", "indication": 5.000, "delta_l": 0.0025},
    ]
    ecc_res = evaluate_eccentricity_test(AccuracyClass.CLASS_III, e, 5.0, positions)
    assert ecc_res["overall_status"] == "PASS"


def test_pdf_and_docx_report_generators(tmp_path):
    eval_sample = {
        "report_number": "TEST-REP-001",
        "application_number": "TEST-APP-001",
        "status": "APPROVED_COMPLIANT",
        "manufacturer_name": "Test Manufacturer Ltd",
        "manufacturer_address": "Test Industrial Area",
        "instrument_type": "Electronic Platform Scale",
        "model_name": "Model-X100",
        "accuracy_class": "Class III",
        "max_capacity": 30.0,
        "min_capacity": 0.2,
        "verification_scale_interval_e": 0.01,
        "scale_interval_d": 0.01,
        "units": "kg",
        "n_intervals": 3000,
        "is_fully_compliant": True,
        "evaluation_summary": {
            "test_summaries": {
                "weighing_test": {
                    "readings": [
                        {
                            "index": 1,
                            "direction": "INCR",
                            "load": 10.0,
                            "indication": 10.0,
                            "delta_l": 0.005,
                            "corrected_error": 0.0,
                            "corrected_error_e": 0.0,
                            "mpe_e": 1.0,
                            "mpe_unit": 0.01,
                            "status": "PASS"
                        }
                    ]
                }
            }
        }
    }

    # Test PDF generation
    pdf_gen = OIMLPDFReportGenerator(output_dir=str(tmp_path))
    pdf_file = pdf_gen.generate_report(eval_sample, "test_out.pdf")
    assert os.path.exists(pdf_file)
    assert os.path.getsize(pdf_file) > 1000

    # Test DOCX generation
    docx_gen = OIMLDocxReportGenerator(output_dir=str(tmp_path))
    docx_file = docx_gen.generate_report(eval_sample, "test_out.docx")
    assert os.path.exists(docx_file)
    assert os.path.getsize(docx_file) > 1000


def test_oiml_api_endpoints():
    # 1. Standards endpoint
    r_std = client.get("/api/v1/oiml/standards")
    assert r_std.status_code == 200
    data = r_std.json()
    assert "active_standard" in data
    assert data["active_standard"]["standard_code"] == "OIML R 76-1:2006"

    # 2. Fast calculation endpoint
    calc_payload = {
        "accuracy_class": "Class III",
        "max_capacity": 15.0,
        "min_capacity": 0.1,
        "verification_scale_interval_e": 0.005,
        "scale_interval_d": 0.005,
        "test_data": {
            "weighing_test": [
                {"load": 0.0, "direction": "INCR", "indication": 0.0, "delta_l": 0.0025},
                {"load": 15.0, "direction": "INCR", "indication": 15.0, "delta_l": 0.0025},
            ]
        }
    }
    r_calc = client.post("/api/v1/oiml/calculate", json=calc_payload)
    assert r_calc.status_code == 200
    c_data = r_calc.json()
    assert c_data["n_intervals"] == 3000
    assert c_data["n_validation"]["is_valid"] is True
    assert c_data["is_fully_compliant"] is True

    # 3. Seed demo records
    r_seed = client.post("/api/v1/oiml/seed-demo")
    assert r_seed.status_code == 200

    # 4. List evaluations
    r_list = client.get("/api/v1/oiml/evaluations")
    assert r_list.status_code == 200
    evals = r_list.json()
    assert len(evals) >= 3

    target_id = evals[0]["id"]

    # 5. Get evaluation by ID
    r_get = client.get(f"/api/v1/oiml/evaluations/{target_id}")
    assert r_get.status_code == 200
    assert r_get.json()["id"] == target_id

    # 6. Dashboard stats
    r_stats = client.get("/api/v1/oiml/dashboard-stats")
    assert r_stats.status_code == 200
    stats = r_stats.json()
    assert stats["total_evaluations"] >= 3
    assert stats["approved_compliant"] >= 1

    # 7. Digital signature
    sig_payload = {
        "officer_name": "Er. Rajesh Sharma",
        "designation": "Senior Metrological Officer",
        "pin_or_token": "GOV-LM-2026",
        "signature_remarks": "Test verified and approved"
    }
    r_sig = client.post(f"/api/v1/oiml/evaluations/{target_id}/sign", json=sig_payload)
    assert r_sig.status_code == 200
    assert r_sig.json()["digital_signature"]["status"] == "VERIFIED_AUTHENTIC"

    # 8. Export PDF
    r_pdf = client.get(f"/api/v1/oiml/evaluations/{target_id}/export/pdf")
    assert r_pdf.status_code == 200
    assert r_pdf.headers["content-type"] == "application/pdf"

    # 9. Export DOCX
    r_docx = client.get(f"/api/v1/oiml/evaluations/{target_id}/export/docx")
    assert r_docx.status_code == 200
    assert "officedocument" in r_docx.headers["content-type"]
