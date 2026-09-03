import { Routes, Route, Navigate } from "react-router-dom";

import Layout from "./components/layouts/Layout";

import Login from "./pages/Login";
import Register from "./pages/Register";

import Dashboard from "./pages/Dashboard";
import ResumeScreener from "./pages/ResumeScreener";
import JobMatrix from "./pages/JobMatrix";
import Logs from "./pages/Logs";

function App() {
  return (
    <Routes>

      {/* AUTH PAGES - NO SIDEBAR / NAVBAR */}
      <Route path="/" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* MAIN APPLICATION */}
      <Route
        path="/home"
        element={
          <Layout>
            <Dashboard />
          </Layout>
        }
      />

      <Route
        path="/dashboard"
        element={
          <Layout>
            <Dashboard />
          </Layout>
        }
      />

      <Route
        path="/resume-screener"
        element={
          <Layout>
            <ResumeScreener />
          </Layout>
        }
      />

      <Route
        path="/job-matrix"
        element={
          <Layout>
            <JobMatrix />
          </Layout>
        }
      />

      <Route
        path="/logs"
        element={
          <Layout>
            <Logs />
          </Layout>
        }
      />

      {/* FALLBACK */}
      <Route path="*" element={<Navigate to="/" replace />} />

    </Routes>
  );
}

export default App;