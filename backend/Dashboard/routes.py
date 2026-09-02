from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
import json
import os
from datetime import datetime

from database import get_db
from models.resume import Resume
from models.user import LoginLog

router = APIRouter(
    tags=["Dashboard"]
)

RESULT_FILE = "results.csv"


@router.get("/dashboard-stats")
def dashboard_stats(db: Session = Depends(get_db)):
    # 1. Try querying from Database first
    db_resumes = db.query(Resume).all()

    if db_resumes:
        total = len(db_resumes)
        scores = [r.resume_score for r in db_resumes if r.resume_score is not None]
        avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0

        roles = {}
        skills_count = {}
        score_analysis = []

        for r in db_resumes:
            role = r.predicted_role or "Unclassified"
            roles[role] = roles.get(role, 0) + 1

            if r.skills:
                try:
                    s_list = json.loads(r.skills) if isinstance(r.skills, str) and r.skills.startswith("[") else [s.strip() for s in r.skills.split(",") if s.strip()]
                    for s in s_list:
                        s_clean = s.strip().lower()
                        if s_clean:
                            skills_count[s_clean] = skills_count.get(s_clean, 0) + 1
                except Exception:
                    pass

            score_analysis.append({
                "score": str(r.resume_score or 0),
                "count": 1
            })

        return {
            "total_resumes": total,
            "average_score": avg_score,
            "roles": roles,
            "skills": skills_count,
            "score_analysis": score_analysis
        }

    # 2. Fallback to CSV if DB is empty
    if not os.path.exists(RESULT_FILE):
        return {
            "total_resumes": 0,
            "average_score": 0,
            "roles": {},
            "skills": {},
            "score_analysis": []
        }

    try:
        df = pd.read_csv(RESULT_FILE)
    except Exception:
        return {
            "total_resumes": 0,
            "average_score": 0,
            "roles": {},
            "skills": {},
            "score_analysis": []
        }

    if df.empty:
        return {
            "total_resumes": 0,
            "average_score": 0,
            "roles": {},
            "skills": {},
            "score_analysis": []
        }

    roles = df["predicted_role"].value_counts().to_dict() if "predicted_role" in df.columns else {}

    skill_count = {}
    if "skills" in df.columns:
        for skills in df["skills"].dropna():
            cleaned = str(skills).replace("[", "").replace("]", "").replace("'", "")
            for skill in cleaned.split(","):
                skill = skill.strip().lower()
                if skill:
                    skill_count[skill] = skill_count.get(skill, 0) + 1

    score_analysis = []
    if "resume_score" in df.columns:
        for score in df["resume_score"].dropna():
            score_analysis.append({
                "score": str(score),
                "count": 1
            })

    avg_score = round(df["resume_score"].mean(), 2) if "resume_score" in df.columns and not df["resume_score"].empty else 0.0

    return {
        "total_resumes": len(df),
        "average_score": avg_score,
        "roles": roles,
        "skills": skill_count,
        "score_analysis": score_analysis
    }


@router.get("/login-stats")
def login_stats(db: Session = Depends(get_db)):
    logs = db.query(LoginLog).all()

    if logs:
        trend_map = {}
        for l in logs:
            if l.login_time:
                date_str = l.login_time.strftime("%Y-%m-%d")
            else:
                date_str = "Recent"
            trend_map[date_str] = trend_map.get(date_str, 0) + 1

        trend_list = [{"date": k, "count": v} for k, v in trend_map.items()]
        return {"login_trend": trend_list}

    return {
        "login_trend": [
            {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "count": 1
            }
        ]
    }