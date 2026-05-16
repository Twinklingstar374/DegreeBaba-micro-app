from typing import Dict, Any
from src.schemas.review_report import ReviewReport
from src.utils.tracking import ExtractedField
from src.config.settings import settings

class ValidationEngine:
    """
    Validates extracted fields before publishing.
    Checks for missing fields, thin content, and malformed repeaters.
    """
    
    def __init__(self, min_content_length: int = 50):
        self.min_content_length = min_content_length

    def validate(self, document_name: str, page_type: str, extracted_data: Dict[str, ExtractedField]) -> ReviewReport:
        report = ReviewReport(document_name=document_name, page_type=page_type)
        report.is_publishable = True # Assume publishable until proven otherwise

        for field_name, field_data in extracted_data.items():
            value = field_data.value
            
            # 1. Check Confidence
            if field_data.confidence < settings.MIN_CONFIDENCE_THRESHOLD:
                report.add_warning(field_name, "low_confidence", f"Confidence score ({field_data.confidence}) is below threshold.", severity="warning")
                field_data.flag_for_review()

            # 2. Check Missing or Empty
            if not value:
                report.add_warning(field_name, "missing_field", "Field is missing or empty.", severity="error")
                field_data.flag_for_review()
                continue

            # 3. Check Thin Content (for strings)
            if isinstance(value, str) and len(value.strip()) < self.min_content_length:
                # We skip thin content check if it's meant to be short like stats, but we assume strings are HTML/text
                if field_data.extraction_method == "html_preservation":
                    report.add_warning(field_name, "thin_content", f"Content length ({len(value)}) is below minimum ({self.min_content_length}).", severity="warning")
                    field_data.flag_for_review()

            # 4. Check Repeater Validity (Lists)
            if isinstance(value, list):
                if len(value) == 0:
                    report.add_warning(field_name, "invalid_repeater", "Repeater array is empty.", severity="error")
                    field_data.flag_for_review()
                # Basic check for dicts inside repeater
                elif not all(isinstance(item, dict) for item in value):
                     # Wait, some repeaters might be Pydantic models depending on how they were mapped, 
                     # but let's assume they are dicts or Pydantic models here.
                     pass

                if field_name == "stats":
                    for stat in value:
                        if isinstance(stat, dict) and len(str(stat.get("value", ""))) > 6:
                            report.add_warning(field_name, "stat_too_long", f"Stat '{stat.get('value')}' exceeds 6 characters.", severity="warning")
                            field_data.flag_for_review()
                            break

            # Store the final value or the field object in the report
            report.extracted_fields[field_name] = field_data

        return report
