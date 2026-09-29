"""
LabelGuard AI - Official Legal Metrology (Packaged Commodities) Rules, 2011
Codified Rule Definitions and Statutory Citations
"""

OFFICIAL_LEGAL_METROLOGY_RULES = [
    {
        "code": "LM-RULE-001",
        "title": "Common or Generic Commodity Name",
        "legal_reference": "Rule 6(1)(a)",
        "applicable_categories": ["food", "cosmetics", "household", "textiles", "electronics", "imported", "general"],
        "severity": "CRITICAL",
        "version": "2011.1",
        "description": "Every package shall bear the name and generic or common name of the commodity contained in the package. In case of packages with more than one product, the name and number or quantity of each product shall be specified.",
        "condition": {
            "required_field": "product_name",
            "min_length": 2,
        }
    },
    {
        "code": "LM-RULE-002",
        "title": "Name & Address of Manufacturer / Packer / Importer",
        "legal_reference": "Rule 6(1)(b)",
        "applicable_categories": ["food", "cosmetics", "household", "textiles", "electronics", "imported", "general"],
        "severity": "CRITICAL",
        "version": "2011.1",
        "description": "The name and complete address of the manufacturer, or where manufacturer is not the packer, name and address of manufacturer and packer; and for imported packages, the name and complete address of importer.",
        "condition": {
            "required_field": "manufacturer_packer",
            "min_length": 10,
            "must_contain_any": ["mfg", "manufactured", "packer", "packed", "pvt", "ltd", "address", "road", "street", "industrial", "marketed"]
        }
    },
    {
        "code": "LM-RULE-003",
        "title": "Country of Origin Declaration",
        "legal_reference": "Rule 6(1)(c) & 2017 Amendment",
        "applicable_categories": ["imported"],
        "severity": "CRITICAL",
        "version": "2017.1",
        "description": "Country of origin or manufacture or assembly in case of imported products shall be mentioned prominently on the package.",
        "condition": {
            "required_field": "country_of_origin",
            "required_if_category": ["imported"],
            "must_contain_any": ["country of origin", "origin", "made in", "product of", "india", "china", "usa", "germany", "vietnam", "thailand", "japan"]
        }
    },
    {
        "code": "LM-RULE-004",
        "title": "Net Quantity in Standard Units of Weight/Measure",
        "legal_reference": "Rule 6(1)(d) & Rule 11, Second Schedule",
        "applicable_categories": ["food", "cosmetics", "household", "textiles", "electronics", "imported", "general"],
        "severity": "CRITICAL",
        "version": "2011.1",
        "description": "The net quantity in terms of standard units of weight, measure or number. Units shall be in SI system (g, kg, ml, l, m, N, U). Non-standard units (e.g., gms, kgs, ltr, cu.cm) are prohibited.",
        "condition": {
            "required_field": "net_quantity",
            "standard_units": ["g", "kg", "ml", "l", "m", "cm", "mm", "u", "n", "piece", "pcs"],
            "prohibited_units": ["gm", "gms", "kg.", "kgs", "ltr", "ltrs", "ml."]
        }
    },
    {
        "code": "LM-RULE-005",
        "title": "Maximum Retail Price (MRP) Declaration",
        "legal_reference": "Rule 6(1)(e)",
        "applicable_categories": ["food", "cosmetics", "household", "textiles", "electronics", "imported", "general"],
        "severity": "CRITICAL",
        "version": "2011.1",
        "description": "The retail sale price of the package shall be clearly declared in the format 'Maximum or Max. Retail Price Rs. ... or ₹ ... inclusive of all taxes' or 'MRP Rs./₹ ... incl. of all taxes'.",
        "condition": {
            "required_field": "mrp",
            "must_contain_any": ["mrp", "max retail price", "maximum retail price", "₹", "rs", "inr"],
            "must_contain_taxes_clause": ["incl", "inclusive of all taxes", "incl. of all taxes"]
        }
    },
    {
        "code": "LM-RULE-006",
        "title": "Unit Sale Price (USP) Declaration",
        "legal_reference": "Rule 6(1)(n) & Amendment Rules, 2021",
        "applicable_categories": ["food", "cosmetics", "household", "general"],
        "severity": "MAJOR",
        "version": "2021.2",
        "description": "Unit sale price shall be declared on packages where net quantity is more than 1 kg or 1 litre in terms of ₹ per kg / litre, and for packages less than 1 kg / litre in terms of ₹ per g / ml. Mandatory as per Department of Consumer Affairs Notification G.S.R. 779(E).",
        "condition": {
            "required_field": "unit_sale_price",
            "check_threshold": True
        }
    },
    {
        "code": "LM-RULE-007",
        "title": "Month & Year of Manufacture / Packing / Import",
        "legal_reference": "Rule 6(1)(f)",
        "applicable_categories": ["food", "cosmetics", "household", "textiles", "electronics", "imported", "general"],
        "severity": "CRITICAL",
        "version": "2011.1",
        "description": "The month and year in which the commodity is manufactured or pre-packed or imported shall be declared. Format e.g., MM/YYYY or Month Year.",
        "condition": {
            "required_field": "mfg_packing_date",
            "date_patterns": [r"\b\d{2}[/-]\d{4}\b", r"\b[A-Za-z]{3}[/-]\d{4}\b", r"\b\d{2}[/-]\d{2}[/-]\d{4}\b"]
        }
    },
    {
        "code": "LM-RULE-008",
        "title": "Consumer Care Cell / Grievance Redressal Details",
        "legal_reference": "Rule 6(2)",
        "applicable_categories": ["food", "cosmetics", "household", "textiles", "electronics", "imported", "general"],
        "severity": "MAJOR",
        "version": "2011.1",
        "description": "Name, complete address, telephone number and e-mail address of the person who can be contacted by the consumer in case of complaints or consumer care cell.",
        "condition": {
            "required_field": "consumer_care",
            "must_contain_any": ["consumer care", "customer care", "helpline", "toll free", "feedback", "email", "@", "tel", "phone"]
        }
    },
    {
        "code": "LM-RULE-009",
        "title": "Minimum Font Size / Height Proportionality",
        "legal_reference": "Rule 9, Table 1 & Table 2",
        "applicable_categories": ["food", "cosmetics", "household", "textiles", "electronics", "imported", "general"],
        "severity": "MINOR",
        "version": "2011.1",
        "description": "The height of any numeral and letter in the declaration shall not be less than the minimum height specified under Rule 9 depending on net quantity (e.g., up to 50g: 1.0mm; 50g-200g: 2.0mm; 200g-1kg: 4.0mm; >1kg: 6.0mm). Note: Photographic estimates are advisory and require physical gauge verification.",
        "condition": {
            "check_readability": True,
            "min_character_height_px": 12
        }
    },
    {
        "code": "LM-RULE-010",
        "title": "Cross-Surface Package Declaration Consistency",
        "legal_reference": "Rule 10 & General Statutory Principle",
        "applicable_categories": ["food", "cosmetics", "household", "textiles", "electronics", "imported", "general"],
        "severity": "CRITICAL",
        "version": "2011.1",
        "description": "No package shall carry conflicting or disparate declarations across different surfaces (e.g. Front net quantity vs Back net quantity, or multiple disparate MRP values) which may deceive or mislead the consumer.",
        "condition": {
            "check_consistency": True
        }
    }
]

STATUTORY_LEGAL_DISCLAIMER = (
    "STATUTORY LEGAL NOTICE: LabelGuard AI provides AI-assisted screening, vision extraction, "
    "and decision support in accordance with the Legal Metrology Act, 2009 and Legal Metrology "
    "(Packaged Commodities) Rules, 2011. Findings requiring enforcement action, compound notices, "
    "or seizure must be reviewed and confirmed by an authorized Legal Metrology Inspector or Officer."
)
