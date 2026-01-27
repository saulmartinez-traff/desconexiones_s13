/**
 * Custom Hook - useAggregation
 * Obtiene datos agregados para la matriz de resumen
 */

import { useState, useEffect } from 'react';
import telemetryAPI from '../services/telemetryAPI.js';

export const useAggregation = (startDate = null, endDate = null, groupId = null) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAggregation = async () => {
      setLoading(true);
      setError(null);

      try {
        const params = {};
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;
        if (groupId) params.group_id = groupId;

        const response = await telemetryAPI.getSummaryMatrix(params);
        setData(response.data);
      } catch (err) {
        setError(err.message || 'Error al cargar datos agregados');
        console.error('Error en useAggregation:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAggregation();
  }, [startDate, endDate, groupId]);

  return { data, loading, error };
};

export default useAggregation;
