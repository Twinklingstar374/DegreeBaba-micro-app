import logging
from typing import Dict, Any
from src.core.parser import DocumentParser
from src.core.segmenter import DocumentSegmenter
from src.core.classifier import PageTypeClassifier
from src.core.deterministic import DeterministicExtractor
from src.mapping.semantic_mapper import SemanticMapper
from src.schemas.validation import ValidationEngine
from src.schemas.review_report import ReviewReport
from src.utils.tracking import ExtractedField
from src.utils.strategies import ExtractionMethod

logger = logging.getLogger(__name__)

class ContentPipeline:
    """
    Orchestrates the conversion of DOCX files into validated ACF JSON payloads.
    """

    def __init__(self):
        self.parser = DocumentParser()
        self.segmenter = DocumentSegmenter()
        self.classifier = PageTypeClassifier()
        self.deterministic = DeterministicExtractor()
        self.ai_mapper = SemanticMapper()
        self.validator = ValidationEngine()

    def process_file(self, file_path_or_obj, document_name: str) -> ReviewReport:
        logger.info(f"Processing document: {document_name}")

        # 1. Parse to HTML
        html_content = self.parser.parse(file_path_or_obj)
        
        # 2. Segment by headings
        segments = self.segmenter.segment(html_content)
        
        # 3. Classify Page Type
        page_type = self.classifier.classify(segments)
        logger.info(f"Classified page as: {page_type}")

        extracted_data: Dict[str, ExtractedField] = {}
        unmapped_segments = {}

        # 4. Deterministic Extraction Layer
        for heading, content in segments.items():
            mapped_deterministically = False
            
            # Try extracting stats (Regex strategy)
            stats = self.deterministic.extract_stats(content, heading)
            if stats:
                if "stats" not in extracted_data:
                    extracted_data["stats"] = ExtractedField(
                        value=[],
                        source_heading="Multiple",
                        extraction_method=ExtractionMethod.REGEX.value,
                        confidence=0.95
                    )
                extracted_data["stats"].value.extend([s.value for s in stats])
                mapped_deterministically = True

            # Try extracting tables
            table = self.deterministic.extract_table(content, heading)
            if table:
                extracted_data["fee_structure_table"] = table # simplified assignment
                mapped_deterministically = True

            # If it's the first heading and looks like an overview, map it directly
            if "overview" in heading.lower() or "about" in heading.lower():
                extracted_data["about_content"] = ExtractedField(
                    value=content,
                    source_heading=heading,
                    extraction_method=ExtractionMethod.HTML_PRESERVATION.value,
                    confidence=1.0
                )
                mapped_deterministically = True

            if not mapped_deterministically:
                unmapped_segments[heading] = content

        # 5. AI Semantic Mapping (Fallback)
        # Determine remaining fields needed based on ACF schema (Simplified)
        target_fields = ["hero_description", "accreditation_details", "faqs"]
        missing_targets = [f for f in target_fields if f not in extracted_data]
        
        if unmapped_segments and missing_targets:
            ai_results = self.ai_mapper.map_sections(unmapped_segments, missing_targets)
            extracted_data.update(ai_results)

        # 6. Validation Layer
        report = self.validator.validate(document_name, page_type, extracted_data)
        
        return report
