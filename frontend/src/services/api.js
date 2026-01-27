/**
 * API Service - Cliente HTTP configurado con Axios
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Crear instancia de Axios
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

/**
 * Interceptor de request - Agregar token JWT si existe
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Interceptor de response - Manejar errores globales
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Si token expirado, intentar refresh
    if (error.response?.status === 401) {
      // TODO: Implementar refresh token logic
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }

    // Log de errores en desarrollo
    if (import.meta.env.DEV) {
      console.error('API Error:', error.response?.data || error.message);
    }

    return Promise.reject(error);
  }
);

export default apiClient;
