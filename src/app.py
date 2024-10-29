import logging
import threading

from dotenv import load_dotenv
from fastapi import FastAPI

from database import EmailLog
from monitor import EmailMonitor
from parser import Parser
from workers.operator import Operator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

load_dotenv()

app = FastAPI()

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
        return parser.process_email(log)
    except Exception as e:
        return {"error": str(e)}
