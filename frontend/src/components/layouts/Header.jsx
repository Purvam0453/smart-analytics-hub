import { useState, useEffect } from "react";
import { 
  Sparkles, 
  Activity, 
  CheckCircle2, 
  RefreshCw,
  SlidersHorizontal,
  ExternalLink
} from "lucide-react";
import api from "../../services/api";
import "./Header.css";

function Header() {
  const [serverOnline, setServerOnline] = useState(true);
  const [checking, setChecking] = useState(false);

  const checkHealth = async () => {
    try {
      setChecking(true);
      await api.get("/");
      setServerOnline(true);
    } catch {
      setServerOnline(false);
    } finally {
      setChecking(false);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="app-header">
      <div className="header-left">
        <div className="header-tag">
          <Sparkles size={14} className="text-indigo" />
          <span>Next-Gen ATS & Career AI</span>
        </div>
      </div>

      <div className="header-right">
        {/* Backend Connectivity Status */}
        <div className={`health-pill ${serverOnline ? "health-online" : "health-offline"}`}>
          <span className="health-dot"></span>
          <span>{serverOnline ? "Backend Connected (FastAPI)" : "Backend Offline"}</span>
          <button 
            onClick={checkHealth} 
            className="refresh-btn"
            title="Refresh Connection"
            disabled={checking}
          >
            <RefreshCw size={12} className={checking ? "animate-spin" : ""} />
          </button>
        </div>

        {/* Quick Action Button */}
        <a 
          href="https://github.com/Purvam0453/smart-analytics-hub" 
          target="_blank" 
          rel="noopener noreferrer"
          className="github-btn"
        >
          <span>GitHub</span>
          <ExternalLink size={14} />
        </a>
      </div>
    </header>
  );
}

export default Header;
