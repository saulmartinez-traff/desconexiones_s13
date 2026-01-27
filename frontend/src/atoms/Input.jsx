/**
 * Input Component - Input reutilizable
 */

import React from 'react';
import { colors, spacing, fontSizes } from '../styles/theme.js';

const Input = ({
  type = 'text',
  placeholder = '',
  value = '',
  onChange,
  onBlur,
  error = '',
  label = '',
  required = false,
  disabled = false,
  maxLength,
  className = '',
  style = {},
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
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        maxLength={maxLength}
        disabled={disabled}
        className={className}
        style={{
          width: '100%',
          padding: `${spacing.sm} ${spacing.md}`,
          fontSize: fontSizes.base,
          border: `1px solid ${error ? colors.danger : colors.gray200}`,
          borderRadius: '4px',
          fontFamily: 'inherit',
          transition: 'border-color 0.3s ease',
          ...style,
        }}
        {...props}
      />
      {error && (
        <p style={{ color: colors.danger, fontSize: fontSizes.sm, marginTop: spacing.xs }}>
          {error}
        </p>
      )}
    </div>
  );
};

export default Input;
