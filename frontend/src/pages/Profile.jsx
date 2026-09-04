import { useState, useEffect } from "react";
import api from "../services/api";
import "./Profile.css";

function Profile() {
  const username = localStorage.getItem("username") || "User";
  const email = localStorage.getItem("email") || "Candidate Account";
  const [stats, setStats] = useState(null);

  useEffect(() => {
    let mounted = true;
    api.get("/analytics/summary")
      .then((res) => {
        if (mounted && res.data) {
          setStats(res.data);
        }
      })
      .catch((err) => {
        console.warn("Profile stats fetch notice:", err);
      });
    return () => {
      mounted = false;
    };
  }, []);

  const totalResumes = stats?.total_resumes || 0;
  const avgScore = stats?.average_score ? `${stats.average_score}%` : "0%";
  const topRole = stats?.highest_score_resume?.role || "General Profile";

  return (
    <div className="profile-container">
      <div className="profile-banner"></div>

      <div className="profile-card">
        <div className="profile-image">
          {username.substring(0, 2).toUpperCase()}
        </div>

        <h1>{username}</h1>
        <p className="designation">{topRole} | Smart Analytics Hub</p>
        <p>{email}</p>

        <div className="profile-stats">
          <div className="stat-box">
            <h2>{totalResumes}</h2>
            <p>Resumes Processed</p>
          </div>

          <div className="stat-box">
            <h2>{avgScore}</h2>
            <p>Avg ATS Score</p>
          </div>

          <div className="stat-box">
            <h2>Active</h2>
            <p>ML Status</p>
          </div>
        </div>

        <div className="section">
          <h3>About Candidate Profile</h3>
          <p>
            AI-powered talent intelligence and resume screening workspace built with Machine Learning, React, and FastAPI.
          </p>
        </div>

        <div className="section">
          <h3>Technical Skills Matrix</h3>
          <div className="tags">
            <span>Python</span>
            <span>React</span>
            <span>FastAPI</span>
            <span>Machine Learning</span>
            <span>SQL</span>
            <span>NLP</span>
            <span>Docker</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Profile;