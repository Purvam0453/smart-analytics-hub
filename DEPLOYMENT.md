# Smart Analytics Hub — Deployment Guide

Step-by-step instructions for deploying the college presentation.

---

## Architecture

```
Frontend (React + Vite)    -> Vercel (free)
Backend  (FastAPI + ML)    -> Render  (free web service)
Database (SQLite)          -> Lives inside the Render backend (ephemeral - see note below)
```

> **SQLite note:** Render free web services use ephemeral disk storage.
> SQLite data is reset every time the service restarts or redeploys.
> For a college presentation demo this is acceptable - you upload a resume, the dashboard
> shows analysis, and it stays live for as long as the Render instance is awake.
> If a restart occurs mid-presentation, simply upload the resume again.

---

## Before You Start

You need accounts at:
- **GitHub** (code is already on GitHub)
- **Render** (render.com) - free account
- **Vercel** (vercel.com) - free account

---

## STEP 1 - Push Latest Code to GitHub

```bash
git add .
git commit -m "Prepare project for production deployment"
git push origin main
```

**Verify:** Go to https://github.com/Purvam0453/smart-analytics-hub - confirm the latest files are visible.

---

## STEP 2 - Deploy Backend to Render

### 2a. Create a Render account
Go to https://render.com and sign up (GitHub login is easiest).

### 2b. Create a new Web Service
1. Click **"New +"** -> **"Web Service"**
2. Click **"Build and deploy from a Git repository"** -> **Next**
3. Connect your GitHub account and select: `Purvam0453/smart-analytics-hub`

### 2c. Configure the Web Service

| Setting | Value |
|---------|-------|
| **Name** | `smart-analytics-hub-backend` |
| **Region** | `Oregon` (or closest to you) |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Root Directory** | `backend` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | `Free` |

### 2d. Add Environment Variables
Click **"Advanced"** -> **"Add Environment Variable"** and add:

| Key | Value |
|-----|-------|
| `JWT_SECRET_KEY` | Click **"Generate"** or type a long random string (e.g. `my-super-secret-key-for-presentation-2026`) |
| `FRONTEND_URL` | *(leave blank for now - fill this in after deploying the frontend)* |
| `DATABASE_URL` | *(leave blank - defaults to SQLite)* |

### 2e. Deploy
Click **"Create Web Service"**. Render will:
1. Clone your repo
2. Run `pip install -r requirements.txt` in the `backend/` directory
3. Download NLTK data (stopwords, wordnet) on first boot - takes ~30 seconds
4. Load the ML model (~2.3MB)
5. Start uvicorn

### 2f. Wait for "Live"
Watch the Render logs. When you see:
```
Uvicorn running on http://0.0.0.0:PORT
```
Your backend is live.

### 2g. Get your Backend URL
Your backend URL will be:
```
https://smart-analytics-hub-backend.onrender.com
```
(Replace `smart-analytics-hub-backend` with whatever name you chose.)

**Test it:** Open `https://smart-analytics-hub-backend.onrender.com` in your browser.
You should see:
```json
{"message":"Smart Analytics Hub Backend Running"}
```

> **Cold start:** Render free tier puts the service to sleep after 15 minutes of inactivity.
> The first request after sleep takes 30-60 seconds while the ML model loads.
> Keep the tab open or use a tool like https://cronitor.io/ping to keep it awake during your presentation.

---

## STEP 3 - Deploy Frontend to Vercel

### 3a. Create a Vercel account
Go to https://vercel.com and sign up (GitHub login).

### 3b. Import the project
1. Click **"Add New..."** -> **"Project"**
2. Under **"Import Git Repository"**, select `Purvam0453/smart-analytics-hub`
3. Click **"Import"**

### 3c. Configure the project
Before clicking Deploy, fill in:

| Setting | Value |
|---------|-------|
| **Framework Preset** | `Vite` (auto-detected) |
| **Root Directory** | Click **"Override"** -> type `frontend` |
| **Build Command** | `npm run build` (auto-detected) |
| **Output Directory** | `dist` (auto-detected) |

### 3d. Add Environment Variable
Click **"Environment Variables"** and add:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://smart-analytics-hub-backend.onrender.com` |

> Use your actual Render backend URL from Step 2g. No trailing slash.

### 3e. Deploy
Click **"Deploy"**. Vercel will:
1. Install npm dependencies
2. Run `npm run build`
3. Deploy the static files

