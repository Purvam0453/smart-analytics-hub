import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine, init_db
import models.user
import models.resume

from auth.routes import router as auth_router
from resume.routes import router as resume_router
from analytics.routes import router as analytics_router
from logs.routes import router as logs_router
from Dashboard.routes import router as dashboard_router

# Initialize database and migrate schema
init_db()

app = FastAPI(title="Smart Analytics Hub")



# =========================
# CORS CONFIGURATION
# =========================

# Allowed CORS origins. In production set the FRONTEND_URL environment variable,
# e.g. https://your-frontend.vercel.app (comma-separated list supported).
# Localhost origins are kept for local development.
cors_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
_configured_frontend = os.getenv("FRONTEND_URL", "").strip()
if _configured_frontend:
    for _origin in _configured_frontend.split(","):
        _origin = _origin.strip()
        if _origin and _origin not in cors_origins:
            cors_origins.append(_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# =========================
# ROUTERS
# =========================

app.include_router(auth_router)

app.include_router(resume_router)

app.include_router(analytics_router)

app.include_router(logs_router)

app.include_router(dashboard_router)




# =========================
# HOME
# =========================

@app.get("/")
def home():

    return {

        "message":
        "Smart Analytics Hub Backend Running"

    }