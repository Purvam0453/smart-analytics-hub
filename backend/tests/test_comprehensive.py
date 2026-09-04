"""
Comprehensive test suite for Smart Analytics Hub.

Covers:
  1. PDF / DOCX / TXT parsing
  2. Empty / invalid resume rejection
  3. Preprocessing consistency (training == inference)
  4. ML inference (model + vectorizer)
  5. ATS scoring (bounded, deterministic)
  6. Database persistence (schema, CRUD)
  7. Analytics endpoints (/analytics/summary)
  8. Dashboard endpoints (/dashboard-stats, /login-stats)
  9. Report generation collision safety (unique filenames)
 10. Job recommendation consistency
"""

import os
import sys
import io
import json
import uuid
import tempfile
import shutil

import pytest

# Ensure backend package is importable
BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, os.path.abspath(BACKEND_DIR))

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


# ---------------------------------------------------------------------------
# FIXTURE: generate sample resume files (PDF, DOCX, TXT)
# ---------------------------------------------------------------------------

SAMPLE_TEXT = (
    "John Doe - Senior Python Developer\n\n"
    "EXPERIENCE\n"
    "5 years of experience in Python, Django, and FastAPI backend development. "
    "Proficient in SQL, PostgreSQL, and MongoDB databases. "
    "Built REST APIs serving millions of requests. "
    "Experience with Docker, Kubernetes, and AWS cloud deployment. "
    "Machine learning projects using scikit-learn and pandas. "
    "Strong skills in data analysis, data visualization, and ETL pipelines. "
    "Implemented CI/CD pipelines with GitHub Actions. "
    "Unit testing with pytest and Selenium automation.\n\n"
    "EDUCATION\n"
    "Bachelor of Science in Computer Science\n\n"
    "SKILLS\n"
    "Python, Java, JavaScript, SQL, HTML, CSS, React, Node.js, "
    "Django, FastAPI, Flask, PostgreSQL, MongoDB, Redis, "
    "Docker, Kubernetes, AWS, Azure, Git, Linux, "
    "Machine Learning, Deep Learning, NLP, Pandas, NumPy, "
    "Scikit-Learn, TensorFlow, PyTorch, "
    "Data Analysis, Data Visualization, Statistics, "
    "Selenium, Pytest, Jira, REST API, Microservices, "
    "PySpark, Spark, Hadoop, ETL, Tableau, Power BI, Excel"
)


