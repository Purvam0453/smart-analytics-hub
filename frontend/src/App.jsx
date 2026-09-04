import { Routes, Route, Navigate } from "react-router-dom";

import Layout from "./components/layouts/Layout";

import Login from "./pages/Login";
import Register from "./pages/Register";

import ResumeScreener from "./pages/ResumeScreener";
import Dashboard from "./pages/Dashboard";
import JobMatrix from "./pages/JobMatrix";
import Logs from "./pages/Logs";
import Profile from "./pages/Profile";

function ProtectedRoute({ children }) {
  const token = localStorage.getItem("token");

  if (!token) {
    return <Navigate to="/" replace />;
  }

  return children;
}

function App() {
  return (
    <Routes>

      {/* LOGIN */}
      <Route path="/" element={<Login />} />

      {/* REGISTER */}
      <Route path="/register" element={<Register />} />

      {/* MAIN WEBSITE - EXISTING UI */}
      <Route
        path="/home"
        element={
          <ProtectedRoute>
            <Layout>
              <ResumeScreener />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Layout>
              <Dashboard />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/resume-screener"
        element={
          <ProtectedRoute>
            <Layout>
              <ResumeScreener />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/job-matrix"
        element={
          <ProtectedRoute>
            <Layout>
              <JobMatrix />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/logs"
        element={
          <ProtectedRoute>
            <Layout>
              <Logs />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <Layout>
              <Profile />
            </Layout>
          </ProtectedRoute>
        }
      />

      {/* INVALID URL */}
      <Route path="*" element={<Navigate to="/" replace />} />

    </Routes>
  );
}

export default App;