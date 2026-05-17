from typing import List, Dict, Any
from pydantic import BaseModel, Field

class ValidationWarning(BaseModel):
    field_name: str
    issue_type: str  # e.g., "missing_field", "thin_content", "low_confidence", "invalid_repeater"
    message: str
    severity: str = "warning"  # "warning", "error"

class ReviewReport(BaseModel):
    """
    Centralized module for validation warnings, missing fields,
    confidence scoring, manual review flags, and extraction traceability.
    """
    document_name: str
    page_type: str
    extracted_fields: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[ValidationWarning] = Field(default_factory=list)
    fields_needing_review: List[str] = Field(default_factory=list)
    unmapped_sections: List[str] = Field(default_factory=list)
    unmapped_section_content: Dict[str, str] = Field(default_factory=dict)
    quality_score: int = 0
    is_publishable: bool = False

    def add_warning(self, field_name: str, issue_type: str, message: str, severity: str = "warning"):
        self.warnings.append(ValidationWarning(
            field_name=field_name,
            issue_type=issue_type,
            message=message,
            severity=severity
        ))
        if severity == "error":
            self.is_publishable = False
        self.fields_needing_review.append(field_name)
