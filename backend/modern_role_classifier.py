"""
Modern Role Classifier — Stage 2 of the two-stage prediction pipeline.

Classifies resumes into modern data/AI roles that are absent from the
original 25-class supervised dataset:
  - Data Engineer
  - AI/ML Engineer
  - Data Scientist

Uses a weighted multi-signal scoring approach:
  1. Skill keyword coverage (weighted by relevance)
  2. Technical terminology density
  3. Role/title evidence in text
  4. Project description patterns
  5. Tool and framework co-occurrence

Each role maintains an independent score. The role with the highest
score wins, but only if it exceeds a minimum threshold — otherwise
the caller falls back to the supervised ML model.
"""

import re
from typing import Dict, Tuple


# ---------------------------------------------------------------------------
# Skill taxonomy with weights
# ---------------------------------------------------------------------------
# Weight meaning:
#   3.0 = defining skill (almost always present in this role)
#   2.0 = strong indicator (very common)
#   1.5 = moderate indicator (frequently seen)
#   1.0 = weak indicator (could appear in multiple roles)

_DATA_ENGINEER_SKILLS = {
    # Core DE tools
    "spark": 3.0,
    "pyspark": 3.0,
    "apache spark": 3.0,
    "kafka": 3.0,
    "apache kafka": 3.0,
    "airflow": 3.0,
    "apache airflow": 3.0,
    "hadoop": 2.5,
    "hdfs": 2.5,
    "hive": 2.5,
    "databricks": 2.5,
    "snowflake": 2.0,
    "redshift": 2.0,
    "bigquery": 2.0,
    "aws glue": 2.0,
    "azure data factory": 2.5,
    "data factory": 2.0,
    # ETL / pipeline
    "etl": 2.0,
    "data pipeline": 2.5,
    "data pipelines": 2.5,
    "data warehouse": 2.0,
    "data lake": 2.5,
    "data lakehouse": 2.5,
    "delta lake": 2.0,
    # Streaming
    "streaming": 2.0,
    "real-time": 1.5,
    "real time": 1.5,
    "batch processing": 2.0,
    # Languages / DB
    "sql": 1.5,
    "python": 1.0,
    "scala": 1.5,
    "java": 1.0,
    "shell scripting": 1.5,
    "bash": 1.0,
    "postgresql": 1.0,
    "mysql": 1.0,
    "mongodb": 1.0,
    "redis": 1.0,
    "cassandra": 1.5,
    "hbase": 1.5,
    "sqoop": 2.0,
    "flume": 1.5,
    "pig": 1.5,
    "oozie": 1.5,
    "informatica": 1.5,
    "talend": 1.5,
    "dbt": 2.0,
    "glue": 1.5,
}

_AI_ML_ENGINEER_SKILLS = {
    # Frameworks
    "pytorch": 3.0,
    "tensorflow": 3.0,
    "keras": 2.5,
    "jax": 2.5,
    # Core ML/DL
    "deep learning": 3.0,
    "neural network": 2.5,
    "neural networks": 2.5,
    "transformer": 3.0,
    "transformers": 3.0,
    "bert": 2.5,
    "gpt": 2.0,
    "large language model": 2.5,
    "llm": 2.0,
    "attention mechanism": 2.0,
    # NLP
    "nlp": 2.5,
    "natural language processing": 2.5,
    "sentiment analysis": 1.5,
    "named entity recognition": 2.0,
    "ner": 1.5,
    "text classification": 1.5,
    # Computer Vision
    "computer vision": 3.0,
    "object detection": 2.5,
    "image segmentation": 2.5,
    "yolo": 2.0,
    "cnn": 2.0,
    "convolutional": 1.5,
    # Deployment / MLOps
    "model deployment": 3.0,
    "ml deployment": 3.0,
    "mlops": 3.0,
    "mlflow": 2.5,
    "model serving": 2.5,
    "onnx": 2.0,
    "tensorrt": 2.0,
    "triton": 1.5,
    "kubeflow": 2.0,
    # Infrastructure
    "docker": 1.5,
    "kubernetes": 1.5,
    "gpu": 2.0,
    "cuda": 2.5,
    "distributed training": 2.5,
    "multi-gpu": 2.0,
    "fine-tuning": 2.0,
    "fine tuning": 2.0,
    "transfer learning": 2.0,
    # Supporting
    "python": 1.0,
    "numpy": 1.0,
    "scikit-learn": 1.0,
    "hugging face": 2.5,
    "huggingface": 2.5,
    "speech recognition": 2.0,
    "reinforcement learning": 2.0,
    "generative ai": 2.0,
    "gen ai": 2.0,
    "rag": 2.0,
    "recommendation system": 1.5,
    "anomaly detection": 1.5,
}

