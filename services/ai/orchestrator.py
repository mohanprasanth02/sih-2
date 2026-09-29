"""
LabelGuard AI - Main AI & Computer Vision Orchestration Service
Orchestrates Quality Check -> Text Region Detection -> OCR -> Field Extraction ->
Cross-Surface Conflict Detection -> Deterministic Compliance Rule Validation -> Evidence Generation.
Emits real-time progress events for WebSocket clients.
"""
import os
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable
from services.ai.quality import OpenCVQualityProvider
from services.ai.ocr_engine import ComputerVisionOCRProvider
from services.ai.field_extractor import RuleBasedFieldExtractor
from services.ai.cross_image import PackageConsistencyDetector
from services.ai.evidence import EvidenceGenerator
from rules.legal_metrology.engine import LegalMetrologyComplianceEngine

class AIOrchestrator:
    def __init__(
        self,
        quality_provider: Optional[OpenCVQualityProvider] = None,
        ocr_provider: Optional[ComputerVisionOCRProvider] = None,
        field_extractor: Optional[RuleBasedFieldExtractor] = None,
        cross_image_detector: Optional[PackageConsistencyDetector] = None,
        compliance_engine: Optional[LegalMetrologyComplianceEngine] = None,
        evidence_generator: Optional[EvidenceGenerator] = None
    ):
        self.quality_provider = quality_provider or OpenCVQualityProvider()
        self.ocr_provider = ocr_provider or ComputerVisionOCRProvider()
        self.field_extractor = field_extractor or RuleBasedFieldExtractor()
        self.cross_image_detector = cross_image_detector or PackageConsistencyDetector()
        self.compliance_engine = compliance_engine or LegalMetrologyComplianceEngine()
        self.evidence_generator = evidence_generator or EvidenceGenerator()

    async def run_pipeline(
        self,
        inspection_id: str,
        category_code: str,
        images_info: List[Dict[str, Any]], # [{'id': 'img-1', 'file_path': '...', 'surface_type': 'front'}]
        progress_callback: Optional[Callable[[str, str, Dict[str, Any]], Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes the complete multi-surface inspection pipeline.
        Emits progress at each statutory checkpoint.
        """
        async def notify(event: str, message: str, payload: Optional[Dict[str, Any]] = None):
            if progress_callback:
                if asyncio.iscoroutinefunction(progress_callback):
                    await progress_callback(event, message, payload or {})
                else:
                    progress_callback(event, message, payload or {})

        await notify("IMAGE_RECEIVED", f"Received {len(images_info)} package surface images for inspection {inspection_id}")

        # Step 1: Quality Check for each image
        quality_results = []
        overall_quality_sufficient = True

        for img in images_info:
            q = self.quality_provider.evaluate_quality(img["file_path"])
            quality_results.append({
                "image_id": img["id"],
                "surface_type": img["surface_type"],
                "quality": q
            })
            if q["quality_status"] == "INSUFFICIENT":
                overall_quality_sufficient = False

        await notify(
            "QUALITY_CHECKED",
            "Image sharpness, illumination, and resolution checked.",
            {"qualities": quality_results}
        )

        # Step 2: OCR Extraction
        await notify("OCR_STARTED", "Running computer vision text detection and optical character recognition...")
        surface_ocr_results = {}
        tokens_by_image = {}

        for img in images_info:
            ocr_res = self.ocr_provider.extract_text(img["file_path"])
            surface_ocr_results[img["surface_type"]] = ocr_res
            tokens_by_image[img["id"]] = ocr_res["tokens"]

        avg_conf = 0.0
        if surface_ocr_results:
            confs = [res["average_confidence"] for res in surface_ocr_results.values() if res["average_confidence"] > 0]
            avg_conf = round(sum(confs) / max(1, len(confs)), 2)

        await notify(
            "OCR_COMPLETED",
            f"OCR completed across all package surfaces. Average confidence: {int(avg_conf*100)}%.",
            {"average_confidence": avg_conf}
        )

        # Step 3: Structured Field Extraction
        await notify("EXTRACTION_STARTED", "Structuring OCR tokens into mandatory Legal Metrology declaration fields...")
        surface_fields = {}
        all_extracted_fields = {}

        for img in images_info:
            s_type = img["surface_type"]
            ocr_res = surface_ocr_results.get(s_type, {"raw_text": "", "tokens": []})
            fields = self.field_extractor.extract_fields(
                raw_text=ocr_res["raw_text"],
                tokens=ocr_res["tokens"],
                category_code=category_code,
                surface_type=s_type
            )
            surface_fields[s_type] = fields

            # Merge into unified inspection fields (preferring front for product name, highest confidence for others)
            for f_name, f_val in fields.items():
                if f_val.get("value") is not None:
                    existing = all_extracted_fields.get(f_name)
                    if not existing or (f_val.get("confidence", 0) > existing.get("confidence", 0)):
                        all_extracted_fields[f_name] = {
                            **f_val,
                            "image_id": img["id"],
                            "surface_type": s_type
                        }

        await notify(
            "EXTRACTION_COMPLETED",
            f"Extracted {len(all_extracted_fields)} declarations from package.",
            {"fields_count": len(all_extracted_fields)}
        )

        # Step 4: Cross-Image Conflict Detection
        conflicts = self.cross_image_detector.detect_conflicts(surface_fields)
        if conflicts:
            await notify(
                "RULE_VALIDATION_STARTED",
                f"Cross-surface analysis flagged {len(conflicts)} declaration discrepancies between package surfaces!",
                {"conflicts": conflicts}
            )
        else:
            await notify("RULE_VALIDATION_STARTED", "Evaluating declarations against Legal Metrology Rules 2011...")

        # Step 5: Deterministic Compliance Rule Validation
        eval_result = self.compliance_engine.evaluate(
            category_code=category_code,
            fields=all_extracted_fields,
            conflicts=conflicts,
            quality_status="SUFFICIENT" if overall_quality_sufficient else "INSUFFICIENT",
            surfaces_captured=len(images_info)
        )

        await notify(
            "RULE_VALIDATION_COMPLETED",
            f"Evaluation complete: {eval_result['summary']['pass']} Pass, {eval_result['summary']['fail']} Fail, {eval_result['summary']['review']} Needs Review.",
            {"summary": eval_result["summary"], "overall_status": eval_result["overall_status"]}
        )

        # Step 6: Evidence Generation & Highlighting
        annotated_images = []
        for img in images_info:
            s_type = img["surface_type"]
            fields = surface_fields.get(s_type, {})
            annotated_path = self.evidence_generator.generate_annotated_image(
                image_path=img["file_path"],
                fields=fields,
                inspection_id=inspection_id,
                surface_type=s_type
            )
            annotated_images.append({
                "image_id": img["id"],
                "surface_type": s_type,
                "annotated_path": annotated_path
            })

        await notify("EVIDENCE_GENERATED", "Visual evidence crops and bounding box overlays created.")

        final_payload = {
            "inspection_id": inspection_id,
            "overall_status": eval_result["overall_status"],
            "summary": eval_result["summary"],
            "rule_results": eval_result["rule_results"],
            "extracted_fields": all_extracted_fields,
            "conflicts": conflicts,
            "qualities": quality_results,
            "annotated_images": annotated_images,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        await notify("ANALYSIS_COMPLETED", f"Inspection analysis finalized with status: {eval_result['overall_status']}", final_payload)
        return final_payload
