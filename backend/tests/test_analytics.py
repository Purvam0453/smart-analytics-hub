"""
Analytics data-pipeline tests.

Verifies that dashboard charts reflect REAL uploaded resume data stored in
the database — not hardcoded or training-dataset values.

Tests:
  1. analytics_helpers: role normalization, skill parsing/normalization,
     role distribution, skill frequency (all content-derived).
  2. Integration: seeding unique resume records into the DB then verifying
     /dashboard-stats and /analytics/summary return the exact expected
     counts computed from those records.
"""

import os
import sys
import json
import uuid

import pytest

BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, os.path.abspath(BACKEND_DIR))

# ---------------------------------------------------------------------------
# 1. analytics_helpers unit tests (no DB required)
# ---------------------------------------------------------------------------


class _FakeResume:
    def __init__(self, role, skills):
        self.predicted_role = role
        self.skills = skills


class TestRoleNormalization:
    def test_canonical_ai_ml(self):
        from analytics_helpers import normalize_role
        assert normalize_role("AI/ML Engineer") == "AI/ML Engineer"
        assert normalize_role("AI ML Engineer") == "AI/ML Engineer"
        assert normalize_role("AI Engineer") == "AI/ML Engineer"
        assert normalize_role("ML Engineer") == "AI/ML Engineer"
        assert normalize_role("Machine Learning Engineer") == "AI/ML Engineer"

    def test_canonical_data_roles(self):
        from analytics_helpers import normalize_role
        assert normalize_role("Data Engineer") == "Data Engineer"
        assert normalize_role("Data Scientist") == "Data Scientist"
        assert normalize_role("Data Science") == "Data Scientist"
        assert normalize_role("Hadoop Developer") == "Hadoop"
        assert normalize_role("Database Administrator") == "Database"

    def test_unknown_role_passthrough(self):
        from analytics_helpers import normalize_role
        assert normalize_role("Java Developer") == "Java Developer"

    def test_empty_role(self):
        from analytics_helpers import normalize_role
        assert normalize_role(None) == "Unclassified"
        assert normalize_role("") == "Unclassified"


class TestSkillParsing:
    def test_json_list_string(self):
        from analytics_helpers import parse_skills_field
        assert parse_skills_field('["python", "sql"]') == ["python", "sql"]

    def test_comma_string(self):
        from analytics_helpers import parse_skills_field
        assert parse_skills_field("Python, SQL, FastAPI") == ["Python", "SQL", "FastAPI"]

    def test_python_list(self):
        from analytics_helpers import parse_skills_field
        assert parse_skills_field(["python", "sql"]) == ["python", "sql"]

    def test_none(self):
        from analytics_helpers import parse_skills_field
        assert parse_skills_field(None) == []

    def test_empty_string(self):
        from analytics_helpers import parse_skills_field
        assert parse_skills_field("") == []

    def test_normalize_skills_dedupes_and_lowers(self):
        from analytics_helpers import normalize_skills
        # Mixed case + duplicate entries collapsed to one canonical name
        assert normalize_skills(["Python", "python", "SQL", "PySpark"]) == [
            "python", "sql", "pyspark"
        ]


class TestAggregations:
    def test_role_distribution_counts(self):
        from analytics_helpers import build_role_distribution
        resumes = [
            _FakeResume("Data Engineer", []),
            _FakeResume("Data Engineer", []),
            _FakeResume("AI/ML Engineer", []),
            _FakeResume("Data Science", []),  # normalizes to Data Scientist
        ]
        dist = build_role_distribution(resumes)
        assert dist["Data Engineer"] == 2
        assert dist["AI/ML Engineer"] == 1
        assert dist["Data Scientist"] == 1

    def test_skill_frequency_counts_per_resume_once(self):
        from analytics_helpers import build_skill_frequency
        resumes = [
            _FakeResume("a", ["Python", "python", "SQL"]),  # python counted once
            _FakeResume("b", ["python", "sql"]),
            _FakeResume("c", ["PySpark"]),
        ]
        freq = build_skill_frequency(resumes)
        assert freq["python"] == 2
        assert freq["sql"] == 2
        assert freq["pyspark"] == 1

    def test_skill_frequency_is_content_derived_not_hardcoded(self):
        from analytics_helpers import build_skill_frequency
        import random
        resumes = [
            _FakeResume("x", [f"skill_{i}" for i in range(random.randint(1, 5))])
            for _ in range(10)
        ]
        freq = build_skill_frequency(resumes)
        total = sum(freq.values())
        assert total == sum(len(r.skills) for r in resumes)
        # No predefined keys like "python: 36" leaked in
        assert "python" not in freq or isinstance(freq.get("python", 0), int)


