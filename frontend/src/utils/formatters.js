/**
 * Utilities - Funciones auxiliares de formato
 */

/**
 * Formatea una fecha a formato legible
 */
export const formatDate = (date) => {
  if (!date) return '-';
  return new Date(date).toLocaleDateString('es-MX', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  });
};

/**
 * Formatea una fecha y hora
 */
export const formatDateTime = (datetime) => {
  if (!datetime) return '-';
  return new Date(datetime).toLocaleString('es-MX');
};

/**
 * Formatea VIN truncado
 */
export const formatVIN = (vin, show = 8) => {
  if (!vin) return '-';
  return `${vin.substring(0, show)}...`;
};

/**
 * Formatea velocidad
 */
export const formatSpeed = (speed) => {
  if (!speed) return '0 km/h';
  return `${parseFloat(speed).toFixed(2)} km/h`;
};

/**
 * Formatea porcentaje
 */
export const formatPercentage = (value, decimals = 1) => {
  if (value === null || value === undefined) return '-';
  return `${parseFloat(value).toFixed(decimals)}%`;
};

/**
 * Capitaliza la primera letra
 */
export const capitalize = (str) => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

/**
 * Obtiene el estado de conectividad como badge color
 */
export const getConnectionStatus = (isConnected) => {
  return isConnected
    ? { color: '#10B981', label: 'Conectado' }
    : { color: '#EF4444', label: 'Desconectado' };
};

export default {
  formatDate,
  formatDateTime,
  formatVIN,
  formatSpeed,
  formatPercentage,
  capitalize,
  getConnectionStatus,
};
