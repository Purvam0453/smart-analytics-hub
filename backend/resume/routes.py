from fastapi import APIRouter, UploadFile, File
import os
import shutil
import csv
from datetime import datetime

from fastapi.responses import FileResponse

from report import create_report

from resume_parser import extract_text
from ai_model import analyze_resume
from job_recommendation import recommend_jobs

from logs.routes import save_log



router = APIRouter(

    prefix="/resume",

    tags=["Resume"]

)



UPLOAD_FOLDER = "uploads"

CSV_FILE = "results.csv"



if not os.path.exists(UPLOAD_FOLDER):

    os.makedirs(UPLOAD_FOLDER)



# Create results.csv if not exists

if not os.path.exists(CSV_FILE):

    with open(

        CSV_FILE,

        "w",

        newline="",

        encoding="utf-8"

    ) as csv_file:


        writer = csv.writer(csv_file)


        writer.writerow(

            [

                "username",

                "filename",

                "skills",

                "predicted_role",

                "resume_score",

                "date_time"

            ]

        )





# =========================
# UPLOAD RESUME API
# =========================


@router.post("/upload")
async def upload_resume(

    file: UploadFile = File(...)

):


    file_location = f"{UPLOAD_FOLDER}/{file.filename}"



    with open(file_location, "wb") as buffer:

        shutil.copyfileobj(

            file.file,

            buffer

        )



    # Log Upload

    save_log(

        "Guest",

        "Resume Upload",

        file.filename

    )



    # Extract Text

    resume_text = extract_text(

        file_location

    )



    # AI Analysis

    analysis = analyze_resume(

        resume_text

    )



    # Job Recommendation

    recommendations = recommend_jobs(

        analysis["skills"]

    )



    # Save Result CSV

    with open(

        CSV_FILE,

        "a",

        newline="",

        encoding="utf-8"

    ) as csv_file:


        writer = csv.writer(csv_file)


        writer.writerow(

            [

                "Guest",

                file.filename,

                str(analysis["skills"]),

                analysis["predicted_role"],

                analysis["resume_score"],

                datetime.now().strftime(

                    "%Y-%m-%d %H:%M:%S"

                )

            ]

        )




    # Log Prediction

    save_log(

        "Guest",

        "Prediction",

        f"Role: {analysis['predicted_role']} | Score: {analysis['resume_score']}"

    )




    return {


        "message":

        "Resume analyzed successfully",


        "filename":

        file.filename,


        "skills":

        analysis["skills"],


        "predicted_role":

        analysis["predicted_role"],


        "resume_score":

        analysis["resume_score"],


        "recommendations":

        recommendations


    }







# =========================
# REPORT API
# =========================


@router.post("/report")

async def generate_report(data: dict):


    try:


        report_file = create_report(data)



        return FileResponse(

            path=report_file,

            media_type="application/pdf",

            filename="AI_Resume_Report.pdf"

        )


    except Exception as e:


        return {

            "error": str(e)

        }