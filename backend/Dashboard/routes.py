from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import json
from datetime import datetime

from database import get_db
from models.resume import Resume
from models.user import LoginLog, AuditLog
from analytics_helpers import build_role_distribution, build_skill_frequency, normalize_role

router = APIRouter(
    tags=["Dashboard"]
)


@router.get("/dashboard-stats")
def dashboard_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get live aggregated talent pipeline and candidate analytics from database.
    """
    db_resumes = db.query(Resume).all()

    if not db_resumes:
        return {
            "total_resumes": 0,
            "average_score": 0.0,
            "roles": {},
            "skills": {},
            "score_analysis": []
        }

    total = len(db_resumes)
    scores = [r.resume_score for r in db_resumes if r.resume_score is not None]
    avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0

    # Role prediction distribution + skill frequency computed from real records
    # using canonical normalization (no hardcoded values).
    roles = build_role_distribution(db_resumes)
    skills_count = build_skill_frequency(db_resumes)

    score_analysis = []
    for r in db_resumes:
        score_analysis.append({
            "score": str(r.resume_score or 0.0),
            "count": 1
        })

    return {
        "total_resumes": total,
        "average_score": avg_score,
        "roles": roles,
        "skills": skills_count,
        "score_analysis": score_analysis
    }


@router.get("/login-stats")
def login_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get real screening activity and authentication event trends over time.
    """
    # Query both screening audits and login records for comprehensive activity
    audits = db.query(AuditLog).all()
    login_logs = db.query(LoginLog).all()

    trend_map: Dict[str, int] = {}

    for a in audits:
        if a.created_at:
            date_str = a.created_at.strftime("%Y-%m-%d")
            trend_map[date_str] = trend_map.get(date_str, 0) + 1

    for l in login_logs:
        if l.login_time:
            date_str = l.login_time.strftime("%Y-%m-%d")
            trend_map[date_str] = trend_map.get(date_str, 0) + 1

    trend_list = [
        {"date": k, "count": v}
        for k, v in sorted(trend_map.items())
    ]

    return {"login_trend": trend_list}