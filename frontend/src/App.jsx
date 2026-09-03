import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/layouts/Layout";
import ResumeScreener from "./pages/ResumeScreener";
import Dashboard from "./pages/Dashboard";
import JobMatrix from "./pages/JobMatrix";
import Logs from "./pages/Logs";
import Login from "./pages/Login";       // <-- adjust filename if different
import Register from "./pages/Register"; // <-- adjust filename if different

// Simple guard: checks if a token exists in localStorage after login.
// Adjust the key name ("token") to whatever your login page actually saves.
function ProtectedRoute({ children }) {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/login" replace />;
}

function App() {
  return (
    <Layout>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <ResumeScreener />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/job-matrix"
          element={
            <ProtectedRoute>
              <JobMatrix />
            </ProtectedRoute>
          }
        />
        <Route
          path="/logs"
          element={
            <ProtectedRoute>
              <Logs />
            </ProtectedRoute>
          }
        />

        {/* Fallback route */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Layout>
  );
}

export default App;
