from typing import Dict, Optional

class PageTypeClassifier:
    """
    Detects the type of page from document structure, headings, and file names.
    based on document structure, headings, or keywords.
    """

    def __init__(self):
        self.university_keywords = ["university", "campus", "chancellor", "accreditation", "ranking", "about us"]
        self.course_keywords = ["course", "program", "online mba", "curriculum", "syllabus", "semester", "degree program", "fee"]
        self.specialization_keywords = ["specialization", "marketing", "finance", "analytics", "major", "concentration", "elective"]
        self.category_keywords = ["category", "universities", "courses", "colleges"]
        self.blog_keywords = ["blog", "article", "author", "published", "read time"]

    def classify(self, segmented_data: Dict[str, str], document_title: Optional[str] = None) -> str:
        """
        Determines page type based on heading names.
        :param segmented_data: Dict of headings to HTML content
        :param document_title: Optional top-level title (e.g. h1)
        :return: page type slug: university, course, specialization, category, blog, or unknown
        """
        all_text = " ".join(segmented_data.keys()).lower()
        if document_title:
            all_text += f" {document_title.lower()}"

        # Simple heuristic scoring based on heading keywords
        scores = {
            "university": sum(1 for kw in self.university_keywords if kw in all_text),
            "course": sum(1 for kw in self.course_keywords if kw in all_text),
            "specialization": sum(1 for kw in self.specialization_keywords if kw in all_text),
            "category": sum(1 for kw in self.category_keywords if kw in all_text),
            "blog": sum(1 for kw in self.blog_keywords if kw in all_text),
        }

        max_score = max(scores.values())
        if max_score == 0:
            return "unknown"
            
        # Return the key with the highest score
        return max(scores, key=scores.get)
