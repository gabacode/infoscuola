from io import BytesIO
import fitz
import PyPDF2
import pytesseract
from PIL import Image


class PDFReader:
    def __init__(self):
        self.file_path = None

    def set_file_path(self, file_path):
        self.file_path = file_path

    def extract_text(self):
        """Extracts text from the PDF file using PyPDF2."""
        text = ''
        with open(self.file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        return text

    def extract_images(self):
        """Extracts images from each page of the PDF using PyMuPDF."""
        images = []
        with fitz.open(self.file_path) as pdf_document:
            for page_number in range(pdf_document.page_count):
                page = pdf_document[page_number]
                image_list = page.get_images(full=True)

                for img in image_list:
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]

                    # Convert bytes to a PIL Image object
                    image = Image.open(BytesIO(image_bytes))
                    images.append(image)
        return images

    def ocr_images(self, language='eng'):
        """Extracts images and applies OCR to each image to retrieve text."""
        pages_text = []
        with fitz.open(self.file_path) as pdf_document:
            for page_number in range(pdf_document.page_count):
                page = pdf_document[page_number]
                image_list = page.get_images(full=True)

                for img in image_list:
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]

                    # Convert bytes to a PIL Image object
                    image = Image.open(BytesIO(image_bytes))

                    # Apply OCR to the image
                    text = pytesseract.image_to_string(image, lang=language)
                    pages_text.append(text)
        return pages_text
