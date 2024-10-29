import logging
import time

from database import DatabaseManager, EmailLog
from readers.pdf import PDFReader
from readers.docs import DocReader
from workers.operator import Operator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


class Parser:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.pdf_reader = PDFReader()
        self.doc_reader = DocReader()
        self.operator = Operator()
        logging.info("Parser initialized.")

    def process_email(self, log: EmailLog):
        body = self.operator.ask(f"Riscrivi il seguente testo conservando solo i contenuti essenziali: {log.body}")
        attachments = self.process_attachments(log.attachments)
        summaries = self.operator.summarise_documents(attachments)
        result = EmailLog(
            id=log.id,
            subject=log.subject,
            sender=log.sender,
            body=body,
            attachments=attachments,
            summary=summaries,
            processed=True,
            received_at=log.received_at
        )
        self.db_manager.update_email_log(result)
        logging.info(f"Processed email: {log.id}")
        return result.to_dict()

    def process_unprocessed_emails(self):
        logs = self.db_manager.read_email_logs()
        logging.info(f"Read {len(logs)} emails.")
        for log in logs:
           self.process_email(log)

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
            logging.info(f"Processing attachment: {attachment['file']}")
            attachment_file = attachment["file"]
            ext = attachment_file.split(".")[-1]
            if ext == "pdf":
                self.pdf_reader.set_file_path(f"attachments/{attachment_file}")
                text = self.pdf_reader.extract_text()
                if text:
                    results.append({
                        "file": attachment_file,
                        "text": text
                    })
                else:
                    ocr = self.pdf_reader.ocr_images()
                    results.append({
                        "file": attachment_file,
                        "text": ocr
                    })
            elif ext in ["doc", "docx"]:
                self.doc_reader.set_file_path(f"attachments/{attachment_file}")
                text = self.doc_reader.extract_text()
                results.append({
                    "file": attachment_file,
                    "text": text
                })
            elif ext in ["jpg", "jpeg", "png", "gif"]:
                # TODO: Pass the image to a model for seeing its contents.
                logging.info(f"Processing image attachment with extension: {ext}")
        return results