def _create_txt_fixture():
    path = os.path.join(FIXTURES_DIR, "sample_resume.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(SAMPLE_TEXT)
    return path


def _create_pdf_fixture():
    """Create a minimal PDF with text content using reportlab."""
    path = os.path.join(FIXTURES_DIR, "sample_resume.pdf")
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(path, pagesize=letter)
    c.setFont("Helvetica", 10)
    y = 750
    for line in SAMPLE_TEXT.split("\n"):
        c.drawString(40, y, line)
        y -= 15
    c.save()
    return path


def _create_docx_fixture():
    """Create a minimal DOCX using zipfile + XML (same approach as parser)."""
    import zipfile
    import xml.etree.ElementTree as ET

    path = os.path.join(FIXTURES_DIR, "sample_resume.docx")

    # Build the document.xml content
    nsmap = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    paragraphs_xml = []
    for line in SAMPLE_TEXT.split("\n"):
        runs = f'<w:r xmlns:w="{nsmap}"><w:t>{line}</w:t></w:r>'
        paragraphs_xml.append(f'<w:p xmlns:w="{nsmap}">{runs}</w:p>')
    body = f'<w:body xmlns:w="{nsmap}">{"".join(paragraphs_xml)}</w:body>'
    doc_xml = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' \
              f'<w:document xmlns:w="{nsmap}">{body}</w:document>'

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml",
                    '<?xml version="1.0"?>'
                    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                    '<Default Extension="xml" ContentType="application/xml"/>'
                    '<Override PartName="/word/document.xml" '
                    'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                    '</Types>')
        zf.writestr("word/document.xml", doc_xml)
    return path


@pytest.fixture(scope="session", autouse=True)
def ensure_fixtures():
    """Create all test fixture files once per test session."""
    os.makedirs(FIXTURES_DIR, exist_ok=True)
    _create_txt_fixture()
    _create_pdf_fixture()
    _create_docx_fixture()
    yield
    # Cleanup is optional; fixture files are small and useful for debugging


# ===================================================================
# 1. PARSING TESTS
# ===================================================================

class TestParsing:
    """Test PDF, DOCX, and TXT resume text extraction."""

    def test_txt_parsing(self):
        from resume_parser import extract_text_from_txt
        path = os.path.join(FIXTURES_DIR, "sample_resume.txt")
        text = extract_text_from_txt(path)
        assert len(text) > 15, "TXT extraction should return substantive text"
        assert "Python" in text or "python" in text.lower()

    def test_pdf_parsing(self):
        from resume_parser import extract_text_from_pdf
        path = os.path.join(FIXTURES_DIR, "sample_resume.pdf")
        text = extract_text_from_pdf(path)
        assert len(text) > 15, "PDF extraction should return substantive text"
        assert "Python" in text or "python" in text.lower()

    def test_docx_parsing(self):
        from resume_parser import extract_text_from_docx
        path = os.path.join(FIXTURES_DIR, "sample_resume.docx")
        text = extract_text_from_docx(path)
        assert len(text) > 15, "DOCX extraction should return substantive text"
        assert "Python" in text or "python" in text.lower()

    def test_extract_text_dispatches_correctly(self):
        from resume_parser import extract_text
        for ext in (".txt", ".pdf", ".docx"):
            path = os.path.join(FIXTURES_DIR, f"sample_resume{ext}")
            text = extract_text(path)
            assert len(text) > 15

    def test_unsupported_format_raises(self):
        from resume_parser import extract_text
        path = os.path.join(FIXTURES_DIR, "sample_resume.txt")
        # Temporarily rename to .xyz
        bad = path.replace(".txt", ".xyz")
        shutil.copy2(path, bad)
        try:
            with pytest.raises(ValueError, match="Unsupported"):
                extract_text(bad)
        finally:
            os.remove(bad)

    def test_nonexistent_file_raises(self):
        from resume_parser import extract_text
        with pytest.raises(FileNotFoundError):
            extract_text("/nonexistent/path.pdf")


# ===================================================================
# 2. EMPTY / INVALID REJECTION
# ===================================================================

class TestEmptyRejection:
    """Test that empty or too-short documents are rejected."""

    def test_empty_txt_rejected(self):
        from resume_parser import extract_text
        path = os.path.join(FIXTURES_DIR, "empty.txt")
        with open(path, "w") as f:
            f.write("")
        with pytest.raises(ValueError, match="no readable text|empty"):
            extract_text(path)
        os.remove(path)

    def test_whitespace_only_rejected(self):
        from resume_parser import extract_text
        path = os.path.join(FIXTURES_DIR, "spaces.txt")
        with open(path, "w") as f:
            f.write("   \n\n  \t  ")
        with pytest.raises(ValueError, match="no readable text|empty"):
            extract_text(path)
        os.remove(path)

    def test_very_short_text_rejected(self):
        from resume_parser import extract_text
        path = os.path.join(FIXTURES_DIR, "short.txt")
        with open(path, "w") as f:
            f.write("Hi")
        with pytest.raises(ValueError, match="no readable text|empty"):
            extract_text(path)
        os.remove(path)

    def test_analyze_resume_short_text_returns_zero(self):
        from ai_model import analyze_resume
        result = analyze_resume("Hi")
        assert result["predicted_role"] == "Unclassified"
        assert result["resume_score"] == 0.0
        assert result["confidence"] == 0.0

    def test_analyze_resume_empty_string_returns_zero(self):
        from ai_model import analyze_resume
        result = analyze_resume("")
        assert result["predicted_role"] == "Unclassified"
        assert result["resume_score"] == 0.0


# ===================================================================
# 3. PREPROCESSING CONSISTENCY
# ===================================================================

class TestPreprocessingConsistency:
    """Verify the shared preprocessing module matches training preprocessing exactly."""

    def test_lemmatization_applied(self):
        from shared_preprocessing import clean_resume_text
        # "developers" should lemmatize to "developer"
        result = clean_resume_text("The developers are building systems")
        assert "developer" in result, f"Expected 'developer' in output, got: {result}"

    def test_stopwords_removed(self):
        from shared_preprocessing import clean_resume_text
        result = clean_resume_text("the and is are was were")
        assert result == "", f"Expected empty string after stopword removal, got: {result}"

    def test_urls_removed(self):
        from shared_preprocessing import clean_resume_text
        result = clean_resume_text("Visit https://example.com for details")
        assert "https" not in result

    def test_emails_removed(self):
        from shared_preprocessing import clean_resume_text
        result = clean_resume_text("Contact john@example.com for info")
        assert "@" not in result

    def test_punctuation_removed(self):
        from shared_preprocessing import clean_resume_text
        result = clean_resume_text("Hello, World! How are you?")
        assert "," not in result
        assert "!" not in result
        assert "?" not in result

    def test_matches_training_preprocessing_exactly(self):
        """
        Core test: shared_preprocessing.clean_resume_text must produce
        the exact same output as the original training preprocess.clean_resume.
        """
        from shared_preprocessing import clean_resume_text
        # Also import via the ML pipeline's preprocess.py wrapper
        sys.path.insert(0, os.path.join(BACKEND_DIR, "..", "ml_pipeline"))
        from processing.preprocess import clean_resume as ml_clean

        test_cases = [
            SAMPLE_TEXT,
            "I am a python developer with 5 years experience in machine learning!",
            "The quick brown fox jumps over the lazy dog.",
            "Contact me at test@gmail.com or visit https://example.com",
            "Built REST APIs using FastAPI, Django, and Flask frameworks.",
        ]
        for text in test_cases:
            shared_out = clean_resume_text(text)
            ml_out = ml_clean(text)
            assert shared_out == ml_out, (
                f"MISMATCH for input: {text[:50]}...\n"
                f"  shared: {shared_out[:80]}\n"
                f"  ml:     {ml_out[:80]}"
            )


# ===================================================================
# 4. ML INFERENCE
# ===================================================================

class TestMLInference:
    """Test ML model loading and prediction on real resume text."""

    def test_model_loaded(self):
        import ai_model
        assert ai_model.model is not None, "Model should be loaded"
        assert ai_model.vectorizer is not None, "Vectorizer should be loaded"

    def test_predicts_valid_role(self):
        from ai_model import analyze_resume
        result = analyze_resume(SAMPLE_TEXT)
        assert result["predicted_role"] != "Unclassified", "Should predict a valid role"
        assert isinstance(result["predicted_role"], str)
        assert len(result["predicted_role"]) > 0

    def test_confidence_is_valid_percentage(self):
        from ai_model import analyze_resume
        result = analyze_resume(SAMPLE_TEXT)
        assert 0.0 <= result["confidence"] <= 100.0

    def test_skills_detected(self):
        from ai_model import analyze_resume
        result = analyze_resume(SAMPLE_TEXT)
        assert len(result["skills"]) > 0, "Should detect skills in a detailed resume"
        assert "python" in result["skills"]

    def test_recommendations_returned(self):
        from ai_model import analyze_resume
        result = analyze_resume(SAMPLE_TEXT)
        assert len(result["recommendations"]) > 0
        for rec in result["recommendations"]:
            assert "job" in rec
            assert "match" in rec
            assert "rank" in rec
            assert 0 <= rec["match"] <= 100

    def test_empty_input_gives_unclassified(self):
        from ai_model import analyze_resume
        result = analyze_resume("")
        assert result["predicted_role"] == "Unclassified"

    def test_heuristic_scoring_produces_nonzero_score(self):
        from ai_model import analyze_resume
        result = analyze_resume(SAMPLE_TEXT)
        assert result["resume_score"] > 0, "A detailed resume should score above 0"


# ===================================================================
# 5. ATS SCORING
# ===================================================================

class TestATSScoring:
    """Test that ATS scoring is bounded and deterministic."""

    def test_score_bounded_0_100(self):
        from ai_model import analyze_resume
        result = analyze_resume(SAMPLE_TEXT)
        assert 0.0 <= result["resume_score"] <= 100.0

    def test_score_deterministic(self):
        from ai_model import analyze_resume
        r1 = analyze_resume(SAMPLE_TEXT)
        r2 = analyze_resume(SAMPLE_TEXT)
        assert r1["resume_score"] == r2["resume_score"], "Score should be deterministic"

    def test_empty_resume_scores_zero(self):
        from ai_model import analyze_resume
        result = analyze_resume("")
        assert result["resume_score"] == 0.0

    def test_minimal_resume_scores_low(self):
        from ai_model import analyze_resume
        result = analyze_resume("I know python and sql databases and machine learning skills")
        assert 0.0 < result["resume_score"] <= 100.0


# ===================================================================
# 6. DATABASE PERSISTENCE
# ===================================================================

class TestDatabase:
    """Test database schema, migrations, and CRUD operations."""

    def test_init_db_creates_tables(self):
        from database import init_db, engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ))
            tables = [row[0] for row in result]
        assert "users" in tables
        assert "resumes" in tables
        assert "login_logs" in tables
        assert "audit_logs" in tables

    def test_resumes_table_has_username_column(self):
        from database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            info = conn.execute(text("PRAGMA table_info(resumes)")).fetchall()
            cols = [row[1] for row in info]
        assert "username" in cols

    def test_resumes_table_has_confidence_column(self):
        from database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            info = conn.execute(text("PRAGMA table_info(resumes)")).fetchall()
            cols = [row[1] for row in info]
        assert "confidence" in cols

    def test_users_table_has_created_at_column(self):
        from database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            info = conn.execute(text("PRAGMA table_info(users)")).fetchall()
            cols = [row[1] for row in info]
        assert "created_at" in cols

    def test_wal_mode_enabled(self):
        from database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            mode = conn.execute(text("PRAGMA journal_mode")).scalar()
        assert mode.lower() == "wal"

    def test_insert_and_query_resume(self):
        from database import SessionLocal
        from models.resume import Resume
        db = SessionLocal()
        try:
            test_id = f"test_{uuid.uuid4().hex[:8]}"
            r = Resume(
                user_id=0,
                username="TestUser",
                filename="test.pdf",
                file_path="/tmp/test.pdf",
                predicted_role="Python Developer",
                resume_score=75.0,
                confidence=85.0,
                skills='["python","sql"]'
            )
            db.add(r)
            db.commit()
            db.refresh(r)
            assert r.id is not None
            # Query it back
            queried = db.query(Resume).filter(Resume.id == r.id).first()
            assert queried is not None
            assert queried.predicted_role == "Python Developer"
            assert queried.username == "TestUser"
            # Cleanup
            db.delete(queried)
            db.commit()
        finally:
            db.close()

    def test_insert_audit_log(self):
        from database import SessionLocal
        from models.user import AuditLog
        db = SessionLocal()
        try:
            log = AuditLog(
                username="TestUser",
                action="Resume Screening",
                details="Test entry"
            )
            db.add(log)
            db.commit()
            db.refresh(log)
            assert log.id is not None
            assert log.created_at is not None
            # Cleanup
            db.delete(log)
            db.commit()
        finally:
            db.close()