_DATA_SCIENTIST_SKILLS = {
    # Statistics / Analysis
    "statistics": 3.0,
    "statistical analysis": 3.0,
    "statistical modeling": 3.0,
    "hypothesis testing": 3.0,
    "a/b testing": 2.5,
    "experimentation": 2.0,
    "regression": 2.0,
    "classification": 1.5,
    "clustering": 1.5,
    "probability": 2.0,
    "bayesian": 2.0,
    # Data Analysis
    "data analysis": 2.5,
    "exploratory data analysis": 3.0,
    "eda": 2.5,
    "feature engineering": 2.0,
    "data mining": 1.5,
    "predictive modeling": 2.5,
    "predictive analytics": 2.0,
    # Visualization
    "data visualization": 2.5,
    "visualization": 1.5,
    "tableau": 2.0,
    "power bi": 2.0,
    "matplotlib": 1.5,
    "seaborn": 1.5,
    "plotly": 1.5,
    # Libraries
    "pandas": 2.0,
    "numpy": 1.5,
    "scikit-learn": 2.5,
    "sklearn": 2.0,
    "scipy": 2.0,
    "statsmodels": 2.5,
    "xgboost": 2.0,
    "lightgbm": 2.0,
    # Languages
    "python": 1.0,
    "r": 1.5,
    "sql": 1.0,
    # Business
    "business intelligence": 1.5,
    "kpi": 1.5,
    "dashboard": 1.5,
    "reporting": 1.0,
    "insights": 1.0,
    "metric": 1.0,
    "cohort": 1.5,
    "funnel": 1.0,
}

# Role/title evidence patterns (regex) — bonus points
_ROLE_TITLE_PATTERNS = {
    "Data Engineer": [
        r"\bdata\s+engineer",
        r"\bbig\s+data\s+engineer",
        r"\bpipeline\s+engineer",
        r"\betl\s+engineer",
    ],
    "AI/ML Engineer": [
        r"\bml\s+engineer",
        r"\bmachine\s+learning\s+engineer",
        r"\bai\s+engineer",
        r"\bdeep\s+learning\s+engineer",
        r"\bmlops\s+engineer",
    ],
    "Data Scientist": [
        r"\bdata\s+scientist",
        r"\banalytics\s+scientist",
        r"\bstatistical\s+scientist",
    ],
}

# Project description patterns — moderate bonus
_PROJECT_PATTERNS = {
    "Data Engineer": [
        r"built.*data\s+pipeline",
        r"designed.*etl",
        r"maintained.*data\s+warehouse",
        r"implemented.*data\s+integration",
        r"processing.*(?:terabyte|petabyte|tb|pb)",
        r"real[- ]?time\s+(?:data\s+)?pipeline",
        r"batch\s+processing",
    ],
    "AI/ML Engineer": [
        r"deployed.*(?:model|ml|machine\s+learning)",
        r"trained.*(?:transformer|bert|gpt|neural)",
        r"built.*(?:nlp|computer\s+vision|deep\s+learning)",
        r"production\s+ml",
        r"model\s+(?:serving|inference|deployment)",
        r"fine[- ]?tuned",
    ],
    "Data Scientist": [
        r"built.*predictive\s+model",
        r"performed.*(?:exploratory|statistical)\s+analysis",
        r"designed.*(?:a/b|ab)\s+test",
        r"created.*(?:dashboard|visualization)",
        r"feature\s+engineering",
        r"customer\s+(?:churn|segmentation|lifetime)",
    ],
}


def _count_skill_hits(text_lower: str, skill_weights: Dict[str, float]) -> Tuple[float, int, list]:
    """
    Count weighted skill hits in text.
    Returns (total_weighted_score, hit_count, list_of_matched_skills).
    """
    total = 0.0
    count = 0
    matched = []
    for skill, weight in skill_weights.items():
        if skill in text_lower:
            total += weight
            count += 1
            matched.append(skill)
    return total, count, matched


def _count_pattern_hits(text_lower: str, patterns: list) -> int:
    """Count regex pattern matches in text."""
    count = 0
    for pat in patterns:
        if re.search(pat, text_lower):
            count += 1
    return count


