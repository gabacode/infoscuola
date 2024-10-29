import email
import imaplib
import logging
import os
import re
import threading
import time
from email.header import decode_header

from dotenv import load_dotenv
from fastapi import FastAPI

from database import DatabaseManager, EmailLog
from parser import Parser
from workers.operator import Operator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

load_dotenv()

app = FastAPI()


class EmailMonitor:
    def __init__(self):
        self.imap_server = os.getenv("IMAP_SERVER")
        self.email_account = os.getenv("EMAIL_ACCOUNT")
        self.password = os.getenv("PASSWORD")
        self.mail = self.connect_to_imap()
        self.db_manager = DatabaseManager()

        os.makedirs("attachments", exist_ok=True)

    def connect_to_imap(self):
        mail = imaplib.IMAP4_SSL(self.imap_server)
        mail.login(self.email_account, self.password)
        mail.select("inbox")
        return mail

    def fetch_email(self, email_id):
        res, msg_data = self.mail.fetch(email_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                return email.message_from_bytes(response_part[1])
        return None

    def check_for_new_emails(self):
        status, messages = self.mail.search(None, 'UNSEEN')
        if status != "OK":
            logging.error("Failed to search for new emails.")
            return False

        email_ids = messages[0].split()
        if not email_ids:
            return False

        for email_id in email_ids:
            msg = self.fetch_email(email_id)
            if msg:
                subject = self.get_email_subject(msg)
                logging.info(f"New email received: {subject}")
                body = self.get_email_body(msg).strip()
                sender = msg["From"]
                attachments = self.process_attachments(msg)
                self.db_manager.log_email(
                    subject=subject,
                    sender=sender,
                    body=body,
                    attachments=attachments
                )
        return True

    @staticmethod
    def get_email_body(msg):
        """Extracts and decodes the email body from the message object."""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    charset = part.get_content_charset()
                    body = part.get_payload(decode=True)
                    if charset:
                        body = body.decode(charset, errors='replace')
                    else:
                        body = body.decode(errors='replace')
                    return body
            return ""
        else:
            charset = msg.get_content_charset()
            body = msg.get_payload(decode=True)
            if charset:
                body = body.decode(charset, errors='replace')
            else:
                body = body.decode(errors='replace')
            return body

    @staticmethod
    def get_email_subject(msg):
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else "utf-8")
        return subject

    def process_attachments(self, msg):
        attachment_names = []
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            filename = part.get_filename()
            if filename:
                safe_filename = self.save_attachment(part, filename)
                attachment_names.append(safe_filename)
        return attachment_names

    @staticmethod
    def save_attachment(part, filename):
        safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
        filepath = os.path.join("attachments", safe_filename)
        with open(filepath, "wb") as file:
            file.write(part.get_payload(decode=True))
        logging.info(f"Attachment saved: {filepath}")
        return safe_filename

    def run(self):
        wait = 60
        try:
            while True:
                if self.check_for_new_emails():
                    continue
                logging.info(f"No new emails. Retrying in {wait} seconds.")
                time.sleep(wait)
        except KeyboardInterrupt:
            logging.info("Stopped email checker.")
        finally:
            self.mail.logout()


monitor = EmailMonitor()
parser = Parser()
operator = Operator()


@app.on_event("startup")
def startup_event():
    threading.Thread(target=monitor.run, daemon=True).start()
    threading.Thread(target=parser.start_periodic_check, args=(60,), daemon=True).start()

@app.get("/logs")
async def read_logs() -> list:
    logs = monitor.db_manager.read_all_email_logs()
    return [log.to_dict() for log in logs]

@app.post("/process/{email_id}")
async def process_email(email_id: int) -> dict:
    try:
        log: EmailLog = monitor.db_manager.read_email_log(email_id)
        if not log:
            return {"error": "Log not found."}
        body = log.body
        prompt = f"Riscrivi il seguente testo conservando solo i contenuti essenziali: {body}"
        rewritten_body = operator.ask(prompt)
        processed_attachments = parser.process_attachments(log.attachments)

        summaries = []
        for document in processed_attachments:
            if document["text"]:
                logging.info(f"Processing document: {document['file']}")
                prompt = f"Genera un riassunto in italiano del documento {document['file']}: {document['text']}"
                summary = operator.ask(prompt)
                summaries.append({
                    "file": document["file"],
                    "summary": summary
                })
        result = EmailLog(
            id=log.id,
            subject=log.subject,
            sender=log.sender,
            body=rewritten_body,
            attachments=processed_attachments,
            summary=summaries,
            processed=True,
            received_at=log.received_at
        )
        monitor.db_manager.update_email_log(result)
        return result.to_dict()
    except Exception as e:
        return {"error": str(e)}
