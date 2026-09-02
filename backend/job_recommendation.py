jobs = {
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
    "Python Developer": [
        "python", "fastapi", "django", "flask", "sql", "api", "git", "docker"
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
    "DevOps & Cloud Engineer": [
        "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "linux", "terraform", "git"
    ],
    "Java Developer": [
        "java", "spring boot", "sql", "hibernate", "microservices", "git", "rest api"
    ],
    "Cybersecurity Specialist": [
        "linux", "networking", "python", "security", "cryptography", "firewalls", "penetration testing"
    ],
    "QA / Automation Tester": [
        "python", "selenium", "java", "sql", "testing", "pytest", "automation", "jira"
    ]
}


def recommend_jobs(skills):
    if not skills:
        skills = []
    
    # Normalize skills to lowercase strings
    skills_set = {str(s).strip().lower() for s in skills if s}

    results = []
    for job, required_skills in jobs.items():
        matched_skills = [s for s in required_skills if s in skills_set]
        matched_count = len(matched_skills)
        score = int((matched_count / len(required_skills)) * 100)

        results.append({
            "job": job,
            "match": score,
            "matched_skills": matched_skills,
            "missing_skills": [s for s in required_skills if s not in skills_set]
        })

    # Sort descending by match score
    results.sort(key=lambda x: x["match"], reverse=True)

    for index, item in enumerate(results):
        item["rank"] = index + 1

    return results[:6]