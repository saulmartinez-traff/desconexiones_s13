/**
 * SearchBar Component - Barra de búsqueda con filtros
 */

import React, { useState } from 'react';
import Input from '../atoms/Input.jsx';
import Button from '../atoms/Button.jsx';
import { colors, spacing } from '../styles/theme.js';

const SearchBar = ({
  onSearch,
  onFilter,
  placeholder = 'Buscar...',
  filters = {},
  showFilters = true,
}) => {
  const [searchValue, setSearchValue] = useState('');

  const handleSearch = (e) => {
    const value = e.target.value;
    setSearchValue(value);
    onSearch?.(value);
  };

  const handleClear = () => {
    setSearchValue('');
    onSearch?.('');
  };

  return (
    <div
      style={{
        padding: spacing.lg,
        backgroundColor: colors.white,
        borderRadius: '4px',
        marginBottom: spacing.lg,
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      }}
    >
      <div style={{ display: 'flex', gap: spacing.md, marginBottom: spacing.md }}>
        <Input
          type="text"
          placeholder={placeholder}
          value={searchValue}
          onChange={handleSearch}
          style={{ flex: 1 }}
        />
        <Button onClick={handleClear} variant="secondary" size="md">
          Limpiar
        </Button>
      </div>

      {showFilters && Object.keys(filters).length > 0 && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: spacing.md,
          }}
        >
          {Object.entries(filters).map(([key, value]) => (
            <div key={key}>
              {/* Renderizar cada filtro */}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchBar;
