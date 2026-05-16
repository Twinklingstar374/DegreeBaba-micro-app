import json
import logging
from typing import Dict, Any, List
from openai import OpenAI
from src.config.settings import settings
from src.utils.tracking import ExtractedField
from src.utils.strategies import ExtractionMethod

logger = logging.getLogger(__name__)

class SemanticMapper:
    """
    AI-assisted semantic mapping for ambiguous sections.
    Only used as a fallback when deterministic extraction is insufficient.
    """

    def __init__(self):
        api_key = settings.GEMINI_API_KEY or settings.OPENAI_API_KEY
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        ) if api_key else None

    def map_sections(self, unmapped_sections: Dict[str, str], target_fields: List[str]) -> Dict[str, ExtractedField]:
        """
        Takes unmapped HTML chunks and asks the AI to map them to specific ACF fields.
        """
        if not self.client:
            logger.warning("Gemini/OpenAI API key not found. Skipping AI semantic mapping.")
            # Return dummy mapping for testing without API key
            return {
                field: ExtractedField(
                    value="[AI Mapping Disabled - Mock Data]",
                    source_heading="Mock",
                    extraction_method=ExtractionMethod.AI_SEMANTIC_MAPPING.value,
                    confidence=0.5
                ) for field in target_fields
            }

        prompt = (
            f"You are a strict data extraction system. Map the following HTML content sections "
            f"to these specific fields: {', '.join(target_fields)}.\n"
            f"Respond with a valid JSON object where keys are the field names and values are the mapped HTML content.\n"
            f"If a field cannot be found, omit it.\n"
            f"Do not strip HTML tags.\n"
            f"You must output valid JSON only. Do not wrap in markdown tags like ```json\n\n"
            f"Sections: {json.dumps(unmapped_sections)}"
        )

        try:
            response = self.client.chat.completions.create(
                model="gemini-1.5-pro",
                messages=[{"role": "system", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result_json = json.loads(response.choices[0].message.content)
            
            mapped_fields = {}
            for key, value in result_json.items():
                if key in target_fields:
                    mapped_fields[key] = ExtractedField(
                        value=value,
                        source_heading="AI_Mapped",
                        extraction_method=ExtractionMethod.AI_SEMANTIC_MAPPING.value,
                        confidence=0.85 # AI is inherently less confident than regex
                    )
            return mapped_fields
            
        except Exception as e:
            logger.error(f"AI Mapping failed: {e}")
            return {}
