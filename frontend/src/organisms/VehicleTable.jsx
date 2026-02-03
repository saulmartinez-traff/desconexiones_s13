/**
 * VehicleTable Component - Tabla de vehículos editable
 */

import React, { useState } from 'react';
import Badge from '../atoms/Badge.jsx';
import Button from '../atoms/Button.jsx';
import Input from '../atoms/Input.jsx';
import Select from '../atoms/Select.jsx';
import { colors, spacing, fontSizes } from '../styles/theme.js';

const VehicleTable = ({
  data = [],
  columns = [],
  editable = false,
  onSave,
  onRowDoubleClick,
  loading = false,
  error = null,
}) => {
  const [editingId, setEditingId] = useState(null);
  const [editData, setEditData] = useState({});

  const handleEdit = (row) => {
    setEditingId(row.id);
    setEditData(row);
  };

  const handleSave = () => {
    onSave?.(editData);
    setEditingId(null);
  };

  const handleCancel = () => {
    setEditingId(null);
    setEditData({});
  };

  const handleChange = (field, value) => {
    setEditData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleDoubleClick = (row) => {
    if (onRowDoubleClick) {
      onRowDoubleClick(row);
    }
  };

  if (loading) {
    return <p>Cargando...</p>;
  }

  if (error) {
    return <p style={{ color: colors.danger }}>Error: {error}</p>;
  }

  if (data.length === 0) {
    return <p>No hay datos disponibles</p>;
  }

  return (
    <div
      style={{
        overflowX: 'auto',
        backgroundColor: colors.white,
        borderRadius: '4px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      }}
    >
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ backgroundColor: colors.darkBlue, color: colors.white }}>
            {columns.map((col) => (
              <th
                key={col.accessor || col.header}
                style={{
                  padding: spacing.md,
                  textAlign: 'left',
                  fontWeight: 600,
                }}
              >
                {col.header}
              </th>
            ))}
            {editable && <th style={{ padding: spacing.md }}>Acciones</th>}
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr
              key={row.id}
              onDoubleClick={() => handleDoubleClick(row)}
              style={{
                borderBottom: `1px solid ${colors.gray200}`,
                cursor: onRowDoubleClick ? 'pointer' : 'default',
              }}
            >
              {columns.map((col) => {
                const value = row[col.accessor];
                const displayValue = col.render ? col.render(value, row) : value;

                return (
                  <td
                    key={`${row.id}-${col.accessor}`}
                    style={{
                      padding: spacing.md,
                      borderBottom: `1px solid ${colors.gray200}`,
                    }}
                  >
                    {editingId === row.id && col.editable ? (
                      <Input
                        value={editData[col.accessor] || ''}
                        onChange={(e) => handleChange(col.accessor, e.target.value)}
                        style={{ margin: 0 }}
                      />
                    ) : (
                      displayValue
                    )}
                  </td>
                );
              })}
              {editable && (
                <td
                  style={{
                    padding: spacing.md,
                    borderBottom: `1px solid ${colors.gray200}`,
                  }}
                >
                  {editingId === row.id ? (
                    <div style={{ display: 'flex', gap: spacing.sm }}>
                      <Button size="sm" onClick={handleSave}>
                        Guardar
                      </Button>
                      <Button size="sm" variant="secondary" onClick={handleCancel}>
                        Cancelar
                      </Button>
                    </div>
                  ) : (
                    <Button size="sm" onClick={() => handleEdit(row)}>
                      Editar
                    </Button>
                  )}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default VehicleTable;
