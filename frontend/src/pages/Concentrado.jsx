// frontend/src/pages/Concentrado.jsx
import React, { useState } from 'react';
import { useFetchRegisters } from '../hooks/useFetchRegisters.js'; // Hook correcto
import { useFilters } from '../hooks/useFilters.js';
import FilterPanel from '../molecules/FilterPanel.jsx';
import SearchBar from '../molecules/SearchBar.jsx';
import VehicleTable from '../organisms/VehicleTable.jsx';
import { colors, spacing } from '../styles/theme.js';

const Concentrado = () => {
  const [page, setPage] = useState(1);
  const { filters, updateFilter, clearFilters } = useFilters({});
  
  // === CORRECCIÓN AQUÍ ===
  // 1. Usamos 'registers' (plural) porque así se llama en tu hook.
  // 2. Agregamos 'error' para evitar que la página truene al pasarlo abajo.
  const { registers, loading, error, pagination } = useFetchRegisters(page, filters);

  const mockGroups = [
    { id: 1, group_description: 'BAJAS COPPEL' },
    { id: 2, group_description: 'GRUPO EXPANSION' },
    { id: 3, group_description: 'GRUPO FONDO' },
  ];

  const columns = [
    { header: 'FECHA REPORTE', accessor: 'report_date' },
    { header: 'VIN', accessor: 'vin' },
    { header: 'CLIENTE', accessor: 'cliente' },
    { header: 'DISTRIBUIDOR', accessor: 'distribuidor' },
    { header: 'CONTRATO', accessor: 'contrato' },
    { header: 'ÚLTIMA CONEXIÓN', accessor: 'last_connection' },
    { header: 'PROBLEMA', accessor: 'problem' },
    { header: 'TIPO', accessor: 'type' },
    { header: 'ESTATUS FINAL', accessor: 'final_status' },
    { header: 'RESPONSABLE', accessor: 'responsible' },
    { header: 'COMENTARIO', accessor: 'comment' },
  ];

  return (
    <div
      style={{
        padding: spacing.xl,
        backgroundColor: colors.lightGray,
        minHeight: '100vh',
      }}
    >
      <h1 style={{ marginBottom: spacing.lg }}>Vista Concentrado</h1>

      <SearchBar
        onSearch={(value) => updateFilter('search', value)}
        placeholder="Buscar por VIN, grupo, etc..."
      />

      <FilterPanel
        groups={mockGroups}
        onFilterChange={(newFilters) => {
          Object.entries(newFilters).forEach(([key, value]) => {
            updateFilter(key, value);
          });
          setPage(1);
        }}
        onClearFilters={clearFilters}
      />

      {/* === CORRECCIÓN AQUÍ === */}
      <VehicleTable
        data={registers}  // <--- CAMBIO: Usamos la variable plural
        columns={columns}
        editable={true}
        loading={loading}
        error={error}     // <--- CAMBIO: Ahora sí existe esta variable
        onSave={(data) => {
          console.log('Guardar:', data);
        }}
      />

      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginTop: spacing.lg,
        }}
      >
        <p>
          Página {pagination.currentPage} de {pagination.totalPages} (
          {pagination.totalCount} registros)
        </p>
      </div>
    </div>
  );
};

export default Concentrado;
