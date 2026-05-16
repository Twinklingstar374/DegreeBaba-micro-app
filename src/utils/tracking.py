from typing import Optional, Any
from pydantic import BaseModel

class ExtractedField(BaseModel):
    """
    Deterministic traceability support.
    Every extracted field should ideally retain this structure.
    """
    value: Any
    source_heading: Optional[str] = None
    extraction_method: str
    confidence: float = 1.0  # 0.0 to 1.0
    needs_review: bool = False

    def flag_for_review(self):
        self.needs_review = True
