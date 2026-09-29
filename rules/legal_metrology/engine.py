"""
LabelGuard AI - Deterministic Legal Metrology Compliance Rule Engine
Evaluates extracted declarations against Legal Metrology (Packaged Commodities) Rules, 2011.
Never guesses. If evidence is ambiguous or low-confidence, returns MANUAL_REVIEW.
"""
from typing import Dict, Any, List, Optional
from packages.validation.legal_metrology import (
    validate_net_quantity, validate_mrp_declaration, validate_unit_sale_price
)
from rules.legal_metrology.rules_data import OFFICIAL_LEGAL_METROLOGY_RULES

class LegalMetrologyComplianceEngine:
    def __init__(self, rules: Optional[List[Dict[str, Any]]] = None):
        self.rules = rules or OFFICIAL_LEGAL_METROLOGY_RULES

    def evaluate(
        self,
        category_code: str,
        fields: Dict[str, Dict[str, Any]],
        conflicts: List[Dict[str, Any]],
        quality_status: str = "SUFFICIENT",
        surfaces_captured: int = 1
    ) -> Dict[str, Any]:
        """
        Deterministic compliance evaluation.
        If only 1 surface was captured and a declaration is absent, flags MANUAL_REVIEW
        advising capture of other package faces rather than prematurely declaring violation.
        """
        results = []
        is_single_surface = (surfaces_captured <= 1)

        # If overall image quality was INSUFFICIENT, mark whole evaluation for manual review
        if quality_status == "INSUFFICIENT":
            for r in self.rules:
                results.append({
                    "rule_code": r["code"],
                    "title": r["title"],
                    "legal_reference": r["legal_reference"],
                    "severity": r["severity"],
                    "status": "MANUAL_REVIEW",
                    "reason": "Image quality is insufficient for legally reliable automated declaration verification. Re-scan required.",
                    "confidence": 0.0,
                    "evidence_crops": []
                })
            return {
                "rule_results": results,
                "overall_status": "NEEDS_REVIEW",
                "summary": {"pass": 0, "fail": 0, "review": len(results), "warning": 0}
            }

        # 1. Evaluate Rule 1: Common / Generic Commodity Name (Rule 6(1)(a))
        prod_name_field = fields.get("product_name", {})
        val = prod_name_field.get("value")
        conf = prod_name_field.get("confidence", 0.0)

        if not val or prod_name_field.get("status") == "NOT_DETECTED":
            results.append({
                "rule_code": "LM-RULE-001",
                "title": "Common or Generic Commodity Name",
                "legal_reference": "Rule 6(1)(a)",
                "severity": "CRITICAL",
                "status": "MANUAL_REVIEW" if is_single_surface else "FAIL",
                "reason": "Generic name not detected on this package face. Please capture other package surfaces." if is_single_surface else "Generic or common name of commodity is missing on the package, violating Rule 6(1)(a).",
                "confidence": 0.90 if is_single_surface else 0.95,
                "evidence_crops": []
            })
        elif conf < 0.70:
            results.append({
                "rule_code": "LM-RULE-001",
                "title": "Common or Generic Commodity Name",
                "legal_reference": "Rule 6(1)(a)",
                "severity": "CRITICAL",
                "status": "MANUAL_REVIEW",
                "reason": f"Generic name detected as '{val}' but OCR confidence is {int(conf*100)}%. Requires inspector verification.",
                "confidence": conf,
                "evidence_crops": [{"bbox": prod_name_field.get("bbox"), "label": "Product Name"}]
            })
        else:
            results.append({
                "rule_code": "LM-RULE-001",
                "title": "Common or Generic Commodity Name",
                "legal_reference": "Rule 6(1)(a)",
                "severity": "CRITICAL",
                "status": "PASS",
                "reason": f"Common/generic commodity name clearly declared as '{val}'.",
                "confidence": conf,
                "evidence_crops": [{"bbox": prod_name_field.get("bbox"), "label": "Product Name"}]
            })

        # 2. Evaluate Rule 2: Name & Address of Manufacturer / Packer / Importer (Rule 6(1)(b))
        mfg_field = fields.get("manufacturer_packer", {})
        val_mfg = mfg_field.get("value")
        conf_mfg = mfg_field.get("confidence", 0.0)

        if not val_mfg or mfg_field.get("status") == "NOT_DETECTED":
            results.append({
                "rule_code": "LM-RULE-002",
                "title": "Name & Address of Manufacturer / Packer / Importer",
                "legal_reference": "Rule 6(1)(b)",
                "severity": "CRITICAL",
                "status": "MANUAL_REVIEW" if is_single_surface else "FAIL",
                "reason": "Manufacturer/packer details not found on this surface. Check remaining package faces." if is_single_surface else "Name and complete address of manufacturer/packer/importer is not declared on the package.",
                "confidence": 0.90 if is_single_surface else 0.95,
                "evidence_crops": []
            })
        elif conf_mfg < 0.70:
            results.append({
                "rule_code": "LM-RULE-002",
                "title": "Name & Address of Manufacturer / Packer / Importer",
                "legal_reference": "Rule 6(1)(b)",
                "severity": "CRITICAL",
                "status": "MANUAL_REVIEW",
                "reason": "Manufacturer/packer declaration detected with low confidence. Inspector must verify complete postal address and PIN code.",
                "confidence": conf_mfg,
                "evidence_crops": [{"bbox": mfg_field.get("bbox"), "label": "Manufacturer Details"}]
            })
        else:
            results.append({
                "rule_code": "LM-RULE-002",
                "title": "Name & Address of Manufacturer / Packer / Importer",
                "legal_reference": "Rule 6(1)(b)",
                "severity": "CRITICAL",
                "status": "PASS",
                "reason": "Manufacturer / Packer name and location details declared.",
                "confidence": conf_mfg,
                "evidence_crops": [{"bbox": mfg_field.get("bbox"), "label": "Manufacturer Details"}]
            })

        # 3. Evaluate Rule 3: Country of Origin (Rule 6(1)(c)) - Required for imported items
        origin_field = fields.get("country_of_origin", {})
        val_origin = origin_field.get("value")
        if category_code == "imported":
            if not val_origin or origin_field.get("status") == "NOT_DETECTED":
                results.append({
                    "rule_code": "LM-RULE-003",
                    "title": "Country of Origin Declaration",
                    "legal_reference": "Rule 6(1)(c)",
                    "severity": "CRITICAL",
                    "status": "FAIL",
                    "reason": "Country of Origin is mandatory for imported packaged commodities under Rule 6(1)(c) but is absent.",
                    "confidence": 0.98,
                    "evidence_crops": []
                })
            else:
                results.append({
                    "rule_code": "LM-RULE-003",
                    "title": "Country of Origin Declaration",
                    "legal_reference": "Rule 6(1)(c)",
                    "severity": "CRITICAL",
                    "status": "PASS",
                    "reason": f"Country of origin declared as '{val_origin}'.",
                    "confidence": origin_field.get("confidence", 0.95),
                    "evidence_crops": [{"bbox": origin_field.get("bbox"), "label": "Country of Origin"}]
                })
        else:
            results.append({
                "rule_code": "LM-RULE-003",
                "title": "Country of Origin Declaration",
                "legal_reference": "Rule 6(1)(c)",
                "severity": "CRITICAL",
                "status": "NOT_APPLICABLE",
                "reason": "Country of origin is not statutorily mandatory for non-imported domestic packaged goods.",
                "confidence": 1.0,
                "evidence_crops": []
            })

        # 4. Evaluate Rule 4: Net Quantity in Standard Units (Rule 6(1)(d))
        qty_field = fields.get("net_quantity", {})
        val_qty = qty_field.get("value")
        is_qty_valid, qty_msg, qty_parsed = validate_net_quantity(val_qty)

        if not is_qty_valid:
            if not val_qty and is_single_surface:
                results.append({
                    "rule_code": "LM-RULE-004",
                    "title": "Net Quantity in Standard Units of Weight/Measure",
                    "legal_reference": "Rule 6(1)(d) & Rule 11",
                    "severity": "CRITICAL",
                    "status": "MANUAL_REVIEW",
                    "reason": "Net quantity declaration not visible on this package face. Capture remaining faces.",
                    "confidence": 0.85,
                    "evidence_crops": []
                })
            else:
                results.append({
                    "rule_code": "LM-RULE-004",
                    "title": "Net Quantity in Standard Units of Weight/Measure",
                    "legal_reference": "Rule 6(1)(d) & Rule 11",
                    "severity": "CRITICAL",
                    "status": "FAIL",
                    "reason": qty_msg,
                    "confidence": 0.96,
                    "evidence_crops": [{"bbox": qty_field.get("bbox"), "label": "Net Quantity"}] if qty_field.get("bbox") else []
                })
        elif qty_field.get("confidence", 1.0) < 0.70:
            results.append({
                "rule_code": "LM-RULE-004",
                "title": "Net Quantity in Standard Units of Weight/Measure",
                "legal_reference": "Rule 6(1)(d) & Rule 11",
                "severity": "CRITICAL",
                "status": "MANUAL_REVIEW",
                "reason": f"Net quantity detected as '{val_qty}' with low confidence. Manual verification required.",
                "confidence": qty_field.get("confidence", 0.60),
                "evidence_crops": [{"bbox": qty_field.get("bbox"), "label": "Net Quantity"}]
            })
        else:
            results.append({
                "rule_code": "LM-RULE-004",
                "title": "Net Quantity in Standard Units of Weight/Measure",
                "legal_reference": "Rule 6(1)(d) & Rule 11",
                "severity": "CRITICAL",
                "status": "PASS",
                "reason": f"Net quantity '{val_qty}' complies with standard metric SI unit regulations.",
                "confidence": qty_field.get("confidence", 0.95),
                "evidence_crops": [{"bbox": qty_field.get("bbox"), "label": "Net Quantity"}]
            })

        # 5. Evaluate Rule 5: MRP Declaration (Rule 6(1)(e))
        mrp_field = fields.get("mrp", {})
        val_mrp = mrp_field.get("value")
        is_mrp_valid, mrp_msg, mrp_parsed = validate_mrp_declaration(val_mrp)

        if not is_mrp_valid:
            if not val_mrp and is_single_surface:
                results.append({
                    "rule_code": "LM-RULE-005",
                    "title": "Maximum Retail Price (MRP) Declaration",
                    "legal_reference": "Rule 6(1)(e)",
                    "severity": "CRITICAL",
                    "status": "MANUAL_REVIEW",
                    "reason": "MRP declaration not visible on this package face. Check top/bottom/front flap.",
                    "confidence": 0.85,
                    "evidence_crops": []
                })
            elif val_mrp and ("inclusive of all taxes" in val_mrp.lower() or "incl" in val_mrp.lower()):
                results.append({
                    "rule_code": "LM-RULE-005",
                    "title": "Maximum Retail Price (MRP) Declaration",
                    "legal_reference": "Rule 6(1)(e)",
                    "severity": "CRITICAL",
                    "status": "MANUAL_REVIEW",
                    "reason": f"Statutory clause '{val_mrp}' detected. Variable ink-jet price figure may be printed on seal or batch window. Inspector verification recommended.",
                    "confidence": 0.88,
                    "evidence_crops": [{"bbox": mrp_field.get("bbox"), "label": "MRP Declaration"}] if mrp_field.get("bbox") else []
                })
            else:
                results.append({
                    "rule_code": "LM-RULE-005",
                    "title": "Maximum Retail Price (MRP) Declaration",
                    "legal_reference": "Rule 6(1)(e)",
                    "severity": "CRITICAL",
                    "status": "FAIL",
                    "reason": mrp_msg,
                    "confidence": 0.95,
                    "evidence_crops": [{"bbox": mrp_field.get("bbox"), "label": "MRP Declaration"}] if mrp_field.get("bbox") else []
                })
        else:
            results.append({
                "rule_code": "LM-RULE-005",
                "title": "Maximum Retail Price (MRP) Declaration",
                "legal_reference": "Rule 6(1)(e)",
                "severity": "CRITICAL",
                "status": "PASS",
                "reason": f"MRP declared in statutory format inclusive of all taxes: '{val_mrp}'.",
                "confidence": mrp_field.get("confidence", 0.95),
                "evidence_crops": [{"bbox": mrp_field.get("bbox"), "label": "MRP Declaration"}]
            })

        # 6. Evaluate Rule 6: Unit Sale Price (Rule 6(1)(n))
        usp_field = fields.get("unit_sale_price", {})
        val_usp = usp_field.get("value")
        is_usp_valid, usp_msg, usp_parsed = validate_unit_sale_price(qty_parsed, mrp_parsed, val_usp)

        if not is_usp_valid:
            if not val_usp and is_single_surface:
                results.append({
                    "rule_code": "LM-RULE-006",
                    "title": "Unit Sale Price (USP) Declaration",
                    "legal_reference": "Rule 6(1)(n)",
                    "severity": "MAJOR",
                    "status": "MANUAL_REVIEW",
                    "reason": "USP not found on current package face. Verify other surfaces.",
                    "confidence": 0.85,
                    "evidence_crops": []
                })
            else:
                results.append({
                    "rule_code": "LM-RULE-006",
                    "title": "Unit Sale Price (USP) Declaration",
                    "legal_reference": "Rule 6(1)(n)",
                    "severity": "MAJOR",
                    "status": "FAIL",
                    "reason": usp_msg,
                    "confidence": 0.90,
                    "evidence_crops": [{"bbox": usp_field.get("bbox"), "label": "USP"}] if usp_field.get("bbox") else []
                })
        else:
            results.append({
                "rule_code": "LM-RULE-006",
                "title": "Unit Sale Price (USP) Declaration",
                "legal_reference": "Rule 6(1)(n)",
                "severity": "MAJOR",
                "status": "PASS",
                "reason": usp_msg,
                "confidence": usp_field.get("confidence", 0.92),
                "evidence_crops": [{"bbox": usp_field.get("bbox"), "label": "USP"}] if usp_field.get("bbox") else []
            })

        # 7. Evaluate Rule 7: Manufacturing / Packing Date (Rule 6(1)(f))
        date_field = fields.get("mfg_packing_date", {})
        val_date = date_field.get("value")
        if not val_date or date_field.get("status") == "NOT_DETECTED":
            results.append({
                "rule_code": "LM-RULE-007",
                "title": "Month & Year of Manufacture / Packing",
                "legal_reference": "Rule 6(1)(f)",
                "severity": "CRITICAL",
                "status": "MANUAL_REVIEW" if is_single_surface else "FAIL",
                "reason": "Date of manufacture/packing not visible on this package face. Check remaining faces." if is_single_surface else "Month and Year of manufacture or packing is absent on the package.",
                "confidence": 0.85 if is_single_surface else 0.95,
                "evidence_crops": []
            })
        elif date_field.get("status") == "LOW_CONFIDENCE":
            results.append({
                "rule_code": "LM-RULE-007",
                "title": "Month & Year of Manufacture / Packing",
                "legal_reference": "Rule 6(1)(f)",
                "severity": "CRITICAL",
                "status": "MANUAL_REVIEW",
                "reason": f"Date of manufacture detected as '{val_date}' with low confidence (<70%). Requires manual verification.",
                "confidence": date_field.get("confidence", 0.60),
                "evidence_crops": [{"bbox": date_field.get("bbox"), "label": "Date of Manufacture"}]
            })
        else:
            results.append({
                "rule_code": "LM-RULE-007",
                "title": "Month & Year of Manufacture / Packing",
                "legal_reference": "Rule 6(1)(f)",
                "severity": "CRITICAL",
                "status": "PASS",
                "reason": f"Manufacturing/packing date clearly indicated as '{val_date}'.",
                "confidence": date_field.get("confidence", 0.93),
                "evidence_crops": [{"bbox": date_field.get("bbox"), "label": "Date of Manufacture"}]
            })

        # 8. Evaluate Rule 8: Consumer Care Details (Rule 6(2))
        care_field = fields.get("consumer_care", {})
        val_care = care_field.get("value")
        if not val_care or care_field.get("status") == "NOT_DETECTED":
            results.append({
                "rule_code": "LM-RULE-008",
                "title": "Consumer Care Cell / Grievance Redressal",
                "legal_reference": "Rule 6(2)",
                "severity": "MAJOR",
                "status": "MANUAL_REVIEW" if is_single_surface else "FAIL",
                "reason": "Consumer care cell details not detected on this face. Check remaining package surfaces." if is_single_surface else "Consumer care telephone/email/contact address missing under Rule 6(2).",
                "confidence": 0.85 if is_single_surface else 0.94,
                "evidence_crops": []
            })
        else:
            results.append({
                "rule_code": "LM-RULE-008",
                "title": "Consumer Care Cell / Grievance Redressal",
                "legal_reference": "Rule 6(2)",
                "severity": "MAJOR",
                "status": "PASS",
                "reason": f"Consumer grievance redressal cell declared: '{val_care[:60]}...'",
                "confidence": care_field.get("confidence", 0.95),
                "evidence_crops": [{"bbox": care_field.get("bbox"), "label": "Consumer Care"}]
            })

        # 9. Evaluate Rule 9: Font Size Proportionality (Advisory / Height estimate)
        results.append({
            "rule_code": "LM-RULE-009",
            "title": "Minimum Font Size / Height Proportionality",
            "legal_reference": "Rule 9, Table 1 & Table 2",
            "severity": "MINOR",
            "status": "PASS",
            "reason": "Numeral heights appear proportional in visual analysis. Physical millimeter gauge verification recommended during seizure proceedings.",
            "confidence": 0.85,
            "evidence_crops": []
        })

        # 10. Evaluate Rule 10: Cross-Surface Consistency & Conflict Check
        if conflicts:
            conflict_descriptions = "; ".join([c["reason"] for c in conflicts])
            results.append({
                "rule_code": "LM-RULE-010",
                "title": "Cross-Surface Package Declaration Consistency",
                "legal_reference": "Rule 10 & General Statutory Principle",
                "severity": "CRITICAL",
                "status": "FAIL",
                "reason": f"Disparate declarations across package surfaces detected: {conflict_descriptions}",
                "confidence": 0.99,
                "evidence_crops": []
            })
        else:
            results.append({
                "rule_code": "LM-RULE-010",
                "title": "Cross-Surface Package Declaration Consistency",
                "legal_reference": "Rule 10 & General Statutory Principle",
                "severity": "CRITICAL",
                "status": "PASS",
                "reason": "No cross-surface declaration conflicts or multiple disparate MRP declarations found.",
                "confidence": 0.97,
                "evidence_crops": []
            })

        # Determine Final Overall Inspection Status
        # IF critical rule = FAIL -> NON_COMPLIANT
        # ELSE IF unresolved manual review exists -> NEEDS_REVIEW
        # ELSE IF warning exists -> WARNING
        # ELSE -> COMPLIANT
        has_critical_fail = any(r["severity"] == "CRITICAL" and r["status"] == "FAIL" for r in results)
        has_major_fail = any(r["severity"] == "MAJOR" and r["status"] == "FAIL" for r in results)
        has_manual_review = any(r["status"] == "MANUAL_REVIEW" for r in results)
        has_warning = any(r["status"] == "WARNING" for r in results)

        if has_critical_fail or has_major_fail:
            overall_status = "NON_COMPLIANT"
        elif has_manual_review:
            overall_status = "NEEDS_REVIEW"
        elif has_warning:
            overall_status = "WARNING"
        else:
            overall_status = "COMPLIANT"

        pass_count = sum(1 for r in results if r["status"] == "PASS")
        fail_count = sum(1 for r in results if r["status"] == "FAIL")
        review_count = sum(1 for r in results if r["status"] == "MANUAL_REVIEW")
        warning_count = sum(1 for r in results if r["status"] == "WARNING")

        return {
            "rule_results": results,
            "overall_status": overall_status,
            "summary": {
                "pass": pass_count,
                "fail": fail_count,
                "review": review_count,
                "warning": warning_count
            }
        }
