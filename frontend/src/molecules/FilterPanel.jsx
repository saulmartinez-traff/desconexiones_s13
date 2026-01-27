/**
 * FilterPanel Component - Panel de filtros avanzados
 */

import React, { useState } from 'react';
import Select from '../atoms/Select.jsx';
import Button from '../atoms/Button.jsx';
import { colors, spacing } from '../styles/theme.js';

const FilterPanel = ({
  groups = [],
  onFilterChange,
  onClearFilters,
  initialFilters = {},
}) => {
  const [selectedGroup, setSelectedGroup] = useState(initialFilters.group || '');

  const handleGroupChange = (e) => {
    const value = e.target.value;
    setSelectedGroup(value);
    onFilterChange?.({ group: value });
  };

  const handleClearAll = () => {
    setSelectedGroup('');
    onClearFilters?.();
  };

  return (
    <div
      style={{
        padding: spacing.lg,
        backgroundColor: colors.skyBlue,
        borderRadius: '4px',
        marginBottom: spacing.lg,
      }}
    >
      <h3 style={{ marginBottom: spacing.md }}>Filtros</h3>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: spacing.md,
          marginBottom: spacing.lg,
        }}
      >
        <Select
          label="Grupo"
          placeholder="Seleccionar grupo..."
          options={groups.map((g) => ({
            value: g.id,
            label: g.group_description,
          }))}
          value={selectedGroup}
          onChange={handleGroupChange}
        />

        {/* Más filtros aquí */}
      </div>

      <Button onClick={handleClearAll} variant="secondary" size="sm">
        Limpiar Filtros
      </Button>
    </div>
  );
};

export default FilterPanel;
