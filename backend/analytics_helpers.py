"""
Analytics aggregation helpers.

Computes role prediction distribution and skill frequency from real
Resume records stored in the database. All values are derived from
actual uploaded/processed resumes — never hardcoded.

Provides:
  - role_normalize(): canonical role names
  - normalize_skills(): parse + normalize a resume's skills field
  - build_role_distribution(): counts of final predicted roles
  - build_skill_frequency(): counts of skills across resumes (deduped per resume)
"""

import json
from typing import Dict, List

# Canonical role name normalization.
# Maps known legacy/variant labels to a single canonical role so the
# "Role Prediction Distribution" chart never shows near-duplicate variants.
ROLE_CANONICAL_MAP = {
    "AI ML Engineer": "AI/ML Engineer",
    "AI Engineer": "AI/ML Engineer",
    "ML Engineer": "AI/ML Engineer",
    "Deep Learning Engineer": "AI/ML Engineer",
    "Machine Learning Engineer": "AI/ML Engineer",
    "Data Engineer": "Data Engineer",
    "Big Data Engineer": "Data Engineer",
    "Data Scientist": "Data Scientist",
    "Data Science": "Data Scientist",
    "Python Developer": "Python Developer",
    "Hadoop": "Hadoop",
    "Hadoop Developer": "Hadoop",
    "ETL Developer": "ETL Developer",
    "Database": "Database",
    "Database Administrator": "Database",
    "Java Developer": "Java Developer",
}


def normalize_role(role: str) -> str:
    """Return canonical role name for a raw predicted role string."""
    if not role:
        return "Unclassified"
    raw = role.strip()
    if not raw:
        return "Unclassified"
    # Exact canonical known labels
    if raw in ROLE_CANONICAL_MAP:
        return ROLE_CANONICAL_MAP[raw]
    # Case-insensitive lookup
    for key, canonical in ROLE_CANONICAL_MAP.items():
        if key.lower() == raw.lower():
            return canonical
    return raw


def parse_skills_field(skills_field) -> List[str]:
    """
    Parse a Resume.skills field into a list of raw skill strings.

    Handles:
      - JSON-encoded list strings     '[ "python", "sql" ]'
      - Comma-separated plain strings 'Python, SQL, FastAPI'
      - Python list objects (e.g. from in-memory records)
    """
    if skills_field is None:
        return []
    if isinstance(skills_field, list):
        return skills_field
    if isinstance(skills_field, str):
        s = skills_field.strip()
        if not s:
            return []
        if s.startswith("["):
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
        # Fall back to comma split
        return [x.strip() for x in s.split(",") if x.strip()]
    return []


def normalize_skills(skills_field) -> List[str]:
    """
    Parse, normalize, and de-duplicate a resume's skills into canonical
    lowercase names. Skills are counted per-resume once (de-duped).
    """
    seen = set()
    result = []
    for raw in parse_skills_field(skills_field):
        name = str(raw).strip().lower()
        # Remove common punctuation-only remnants
        if not name or name in ("-", "—", ",", "|"):
            continue
        if name not in seen:
            seen.add(name)
            result.append(name)
    return result


def build_role_distribution(resumes) -> Dict[str, int]:
    """
    Count final predicted roles across resume records using canonical
    role names. Returns {role: count} sorted by count descending.
    """
    counts: Dict[str, int] = {}
    for r in resumes:
        role = normalize_role(getattr(r, "predicted_role", None))
        counts[role] = counts.get(role, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))


def build_skill_frequency(resumes) -> Dict[str, int]:
    """
    Count how many resumes contain each normalized skill.

    A skill is counted once per resume (de-duplicated across records),
    so the number reflects candidate/resume frequency — not repeated
    occurrences within one resume.
    """
    counts: Dict[str, int] = {}
    for r in resumes:
        skills = normalize_skills(getattr(r, "skills", None))
        for skill in skills:
            counts[skill] = counts.get(skill, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))
