import csv
import os
from datetime import datetime

CSV_FILE = "results/prediction_result.csv"


def save_prediction(data):
    print("save_prediction function called")

    os.makedirs("results", exist_ok=True)

    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Date",
                "Time",
                "Role",
                "Resume Score",
                "Skills"
            ])

        writer.writerow([
            datetime.now().strftime("%d-%m-%Y"),
            datetime.now().strftime("%H:%M:%S"),
            data["role"],
            data["score"],
            ", ".join(data["skills"])
        ])