import api from "./api";

export const loginUser = async (email, password) => {
  const response = await api.post("/auth/login", { email, password });
  if (response.data && response.data.access_token) {
    localStorage.setItem("token", response.data.access_token);
    localStorage.setItem("username", response.data.username || email);
  }
  return response.data;
};

export const registerUser = async (username, email, password) => {
  const response = await api.post("/auth/register", { username, email, password });
  return response.data;
};

export const logoutUser = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("username");
  window.location.href = "/";
};

export const getToken = () => {
  return localStorage.getItem("token");
};

export const getUsername = () => {
  return localStorage.getItem("username") || "Guest";
};

export const isAuthenticated = () => {
  return !!localStorage.getItem("token");
};
