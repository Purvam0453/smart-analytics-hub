from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import json

from database import get_db
from models.resume import Resume
from models.user import User
from analytics_helpers import build_role_distribution, normalize_role

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/summary")
def analytics_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Authoritative analytics summary querying directly from the database.
    Handles 0, 1, and multiple resume records with null safety.
    """
    resumes = db.query(Resume).all()

    if not resumes:
        return {
            "total_resumes": 0,
            "average_score": 0.0,
            "highest_score_resume": None,
            "best_user": "None",
            "role_distribution": {},
            "daily_accuracy": []
        }

    valid_scores = [r.resume_score for r in resumes if r.resume_score is not None]
    avg_score = round(sum(valid_scores) / len(valid_scores), 2) if valid_scores else 0.0

    # Highest scoring resume
    highest_resume = max(resumes, key=lambda r: (r.resume_score or 0.0))
    highest_info = {
        "filename": highest_resume.filename,
        "score": highest_resume.resume_score or 0.0,
        "role": normalize_role(highest_resume.predicted_role),
        "username": highest_resume.username or "Guest"
    }

    # Best / most active user
    user_counts: Dict[str, int] = {}
    daily_map: Dict[str, list] = {}

    for r in resumes:
        uname = r.username or "Guest"
        user_counts[uname] = user_counts.get(uname, 0) + 1

        date_str = r.uploaded_at.strftime("%Y-%m-%d") if r.uploaded_at else "Recent"
        if r.resume_score is not None:
            daily_map.setdefault(date_str, []).append(r.resume_score)

    best_user = max(user_counts.items(), key=lambda x: x[1])[0] if user_counts else "Guest"

    daily_accuracy = []
    for date_k, score_list in sorted(daily_map.items()):
        daily_accuracy.append({
            "date": date_k,
            "average_score": round(sum(score_list) / len(score_list), 2),
            "count": len(score_list)
        })

    return {
        "total_resumes": len(resumes),
        "average_score": avg_score,
        "highest_score_resume": highest_info,
        "best_user": best_user,
        "role_distribution": build_role_distribution(resumes),
        "daily_accuracy": daily_accuracy
    }