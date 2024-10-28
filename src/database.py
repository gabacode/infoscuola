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
    processed = Column(Boolean, default=False)
    received_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ZoneInfo('Europe/Rome'))
    )


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
                attachments=attachments
            )
            session.add(email_entry)
            session.commit()
        except Exception as e:
            print(f"Error logging email: {e}")
            logging.error(f"Error logging email: {e}")
        finally:
            session.close()
