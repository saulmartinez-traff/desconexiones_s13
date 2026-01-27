/**
 * Constantes - Opciones de filtros y estados
 */

export const GROUPS = [
  { id: 1, label: 'BAJAS COPPEL' },
  { id: 2, label: 'GRUPO EXPANSION' },
  { id: 3, label: 'GRUPO FONDO' },
];

export const DISCONNECTION_TYPES = [
  { value: 'ROUTE', label: 'Desconexión en trayecto' },
  { value: 'BASE', label: 'Desconexión en base' },
  { value: 'UNKNOWN', label: 'Desconocida' },
];

export const PROBLEM_TYPES = [
  { value: 'MALFUNCTION', label: 'Mal funcionamiento' },
  { value: 'CONNECTION_LOSS', label: 'Pérdida de conexión' },
  { value: 'LOW_BATTERY', label: 'Batería baja' },
  { value: 'HARDWARE_FAILURE', label: 'Fallo de hardware' },
  { value: 'UNKNOWN', label: 'Desconocido' },
];

export const FINAL_STATUSES = [
  { value: 'WORKSHOP', label: 'Taller' },
  { value: 'BASE', label: 'Base' },
  { value: 'RESOLVED', label: 'Resuelto' },
  { value: 'PENDING', label: 'Pendiente' },
  { value: 'NA', label: 'No aplica' },
];

export const USER_ROLES = [
  { value: 'ADMIN', label: 'Administrador' },
  { value: 'MANAGER', label: 'Gestor' },
  { value: 'OPERATOR', label: 'Operador' },
  { value: 'VIEWER', label: 'Visualizador' },
];

export default {
  GROUPS,
  DISCONNECTION_TYPES,
  PROBLEM_TYPES,
  FINAL_STATUSES,
  USER_ROLES,
};
