"""
LabelGuard AI - Cross-Image Package Consistency & Conflict Detection
Compares declarations extracted across multi-surface captures (Front vs Back vs Sides).
Flags discrepancies (e.g. Net Quantity or MRP mismatches) as potential deceptive packaging.
"""
import re
from typing import Dict, Any, List
from services.ai.interfaces import CrossImageProvider

class PackageConsistencyDetector(CrossImageProvider):
    def detect_conflicts(
        self,
        surface_fields: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        surface_fields format:
        {
            'front': { 'net_quantity': {'value': '500 g', ...}, 'mrp': ... },
            'back': { 'net_quantity': {'value': '450 g', ...}, 'mrp': ... }
        }
        """
        conflicts = []
        surfaces = list(surface_fields.keys())

        # Check all pairs of surfaces
        for i in range(len(surfaces)):
            for j in range(i + 1, len(surfaces)):
                s_a = surfaces[i]
                s_b = surfaces[j]
                fields_a = surface_fields[s_a]
                fields_b = surface_fields[s_b]

                # 1. Compare Net Quantity
                qty_a = fields_a.get("net_quantity", {}).get("value")
                qty_b = fields_b.get("net_quantity", {}).get("value")
                if qty_a and qty_b:
                    clean_a = re.sub(r"\s+", "", qty_a.lower())
                    clean_b = re.sub(r"\s+", "", qty_b.lower())
                    if clean_a != clean_b:
                        conflicts.append({
                            "field_name": "net_quantity",
                            "surface_a": s_a,
                            "value_a": qty_a,
                            "surface_b": s_b,
                            "value_b": qty_b,
                            "reason": f"Discrepant Net Quantity declarations: {s_a.title()} face declares '{qty_a}' while {s_b.title()} face declares '{qty_b}'."
                        })

                # 2. Compare MRP
                mrp_a = fields_a.get("mrp", {}).get("value")
                mrp_b = fields_b.get("mrp", {}).get("value")
                if mrp_a and mrp_b:
                    # Extract numeric amounts
                    num_a = re.search(r"\d+(?:\.\d+)?", mrp_a)
                    num_b = re.search(r"\d+(?:\.\d+)?", mrp_b)
                    if num_a and num_b:
                        val_a = float(num_a.group(0))
                        val_b = float(num_b.group(0))
                        if abs(val_a - val_b) > 0.01:
                            conflicts.append({
                                "field_name": "mrp",
                                "surface_a": s_a,
                                "value_a": mrp_a,
                                "surface_b": s_b,
                                "value_b": mrp_b,
                                "reason": f"Conflicting MRP values: {s_a.title()} face shows '₹{val_a}' but {s_b.title()} face shows '₹{val_b}'. Multiple MRP on same commodity is prohibited under Rule 18."
                            })

        return conflicts
