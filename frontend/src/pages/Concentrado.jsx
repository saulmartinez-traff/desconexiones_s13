// frontend/src/pages/Concentrado.jsx
import React, { useState } from 'react';
import { useFetchRegisters } from '../hooks/useFetchRegisters.js';
import { useFilters } from '../hooks/useFilters.js';
import FilterPanel from '../molecules/FilterPanel.jsx';
import SearchBar from '../molecules/SearchBar.jsx';
import VehicleTable from '../organisms/VehicleTable.jsx';
import EditRegisterModal from '../components/EditRegisterModal.jsx';
import { colors, spacing } from '../styles/theme.js';
import { updateRegister } from '../services/api.js';

const Concentrado = () => {
  const [page, setPage] = useState(1);
  const { filters, updateFilter, clearFilters } = useFilters({});
  const [selectedRegister, setSelectedRegister] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { registers, loading, error, pagination, refetch } = useFetchRegisters(page, filters);

  const mockGroups = [
    { id: 1, group_description: 'BAJAS COPPEL' },
    { id: 2, group_description: 'GRUPO EXPANSION' },
    { id: 3, group_description: 'GRUPO FONDO' },
  ];

  // Columnas actualizadas según especificación
  const columns = [
    {
      header: 'Fecha',
      accessor: 'created_at',
      render: (value) => new Date(value).toLocaleDateString('es-MX')
    },
    { header: 'VIN', accessor: 'vin' },
    { header: 'Cliente', accessor: 'client_description' },
    {
      header: 'Distribuidor',
      accessor: 'distribuidor_name',
      render: (value) => value || '(Sin asignar)'
    },
    {
      header: 'Contrato',
      accessor: 'contrato',
      render: (value) => value || '(Sin asignar)'
    },
    {
      header: 'Última Conexión',
      accessor: 'last_connection',
      render: (value) => new Date(value).toLocaleString('es-MX')
    },
    { header: 'Problema', accessor: 'problem' },
    { header: 'Tipo', accessor: 'tipo' },
    { header: 'Estatus Final', accessor: 'estatus_final' },
    { header: 'Responsable', accessor: 'responsable' },
    {
      header: 'Comentario',
      accessor: 'comentario',
      render: (value) => value || '(Sin comentarios)'
    },
  ];

  const handleRowDoubleClick = (register) => {
    setSelectedRegister(register);
    setIsModalOpen(true);
  };

  const handleSaveRegister = async (updatedRegister) => {
    try {
      await updateRegister(updatedRegister.id, {
        tipo: updatedRegister.tipo,
        estatus_final: updatedRegister.estatus_final,
        responsable: updatedRegister.responsable,
        comentario: updatedRegister.comentario,
      });

      setIsModalOpen(false);
      setSelectedRegister(null);
      refetch(); // Recargar datos
    } catch (err) {
      console.error('Error al guardar registro:', err);
      alert('Error al guardar los cambios');
    }
  };

  return (
    <div
      style={{
        padding: spacing.xl,
        backgroundColor: colors.lightGray,
        minHeight: '100vh',
      }}
    >
      <h1 style={{ marginBottom: spacing.lg }}>Vista Concentrado - Desconexiones</h1>

      <SearchBar
        onSearch={(value) => updateFilter('search', value)}
        placeholder="Buscar por VIN, cliente, etc..."
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

      <VehicleTable
        data={registers}
        columns={columns}
        editable={false} // La edición se hace por modal
        loading={loading}
        error={error}
        onRowDoubleClick={handleRowDoubleClick}
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

        <div style={{ display: 'flex', gap: spacing.sm }}>
          <button
            onClick={() => setPage(prev => Math.max(1, prev - 1))}
            disabled={page === 1}
            style={{
              padding: `${spacing.sm} ${spacing.md}`,
              borderRadius: '4px',
              border: `1px solid ${colors.border}`,
              backgroundColor: page === 1 ? colors.lightGray : colors.white,
              cursor: page === 1 ? 'not-allowed' : 'pointer',
            }}
          >
            Anterior
          </button>
          <button
            onClick={() => setPage(prev => Math.min(pagination.totalPages, prev + 1))}
            disabled={page === pagination.totalPages}
            style={{
              padding: `${spacing.sm} ${spacing.md}`,
              borderRadius: '4px',
              border: `1px solid ${colors.border}`,
              backgroundColor: page === pagination.totalPages ? colors.lightGray : colors.white,
              cursor: page === pagination.totalPages ? 'not-allowed' : 'pointer',
            }}
          >
            Siguiente
          </button>
        </div>
      </div>

      {isModalOpen && selectedRegister && (
        <EditRegisterModal
          register={selectedRegister}
          onClose={() => {
            setIsModalOpen(false);
            setSelectedRegister(null);
          }}
          onSave={handleSaveRegister}
        />
      )}
    </div>
  );
};

export default Concentrado;
