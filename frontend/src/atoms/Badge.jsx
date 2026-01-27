/**
 * Badge Component - Etiquetas de estado
 */

import React from 'react';
import { colors, spacing, fontSizes } from '../styles/theme.js';

const Badge = ({
  children,
  variant = 'default',
  size = 'md',
  className = '',
  style = {},
}) => {
  const variants = {
    default: {
      backgroundColor: colors.gray200,
      color: colors.gray700,
    },
    primary: {
      backgroundColor: colors.mediumBlue,
      color: colors.white,
    },
    success: {
      backgroundColor: colors.success,
      color: colors.white,
    },
    danger: {
      backgroundColor: colors.danger,
      color: colors.white,
    },
    warning: {
      backgroundColor: colors.warning,
      color: colors.white,
    },
    info: {
      backgroundColor: colors.info,
      color: colors.white,
    },
  };

  const sizes = {
    sm: {
      padding: `${spacing.xs} ${spacing.sm}`,
      fontSize: fontSizes.xs,
    },
    md: {
      padding: `${spacing.xs} ${spacing.md}`,
      fontSize: fontSizes.sm,
    },
    lg: {
      padding: `${spacing.sm} ${spacing.lg}`,
      fontSize: fontSizes.base,
    },
  };

  const badgeStyle = {
    ...variants[variant],
    ...sizes[size],
    borderRadius: '12px',
    display: 'inline-block',
    fontWeight: 600,
    whiteSpace: 'nowrap',
    ...style,
  };

  return (
    <span style={badgeStyle} className={className}>
      {children}
    </span>
  );
};

export default Badge;
