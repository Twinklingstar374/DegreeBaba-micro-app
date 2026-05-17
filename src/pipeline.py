import logging
import re
from typing import Dict, Optional
from bs4 import BeautifulSoup
from src.core.parser import DocumentParser
from src.core.segmenter import DocumentSegmenter
from src.core.classifier import PageTypeClassifier
from src.core.deterministic import DeterministicExtractor
from src.mapping.semantic_mapper import SemanticMapper
from src.schemas.validation import ValidationEngine
from src.schemas.review_report import ReviewReport
from src.schemas.page_fields import get_fields
from src.utils.tracking import ExtractedField
from src.utils.strategies import ExtractionMethod

logger = logging.getLogger(__name__)

class ContentPipeline:
    """
    Orchestrates the conversion of DOCX files into validated ACF JSON payloads.
    """

    def __init__(self, ai_api_key: str = ""):
        self.parser = DocumentParser()
        self.segmenter = DocumentSegmenter()
        self.classifier = PageTypeClassifier()
        self.deterministic = DeterministicExtractor()
        self.ai_mapper = SemanticMapper(api_key_override=ai_api_key)
        self.validator = ValidationEngine()

        self.section_map = {
            "about": {
                "keywords": ["about", "overview", "introduction", "course details", "short description"],
                "content": "about_content",
                "heading": "about_heading",
            },
            "why_choose": {
                "keywords": ["why choose", "benefits", "highlights", "advantages", "course facts", "facts"],
                "content": "why_choose_content",
                "heading": "why_choose_heading",
                "course_content": "highlights",
                "course_heading": "highlights_heading",
            },
            "accreditations": {
                "keywords": ["accreditation", "approval", "recognition", "ugc", "naac"],
                "content": "accreditations",
                "heading": "accreditations_heading",
            },
            "programs": {
                "keywords": ["program", "course offered", "courses offered", "courses"],
                "content": "programs_table",
                "heading": "programs_heading",
            },
            "fee": {
                "keywords": ["fee", "fees", "emi", "payment", "specialization fee"],
                "content": "fee_plans",
                "heading": "fee_heading",
            },
            "eligibility": {
                "keywords": ["eligibility"],
                "content": "eligibility_content",
                "heading": "eligibility_heading",
            },
            "admission": {
                "keywords": ["admission", "apply", "enroll"],
                "content": "admission_steps",
                "heading": "admission_heading",
            },
            "syllabus": {
                "keywords": ["syllabus", "curriculum", "semester"],
                "content": "syllabus_content",
                "heading": "syllabus_heading",
            },
            "placement": {
                "keywords": ["placement", "career", "hiring", "job", "salary"],
                "content": "placement_content",
                "heading": "placement_heading",
            },
            "faculty": {
                "keywords": ["faculty", "professor", "teacher"],
                "content": "faculty_members",
                "heading": "faculty_heading",
            },
            "reviews": {
                "keywords": ["review", "testimonial"],
                "content": "reviews",
                "heading": "reviews_heading",
            },
            "faqs": {
                "keywords": ["faq", "frequently asked"],
                "content": "faqs",
                "heading": "faqs_heading",
            },
            "exam": {
                "keywords": ["exam", "assessment"],
                "content": "exam_content",
                "heading": "exam_heading",
            },
        }

    def process_file(self, file_path_or_obj, document_name: str, selected_page_type: Optional[str] = None) -> ReviewReport:
        logger.info(f"Processing document: {document_name}")

        # 1. Parse to HTML
        html_content = self.parser.parse(file_path_or_obj)
        
        # 2. Segment by headings
        segments = self.segmenter.segment(html_content)
        
        # 3. Classify Page Type
        page_type = selected_page_type or self.classifier.classify(segments, document_name)
        logger.info(f"Classified page as: {page_type}")

        extracted_data: Dict[str, ExtractedField] = {}
        unmapped_segments = {}

        # 4. Deterministic Extraction Layer
        self._extract_title_fields(document_name, page_type, segments, extracted_data)

        for heading, content in segments.items():
            mapped_deterministically = False
            section_result = self._map_known_section(page_type, heading, content)
            if section_result:
                for field_name, field in section_result.items():
                    if field_name not in extracted_data:
                        extracted_data[field_name] = field
                mapped_deterministically = True
            
            # Try extracting stats (Regex strategy)
            stats = self.deterministic.extract_stats(content, heading)
            if stats:
                self._assign_stats(page_type, stats, extracted_data)
                mapped_deterministically = True

            # Try extracting tables
            table = self.deterministic.extract_table(content, heading)
            if table:
                table_field = self._table_field_for_heading(page_type, heading)
                extracted_data[table_field] = table
                mapped_deterministically = True

            facts = self._extract_course_facts(page_type, content, heading)
            if facts:
                extracted_data.update({k: v for k, v in facts.items() if k not in extracted_data})
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
        target_fields = [
            field for field in get_fields(page_type)
            if field not in extracted_data and field in {"hero_description", "meta_description", "seo_title"}
        ]
        missing_targets = [f for f in target_fields if f not in extracted_data]
        
        if unmapped_segments and missing_targets:
            ai_results = self.ai_mapper.map_sections(unmapped_segments, missing_targets)
            extracted_data.update(ai_results)

        # 6. Validation Layer
        report = self.validator.validate(document_name, page_type, extracted_data)
        report.unmapped_sections = list(unmapped_segments.keys())
        report.unmapped_section_content = unmapped_segments
        
        return report

    def _extract_title_fields(self, document_name: str, page_type: str, segments: Dict[str, str], extracted_data: Dict[str, ExtractedField]) -> None:
        clean_name = re.sub(r"\.docx$", "", document_name, flags=re.IGNORECASE).replace("_", " ").strip()
        first_heading = next((heading for heading in segments if heading != "Document_Start"), clean_name)
        title = first_heading if first_heading else clean_name

        title_field = {
            "university": "university_name",
            "course": "program_name",
            "specialization": "spec_name",
            "category": "category_name",
            "blog": "post_title",
        }.get(page_type, "university_name")

        extracted_data[title_field] = ExtractedField(
            value=title,
            source_heading=first_heading,
            extraction_method=ExtractionMethod.REGEX.value,
            confidence=0.9,
        )
        if page_type in {"course", "specialization"} and "university_name" not in extracted_data:
            extracted_data["university_name"] = ExtractedField(
                value=self._infer_university_name(clean_name),
                source_heading=document_name,
                extraction_method=ExtractionMethod.REGEX.value,
                confidence=0.72,
            )
        if page_type in {"course", "specialization"}:
            extracted_data.setdefault(
                "mode",
                ExtractedField(
                    value="Online",
                    source_heading=document_name,
                    extraction_method=ExtractionMethod.REGEX.value,
                    confidence=0.82,
                ),
            )
        extracted_data["seo_title"] = ExtractedField(
            value=title,
            source_heading=first_heading,
            extraction_method=ExtractionMethod.REGEX.value,
            confidence=0.82,
        )
        first_content_heading, first_content = next(iter(segments.items()), (first_heading, ""))
        hero_text = self._excerpt(first_content, 220)
        if hero_text:
            extracted_data["hero_description"] = ExtractedField(
                value=hero_text,
                source_heading=first_content_heading,
                extraction_method=ExtractionMethod.HTML_PRESERVATION.value,
                confidence=0.78,
            )
            extracted_data["meta_description"] = ExtractedField(
                value=self._excerpt(first_content, 155),
                source_heading=first_content_heading,
                extraction_method=ExtractionMethod.REGEX.value,
                confidence=0.76,
            )

    def _map_known_section(self, page_type: str, heading: str, content: str) -> Optional[Dict[str, ExtractedField]]:
        normalized = heading.lower()
        for section in self.section_map.values():
            if not any(keyword in normalized for keyword in section["keywords"]):
                continue

            content_field = section.get("content")
            heading_field = section.get("heading")
            if page_type in {"course", "specialization"}:
                content_field = section.get("course_content", content_field)
                heading_field = section.get("course_heading", heading_field)

            if content_field not in get_fields(page_type):
                return None

            mapped = {
                content_field: ExtractedField(
                    value=self._normalise_repeater_content(content_field, content),
                    source_heading=heading,
                    extraction_method=ExtractionMethod.HTML_PRESERVATION.value,
                    confidence=0.93,
                )
            }
            if heading_field in get_fields(page_type):
                mapped[heading_field] = ExtractedField(
                    value=heading,
                    source_heading=heading,
                    extraction_method=ExtractionMethod.REGEX.value,
                    confidence=0.96,
                )
            return mapped
        return None

    def _normalise_repeater_content(self, field_name: str, content: str):
        repeater_fields = {
            "faqs", "reviews", "admission_steps", "facts", "accreditations",
            "highlights", "specializations", "job_profiles", "placement_partners",
            "faculty_members", "other_specs",
        }
        if field_name not in repeater_fields:
            return content

        soup = BeautifulSoup(content, "html.parser")
        items = [item.get_text(" ", strip=True) for item in soup.find_all("li")]
        if not items and field_name == "faqs":
            text = soup.get_text("\n", strip=True)
            parts = [part.strip() for part in re.split(r"\n+", text) if part.strip()]
            items = parts
        if not items:
            return content
        if field_name == "faqs":
            faqs = []
            for index in range(0, len(items), 2):
                question = items[index]
                answer = items[index + 1] if index + 1 < len(items) else ""
                faqs.append({"question": question, "answer": answer})
            return faqs
        return [{"item": item} for item in items]

    def _excerpt(self, html_content: str, limit: int) -> str:
        soup = BeautifulSoup(html_content, "html.parser")
        text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()
        if len(text) <= limit:
            return text
        return text[:limit].rsplit(" ", 1)[0].strip()

    def _infer_university_name(self, clean_name: str) -> str:
        known = ["NMIMS", "Amity", "Manipal", "Jain", "LPU", "Chandigarh", "Lovely Professional"]
        lowered = clean_name.lower()
        for name in known:
            if name.lower() in lowered:
                return name
        return clean_name

    def _extract_course_facts(self, page_type: str, html_content: str, heading: str) -> Dict[str, ExtractedField]:
        if page_type not in {"course", "specialization"}:
            return {}

        soup = BeautifulSoup(html_content, "html.parser")
        text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()
        results: Dict[str, ExtractedField] = {}

        duration_match = re.search(r"(\d{1,2})\s*(?:month|months)", text, re.IGNORECASE)
        if duration_match:
            months = int(duration_match.group(1))
            if months % 12 == 0:
                value = f"{months // 12} Years"
            else:
                value = f"{months} Months"
            results["duration"] = ExtractedField(
                value=value,
                source_heading=heading,
                extraction_method=ExtractionMethod.REGEX.value,
                confidence=0.88,
            )

        if re.search(r"\bonline\b|remote|virtual", text, re.IGNORECASE):
            results["mode"] = ExtractedField(
                value="Online",
                source_heading=heading,
                extraction_method=ExtractionMethod.REGEX.value,
                confidence=0.9,
            )

        placement_bits = re.findall(r"[^.]*\b(?:placement|job|hiring|employability|portal)\b[^.]*\.", text, re.IGNORECASE)
        for index, value in enumerate(placement_bits[:3], start=1):
            results[f"placement_stat_{index}"] = ExtractedField(
                value=value.strip(),
                source_heading=heading,
                extraction_method=ExtractionMethod.REGEX.value,
                confidence=0.74,
                needs_review=True,
            )

        return results

    def _table_field_for_heading(self, page_type: str, heading: str) -> str:
        normalized = heading.lower()
        if "fee" in normalized or "emi" in normalized:
            return "fee_plans" if page_type in {"course", "specialization"} else "programs_table"
        if "program" in normalized or "course" in normalized:
            return "programs_table"
        return "programs_table" if page_type == "university" else "fee_plans"

    def _assign_stats(self, page_type: str, stats, extracted_data: Dict[str, ExtractedField]) -> None:
        university_map = {
            "students": "stat_students",
            "alumni": "stat_alumni",
            "faculty": "stat_faculty",
            "placement": "stat_hiring_partners",
        }
        if page_type == "university":
            for stat in stats:
                stat_type = stat.value.get("type")
                field_name = university_map.get(stat_type, f"stat_{stat_type}")
                if field_name in get_fields(page_type):
                    extracted_data[field_name] = ExtractedField(
                        value=stat.value.get("value"),
                        source_heading=stat.source_heading,
                        extraction_method=stat.extraction_method,
                        confidence=stat.confidence,
                    )
            return

        slot = 1
        for stat in stats:
            while f"hero_stat_{slot}_value" in extracted_data and slot <= 4:
                slot += 1
            if slot > 4:
                break
            extracted_data[f"hero_stat_{slot}_value"] = ExtractedField(
                value=stat.value.get("value"),
                source_heading=stat.source_heading,
                extraction_method=stat.extraction_method,
                confidence=stat.confidence,
            )
            extracted_data[f"hero_stat_{slot}_label"] = ExtractedField(
                value=stat.value.get("type", "stat").replace("_", " ").title(),
                source_heading=stat.source_heading,
                extraction_method=ExtractionMethod.REGEX.value,
                confidence=0.9,
            )
            slot += 1
