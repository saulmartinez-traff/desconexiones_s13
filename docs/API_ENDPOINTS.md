# 🔌 API Endpoints - Guía Completa

**Versión:** 1.0  
**Base URL:** `http://localhost:8000/api`  
**Autenticación:** JWT Bearer Token

---

## 🔐 Autenticación

### 1. Obtener Token (Login)

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. Refrescar Token

```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

### 3. Verificar Token

```bash
curl -X POST http://localhost:8000/api/auth/token/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

**Headers para endpoints protegidos:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## 👥 Organization Endpoints

### Users

#### Lista todos los usuarios
```bash
curl -X GET http://localhost:8000/api/v1/organization/users/ \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json"
```

**Query Parameters:**
- `role` (ADMIN, MANAGER, OPERATOR, VIEWER)
- `is_active` (true/false)
- `search` (username, email, first_name, last_name)

**Ejemplo:**
```bash
curl -X GET "http://localhost:8000/api/v1/organization/users/?role=MANAGER&is_active=true&search=juan" \
  -H "Authorization: Bearer {TOKEN}"
```

#### Mi perfil
```bash
curl -X GET http://localhost:8000/api/v1/organization/users/me/ \
  -H "Authorization: Bearer {TOKEN}"
```

#### Crear usuario
```bash
curl -X POST http://localhost:8000/api/v1/organization/users/ \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "juan_perez",
    "email": "juan@example.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "password": "SecurePass123!",
    "role": "OPERATOR",
    "phone": "+52 5555555555"
  }'
```

#### Actualizar usuario
```bash
curl -X PATCH http://localhost:8000/api/v1/organization/users/{id}/ \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Juan Carlos",
    "phone": "+52 5555555556"
  }'
```

#### Cambiar contraseña
```bash
curl -X POST http://localhost:8000/api/v1/organization/users/{id}/set_password/ \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "NewSecurePass123!"
  }'
```

### Distribuidores

#### Lista
```bash
curl -X GET http://localhost:8000/api/v1/organization/distribuidores/ \
  -H "Authorization: Bearer {TOKEN}"
```

**Query Parameters:**
- `is_active` (true/false)
- `search` (name, distribuidor_id, contact_email)

#### Crear
```bash
curl -X POST http://localhost:8000/api/v1/organization/distribuidores/ \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "distribuidor_id": "DIST-001",
    "name": "Distribuidora Nacional",
    "contact_name": "Carlos Mendez",
    "contact_email": "carlos@distribuidora.com",
    "contact_phone": "+52 5555555550",
    "is_active": true
  }'
```

#### Activar/Desactivar
```bash
curl -X POST http://localhost:8000/api/v1/organization/distribuidores/{id}/activate/ \
  -H "Authorization: Bearer {TOKEN}"

curl -X POST http://localhost:8000/api/v1/organization/distribuidores/{id}/deactivate/ \
  -H "Authorization: Bearer {TOKEN}"
```

### Clientes

#### Lista
```bash
curl -X GET http://localhost:8000/api/v1/organization/clients/ \
  -H "Authorization: Bearer {TOKEN}"
```

**Query Parameters:**
- `distribuidor` (distribuidor_id)
- `is_active` (true/false)
- `search` (name, client_id, contact_email)

#### Crear
```bash
curl -X POST http://localhost:8000/api/v1/organization/clients/ \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "CLI-001",
    "distribuidor": 1,
    "name": "Transporte del Centro",
    "description": "Flota de transporte",
    "contact_name": "Roberto García",
    "contact_email": "roberto@transporte.com",
    "contact_phone": "+52 5555555551",
    "is_active": true
  }'
```

### Grupos

#### Lista
```bash
curl -X GET http://localhost:8000/api/v1/organization/groups/ \
  -H "Authorization: Bearer {TOKEN}"
```

**Query Parameters:**
- `client` (client_id)
- `is_active` (true/false)
- `search` (name, group_id, client__name)

#### Detalle (con relaciones anidadas)
```bash
curl -X GET http://localhost:8000/api/v1/organization/groups/{id}/ \
  -H "Authorization: Bearer {TOKEN}"
```

#### Crear
```bash
curl -X POST http://localhost:8000/api/v1/organization/groups/ \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "group_id": "GRP-001",
    "client": 1,
    "name": "Flota Zona Centro",
    "description": "Vehículos en zona metropolitana",
    "is_active": true
  }'
```