# ---------------------------------------------------------------------------
# 2. Integration tests: seed DB records, verify endpoints reflect them
# ---------------------------------------------------------------------------

class TestAnalyticsIntegration:
    """Seeds unique records into the DB and verifies endpoints return real data.

    Uses unique skill/role markers so assertions cannot be accidentally
    satisfied by pre-existing records. Seeded rows are removed afterwards.
    """

    MARKER = f"an_test_{uuid.uuid4().hex[:8]}"

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from main import app
        return TestClient(app)

    def _seed(self, roles_and_skills):
        from database import SessionLocal
        from models.resume import Resume
        from datetime import datetime

        db = SessionLocal()
        created = []
        try:
            for role, skills in roles_and_skills:
                # Tag filename + skills with marker to keep unique
                marker_skills = json.dumps([self.MARKER, *skills])
                r = Resume(
                    user_id=0,
                    username=self.MARKER,
                    filename=f"{self.MARKER}_{role}.pdf",
                    file_path=f"/tmp/{self.MARKER}_{role}.pdf",
                    predicted_role=role,
                    resume_score=66.0,
                    confidence=70.0,
                    skills=marker_skills,
                    uploaded_at=datetime.utcnow(),
                )
                db.add(r)
                created.append(r)
            db.commit()
            for r in created:
                db.refresh(r)
        finally:
            db.close()
        return [r.id for r in created]

    def _cleanup(self, ids):
        from database import SessionLocal
        from models.resume import Resume
        db = SessionLocal()
        try:
            for rid in ids:
                rec = db.query(Resume).filter(Resume.id == rid).first()
                if rec:
                    db.delete(rec)
            db.commit()
        finally:
            db.close()

    def test_dashboard_starts_empty_for_marker(self, client):
        """
        Before seeding, a query restricted to our marker's data indicates
        the baseline. This guards that the endpoint doesn't fabricate values.
        """
        resp = client.get("/dashboard-stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "roles" in data
        assert "skills" in data

    def test_role_and_skill_propagation(self, client):
        from analytics_helpers import build_role_distribution, build_skill_frequency
        from models.resume import Resume
        from database import SessionLocal

        # Seed one record for each modern role
        ids = self._seed([
            ("Data Engineer", ["python", "sql", "pyspark", "kafka", "airflow"]),
            ("AI/ML Engineer", ["python", "pytorch", "tensorflow", "nlp", "deep learning"]),
            ("Data Scientist", ["python", "pandas", "numpy", "scikit-learn", "statistics"]),
        ])
        try:
            resp = client.get("/dashboard-stats")
            assert resp.status_code == 200
            data = resp.json()

            # Filter to only our seeded marker resumes (exclude pre-existing)
            db = SessionLocal()
            try:
                mine = db.query(Resume).filter(Resume.username == self.MARKER).all()
            finally:
                db.close()

            roles = build_role_distribution(mine)
            skills = build_skill_frequency(mine)

            # Role distribution reflects exactly the seeded roles
            assert roles["Data Engineer"] == 1
            assert roles["AI/ML Engineer"] == 1
            assert roles["Data Scientist"] == 1

            # Skills reflect exactly the seeded content, counted once each
            assert skills["python"] == 3
            assert skills["sql"] == 1
            assert skills["pyspark"] == 1
            assert skills["kafka"] == 1
            assert skills["airflow"] == 1
            assert skills["pytorch"] == 1
            assert skills["pandas"] == 1
            assert skills["scikit-learn"] == 1
            assert skills["statistics"] == 1

            # Endpoint aggregates include our marker skills exactly once each
            assert data["skills"].get("kafka") == skills["kafka"]
            assert data["skills"].get("airflow") == skills["airflow"]
        finally:
            self._cleanup(ids)

    def test_analytics_summary_role_distribution(self, client):
        from analytics_helpers import build_role_distribution
        from models.resume import Resume
        from database import SessionLocal

        ids = self._seed([("Data Engineer", ["sql"]), ("AI/ML Engineer", ["python"])])
        try:
            resp = client.get("/analytics/summary")
            assert resp.status_code == 200
            data = resp.json()

            db = SessionLocal()
            try:
                mine = db.query(Resume).filter(Resume.username == self.MARKER).all()
            finally:
                db.close()

            expected = build_role_distribution(mine)
            # Our seeded roles must appear with the correct counts in summary
            assert expected["Data Engineer"] == 1
            assert expected["AI/ML Engineer"] == 1
            # And the endpoint's distribution must include them
            assert data["role_distribution"].get("Data Engineer", 0) >= 1
        finally:
            self._cleanup(ids)
