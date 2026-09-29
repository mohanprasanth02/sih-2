"""
OIML R 76 Standards Configuration & Version Registry
Supports updating OIML recommendations or Indian Legal Metrology General Rules (Seventh Schedule)
without altering core test logic.
"""

from typing import Dict, Any, List


OIML_STANDARDS_REGISTRY: Dict[str, Dict[str, Any]] = {
    "OIML_R76_2006": {
        "standard_code": "OIML R 76-1:2006",
        "title": "Non-automatic weighing instruments - Part 1: Metrological and technical requirements - Tests",
        "year": 2006,
        "is_active": True,
        "description": "Standard international model approval specification for NAWIs.",
        "classes": {
            "Class I": {
                "designation": "Special Accuracy",
                "min_e_grams": 0.001,
                "n_min": 50000,
                "n_max": None,
                "mpe_steps": [
                    {"max_m_e": 50000, "mpe_initial_e": 0.5, "mpe_service_e": 1.0},
                    {"max_m_e": 200000, "mpe_initial_e": 1.0, "mpe_service_e": 2.0},
                    {"max_m_e": None, "mpe_initial_e": 1.5, "mpe_service_e": 3.0},
                ],
                "typical_instruments": ["Analytical microbalances", "Precious metal mass comparators"]
            },
            "Class II": {
                "designation": "High Accuracy",
                "min_e_grams": 0.001,
                "n_min": 100,
                "n_max": 100000,
                "mpe_steps": [
                    {"max_m_e": 5000, "mpe_initial_e": 0.5, "mpe_service_e": 1.0},
                    {"max_m_e": 20000, "mpe_initial_e": 1.0, "mpe_service_e": 2.0},
                    {"max_m_e": 100000, "mpe_initial_e": 1.5, "mpe_service_e": 3.0},
                ],
                "typical_instruments": ["Jewellery scales", "Laboratory precision balances", "Pharmaceutical scales"]
            },
            "Class III": {
                "designation": "Medium Accuracy",
                "min_e_grams": 0.1,
                "n_min": 100,
                "n_max": 10000,
                "mpe_steps": [
                    {"max_m_e": 500, "mpe_initial_e": 0.5, "mpe_service_e": 1.0},
                    {"max_m_e": 2000, "mpe_initial_e": 1.0, "mpe_service_e": 2.0},
                    {"max_m_e": 10000, "mpe_initial_e": 1.5, "mpe_service_e": 3.0},
                ],
                "typical_instruments": ["Commercial retail price-computing scales", "Platform scales", "Weighbridges", "Crane scales"]
            },
            "Class IIII": {
                "designation": "Ordinary Accuracy",
                "min_e_grams": 5.0,
                "n_min": 100,
                "n_max": 1000,
                "mpe_steps": [
                    {"max_m_e": 50, "mpe_initial_e": 0.5, "mpe_service_e": 1.0},
                    {"max_m_e": 200, "mpe_initial_e": 1.0, "mpe_service_e": 2.0},
                    {"max_m_e": 1000, "mpe_initial_e": 1.5, "mpe_service_e": 3.0},
                ],
                "typical_instruments": ["Coarse gravel/aggregate scales", "Freight loading indicators"]
            }
        },
        "prescribed_tests": [
            {
                "code": "A.4.4",
                "name": "Weighing Performance Test",
                "mandatory": True,
                "description": "Applies increasing and decreasing loads up to Max with at least 5 test points."
            },
            {
                "code": "A.4.10",
                "name": "Repeatability Test",
                "mandatory": True,
                "description": "Evaluates series of weighings at 0.5 Max and Max. Max difference <= |MPE|."
            },
            {
                "code": "A.4.7",
                "name": "Eccentricity / Off-Center Test",
                "mandatory": True,
                "description": "Applies test load (1/3 Max) at center and four corner quadrants."
            },
            {
                "code": "A.4.2",
                "name": "Zero-Setting and Zero-Tracking Test",
                "mandatory": True,
                "description": "Verifies residual zero error <= +/- 0.25 e."
            },
            {
                "code": "A.4.8",
                "name": "Discrimination Test",
                "mandatory": True,
                "description": "Evaluates response to additional 1.4 d load."
            },
            {
                "code": "A.5.3",
                "name": "Static Temperatures Test",
                "mandatory": True,
                "description": "Performance across temperature range (-10 deg C to +40 deg C)."
            },
            {
                "code": "A.5.4",
                "name": "Voltage Variation Test",
                "mandatory": True,
                "description": "Evaluates operation at nominal, +10% and -15% AC mains voltage."
            },
            {
                "code": "A.4.11",
                "name": "Creep Test",
                "mandatory": False,
                "description": "Measures indication drift at Max load over a 40-minute span."
            }
        ]
    }
}


def get_active_standard() -> Dict[str, Any]:
    """Retrieve the currently active OIML standard specification."""
    return OIML_STANDARDS_REGISTRY["OIML_R76_2006"]


def list_standards() -> List[Dict[str, Any]]:
    """List all registered standards with metadata."""
    return [
        {
            "id": k,
            "standard_code": v["standard_code"],
            "title": v["title"],
            "year": v["year"],
            "is_active": v["is_active"],
            "description": v["description"]
        }
        for k, v in OIML_STANDARDS_REGISTRY.items()
    ]
