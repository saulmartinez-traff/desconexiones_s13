/** frontend/src/services/telemetryAPI.js
 * Telemetry API - Endpoints de telemetría y vehículos
 */

import apiClient from './api.js';

const telemetryAPI = {
  /**
   * Obtener listado de vehículos con paginación
   */
  getVehicles: (page = 1, filters = {}) => {
    return apiClient.get('/vehicles/data/', {
      params: {
        page,
        ...filters,
      },
    });
  },

  /**
   * Obtener detalle de un vehículo
   */
  getVehicle: (vehicleId) => {
    return apiClient.get(`/vehicles/data/${vehicleId}/`);
  },

  /**
   * Actualizar vehículo
   */
  updateVehicle: (vehicleId, data) => {
    return apiClient.patch(`/vehicles/data/${vehicleId}/`, data);
  },

  /**
   * Obtener registros de desconexión
   */
  getRegisters: (page = 1, filters = {}) => {
    return apiClient.get('/registers/', {
      params: {
        page,
        ...filters,
      },
    });
  },

  /**
   * Crear un registro de desconexión
   */
  createRegister: (data) => {
    return apiClient.post('/registers/', data);
  },

  /**
   * Actualizar registro
   */
  updateRegister: (registerId, data) => {
    return apiClient.patch(`/registers/${registerId}/`, data);
  },

  /**
   * Obtener datos para matriz de resumen
   */
  getSummaryMatrix: (params = {}) => {
    return apiClient.get('/analytics/summary-matrix/', { params });
  },

  /**
   * Obtener estadísticas de grupo
   */
  getGroupStats: (groupId, params = {}) => {
    return apiClient.get(`/analytics/group/${groupId}/stats/`, { params });
  },

  /**
   * Obtener vehículos con más desconexiones
   */
  getTopDisconnectedVehicles: (params = {}) => {
    return apiClient.get('/analytics/top-disconnected/', { params });
  },
};

export default telemetryAPI;
