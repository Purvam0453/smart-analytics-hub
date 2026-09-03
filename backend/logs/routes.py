from fastapi import APIRouter
import csv
import os
from datetime import datetime

router = APIRouter(
    prefix="/logs",
    tags=["Logs"]
)

LOG_FILE = "/tmp/logs.csv"


# =========================
# CREATE LOG FILE
# =========================

if not os.path.exists(LOG_FILE):
    with open(
        LOG_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as log_file:

        writer = csv.writer(log_file)

        writer.writerow([
            "username",
            "action",
            "details",
            "date_time"
        ])


# =========================
# SAVE LOG
# =========================

def save_log(username, action, details):

    with open(
        LOG_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as log_file:

        writer = csv.writer(log_file)

        writer.writerow([
            username,
            action,
            details,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ])


# =========================
# GET ALL LOGS
# =========================

@router.get("/all")
def get_all_logs():

    logs = []

    if os.path.exists(LOG_FILE):

        with open(
            LOG_FILE,
            "r",
            encoding="utf-8"
        ) as log_file:

            reader = csv.DictReader(log_file)

            for row in reader:
                logs.append(row)

    return {
        "total_logs": len(logs),
        "logs": logs
    }