import time
from sqlalchemy import select
from database import DatabaseManager, EmailLog

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class Parser:
    def __init__(self):
        self.db_manager = DatabaseManager()
        logging.info("Parser initialized.")


    def process_unprocessed_emails(self):
        read_email_logs = self.db_manager.read_email_logs()
        logging.info(f"Read {len(read_email_logs)} email logs.")
        for email_log in read_email_logs:
            log = EmailLog(
                subject=email_log.subject,
                sender=email_log.sender,
                body=email_log.body,
                attachments=email_log.attachments
            )
            logging.info(f"Processing email log: {log.to_dict()}")

    def start_periodic_check(self, interval_seconds=10):
        """Run periodic check for unprocessed emails."""
        logging.info(f"Starting periodic check for unprocessed emails every {interval_seconds} seconds.")
        while True:
            self.process_unprocessed_emails()
            logging.info(f"Sleeping for {interval_seconds} seconds.")
            time.sleep(interval_seconds)
