import textract
from docx import Document

class DocReader:
    def __init__(self):
        self.file_path = None

    def set_file_path(self, file_path):
        self.file_path = file_path

    def extract_text(self):
        if self.file_path.endswith('.docx'):
            return self._extract_text_docx()
        elif self.file_path.endswith('.doc'):
            return self._extract_text_doc()
        else:
            raise ValueError("Unsupported file format. Only .doc and .docx files are supported.")

    def _extract_text_docx(self):
        """Extracts text from a .docx file using python-docx."""
        text = []
        document = Document(self.file_path)
        for paragraph in document.paragraphs:
            text.append(paragraph.text)
        return '\n'.join(text)

    def _extract_text_doc(self):
        """Extracts text from a .doc file using textract."""
        try:
            text = textract.process(self.file_path).decode('utf-8')
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from .doc file: {e}")
        return text
