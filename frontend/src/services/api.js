import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('emotionlens.access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && err.config?.url !== '/auth/login') {
      localStorage.removeItem('emotionlens.access_token');
      window.dispatchEvent(new Event('emotionlens:unauthorized'));
    }
    const message =
      err.response?.data?.detail ||
      err.response?.data?.message ||
      err.message ||
      'Erro ao comunicar com o servidor';
    return Promise.reject({ ...err, friendlyMessage: message });
  }
);
