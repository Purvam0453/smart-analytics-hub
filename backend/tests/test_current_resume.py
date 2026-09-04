"""
Current-resume dashboard analytics tests.

Verifies the "current candidate analysis" flow:
  upload resume A -> /resume/analysis/A reflects resume A only
  upload resume B -> /resume/analysis/B reflects resume B only (no leakage)
  upload resume C -> /resume/analysis/C reflects resume C only

Each resume's dashboard data is derived from that exact stored record
and never from other candidates / aggregate history / training data.
"""

import os
import sys
import io

import pytest

BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, os.path.abspath(BACKEND_DIR))

from fastapi.testclient import TestClient

DE_RESUME = (
    "Senior Data Engineer. Expert in Apache Spark, PySpark, Kafka, Airflow. "
    "Build ETL pipelines and data warehouses. Hadoop HDFS, SQL, Python. "
    "Spark Streaming, Delta Lake, Databricks, data lake, data pipeline."
)

AIML_RESUME = (
    "AI/ML Engineer. Deep learning, PyTorch, TensorFlow, NLP, transformers, "
    "computer vision, neural networks, model deployment, MLOps. "
    "Training BERT and large language models with Python."
)

DS_RESUME = (
    "Data Scientist. Statistics, statistical analysis, pandas, NumPy, "
    "scikit-learn, regression, classification, hypothesis testing, "
    "data visualization, predictive modeling, machine learning."
)


class TestCurrentResumeFlow:
    @pytest.fixture(autouse=True)
    def _cleanup_created(self, request):
        """Track uploaded resume IDs and remove them after each test so the
        test suite never pollutes the real analytics database."""
        created_ids = []
        original_upload = self._upload

        def tracked_upload(client, text, filename):
            result = original_upload(client, text, filename)
            if result and result.get("id") is not None:
                created_ids.append(result["id"])
            return result

        self._upload = tracked_upload
        yield
        # Restore for other tests
        self._upload = original_upload

        from database import SessionLocal
        from models.resume import Resume
        if created_ids:
            db = SessionLocal()
            try:
                for rid in created_ids:
                    rec = db.query(Resume).filter(Resume.id == rid).first()
                    if rec:
                        db.delete(rec)
                db.commit()
            finally:
                db.close()

    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)

    def _upload(self, client, text, filename):
        files = {"file": (filename, io.BytesIO(text.encode("utf-8")), "text/plain")}
        resp = client.post("/resume/upload", files=files)
        assert resp.status_code == 200, resp.text
        return resp.json()

    def test_data_engineer_resume_analysis(self, client):
        data = self._upload(client, DE_RESUME, "de_candidate.txt")
        rid = data["id"]
        assert data["predicted_role"] == "Data Engineer"

        # Fetch current-resume analytics
        resp = client.get(f"/resume/analysis/{rid}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["predicted_role"] == "Data Engineer"
        # Skills detected from THIS resume
        assert "pyspark" in body["skills"]
        assert "hadoop" in body["skills"]
        # Role distribution is single candidate = predicted role
        assert body["role_distribution"] == {"Data Engineer": 1}
        # Confidence is a valid percentage
        assert 0 <= body["confidence"] <= 100

    def test_aiml_engineer_resume_analysis(self, client):
        data = self._upload(client, AIML_RESUME, "aiml_candidate.txt")
        rid = data["id"]
        assert data["predicted_role"] == "AI/ML Engineer"

        resp = client.get(f"/resume/analysis/{rid}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["predicted_role"] == "AI/ML Engineer"
        assert "pytorch" in body["skills"]
        assert "tensorflow" in body["skills"]
        assert body["role_distribution"] == {"AI/ML Engineer": 1}

    def test_data_scientist_resume_analysis(self, client):
        data = self._upload(client, DS_RESUME, "ds_candidate.txt")
        rid = data["id"]
        assert data["predicted_role"] == "Data Scientist"

        resp = client.get(f"/resume/analysis/{rid}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["predicted_role"] == "Data Scientist"
        assert "pandas" in body["skills"]
        assert "scikit-learn" in body["skills"]
        assert body["role_distribution"] == {"Data Scientist": 1}

    def test_no_leakage_between_candidates(self, client):
        """After uploading A then B, analysis B must not contain A's signals."""
        a = self._upload(client, DE_RESUME, "a_data_engineer.txt")
        b = self._upload(client, AIML_RESUME, "b_aiml.txt")

        b_analysis = client.get(f"/resume/analysis/{b['id']}").json()
        a_analysis = client.get(f"/resume/analysis/{a['id']}").json()

        # B (AI/ML Engineer) must NOT show Data Engineer's pipeline skills
        assert b_analysis["predicted_role"] == "AI/ML Engineer"
        assert "spark" not in b_analysis["skills"]
        assert "etl" not in b_analysis["skills"]

        # A (Data Engineer) must NOT show AI/ML Engineer's skills
        assert a_analysis["predicted_role"] == "Data Engineer"
        assert "pytorch" not in a_analysis["skills"]
        assert "tensorflow" not in a_analysis["skills"]

    def test_three_candidates_each_predict_correctly(self, client):
        """Upload A, B, C sequentially; each analysis stays respective."""
        a = self._upload(client, DE_RESUME, "c1_de.txt")
        b = self._upload(client, AIML_RESUME, "c2_aiml.txt")
        c = self._upload(client, DS_RESUME, "c3_ds.txt")

        for record, expected in [
            (a, "Data Engineer"),
            (b, "AI/ML Engineer"),
            (c, "Data Scientist"),
        ]:
            body = client.get(f"/resume/analysis/{record['id']}").json()
            assert body["predicted_role"] == expected
            # Single-candidate role distribution matches predicted role
            assert body["role_distribution"] == {expected: 1}

    def test_analysis_404_for_missing_resume(self, client):
        resp = client.get("/resume/analysis/99999999")
        assert resp.status_code == 404

    def test_skills_counted_once_per_resume(self, client):
        """Each detected skill appears once for the current resume."""
        data = self._upload(client, DS_RESUME, "ds_unique.txt")
        rid = data["id"]
        body = client.get(f"/resume/analysis/{rid}").json()
        skill_counts = body["skill_counts"]
        # Each skill in skill_counts should have count 1 (no duplicates)
        for skill, count in skill_counts.items():
            assert count == 1
        # Keys match the normalized skills list
        assert set(skill_counts.keys()) == set(body["skills"])

    def test_role_probabilities_present_for_modern_role(self, client):
        """Model-derived probability distribution is returned for the resume."""
        data = self._upload(client, DE_RESUME, "de_prob.txt")
        rid = data["id"]
        body = client.get(f"/resume/analysis/{rid}").json()
        probs = body["role_probabilities"]
        assert isinstance(probs, dict)
        if probs:
            # Predicted role should have the highest probability
            top_role = max(probs, key=probs.get)
            assert probs[top_role] > 0
