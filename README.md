# Sistema de Gestión de Desconexiones S13

## 📋 Descripción

Sistema web para monitoreo y gestión de desconexiones de vehículos equipados con dispositivos de telemetría. Permite identificar, clasificar y dar seguimiento a unidades que presentan problemas de conectividad, facilitando la toma de decisiones y el control operativo.

## 🎯 Objetivo

Proporcionar una plataforma centralizada para:
- Detectar automáticamente desconexiones de vehículos
- Clasificar desconexiones según tipo (en trayecto vs en base)
- Gestionar el seguimiento y resolución de incidencias
- Generar reportes y análisis de desconexiones
- Facilitar la comunicación entre distribuidores, clientes y equipo técnico

## 🚀 Características Principales

### Backend (Django + Django REST Framework)
- **API RESTful** con autenticación JWT
- **ETL automatizado** para consumo de datos de telemetría
- **Modelos relacionales** para organización jerárquica (Cliente → Grupo → Vehículo)
- **Sistema de permisos** basado en roles (Admin, PM, Director, Distribuidor)
- **Bitácora de auditoría** para trazabilidad de cambios
- **Paginación y filtros** optimizados para grandes volúmenes de datos

### Frontend (React + Vite)
- **Arquitectura Atomic Design** (Atoms → Molecules → Organisms → Pages)
- **Vista Concentrado** con tabla interactiva de desconexiones
- **Edición inline** de registros con validación
- **Filtros dinámicos** por cliente, grupo, fecha, estado
- **Dashboard analítico** con métricas y gráficas
- **Responsive design** para múltiples dispositivos

## 🛠️ Stack Tecnológico

### Backend
- **Framework**: Django 4.2+
- **API**: Django REST Framework
- **Base de Datos**: MySQL 8.0+ / PostgreSQL 13+
- **Autenticación**: JWT (djangorestframework-simplejwt)
- **ORM**: Django ORM
- **Validación**: Django Validators + Custom validators

### Frontend
- **Framework**: React 18+
- **Build Tool**: Vite 5+
- **Routing**: React Router v6
- **State Management**: React Hooks (useState, useContext)
- **HTTP Client**: Axios
- **Styling**: CSS Modules + Theme system

### DevOps
- **Control de versiones**: Git
- **Gestión de dependencias**: pip (backend), npm (frontend)
- **Entorno virtual**: venv (Python)
- **Logging**: Python logging + JSON formatter

## 📁 Estructura del Proyecto

```
desconexiones_s13/
├── backend/
│   ├── apps/
│   │   ├── organization/      # Clientes, Grupos, Usuarios, Distribuidores
│   │   ├── vehicles/          # Vehículos, Geocercas, Contratos
│   │   └── registers/         # Registros de desconexión, Bitácora
│   ├── services/              # Lógica de negocio (ETL, Analytics)
│   ├── core/                  # Configuración Django
│   ├── middleware/            # Middleware personalizado
│   └── manage.py
│
├── frontend/
│   ├── src/
│   │   ├── atoms/             # Componentes básicos (Button, Input)
│   │   ├── molecules/         # Composiciones (SearchBar, FilterPanel)
│   │   ├── organisms/         # Componentes complejos (VehicleTable)
│   │   ├── pages/             # Vistas (Concentrado, Dashboard, Resumen)
│   │   ├── hooks/             # Custom hooks
│   │   ├── services/          # API clients
│   │   ├── styles/            # Theme y estilos globales
│   │   └── utils/             # Utilidades
│   └── package.json
│
├── docs/                      # Documentación técnica
├── logs/                      # Archivos de log
└── README.md
```

## 🔧 Instalación

### Requisitos Previos
- Python 3.11+
- Node.js 16+
- MySQL 8.0+ o PostgreSQL 13+
- Git

### Backend

```bash
# Clonar repositorio
cd desconexiones_s13/backend

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de BD

# Crear base de datos
# MySQL:
mysql -u root -p
CREATE DATABASE desconexiones_s13 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev

# Build para producción
npm run build
```

## 📖 Uso Básico

### 1. Acceso al Sistema
- **Admin Panel**: http://localhost:8000/admin
- **API Root**: http://localhost:8000/api/
- **Frontend**: http://localhost:5173

### 2. Proceso ETL
```bash
# Ejecutar ETL manualmente
python manage.py shell
>>> from services.etl_service import ETLService
>>> etl = ETLService()
>>> stats = etl.run_etl()
>>> print(stats)
```

### 3. Vista Concentrado
1. Acceder a la vista Concentrado en el frontend
2. Filtrar por cliente, grupo o fecha
3. Hacer doble clic en un registro para editarlo
4. Modificar Tipo, Estatus Final, Responsable o Comentario
5. Guardar cambios

### 4. API Endpoints Principales

```bash
# Autenticación
POST /api/auth/token/
POST /api/auth/token/refresh/

# Registros de desconexión
GET /api/registers/
GET /api/registers/{id}/
PUT /api/registers/{id}/
PATCH /api/registers/{id}/

# Vehículos
GET /api/vehicles/
GET /api/vehicles/{id}/

# Clientes y Grupos
GET /api/clients/
GET /api/groups/
```

## 🔐 Roles y Permisos

- **ADMIN**: Acceso completo al sistema
- **PM (Project Manager)**: Gestión de distribuidores y contratos, carga de Excel
- **DIRECTOR**: Vista de clientes asignados, edición de registros
- **DISTRIBUIDOR**: Vista de vehículos asignados, edición limitada

## 📊 Modelo de Datos

### Entidades Principales
- **Client**: Cliente propietario de vehículos
- **Group**: Agrupación de vehículos bajo un cliente
- **Vehicle**: Vehículo con telemetría
- **Register**: Registro de desconexión
- **Distribuidor**: Empresa distribuidora responsable
- **Geofence**: Geocerca/base de operación
- **Bitacora**: Auditoría de cambios

### Lógica de Desconexión
- **Desconexión**: `last_connection` < día actual
- **Tipo**:
  - **En trayecto**: `speed > 0` AND `geofence_name == null`
  - **En base**: Cualquier otro caso

## 📚 Documentación Adicional

- [QUICKSTART.md](./QUICKSTART.md) - Guía de inicio rápido
- [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) - Arquitectura del sistema
- [docs/API_ENDPOINTS.md](./docs/API_ENDPOINTS.md) - Documentación de API
- [docs/SETUP_GUIDE.md](./docs/SETUP_GUIDE.md) - Guía de instalación detallada
- [ROADMAP.md](./ROADMAP.md) - Plan de desarrollo

## 🐛 Troubleshooting

### Error de conexión a BD
```bash
# Verificar credenciales en .env
# Verificar que MySQL/PostgreSQL esté corriendo
# Verificar que la base de datos exista
```

### Error de migraciones
```bash
# Limpiar migraciones
python manage.py migrate --fake
python manage.py migrate
```

### Error de CORS en frontend
```bash
# Verificar CORS_ALLOWED_ORIGINS en settings.py
# Debe incluir http://localhost:5173
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 Licencia

Este proyecto es privado y confidencial.

## 👥 Equipo

- **Desarrollo**: Equipo de desarrollo Traffilog
- **Product Owner**: [Nombre]
- **Tech Lead**: [Nombre]

## 📞 Soporte

Para soporte técnico o preguntas:
- **Email**: soporte@traffilog.com
- **Documentación**: Ver carpeta `/docs`
- **Issues**: Reportar en el sistema de tickets interno

---

**Última actualización**: 02 de Febrero, 2026  
**Versión**: 0.3.0  
**Estado**: En desarrollo activo