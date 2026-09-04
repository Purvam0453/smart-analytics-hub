# AI Resume Screening & Job Role Prediction System 🚀

An AI-powered Resume Screening System that analyzes resumes, extracts skills, predicts suitable job roles, and provides analytics through an interactive dashboard.

## 📌 Project Overview

The system helps recruiters and candidates by automatically analyzing resumes using Machine Learning and Natural Language Processing techniques.

Features:
- Resume PDF Upload
- Resume Text Extraction
- Skill Detection
- Job Role Prediction
- Resume Score Calculation
- User Authentication
- Analytics Dashboard
- Resume History & Logs
- ML-based Prediction Pipeline


## 🛠️ Tech Stack

### Frontend
- React.js
- Vite
- JavaScript
- CSS
- Axios
- Recharts

### Backend
- FastAPI
- Python
- SQLAlchemy
- JWT Authentication
- REST API

### Machine Learning
- Python
- Scikit-learn
- NLP
- Pandas
- Joblib

### Database
- SQLite / SQL Database

## 📂 Project Structure

```
Smart-Analytics-Hub/
│
├── backend
│   ├── main.py                  (FastAPI entry point)
│   ├── ai_model.py              (ML inference + skill extraction)
│   ├── modern_role_classifier.py (Stage 2: Data Engineer / AI-ML / Data Scientist)
│   ├── trained_model/           (model.pkl + vectorizer.pkl)
│   ├── auth/                    (JWT authentication)
│   ├── resume/                  (upload, analysis, report endpoints)
│   ├── analytics/               (aggregate analytics)
│   └── Dashboard/               (dashboard stats)
│
├── frontend
│   ├── src/pages/               (Dashboard, Login, Register, ResumeScreener)
│   ├── src/services/api.js      (Axios client - uses VITE_API_URL)
│   └── vercel.json              (Vercel deployment config)
│
├── ml_pipeline
│   └── trained_model/           (training pipeline + original model)
│
├── render.yaml                  (Render backend deployment config)
└── DEPLOYMENT.md                (Step-by-step deployment guide)
```

## 🚀 Deployment

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for complete step-by-step deployment instructions.

**Quick summary:**
- **Frontend:** Vercel (set `VITE_API_URL` to your backend URL)
- **Backend:** Render Web Service (set `FRONTEND_URL` to your Vercel URL, `JWT_SECRET_KEY`)
- **Database:** SQLite (included - no setup needed)
