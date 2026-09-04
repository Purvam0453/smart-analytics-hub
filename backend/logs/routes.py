from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import csv
import os
from datetime import datetime

from database import get_db, BASE_DIR
from models.user import AuditLog

router = APIRouter(
    prefix="/logs",
    tags=["Logs"]
)

# Unified log file path
LOG_FILE = os.path.join(BASE_DIR, "logs.csv")


def save_log(username: str, action: str, details: str):
    """Save event entry to the unified logs file."""
    try:
        file_exists = os.path.exists(LOG_FILE)
        with open(LOG_FILE, "a", newline="", encoding="utf-8") as log_file:
            writer = csv.writer(log_file)
            if not file_exists:
                writer.writerow(["username", "action", "details", "date_time"])
            writer.writerow([
                username or "Guest",
                action,
                details,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
    except Exception as e:
        print(f"File log error: {e}")


@router.get("/all")
def get_all_logs(db: Session = Depends(get_db)):
    """
    Get all system audit logs. Queries database AuditLog table first,
    falling back to CSV log file if database has no records.
    """
    db_logs = db.query(AuditLog).order_by(AuditLog.id.desc()).all()

    if db_logs:
        logs_data = [
            {
                "username": l.username or "Guest",
                "action": l.action,
                "details": l.details or "-",
                "date_time": l.created_at.strftime("%Y-%m-%d %H:%M:%S") if l.created_at else "Recent"
            }
            for l in db_logs
        ]
        return {
            "total_logs": len(logs_data),
            "logs": logs_data
        }

    # Fallback to CSV if DB is empty
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as log_file:
                reader = csv.DictReader(log_file)
                for row in reader:
                    logs.append(row)
        except Exception:
            pass

    return {
        "total_logs": len(logs),
        "logs": list(reversed(logs))
    }