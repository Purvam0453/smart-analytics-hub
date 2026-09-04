import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "app.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        except Exception:
            pass

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

from sqlalchemy import text

Base = declarative_base()


def init_db():
    """Create all tables and perform non-destructive SQLite column migrations."""
    Base.metadata.create_all(bind=engine)
    if DATABASE_URL.startswith("sqlite"):
        try:
            with engine.begin() as conn:
                # Resumes migration
                res_info = conn.execute(text("PRAGMA table_info(resumes)")).fetchall()
                cols = [row[1] for row in res_info]
                if cols:
                    if "username" not in cols:
                        conn.execute(text("ALTER TABLE resumes ADD COLUMN username VARCHAR DEFAULT 'Guest'"))
                    if "confidence" not in cols:
                        conn.execute(text("ALTER TABLE resumes ADD COLUMN confidence FLOAT DEFAULT 0.0"))
                    if "role_probabilities" not in cols:
                        conn.execute(text("ALTER TABLE resumes ADD COLUMN role_probabilities TEXT"))

                # Users migration
                user_info = conn.execute(text("PRAGMA table_info(users)")).fetchall()
                u_cols = [row[1] for row in user_info]
                if u_cols:
                    if "created_at" not in u_cols:
                        conn.execute(text("ALTER TABLE users ADD COLUMN created_at DATETIME"))
        except Exception as e:
            print(f"DB Migration notice: {e}")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()