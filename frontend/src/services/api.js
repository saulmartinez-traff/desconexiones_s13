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
  timeout: 60000, // 60 segundos para consultas de analytics
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

// ============================================================================
// API Functions - Registers
// ============================================================================

/**
 * Obtener lista de registros con paginación y filtros
 */
export const fetchRegisters = async (page = 1, filters = {}) => {
  const params = {
    page,
    page_size: 20,
    ...filters,
  };

  const response = await apiClient.get('/registers/', { params });
  return response.data;
};

/**
 * Obtener un registro por ID
 */
export const fetchRegisterById = async (id) => {
  const response = await apiClient.get(`/registers/${id}/`);
  return response.data;
};

/**
 * Actualizar un registro
 */
export const updateRegister = async (id, data) => {
  const response = await apiClient.patch(`/registers/${id}/`, data);
  return response.data;
};

/**
 * Crear un nuevo registro
 */
export const createRegister = async (data) => {
  const response = await apiClient.post('/registers/', data);
  return response.data;
};

// ============================================================================
// API Functions - Vehicles
// ============================================================================

/**
 * Obtener lista de vehículos
 */
export const fetchVehicles = async (page = 1, filters = {}) => {
  const params = {
    page,
    page_size: 20,
    ...filters,
  };

  const response = await apiClient.get('/vehicles/', { params });
  return response.data;
};

// ============================================================================
// API Functions - Auth
// ============================================================================

/**
 * Login
 */
export const login = async (username, password) => {
  const response = await apiClient.post('/auth/token/', {
    username,
    password,
  });

  if (response.data.access) {
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
  }

  return response.data;
};

/**
 * Logout
 */
export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

export default apiClient;
