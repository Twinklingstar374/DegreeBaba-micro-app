import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from src.utils.tracking import ExtractedField
from src.utils.strategies import ExtractionMethod

class DeterministicExtractor:
    """
    Handles regex-based extraction for stats and structured HTML extraction for tables and FAQs.
    """

    def __init__(self):
        # Prevent stat confusion by targeting specific prefixes/suffixes
        self.stat_patterns = {
            "students": re.compile(r'(\d+[kK\+]*)\s*(?:students|alumni)', re.IGNORECASE),
            "placement": re.compile(r'(\d+%)\s*(?:placement|hired)', re.IGNORECASE),
            "faculty": re.compile(r'(\d+[kK\+]*)\s*(?:faculty|professors|teachers)', re.IGNORECASE),
            "salary": re.compile(r'(\d+(?:\.\d+)?\s*[lL]akhs?|\d+(?:\.\d+)?\s*LPA)', re.IGNORECASE)
        }

    def extract_stats(self, html_content: str, heading: str) -> List[ExtractedField]:
        """
        Extracts structured stats using Regex to prevent stat confusion.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text(separator=" ")
        extracted_stats = []

        for stat_type, pattern in self.stat_patterns.items():
            matches = pattern.findall(text)
            for match in matches:
                field = ExtractedField(
                    value={"type": stat_type, "value": match},
                    source_heading=heading,
                    extraction_method=ExtractionMethod.REGEX.value,
                    confidence=0.95
                )
                extracted_stats.append(field)

        return extracted_stats

    def extract_table(self, html_content: str, heading: str) -> Optional[ExtractedField]:
        """
        Extracts HTML tables and preserves their structure for ACF repeaters.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find('table')
        
        if not table:
            return None

        # Basic table parsing to list of dicts (assuming first row is header)
        rows = table.find_all('tr')
        if len(rows) < 2:
            return None

        headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
        table_data = []

        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            row_data = {
                headers[i] if i < len(headers) else f"col_{i}": cell.get_text(strip=True)
                for i, cell in enumerate(cells)
            }
            if any(row_data.values()): # Only add non-empty rows
                table_data.append(row_data)

        if not table_data:
            return None

        return ExtractedField(
            value=table_data,
            source_heading=heading,
            extraction_method=ExtractionMethod.STRUCTURED_EXTRACTION.value,
            confidence=0.90
        )
