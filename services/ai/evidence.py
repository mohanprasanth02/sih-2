"""
LabelGuard AI - Visual Evidence Generator & Annotator
Draws high-contrast bounding boxes, label chips, and extracts evidence crops for human audit.
"""
import os
import cv2
import numpy as np
from typing import Dict, Any, List

class EvidenceGenerator:
    def __init__(self, output_dir: str = "uploads/evidence"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_annotated_image(
        self,
        image_path: str,
        fields: Dict[str, Dict[str, Any]],
        inspection_id: str,
        surface_type: str
    ) -> str:
        if not os.path.exists(image_path):
            return ""

        img = cv2.imread(image_path)
        if img is None:
            return ""

        annotated = img.copy()
        h, w = annotated.shape[:2]

        # Colors in BGR
        color_green = (46, 204, 113)  # PASS
        color_yellow = (241, 196, 15) # REVIEW
        color_red = (231, 76, 60)    # FAIL

        for field_name, info in fields.items():
            bbox = info.get("bbox")
            if not bbox or len(bbox) != 4:
                continue

            x1, y1, x2, y2 = [int(v) for v in bbox]
            # Clamp coordinates
            x1, y1 = max(0, min(w - 1, x1)), max(0, min(h - 1, y1))
            x2, y2 = max(0, min(w - 1, x2)), max(0, min(h - 1, y2))

            status = info.get("status", "DETECTED")
            conf = info.get("confidence", 0.0)

            if status == "LOW_CONFIDENCE" or conf < 0.70:
                color = color_yellow
            elif status == "NOT_DETECTED":
                color = color_red
            else:
                color = color_green

            # Draw rectangle
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 3)

            # Draw label banner
            label = f"{field_name.replace('_', ' ').title()} ({int(conf*100)}%)"
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
            cv2.rectangle(annotated, (x1, max(0, y1 - label_h - 10)), (x1 + label_w + 10, y1), color, -1)
            cv2.putText(
                annotated, label, (x1 + 5, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA
            )

        annotated_filename = f"{inspection_id}_{surface_type}_annotated.jpg"
        out_path = os.path.join(self.output_dir, annotated_filename)
        cv2.imwrite(out_path, annotated)
        return out_path

    def crop_field_evidence(
        self,
        image_path: str,
        bbox: List[int],
        field_name: str,
        inspection_id: str
    ) -> str:
        if not os.path.exists(image_path) or not bbox or len(bbox) != 4:
            return ""

        img = cv2.imread(image_path)
        if img is None:
            return ""

        h, w = img.shape[:2]
        x1, y1, x2, y2 = [int(v) for v in bbox]
        # Pad slightly
        pad = 12
        x1 = max(0, x1 - pad)
        y1 = max(0, y1 - pad)
        x2 = min(w, x2 + pad)
        y2 = min(h, y2 + pad)

        crop = img[y1:y2, x1:x2]
        if crop.size == 0:
            return ""

        crop_filename = f"{inspection_id}_{field_name}_crop.jpg"
        crop_path = os.path.join(self.output_dir, crop_filename)
        cv2.imwrite(crop_path, crop)
        return crop_path
