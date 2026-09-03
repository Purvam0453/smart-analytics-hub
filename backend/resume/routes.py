from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import shutil
import csv
import uuid
import json
from datetime import datetime

from database import get_db
from models.resume import Resume
from models.user import User
from auth.jwt import get_optional_current_user
from report import create_report
from resume_parser import extract_text
from ai_model import analyze_resume
from job_recommendation import recommend_jobs
from logs.routes import save_log


router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)


# =========================
# VERCEL WRITABLE STORAGE
# =========================

UPLOAD_FOLDER = "/tmp/uploads"
CSV_FILE = "/tmp/results.csv"


# Create upload folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Create results.csv if not exists
if not os.path.exists(CSV_FILE):
    with open(
        CSV_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:
        writer = csv.writer(csv_file)

        writer.writerow([
            "username",
            "filename",
            "skills",
            "predicted_role",
            "resume_score",
            "date_time"
        ])


# =========================
# UPLOAD & ANALYZE RESUME API
# =========================

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_optional_current_user)
):

    # Validate extension
    filename = file.filename or "resume.pdf"

    ext = os.path.splitext(filename)[1].lower()

    if ext not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a PDF, DOCX, or TXT file."
        )


    # =========================
    # RESOLVE USER
    # =========================

    username = "Guest"
    user_id = 0

    if current_user and current_user.get("email"):

        db_user = (
            db.query(User)
            .filter(User.email == current_user["email"])
            .first()
        )

        if db_user:
            username = db_user.username
            user_id = db_user.id


    # =========================
    # UNIQUE FILE NAME
    # =========================

    file_uuid = uuid.uuid4().hex[:12]

    safe_filename = f"{file_uuid}_{filename}"

    file_location = os.path.join(
        UPLOAD_FOLDER,
        safe_filename
    )


    # =========================
    # SAVE UPLOADED FILE
    # =========================

    try:

        with open(
            file_location,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )


    # =========================
    # LOG UPLOAD
    # =========================

    try:

        save_log(
            username,
            "Resume Upload",
            filename
        )

    except Exception as e:

        print(f"Upload logging error: {e}")


    # =========================
    # EXTRACT RESUME TEXT
    # =========================

    try:

        resume_text = extract_text(
            file_location
        )

    except Exception as e:

        resume_text = ""

        print(
            f"Text extraction failed: {e}"
        )


    # =========================
    # AI ANALYSIS
    # =========================

    try:

        analysis = analyze_resume(
            resume_text
        )

    except Exception as e:

        print(
            f"AI analysis error: {e}"
        )

        analysis = {
            "skills": [],
            "predicted_role": "General",
            "resume_score": 0.0,
            "recommendations": []
        }


    skills = analysis.get(
        "skills",
        []
    )

    predicted_role = analysis.get(
        "predicted_role",
        "General"
    )

    resume_score = analysis.get(
        "resume_score",
        0.0
    )

    recommendations = analysis.get(
        "recommendations",
        []
    )


    # =========================
    # SAVE TO DATABASE
    # =========================

    try:

        db_resume = Resume(
            user_id=user_id,
            filename=filename,
            file_path=file_location,
            predicted_role=predicted_role,
            resume_score=float(resume_score),
            skills=json.dumps(skills),
            uploaded_at=datetime.utcnow()
        )

        db.add(db_resume)

        db.commit()

        db.refresh(db_resume)

    except Exception as e:

        print(
            f"Database insertion error: {e}"
        )

        db.rollback()


    # =========================
    # SAVE RESULT TO CSV
    # =========================

    try:

        with open(
            CSV_FILE,
            "a",
            newline="",
            encoding="utf-8"
        ) as csv_file:

            writer = csv.writer(
                csv_file
            )

            writer.writerow([
                username,
                filename,
                str(skills),
                predicted_role,
                resume_score,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ])

    except Exception as e:

        print(
            f"CSV sync error: {e}"
        )


    # =========================
    # LOG PREDICTION
    # =========================

    try:

        save_log(
            username,
            "Prediction",
            f"Role: {predicted_role} | Score: {resume_score}"
        )

    except Exception as e:

        print(
            f"Prediction logging error: {e}"
        )


    # =========================
    # RETURN RESULT
    # =========================

    return {
        "message": "Resume analyzed successfully",
        "filename": filename,
        "skills": skills,
        "predicted_role": predicted_role,
        "resume_score": resume_score,
        "recommendations": recommendations,
        "username": username
    }


# =========================
# REPORT GENERATION API
# =========================

@router.post("/report")
async def generate_report(data: dict):

    try:

        report_file = create_report(
            data
        )

        if not os.path.exists(
            report_file
        ):
            raise HTTPException(
                status_code=500,
                detail="Report file was not created"
            )

        return FileResponse(
            path=report_file,
            media_type="application/pdf",
            filename="AI_Resume_Report.pdf"
        )

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation error: {str(e)}"
        )