import email
import imaplib
import logging
import os
import re
import time
from email.header import decode_header

from database import DatabaseManager


class EmailMonitor:
    def __init__(self):
        self.imap_server = os.getenv("IMAP_SERVER")
        self.email_account = os.getenv("EMAIL_ACCOUNT")
        self.password = os.getenv("PASSWORD")
        self.mail = self.connect_to_imap()
        self.db_manager = DatabaseManager()

        os.makedirs("attachments", exist_ok=True)

    def connect_to_imap(self):
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, timeout=30)
            mail.login(self.email_account, self.password)
            mail.select("inbox")
            logging.info("Connected to IMAP server.")
            return mail
        except Exception as e:
            logging.error(f"Failed to connect to IMAP server: {e}")
            return None

    def reconnect_to_imap(self):
        logging.info("Attempting to reconnect to the IMAP server...")
        try:
            if self.mail:
                self.mail.logout()
        except Exception as e:
            logging.warning(f"Error during logout: {e}")
        self.mail = self.connect_to_imap()

    def fetch_email(self, email_id):
        res, msg_data = self.mail.fetch(email_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                return email.message_from_bytes(response_part[1])
        return None

    def check_for_new_emails(self):
        try:
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

        except imaplib.IMAP4.abort as e:
            logging.warning(f"IMAP connection aborted: {e}")
            self.reconnect_to_imap()
            return False
        except Exception as e:
            logging.error(f"Error while checking for new emails: {e}")
            return False

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
        attachments = []
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            filename = part.get_filename()
            if filename:
                safe_filename = self.save_attachment(part, filename)
                attachments.append({
                    "file": safe_filename,
                })
        return attachments

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
                try:
                    self.mail.noop()
                    if self.check_for_new_emails():
                        continue
                    logging.info(f"No new emails. Retrying in {wait} seconds.")
                    time.sleep(wait)
                except imaplib.IMAP4.abort:
                    logging.warning("IMAP server disconnected. Reconnecting...")
                    self.reconnect_to_imap()
                except Exception as e:
                    logging.error(f"Unexpected error: {e}")
                    time.sleep(wait)
        except KeyboardInterrupt:
            logging.info("Stopped email checker.")
        finally:
            self.mail.logout()
