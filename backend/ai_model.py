import os
import re
import joblib
from typing import Dict, Any, List
from resume_parser import extract_text
from job_recommendation import recommend_jobs
from shared_preprocessing import clean_resume_text
from modern_role_classifier import classify_modern_role

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

# Canonical unclassified role constant
UNCLASSIFIED_ROLE = "Unclassified"

# Load ML model and vectorizer
try:
    if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)
        print("ML model and vectorizer loaded successfully.")
    else:
        # Check parent/sibling ml_pipeline directory fallback
        alt_model = os.path.join(BASE_DIR, "..", "ml_pipeline", "trained_model", "model.pkl")
        alt_vec = os.path.join(BASE_DIR, "..", "ml_pipeline", "trained_model", "vectorizer.pkl")
        if os.path.exists(alt_model) and os.path.exists(alt_vec):
            model = joblib.load(alt_model)
            vectorizer = joblib.load(alt_vec)
            print("ML model and vectorizer loaded from ml_pipeline.")
        else:
            model = None
            vectorizer = None
            print("Warning: ML model not found. Running in heuristic mode.")
except Exception as e:
    print(f"Warning: ML model failed to load: {e}")
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


def extract_skills_from_text(text: str) -> List[str]:
    """Extract matching technical skills from text using regex patterns."""
    if not text:
        return []

    found_skills = []
    lower_text = text.lower()

    for skill_name, pattern in SKILL_PATTERNS.items():
        if re.search(pattern, lower_text, re.IGNORECASE):
            found_skills.append(skill_name)

    return found_skills


def analyze_resume(text: str) -> Dict[str, Any]:
    """
    Analyze resume content:
    1. Extracts domain skills via regex taxonomy.
    2. Runs cleaned text through trained TF-IDF + Classifier.
    3. Computes deterministic composite ATS resume score.
    4. Recommends career paths aligned with skills & predicted domain.
    """
    if not text or len(text.strip()) < 15:
        return {
            "skills": [],
            "predicted_role": UNCLASSIFIED_ROLE,
            "resume_score": 0.0,
            "confidence": 0.0,
            "role_probabilities": {},
            "recommendations": recommend_jobs([], UNCLASSIFIED_ROLE)
        }

    # Extract skills
    found_skills = extract_skills_from_text(text)

    # Preprocess text before TF-IDF vectorization
    cleaned_text = clean_resume_text(text)

    predicted_role = UNCLASSIFIED_ROLE
    confidence = 0.0
    role_probabilities: Dict[str, float] = {}

    # ML Inference (Stage 1: supervised 25-class model)
    if model and vectorizer and cleaned_text:
        try:
            vector = vectorizer.transform([cleaned_text])
            prediction = model.predict(vector)
            predicted_role = str(prediction[0])

            if hasattr(model, "predict_proba"):
                probability = model.predict_proba(vector)[0]
                confidence = float(max(probability)) * 100.0
                # Capture the model's actual per-class probability distribution
                classes = getattr(model, "classes_", None)
                if classes is not None:
                    for cls, prob in zip(classes, probability):
                        role_probabilities[str(cls)] = round(float(prob) * 100.0, 2)
            else:
                confidence = 0.0

        except Exception as e:
            print(f"ML inference error: {e}")
            predicted_role = UNCLASSIFIED_ROLE
            confidence = 0.0
            role_probabilities = {}

    # Stage 2: Modern role classifier for roles absent from training data
    # Checks whether the resume better matches Data Engineer, AI/ML Engineer,
    # or Data Scientist using weighted multi-signal skill taxonomy scoring.
    modern_result = classify_modern_role(text)
    if modern_result["role"] is not None:
        predicted_role = modern_result["role"]
        confidence = modern_result["confidence"]
        # When the modern layer selects the role, use its explainable
        # per-role scores as the probability distribution (normalized).
        scores = modern_result.get("scores", {})
        total = sum(max(v, 0.0) for v in scores.values()) or 1.0
        role_probabilities = {
            r: round(max(v, 0.0) / total * 100.0, 2)
            for r, v in scores.items()
        }

    # Deterministic, explainable ATS resume score:
    # 50% max from ML classification confidence + 50% max from skill breadth (up to 10 detected skills)
    skill_score = min(len(found_skills) * 5.0, 50.0)
    confidence_component = (confidence * 0.5) if predicted_role != UNCLASSIFIED_ROLE else 0.0
    composite_score = round(min(confidence_component + skill_score, 100.0), 2)

    # Job recommendations aligned with predicted role and detected skills
    recommendations = recommend_jobs(found_skills, predicted_role=predicted_role)

    # Sort probabilities descending for clean display
    role_probs_sorted = dict(
        sorted(role_probabilities.items(), key=lambda kv: -kv[1])
    )

    return {
        "skills": found_skills,
        "predicted_role": predicted_role,
        "resume_score": composite_score,
        "confidence": round(confidence, 2),
        "role_probabilities": role_probs_sorted,
        "recommendations": recommendations
    }
