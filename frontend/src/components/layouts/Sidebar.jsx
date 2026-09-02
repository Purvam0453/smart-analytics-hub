import { NavLink } from "react-router-dom";
import { 
  FileScan, 
  LayoutDashboard, 
  Briefcase, 
  History, 
  Sparkles,
  Zap,
  Activity,
  Layers
} from "lucide-react";
import "./Sidebar.css";

function Sidebar() {
  const navItems = [
    {
      to: "/",
      label: "AI Resume Screener",
      icon: FileScan,
      badge: "Core AI",
      end: true
    },
    {
      to: "/dashboard",
      label: "Analytics Hub",
      icon: LayoutDashboard,
      badge: "Live"
    },
    {
      to: "/job-matrix",
      label: "Role Benchmarks",
      icon: Briefcase,
    },
    {
      to: "/logs",
      label: "Screening Logs",
      icon: History,
    }
  ];

  return (
    <aside className="app-sidebar">
      {/* Brand Header */}
      <div className="sidebar-brand">
        <div className="brand-icon-wrapper">
          <Sparkles className="brand-icon" size={22} />
        </div>
        <div className="brand-text-container">
          <span className="brand-title">Smart Analytics</span>
          <span className="brand-subtitle">AI Talent Intelligence</span>
        </div>
      </div>

      {/* Navigation */}
      <div className="sidebar-section-label">PLATFORM</div>
      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `nav-link ${isActive ? "nav-link-active" : ""}`
              }
            >
              <div className="nav-link-content">
                <Icon size={19} className="nav-icon" />
                <span className="nav-label">{item.label}</span>
              </div>
              {item.badge && (
                <span className="nav-pill-badge">{item.badge}</span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Quick AI Info Card */}
      <div className="sidebar-footer-card">
        <div className="footer-card-header">
          <Zap size={16} className="text-amber" />
          <span>ML Engine Status</span>
        </div>
        <p className="footer-card-desc">
          NLP Classifier + TF-IDF Vectorizer Active
        </p>
        <div className="status-indicator">
          <span className="status-dot"></span>
          <span>Online & Ready</span>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;