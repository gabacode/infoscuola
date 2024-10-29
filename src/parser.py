import logging
import time

from database import DatabaseManager
from readers.pdf import PDFReader
from readers.docs import DocReader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


class Parser:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.pdf_reader = PDFReader()
        self.doc_reader = DocReader()
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
        if not attachments:
            logging.info("No attachments to process.")
            return []
        results = []
        for attachment in attachments:
            ext = attachment.split(".")[-1]
            if ext == "pdf":
                self.pdf_reader.set_file_path(f"attachments/{attachment}")
                text = self.pdf_reader.extract_text()
                if text:
                    results.append({
                        "file": attachment,
                        "text": text
                    })
                else:
                    ocr = self.pdf_reader.ocr_images()
                    results.append({
                        "file": attachment,
                        "text": ocr
                    })
            elif ext in ["doc", "docx"]:
                self.doc_reader.set_file_path(f"attachments/{attachment}")
                text = self.doc_reader.extract_text()
                results.append({
                    "file": attachment,
                    "text": text
                })
            elif ext in ["jpg", "jpeg", "png", "gif"]:
                # TODO: Pass the image to a model for seeing its contents.
                logging.info(f"Processing image attachment with extension: {ext}")
        return results
