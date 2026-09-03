import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/layouts/Layout";
import ResumeScreener from "./pages/ResumeScreener";
import Dashboard from "./pages/Dashboard";
import JobMatrix from "./pages/JobMatrix";
import Logs from "./pages/Logs";

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<ResumeScreener />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/job-matrix" element={<JobMatrix />} />
        <Route path="/logs" element={<Logs />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}

export default App;