from typing import List, Optional, Dict, Any

# Benchmark job roles and their key competency skills
jobs = {
    # Data & AI
    "Data Scientist": [
        "python", "machine learning", "pandas", "numpy", "sql", "scikit-learn", "statistics", "data analysis"
    ],
    "AI / ML Engineer": [
        "python", "machine learning", "deep learning", "tensorflow", "pytorch", "nlp", "computer vision", "numpy"
    ],
    "Data Engineer": [
        "python", "sql", "pyspark", "azure", "aws", "databricks", "hadoop", "spark", "etl"
    ],
    "Data Analyst": [
        "python", "sql", "pandas", "numpy", "excel", "power bi", "tableau", "data visualization"
    ],
    "Business Analyst": [
        "sql", "excel", "tableau", "power bi", "data analysis", "jira", "statistics"
    ],

    # Software Engineering
    "Python Developer": [
        "python", "fastapi", "django", "flask", "sql", "api", "git", "docker"
    ],
    "Java Developer": [
        "java", "spring boot", "sql", "microservices", "git", "rest api"
    ],
    "Backend Developer": [
        "python", "node.js", "java", "fastapi", "django", "express", "sql", "postgresql", "mongodb", "api"
    ],
    "Frontend Developer": [
        "javascript", "typescript", "react", "html", "css", "vue", "angular", "tailwind", "redux"
    ],
    "Full Stack Developer": [
        "javascript", "react", "node.js", "python", "sql", "html", "css", "git", "docker"
    ],
    "DotNet Developer": [
        "c#", "sql", "rest api", "git", "microservices", "azure"
    ],

    # Infrastructure & Quality
    "DevOps & Cloud Engineer": [
        "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "linux", "terraform", "git"
    ],
    "Cybersecurity Specialist": [
        "linux", "python", "aws", "azure", "docker", "testing", "microservices"
    ],
    "QA / Automation Tester": [
        "python", "selenium", "java", "sql", "testing", "pytest", "jira"
    ],

    # Enterprise & Emerging Tech
    "Database Administrator": [
        "sql", "postgresql", "mysql", "mongodb", "redis", "linux", "etl"
    ],
    "Big Data Engineer": [
        "hadoop", "spark", "pyspark", "python", "sql", "databricks", "aws", "etl"
    ],
    "Blockchain Developer": [
        "python", "javascript", "c++", "node.js", "git", "docker"
    ],
    "Project / PMO Manager": [
        "jira", "excel", "git", "ci/cd", "data analysis"
    ]
}

# Domain mapping for ML prediction alignment
ROLE_DOMAIN_MAP = {
    "Data Science": ["Data Scientist", "AI / ML Engineer", "Data Analyst"],
    "Python Developer": ["Python Developer", "Backend Developer", "Full Stack Developer"],
    "Java Developer": ["Java Developer", "Backend Developer", "Full Stack Developer"],
    "DevOps Engineer": ["DevOps & Cloud Engineer", "Cybersecurity Specialist"],
    "Network Security Engineer": ["Cybersecurity Specialist", "DevOps & Cloud Engineer"],
    "Automation Testing": ["QA / Automation Tester"],
    "Testing": ["QA / Automation Tester"],
    "Database": ["Database Administrator", "Data Engineer"],
    "Hadoop": ["Big Data Engineer", "Data Engineer"],
    "ETL Developer": ["Data Engineer", "Database Administrator"],
    "DotNet Developer": ["DotNet Developer", "Backend Developer", "Full Stack Developer"],
    "Blockchain": ["Blockchain Developer", "Backend Developer"],
    "Web Designing": ["Frontend Developer", "Full Stack Developer"],
    "Business Analyst": ["Business Analyst", "Data Analyst"],
    "PMO": ["Project / PMO Manager", "Business Analyst"]
}


def recommend_jobs(skills: Optional[List[str]] = None, predicted_role: Optional[str] = None) -> List[Dict[str, Any]]:
    if not skills:
        skills = []

    # Normalize skills to lowercase strings
    skills_set = {str(s).strip().lower() for s in skills if s}

    results = []
    preferred_jobs = ROLE_DOMAIN_MAP.get(predicted_role, []) if predicted_role else []

    for job, required_skills in jobs.items():
        matched_skills = [s for s in required_skills if s in skills_set]
        matched_count = len(matched_skills)
        raw_match = (matched_count / len(required_skills)) * 100

        # Domain alignment bonus if the candidate's predicted role directly corresponds to this job
        domain_bonus = 15.0 if job in preferred_jobs else 0.0
        match_score = min(int(round(raw_match + domain_bonus)), 100)

        # If zero skills matched and not in preferred domain, score is 0
        if matched_count == 0 and job not in preferred_jobs:
            match_score = 0

        results.append({
            "job": job,
            "match": match_score,
            "matched_skills": matched_skills,
            "missing_skills": [s for s in required_skills if s not in skills_set]
        })

    # Sort descending by match score, then alphabetically
    results.sort(key=lambda x: (x["match"], len(x["matched_skills"])), reverse=True)

    for index, item in enumerate(results):
        item["rank"] = index + 1

    return results[:6]