def classify_modern_role(text: str) -> Dict[str, any]:
    """
    Classify resume text into modern data/AI roles using multi-signal scoring.

    Returns dict with:
      - role: str (predicted role or None if no strong match)
      - confidence: float (0-100, normalized score)
      - scores: dict (per-role raw scores for debugging)
      - signals: dict (per-role signal breakdown)
    """
    if not text or len(text.strip()) < 30:
        return {"role": None, "confidence": 0.0, "scores": {}, "signals": {}}

    text_lower = text.lower()

    scores = {}
    signals = {}

    for role, skill_weights in [
        ("Data Engineer", _DATA_ENGINEER_SKILLS),
        ("AI/ML Engineer", _AI_ML_ENGINEER_SKILLS),
        ("Data Scientist", _DATA_SCIENTIST_SKILLS),
    ]:
        # Signal 1: Skill keyword coverage (weighted)
        skill_score, skill_count, matched_skills = _count_skill_hits(text_lower, skill_weights)
        total_possible = sum(skill_weights.values())
        skill_coverage = skill_count / len(skill_weights) if skill_weights else 0

        # Signal 2: Role/title evidence
        title_patterns = _ROLE_TITLE_PATTERNS.get(role, [])
        title_hits = _count_pattern_hits(text_lower, title_patterns)

        # Signal 3: Project description patterns
        project_patterns = _PROJECT_PATTERNS.get(role, [])
        project_hits = _count_pattern_hits(text_lower, project_patterns)

        # Combine signals with weights
        # Skill score is the primary signal (0-100 normalized by max possible)
        skill_component = (skill_score / total_possible) * 100 if total_possible > 0 else 0

        # Title evidence adds up to 20 points
        title_component = min(title_hits * 10, 20)

        # Project evidence adds up to 15 points
        project_component = min(project_hits * 5, 15)

        # Coverage bonus: if >30% of skills match, add bonus
        coverage_bonus = min(skill_coverage * 30, 15) if skill_coverage > 0.3 else 0

        total = skill_component + title_component + project_component + coverage_bonus

        scores[role] = round(total, 2)
        signals[role] = {
            "skill_score": round(skill_component, 2),
            "skill_count": skill_count,
            "matched_skills": matched_skills[:10],
            "title_hits": title_hits,
            "project_hits": project_hits,
            "coverage_bonus": round(coverage_bonus, 2),
        }

    # Find best role
    best_role = max(scores, key=scores.get)
    best_score = scores[best_role]

    # Minimum threshold: must have meaningful skill coverage
    # Threshold: at least 3 skills matched AND score > 15
    best_signals = signals[best_role]
    min_skills = 3
    min_score = 15.0

    if best_signals["skill_count"] < min_skills or best_score < min_score:
        return {
            "role": None,
            "confidence": 0.0,
            "scores": scores,
            "signals": signals,
        }

    # High-weight skill requirement:
    # Must have at least 3 defining skills (weight >= 2.5) matched.
    # For Data Engineer, the 3 defining skills are: spark, pyspark, kafka.
    # ALL three must be present to override the supervised model.
    # This prevents Hadoop resumes (HDFS+Hadoop+Hive) from being misclassified.
    high_weight_count = 0
    defining_skills_met = 0
    for skill in best_signals["matched_skills"]:
        skill_weights_for_role = {
            "Data Engineer": _DATA_ENGINEER_SKILLS,
            "AI/ML Engineer": _AI_ML_ENGINEER_SKILLS,
            "Data Scientist": _DATA_SCIENTIST_SKILLS,
        }
        if skill in skill_weights_for_role.get(best_role, {}):
            weight = skill_weights_for_role[best_role][skill]
            if weight >= 2.5:
                high_weight_count += 1
                defining_skills_met += 1
            elif weight >= 2.0:
                high_weight_count += 1

    # Data Engineer: require at least 3 of the 4 defining skills
    # (spark, pyspark, kafka, airflow) to be present
    if best_role == "Data Engineer":
        de_defining = {"spark", "pyspark", "kafka", "airflow"}
        de_matched = set(best_signals["matched_skills"]) & de_defining
        if len(de_matched) < 3:
            return {
                "role": None,
                "confidence": 0.0,
                "scores": scores,
                "signals": signals,
            }
    else:
        # For AI/ML and Data Scientist: require >= 3 high-weight skills
        if high_weight_count < 3:
            return {
                "role": None,
                "confidence": 0.0,
                "scores": scores,
                "signals": signals,
            }

    # Confidence: normalize best score to 0-100 range
    # Cap at reasonable maximum
    confidence = min(best_score, 100.0)

    return {
        "role": best_role,
        "confidence": round(confidence, 2),
        "scores": scores,
        "signals": signals,
    }
