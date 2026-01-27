# Architecture Guide - S13 Desconexiones

## Visión General

Sistema modular, escalable y mantenible para gestión de desconexiones vehiculares. Basado en principios SOLID y patrones de arquitectura limpios.

## Capas de Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│         Frontend (React + Vite)                         │
│  ├─ Presentación (Components)                           │
│  ├─ Lógica de UI (Hooks)                                │
│  └─ Estado Global (Zustand)                             │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────v────────────────────────────────────┐
│         API Gateway (Django)                             │
│  ├─ Views/ViewSets                                      │
│  ├─ Serializers (Validación)                            │
│  └─ URLs Router                                         │
└────────────────────┬────────────────────────────────────┘
                     │ ORM
┌────────────────────v────────────────────────────────────┐
│      Services Layer (Lógica de Negocio)                │
│  ├─ ETLService                                          │
│  ├─ GeofenceService                                     │
│  ├─ DisconnectionRules                                  │
│  └─ AnalyticsService                                    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────v────────────────────────────────────┐
│           Models Layer (ORM)                            │
│  ├─ User, Distribuidor, Client, Group                 │
│  ├─ Vehicle, Geofence, Contrato                        │
│  └─ Register, Bitacora                                  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────v────────────────────────────────────┐
│           Database Layer (MySQL/PostgreSQL)            │
│  ├─ Tables & Schemas                                    │
│  ├─ Indexes                                             │
│  └─ Constraints                                         │
└──────────────────────────────────────────────────────────┘
```

## Módulos Backend

### 1. Organization App (apps/organization)

**Responsabilidad:** Gestión de entidades organizacionales.

**Models:**
- `User`: Extended user model con roles
- `Distribuidor`: Empresa distribuidora
- `Client`: Cliente (ej: BAJAS COPPEL)
- `Group`: Agrupación de vehículos

**Endpoints:**
```
GET  /api/v1/organization/clients/
GET  /api/v1/organization/groups/
GET  /api/v1/organization/distribuidores/
```

### 2. Vehicles App (apps/vehicles)

**Responsabilidad:** Gestión de vehículos y geocercas.

**Models:**
- `Vehicle`: Entidad principal (con relaciones)
- `Geofence`: Zonas geográficas (polígonos/círculos)
- `Contrato`: Relación VIN-Contrato

**Lógica:**
- Validación de VIN
- Detección de posición en geocerca
- Cálculo de distancias (Haversine)

**Endpoints:**
```
GET    /api/v1/vehicles/
POST   /api/v1/vehicles/
PATCH  /api/v1/vehicles/{id}/
GET    /api/v1/vehicles/by-vin/{vin}/
```

### 3. Registers App (apps/registers)

**Responsabilidad:** Registros de desconexiones y auditoría.

**Models:**
- `Register`: Evento de desconexión
- `Bitacora`: Historial de cambios (audit log)

**Campos Editables:**
- `problem`: Tipo de problema
- `final_status`: Estado de resolución
- `responsible`: Usuario asignado
- `comment`: Comentarios

**Endpoints:**
```
GET    /api/v1/registers/
POST   /api/v1/registers/
PATCH  /api/v1/registers/{id}/
```

### 4. Auth App (apps/auth)

**Responsabilidad:** Autenticación y autorización.

**Features:**
- JWT Token-based auth
- Permission classes customizadas
- Roles: ADMIN, MANAGER, OPERATOR, VIEWER

**Endpoints:**
```
POST  /api/auth/token/
POST  /api/auth/token/refresh/
```

## Services Layer

### ETLService

Orquesta el flujo de extracción y transformación de telemetría.

```python
class ETLService:
    def consume_telemetry_endpoint(max_pages) → List[Dict]
    def apply_vin_filter(vehicles) → List[Dict]
    def validate_data(vehicles) → Tuple[valid, invalid]
    def batch_process(vehicles, geofence_svc, rules) → Dict
```

**Flujo:**
1. Fetch datos del API de telemetría (con paginación)
2. Filtrar VINs que contengan "SZ"
3. Validar integridad de datos
4. Procesar en lotes (batch)
5. Persistir registros

### GeofenceService

Gestiona lógica de geoprocesamiento.

```python
class GeofenceService:
    def is_in_geofence(lat, lon, geofence) → bool
    def get_geofence_name(geofence) → str
    def find_geofence_by_location(lat, lon) → Geofence
    def validate_polygon(coordinates) → Tuple[bool, str]
    def validate_circle(circle_data) → Tuple[bool, str]
    def calculate_distance(lat1, lon1, lat2, lon2) → float
```

**Algoritmos:**
- **Ray Casting**: Punto en polígono
- **Haversine**: Distancia entre coordenadas

### DisconnectionRules

Reglas de negocio para clasificación.

```python
class DisconnectionRules:
    def classify_disconnection(vehicle, speed, in_geofence, geofence_name) → str
    def is_disconnection(vehicle_data) → bool
    def validate_speed(speed) → bool
    def determine_status(problem) → str
    def validate_responsible_assignment(user) → bool
    def get_priority_level(disconnection_type, problem) → int
```

**Reglas Principales:**
```
IF speed > 5 km/h AND NOT in_geofence:
    THEN "Desconexión en trayecto"
ELSE:
    THEN "Desconexión en base"
```

### AnalyticsService

Genera agregaciones y reportes.

```python
class AnalyticsService:
    def get_summary_matrix(start_date, end_date, group_id) → Dict
    def get_group_statistics(group_id, days) → Dict
    def get_top_disconnection_vehicles(days, limit) → List[Dict]
