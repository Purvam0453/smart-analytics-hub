import os
import re
import joblib
from resume_parser import extract_text
from job_recommendation import recommend_jobs

# ML model paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "trained_model",
    "model.pkl"
)

VECTORIZER_PATH = os.path.join(
    BASE_DIR,
    "trained_model",
    "vectorizer.pkl"
)

# Load model
try:
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    print("ML model and vectorizer loaded successfully.")

except Exception as e:
    print(f"Warning: ML model failed to load from {MODEL_PATH}: {e}")
    model = None
    vectorizer = None


# Comprehensive skill taxonomy with regex patterns
SKILL_PATTERNS = {
    # Programming Languages
    "python": r"\bpython\b",
    "java": r"\bjava\b(?!script)",
    "javascript": r"\b(javascript|js|es6)\b",
    "typescript": r"\b(typescript|ts)\b",
    "c++": r"\bc\+\+\b",
    "c#": r"\bc#|\bcsharp\b",
    "sql": r"\bsql\b",
    "r": r"\br\b(?:\s+programming|\s+language)?",
    "html": r"\bhtml(?:5)?\b",
    "css": r"\bcss(?:3)?\b",

    # Frameworks & Libraries
    "react": r"\b(react|react\.js|reactjs)\b",
    "angular": r"\b(angular|angularjs)\b",
    "vue": r"\b(vue|vue\.js|vuejs)\b",
    "node.js": r"\b(node|node\.js|nodejs)\b",
    "fastapi": r"\bfastapi\b",
    "django": r"\bdjango\b",
    "flask": r"\bflask\b",
    "spring boot": r"\bspring\s*boot\b",
    "express": r"\bexpress(?:\.js)?\b",
    "tailwind": r"\btailwind(?:\s*css)?\b",
    "redux": r"\bredux\b",

    # Data & AI / ML
    "machine learning": r"\bmachine\s+learning\b|\bml\b",
    "deep learning": r"\bdeep\s+learning\b",
    "nlp": r"\b(nlp|natural\s+language\s+processing)\b",
    "computer vision": r"\bcomputer\s+vision\b",
    "pandas": r"\bpandas\b",
    "numpy": r"\bnumpy\b",
    "scikit-learn": r"\b(scikit-learn|sklearn)\b",
    "tensorflow": r"\btensorflow\b",
    "pytorch": r"\bpytorch\b",
    "data analysis": r"\bdata\s+analysis\b",
    "data visualization": r"\bdata\s+visualization\b",
    "statistics": r"\bstatistics\b|\bstatistical\b",
    "pyspark": r"\bpyspark\b",
    "spark": r"\bspark\b",
    "databricks": r"\bdatabricks\b",
    "hadoop": r"\bhadoop\b",
    "etl": r"\betl\b|\bdata\s+pipeline\b",
    "power bi": r"\bpower\s*bi\b",
    "tableau": r"\btableau\b",
    "excel": r"\b(ms\s*)?excel\b",

    # Databases
    "postgresql": r"\b(postgresql|postgres)\b",
    "mysql": r"\bmysql\b",
    "mongodb": r"\bmongodb\b|\bmongo\b",
    "redis": r"\bredis\b",
    "cassandra": r"\bcassandra\b",
    "sqlite": r"\bsqlite\b",

    # Cloud & DevOps
    "aws": r"\b(aws|amazon\s+web\s+services)\b",
    "azure": r"\b(azure|microsoft\s+azure)\b",
    "gcp": r"\b(gcp|google\s+cloud)\b",
    "docker": r"\bdocker\b",
    "kubernetes": r"\b(kubernetes|k8s)\b",
    "ci/cd": r"\b(ci/cd|continuous\s+integration)\b",
    "git": r"\bgit\b|\bgithub\b|\bgitlab\b",
    "linux": r"\blinux\b",
    "terraform": r"\bterraform\b",

    # Testing & Tools
    "selenium": r"\bselenium\b",
    "pytest": r"\bpytest\b",
    "testing": r"\bunit\s*testing\b|\bqa\s*testing\b|\bautomation\s*testing\b",
    "jira": r"\bjira\b",
    "rest api": r"\brest\s*api|\bapi\b",
    "microservices": r"\bmicroservices\b"
}


def extract_skills_from_text(text: str):
    if not text:
        return []

    found_skills = []
    lower_text = text.lower()

    for skill_name, pattern in SKILL_PATTERNS.items():
        if re.search(pattern, lower_text, re.IGNORECASE):
            found_skills.append(skill_name)

    return found_skills


def analyze_resume(text: str):
    if not text:
        text = ""

    # Extract skills using regex taxonomy
    found_skills = extract_skills_from_text(text)

    predicted_role = "General Profile"
    confidence = 70.0

    # ML Inference if model is available
    if model and vectorizer and text.strip():
        try:
            vector = vectorizer.transform([text])
            prediction = model.predict(vector)
            predicted_role = str(prediction[0])

            probability = model.predict_proba(vector)
            confidence = max(probability[0]) * 100

        except Exception as e:
            print(f"Inference error: {e}")

    # Calculate dynamic composite score
    skill_bonus = min(len(found_skills) * 3.5, 35.0)
    base_score = (confidence * 0.65) + skill_bonus
    composite_score = min(
        max(round(base_score, 2), 40.0),
        98.0
    )

    recommendations = recommend_jobs(found_skills)

    return {
        "skills": found_skills,
        "predicted_role": predicted_role,
        "resume_score": composite_score,
        "recommendations": recommendations
    }
