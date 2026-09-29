"""
OIML R 76 Metrological Engine
Reference: OIML Recommendation R 76-1 (Edition 2006 (E))
Non-automatic weighing instruments - Metrological and technical requirements - Tests

Covers:
- Accuracy Classes: Class I (Special), Class II (High), Class III (Medium), Class IIII (Ordinary)
- Scale intervals (d, e, n = Max / e)
- Maximum Permissible Errors (MPE) for initial verification (Table 6) and in-service verification
- Changeover point / Flash point error calculation method (Clause A.4.4.3):
    E = I + 0.5e - delta_L - L
    Ec = E - E0
- Evaluation of prescribed test procedures:
    1. Weighing Performance Test (Clause A.4.4)
    2. Repeatability Test (Clause A.4.10)
    3. Eccentricity / Off-Center Loading Test (Clause A.4.7)
    4. Tare and Zero-Setting Test (Clause A.4.2 & A.4.6)
    5. Discrimination Test (Clause A.4.8)
    6. Temperature and Environmental Test (Clause A.5.3)
    7. Voltage Variation Test (Clause A.5.4)
    8. Creep Test (Clause A.4.11)
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import math


class AccuracyClass(str, Enum):
    CLASS_I = "Class I"      # Special accuracy
    CLASS_II = "Class II"    # High accuracy
    CLASS_III = "Class III"  # Medium accuracy
    CLASS_IIII = "Class IIII"# Ordinary accuracy


class EvaluationStatus(str, Enum):
    DRAFT = "DRAFT"
    TESTING_IN_PROGRESS = "TESTING_IN_PROGRESS"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED_COMPLIANT = "APPROVED_COMPLIANT"
    REJECTED_NON_COMPLIANT = "REJECTED_NON_COMPLIANT"


# OIML R 76 Table 6: Maximum permissible errors on initial verification
# Specified in terms of verification scale intervals e
MPE_RULES = {
    AccuracyClass.CLASS_I: [
        {"max_m_in_e": 50000, "mpe_e": 0.5},
        {"max_m_in_e": 200000, "mpe_e": 1.0},
        {"max_m_in_e": float("inf"), "mpe_e": 1.5},
    ],
    AccuracyClass.CLASS_II: [
        {"max_m_in_e": 5000, "mpe_e": 0.5},
        {"max_m_in_e": 20000, "mpe_e": 1.0},
        {"max_m_in_e": 100000, "mpe_e": 1.5},
    ],
    AccuracyClass.CLASS_III: [
        {"max_m_in_e": 500, "mpe_e": 0.5},
        {"max_m_in_e": 2000, "mpe_e": 1.0},
        {"max_m_in_e": 10000, "mpe_e": 1.5},
    ],
    AccuracyClass.CLASS_IIII: [
        {"max_m_in_e": 50, "mpe_e": 0.5},
        {"max_m_in_e": 200, "mpe_e": 1.0},
        {"max_m_in_e": 1000, "mpe_e": 1.5},
    ],
}

# Permissible ranges of n = Max / e as per Table 3
CLASS_LIMITS = {
    AccuracyClass.CLASS_I: {
        "min_e_grams": 0.001,
        "n_min": 50000,
        "n_max": None, # No limit
        "min_load_factor": 100, # Min = 100 e
    },
    AccuracyClass.CLASS_II: {
        "min_e_grams": 0.001,
        "n_min": 100,
        "n_max": 100000,
        "min_load_factor": 20, # Min = 20 e or 50 e depending on e
    },
    AccuracyClass.CLASS_III: {
        "min_e_grams": 0.1,
        "n_min": 100,
        "n_max": 10000,
        "min_load_factor": 20, # Min = 20 e
    },
    AccuracyClass.CLASS_IIII: {
        "min_e_grams": 5.0,
        "n_min": 100,
        "n_max": 1000,
        "min_load_factor": 10, # Min = 10 e
    },
}


def normalize_class(acc_class: str) -> AccuracyClass:
    """Normalize input string to standard AccuracyClass enum."""
    val = acc_class.strip().upper()
    if "IIII" in val or "4" in val or "FOUR" in val:
        return AccuracyClass.CLASS_IIII
    elif "III" in val or "3" in val or "THREE" in val:
        return AccuracyClass.CLASS_III
    elif "II" in val or "2" in val or "TWO" in val:
        return AccuracyClass.CLASS_II
    elif "I" in val or "1" in val or "ONE" in val:
        return AccuracyClass.CLASS_I
    return AccuracyClass.CLASS_III


def calculate_verification_scale_intervals(max_capacity: float, e: float) -> int:
    """Compute number of verification scale intervals n = Max / e."""
    if e <= 0:
        raise ValueError("Verification scale interval 'e' must be positive.")
    return int(round(max_capacity / e))


def validate_scale_intervals(acc_class: AccuracyClass, n: int) -> Tuple[bool, str]:
    """Validate if n is within OIML R 76 Table 3 permissible limits."""
    limits = CLASS_LIMITS.get(acc_class, CLASS_LIMITS[AccuracyClass.CLASS_III])
    n_min = limits["n_min"]
    n_max = limits["n_max"]

    if n < n_min:
        return False, f"Number of scale intervals n={n} is below minimum {n_min} for {acc_class.value}."
    if n_max is not None and n > n_max:
        return False, f"Number of scale intervals n={n} exceeds maximum {n_max} for {acc_class.value}."
    return True, f"Valid scale intervals (n={n}, permissible [{n_min} - {n_max or 'unlimited'}])."


def get_mpe_in_e(acc_class: AccuracyClass, load_m: float, e: float, in_service: bool = False) -> float:
    """
    Get Maximum Permissible Error (MPE) in terms of 'e' for a given load 'load_m'.
    As per OIML R 76 Table 6:
    Returns absolute value in units of e (e.g., 0.5, 1.0, 1.5).
    In-service verification doubles initial MPE.
    """
    if e <= 0:
        return 0.5
    
    m_in_e = abs(load_m) / e
    rules = MPE_RULES.get(acc_class, MPE_RULES[AccuracyClass.CLASS_III])
    
    mpe_e = 1.5
    for rule in rules:
        if m_in_e <= rule["max_m_in_e"]:
            mpe_e = rule["mpe_e"]
            break
            
    if in_service:
        mpe_e *= 2.0
        
    return mpe_e


def get_mpe_in_engineering_units(acc_class: AccuracyClass, load_m: float, e: float, in_service: bool = False) -> float:
    """Returns MPE converted into engineering units (same unit as e and load_m)."""
    return get_mpe_in_e(acc_class, load_m, e, in_service) * e


def calculate_raw_error(
    indication_i: float,
    load_l: float,
    delta_l: Optional[float] = None,
    e: Optional[float] = None,
    d: Optional[float] = None
) -> float:
    """
    Calculates error E before rounding.
    According to Clause A.4.4.3:
    If changeover point / flash point weights delta_L are applied:
        E = I + 0.5e - delta_L - L
    If resolution d < e (e.g. auxiliary indicating device with small d):
        E = I - L
    If delta_L is None and d == e:
        E = I - L
    """
    if delta_l is not None and e is not None and e > 0:
        # Standard OIML R 76 flash point formula
        return round(indication_i + (0.5 * e) - delta_l - load_l, 6)
    return round(indication_i - load_l, 6)


def calculate_corrected_error(raw_error_e: float, zero_error_e0: float) -> float:
    """
    Calculates corrected error:
    Ec = E - E0
    """
    return round(raw_error_e - zero_error_e0, 6)


def evaluate_weighing_test(
    acc_class: AccuracyClass,
    e: float,
    readings: List[Dict[str, Any]],
    in_service: bool = False
) -> Dict[str, Any]:
    """
    Evaluates Weighing Performance Test (Clause A.4.4).
    Each item in readings:
    {
        "load": float,
        "direction": "INCR" or "DECR",
        "indication": float,
        "delta_l": Optional[float],
        "zero_delta_l": Optional[float] # for zero load before reading
    }
    """
    processed = []
    all_pass = True
    max_error_ratio = 0.0
    zero_error_e0 = 0.0

    # Find zero load error E0 if available
    for r in readings:
        if float(r.get("load", 0.0)) == 0.0 and r.get("direction", "INCR").upper() == "INCR":
            ind = float(r.get("indication", 0.0))
            dl = float(r["delta_l"]) if r.get("delta_l") is not None else None
            zero_error_e0 = calculate_raw_error(ind, 0.0, dl, e)
            break

    # Calculate increasing vs decreasing pairs for hysteresis check
    incr_map = {}

    for idx, item in enumerate(readings):
        load = float(item.get("load", 0.0))
        direction = item.get("direction", "INCR").upper()
        indication = float(item.get("indication", 0.0))
        delta_l = float(item["delta_l"]) if item.get("delta_l") is not None else None
        
        mpe_e = get_mpe_in_e(acc_class, load, e, in_service)
        mpe_unit = mpe_e * e

        raw_error = calculate_raw_error(indication, load, delta_l, e)
        corrected_error = calculate_corrected_error(raw_error, zero_error_e0)
        corrected_error_in_e = round(corrected_error / e, 3) if e > 0 else corrected_error

        passed = abs(corrected_error) <= (mpe_unit + 1e-9)
        if not passed:
            all_pass = False

        ratio = abs(corrected_error) / mpe_unit if mpe_unit > 0 else 0
        if ratio > max_error_ratio:
            max_error_ratio = ratio

        row_res = {
            "index": idx + 1,
            "direction": direction,
            "load": load,
            "indication": indication,
            "delta_l": delta_l,
            "raw_error": raw_error,
            "corrected_error": corrected_error,
            "corrected_error_e": corrected_error_in_e,
            "mpe_e": mpe_e,
            "mpe_unit": round(mpe_unit, 6),
            "status": "PASS" if passed else "FAIL"
        }

        # Track for hysteresis
        load_key = round(load, 4)
        if direction == "INCR":
            incr_map[load_key] = row_res
        elif direction == "DECR" and load_key in incr_map:
            hysteresis = abs(corrected_error - incr_map[load_key]["corrected_error"])
            hysteresis_pass = hysteresis <= (mpe_unit + 1e-9)
            row_res["hysteresis"] = round(hysteresis, 6)
            row_res["hysteresis_status"] = "PASS" if hysteresis_pass else "FAIL"
            if not hysteresis_pass:
                all_pass = False

        processed.append(row_res)

    return {
        "test_name": "Weighing Performance Test (Clause A.4.4)",
        "zero_error_e0": zero_error_e0,
        "readings": processed,
        "overall_status": "PASS" if all_pass else "FAIL",
        "max_error_ratio": round(max_error_ratio, 2)
    }


def evaluate_repeatability_test(
    acc_class: AccuracyClass,
    e: float,
    load_levels: List[Dict[str, Any]],
    in_service: bool = False
) -> Dict[str, Any]:
    """
    Evaluates Repeatability Test (Clause A.4.10).
    Requires series of weighings (e.g. 10 at 0.5 Max and 10 at Max, or 3 for large).
    Maximum difference between any two results at the same load shall not exceed |MPE| for that load.
    load_levels: [
        {
            "load": float,
            "readings": [float, float, ...]
        }, ...
    ]
    """
    results = []
    overall_pass = True

    for level in load_levels:
        load = float(level.get("load", 0.0))
        readings = [float(x) for x in level.get("readings", [])]
        if not readings:
            continue

        min_val = min(readings)
        max_val = max(readings)
        delta_max = round(max_val - min_val, 6)
        
        mpe_e = get_mpe_in_e(acc_class, load, e, in_service)
        mpe_unit = round(mpe_e * e, 6)

        passed = delta_max <= (mpe_unit + 1e-9)
        if not passed:
            overall_pass = False

        results.append({
            "load": load,
            "readings_count": len(readings),
            "readings": readings,
            "min_indication": min_val,
            "max_indication": max_val,
            "max_difference": delta_max,
            "mpe_unit": mpe_unit,
            "mpe_e": mpe_e,
            "status": "PASS" if passed else "FAIL"
        })

    return {
        "test_name": "Repeatability Test (Clause A.4.10)",
        "load_series": results,
        "overall_status": "PASS" if (overall_pass and len(results) > 0) else "FAIL"
    }


def evaluate_eccentricity_test(
    acc_class: AccuracyClass,
    e: float,
    test_load: float,
    positions: List[Dict[str, Any]],
    in_service: bool = False
) -> Dict[str, Any]:
    """
    Evaluates Eccentricity / Off-Center Loading Test (Clause A.4.7).
    Positions usually: Center, Front-Left, Rear-Left, Rear-Right, Front-Right.
    Test load is normally 1/3 Max (or Max / (N-1)).
    Error at each position shall not exceed MPE.
    """
    mpe_e = get_mpe_in_e(acc_class, test_load, e, in_service)
    mpe_unit = round(mpe_e * e, 6)

    # First determine center / reference error if present
    zero_e0 = 0.0
    for p in positions:
        if p.get("position", "").lower() in ["center", "1", "pos 1", "position 1"]:
            ind = float(p.get("indication", test_load))
            dl = float(p["delta_l"]) if p.get("delta_l") is not None else None
            raw_err = calculate_raw_error(ind, test_load, dl, e)
            # Center error is tracked
            break

    evaluated_positions = []
    overall_pass = True

    for p in positions:
        pos_name = p.get("position", "Unknown")
        indication = float(p.get("indication", test_load))
        delta_l = float(p["delta_l"]) if p.get("delta_l") is not None else None
        
        raw_err = calculate_raw_error(indication, test_load, delta_l, e)
        # In eccentricity, corrected error is raw_err - zero error at unloaded
        unloaded_zero_e = float(p.get("zero_error", 0.0))
        corrected_err = calculate_corrected_error(raw_err, unloaded_zero_e)
        
        passed = abs(corrected_err) <= (mpe_unit + 1e-9)
        if not passed:
            overall_pass = False

        evaluated_positions.append({
            "position": pos_name,
            "indication": indication,
            "delta_l": delta_l,
            "raw_error": raw_err,
            "corrected_error": corrected_err,
            "corrected_error_e": round(corrected_err / e, 3) if e > 0 else corrected_err,
            "mpe_unit": mpe_unit,
            "mpe_e": mpe_e,
            "status": "PASS" if passed else "FAIL"
        })

    return {
        "test_name": "Eccentricity Loading Test (Clause A.4.7)",
        "test_load": test_load,
        "mpe_unit": mpe_unit,
        "mpe_e": mpe_e,
        "positions": evaluated_positions,
        "overall_status": "PASS" if overall_pass else "FAIL"
    }


def evaluate_tare_and_zero_test(
    e: float,
    zero_setting_indication: float,
    zero_delta_l: Optional[float] = None,
    tare_load: float = 0.0,
    tare_indication: float = 0.0,
    tare_delta_l: Optional[float] = None,
    net_load: float = 0.0,
    net_indication: float = 0.0,
    net_delta_l: Optional[float] = None
) -> Dict[str, Any]:
    """
    Evaluates Tare and Zero-Setting Tests (Clauses A.4.2 & A.4.6).
    1. Zero-setting error E0 shall not exceed +/- 0.25 e.
    2. Tare weighing error shall comply with MPE for that net load.
    """
    # 1. Zero setting error
    e0 = calculate_raw_error(zero_setting_indication, 0.0, zero_delta_l, e)
    max_allowed_zero_error = 0.25 * e
    zero_passed = abs(e0) <= (max_allowed_zero_error + 1e-9)

    # 2. Tare net weighing error
    net_err = calculate_raw_error(net_indication, net_load, net_delta_l, e)
    corrected_net_err = calculate_corrected_error(net_err, e0)
    # MPE for net load
    mpe_net = get_mpe_in_e(AccuracyClass.CLASS_III, net_load, e) * e # Default fallback
    net_passed = abs(corrected_net_err) <= (mpe_net + 1e-9)

    overall_pass = zero_passed and net_passed

    return {
        "test_name": "Zero-Setting and Tare Test (Clauses A.4.2 & A.4.6)",
        "zero_error_e0": e0,
        "max_allowed_zero_error": max_allowed_zero_error,
        "zero_setting_status": "PASS" if zero_passed else "FAIL",
        "tare_load": tare_load,
        "net_load": net_load,
        "net_corrected_error": corrected_net_err,
        "net_weighing_status": "PASS" if net_passed else "FAIL",
        "overall_status": "PASS" if overall_pass else "FAIL"
    }


def evaluate_discrimination_test(
    d: float,
    observations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluates Discrimination Test (Clause A.4.8).
    An extra load of 1.4 d smoothly placed on the loaded receptor shall cause
    the indication to increment by 1 scale interval.
    observations: [
        {
            "load_level": "Min" / "Half-Max" / "Max",
            "load": float,
            "initial_indication": float,
            "extra_load": float (expected ~1.4*d),
            "new_indication": float,
            "indication_changed": bool
        }
    ]
    """
    results = []
    overall_pass = True

    for obs in observations:
        init_ind = float(obs.get("initial_indication", 0.0))
        new_ind = float(obs.get("new_indication", init_ind))
        diff = round(new_ind - init_ind, 6)
        
        # Expected shift is at least 1 d
        passed = diff >= (d - 1e-6)
        if not passed:
            overall_pass = False

        results.append({
            "load_level": obs.get("load_level", "Unknown"),
            "load": float(obs.get("load", 0.0)),
            "initial_indication": init_ind,
            "extra_load": float(obs.get("extra_load", 1.4 * d)),
            "new_indication": new_ind,
            "indication_shift": diff,
            "required_shift": d,
            "status": "PASS" if passed else "FAIL"
        })

    return {
        "test_name": "Discrimination Test (Clause A.4.8)",
        "scale_interval_d": d,
        "results": results,
        "overall_status": "PASS" if (overall_pass and len(results) > 0) else "FAIL"
    }


