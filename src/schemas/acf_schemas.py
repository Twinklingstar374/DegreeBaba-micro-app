from typing import List, Dict, Optional
from pydantic import BaseModel, Field

# Base ACF Schemas

class FAQItem(BaseModel):
    question: str
    answer: str

class StatItem(BaseModel):
    label: str
    value: str

class UniversityPageSchema(BaseModel):
    """
    WordPress ACF compatible JSON payload schema for a University.
    """
    hero_description: Optional[str] = Field(None, description="HTML formatted hero section description")
    about_content: Optional[str] = Field(None, description="HTML formatted about university content")
    stats: List[StatItem] = Field(default_factory=list, description="Array of stats")
    fee_structure_table: List[Dict[str, str]] = Field(default_factory=list, description="JSON Array representing the fee structure table")
    faqs: List[FAQItem] = Field(default_factory=list, description="List of FAQs")
    accreditation_details: Optional[str] = Field(None, description="Accreditation information")
