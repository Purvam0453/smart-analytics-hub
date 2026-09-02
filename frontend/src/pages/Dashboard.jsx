import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area
} from "recharts";
import { 
  FileText, 
  Target, 
  Award, 
  Cpu, 
  TrendingUp, 
  Users, 
  Layers, 
  RefreshCw,
  Zap
} from "lucide-react";
import api from "../services/api";
import "./Dashboard.css";

const PALETTE = [
  "#6366f1", "#10b981", "#06b6d4", "#f59e0b", 
  "#ec4899", "#8b5cf6", "#14b8a6", "#f97316"
];

function Dashboard() {
  const [data, setData] = useState(null);
  const [loginData, setLoginData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [statsRes, loginRes] = await Promise.all([
        api.get("/dashboard-stats"),
        api.get("/login-stats")
      ]);
      setData(statsRes.data);
      setLoginData(loginRes.data?.login_trend || []);
    } catch (err) {
      console.error("Dashboard data load error:", err);
      setError("Unable to connect to backend server. Make sure FastAPI is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="dashboard-loading-state glass-panel">
        <RefreshCw size={28} className="animate-spin text-indigo" />
        <h3>Loading Real-time Analytics...</h3>
        <p>Aggregating resumes, skill frequency, and role predictions</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error-state glass-panel">
        <h3>Backend Connection Alert</h3>
        <p>{error}</p>
        <button onClick={loadData} className="btn-primary">
          <RefreshCw size={16} />
          <span>Retry Connection</span>
        </button>
      </div>
    );
  }

  const roleData = Object.keys(data?.roles || {}).map((role) => ({
    name: role,
    value: data.roles[role]
  }));

  const skillData = Object.keys(data?.skills || {})
    .map((skill) => ({
      name: skill,
      count: data.skills[skill]
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);

  const topRole = roleData.sort((a, b) => b.value - a.value)[0]?.name || "General Profile";

  return (
    <div className="dashboard-page">
      {/* Dashboard Header */}
      <div className="dashboard-header-row">
        <div>
          <span className="badge badge-indigo">
            <Zap size={13} /> Live Intelligence
          </span>
          <h1 className="dashboard-title">Talent Intelligence & Analytics</h1>
          <p className="dashboard-subtitle">
            Real-time pipeline metrics, skill demand distributions, and AI role classification insights.
          </p>
        </div>
        <button onClick={loadData} className="btn-secondary">
          <RefreshCw size={15} />
          <span>Refresh Data</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="glass-panel kpi-card">
          <div className="kpi-header">
            <span>Total Resumes Screened</span>
            <div className="kpi-icon-badge bg-indigo-soft">
              <FileText size={18} className="text-indigo" />
            </div>
          </div>
          <div className="kpi-value">{data?.total_resumes || 0}</div>
          <div className="kpi-trend trend-up">
            <TrendingUp size={13} />
            <span>Active Candidate Pipeline</span>
          </div>
        </div>

        <div className="glass-panel kpi-card">
          <div className="kpi-header">
            <span>Average ATS Score</span>
            <div className="kpi-icon-badge bg-emerald-soft">
              <Award size={18} className="text-emerald" />
            </div>
          </div>
          <div className="kpi-value">{data?.average_score || 0}%</div>
          <div className="kpi-trend trend-neutral">
            <span>Composite Benchmarked Score</span>
          </div>
        </div>

        <div className="glass-panel kpi-card">
          <div className="kpi-header">
            <span>Dominant Role Category</span>
            <div className="kpi-icon-badge bg-cyan-soft">
              <Target size={18} className="text-cyan" />
            </div>
          </div>
          <div className="kpi-value kpi-text-value">{topRole}</div>
          <div className="kpi-trend trend-up">
            <span>Top Predicted Domain</span>
          </div>
        </div>

        <div className="glass-panel kpi-card">
          <div className="kpi-header">
            <span>Unique Skills Indexed</span>
            <div className="kpi-icon-badge bg-purple-soft">
              <Cpu size={18} className="text-purple" />
            </div>
          </div>
          <div className="kpi-value">{Object.keys(data?.skills || {}).length}</div>
          <div className="kpi-trend trend-up">
            <span>Across 60+ Tech Taxonomies</span>
          </div>
        </div>
      </div>

      {/* Charts Section Grid */}
      <div className="charts-main-grid">
        {/* Top In-Demand Skills Chart */}
        <div className="glass-panel chart-container-card">
          <div className="chart-card-header">
            <div>
              <h3 className="chart-title">Top In-Demand Technical Skills</h3>
              <p className="chart-desc">Frequency of detected technical competencies across candidates</p>
            </div>
          </div>
          <div className="chart-wrapper">
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
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} />
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
          </div>
        </div>

        {/* Role Distribution Pie Chart */}
        <div className="glass-panel chart-container-card">
          <div className="chart-card-header">
            <div>
              <h3 className="chart-title">Role Prediction Distribution</h3>
              <p className="chart-desc">Breakdown of classified applicant career categories</p>
            </div>
          </div>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={roleData.length > 0 ? roleData : [{ name: "General", value: 1 }]}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={65}
                  outerRadius={105}
                  paddingAngle={4}
                >
                  {(roleData.length > 0 ? roleData : [{ name: "General", value: 1 }]).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PALETTE[index % PALETTE.length]} />
                  ))}
                </Pie>
                <Tooltip 
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
          </div>
        </div>
      </div>

      {/* Activity Timeline Chart */}
      <div className="glass-panel chart-container-card">
        <div className="chart-card-header">
          <div>
            <h3 className="chart-title">Screening Activity & System Traffic</h3>
            <p className="chart-desc">Candidate screening submissions and system logins timeline</p>
          </div>
        </div>
        <div className="chart-wrapper">
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={loginData.length > 0 ? loginData : [{ date: "Today", count: 1 }]}>
              <defs>
                <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="date" stroke="#64748b" fontSize={12} tickLine={false} />
              <YAxis stroke="#64748b" fontSize={12} tickLine={false} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: "#0f172a", 
                  borderColor: "rgba(255,255,255,0.1)", 
                  borderRadius: "10px",
                  color: "#f8fafc"
                }} 
              />
              <Area type="monotone" dataKey="count" stroke="#06b6d4" strokeWidth={3} fillOpacity={1} fill="url(#colorCount)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;