#### Contar vehículos
```bash
curl -X GET http://localhost:8000/api/v1/organization/groups/{id}/vehicle_count/ \
  -H "Authorization: Bearer {TOKEN}"
```

---

## 🚗 Vehicles Endpoints

### Vehículos

#### Lista con filtros
```bash
curl -X GET "http://localhost:8000/api/v1/vehicles/vehicles/?group=1&is_connected=true&search=KL5CM67" \
  -H "Authorization: Bearer {TOKEN}"
```

**Query Parameters:**
- `group` (group_id)
- `distribuidor` (distribuidor_id)
- `geofence` (geofence_id)
- `is_connected` (true/false)
- `search` (vin, vehicle_id)
- `ordering` (vehicle_id, vin, updated_at)

#### Crear vehículo
```bash
curl -X POST http://localhost:8000/api/v1/vehicles/vehicles/ \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "VEH-001",
    "vin": "WBADO8104K0909217",
    "latitude": 25.6866,
    "longitude": -100.3161,
    "group": 1,
    "distribuidor": 1,
    "geofence": 1,
    "is_connected": true
  }'
```

#### Actualizar ubicación
```bash
curl -X POST http://localhost:8000/api/v1/vehicles/vehicles/{id}/update_location/ \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 25.6900,
    "longitude": -100.3200
  }'
```

#### Marcar como conectado/desconectado
```bash
curl -X POST http://localhost:8000/api/v1/vehicles/vehicles/{id}/connect/ \
  -H "Authorization: Bearer {TOKEN}"

curl -X POST http://localhost:8000/api/v1/vehicles/vehicles/{id}/disconnect/ \
  -H "Authorization: Bearer {TOKEN}"
```

#### Verificar estado de geocerca
```bash
curl -X GET http://localhost:8000/api/v1/vehicles/vehicles/{id}/geofence_status/ \
  -H "Authorization: Bearer {TOKEN}"
```

### Geocercas

#### Lista
```bash
curl -X GET "http://localhost:8000/api/v1/vehicles/geofences/?type=POLYGON&is_active=true" \
  -H "Authorization: Bearer {TOKEN}"
```

#### Crear geocerca (polígono)
```bash
curl -X POST http://localhost:8000/api/v1/vehicles/geofences/ \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Centro Logístico",
    "type": "POLYGON",
    "coordinates": {
      "polygon": [
        [25.6800, -100.3100],
        [25.6900, -100.3100],
        [25.6900, -100.3200],
        [25.6800, -100.3200]
      ]
    },
    "description": "Zona de almacén central",
    "is_active": true
  }'
```

#### Crear geocerca (círculo)
```bash
curl -X POST http://localhost:8000/api/v1/vehicles/geofences/ \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Oficina Principal",
    "type": "CIRCLE",
    "coordinates": {
      "center": [25.6866, -100.3161],
      "radius_km": 5.0
    },
    "description": "Radio 5km alrededor de oficina",
    "is_active": true
  }'
```

#### Verificar punto en geocerca
```bash
curl -X POST http://localhost:8000/api/v1/vehicles/geofences/{id}/check_point/ \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 25.6875,
    "longitude": -100.3180
  }'
```

**Response:**
```json
{
  "geofence_id": 1,
  "point": {
    "latitude": 25.6875,
    "longitude": -100.3180
  },
  "is_inside": true
}
```

### Contratos

#### Lista
```bash
curl -X GET "http://localhost:8000/api/v1/vehicles/contratos/?is_active=true" \
  -H "Authorization: Bearer {TOKEN}"
```

#### Crear contrato
```bash
curl -X POST http://localhost:8000/api/v1/vehicles/contratos/ \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle": 1,
    "contract_id": "CONT-001",
    "vin": "WBADO8104K0909217",
    "start_date": "2025-01-27",
    "end_date": "2026-01-27",
    "is_active": true
  }'
```

---

## 📋 Registers Endpoints

### Desconexiones

#### Lista con filtros
```bash
curl -X GET "http://localhost:8000/api/v1/registers/registers/?disconnection_type=ROUTE&final_status=PENDING&search=KL5CM67" \
  -H "Authorization: Bearer {TOKEN}"
```

**Query Parameters:**
- `vehicle` (vehicle_id)
- `disconnection_type` (ROUTE, BASE, UNKNOWN)
- `problem_type` (MALFUNCTION, CONNECTION_LOSS, LOW_BATTERY, HARDWARE_FAILURE)
- `final_status` (WORKSHOP, BASE, RESOLVED, PENDING)
- `responsible` (user_id)
- `search` (vehicle__vin, vehicle__vehicle_id, problem)
- `ordering` (report_date, created_at, updated_at)

