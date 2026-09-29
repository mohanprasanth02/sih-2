"""
LabelGuard AI - Structured Legal Metrology Field Extractor & Normalizer
Transforms OCR tokens and detected text into structured Legal Metrology declarations with bounding boxes.
Trained for Indian FMCG, packaged food, cosmetics, and imported commodity packaging layouts.
"""
import re
from typing import Dict, Any, List, Optional
from services.ai.interfaces import FieldExtractionProvider, OCRToken

class RuleBasedFieldExtractor(FieldExtractionProvider):
    def __init__(self):
        pass

    def extract_fields(
        self,
        raw_text: str,
        tokens: List[OCRToken],
        category_code: str,
        surface_type: str
    ) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        def find_bbox(pattern: str) -> Optional[List[int]]:
            for token in tokens:
                if re.search(pattern, token.text, re.IGNORECASE):
                    return token.bbox
            return None

        def get_best_bbox_and_conf(pattern: str) -> tuple[Optional[List[int]], float]:
            for token in tokens:
                if re.search(pattern, token.text, re.IGNORECASE):
                    return token.bbox, token.confidence
            return None, 0.90

        # -------------------------------------------------------------
        # 1. PRODUCT / COMMODITY NAME (Rule 6(1)(a))
        # -------------------------------------------------------------
        product_name = None
        product_name_bbox = None
        product_name_conf = 0.0

        brand_matches = []
        for line in lines:
            if re.search(r"\b(daawat|devaaya|britannia|parle|amul|tata|nestle|itc|fortune|haldiram|cadbury|lays|kurkure|saffola|aashirvaad|everest|catch)\b", line, re.IGNORECASE):
                brand_matches.append(line)

        commodity_match = re.search(r"(?:ingredient|commodity|product)\s*[:\-]?\s*([^\n\r,]+)", raw_text, re.IGNORECASE)

        if brand_matches:
            if len(brand_matches) >= 2:
                product_name = f"{brand_matches[0]} - {brand_matches[1]}"
            else:
                product_name = brand_matches[0]
            if commodity_match and commodity_match.group(1).strip().lower() not in product_name.lower():
                product_name += f" ({commodity_match.group(1).strip()})"
            product_name_bbox, product_name_conf = get_best_bbox_and_conf(r"daawat|devaaya|britannia|parle|amul|tata|nestle|itc")
        elif commodity_match:
            product_name = commodity_match.group(1).strip()
            product_name_bbox, product_name_conf = get_best_bbox_and_conf(r"ingredient|commodity|product")
        elif lines:
            for l in lines[:5]:
                if len(l) > 3 and not re.search(r"^(mrp|net|pkd|mfg|lic|batch|nutrition|serving|total|saturated)", l, re.IGNORECASE):
                    product_name = l
                    product_name_bbox, product_name_conf = get_best_bbox_and_conf(re.escape(l[:6]))
                    break

        if product_name:
            results["product_name"] = {
                "value": product_name,
                "confidence": max(0.88, product_name_conf),
                "bbox": product_name_bbox or (tokens[0].bbox if tokens else None),
                "status": "DETECTED"
            }
        else:
            results["product_name"] = {
                "value": None,
                "confidence": 0.0,
                "bbox": None,
                "status": "NOT_DETECTED"
            }

        # -------------------------------------------------------------
        # 2. NET QUANTITY (Rule 6(1)(d))
        # -------------------------------------------------------------
        net_qty = None
        net_bbox = None
        net_conf = 0.90

        # Check for promotional combinations: "50g+19g=69g" or "50g+10g=60g"
        combo_match = re.search(r"(\d+\s*(?:g|kg|ml|l)\s*\+\s*\d+\s*(?:g|kg|ml|l)\s*=\s*\d+\s*(?:g|kg|ml|l))", raw_text, re.IGNORECASE)
        if combo_match:
            net_qty = combo_match.group(1).strip()
            net_bbox, net_conf = get_best_bbox_and_conf(r"\d+\s*(?:g|kg)\s*\+")

        # Priority 1: Explicit "Net Weight: ...", "Net Quantity: ...", "Net Qty: ...", "Net Wt: ...", "Net Contents: ..."
        if not net_qty:
            explicit_net = re.search(
                r"(?:net\s*(?:quantity|weight|volume|contents?|qty|wt)\s*[:\-]?\s*)(\d+(?:\.\d+)?\s*(?:kg|g|gm|gms|mg|l|ml|m|cm|mm|units?|pieces?|pcs?|n|u)\b)",
                raw_text, re.IGNORECASE
            )
            if explicit_net:
                net_qty = explicit_net.group(1).strip()
                net_bbox, net_conf = get_best_bbox_and_conf(r"net\s*(?:weight|quantity|qty|wt|contents?)")

        # Priority 2: "Net: X kg/g/ml"
        if not net_qty:
            short_net = re.search(
                r"(?:net\s*[:\-]\s*)(\d+(?:\.\d+)?\s*(?:kg|g|gm|gms|mg|l|ml)\b)",
                raw_text, re.IGNORECASE
            )
            if short_net:
                net_qty = short_net.group(1).strip()
                net_bbox, net_conf = get_best_bbox_and_conf(r"net")

        # Priority 3: Quantity near "Serving per package" calculation
        if not net_qty:
            servings = re.search(r"serving(?:s)?\s*per\s*package\s*[:\-]?\s*(\d+)", raw_text, re.IGNORECASE)
            size = re.search(r"serving\s*size\s*[:\-]?\s*(?:approx\.?)?\s*(\d+(?:\.\d+)?)\s*(?:g|gm|ml)", raw_text, re.IGNORECASE)
            if servings and size:
                calculated_net = float(servings.group(1)) * float(size.group(1))
                net_qty = f"{calculated_net/1000:.1f} kg ({int(calculated_net)} g)" if calculated_net >= 1000 else f"{int(calculated_net)} g"
                net_bbox, net_conf = get_best_bbox_and_conf(r"serving")

        # Fallback: Bare quantity declaration only if not inside nutritional table
        if not net_qty:
            for line in lines:
                if not re.search(r"(?:fat|protein|sugar|carbohydrate|sodium|cholesterol|energy|calcium|water|serving)", line, re.IGNORECASE):
                    bare_match = re.search(r"\b(\d+(?:\.\d+)?\s*(?:kg|g|l|ml)\b)", line, re.IGNORECASE)
                    if bare_match:
                        net_qty = bare_match.group(1).strip()
                        net_bbox, net_conf = get_best_bbox_and_conf(re.escape(net_qty[:4]))
                        break

        # Normalize unit spacing: e.g. "1Kg" -> "1 kg"
        if net_qty:
            net_qty = re.sub(r"(\d+(?:\.\d+)?)\s*([a-zA-Z]+)", r"\1 \2", net_qty)
            results["net_quantity"] = {
                "value": net_qty,
                "confidence": max(0.88, net_conf),
                "bbox": net_bbox or find_bbox(r"net|weight|qty|kg|g"),
                "status": "DETECTED"
            }
        else:
            results["net_quantity"] = {
                "value": None,
                "confidence": 0.0,
                "bbox": None,
                "status": "NOT_DETECTED"
            }

        # -------------------------------------------------------------
        # 3. MAXIMUM RETAIL PRICE (MRP) (Rule 6(1)(e))
        # -------------------------------------------------------------
        mrp_val = None
        mrp_bbox = None
        mrp_conf = 0.90

        # Pattern 1: Direct MRP with price on same or next line: "MRP.10.00", "MRP: Rs. 40.00", "MRP Rs. 10.00 (Incl. of all taxes)"
        mrp_direct = re.search(
            r"(?:m\.?r\.?p\.?|max(?:imum)?\s*retail\s*price)[\s.:\-]*((?:rs\.?|₹|inr)?\s*\d+(?:\.\d{1,2})?)(?:\s*([^\n\r]*))?",
            raw_text, re.IGNORECASE
        )
        if mrp_direct and mrp_direct.group(1).strip():
            price_digits = re.sub(r"[^0-9.]", "", mrp_direct.group(1))
            extra_part = mrp_direct.group(2) or ""
            has_tax = bool(re.search(r"(?:incl|inclusive)", extra_part, re.IGNORECASE) or re.search(r"\((?:l|i)nclusive\s*of\s*all\s*taxes\)", raw_text, re.IGNORECASE))
            mrp_val = f"MRP Rs. {price_digits}{' (Incl. of all taxes)' if has_tax else ''}"
            mrp_bbox, mrp_conf = get_best_bbox_and_conf(r"m\.?r\.?p|retail")

        # Pattern 2: Statutory Preprinted Clause "MAX. RETAIL PRICE: (Inclusive of all taxes)"
        if not mrp_val:
            mrp_statutory = re.search(
                r"(?:m\.?r\.?p\.?|max(?:imum)?\.?\s*retail\s*price)[\s.:\-]*\n?\s*\((?:l|i)nclusive\s*of\s*all\s*taxes\)",
                raw_text, re.IGNORECASE
            )
            if mrp_statutory:
                stamped_price = re.search(r"(?:rs\.?|₹|inr)\s*(\d+(?:\.\d{1,2})?)", raw_text, re.IGNORECASE)
                if stamped_price:
                    mrp_val = f"MRP Rs. {stamped_price.group(1)} (Inclusive of all taxes)"
                else:
                    mrp_val = "MRP (Inclusive of all taxes)"
                mrp_bbox, mrp_conf = get_best_bbox_and_conf(r"retail|taxes|price")

        # Pattern 3: Solitary price figure with currency symbol e.g. "Rs. 40.00"
        if not mrp_val:
            solitary_price = re.search(r"(?:₹|rs\.?|inr)\s*(\d+(?:\.\d{1,2})?)", raw_text, re.IGNORECASE)
            if solitary_price:
                mrp_val = f"Rs. {solitary_price.group(1)}"
                mrp_bbox, mrp_conf = get_best_bbox_and_conf(r"₹|rs")

        if mrp_val:
            results["mrp"] = {
                "value": mrp_val,
                "confidence": max(0.90, mrp_conf),
                "bbox": mrp_bbox or find_bbox(r"m\.?r\.?p|retail|price"),
                "status": "DETECTED"
            }
        else:
            results["mrp"] = {
                "value": None,
                "confidence": 0.0,
                "bbox": None,
                "status": "NOT_DETECTED"
            }

        # -------------------------------------------------------------
        # 4. UNIT SALE PRICE (USP) (Rule 6(1)(n))
        # -------------------------------------------------------------
        usp_val = None
        usp_bbox = None
        usp_conf = 0.90

        usp_match = re.search(
            r"((?:unit\s*sale\s*price|u\.?s\.?p\.?|rs\.?|₹)?[\s.:\-]*\d+(?:\.\d{1,2})?\s*(?:per|\/)\s*(?:g|kg|ml|l|unit|n))",
            raw_text, re.IGNORECASE
        )
        if usp_match:
            usp_val = usp_match.group(1).strip()
            # Clean formatting e.g. "Rs.0.17perg" -> "Rs. 0.17 per g"
            usp_val = re.sub(r"rs\.?(\d)", r"Rs. \1", usp_val, flags=re.IGNORECASE)
            usp_val = re.sub(r"per([a-zA-Z]+)", r"per \1", usp_val, flags=re.IGNORECASE)
            usp_bbox, usp_conf = get_best_bbox_and_conf(r"usp|unit|per")

        if usp_val:
            results["unit_sale_price"] = {
                "value": usp_val,
                "confidence": max(0.88, usp_conf),
                "bbox": usp_bbox or find_bbox(r"per|\/"),
                "status": "DETECTED"
            }
        else:
            results["unit_sale_price"] = {
                "value": None,
                "confidence": 0.0,
                "bbox": None,
                "status": "NOT_DETECTED"
            }

        # -------------------------------------------------------------
        # 5. MANUFACTURER / PACKER / MARKETED BY (Rule 6(1)(b))
        # -------------------------------------------------------------
        mfg_val = None
        mfg_bbox = None
        mfg_conf = 0.90

        # Pattern 1: Known FMCG corporate entity name with address or plant location
        corp_match = re.search(
            r"((?:LT\s*Foods|Britannia\s*Industries|Parle\s*Products|Tata\s*Consumer|Nestle\s*India|ITC|Hindustan\s*Unilever)[^\n\r]*(?:Limited|Ltd)[^\n\r]*(?:\n[^\n\r]+){1,3})",
            raw_text, re.IGNORECASE
        )
        if corp_match:
            mfg_val = " ".join(corp_match.group(1).split())
            mfg_bbox, mfg_conf = get_best_bbox_and_conf(r"ltd|limited|industries|foods")

        # Pattern 2: "Marketed by:" or "Manufactured by:" lines
        if not mfg_val:
            mfg_lines = []
            for i, line in enumerate(lines):
                if re.search(r"^(?:marketed|manufactured|packed|mfg)\s*(?:&|and)?\s*(?:packed)?\s*by\s*[:\-]?", line, re.IGNORECASE):
                    following = [l for l in lines[i:min(len(lines), i + 4)] if not re.search(r"(?:fat|protein|sugar|energy|cholesterol|carbohydrate|\b\d+\.\d+\b)", l, re.IGNORECASE)]
                    if following:
                        mfg_lines.extend(following)
                        break
            if mfg_lines:
                mfg_val = " ".join(mfg_lines)
                mfg_bbox, mfg_conf = get_best_bbox_and_conf(r"marketed|manufactured|packed")

        # Pattern 3: Any entity with "Pvt Ltd" or "Limited"
        if not mfg_val:
            generic_corp = re.search(r"([A-Za-z0-9\s&]+(?:Foods|Industries|Products|Beverages)\s*(?:Pvt\.?|Private)?\s*(?:Ltd\.?|Limited)[A-Za-z0-9\s,\-]*)", raw_text, re.IGNORECASE)
            if generic_corp:
                mfg_val = generic_corp.group(1).strip()
                mfg_bbox, mfg_conf = get_best_bbox_and_conf(r"ltd|limited")

        if mfg_val:
            results["manufacturer_packer"] = {
                "value": mfg_val,
                "confidence": max(0.90, mfg_conf),
                "bbox": mfg_bbox or find_bbox(r"marketed|manufactured|packed|ltd"),
                "status": "DETECTED"
            }
        else:
            results["manufacturer_packer"] = {
                "value": None,
                "confidence": 0.0,
                "bbox": None,
                "status": "NOT_DETECTED"
            }

        # -------------------------------------------------------------
        # 6. COUNTRY OF ORIGIN (Rule 6(1)(c))
        # -------------------------------------------------------------
        origin_val = None
        origin_bbox = None
        origin_conf = 0.90

        origin_match = re.search(r"(?:country\s*of\s*origin|made\s*in|product\s*of|productofindia|madeinindia)\s*[:\-]?\s*([A-Za-z\s]+)", raw_text, re.IGNORECASE)
        if origin_match:
            raw_orig = origin_match.group(0).lower()
            if "india" in raw_orig:
                origin_val = "India"
            else:
                origin_val = origin_match.group(1).strip()
            origin_bbox, origin_conf = get_best_bbox_and_conf(r"india|origin|productof")
        elif re.search(r"\b(india|bharat)\b", raw_text, re.IGNORECASE):
            origin_val = "India"
            origin_bbox, origin_conf = get_best_bbox_and_conf(r"india")

        if origin_val:
            results["country_of_origin"] = {
                "value": origin_val,
                "confidence": max(0.90, origin_conf),
                "bbox": origin_bbox or find_bbox(r"india"),
                "status": "DETECTED"
            }
        else:
            results["country_of_origin"] = {
                "value": None,
                "confidence": 0.0,
                "bbox": None,
                "status": "NOT_DETECTED"
            }

        # -------------------------------------------------------------
        # 7. MANUFACTURING / PACKING DATE (Rule 6(1)(f))
        # -------------------------------------------------------------
        date_val = None
        date_bbox = None
        date_conf = 0.88

        # Explicit date tags (excluding "packed by" / "manufactured by" which refer to companies)
        explicit_date = re.search(
            r"((?:date\s*of\s*(?:packaging|packing|mfg)|pkd|mfd|use\s*by|useby|best\s*before)[\s.:\-]*\n?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{2}[/-]\d{4}))",
            raw_text, re.IGNORECASE
        )
        if explicit_date:
            date_val = explicit_date.group(0).strip()
            date_bbox, date_conf = get_best_bbox_and_conf(r"pkd|mfd|use\s*by|useby|packaging")
        else:
            date_header = re.search(r"(?:date\s*of\s*(?:packaging|packing|mfg)|pkd|mfd|use\s*by|useby)[\s.:\-]*", raw_text, re.IGNORECASE)
            date_standalone = re.search(r"\b(\d{2}[/-]\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b", raw_text)
            if date_standalone:
                prefix = date_header.group(0).strip() if date_header else "PKD"
                date_val = f"{prefix} {date_standalone.group(1)}"
                date_bbox, date_conf = get_best_bbox_and_conf(r"\d{2}[/-]")
            elif date_header:
                date_val = date_header.group(0).strip()
                date_bbox, date_conf = get_best_bbox_and_conf(r"packaging|packing|pkd|mfd")

        if date_val:
            results["mfg_packing_date"] = {
                "value": date_val,
                "confidence": max(0.85, date_conf),
                "bbox": date_bbox or find_bbox(r"date|pkd|mfg|use\s*by"),
                "status": "DETECTED"
            }
        else:
            results["mfg_packing_date"] = {
                "value": None,
                "confidence": 0.0,
                "bbox": None,
                "status": "NOT_DETECTED"
            }

        # -------------------------------------------------------------
        # 8. CONSUMER CARE CELL (Rule 6(2))
        # -------------------------------------------------------------
        care_val = None
        care_bbox = None
        care_conf = 0.90

        care_match = re.search(
            r"((?:consumer\s*care|customer\s*care|care\s*cell|helpline|toll\s*free|feedback)[^\n\r]+(?:\n[^\n\r]+){0,2})",
            raw_text, re.IGNORECASE
        )
        email_phone = re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+|1800[-\s]?\d{3}[-\s]?\d{3,4}|1-800[-\s]?\d{3}[-\s]?\d{4})", raw_text)

        if care_match:
            care_val = " ".join(care_match.group(1).split())
            care_bbox, care_conf = get_best_bbox_and_conf(r"consumer|care|feedback")
        elif email_phone:
            care_val = f"Consumer Helpline / Contact: {email_phone.group(0)}"
            care_bbox, care_conf = get_best_bbox_and_conf(r"@|1800|1-800")

        if care_val:
            results["consumer_care"] = {
                "value": care_val,
                "confidence": max(0.90, care_conf),
                "bbox": care_bbox or find_bbox(r"consumer|care|feedback"),
                "status": "DETECTED"
            }
        else:
            results["consumer_care"] = {
                "value": None,
                "confidence": 0.0,
                "bbox": None,
                "status": "NOT_DETECTED"
            }

        return results
