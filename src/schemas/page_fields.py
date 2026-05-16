from typing import Dict, List


PAGE_FIELDS: Dict[str, List[str]] = {
    "university": [
        "university_name", "university_full_name", "hero_description", "established_year",
        "naac_grade", "ugc_approved", "mode_of_learning", "stat_students", "stat_alumni",
        "stat_hiring_partners", "stat_faculty", "about_heading", "about_content",
        "why_choose_heading", "why_choose_content", "facts_heading", "facts",
        "accreditations_heading", "accreditations", "programs_heading", "programs_table",
        "admission_heading", "admission_steps", "emi_heading", "emi_content",
        "exam_heading", "exam_content", "faculty_heading", "faculty_members",
        "placement_heading", "placement_content", "placement_partners",
        "reviews_heading", "reviews", "faqs_heading", "faqs", "seo_title", "meta_description",
    ],
    "course": [
        "program_name", "university_name", "hero_description", "duration", "mode",
        "naac_grade", "ugc_status", "hero_stat_1_value", "hero_stat_1_label",
        "hero_stat_2_value", "hero_stat_2_label", "hero_stat_3_value", "hero_stat_3_label",
        "hero_stat_4_value", "hero_stat_4_label", "about_heading", "about_content",
        "highlights_heading", "highlights", "accreditations_heading", "accreditations",
        "specializations_heading", "specializations_intro", "specializations",
        "fee_heading", "fee_plans", "emi_content", "eligibility_heading", "eligibility_content",
        "admission_heading", "admission_steps", "syllabus_heading", "syllabus_content",
        "placement_heading", "placement_stat_1", "placement_stat_2", "placement_stat_3",
        "placement_content", "placement_partners", "jobs_heading", "job_profiles",
        "certificate_description", "reviews_heading", "reviews", "faqs_heading", "faqs",
        "seo_title", "meta_description",
    ],
    "specialization": [
        "spec_name", "university_name", "hero_description", "duration", "mode",
        "naac_grade", "ugc_status", "hero_stat_1_value", "hero_stat_1_label",
        "hero_stat_2_value", "hero_stat_2_label", "hero_stat_3_value", "hero_stat_3_label",
        "about_heading", "about_content", "highlights_heading", "highlights",
        "eligibility_heading", "eligibility_content", "fee_heading", "fee_plans", "emi_content",
        "other_specs_heading", "other_specs", "syllabus_heading", "syllabus_content",
        "exam_heading", "exam_content", "admission_heading", "admission_steps",
        "placement_heading", "placement_stat_1", "placement_stat_2", "placement_stat_3",
        "placement_content", "placement_partners", "jobs_heading", "job_profiles",
        "certificate_description", "reviews_heading", "reviews", "faqs_heading", "faqs",
        "seo_title", "meta_description",
    ],
    "category": [
        "category_name", "hero_description", "category_intro", "related_pages",
        "faqs_heading", "faqs", "seo_title", "meta_description",
    ],
    "blog": [
        "post_title", "hero_description", "author_name", "publish_date", "content_body",
        "content_1_image", "content_2_image", "og_image", "thumbnail_image",
        "faqs_heading", "faqs", "seo_title", "meta_description",
    ],
}


REQUIRED_FIELDS: Dict[str, List[str]] = {
    "university": [
        "university_name", "hero_description", "about_content", "accreditations",
        "programs_table", "admission_steps", "faqs", "seo_title", "meta_description",
    ],
    "course": [
        "program_name", "university_name", "hero_description", "duration", "mode",
        "about_content", "fee_plans", "eligibility_content", "admission_steps",
        "syllabus_content", "faqs", "seo_title", "meta_description",
    ],
    "specialization": [
        "spec_name", "university_name", "hero_description", "duration", "mode",
        "about_content", "eligibility_content", "fee_plans", "syllabus_content",
        "faqs", "seo_title", "meta_description",
    ],
    "category": ["category_name", "hero_description", "category_intro", "seo_title", "meta_description"],
    "blog": ["post_title", "hero_description", "content_body", "seo_title", "meta_description"],
}


IMAGE_SLOTS: Dict[str, List[dict]] = {
    "university": [
        {"name": "hero", "required": True},
        {"name": "logo", "required": True},
        {"name": "campus", "required": False},
    ],
    "course": [
        {"name": "hero", "required": True},
        {"name": "logo", "required": True},
        {"name": "certificate", "required": False},
    ],
    "specialization": [
        {"name": "hero", "required": True},
        {"name": "logo", "required": True},
        {"name": "certificate", "required": False},
    ],
    "category": [{"name": "hero", "required": True}],
    "blog": [
        {"name": "hero", "required": True},
        {"name": "content-1", "required": False},
        {"name": "content-2", "required": False},
        {"name": "og", "required": False},
        {"name": "thumbnail", "required": False},
    ],
}


def get_fields(page_type: str) -> List[str]:
    return PAGE_FIELDS.get(page_type, PAGE_FIELDS["university"])


def get_required_fields(page_type: str) -> List[str]:
    return REQUIRED_FIELDS.get(page_type, REQUIRED_FIELDS["university"])


def get_image_slots(page_type: str) -> List[dict]:
    return IMAGE_SLOTS.get(page_type, IMAGE_SLOTS["university"])
