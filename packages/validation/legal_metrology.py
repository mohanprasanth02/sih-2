"""
LabelGuard AI - Legal Metrology Validation Functions
Pure deterministic validators based on Legal Metrology (Packaged Commodities) Rules, 2011
"""
import re
from typing import Dict, Any, Tuple, Optional

def validate_net_quantity(qty_str: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Validates net quantity against Rule 6(1)(d) & Rule 11.
    Standard SI units: g, kg, ml, l, m, cm, mm, U, N.
    Prohibited non-standard abbreviations: gms, gm, gms., kgs, kgs., ltr, ltrs, ml.
    """
    if not qty_str:
        return False, "Net quantity declaration is missing", None
    
    cleaned = qty_str.strip().lower()
    
    # Check for prohibited units: e.g. gms, gm, kgs, kg., ltr, ltrs, ml.
    prohibited_match = re.search(r"\b(gms?\.?|gm\b|kgs\.?|kg\.|ltrs?\.?|ltr\b|cu\.?cm)\b", cleaned)
    if prohibited_match:
        proh = prohibited_match.group(0)
        return False, f"Non-standard unit '{proh}' detected. Legal Metrology Rules mandate standard SI symbols: 'g', 'kg', 'ml', 'l' without trailing periods or plurals.", None

    # Match number + unit
    pattern = r"(\d+(?:\.\d+)?)\s*(kg|g|mg|l|ml|m|cm|mm|units?|pieces?|pcs?|n|u)\b"
    match = re.search(pattern, cleaned)
    if not match:
        return False, f"Could not parse valid standard unit of weight/measure from '{qty_str}'", None

    value_num = float(match.group(1))
    unit = match.group(2)
    
    # Normalize unit
    if unit in ["units", "unit", "pieces", "piece", "pcs"]:
        unit = "N"
    elif unit in ["g", "kg", "ml", "l"]:
        pass

    return True, "Valid standard metric net quantity", {
        "numeric_value": value_num,
        "unit": unit,
        "standardized": f"{value_num} {unit}"
    }

def validate_mrp_declaration(mrp_str: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Validates MRP according to Rule 6(1)(e):
    Must state Maximum Retail Price, value in Rs./₹, and 'inclusive of all taxes'.
    """
    if not mrp_str:
        return False, "MRP declaration is missing", None
    
    cleaned = mrp_str.lower()
    has_mrp_prefix = bool(re.search(r"\b(mrp|max\.?\s*retail\s*price|maximum\s*retail\s*price)\b", cleaned))
    has_currency = bool(re.search(r"(₹|rs\.?|inr)", cleaned))
    has_tax_clause = bool(re.search(r"(incl|inclusive\s*of\s*all\s*taxes)", cleaned))

    # Extract numeric price
    price_match = re.search(r"(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d{1,2})?)", cleaned)
    price_val = float(price_match.group(1)) if price_match else None

    if not price_val:
        return False, "No valid numeric retail price found in MRP declaration", None

    notes = []
    is_valid = True

    if not has_mrp_prefix:
        notes.append("Prefix 'MRP' or 'Maximum Retail Price' not clearly declared.")
        is_valid = False

    if not has_tax_clause:
        notes.append("Mandatory statutory clause 'inclusive of all taxes' or 'incl. of all taxes' missing.")
        # Under Rule 6(1)(e), missing tax clause is a violation
        is_valid = False

    if is_valid:
        return True, "Valid statutory MRP declaration", {
            "price": price_val,
            "has_tax_clause": has_tax_clause
        }
    else:
        return False, "; ".join(notes), {
            "price": price_val,
            "has_tax_clause": has_tax_clause
        }

def validate_unit_sale_price(
    net_qty: Optional[Dict[str, Any]], 
    mrp: Optional[Dict[str, Any]], 
    usp_str: Optional[str]
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Validates Unit Sale Price (USP) under Rule 6(1)(n) (2021 amendment).
    Mandatory when net quantity is above 1kg/1L (expressed in ₹/kg or ₹/L) or <1kg (expressed in ₹/g or ₹/ml).
    """
    if not net_qty or not mrp:
        return False, "Cannot evaluate USP without valid Net Quantity and MRP", None
    
    num_qty = net_qty.get("numeric_value", 0)
    unit = net_qty.get("unit", "")
    price = mrp.get("price", 0)
    
    if num_qty <= 0 or price <= 0:
        return False, "Invalid numeric quantity or price for USP check", None

    # Calculate expected USP
    if unit in ["g", "ml"]:
        expected_usp_per_unit = price / num_qty
        unit_target = f"per {unit}"
    elif unit in ["kg", "l"]:
        expected_usp_per_unit = price / num_qty
        unit_target = f"per {unit}"
    else:
        expected_usp_per_unit = price / num_qty
        unit_target = "per unit"

    if not usp_str:
        return False, f"USP mandatory under Rule 6(1)(n) but not detected on package (Expected approx ₹{expected_usp_per_unit:.2f} {unit_target})", {
            "expected_usp": round(expected_usp_per_unit, 2),
            "unit": unit_target
        }

    # If USP string is present, check parsed value
    usp_match = re.search(r"(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d{1,2})?)", usp_str.lower())
    if usp_match:
        declared_usp = float(usp_match.group(1))
        # Allow 5% tolerance for rounding difference
        ratio = abs(declared_usp - expected_usp_per_unit) / max(expected_usp_per_unit, 0.001)
        if ratio > 0.15:
            return False, f"Declared USP (₹{declared_usp}) does not match calculated USP (₹{expected_usp_per_unit:.2f} {unit_target})", {
                "declared_usp": declared_usp,
                "expected_usp": round(expected_usp_per_unit, 2)
            }
        return True, f"USP verified compliant with Rule 6(1)(n)", {
            "declared_usp": declared_usp,
            "expected_usp": round(expected_usp_per_unit, 2)
        }

    return True, "USP declared", {"raw": usp_str}
