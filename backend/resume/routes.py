from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import shutil
import uuid
import json
from datetime import datetime

from database import get_db, BASE_DIR
from models.resume import Resume
from models.user import User, AuditLog
from auth.jwt import get_optional_current_user
from report import create_report
from resume_parser import extract_text
from ai_model import analyze_resume
from logs.routes import save_log

router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)

# Upload storage directory
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
except Exception:
    UPLOAD_FOLDER = "/tmp/uploads"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_optional_current_user)
):
    # Validate file extension
    filename = file.filename or "resume.pdf"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Please upload a PDF, DOCX, or TXT file."
        )

    # Resolve user
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

    # Generate unique safe file location
    file_uuid = uuid.uuid4().hex[:12]
    safe_filename = f"{file_uuid}_{filename}"
    file_location = os.path.join(UPLOAD_FOLDER, safe_filename)

    # Save uploaded file
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file on server: {str(e)}"
        )

    # Extract text from resume
    try:
        resume_text = extract_text(file_location)
    except ValueError as ve:
        # Cleanup uploaded file on validation failure
        if os.path.exists(file_location):
            try:
                os.remove(file_location)
            except Exception:
                pass
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        if os.path.exists(file_location):
            try:
                os.remove(file_location)
            except Exception:
                pass
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not parse document: {str(e)}"
        )

    # AI ML Analysis
    try:
        analysis = analyze_resume(resume_text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI model inference failed: {str(e)}"
        )

    skills = analysis.get("skills", [])
    predicted_role = analysis.get("predicted_role", "Unclassified")
    resume_score = float(analysis.get("resume_score", 0.0))
    confidence = float(analysis.get("confidence", 0.0))
    recommendations = analysis.get("recommendations", [])
    role_probabilities = analysis.get("role_probabilities", {})

    # Save record to authoritative Database
    try:
        db_resume = Resume(
            user_id=user_id,
            username=username,
            filename=filename,
            file_path=file_location,
            predicted_role=predicted_role,
            resume_score=resume_score,
            confidence=confidence,
            skills=json.dumps(skills),
            role_probabilities=json.dumps(role_probabilities) if role_probabilities else None,
            uploaded_at=datetime.utcnow()
        )
        db.add(db_resume)

        # Single authoritative screening audit log
        audit_entry = AuditLog(
            username=username,
            action="Resume Screening",
            details=f"File: {filename} | Role: {predicted_role} | Score: {resume_score}%"
        )
        db.add(audit_entry)

        db.commit()
        db.refresh(db_resume)
    except Exception as e:
        db.rollback()
        print(f"Database persistence error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record analysis to database."
        )

    # Save to unified file log
    try:
        save_log(
            username,
            "Resume Screening",
            f"File: {filename} | Role: {predicted_role} | Score: {resume_score}%"
        )
    except Exception as e:
        print(f"Log sync notice: {e}")

    return {
        "message": "Resume analyzed successfully",
        "id": db_resume.id,
        "filename": filename,
        "skills": skills,
        "predicted_role": predicted_role,
        "resume_score": resume_score,
        "confidence": confidence,
        "role_probabilities": role_probabilities,
        "recommendations": recommendations,
        "username": username
    }


@router.post("/report")
async def generate_report(data: dict):
    try:
        report_file = create_report(data)
        if not os.path.exists(report_file):
            raise HTTPException(
                status_code=500,
                detail="Report file was not generated."
            )

        download_name = f"AI_Resume_Report_{data.get('predicted_role', 'Candidate')}.pdf"

        return FileResponse(
            path=report_file,
            media_type="application/pdf",
            filename=download_name
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation error: {str(e)}"
        )


@router.get("/analysis/{resume_id}")
def resume_analysis(resume_id: int, db: Session = Depends(get_db)):
    """
    Current-resume analytics endpoint.

    Returns ONLY the analytics for the single selected resume record:
      - resume metadata (id, filename, username, uploaded_at)
      - final predicted role + confidence
      - extracted skills (deduped, counted once)
      - role probability distribution for this resume (model-derived)
      - screening/processing information

    This powers the dashboard's "current candidate analysis" view so charts
    reflect the uploaded resume rather than aggregate historical records.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume record {resume_id} not found."
        )

    # Skills: parse + normalize (dedupe per resume, independent of global counts)
    from analytics_helpers import normalize_skills, normalize_role
    skills = normalize_skills(resume.skills)

    # Role probabilities stored at analysis time (model-derived)
    role_probs = {}
    if resume.role_probabilities:
        try:
            parsed = json.loads(resume.role_probabilities)
            if isinstance(parsed, dict):
                role_probs = {str(k): round(float(v), 2) for k, v in parsed.items()}
        except Exception:
            role_probs = {}

    predicted_role = normalize_role(resume.predicted_role)

    # Skill counts: each detected skill counted once for the current resume.
    skill_counts = {sk: 1 for sk in skills}

    # Role distribution for the current candidate only:
    # the predicted role represents 100% of this single candidate.
    role_distribution = {predicted_role: 1}

    screening_info = {
        "resume_id": resume.id,
        "filename": resume.filename,
        "username": resume.username or "Guest",
        "uploaded_at": resume.uploaded_at.strftime("%Y-%m-%d %H:%M:%S") if resume.uploaded_at else None,
        "parsing_status": "Completed" if resume.file_path else "Failed",
        "analysis_status": "Completed" if resume.resume_score is not None else "Pending",
        "prediction_status": "Completed" if predicted_role and predicted_role != "Unclassified" else "Pending",
        "resume_score": resume.resume_score or 0.0,
    }

    return {
        "resume_id": resume.id,
        "filename": resume.filename,
        "predicted_role": predicted_role,
        "confidence": resume.confidence or 0.0,
        "resume_score": resume.resume_score or 0.0,
        "skills": skills,
        "skill_counts": skill_counts,
        "role_probabilities": role_probs,
        "role_distribution": role_distribution,
        "screening_information": screening_info,
    }
