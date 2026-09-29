"""
LabelGuard AI - Pluggable AI and Computer Vision Provider Interfaces
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple

class QualityProvider(ABC):
    @abstractmethod
    def evaluate_quality(self, image_path: str) -> Dict[str, Any]:
        """
        Evaluates blur, brightness, contrast, and resolution.
        Returns: {
            'blur_score': float,
            'brightness_score': float,
            'contrast_score': float,
            'quality_status': 'SUFFICIENT' | 'INSUFFICIENT' | 'WARNING',
            'notes': str,
            'width': int,
            'height': int
        }
        """
        pass

class OCRToken:
    def __init__(self, text: str, confidence: float, bbox: List[int]):
        self.text = text
        self.confidence = confidence
        self.bbox = bbox # [x1, y1, x2, y2]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "confidence": self.confidence,
            "bbox": self.bbox
        }

class OCRProvider(ABC):
    @abstractmethod
    def extract_text(self, image_path: str) -> Dict[str, Any]:
        """
        Performs text detection and OCR recognition.
        Returns: {
            'raw_text': str,
            'tokens': List[OCRToken],
            'average_confidence': float,
            'model_name': str,
            'latency_ms': float
        }
        """
        pass

class FieldExtractionProvider(ABC):
    @abstractmethod
    def extract_fields(
        self,
        raw_text: str,
        tokens: List[OCRToken],
        category_code: str,
        surface_type: str
    ) -> Dict[str, Any]:
        """
        Transforms raw text and OCR tokens into structured Legal Metrology fields.
        Returns dict of field_name -> {
            'value': str | None,
            'confidence': float,
            'bbox': List[int] | None,
            'status': 'DETECTED' | 'NOT_DETECTED' | 'LOW_CONFIDENCE'
        }
        """
        pass

class CrossImageProvider(ABC):
    @abstractmethod
    def detect_conflicts(
        self,
        surface_fields: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Cross-checks declarations across multiple surfaces (Front, Back, Sides).
        Returns list of conflict items: [{
            'field_name': str,
            'surface_a': str,
            'value_a': str,
            'surface_b': str,
            'value_b': str,
            'reason': str
        }]
        """
        pass
