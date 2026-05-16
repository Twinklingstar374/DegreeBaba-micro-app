from typing import Dict, Optional

class PageTypeClassifier:
    """
    Detects the type of page (University, Course, Specialization)
    based on document structure, headings, or keywords.
    """

    def __init__(self):
        self.university_keywords = ["university", "campus", "chancellor", "accreditation", "ranking"]
        self.course_keywords = ["course", "curriculum", "syllabus", "semester", "degree program"]
        self.specialization_keywords = ["specialization", "major", "concentration", "elective"]

    def classify(self, segmented_data: Dict[str, str], document_title: Optional[str] = None) -> str:
        """
        Determines page type based on heading names.
        :param segmented_data: Dict of headings to HTML content
        :param document_title: Optional top-level title (e.g. h1)
        :return: String representing page type ('university', 'course', 'specialization', 'unknown')
        """
        all_text = " ".join(segmented_data.keys()).lower()
        if document_title:
            all_text += f" {document_title.lower()}"

        # Simple heuristic scoring based on heading keywords
        scores = {
            "university": sum(1 for kw in self.university_keywords if kw in all_text),
            "course": sum(1 for kw in self.course_keywords if kw in all_text),
            "specialization": sum(1 for kw in self.specialization_keywords if kw in all_text),
        }

        max_score = max(scores.values())
        if max_score == 0:
            return "unknown"
            
        # Return the key with the highest score
        return max(scores, key=scores.get)
