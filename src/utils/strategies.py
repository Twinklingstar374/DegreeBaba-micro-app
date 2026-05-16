from enum import Enum
from typing import Dict

class ExtractionMethod(str, Enum):
    REGEX = "regex"
    HTML_PRESERVATION = "html_preservation"
    STRUCTURED_EXTRACTION = "structured_extraction"
    AI_SEMANTIC_MAPPING = "ai_semantic_mapping"

# Configurable extraction strategy mapping
FIELD_STRATEGIES: Dict[str, str] = {
    "stats": ExtractionMethod.REGEX.value,
    "body_content": ExtractionMethod.HTML_PRESERVATION.value,
    "faq_repeaters": ExtractionMethod.STRUCTURED_EXTRACTION.value,
    "tables": ExtractionMethod.STRUCTURED_EXTRACTION.value,
    "ambiguous_sections": ExtractionMethod.AI_SEMANTIC_MAPPING.value,
}
