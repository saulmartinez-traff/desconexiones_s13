/**
 * App Component - Raíz de la aplicación
 */

import React, { useState } from 'react';
import { colors, spacing, fonts } from './styles/theme.js';
import Concentrado from './pages/Concentrado.jsx';
import Resumen from './pages/Resumen.jsx';

const App = () => {
  const [currentView, setCurrentView] = useState('concentrado');

  return (
    <div
      style={{
        fontFamily: fonts.bodyFont,
        backgroundColor: colors.lightGray,
        minHeight: '100vh',
      }}
    >
      {/* Header Navigation */}
      <header
        style={{
          backgroundColor: colors.darkBlue,
          color: colors.white,
          padding: spacing.lg,
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        }}
      >
        <div
          style={{
            maxWidth: '1400px',
            margin: '0 auto',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          {/* Logo Placeholder */}
          <div
            style={{
              width: '40px',
              height: '40px',
              backgroundColor: colors.mediumBlue,
              borderRadius: '4px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 'bold',
            }}
          >
            S13
          </div>

          <h1
            style={{
              fontSize: '24px',
              fontFamily: fonts.titleFont,
              margin: 0,
            }}
          >
            Desconexiones Vehiculares
          </h1>

          {/* Navigation Links */}
          <nav style={{ display: 'flex', gap: spacing.lg }}>
            <button
              onClick={() => setCurrentView('concentrado')}
              style={{
                backgroundColor:
                  currentView === 'concentrado'
                    ? colors.mediumBlue
                    : 'transparent',
                color: colors.white,
                border: 'none',
                padding: `${spacing.sm} ${spacing.md}`,
                cursor: 'pointer',
                borderRadius: '4px',
                fontWeight: 600,
                transition: 'background-color 0.3s ease',
              }}
              onMouseOver={(e) => {
                if (currentView !== 'concentrado') {
                  e.target.style.backgroundColor = colors.mediumBlue;
                  e.target.style.opacity = '0.7';
                }
              }}
              onMouseOut={(e) => {
                if (currentView !== 'concentrado') {
                  e.target.style.backgroundColor = 'transparent';
                  e.target.style.opacity = '1';
                }
              }}
            >
              Concentrado
            </button>
            <button
              onClick={() => setCurrentView('resumen')}
              style={{
                backgroundColor:
                  currentView === 'resumen' ? colors.mediumBlue : 'transparent',
                color: colors.white,
                border: 'none',
                padding: `${spacing.sm} ${spacing.md}`,
                cursor: 'pointer',
                borderRadius: '4px',
                fontWeight: 600,
                transition: 'background-color 0.3s ease',
              }}
              onMouseOver={(e) => {
                if (currentView !== 'resumen') {
                  e.target.style.backgroundColor = colors.mediumBlue;
                  e.target.style.opacity = '0.7';
                }
              }}
              onMouseOut={(e) => {
                if (currentView !== 'resumen') {
                  e.target.style.backgroundColor = 'transparent';
                  e.target.style.opacity = '1';
                }
              }}
            >
              Resumen
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: '1400px', margin: '0 auto' }}>
        {currentView === 'concentrado' && <Concentrado />}
        {currentView === 'resumen' && <Resumen />}
      </main>

      {/* Footer */}
      <footer
        style={{
          backgroundColor: colors.darkBlue,
          color: colors.white,
          textAlign: 'center',
          padding: spacing.lg,
          marginTop: spacing.xl,
        }}
      >
        <p>© 2025 S13 Desconexiones. Sistema de Gestión Vehicular.</p>
      </footer>
    </div>
  );
};

export default App;
