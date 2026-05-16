import io
import mammoth

class DocumentParser:
    """
    Parses DOCX files using Mammoth to preserve HTML structure (WYSIWYG requirements).
    """

    def __init__(self):
        # We can configure Mammoth style mappings if needed to preserve specific docx styles
        # e.g., mapping custom word styles to specific HTML elements
        self.style_map = (
            "p[style-name='Heading 1'] => h1:fresh\n"
            "p[style-name='Heading 2'] => h2:fresh\n"
            "p[style-name='Heading 3'] => h3:fresh\n"
        )

    def parse(self, docx_file) -> str:
        """
        Converts a DOCX file to an HTML string, preserving tables, formatting, and headings.
        :param docx_file: Path to a file or a file-like object
        :return: HTML string
        """
        if isinstance(docx_file, str):
            with open(docx_file, "rb") as docx_file_obj:
                return self._process_mammoth(docx_file_obj)
        else:
            return self._process_mammoth(docx_file)

    def _process_mammoth(self, docx_file_obj) -> str:
        result = mammoth.convert_to_html(docx_file_obj, style_map=self.style_map)
        html = result.value
        
        # We can log warnings if needed: result.messages
        # for message in result.messages:
        #     print(f"Mammoth Warning: {message}")
            
        return html
