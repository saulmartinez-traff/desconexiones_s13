/** frontend/src/hooks/useFetchRegisters.js
 * Custom Hook - useFetchRegisters
 * Maneja el fetch de registros con paginación y filtros
 */

import { useState, useEffect } from 'react';
import telemetryAPI from '../services/telemetryAPI.js';

export const useFetchRegisters = (page = 1, filters = {}) => {
  const [registers, setRegisters] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalCount: 0,
  });

  useEffect(() => {
    const fetchRegisters = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await telemetryAPI.getRegisters(page, filters);
        setRegisters(response.data.results || []);
        setPagination({
          currentPage: page,
          totalPages: Math.ceil((response.data.count || 0) / 20),
          totalCount: response.data.count || 0,
        });
      } catch (err) {
        setError(err.message || 'Error al cargar registros');
        console.error('Error en useFetchRegisters:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRegisters();
  }, [page, filters]);

  return {
    registers,
    loading,
    error,
    pagination,
    refetch: () => {},
  };
};

export default useFetchRegisters;