### 3f. Get your Frontend URL
When deployment finishes, Vercel gives you a URL like:
```
https://smart-analytics-hub-abc123.vercel.app
```
Click **"Visit"** to confirm the frontend loads.

---

## STEP 4 - Connect Frontend to Backend (CORS)

### 4a. Update Render environment variable
Go back to your **Render dashboard** -> your web service -> **Environment** tab.

Set `FRONTEND_URL` to your actual Vercel URL:
```
https://smart-analytics-hub-abc123.vercel.app
```
(Use your real Vercel URL from Step 3f.)

### 4b. Save and redeploy
Render auto-redeploys when you change environment variables. Wait for the new deploy to finish.

### 4c. Test the connection
1. Open your Vercel URL
2. You should see the login/register page
3. Register a new account
4. Login with those credentials
5. Upload a resume
6. Check the dashboard - it should show analysis for your resume

---

## STEP 5 - Verify Everything Works

Open your **Vercel frontend URL** in a browser and test:

### 5a. Register + Login
- Register with any email/password
- Login with those credentials
- You should see the sidebar with Dashboard, Upload Resume, etc.

### 5b. Upload Resume
- Go to "Upload Resume"
- Upload a PDF, DOCX, or TXT file
- Confirm you see the analysis results (predicted role, skills, confidence, etc.)

### 5c. Dashboard
- Go to "Dashboard"
- Confirm it shows charts for YOUR uploaded resume (not static/fake data)
- The top skills bar chart shows skills from your resume
- The role prediction pie chart shows the model's probability distribution
- Upload a DIFFERENT resume -> go back to Dashboard -> confirm it changed

### 5d. ML Prediction Test
Upload these three resumes and verify the predicted roles:

| Resume Content | Expected Role |
|---------------|---------------|
| Data Engineer (Spark, PySpark, Kafka, Airflow, Hadoop) | **Data Engineer** |
| AI/ML Engineer (PyTorch, TensorFlow, NLP, deep learning) | **AI/ML Engineer** |
| Data Scientist (pandas, scikit-learn, statistics, regression) | **Data Scientist** |

### 5e. Report Download
- After uploading a resume, click "Download Report"
- A PDF should download with the analysis summary

---

## STEP 6 - Redeploy After Changes

### Backend (Render)
Render auto-deploys on every push to `main`. Just run:
```bash
git add .
git commit -m "Your change message"
git push origin main
```

### Frontend (Vercel)
Vercel also auto-deploys on every push to `main`. Same command.

If you change `VITE_API_URL`, update it in Vercel dashboard -> Settings -> Environment Variables -> then click **"Redeploy"** on the latest deployment.

---

## Environment Variables Summary

### Render (Backend)
| Variable | Required | Example |
|----------|----------|---------|
| `JWT_SECRET_KEY` | Yes | `my-secret-key-abc123` |
| `FRONTEND_URL` | Yes | `https://your-app.vercel.app` |
| `DATABASE_URL` | No | *(defaults to SQLite)* |

### Vercel (Frontend)
| Variable | Required | Example |
|----------|----------|---------|
| `VITE_API_URL` | Yes | `https://your-app.onrender.com` |

---

## Known Limitations (College Presentation)

| Limitation | Impact | Workaround |
|------------|--------|------------|
| SQLite is ephemeral on Render | Data resets on restart/redeploy | Upload resume fresh after each restart. Keep the service awake. |
| Render free tier sleeps after 15 min | First request after sleep takes 30-60s | Keep a browser tab open, or use UptimeRobot to ping `/` every 10 min |
| NLTK data downloads on each cold start | Adds ~5s to cold start | Acceptable for a demo |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Cannot connect to backend" | Check `VITE_API_URL` in Vercel matches your Render URL exactly. No trailing slash. |
| CORS error in browser console | Check `FRONTEND_URL` in Render matches your Vercel URL exactly. |
| Upload fails with 500 | Render may be restarting. Wait 30s and try again. Check Render logs. |
| ML model not found warning | The model files (model.pkl, vectorizer.pkl) are in `backend/trained_model/` and committed to GitHub. Should be present after deploy. |
| Render deploy fails | Check build logs. Ensure `requirements.txt` is in the `backend/` directory. |
| Charts show no data | Upload a resume first. The dashboard shows data for the most recently uploaded resume. |
