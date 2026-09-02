import { useState, useRef } from "react";
import confetti from "canvas-confetti";
import { 
  UploadCloud, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  Sparkles, 
  Download, 
  TrendingUp, 
  Award, 
  Target, 
  Cpu, 
  Layers, 
  X,
  ArrowRight,
  ShieldCheck,
  Briefcase
} from "lucide-react";
import api from "../services/api";
import "./ResumeScreener.css";

function ResumeScreener() {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusStep, setStatusStep] = useState("");
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true);
    } else if (e.type === "dragleave") {
      setIsDragging(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const processSelectedFile = (selectedFile) => {
    setErrorMessage("");
    setResult(null);

    if (!selectedFile.name.toLowerCase().endsWith(".pdf")) {
      setErrorMessage("Please upload a PDF document (.pdf format only).");
      setFile(null);
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setErrorMessage("File size exceeds the 10MB limit. Please upload a smaller PDF.");
      setFile(null);
      return;
    }

    setFile(selectedFile);
  };

  const triggerConfetti = () => {
    confetti({
      particleCount: 80,
      spread: 70,
      origin: { y: 0.6 },
      colors: ["#6366f1", "#10b981", "#06b6d4", "#f59e0b"]
    });
  };

  const analyzeResume = async () => {
    if (!file) {
      setErrorMessage("Please select or drop a PDF resume first.");
      return;
    }

    setErrorMessage("");
    setLoading(true);
    setProgress(15);
    setStatusStep("Extracting text from PDF document...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const stepTimer1 = setTimeout(() => {
        setProgress(50);
        setStatusStep("Running ML Classifier & TF-IDF Vectorization...");
      }, 400);

      const stepTimer2 = setTimeout(() => {
        setProgress(85);
        setStatusStep("Matching skills against industry role benchmarks...");
      }, 800);

      const response = await api.post("/resume/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);

      setProgress(100);
      setStatusStep("Analysis Complete!");
      setResult(response.data);

      if (response.data?.resume_score >= 60) {
        triggerConfetti();
      }
    } catch (error) {
      console.error("Resume analysis error:", error);
      const msg =
        error.response?.data?.detail ||
        (error.code === "ERR_NETWORK"
          ? "Cannot reach FastAPI backend server. Please verify it is running on port 8000."
          : "Resume analysis failed. Please check the uploaded file and try again.");
      setErrorMessage(msg);
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async () => {
    if (!result) return;
    try {
      const response = await api.post("/resume/report", result, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.download = `AI_Resume_Report_${result.predicted_role || "Candidate"}.pdf`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Report download error:", error);
      setErrorMessage("Failed to export PDF report. Please try again.");
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return "score-high";
    if (score >= 60) return "score-mid";
    return "score-low";
  };

  const getScoreTag = (score) => {
    if (score >= 80) return "Tier 1 Top Match";
    if (score >= 60) return "Competitive Fit";
    return "Needs Optimization";
  };

  return (
    <div className="screener-page">
      {/* Hero Banner */}
      <div className="screener-hero">
        <div className="hero-pill">
          <Sparkles size={14} className="text-cyan" />
          <span>Enterprise AI Resume Screening Platform</span>
        </div>
        <h1 className="hero-headline">
          Screen Resumes & Predict Career Roles with <span className="gradient-text">Machine Learning</span>
        </h1>
        <p className="hero-subtext">
          Upload candidate PDF resumes for automated entity parsing, 60+ technical skill taxonomy detection, ATS score benchmarking, and tailored job recommendations.
        </p>
      </div>

      {/* Upload Box Section */}
      <div className="screener-upload-section">
        {errorMessage && (
          <div className="error-alert">
            <AlertCircle size={18} />
            <span>{errorMessage}</span>
            <button onClick={() => setErrorMessage("")} className="alert-close-btn">
              <X size={15} />
            </button>
          </div>
        )}

        <div 
          className={`dropzone-card ${isDragging ? "dropzone-active" : ""}`}
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input 
            ref={fileInputRef}
            type="file" 
            accept=".pdf" 
            style={{ display: "none" }}
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                processSelectedFile(e.target.files[0]);
              }
            }}
          />
          <div className="dropzone-icon-circle">
            <UploadCloud size={32} className="dropzone-icon" />
          </div>
          <h3 className="dropzone-title">Click to browse or drag & drop resume</h3>
          <p className="dropzone-hint">Supports PDF formats (Max 10MB) • Zero registration required</p>

          <div className="dropzone-pills">
            <span className="badge badge-indigo">
              <Cpu size={12} /> TF-IDF NLP Model
            </span>
            <span className="badge badge-cyan">
              <Layers size={12} /> 60+ Skill Taxonomy
            </span>
            <span className="badge badge-emerald">
              <ShieldCheck size={12} /> Secure & Private
            </span>
          </div>
        </div>

        {file && (
          <div className="file-selection-preview glass-panel">
            <div className="file-info-group">
              <div className="file-icon-badge">
                <FileText size={22} />
              </div>
              <div>
                <div className="file-selected-name">{file.name}</div>
                <div className="file-selected-meta">
                  {(file.size / 1024).toFixed(1)} KB • PDF Document
                </div>
              </div>
            </div>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                setFile(null);
                setResult(null);
              }}
              className="file-remove-btn"
              title="Remove File"
            >
              <X size={16} />
            </button>
          </div>
        )}

        {loading && (
          <div className="analysis-progress-card glass-panel">
            <div className="progress-header">
              <span className="progress-step-text">{statusStep}</span>
              <span className="progress-percent">{progress}%</span>
            </div>
            <div className="progress-track">
              <div className="progress-indicator-bar" style={{ width: `${progress}%` }}></div>
            </div>
          </div>
        )}

        <div className="action-row">
          <button 
            onClick={analyzeResume} 
            className="btn-primary analyze-cta-btn"
            disabled={!file || loading}
          >
            {loading ? (
              <>
                <Cpu size={18} className="animate-spin" />
                <span>Running AI Intelligence...</span>
              </>
            ) : (
              <>
                <Sparkles size={18} />
                <span>Analyze Resume Now</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Analysis Results View */}
      {result && (
        <div className="screener-results-section animate-fade-in">
          <div className="results-header-bar">
            <div>
              <span className="badge badge-emerald">
                <CheckCircle size={13} /> Evaluation Ready
              </span>
              <h2 className="results-title">AI Candidate Intelligence Card</h2>
            </div>
            <button onClick={downloadReport} className="btn-secondary export-report-btn">
              <Download size={16} />
              <span>Export PDF Evaluation Report</span>
            </button>
          </div>

          {/* Metric Cards Grid */}
          <div className="results-metric-grid">
            {/* ATS Score Card */}
            <div className="glass-panel result-score-card">
              <div className="metric-header">
                <Award size={18} className="text-indigo" />
                <span>Resume ATS Score</span>
              </div>
              <div className={`score-display-radial ${getScoreColor(result.resume_score)}`}>
                <span className="score-number">{result.resume_score}%</span>
                <span className="score-sub">{getScoreTag(result.resume_score)}</span>
              </div>
              <p className="metric-footnote">Calculated via TF-IDF confidence & skill density algorithms</p>
            </div>

            {/* Predicted Role Card */}
            <div className="glass-panel result-role-card">
              <div className="metric-header">
                <Target size={18} className="text-cyan" />
                <span>Predicted Primary Role</span>
              </div>
              <div className="role-highlight">
                <h3 className="role-name">{result.predicted_role}</h3>
                <span className="badge badge-cyan">Classification: Optimal</span>
              </div>
              <p className="metric-footnote">Multiclass logistic model classified candidate profile</p>
            </div>
          </div>

          {/* Extracted Skills Section */}
          <div className="glass-panel skills-breakdown-card">
            <div className="card-section-title">
              <Cpu size={18} className="text-indigo" />
              <span>Extracted Technical Skills ({result.skills?.length || 0})</span>
            </div>
            <div className="skills-tag-cloud">
              {result.skills && result.skills.length > 0 ? (
                result.skills.map((skill, index) => (
                  <span key={index} className="skill-pill">
                    {skill}
                  </span>
                ))
              ) : (
                <div className="no-skills-msg">
                  No standardized technical skills matched in the document.
                </div>
              )}
            </div>
          </div>

          {/* Job Recommendations Section */}
          <div className="glass-panel recommendations-card">
            <div className="card-section-title">
              <Briefcase size={18} className="text-indigo" />
              <span>Role Compatibility & Benchmarks</span>
            </div>
            <div className="recommendations-grid">
              {result.recommendations && result.recommendations.length > 0 ? (
                result.recommendations.map((job, idx) => (
                  <div key={idx} className="rec-job-item">
                    <div className="rec-job-header">
                      <div className="rec-job-title-group">
                        <span className="rec-job-rank">#{job.rank}</span>
                        <span className="rec-job-name">{job.job}</span>
                      </div>
                      <span className={`rec-match-pill ${job.match >= 50 ? "match-high" : "match-normal"}`}>
                        {job.match}% Match
                      </span>
                    </div>
                    <div className="rec-progress-track">
                      <div 
                        className="rec-progress-fill" 
                        style={{ width: `${job.match}%` }}
                      ></div>
                    </div>
                    {job.missing_skills && job.missing_skills.length > 0 && (
                      <div className="missing-skills-box">
                        <span className="missing-label">Skill gaps:</span>
                        <span className="missing-list">{job.missing_skills.slice(0, 4).join(", ")}</span>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <p>No job profiles matched.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ResumeScreener;
