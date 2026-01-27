/**
 * Custom Hook - useFetchVehicles
 * Maneja el fetch de vehículos con paginación y filtros
 */

import { useState, useEffect } from 'react';
import telemetryAPI from '../services/telemetryAPI.js';

export const useFetchVehicles = (page = 1, filters = {}) => {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalCount: 0,
  });

  useEffect(() => {
    const fetchVehicles = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await telemetryAPI.getVehicles(page, filters);
        setVehicles(response.data.results || []);
        setPagination({
          currentPage: page,
          totalPages: Math.ceil((response.data.count || 0) / 20),
          totalCount: response.data.count || 0,
        });
      } catch (err) {
        setError(err.message || 'Error al cargar vehículos');
        console.error('Error en useFetchVehicles:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchVehicles();
  }, [page, filters]);

  return {
    vehicles,
    loading,
    error,
    pagination,
    refetch: () => {},
  };
};

export default useFetchVehicles;
