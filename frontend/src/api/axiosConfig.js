import axios from 'axios';

const baseURL = process.env.NODE_ENV === 'production' 
  ? 'https://drdo-production.up.railway.app/api'
  : 'http://localhost:5000/api';

const axiosInstance = axios.create({
  baseURL,
  withCredentials: true,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Fix: Change 'instance' to 'axiosInstance' 
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default axiosInstance;