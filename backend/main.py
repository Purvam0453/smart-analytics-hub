from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models.user
import models.resume

from auth.routes import router as auth_router
from resume.routes import router as resume_router
from analytics.routes import router as analytics_router
from logs.routes import router as logs_router
from Dashboard.routes import router as dashboard_router

# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Analytics Hub")



# =========================
# CORS CONFIGURATION
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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