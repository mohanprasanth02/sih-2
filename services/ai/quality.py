"""
LabelGuard AI - Computer Vision Image Quality Assessment
Calculates blur (Laplacian variance), illumination, contrast, and resolution.
Flags inadequate images with explicit guidance rather than failing silently.
"""
import os
import cv2
import numpy as np
from typing import Dict, Any
from services.ai.interfaces import QualityProvider

class OpenCVQualityProvider(QualityProvider):
    def __init__(self, blur_threshold: float = 65.0, min_brightness: float = 40.0, max_brightness: float = 230.0):
        self.blur_threshold = blur_threshold
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness

    def evaluate_quality(self, image_path: str) -> Dict[str, Any]:
        if not os.path.exists(image_path):
            return {
                "blur_score": 0.0,
                "brightness_score": 0.0,
                "contrast_score": 0.0,
                "quality_status": "INSUFFICIENT",
                "notes": f"Image file not found at {image_path}",
                "width": 0,
                "height": 0
            }

        img = cv2.imread(image_path)
        if img is None:
            return {
                "blur_score": 0.0,
                "brightness_score": 0.0,
                "contrast_score": 0.0,
                "quality_status": "INSUFFICIENT",
                "notes": "Could not decode image file format",
                "width": 0,
                "height": 0
            }

        height, width = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 1. Blur evaluation using Laplacian variance
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        blur_score = float(laplacian.var())

        # 2. Illumination / Brightness (Mean pixel intensity)
        brightness_score = float(np.mean(gray))

        # 3. Contrast (Standard deviation of pixel intensities)
        contrast_score = float(np.std(gray))

        # Quality decision logic
        notes = []
        status = "SUFFICIENT"

        if blur_score < self.blur_threshold:
            status = "INSUFFICIENT"
            notes.append(f"Image is significantly blurred (score {blur_score:.1f} < {self.blur_threshold}). Please hold camera steady and tap to focus.")
        elif blur_score < self.blur_threshold + 30.0:
            status = "WARNING"
            notes.append("Moderate blur detected. Text edges may have reduced recognition accuracy.")

        if brightness_score < self.min_brightness:
            status = "INSUFFICIENT"
            notes.append(f"Image is too dark (brightness {brightness_score:.1f}). Turn on device flashlight or move to better lit area.")
        elif brightness_score > self.max_brightness:
            status = "WARNING"
            notes.append(f"Overexposure or glare detected (brightness {brightness_score:.1f}). Avoid direct reflections on glossy packaging.")

        if contrast_score < 25.0:
            if status != "INSUFFICIENT":
                status = "WARNING"
            notes.append("Low contrast detected between text and background.")

        if width < 400 or height < 400:
            status = "INSUFFICIENT"
            notes.append(f"Resolution is too low ({width}x{height}px). Minimum recommended is 600x600px.")

        if not notes:
            notes.append("Image sharpness, illumination, and contrast are optimal for OCR verification.")

        return {
            "blur_score": round(blur_score, 2),
            "brightness_score": round(brightness_score, 2),
            "contrast_score": round(contrast_score, 2),
            "quality_status": status,
            "notes": " ".join(notes),
            "width": width,
            "height": height
        }
