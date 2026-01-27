/**
 * Concentrado Page - Vista de tabla concentrada con filtros
 */

import React, { useState } from 'react';
import { useFetchVehicles } from '../hooks/useFetchVehicles.js';
import { useFilters } from '../hooks/useFilters.js';
import FilterPanel from '../molecules/FilterPanel.jsx';
import SearchBar from '../molecules/SearchBar.jsx';
import VehicleTable from '../organisms/VehicleTable.jsx';
import { colors, spacing } from '../styles/theme.js';

const Concentrado = () => {
  const [page, setPage] = useState(1);
  const { filters, updateFilter, clearFilters } = useFilters({});
  const { vehicles, loading, error, pagination } = useFetchVehicles(page, filters);

  const mockGroups = [
    { id: 1, group_description: 'BAJAS COPPEL' },
    { id: 2, group_description: 'GRUPO EXPANSION' },
    { id: 3, group_description: 'GRUPO FONDO' },
  ];

  const columns = ['VIN', 'TIPO', 'ESTATUS FINAL', 'RESPONSABLE', 'COMENTARIO'];

  return (
    <div
      style={{
        padding: spacing.xl,
        backgroundColor: colors.lightGray,
        minHeight: '100vh',
      }}
    >
      {/* Encabezado */}
      <h1 style={{ marginBottom: spacing.lg }}>Vista Concentrado</h1>

      {/* Barra de búsqueda */}
      <SearchBar
        onSearch={(value) => updateFilter('search', value)}
        placeholder="Buscar por VIN, grupo, etc..."
      />

      {/* Panel de filtros */}
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

      {/* Tabla de vehículos */}
      <VehicleTable
        data={vehicles}
        columns={columns}
        editable={true}
        loading={loading}
        error={error}
        onSave={(data) => {
          console.log('Guardar:', data);
          // TODO: Implementar guardar cambios
        }}
      />

      {/* Paginación */}
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
