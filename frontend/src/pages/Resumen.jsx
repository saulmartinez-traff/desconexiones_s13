/**
 * Resumen Page - Vista de matriz dinámica de análisis
 */

import React, { useState } from 'react';
import { useAggregation } from '../hooks/useAggregation.js';
import SummaryMatrix from '../organisms/SummaryMatrix.jsx';
import Input from '../atoms/Input.jsx';
import Button from '../atoms/Button.jsx';
import { colors, spacing } from '../styles/theme.js';

const Resumen = () => {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [selectedGroup, setSelectedGroup] = useState(null);

  const { data, loading, error } = useAggregation(startDate, endDate, selectedGroup);

  const handleFilter = () => {
    // Trigger refetch con nuevas fechas
    console.log('Filtrar con fechas:', startDate, endDate);
  };

  return (
    <div
      style={{
        padding: spacing.xl,
        backgroundColor: colors.lightGray,
        minHeight: '100vh',
      }}
    >
      {/* Encabezado */}
      <h1 style={{ marginBottom: spacing.lg }}>Vista Resumen</h1>
      <p style={{ marginBottom: spacing.lg, color: colors.gray600 }}>
        Matriz de análisis de vehículos conectados/desconectados por fecha y contrato
      </p>

      {/* Controles de filtro */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: spacing.md,
          marginBottom: spacing.lg,
          padding: spacing.lg,
          backgroundColor: colors.white,
          borderRadius: '4px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        }}
      >
        <Input
          type="date"
          label="Fecha Inicio"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
        />
        <Input
          type="date"
          label="Fecha Fin"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
        />
        <div style={{ display: 'flex', alignItems: 'flex-end' }}>
          <Button onClick={handleFilter}>Aplicar Filtros</Button>
        </div>
      </div>

      {/* Matriz de resumen */}
      <SummaryMatrix
        data={data}
        loading={loading}
        error={error}
      />

      {/* Leyenda */}
      <div
        style={{
          marginTop: spacing.xl,
          padding: spacing.lg,
          backgroundColor: colors.skyBlue,
          borderRadius: '4px',
        }}
      >
        <h3 style={{ marginBottom: spacing.md }}>Leyenda</h3>
        <p style={{ marginBottom: spacing.sm }}>
          <strong>C:</strong> Vehículos conectados
        </p>
        <p style={{ marginBottom: spacing.sm }}>
          <strong>D:</strong> Vehículos desconectados
        </p>
        <p>
          <strong>%:</strong> Porcentaje de conexión
        </p>
      </div>
    </div>
  );
};

export default Resumen;
