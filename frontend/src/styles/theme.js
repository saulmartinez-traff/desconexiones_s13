/**
 * Paleta de colores del sistema S13 Desconexiones
 */

export const colors = {
  // Primary Colors
  darkBlue: '#18325A',      // Dark Blue (Títulos principales)
  mediumBlue: '#3274BA',    // Medium Blue (Elementos interactivos)
  deepTeal: '#1F6589',      // Deep Teal (Acentos)
  
  // Secondary Colors
  lightGray: '#EFF3F6',     // Light Gray (Fondos)
  skyBlue: '#EBF5FA',       // Sky Blue (Fondos alternos)
  black: '#070B0E',         // Black (Texto principal)
  
  // Status Colors
  success: '#10B981',       // Verde (Conectado)
  warning: '#F59E0B',       // Naranja (Advertencia)
  danger: '#EF4444',        // Rojo (Desconectado)
  info: '#3B82F6',          // Azul (Información)
  
  // Neutral
  white: '#FFFFFF',
  gray50: '#F9FAFB',
  gray100: '#F3F4F6',
  gray200: '#E5E7EB',
  gray300: '#D1D5DB',
  gray400: '#9CA3AF',
  gray500: '#6B7280',
  gray600: '#4B5563',
  gray700: '#374151',
  gray800: '#1F2937',
  gray900: '#111827',
};

/**
 * Tipografía del sistema
 */
export const fonts = {
  titleFont: "'Quesat', serif",        // Para títulos
  bodyFont: "'Questrial', sans-serif", // Para cuerpo
};

/**
 * Tamaños de fuente
 */
export const fontSizes = {
  xs: '12px',
  sm: '14px',
  base: '16px',
  lg: '18px',
  xl: '20px',
  '2xl': '24px',
  '3xl': '30px',
  '4xl': '36px',
};

/**
 * Espaciado
 */
export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  '2xl': '48px',
  '3xl': '64px',
};

/**
 * Breakpoints (responsive)
 */
export const breakpoints = {
  mobile: '640px',
  tablet: '768px',
  desktop: '1024px',
  widescreen: '1280px',
};

/**
 * Sombras
 */
export const shadows = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
};

/**
 * Tema completo
 */
export const theme = {
  colors,
  fonts,
  fontSizes,
  spacing,
  breakpoints,
  shadows,
};

export default theme;
