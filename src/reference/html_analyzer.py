from pathlib import Path
from typing import Dict, List

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[2]


REFERENCE_FILES = {
    "university": ROOT / "references" / "html" / "nmims-university-page.html",
    "course": ROOT / "references" / "html" / "nmims-online-mba.html",
    "specialization": ROOT / "references" / "html" / "nmims-mba-marketing.html",
}


SECTION_FIELD_MAP = {
    "university": {
        "About NMIMS Online": ["about_heading", "about_content"],
        "Why Choose NMIMS Online?": ["why_choose_heading", "why_choose_content"],
        "NMIMS Online Facts": ["facts_heading", "facts", "stat_students", "stat_alumni", "stat_hiring_partners", "stat_faculty"],
        "Accreditations & Rankings": ["accreditations_heading", "accreditations", "naac_grade", "ugc_approved"],
        "Programs & Fee Structure": ["programs_heading", "programs_table"],
        "Admission Process": ["admission_heading", "admission_steps"],
        "EMI & Financial Assistance": ["emi_heading", "emi_content"],
        "Examination Process": ["exam_heading", "exam_content"],
        "Faculty Members": ["faculty_heading", "faculty_members"],
        "Placement & Career Services": ["placement_heading", "placement_content", "placement_partners"],
        "Student Reviews": ["reviews_heading", "reviews"],
        "Frequently Asked Questions": ["faqs_heading", "faqs"],
    },
    "course": {
        "About the Program": ["about_heading", "about_content"],
        "NMIMS Online MBA — Program Highlights": ["highlights_heading", "highlights"],
        "Accreditations & Rankings": ["accreditations_heading", "accreditations", "naac_grade", "ugc_status"],
        "Specializations": ["specializations_heading", "specializations_intro", "specializations"],
        "Fee Structure & EMI": ["fee_heading", "fee_plans", "emi_content"],
        "Eligibility Criteria": ["eligibility_heading", "eligibility_content"],
        "Admission Process": ["admission_heading", "admission_steps"],
        "Syllabus & Curriculum": ["syllabus_heading", "syllabus_content"],
        "Placement & Career Services": ["placement_heading", "placement_content", "placement_partners", "placement_stat_1", "placement_stat_2", "placement_stat_3"],
        "Job Profiles & Average Salary": ["jobs_heading", "job_profiles"],
        "Sample Certificate": ["certificate_description"],
        "Student Reviews": ["reviews_heading", "reviews"],
        "Frequently Asked Questions": ["faqs_heading", "faqs"],
    },
    "specialization": {
        "About the Specialization": ["about_heading", "about_content"],
        "MBA in Marketing — Program Highlights": ["highlights_heading", "highlights"],
        "Eligibility Criteria": ["eligibility_heading", "eligibility_content"],
        "Fee Structure & EMI": ["fee_heading", "fee_plans", "emi_content"],
        "Other MBA Specializations": ["other_specs_heading", "other_specs"],
        "Syllabus & Curriculum": ["syllabus_heading", "syllabus_content"],
        "Examination Process": ["exam_heading", "exam_content"],
        "Admission Process": ["admission_heading", "admission_steps"],
        "Placement & Career Services": ["placement_heading", "placement_content", "placement_partners", "placement_stat_1", "placement_stat_2", "placement_stat_3"],
        "Job Opportunities & Salary": ["jobs_heading", "job_profiles"],
        "Sample Certificate": ["certificate_description"],
        "Student Reviews": ["reviews_heading", "reviews"],
        "Frequently Asked Questions": ["faqs_heading", "faqs"],
    },
}


def extract_reference_sections(page_type: str) -> Dict:
    path = REFERENCE_FILES.get(page_type)
    if not path or not path.exists():
        return {
            "page_type": page_type,
            "exists": False,
            "path": str(path) if path else "",
            "title": "",
            "sections": [],
        }

    soup = BeautifulSoup(path.read_text(errors="ignore"), "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    headings = []
    seen = set()
    for heading in soup.find_all(["h1", "h2", "h3"]):
        text = heading.get_text(" ", strip=True)
        if not text or text in seen:
            continue
        seen.add(text)
        headings.append({"level": heading.name, "heading": text, "acf_fields": SECTION_FIELD_MAP.get(page_type, {}).get(text, [])})

    return {
        "page_type": page_type,
        "exists": True,
        "path": str(path),
        "title": title,
        "sections": headings,
    }


def get_all_reference_alignments() -> List[Dict]:
    return [extract_reference_sections(page_type) for page_type in ["university", "course", "specialization"]]
