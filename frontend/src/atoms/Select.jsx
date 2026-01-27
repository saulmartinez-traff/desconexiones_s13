/**
 * Select Component - Dropdown reutilizable
 */

import React from 'react';
import { colors, spacing, fontSizes } from '../styles/theme.js';

const Select = ({
  options = [],
  value = '',
  onChange,
  placeholder = 'Seleccionar...',
  label = '',
  required = false,
  disabled = false,
  className = '',
  style = {},
  error = '',
  ...props
}) => {
  return (
    <div style={{ marginBottom: spacing.md }}>
      {label && (
        <label
          style={{
            display: 'block',
            marginBottom: spacing.sm,
            fontWeight: 600,
            color: colors.darkBlue,
          }}
        >
          {label}
          {required && <span style={{ color: colors.danger }}>*</span>}
        </label>
      )}
      <select
        value={value}
        onChange={onChange}
        disabled={disabled}
        className={className}
        style={{
          width: '100%',
          padding: `${spacing.sm} ${spacing.md}`,
          fontSize: fontSizes.base,
          border: `1px solid ${error ? colors.danger : colors.gray200}`,
          borderRadius: '4px',
          fontFamily: 'inherit',
          backgroundColor: colors.white,
          cursor: disabled ? 'not-allowed' : 'pointer',
          transition: 'border-color 0.3s ease',
          ...style,
        }}
        {...props}
      >
        <option value="">{placeholder}</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && (
        <p style={{ color: colors.danger, fontSize: fontSizes.sm, marginTop: spacing.xs }}>
          {error}
        </p>
      )}
    </div>
  );
};

export default Select;
