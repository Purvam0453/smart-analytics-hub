import { useState } from "react";
import api from "../services/api";
import "./UploadResume.css";

function UploadResume() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setErrorMessage("");
    setSuccessMessage("");
    setResult(null);

    if (!selectedFile) return;

    if (!selectedFile.name.toLowerCase().endsWith(".pdf")) {
      setErrorMessage("Please select a valid PDF file.");
      setFile(null);
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setErrorMessage("File size exceeds 10MB limit.");
      setFile(null);
      return;
    }

    setFile(selectedFile);
    setProgress(0);
  };

  const uploadResume = async () => {
    if (!file) {
      setErrorMessage("Please select a PDF file before analyzing.");
      return;
    }

    setErrorMessage("");
    setSuccessMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      const response = await api.post("/resume/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percent = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setProgress(percent);
          }
        },
      });

      setResult(response.data);
      setSuccessMessage("Resume analyzed successfully!");
    } catch (error) {
      console.error("Upload error:", error);
      const msg =
        error.response?.data?.detail ||
        "Upload failed. Please verify that the backend server is running.";
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
      link.download = `AI_Resume_Report_${result.predicted_role || "Analysis"}.pdf`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Report download error:", error);
      setErrorMessage("Failed to generate and download PDF report.");
    }
  };

  return (
    <div className="ai-upload-page">
      <div className="hero">
        <div className="intro">
          <h1>🤖 AI Resume Analyzer</h1>
          <p>
            Smart AI system that analyzes your resume, detects industry skills,
            calculates ATS match scoring, and recommends top career paths.
          </p>
          <div className="features">
            <div>⚡ 60+ Tech Skills Detection</div>
            <div>🎯 Real-time Role Classification</div>
            <div>📊 ATS Quality Scoring</div>
          </div>
        </div>

        <div className="upload-container">
          <h2>Upload Resume</h2>

          {errorMessage && (
            <div
              style={{
                backgroundColor: "#fee2e2",
                color: "#b91c1c",
                padding: "10px 14px",
                borderRadius: "8px",
                marginBottom: "15px",
                fontSize: "14px",
                fontWeight: "500",
              }}
            >
              ⚠️ {errorMessage}
            </div>
          )}

          {successMessage && (
            <div
              style={{
                backgroundColor: "#dcfce7",
                color: "#15803d",
                padding: "10px 14px",
                borderRadius: "8px",
                marginBottom: "15px",
                fontSize: "14px",
                fontWeight: "500",
              }}
            >
              ✅ {successMessage}
            </div>
          )}

          <div className="drop-box">
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
            />
            <div>
              <div className="upload-icon">📄</div>
              <h3>Choose PDF Resume</h3>
              <p>Click or drag to select your PDF resume (Max 10MB)</p>
            </div>
          </div>

          {file && (
            <div className="file-card">
              <div className="file-icon">📑</div>
              <div className="file-name">{file.name}</div>
            </div>
          )}

          {loading && (
            <div className="progress-box">
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <div className="progress-text">Analyzing {progress}%</div>
            </div>
          )}

          <button
            onClick={uploadResume}
            className="ai-btn"
            disabled={loading}
          >
            {loading ? "🤖 AI Analyzing..." : "Analyze Resume"}
          </button>
        </div>
      </div>

      {result && (
        <div className="result-dashboard">
          <h2>📊 AI Analysis Result</h2>

          <div className="result-grid">
            <div className="glass-card score-card">
              <div className="score-circle">{result.resume_score}%</div>
              <h3>Resume Score</h3>
            </div>

            <div className="glass-card">
              <h3>🎯 Predicted Role</h3>
              <h2>{result.predicted_role}</h2>
            </div>
          </div>

          <div className="glass-card">
            <h3>🛠 Skills Detected ({result.skills?.length || 0})</h3>
            <div className="skills">
              {result.skills && result.skills.length > 0 ? (
                result.skills.map((skill, index) => (
                  <span key={index}>{skill}</span>
                ))
              ) : (
                <p style={{ color: "#888", fontStyle: "italic" }}>
                  No standardized technical keywords detected.
                </p>
              )}
            </div>
          </div>

          <div className="glass-card">
            <h3>💼 Recommended Job Roles</h3>
            {result.recommendations && result.recommendations.length > 0 ? (
              result.recommendations.map((job, index) => (
                <div className="job-card" key={index}>
                  <strong>
                    #{job.rank} {job.job}
                  </strong>
                  <span>{job.match}% Match</span>
                </div>
              ))
            ) : (
              <p>No job matches found.</p>
            )}
          </div>

          <button className="download-btn" onClick={downloadReport}>
            📄 Download AI PDF Report
          </button>
        </div>
      )}
    </div>
  );
}

export default UploadResume;