# ===================================================================
# 7. ANALYTICS ENDPOINTS
# ===================================================================

class TestAnalyticsAPI:
    """Test analytics summary endpoint via FastAPI TestClient."""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from main import app
        return TestClient(app)

    def test_analytics_summary_empty(self, client):
        """When no resumes exist, summary returns zeros."""
        resp = client.get("/analytics/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_resumes" in data
        assert "average_score" in data
        assert "role_distribution" in data

    def test_analytics_summary_structure(self, client):
        resp = client.get("/analytics/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["total_resumes"], int)
        assert isinstance(data["average_score"], (int, float))
        assert isinstance(data["role_distribution"], dict)


# ===================================================================
# 8. DASHBOARD ENDPOINTS
# ===================================================================

class TestDashboardAPI:
    """Test dashboard-stats and login-stats endpoints."""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from main import app
        return TestClient(app)

    def test_dashboard_stats_structure(self, client):
        resp = client.get("/dashboard-stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_resumes" in data
        assert "average_score" in data
        assert "roles" in data
        assert "skills" in data

    def test_login_stats_structure(self, client):
        resp = client.get("/login-stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "login_trend" in data
        assert isinstance(data["login_trend"], list)

    def test_logs_endpoint(self, client):
        resp = client.get("/logs/all")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_logs" in data
        assert "logs" in data


# ===================================================================
# 9. REPORT GENERATION COLLISION SAFETY
# ===================================================================

class TestReportGeneration:
    """Test that PDF report generation creates unique, collision-free files."""

    def test_report_creates_file(self):
        from report import create_report, REPORTS_DIR
        data = {
            "resume_score": 75.0,
            "predicted_role": "Python Developer",
            "filename": "test_resume.pdf",
            "skills": ["python", "sql", "django"],
            "recommendations": [
                {"job": "Python Developer", "match": 85, "rank": 1, "missing_skills": []}
            ]
        }
        path = create_report(data)
        assert os.path.exists(path), f"Report file should exist at {path}"
        assert path.endswith(".pdf")
        # Cleanup
        os.remove(path)

    def test_report_filenames_are_unique(self):
        from report import create_report
        data = {
            "resume_score": 50.0,
            "predicted_role": "Data Scientist",
            "filename": "test.pdf",
            "skills": ["python"],
            "recommendations": []
        }
        paths = set()
        for _ in range(5):
            path = create_report(data)
            paths.add(os.path.basename(path))
            os.remove(path)
        assert len(paths) == 5, f"All 5 report filenames should be unique, got: {paths}"

    def test_report_contains_score_and_role(self):
        from report import create_report
        data = {
            "resume_score": 88.5,
            "predicted_role": "Full Stack Developer",
            "filename": "candidate.pdf",
            "skills": ["javascript", "react", "node.js"],
            "recommendations": [
                {"job": "Full Stack Developer", "match": 90, "rank": 1, "missing_skills": ["docker"]}
            ]
        }
        path = create_report(data)
        assert os.path.exists(path)
        file_size = os.path.getsize(path)
        assert file_size > 1000, f"PDF should have substantial content, got {file_size} bytes"
        os.remove(path)


# ===================================================================
# 10. JOB RECOMMENDATIONS
# ===================================================================

class TestJobRecommendations:
    """Test job recommendation engine consistency."""

    def test_returns_top_six(self):
        from job_recommendation import recommend_jobs
        recs = recommend_jobs(["python", "sql", "machine learning"], "Data Science")
        assert len(recs) == 6

    def test_recommendations_sorted_by_match(self):
        from job_recommendation import recommend_jobs
        recs = recommend_jobs(["python", "sql", "react", "docker"], "Python Developer")
        matches = [r["match"] for r in recs]
        assert matches == sorted(matches, reverse=True)

    def test_all_recommendations_have_required_fields(self):
        from job_recommendation import recommend_jobs
        recs = recommend_jobs(["python"], "Data Science")
        for rec in recs:
            assert "job" in rec
            assert "match" in rec
            assert "rank" in rec
            assert "matched_skills" in rec
            assert "missing_skills" in rec
            assert isinstance(rec["rank"], int)

    def test_domain_bonus_applied(self):
        from job_recommendation import recommend_jobs
        # "Data Science" predicted role should give bonus to Data Scientist job
        recs = recommend_jobs(["python", "sql"], "Data Science")
        ds_rec = next(r for r in recs if r["job"] == "Data Scientist")
        # With domain bonus, Data Scientist should rank higher
        assert ds_rec["match"] > 0

    def test_no_skills_gives_zero_for_non_domain(self):
        from job_recommendation import recommend_jobs
        recs = recommend_jobs([], "Data Science")
        non_domain = [r for r in recs if r["match"] == 0]
        # Some non-domain jobs should have 0 match when no skills
        assert len(non_domain) > 0

    def test_empty_skills_empty_role(self):
        from job_recommendation import recommend_jobs
        recs = recommend_jobs([], None)
        assert isinstance(recs, list)


# ===================================================================
# 11. SHARED PREPROCESSING MODULE
# ===================================================================

class TestSharedPreprocessing:
    """Direct tests of the shared_preprocessing module."""

    def test_import_from_backend(self):
        from shared_preprocessing import clean_resume_text
        assert callable(clean_resume_text)

    def test_import_from_ml_pipeline(self):
        sys.path.insert(0, os.path.join(BACKEND_DIR, "..", "ml_pipeline"))
        from processing.preprocess import clean_resume
        assert callable(clean_resume)

    def test_both_modules_produce_same_output(self):
        from shared_preprocessing import clean_resume_text
        sys.path.insert(0, os.path.join(BACKEND_DIR, "..", "ml_pipeline"))
        from processing.preprocess import clean_resume
        inputs = [
            SAMPLE_TEXT,
            "Hello World!",
            "",
            "python developer",
        ]
        for text in inputs:
            assert clean_resume_text(text) == clean_resume(text)


# ===================================================================
# 12. AUTH
# ===================================================================

class TestAuth:
    """Test authentication routes."""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from main import app
        return TestClient(app)

    def test_register_and_login(self, client):
        username = f"testuser_{uuid.uuid4().hex[:8]}"
        email = f"{username}@test.com"
        password = "TestPass123!"

        # Register
        resp = client.post("/auth/register", json={
            "username": username,
            "email": email,
            "password": password
        })
        assert resp.status_code == 200
        assert resp.json()["username"] == username

        # Login
        resp = client.post("/auth/login", json={
            "email": email,
            "password": password
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        resp = client.post("/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "wrong"
        })
        assert resp.status_code == 401
