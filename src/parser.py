import logging
import time

from database import DatabaseManager
from readers.pdf import PDFReader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


class Parser:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.pdf_reader = PDFReader()
        logging.info("Parser initialized.")

    def process_unprocessed_emails(self):
        mails = self.db_manager.read_email_logs()
        logging.info(f"Read {len(mails)} emails.")
        for mail in mails:
            self.process_attachments(mail.attachments)

    def start_periodic_check(self, interval_seconds=10):
        """Run periodic check for unprocessed emails."""
        logging.info(f"Starting periodic check for unprocessed emails every {interval_seconds} seconds.")
        while True:
            self.process_unprocessed_emails()
            logging.info(f"Sleeping for {interval_seconds} seconds.")
            time.sleep(interval_seconds)

    def process_attachments(self, attachments: list):
        results = []
        for attachment in attachments:
            ext = attachment.split(".")[-1]
            if ext == "pdf":
                self.pdf_reader.set_file_path(f"attachments/{attachment}")
                text = self.pdf_reader.extract_text()
                if text:
                    results.append(text)
                else:
                    ocr = self.pdf_reader.ocr_images()
                    results.extend(ocr)
            elif ext in ["doc", "docx"]:
                # TODO: Extract text from the document.
                logging.info(f"Processing doc/docx ({ext})")
            elif ext in ["jpg", "jpeg", "png", "gif"]:
                # TODO: Pass the image to a model for seeing its contents.
                logging.info(f"Processing image attachment with extension: {ext}")
        return results
