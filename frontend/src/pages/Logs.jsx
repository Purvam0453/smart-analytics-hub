import { useState, useEffect } from "react";
import { History, Search, Download, RefreshCw, FileText, User, Calendar, CheckCircle2 } from "lucide-react";
import api from "../services/api";
import "./Logs.css";

function Logs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterAction, setFilterAction] = useState("All");

  const loadLogs = async () => {
    try {
      setLoading(true);
      const res = await api.get("/logs/all");
      if (res.data?.logs) {
        setLogs(res.data.logs);
      }
    } catch (err) {
      console.warn("Could not load backend logs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, []);

  const filteredLogs = logs.filter((log) => {
    const matchSearch =
      (log.username || "").toLowerCase().includes(search.toLowerCase()) ||
      (log.action || "").toLowerCase().includes(search.toLowerCase()) ||
      (log.details || "").toLowerCase().includes(search.toLowerCase());

    const matchFilter =
      filterAction === "All" ||
      (log.action || "").toLowerCase().includes(filterAction.toLowerCase());

    return matchSearch && matchFilter;
  });

  const exportCSV = () => {
    if (logs.length === 0) return;

    const headers = ["Timestamp", "User", "Action", "Details"];
    const rows = logs.map((l) => [
      `"${l.date_time || ""}"`,
      `"${l.username || "Guest"}"`,
      `"${l.action || ""}"`,
      `"${(l.details || "").replace(/"/g, '""')}"`
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `Screening_Audit_Logs_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="logs-page">
      <div className="logs-header-row">
        <div>
          <span className="badge badge-indigo">System Audit Trail</span>
          <h1 className="logs-title">Screening Activity & Event Logs</h1>
          <p className="logs-subtitle">
            Chronological audit records of all resume uploads, AI predictions, and document analysis events.
          </p>
        </div>
        <div className="logs-actions">
          <button onClick={loadLogs} className="btn-secondary">
            <RefreshCw size={15} />
            <span>Refresh</span>
          </button>
          <button onClick={exportCSV} className="btn-primary" disabled={logs.length === 0}>
            <Download size={15} />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="logs-controls glass-panel">
        <div className="search-input-group">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            placeholder="Search by username, action, or filename..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="matrix-search-field"
          />
        </div>

        <div className="filter-buttons-row">
          {["All", "Upload", "Prediction"].map((f) => (
            <button
              key={f}
              onClick={() => setFilterAction(f)}
              className={`cat-tab-btn ${filterAction === f ? "cat-tab-active" : ""}`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Logs Table */}
      <div className="glass-panel table-container">
        {loading ? (
          <div className="table-loading">
            <RefreshCw size={24} className="animate-spin text-indigo" />
            <span>Loading Activity Logs...</span>
          </div>
        ) : filteredLogs.length > 0 ? (
          <table className="modern-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Candidate / User</th>
                <th>Action Type</th>
                <th>Details & Metadata</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.map((log, index) => (
                <tr key={index}>
                  <td className="cell-time">
                    <div className="cell-flex">
                      <Calendar size={14} className="text-muted" />
                      <span>{log.date_time || "Recent"}</span>
                    </div>
                  </td>
                  <td className="cell-user">
                    <div className="cell-flex">
                      <User size={14} className="text-indigo" />
                      <span>{log.username || "Guest User"}</span>
                    </div>
                  </td>
                  <td>
                    <span
                      className={`badge ${
                        (log.action || "").includes("Upload")
                          ? "badge-cyan"
                          : "badge-emerald"
                      }`}
                    >
                      {log.action || "Activity"}
                    </span>
                  </td>
                  <td className="cell-details">{log.details || "-"}</td>
                  <td>
                    <span className="status-badge-completed">
                      <CheckCircle2 size={13} /> Processed
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="table-empty-state">
            <FileText size={36} className="text-muted" />
            <h3>No Activity Records Found</h3>
            <p>Upload a resume in the AI Resume Screener to generate screening activity logs.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Logs;