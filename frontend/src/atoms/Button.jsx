/**
 * Button Component - Botón reutilizable
 */

import React from 'react';
import { colors, spacing, fontSizes } from '../styles/theme.js';

const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  onClick,
  disabled = false,
  type = 'button',
  className = '',
  style = {},
  ...props
}) => {
  const variants = {
    primary: {
      backgroundColor: colors.mediumBlue,
      color: colors.white,
      border: `2px solid ${colors.mediumBlue}`,
      '&:hover': {
        backgroundColor: colors.darkBlue,
        borderColor: colors.darkBlue,
      },
    },
    secondary: {
      backgroundColor: colors.lightGray,
      color: colors.darkBlue,
      border: `2px solid ${colors.darkBlue}`,
      '&:hover': {
        backgroundColor: colors.skyBlue,
      },
    },
    danger: {
      backgroundColor: colors.danger,
      color: colors.white,
      border: `2px solid ${colors.danger}`,
      '&:hover': {
        opacity: 0.8,
      },
    },
    success: {
      backgroundColor: colors.success,
      color: colors.white,
      border: `2px solid ${colors.success}`,
      '&:hover': {
        opacity: 0.8,
      },
    },
  };

  const sizes = {
    sm: {
      padding: `${spacing.xs} ${spacing.md}`,
      fontSize: fontSizes.sm,
    },
    md: {
      padding: `${spacing.sm} ${spacing.lg}`,
      fontSize: fontSizes.base,
    },
    lg: {
      padding: `${spacing.md} ${spacing.xl}`,
      fontSize: fontSizes.lg,
    },
  };

  const buttonStyle = {
    ...variants[variant],
    ...sizes[size],
    borderRadius: '4px',
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.5 : 1,
    transition: 'all 0.3s ease',
    fontWeight: 600,
    ...style,
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      style={buttonStyle}
      className={className}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;
