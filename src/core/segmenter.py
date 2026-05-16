from typing import Dict
from bs4 import BeautifulSoup

class DocumentSegmenter:
    """
    Splits an HTML document into logical sections based on headings.
    Builds a structured dictionary from heading-based chunks.
    """

    def segment(self, html_content: str) -> Dict[str, str]:
        """
        Parses HTML and groups content under the nearest preceding heading.
        :param html_content: Raw HTML string from Mammoth
        :return: Dictionary mapping heading text to its HTML content
        """
        soup = BeautifulSoup(html_content, "html.parser")
        sections = {}
        current_heading = "Document_Start"
        current_content = []

        for element in soup.children:
            if element.name in ['h1', 'h2', 'h3']:
                # Save previous section
                if current_content:
                    sections[current_heading] = "".join([str(tag) for tag in current_content]).strip()
                
                # Start new section
                current_heading = element.get_text(strip=True)
                current_content = []
            elif element.name is not None:
                # Add element to current section
                current_content.append(element)

        # Save the last section
        if current_content:
            sections[current_heading] = "".join([str(tag) for tag in current_content]).strip()

        # Filter out empty sections
        return {k: v for k, v in sections.items() if v}
