import logging
import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class EmailLog(Base):
    __tablename__ = "email_log"

    id = Column(Integer, primary_key=True)
    subject = Column(String(255))
    sender = Column(String(255))
    body = Column(Text)
    attachments = Column(JSON)
    summary = Column(JSON, nullable=True)
    processed = Column(Boolean, default=False)
    received_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ZoneInfo('Europe/Rome'))
    )

    def to_dict(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "sender": self.sender,
            "body": self.body,
            # "attachments": self.attachments,
            "summary": self.summary,
            "processed": self.processed,
            "received_at": self.received_at
        }


class DatabaseManager:
    def __init__(self):
        db_user = os.getenv("DB_USER", "user")
        db_password = os.getenv("DB_PASSWORD", "password")
        db_host = os.getenv("DB_HOST", "postgres")
        db_name = os.getenv("DB_NAME", "email_db")

        self.engine = create_engine(
            f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}/{db_name}",
            echo=False,
            connect_args={'options': '-c timezone=Europe/Rome'}
        )
        self._connect_with_retries()

    def _connect_with_retries(self, retries=5, delay=5):
        for attempt in range(retries):
            try:
                Base.metadata.create_all(self.engine)
                self.Session = sessionmaker(bind=self.engine)
                print("Connected to the database.")
                return
            except Exception as e:
                print(f"Database connection failed (attempt {attempt + 1}/{retries}): {e}")
                time.sleep(delay)
        raise Exception("Failed to connect to the database after multiple attempts.")

    def read_email_logs(self):
        session = None
        try:
            session = self.Session()
            return session.query(EmailLog).where(EmailLog.processed == False).all()
        except Exception as e:
            print(f"Error reading email logs: {e}")
            logging.error(f"Error reading email logs: {e}")
            return []
        finally:
            session.close()

    def read_all_email_logs(self):
        session = None
        try:
            session = self.Session()
            return session.query(EmailLog).all()
        except Exception as e:
            print(f"Error reading email logs: {e}")
            logging.error(f"Error reading email logs: {e}")
            return []
        finally:
            session.close()

    def read_email_log(self, email_id):
        session = None
        try:
            session = self.Session()
            return session.query(EmailLog).get(email_id)
        except Exception as e:
            print(f"Error reading email log: {e}")
            logging.error(f"Error reading email log: {e}")
            return None
        finally:
            session.close()

    def log_email(self, subject, sender, body, attachments=None):
        if attachments is None:
            attachments = []
        session = None
        try:
            session = self.Session()
            email_entry = EmailLog(
                subject=subject,
                sender=sender,
                body=body,
                attachments=attachments,
                processed=False
            )
            session.add(email_entry)
            session.commit()
        except Exception as e:
            print(f"Error logging email: {e}")
            logging.error(f"Error logging email: {e}")
        finally:
            session.close()

    def update_email_log(self, email_log: EmailLog):
        session = None
        try:
            session = self.Session()
            session.merge(email_log)
            session.commit()
            print(f"EmailLog (ID: {email_log.id}) updated successfully.")
        except Exception as e:
            print(f"Error updating email log (ID: {email_log.id}): {e}")
            logging.error(f"Error updating email log (ID: {email_log.id}): {e}")
            session.rollback()
        finally:
            if session:
                session.close()
