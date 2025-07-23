import axios from "axios";

const axiosInstance = axios.create({
    baseURL: import.meta.env.VITE_BACKEND_URL || "http://localhost:5000/api", // ✅ Vite env vars + fallback
  withCredentials: true 
});

axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem("authToken");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for better error handling
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error);
    if (error.response?.status === 401) {
      // Clear invalid token
      localStorage.removeItem("authToken");
      localStorage.removeItem("currentUser");
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;