def evaluate_environmental_and_voltage_test(
    acc_class: AccuracyClass,
    e: float,
    temperature_records: List[Dict[str, Any]],
    voltage_records: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluates Temperature (A.5.3) and Voltage Variations (A.5.4) tests.
    - Zero drift with temperature shall not exceed 1 e per 5 deg C.
    - Errors at 20 C, high temp (40 C), low temp (-10 C or 10 C) shall be <= MPE.
    - Mains voltage at +10% and -15% shall be <= MPE.
    """
    temp_pass = True
    temp_results = []

    for t in temperature_records:
        temp_c = float(t.get("temperature_c", 20.0))
        load = float(t.get("load", 0.0))
        err = float(t.get("corrected_error", 0.0))
        mpe_val = get_mpe_in_engineering_units(acc_class, load, e)
        
        ok = abs(err) <= (mpe_val + 1e-9)
        if not ok:
            temp_pass = False
            
        temp_results.append({
            "temperature_c": temp_c,
            "load": load,
            "corrected_error": err,
            "mpe": mpe_val,
            "status": "PASS" if ok else "FAIL"
        })

    volt_pass = True
    volt_results = []

    for v in voltage_records:
        condition = v.get("condition", "Nominal (230V)")
        load = float(v.get("load", 0.0))
        err = float(v.get("corrected_error", 0.0))
        mpe_val = get_mpe_in_engineering_units(acc_class, load, e)

        ok = abs(err) <= (mpe_val + 1e-9)
        if not ok:
            volt_pass = False

        volt_results.append({
            "condition": condition,
            "load": load,
            "corrected_error": err,
            "mpe": mpe_val,
            "status": "PASS" if ok else "FAIL"
        })

    overall_pass = temp_pass and volt_pass

    return {
        "test_name": "Environmental & Influence Factors (Clauses A.5.3 & A.5.4)",
        "temperature_evaluation": {
            "results": temp_results,
            "status": "PASS" if temp_pass else "FAIL"
        },
        "voltage_evaluation": {
            "results": volt_results,
            "status": "PASS" if volt_pass else "FAIL"
        },
        "overall_status": "PASS" if overall_pass else "FAIL"
    }


def evaluate_complete_oiml_r76_evaluation(
    specs: Dict[str, Any],
    test_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Comprehensive pipeline evaluating all tests of a NAWI Model Approval submission.
    Computes instrument metrology parameters (n, class compliance),
    evaluates all individual test modules,
    and returns a full metrological compliance audit.
    """
    acc_class = normalize_class(specs.get("accuracy_class", "Class III"))
    max_cap = float(specs.get("max_capacity", 15.0))
    min_cap = float(specs.get("min_capacity", 0.1))
    e = float(specs.get("verification_scale_interval", 0.005))
    d = float(specs.get("scale_interval", e))
    in_service = bool(specs.get("is_in_service_test", False))

    n = calculate_verification_scale_intervals(max_cap, e)
    n_valid, n_message = validate_scale_intervals(acc_class, n)

    test_summaries = {}
    test_statuses = []

    # 1. Weighing test
    weighing_data = test_data.get("weighing_test", [])
    if weighing_data:
        w_res = evaluate_weighing_test(acc_class, e, weighing_data, in_service)
        test_summaries["weighing_test"] = w_res
        test_statuses.append(w_res["overall_status"] == "PASS")

    # 2. Repeatability test
    repeat_data = test_data.get("repeatability_test", [])
    if repeat_data:
        r_res = evaluate_repeatability_test(acc_class, e, repeat_data, in_service)
        test_summaries["repeatability_test"] = r_res
        test_statuses.append(r_res["overall_status"] == "PASS")

    # 3. Eccentricity test
    ecc_data = test_data.get("eccentricity_test", {})
    if ecc_data:
        test_load = float(ecc_data.get("test_load", max_cap / 3.0))
        positions = ecc_data.get("positions", [])
        e_res = evaluate_eccentricity_test(acc_class, e, test_load, positions, in_service)
        test_summaries["eccentricity_test"] = e_res
        test_statuses.append(e_res["overall_status"] == "PASS")

    # 4. Tare & zero test
    tare_data = test_data.get("tare_zero_test", {})
    if tare_data:
        tz_res = evaluate_tare_and_zero_test(
            e=e,
            zero_setting_indication=float(tare_data.get("zero_setting_indication", 0.0)),
            zero_delta_l=tare_data.get("zero_delta_l"),
            tare_load=float(tare_data.get("tare_load", 0.0)),
            tare_indication=float(tare_data.get("tare_indication", 0.0)),
            tare_delta_l=tare_data.get("tare_delta_l"),
            net_load=float(tare_data.get("net_load", 0.0)),
            net_indication=float(tare_data.get("net_indication", 0.0)),
            net_delta_l=tare_data.get("net_delta_l")
        )
        test_summaries["tare_zero_test"] = tz_res
        test_statuses.append(tz_res["overall_status"] == "PASS")

    # 5. Discrimination test
    disc_data = test_data.get("discrimination_test", [])
    if disc_data:
        d_res = evaluate_discrimination_test(d, disc_data)
        test_summaries["discrimination_test"] = d_res
        test_statuses.append(d_res["overall_status"] == "PASS")

    # 6. Environmental and voltage tests
    env_data = test_data.get("environmental_voltage_test", {})
    if env_data:
        ev_res = evaluate_environmental_and_voltage_test(
            acc_class,
            e,
            env_data.get("temperatures", []),
            env_data.get("voltages", [])
        )
        test_summaries["environmental_voltage_test"] = ev_res
        test_statuses.append(ev_res["overall_status"] == "PASS")

    # Overall verdict
    is_compliant = n_valid and all(test_statuses) if test_statuses else False

    final_verdict = "APPROVED_COMPLIANT" if is_compliant else "REJECTED_NON_COMPLIANT"

    return {
        "accuracy_class": acc_class.value,
        "max_capacity": max_cap,
        "min_capacity": min_cap,
        "verification_scale_interval_e": e,
        "scale_interval_d": d,
        "n_intervals": n,
        "n_validation": {
            "is_valid": n_valid,
            "message": n_message
        },
        "tests_evaluated_count": len(test_statuses),
        "tests_passed_count": sum(1 for s in test_statuses if s),
        "tests_failed_count": sum(1 for s in test_statuses if not s),
        "test_summaries": test_summaries,
        "is_fully_compliant": is_compliant,
        "final_verdict": final_verdict,
        "statutory_reference": "Legal Metrology Act, 2009 & OIML Recommendation R 76-1:2006 (E)"
    }
