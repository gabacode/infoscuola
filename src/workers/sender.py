import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import markdown
from database import EmailLog


class Sender:
    def __init__(self):
        self.smtp_server = os.getenv("IMAP_SERVER")
        self.port = int(os.getenv("SMTP_PORT", 465))
        self.email_account = os.getenv("EMAIL_ACCOUNT")
        self.password = os.getenv("PASSWORD")
        self.recipients = os.getenv("RECIPIENTS").split(",")

    def connect_to_smtp(self):
        try:
            server = smtplib.SMTP_SSL(self.smtp_server, self.port)
            server.login(self.email_account, self.password)
            logging.info("Connected to SMTP server successfully.")
            return server
        except smtplib.SMTPException as e:
            logging.error(f"SMTP connection error: {e}")
            raise e

    @staticmethod
    def markdown_to_html(text):
        return markdown.markdown(text)

    def send_email(self, mail_id, to_address, subject, body):
        server = None
        try:
            server = self.connect_to_smtp()
            html_body = self.markdown_to_html(body)

            message = MIMEMultipart("alternative")
            message["From"] = self.email_account
            message["To"] = to_address
            message["Subject"] = subject

            message.attach(MIMEText(body, "plain"))
            message.attach(MIMEText(html_body, "html"))

            server.sendmail(self.email_account, to_address, message.as_string())
            logging.info(f"Email sent to {to_address}")
            return {"id": mail_id, "recipient": to_address, "success": True, "error": None}

        except Exception as e:
            logging.error(f"Error sending email: {e}")
            return {"id": mail_id, "recipient": to_address, "success": False, "error": str(e)}

        finally:
            if server:
                server.quit()

    @staticmethod
    def email_transformer(email: EmailLog) -> EmailLog:
        email.subject = f"Riassunto Circolare: {email.subject}"
        summarised_body = "\n".join([f"Allegato {i + 1}: {summary['text']}" for i, summary in enumerate(email.summary)])
        email.body = email.body + "\n\n" + summarised_body
        return email

    def send_emails(self, log: EmailLog) -> list[dict]:
        log = self.email_transformer(log)
        responses = []
        for recipient in self.recipients:
            response = self.send_email(log.id, recipient, log.subject, log.body)
            responses.append(response)
        return responses
