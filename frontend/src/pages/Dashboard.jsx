import { useEffect, useState, useCallback } from "react";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";
import {
  FileText,
  Target,
  Award,
  Cpu,
  TrendingUp,
  Users,
  RefreshCw,
  Zap,
  UploadCloud,
  Clock,
  CheckCircle2,
  AlertCircle
} from "lucide-react";
import api from "../services/api";
import "./Dashboard.css";

const PALETTE = [
  "#6366f1", "#10b981", "#06b6d4", "#f59e0b",
  "#ec4899", "#8b5cf6", "#14b8a6", "#f97316"
];

function Dashboard() {
  const [current, setCurrent] = useState(null);
  const [currentId, setCurrentId] = useState(
    () => localStorage.getItem("currentResumeId") || null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notFound, setNotFound] = useState(false);

  const loadCurrent = useCallback(async () => {
    const id = localStorage.getItem("currentResumeId");
    setCurrentId(id);
    setNotFound(false);
    if (!id) {
      setCurrent(null);
      setLoading(false);
      return;
    }
    try {
      setLoading(true);
      setError(null);
      const resp = await api.get(`/resume/analysis/${id}`);
      setCurrent(resp.data);
    } catch (err) {
      if (err.response?.status === 404) {
        // Selected resume no longer exists — clear reference and show empty state
        localStorage.removeItem("currentResumeId");
        setCurrentId(null);
        setCurrent(null);
        setNotFound(true);
      } else {
        console.error("Dashboard current-resume load error:", err);
        setError("Unable to connect to backend server. Make sure FastAPI is running on port 8000.");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCurrent();
  }, [loadCurrent]);

  if (loading) {
    return (
      <div className="dashboard-loading-state glass-panel">
        <RefreshCw size={28} className="animate-spin text-indigo" />
        <h3>Loading Current Resume Analysis...</h3>
        <p>Fetching the selected candidate's skills, role, and predictions</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error-state glass-panel">
        <h3>Backend Connection Alert</h3>
        <p>{error}</p>
        <button onClick={loadCurrent} className="btn-primary">
          <RefreshCw size={16} />
          <span>Retry Connection</span>
        </button>
      </div>
    );
  }

  if (!current) {
    const upload = () => {
      window.location.href = "/resume-screener";
    };
    return (
      <div className="dashboard-page">
        <div className="dashboard-header-row">
          <div>
            <span className="badge badge-indigo">
              <Zap size={13} /> Current Candidate
            </span>
            <h1 className="dashboard-title">Talent Intelligence & Analytics</h1>
            <p className="dashboard-subtitle">
              Upload a resume to see this candidate's skills, role prediction, and screening analytics.
            </p>
          </div>
        </div>

        <div className="glass-panel dashboard-empty-state">
          <div className="empty-state-icon">
            <UploadCloud size={40} />
          </div>
          <h3>{notFound ? "Selected resume is no longer available" : "No candidate selected yet"}</h3>
          <p>
            Upload and analyze a resume to populate the current-candidate dashboard.
            Charts will reflect only that uploaded resume.
          </p>
          <button onClick={upload} className="btn-primary">
            <UploadCloud size={16} />
            <span>Upload a Resume</span>
          </button>
        </div>
      </div>
    );
  }

  const screening = current.screening_information || {};

  // Chart 1: Top Technical Skills — from the CURRENT resume (each counted once)
  const skillData = Object.keys(current.skill_counts || {})
    .map((skill) => ({
      name: skill,
      count: current.skill_counts[skill]
    }))
    .sort((a, b) => b.count - a.count);

  // Chart 2: Role Prediction Distribution — the model's actual probability
  // distribution for the CURRENT resume (values from role_probabilities).
  let roleData = Object.keys(current.role_probabilities || {})
    .filter((r) => (current.role_probabilities[r] || 0) > 0)
    .map((role) => ({
      name: role,
      value: current.role_probabilities[role]
    }))
    .sort((a, b) => b.value - a.value);

  // If the model did not provide probabilities, fall back to the predicted
  // role representing this single candidate (100% / 1 candidate), rather than
  // inventing percentages.
  if (roleData.length === 0) {
    roleData = [
      { name: current.predicted_role, value: 100 }
    ];
  }

  const topRole = current.predicted_role;
  const numSkills = (current.skills || []).length;

  const statusBadge = (status) =>
    status === "Completed" ? (
      <span className="badge badge-emerald"><CheckCircle2 size={12} /> {status}</span>
    ) : (
      <span className="badge badge-amber"><AlertCircle size={12} /> {status || "Pending"}</span>
    );

  return (
    <div className="dashboard-page">
      {/* Dashboard Header */}
      <div className="dashboard-header-row">
        <div>
          <span className="badge badge-indigo">
            <Zap size={13} /> Current Candidate Analysis
          </span>
          <h1 className="dashboard-title">Talent Intelligence & Analytics</h1>
          <p className="dashboard-subtitle">
            Analytics for the selected/uploaded resume: <strong>{current.filename}</strong>
          </p>
        </div>
        <button onClick={loadCurrent} className="btn-secondary">
          <RefreshCw size={15} />
          <span>Refresh Data</span>
        </button>
      </div>

      {/* KPI Cards — current candidate only */}
      <div className="kpi-grid">
        <div className="glass-panel kpi-card">
          <div className="kpi-header">
            <span>Predicted Role</span>
            <div className="kpi-icon-badge bg-indigo-soft">
              <Target size={18} className="text-indigo" />
            </div>
          </div>
          <div className="kpi-value kpi-text-value">{topRole}</div>
          <div className="kpi-trend trend-up">
            <TrendingUp size={13} />
            <span>{current.filename}</span>
          </div>
        </div>

        <div className="glass-panel kpi-card">
          <div className="kpi-header">
            <span>Model Confidence</span>
            <div className="kpi-icon-badge bg-cyan-soft">
              <Zap size={18} className="text-cyan" />
            </div>
          </div>
          <div className="kpi-value">{current.confidence}%</div>
          <div className="kpi-trend trend-neutral">
            <span>This resume's top probability</span>
          </div>
        </div>

        <div className="glass-panel kpi-card">
          <div className="kpi-header">
            <span>Resume ATS Score</span>
            <div className="kpi-icon-badge bg-emerald-soft">
              <Award size={18} className="text-emerald" />
            </div>
          </div>
          <div className="kpi-value">{current.resume_score}%</div>
          <div className="kpi-trend trend-up">
            <span>Composite benchmarked score</span>
          </div>
        </div>

        <div className="glass-panel kpi-card">
          <div className="kpi-header">
            <span>Skills Detected</span>
            <div className="kpi-icon-badge bg-purple-soft">
              <Cpu size={18} className="text-purple" />
            </div>
          </div>
          <div className="kpi-value">{numSkills}</div>
          <div className="kpi-trend trend-up">
            <span>Extracted from this resume</span>
          </div>
        </div>
      </div>

      {/* Charts Section Grid */}
      <div className="charts-main-grid">
        {/* Top Skills Chart — current resume */}
        <div className="glass-panel chart-container-card">
          <div className="chart-card-header">
            <div>
              <h3 className="chart-title">Top Technical Skills</h3>
              <p className="chart-desc">Skills detected from this resume (each counted once)</p>
            </div>
          </div>
          <div className="chart-wrapper">
            {skillData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={skillData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <XAxis
                    dataKey="name"
                    stroke="#64748b"
                    fontSize={12}
                    tickLine={false}
                    angle={-25}
                    textAnchor="end"
                  />
                  <YAxis stroke="#64748b" fontSize={12} tickLine={false} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      borderColor: "rgba(255,255,255,0.1)",
                      borderRadius: "10px",
                      color: "#f8fafc"
                    }}
                  />
                  <Bar dataKey="count" fill="#6366f1" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="chart-empty-msg">
                No standardized technical skills matched in this document.
              </div>
            )}
          </div>
        </div>

        {/* Role Distribution Pie Chart — this resume's model probabilities */}
        <div className="glass-panel chart-container-card">
          <div className="chart-card-header">
            <div>
              <h3 className="chart-title">Role Prediction Distribution</h3>
              <p className="chart-desc">Model probability distribution for this resume</p>
            </div>
          </div>
          <div className="chart-wrapper">
            {roleData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={roleData}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={65}
                    outerRadius={105}
                    paddingAngle={4}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {roleData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={PALETTE[index % PALETTE.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value) => [`${value}%`, "Probability"]}
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      borderColor: "rgba(255,255,255,0.1)",
                      borderRadius: "10px",
                      color: "#f8fafc"
                    }}
                  />
                  <Legend
                    verticalAlign="bottom"
                    height={36}
                    formatter={(value) => <span style={{ color: "#94a3b8", fontSize: "12px" }}>{value}</span>}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="chart-empty-msg">
                No probability data available for this resume.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Screening Activity / Current Resume Info */}
      <div className="glass-panel chart-container-card">
        <div className="chart-card-header">
          <div>
            <h3 className="chart-title">Current Resume Screening</h3>
            <p className="chart-desc">Processing and prediction status for this resume</p>
          </div>
        </div>
        <div className="screening-grid">
          <div className="screening-item">
            <Clock size={16} className="text-cyan" />
            <div>
              <span className="screening-label">Upload Time</span>
              <span className="screening-value">{screening.uploaded_at || "N/A"}</span>
            </div>
          </div>
          <div className="screening-item">
            <FileText size={16} className="text-indigo" />
            <div>
              <span className="screening-label">Parsing Status</span>
              {statusBadge(screening.parsing_status)}
            </div>
          </div>
          <div className="screening-item">
            <Cpu size={16} className="text-purple" />
            <div>
              <span className="screening-label">Analysis Status</span>
              {statusBadge(screening.analysis_status)}
            </div>
          </div>
          <div className="screening-item">
            <Target size={16} className="text-emerald" />
            <div>
              <span className="screening-label">Prediction Status</span>
              {statusBadge(screening.prediction_status)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
