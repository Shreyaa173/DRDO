import axios from "axios";

const axiosInstance = axios.create({
    baseURL: process.env.REACT_APP_BACKEND_URL, // ✅ from .env
  withCredentials: true 
});

axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem("authToken");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