#### Registros editables (< 7 días)
```bash
curl -X GET http://localhost:8000/api/v1/registers/registers/editable/ \
  -H "Authorization: Bearer {TOKEN}"
```

#### Contar por estado
```bash
curl -X GET http://localhost:8000/api/v1/registers/registers/by_status/ \
  -H "Authorization: Bearer {TOKEN}"
```

**Response:**
```json
{
  "WORKSHOP": 5,
  "BASE": 12,
  "RESOLVED": 45,
  "PENDING": 8
}
```

#### Crear desconexión
```bash
curl -X POST http://localhost:8000/api/v1/registers/registers/ \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle": 1,
    "problem": "Pérdida de conexión en zona"
  }'
```

**Response incluye:**
```json
{
  "id": 1,
  "vehicle": {...},
  "report_date": "2025-01-27T10:30:00Z",
  "disconnection_type": "ROUTE",
  "problem_type": "CONNECTION_LOSS",
  "final_status": "PENDING",
  "created_at": "2025-01-27T10:30:00Z"
}
```

#### Asignar responsable
```bash
curl -X POST http://localhost:8000/api/v1/registers/registers/{id}/assign_to/ \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2
  }'
```

#### Agregar comentario
```bash
curl -X POST http://localhost:8000/api/v1/registers/registers/{id}/add_comment/ \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "comment": "Se envió a taller para revisión de hardware"
  }'
```

#### Cambiar estado
```bash
curl -X POST http://localhost:8000/api/v1/registers/registers/{id}/set_status/ \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "final_status": "WORKSHOP"
  }'
```

#### Detalle con auditoría
```bash
curl -X GET http://localhost:8000/api/v1/registers/registers/{id}/ \
  -H "Authorization: Bearer {TOKEN}"
```

**Response incluye bitacora:**
```json
{
  "id": 1,
  "vehicle": {...},
  "final_status": "WORKSHOP",
  "bitacora": [
    {
      "id": 1,
      "action": "CREATE",
      "action_display": "Creado",
      "user": {...},
      "created_at": "2025-01-27T10:30:00Z"
    },
    {
      "id": 2,
      "action": "ASSIGNED",
      "user": {...},
      "field_name": "responsible",
      "old_value": null,
      "new_value": "juan_perez"
    }
  ]
}
```

### Auditoría (Bitacora)

#### Lista de todos los cambios
```bash
curl -X GET "http://localhost:8000/api/v1/registers/bitacora/?action=UPDATE&ordering=-created_at" \
  -H "Authorization: Bearer {TOKEN}"
```

**Query Parameters:**
- `register` (register_id)
- `action` (CREATE, UPDATE, STATUS, COMMENT, ASSIGNED, DELETED)
- `user` (user_id)
- `ordering` (created_at)

#### Auditoría de un registro
```bash
curl -X GET "http://localhost:8000/api/v1/registers/bitacora/?register_id=1" \
  -H "Authorization: Bearer {TOKEN}"
```

---

## 📊 Analytics Endpoints (Próximo)

Endpoints para integración con servicios:
```
GET    /api/v1/analytics/summary-matrix/      # Matriz por fecha/grupo
GET    /api/v1/analytics/group-stats/         # Estadísticas por grupo
GET    /api/v1/analytics/top-vehicles/        # Top vehículos con desconexiones
```

---

## 🔒 Códigos de Estado

| Código | Significado |
|--------|------------|
| 200 | OK - Operación exitosa |
| 201 | Created - Recurso creado |
| 204 | No Content - Eliminado exitosamente |
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - Token faltante o inválido |
| 403 | Forbidden - Permisos insuficientes |
| 404 | Not Found - Recurso no encontrado |
| 500 | Server Error - Error interno |

---

## 📌 Notas

1. **Autenticación requerida**: Todos los endpoints excepto `/api/auth/token/` requieren token JWT
2. **Permisos por rol**: Algunos endpoints solo funcionan con roles específicos
3. **Validaciones**: Los datos se validan en el serializer antes de persistir
4. **Auditoría**: Todos los cambios se registran en Bitacora automáticamente
5. **Paginación**: Se implementará en próxima fase

---

**Documento generado:** 27/01/2025  
**API Version:** 1.0  
**Status:** ✅ COMPLETO
