import React, { useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext';
import Concentrado from './pages/Concentrado';
import Resumen from './pages/Resumen';
import Login from './pages/Login';

// Componente para proteger rutas (El "Cadenero")
const PrivateRoute = ({ children }) => {
  const { user, loading } = useContext(AuthContext);
  if (loading) return <div className="p-10 text-center">Cargando...</div>;
  return user ? children : <Navigate to="/login" replace />;
};

// Layout Principal (Header + Contenido + Footer)
// Solo se muestra cuando ya estás logueado
const MainLayout = ({ children }) => {
  const { logout, user } = useContext(AuthContext);
  const location = useLocation(); // Para saber en qué ruta estamos

  // Función auxiliar para estilos de botones activos
  const getLinkClass = (path) => {
    const baseClass = "px-4 py-2 rounded font-semibold transition-colors duration-200 ";
    return location.pathname === path 
      ? baseClass + "bg-blue-600 text-white" 
      : baseClass + "text-white hover:bg-white/10";
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-100 font-sans">
      {/* HEADER */}
      <header className="bg-blue-900 text-white shadow-md p-4">
        <div className="max-w-[1400px] mx-auto flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-blue-600 rounded flex items-center justify-center font-bold">
              S13
            </div>
            <h1 className="text-xl font-bold hidden md:block">Desconexiones Vehiculares</h1>
          </div>

          <nav className="flex items-center gap-2">
            <Link to="/concentrado" className={getLinkClass('/concentrado')}>
              Concentrado
            </Link>
            <Link to="/resumen" className={getLinkClass('/resumen')}>
              Resumen
            </Link>
            <button 
              onClick={logout}
              className="ml-4 px-3 py-1 text-sm bg-red-600 hover:bg-red-700 rounded text-white transition"
            >
              Salir ({user?.username})
            </button>
          </nav>
        </div>
      </header>

      {/* MAIN CONTENT */}
      <main className="flex-grow max-w-[1400px] w-full mx-auto p-4">
        {children}
      </main>

      {/* FOOTER */}
      <footer className="bg-blue-900 text-white text-center p-4 mt-auto">
        <p className="text-sm">© 2025 S13 Desconexiones. Sistema de Gestión Vehicular.</p>
      </footer>
    </div>
  );
};

const App = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Ruta Pública: Login */}
          <Route path="/login" element={<Login />} />

          {/* Rutas Protegidas (Envueltas en el Layout) */}
          <Route 
            path="/concentrado" 
            element={
              <PrivateRoute>
                <MainLayout>
                  <Concentrado />
                </MainLayout>
              </PrivateRoute>
            } 
          />

          <Route 
            path="/resumen" 
            element={
              <PrivateRoute>
                <MainLayout>
                  <Resumen />
                </MainLayout>
              </PrivateRoute>
            } 
          />

          {/* Redirección por defecto */}
          <Route path="*" element={<Navigate to="/concentrado" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;