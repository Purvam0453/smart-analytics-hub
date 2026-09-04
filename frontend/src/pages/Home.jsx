import { useState, useEffect } from "react";
import {
  FaRobot,
  FaFileAlt,
  FaChartLine,
  FaUpload,
  FaBrain,
  FaCheckCircle,
  FaUsers,
  FaStar,
  FaBolt
} from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import "./Home.css";

function Home() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);

  useEffect(() => {
    let mounted = true;
    api.get("/dashboard-stats")
      .then((res) => {
        if (mounted && res.data) {
          setStats(res.data);
        }
      })
      .catch((err) => {
        console.warn("Home dashboard stats fetch notice:", err);
      });
    return () => {
      mounted = false;
    };
  }, []);

  const totalResumes = stats?.total_resumes || 0;
  const avgScore = stats?.average_score ? `${stats.average_score}%` : "0%";
  const uniqueSkills = Object.keys(stats?.skills || {}).length;

  return (
    <div className="home">
      {/* HERO SECTION */}
      <div className="home-hero">
        <div className="hero-icon">
          <FaRobot />
        </div>

        <h1>
          AI Resume Screening
          <br />
          <span>Smart Analytics Hub</span>
        </h1>

        <p>
          Analyze candidate resumes, predict career domains with machine learning, and benchmark industry skills in real time.
        </p>

        <button
          className="home-btn"
          onClick={() => navigate("/resume-screener")}
        >
          <FaUpload />
          &nbsp;
          Analyze Resume Now
        </button>
      </div>

      {/* LIVE STATS */}
      <div className="home-cards">
        <div className="home-card">
          <FaFileAlt className="card-icon" />
          <h2>{totalResumes}</h2>
          <p>Resumes Processed</p>
        </div>

        <div className="home-card">
          <FaUsers className="card-icon" />
          <h2>{uniqueSkills}</h2>
          <p>Skills Indexed</p>
        </div>

        <div className="home-card">
          <FaStar className="card-icon" />
          <h2>{avgScore}</h2>
          <p>Average ATS Score</p>
        </div>

        <div className="home-card">
          <FaBolt className="card-icon" />
          <h2>Active</h2>
          <p>ML Engine Status</p>
        </div>
      </div>

      {/* FEATURES */}
      <h2 className="section-title">Powerful AI Features</h2>

      <div className="home-features">
        <div className="feature-box">
          <FaRobot className="big-icon" />
          <h3>AI Resume Screening</h3>
          <p>
            Machine learning classifier categorizes applicants and predicts optimal career domains.
          </p>
        </div>

        <div className="feature-box">
          <FaFileAlt className="big-icon" />
          <h3>Skill Taxonomy Extraction</h3>
          <p>
            Extract technical competencies, frameworks, cloud tools, and database proficiencies.
          </p>
        </div>

        <div className="feature-box">
          <FaChartLine className="big-icon" />
          <h3>Analytics Dashboard</h3>
          <p>
            Visualize pipeline metrics, demand distributions, and candidate performance timelines.
          </p>
        </div>
      </div>

      {/* WORKFLOW */}
      <div className="workflow-box">
        <h2>How It Works ⚡</h2>

        <div className="workflow">
          <div>
            <FaUpload />
            <span>01</span>
            <p>Upload Resume</p>
          </div>

          <div>
            <FaBrain />
            <span>02</span>
            <p>AI Processing</p>
          </div>

          <div>
            <FaCheckCircle />
            <span>03</span>
            <p>Role Prediction</p>
          </div>

          <div>
            <FaChartLine />
            <span>04</span>
            <p>Generate Report</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;