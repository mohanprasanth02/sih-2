"""
LabelGuard AI - Database Seeding Script (SIH26034)
Seeds official Legal Metrology Rules, default users, categories, and demo inspections.
All demo inspection records are strictly marked with is_demo = True.
"""
import os
import sys
from datetime import datetime, timezone, timedelta

# Ensure python path includes project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from services.api.security import hash_password
from services.api.database import SessionLocal, engine, Base
from services.api.models import (
    User, ProductCategory, Product, ComplianceRule, Inspection,
    InspectionImage, ExtractedField, RuleResult, ConflictItem, AuditLog
)
from rules.legal_metrology.rules_data import OFFICIAL_LEGAL_METROLOGY_RULES

def seed():
    # Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("🌱 Seeding Users...")
        users = [
            {
                "id": "usr-inspector-01",
                "email": "inspector@legalmetrology.gov.in",
                "full_name": "Rajesh Sharma (Inspector)",
                "role": "inspector",
                "organization": "Legal Metrology Dept, Delhi Zone",
                "hashed_password": hash_password("Inspector@123"),
            },
            {
                "id": "usr-supervisor-01",
                "email": "supervisor@legalmetrology.gov.in",
                "full_name": "Priya V. Iyer (Senior Assistant Controller)",
                "role": "supervisor",
                "organization": "Department of Consumer Affairs",
                "hashed_password": hash_password("Supervisor@123"),
            },
            {
                "id": "usr-admin-01",
                "email": "admin@legalmetrology.gov.in",
                "full_name": "Anil K. Verma (Directorate Admin)",
                "role": "admin",
                "organization": "National Legal Metrology Portal",
                "hashed_password": hash_password("Admin@123"),
            },
            {
                "id": "usr-viewer-01",
                "email": "viewer@legalmetrology.gov.in",
                "full_name": "Suresh Nair (Verification Officer / Public Viewer)",
                "role": "viewer",
                "organization": "Regional Metrology Office",
                "hashed_password": hash_password("Viewer@123"),
            }
        ]

        for u in users:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if not existing:
                db.add(User(**u))
        db.commit()

        print("🌱 Seeding Product Categories...")
        categories = [
            {
                "code": "food",
                "name": "Packaged Food & Beverages",
                "description": "Edible packaged goods, snacks, beverages subject to FSSAI & Legal Metrology Rules",
                "required_fields": ["product_name", "net_quantity", "mrp", "unit_sale_price", "manufacturer_packer", "mfg_packing_date", "consumer_care"]
            },
            {
                "code": "cosmetics",
                "name": "Cosmetics & Personal Care",
                "description": "Lotions, soaps, perfumes, toiletries, skincare commodities",
                "required_fields": ["product_name", "net_quantity", "mrp", "unit_sale_price", "manufacturer_packer", "mfg_packing_date", "consumer_care"]
            },
            {
                "code": "household",
                "name": "Household & Cleaning Products",
                "description": "Detergents, disinfectants, paper goods, household chemicals",
                "required_fields": ["product_name", "net_quantity", "mrp", "unit_sale_price", "manufacturer_packer", "mfg_packing_date", "consumer_care"]
            },
            {
                "code": "textiles",
                "name": "Textiles & Garments",
                "description": "Apparel, fabrics, yarns, bedsheets, measuring in meter/number",
                "required_fields": ["product_name", "net_quantity", "mrp", "manufacturer_packer", "consumer_care"]
            },
            {
                "code": "electronics",
                "name": "Packaged Consumer Electronics",
                "description": "Cables, chargers, appliances, mobile accessories",
                "required_fields": ["product_name", "net_quantity", "mrp", "manufacturer_packer", "country_of_origin", "consumer_care"]
            },
            {
                "code": "imported",
                "name": "Imported Packaged Commodities",
                "description": "Any commodity pre-packed abroad and imported into India",
                "required_fields": ["product_name", "net_quantity", "mrp", "unit_sale_price", "manufacturer_packer", "country_of_origin", "mfg_packing_date", "consumer_care"]
            }
        ]

        for c in categories:
            existing = db.query(ProductCategory).filter(ProductCategory.code == c["code"]).first()
            if not existing:
                db.add(ProductCategory(**c))
        db.commit()

        print("🌱 Seeding Official Legal Metrology (Packaged Commodities) Rules 2011...")
        for r in OFFICIAL_LEGAL_METROLOGY_RULES:
            existing = db.query(ComplianceRule).filter(ComplianceRule.code == r["code"]).first()
            if not existing:
                db.add(ComplianceRule(
                    code=r["code"],
                    title=r["title"],
                    legal_reference=r["legal_reference"],
                    applicable_categories=r["applicable_categories"],
                    severity=r["severity"],
                    version=r["version"],
                    description=r["description"],
                    condition_json=r["condition"]
                ))
        db.commit()

        print("🌱 Seeding Demo Inspections (marked is_demo=True)...")
        now = datetime.now(timezone.utc)

        # Demo 1: Compliant Food Package
        insp_1 = db.query(Inspection).filter(Inspection.id == "LG-2026-09-000101").first()
        if not insp_1:
            insp_1 = Inspection(
                id="LG-2026-09-000101",
                inspector_id="usr-inspector-01",
                product_name="Britannia Good Day Butter Cookies",
                brand="Britannia",
                category_code="food",
                status="COMPLIANT",
                latitude=28.6139,
                longitude=77.2090,
                address="Connaught Place Market, New Delhi",
                is_demo=True,
                created_at=now - timedelta(days=2),
                updated_at=now - timedelta(days=2)
            )
            db.add(insp_1)
            db.flush()

            img1 = InspectionImage(
                id="img-demo-01-front",
                inspection_id=insp_1.id,
                surface_type="front",
                file_path="uploads/demo/britannia_front.jpg",
                original_filename="good_day_front.jpg",
                blur_score=145.2,
                brightness_score=138.4,
                quality_status="SUFFICIENT",
                width=1280,
                height=960
            )
            img2 = InspectionImage(
                id="img-demo-01-back",
                inspection_id=insp_1.id,
                surface_type="back",
                file_path="uploads/demo/britannia_back.jpg",
                original_filename="good_day_back.jpg",
                blur_score=162.0,
                brightness_score=142.1,
                quality_status="SUFFICIENT",
                width=1280,
                height=960
            )
            db.add_all([img1, img2])
            db.flush()

            fields_1 = [
                ExtractedField(
                    inspection_id=insp_1.id, image_id=img1.id,
                    field_name="product_name", detected_value="Britannia Good Day Butter Cookies",
                    confidence=0.98, bbox=[45, 120, 110, 480], status="DETECTED"
                ),
                ExtractedField(
                    inspection_id=insp_1.id, image_id=img1.id,
                    field_name="net_quantity", detected_value="200 g",
                    confidence=0.97, bbox=[280, 80, 320, 220], status="DETECTED"
                ),
                ExtractedField(
                    inspection_id=insp_1.id, image_id=img2.id,
                    field_name="mrp", detected_value="MRP Rs. 40.00 incl. of all taxes",
                    confidence=0.96, bbox=[310, 320, 350, 560], status="DETECTED"
                ),
                ExtractedField(
                    inspection_id=insp_1.id, image_id=img2.id,
                    field_name="unit_sale_price", detected_value="₹0.20 per g",
                    confidence=0.94, bbox=[360, 320, 395, 480], status="DETECTED"
                ),
                ExtractedField(
                    inspection_id=insp_1.id, image_id=img2.id,
                    field_name="manufacturer_packer", detected_value="Britannia Industries Ltd., 5/1A Hungerford Street, Kolkata - 700017, West Bengal",
                    confidence=0.95, bbox=[410, 60, 490, 620], status="DETECTED"
                ),
                ExtractedField(
                    inspection_id=insp_1.id, image_id=img2.id,
                    field_name="mfg_packing_date", detected_value="PKD 08/2026",
                    confidence=0.93, bbox=[505, 120, 535, 290], status="DETECTED"
                ),
                ExtractedField(
                    inspection_id=insp_1.id, image_id=img2.id,
                    field_name="consumer_care", detected_value="Feedback: 1800-425-4449 or feedback@britindia.com",
                    confidence=0.96, bbox=[550, 60, 590, 540], status="DETECTED"
                )
            ]
            db.add_all(fields_1)

            results_1 = [
                RuleResult(
                    inspection_id=insp_1.id, rule_code="LM-RULE-001",
                    title="Common or Generic Commodity Name", legal_reference="Rule 6(1)(a)",
                    status="PASS", reason="Generic name 'Britannia Good Day Butter Cookies' clearly declared on front surface.",
                    confidence=0.98
                ),
                RuleResult(
                    inspection_id=insp_1.id, rule_code="LM-RULE-004",
                    title="Net Quantity in Standard Units", legal_reference="Rule 6(1)(d)",
                    status="PASS", reason="Standard SI unit '200 g' declared without prohibited plural abbreviations.",
                    confidence=0.97
                ),
                RuleResult(
                    inspection_id=insp_1.id, rule_code="LM-RULE-005",
                    title="Maximum Retail Price (MRP) Declaration", legal_reference="Rule 6(1)(e)",
                    status="PASS", reason="MRP declared with statutory clause 'incl. of all taxes'.",
                    confidence=0.96
                ),
                RuleResult(
                    inspection_id=insp_1.id, rule_code="LM-RULE-006",
                    title="Unit Sale Price (USP) Declaration", legal_reference="Rule 6(1)(n)",
                    status="PASS", reason="Unit Sale Price declared as ₹0.20 per g matches calculated rate (₹40.00 / 200g).",
                    confidence=0.94
                )
            ]
            db.add_all(results_1)

        # Demo 2: Needs Review (Low OCR confidence on date)
        insp_2 = db.query(Inspection).filter(Inspection.id == "LG-2026-09-000102").first()
        if not insp_2:
            insp_2 = Inspection(
                id="LG-2026-09-000102",
                inspector_id="usr-inspector-01",
                product_name="Nivea Soft Light Moisturiser",
                brand="Nivea",
                category_code="cosmetics",
                status="NEEDS_REVIEW",
                latitude=19.0760,
                longitude=72.8777,
                address="Bandra West Supermarket, Mumbai",
                is_demo=True,
                created_at=now - timedelta(days=1),
                updated_at=now - timedelta(hours=3)
            )
            db.add(insp_2)
            db.flush()

            img3 = InspectionImage(
                id="img-demo-02-front",
                inspection_id=insp_2.id,
                surface_type="front",
                file_path="uploads/demo/nivea_front.jpg",
                original_filename="nivea_front.jpg",
                blur_score=85.4,
                brightness_score=110.0,
                quality_status="WARNING",
                quality_notes="Slight specular glare on bottom edge",
                width=1080,
                height=1080
            )
            db.add(img3)
            db.flush()

            fields_2 = [
                ExtractedField(
                    inspection_id=insp_2.id, image_id=img3.id,
                    field_name="product_name", detected_value="Nivea Soft Light Moisturiser",
                    confidence=0.96, bbox=[60, 100, 120, 520], status="DETECTED"
                ),
                ExtractedField(
                    inspection_id=insp_2.id, image_id=img3.id,
                    field_name="net_quantity", detected_value="100 ml",
                    confidence=0.94, bbox=[240, 120, 275, 260], status="DETECTED"
                ),
                ExtractedField(
                    inspection_id=insp_2.id, image_id=img3.id,
                    field_name="mrp", detected_value="MRP Rs. 195.00 incl. of all taxes",
                    confidence=0.91, bbox=[320, 180, 360, 480], status="DETECTED"
                ),
                ExtractedField(
                    inspection_id=insp_2.id, image_id=img3.id,
                    field_name="mfg_packing_date", detected_value="B.No 442? / 0?25",
                    confidence=0.58, bbox=[410, 150, 450, 320], status="LOW_CONFIDENCE"
                )
            ]
            db.add_all(fields_2)

            results_2 = [
                RuleResult(
                    inspection_id=insp_2.id, rule_code="LM-RULE-007",
                    title="Month & Year of Manufacture / Packing", legal_reference="Rule 6(1)(f)",
                    status="MANUAL_REVIEW", reason="OCR confidence for date of manufacture is 58% (below 70% threshold). Manual verification required.",
                    confidence=0.58
                )
            ]
            db.add_all(results_2)

        # Demo 3: Imported Commodity Non-Compliant (Missing Country of Origin & USP)
        insp_3 = db.query(Inspection).filter(Inspection.id == "LG-2026-09-000103").first()
        if not insp_3:
            insp_3 = Inspection(
                id="LG-2026-09-000103",
                inspector_id="usr-inspector-01",
                product_name="Pro Wireless Stereo Headset",
                brand="SonicSound",
                category_code="imported",
                status="NON_COMPLIANT",
                latitude=12.9716,
                longitude=77.5946,
                address="Brigade Road Electronics Hub, Bengaluru",
                is_demo=True,
                created_at=now - timedelta(hours=14),
                updated_at=now - timedelta(hours=14)
            )
            db.add(insp_3)
            db.flush()

            img4 = InspectionImage(
                id="img-demo-03-back",
                inspection_id=insp_3.id,
                surface_type="back",
                file_path="uploads/demo/headset_back.jpg",
                original_filename="headset_back.jpg",
                blur_score=150.0,
                brightness_score=140.0,
                quality_status="SUFFICIENT",
                width=1280,
                height=960
            )
            db.add(img4)
            db.flush()

            fields_3 = [
                ExtractedField(
                    inspection_id=insp_3.id, image_id=img4.id,
                    field_name="product_name", detected_value="SonicSound Wireless Headset",
                    confidence=0.97, bbox=[50, 100, 110, 480], status="DETECTED"
                ),
                ExtractedField(
                    inspection_id=insp_3.id, image_id=img4.id,
                    field_name="net_quantity", detected_value="1 N",
                    confidence=0.95, bbox=[130, 80, 160, 180], status="DETECTED"
                ),
                ExtractedField(
                    inspection_id=insp_3.id, image_id=img4.id,
                    field_name="mrp", detected_value="MRP Rs. 2499.00", # Missing tax clause
                    confidence=0.96, bbox=[200, 120, 240, 360], status="DETECTED"
                ),
                ExtractedField(
                    inspection_id=insp_3.id, image_id=img4.id,
                    field_name="country_of_origin", detected_value=None,
                    confidence=0.0, bbox=None, status="NOT_DETECTED"
                )
            ]
            db.add_all(fields_3)

            results_3 = [
                RuleResult(
                    inspection_id=insp_3.id, rule_code="LM-RULE-003",
                    title="Country of Origin Declaration", legal_reference="Rule 6(1)(c)",
                    status="FAIL", reason="Mandatory Country of Origin is absent on imported commodity package.",
                    confidence=0.99
                ),
                RuleResult(
                    inspection_id=insp_3.id, rule_code="LM-RULE-005",
                    title="Maximum Retail Price (MRP) Declaration", legal_reference="Rule 6(1)(e)",
                    status="FAIL", reason="Statutory clause 'inclusive of all taxes' or 'incl. of all taxes' is missing.",
                    confidence=0.96
                )
            ]
            db.add_all(results_3)

        # Demo 4: Conflict Detected (Front says 500 g, Back says 450 g)
        insp_4 = db.query(Inspection).filter(Inspection.id == "LG-2026-09-000104").first()
        if not insp_4:
            insp_4 = Inspection(
                id="LG-2026-09-000104",
                inspector_id="usr-inspector-01",
                product_name="Heritage Organic Rice Flour",
                brand="Heritage Farms",
                category_code="food",
                status="NON_COMPLIANT",
                latitude=17.3850,
                longitude=78.4867,
                address="Banjara Hills Organic Store, Hyderabad",
                is_demo=True,
                created_at=now - timedelta(hours=5),
                updated_at=now - timedelta(hours=5)
            )
            db.add(insp_4)
            db.flush()

            img5 = InspectionImage(
                id="img-demo-04-front",
                inspection_id=insp_4.id,
                surface_type="front",
                file_path="uploads/demo/flour_front.jpg",
                original_filename="flour_front.jpg",
                blur_score=142.0,
                brightness_score=135.0,
                quality_status="SUFFICIENT",
                width=1000,
                height=1000
            )
            img6 = InspectionImage(
                id="img-demo-04-back",
                inspection_id=insp_4.id,
                surface_type="back",
                file_path="uploads/demo/flour_back.jpg",
                original_filename="flour_back.jpg",
                blur_score=139.0,
                brightness_score=132.0,
                quality_status="SUFFICIENT",
                width=1000,
                height=1000
            )
            db.add_all([img5, img6])
            db.flush()

            fields_4 = [
                ExtractedField(
                    inspection_id=insp_4.id, image_id=img5.id,
                    field_name="product_name", detected_value="Heritage Organic Rice Flour",
                    confidence=0.98, bbox=[80, 100, 140, 520], status="DETECTED"
                ),
                ExtractedField(
                    inspection_id=insp_4.id, image_id=img5.id,
                    field_name="net_quantity", detected_value="500 g",
                    confidence=0.97, bbox=[320, 140, 360, 240], status="DETECTED"
                ),
                ExtractedField(
                    inspection_id=insp_4.id, image_id=img6.id,
                    field_name="net_quantity", detected_value="450 g",
                    confidence=0.95, bbox=[340, 200, 380, 300], status="DETECTED"
                )
            ]
            db.add_all(fields_4)

            conflict = ConflictItem(
                inspection_id=insp_4.id,
                field_name="net_quantity",
                surface_a="front",
                value_a="500 g",
                surface_b="back",
                value_b="450 g",
                reason="Cross-surface discrepancy: Front package face declares '500 g' but Back package face declares '450 g'."
            )
            db.add(conflict)

            results_4 = [
                RuleResult(
                    inspection_id=insp_4.id, rule_code="LM-RULE-010",
                    title="Cross-Surface Package Declaration Consistency", legal_reference="Rule 10",
                    status="FAIL", reason="Conflict detected: Disparate net quantity values across front and back surfaces (500 g vs 450 g). Deceptive declaration under Rule 10.",
                    confidence=0.99
                )
            ]
            db.add_all(results_4)

        # Seed Laboratories
        print("🌱 Seeding Official Metrology Laboratories...")
        from services.api.models import Laboratory, Manufacturer, RuleVersion
        labs = [
            {
                "id": "lab-nlmtel-delhi",
                "code": "NLMTEL-DELHI",
                "name": "National Legal Metrology Type Evaluation Laboratory",
                "address": "Krishi Bhawan, Dr. Rajendra Prasad Road, New Delhi - 110001",
                "accreditation": "NABL ISO/IEC 17025 Accredited & OIML Issuing Authority (OIML-CS)",
                "contact_email": "director-lm@nic.in",
                "contact_phone": "+91 11 2338 9447",
                "is_active": True
            },
            {
                "id": "lab-rrsl-ahmedabad",
                "code": "RRSL-AHMEDABAD",
                "name": "Regional Reference Standard Laboratory (RRSL), Ahmedabad",
                "address": "Near Government Polytechnic, Ambawadi, Ahmedabad, Gujarat - 380015",
                "accreditation": "NABL ISO/IEC 17025 Accredited Metrological Testing Laboratory",
                "contact_email": "rrsl-ahmedabad@gov.in",
                "contact_phone": "+91 79 2630 1145",
                "is_active": True
            },
            {
                "id": "lab-rrsl-bangalore",
                "code": "RRSL-BANGALORE",
                "name": "Regional Reference Standard Laboratory (RRSL), Bangalore",
                "address": "PB No 5845, Peenya Industrial Area, Bangalore, Karnataka - 560058",
                "accreditation": "NABL ISO/IEC 17025 Accredited Metrological Testing Laboratory",
                "contact_email": "rrsl-bangalore@gov.in",
                "contact_phone": "+91 80 2839 4922",
                "is_active": True
            }
        ]
        for l in labs:
            if not db.query(Laboratory).filter(Laboratory.id == l["id"]).first():
                db.add(Laboratory(**l))

        # Seed Manufacturers
        print("🌱 Seeding Weighing Instrument Manufacturers...")
        manufacturers = [
            {
                "id": "mfg-metler-india",
                "name": "Metler Precision Weighing Systems India Pvt Ltd",
                "address": "Plot 44-46, Electronics City Phase II, Bangalore, Karnataka - 560100",
                "country": "India",
                "contact_email": "regulatory@metlerprecision.in",
                "contact_phone": "+91 80 4123 9988",
                "license_number": "LM-IND-MFG-KA-4491"
            },
            {
                "id": "mfg-optima-analytical",
                "name": "Optima Analytical Instruments LLP",
                "address": "Tech Zone IV, Greater Noida West, Uttar Pradesh - 201306",
                "country": "India",
                "contact_email": "compliance@optima-analytical.com",
                "contact_phone": "+91 120 6789 2200",
                "license_number": "LM-IND-MFG-UP-2023-882"
            },
            {
                "id": "mfg-bharat-heavy",
                "name": "Bharat Heavy Weighbridges & Sensorics Ltd",
                "address": "Heavy Machinery Complex, MIDC Bhosari, Pune, Maharashtra - 411026",
                "country": "India",
                "contact_email": "type-approval@bhw-india.com",
                "contact_phone": "+91 20 2712 5599",
                "license_number": "LM-IND-MFG-MH-10294"
            },
            {
                "id": "mfg-standard-inst",
                "name": "Standard Instruments & Metrology Ltd",
                "address": "Plot 12, Metrology Industrial Estate, Pune, Maharashtra - 411026",
                "country": "India",
                "contact_email": "compliance@standardmetrology.in",
                "contact_phone": "+91 20 2712 4400",
                "license_number": "LM-IND-MFG-MH-5521"
            }
        ]
        for m in manufacturers:
            if not db.query(Manufacturer).filter(Manufacturer.id == m["id"]).first():
                db.add(Manufacturer(**m))

        # Seed Rule Versions
        print("🌱 Seeding OIML Rule Versions...")
        rule_versions = [
            {
                "id": "rv-oiml-r76-2006",
                "rule_name": "OIML R 76-1:2006 (E)",
                "rule_version": "2006.1",
                "effective_from": datetime(2006, 10, 1),
                "source_reference": "International Recommendation OIML R 76-1 (Edition 2006)",
                "configuration": {
                    "mpe_table": "Table 6",
                    "scale_interval_table": "Table 3",
                    "initial_verification_mpe": [0.5, 1.0, 1.5],
                    "in_service_multiplier": 2.0,
                    "changeover_point_formula": "E = I + 0.5e - delta_L - L",
                    "corrected_error_formula": "Ec = E - E0"
                },
                "active": True
            },
            {
                "id": "rv-lm-general-2011",
                "rule_name": "Legal Metrology (General) Rules, 2011 - Seventh Schedule",
                "rule_version": "2011.1",
                "effective_from": datetime(2011, 4, 1),
                "source_reference": "The Gazette of India: Extraordinary Part II-Sec 3(i)",
                "configuration": {
                    "standard": "Non-Automatic Weighing Instruments Specifications",
                    "verification_cycle_months": 12,
                    "mandatory_stamping": True
                },
                "active": True
            }
        ]
        for rv in rule_versions:
            if not db.query(RuleVersion).filter(RuleVersion.id == rv["id"]).first():
                db.add(RuleVersion(**rv))

        db.commit()
        print("✅ Database seeding completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