```

## Componentes Frontend

### Estructura Atómica

```
atoms/               # Componentes básicos
├─ Button.jsx
├─ Input.jsx
├─ Badge.jsx
└─ Select.jsx

molecules/           # Composiciones simples
├─ SearchBar.jsx
├─ FilterPanel.jsx
└─ TableHeader.jsx

organisms/           # Componentes complejos
├─ VehicleTable.jsx
└─ SummaryMatrix.jsx

pages/              # Vistas completas
├─ Concentrado.jsx
└─ Resumen.jsx
```

### Custom Hooks

```javascript
useFetchVehicles()   // Fetch con paginación
useFilters()          // Gestión de filtros
useAggregation()      // Datos agregados
```

### State Management

Actualmente usa estado local con hooks. Zustand listo para expansión.

```javascript
// Futura integración con Zustand
const useVehicleStore = create((set) => ({
  vehicles: [],
  filters: {},
  setVehicles: (data) => set({ vehicles: data }),
  setFilters: (filters) => set({ filters })
}));
```

## Flujo de Datos (ETL)

```
API Telemetría
     │
     ▼
ETLService.consume_telemetry_endpoint()
     │
     ▼
apply_vin_filter()  [Keep only "SZ" VINs]
     │
     ▼
validate_data()     [Check integrity]
     │
     ▼
batch_process()
  ├─ GeofenceService.is_in_geofence()
  ├─ DisconnectionRules.classify_disconnection()
  └─ Create Register + Bitacora
     │
     ▼
Save to Database
     │
     ▼
Frontend fetch via /api/v1/registers/
     │
     ▼
Render VehicleTable & SummaryMatrix
```

## Patrones Utilizados

### 1. Service Layer Pattern

Toda lógica de negocio en servicios, no en views.

```python
# ✓ Correcto
@api_view(['GET'])
def get_vehicles(request):
    service = VehicleService()
    vehicles = service.get_active_vehicles()
    return Response(vehicles)

# ✗ Incorrecto (lógica en view)
@api_view(['GET'])
def get_vehicles(request):
    vehicles = Vehicle.objects.filter(is_active=True)
    # mucha lógica aquí...
```

### 2. Dependency Injection

Pasar dependencias como parámetros.

```python
def batch_process(self, vehicles, geofence_service, business_rules):
    # Services inyectados como parámetros
    for vehicle in vehicles:
        in_geofence = geofence_service.is_in_geofence(...)
        type = business_rules.classify_disconnection(...)
```

### 3. Composition over Inheritance

Favorecer composición sobre herencia.

```python
# ✓ Correcto - Composición
class ReportGenerator:
    def __init__(self, analytics_service, export_service):
        self.analytics = analytics_service
        self.export = export_service

# ✗ Incorrecto - Herencia excesiva
class ReportGenerator(AnalyticsService, ExportService):
    pass
```

### 4. Factory Pattern

Para crear instancias complejas.

```python
class ServiceFactory:
    @staticmethod
    def create_etl_service():
        return ETLService()
    
    @staticmethod
    def create_geofence_service():
        return GeofenceService()
```

## Consideraciones de Seguridad

### Backend

- **SQL Injection**: ORM Django (parameterización automática)
- **XSS**: DRF serializers con validación
- **CSRF**: Django middleware + CSRF tokens
- **Auth**: JWT con refresh tokens seguros
- **Rate Limiting**: Throttling de DRF
- **CORS**: Whitelist de dominios
- **Datos Sensibles**: No en logs, usar masking
- **Contraseñas**: Hashing con Django auth

### Frontend

- **XSS**: React escapa automáticamente
- **CSRF**: Token en headers
- **Storage**: JWT en sessionStorage (no localStorage)
- **Validación**: Cliente Y servidor
- **Errores**: No exponer detalles técnicos

## Escalabilidad

### Horizontal Scaling

```
Load Balancer
├─ API Server 1
├─ API Server 2
└─ API Server 3
     └─ Shared Database (PostgreSQL)
     └─ Redis (Cache/Sessions)
```

### Caching

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # 5 minutos
@api_view(['GET'])
def get_summary_matrix(request):
    pass
```

### Async Tasks

```python
from celery import shared_task

@shared_task
def process_etl_batch(batch_id):
    # Procesamiento async de lotes grandes
    pass
```

## Testing

### Unit Tests

```python
class GeofenceServiceTest(TestCase):
    def test_point_in_polygon(self):
        service = GeofenceService()
        result = service.is_in_geofence(25.68, -100.31, geofence)
        self.assertTrue(result)
```

### Integration Tests

```python
class ETLServiceTest(TestCase):
    def test_consume_and_process(self):
        # Test flujo completo ETL
        pass
```

## Monitoreo y Logging

### Logging Estructurado

```python
logger = logging.getLogger('services')
logger.info(f"Procesando {len(vehicles)} vehículos",
    extra={
        'batch_id': batch_id,
        'duration_ms': duration
    }
)
```

### Métricas

- Tasa de desconexiones
- Tiempo de resolución promedio
- Cobertura de geocercas
- Latencia de API

## Roadmap Futuro

1. **v0.2.0**: Integración con WebSockets (real-time updates)
2. **v0.3.0**: Exportación a BigQuery para analítica
3. **v0.4.0**: Dashboard ejecutivo con gráficos
4. **v0.5.0**: Predicción de desconexiones (ML)
5. **v1.0.0**: Release production-ready

---

**Documento actualizado**: 27/01/2025
**Versión**: 0.1.0-alpha
