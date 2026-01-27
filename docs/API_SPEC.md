# API Specification - S13 Desconexiones

## Endpoints Principales

### Authentication

```
POST   /api/auth/token/          Obtener token JWT
POST   /api/auth/token/refresh/  Refrescar token
```

### Vehicles

```
GET    /api/v1/vehicles/                  Listar vehículos (paginado)
GET    /api/v1/vehicles/{id}/             Detalle de vehículo
PATCH  /api/v1/vehicles/{id}/             Actualizar vehículo
GET    /api/v1/vehicles/by-vin/{vin}/     Buscar por VIN
```

**Query Parameters (GET /vehicles/):**
- `page`: Número de página (default: 1)
- `group`: ID del grupo (filtro)
- `distribuidor`: ID del distribuidor (filtro)
- `search`: Búsqueda de VIN (filtro)
- `ordering`: Ordenamiento (-last_connection, vin, etc.)

**Response:**
```json
{
  "count": 250,
  "next": "http://api/vehicles/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "vehicle_id": 12345,
      "vin": "3SZ123456789ABCDE",
      "group": "BAJAS COPPEL",
      "distribuidor": "Distribuidor X",
      "last_connection": "2025-01-27T14:30:00Z",
      "is_connected": true,
      "last_latitude": 25.6867,
      "last_longitude": -100.3161
    }
  ]
}
```

### Registers (Desconexiones)

```
GET    /api/v1/registers/                 Listar registros
POST   /api/v1/registers/                 Crear registro
GET    /api/v1/registers/{id}/            Detalle
PATCH  /api/v1/registers/{id}/            Actualizar registro
```

**POST /registers/ - Crear desconexión:**
```json
{
  "vehicle": 1,
  "problem": "MALFUNCTION",
  "final_status": "PENDING",
  "responsible": null,
  "comment": "Descripción del problema"
}
```

### Analytics

```
GET    /api/v1/analytics/summary-matrix/     Matriz de resumen
GET    /api/v1/analytics/group/{id}/stats/   Estadísticas de grupo
GET    /api/v1/analytics/top-disconnected/   Top vehículos desconectados
```

**Response /summary-matrix/:**
```json
{
  "dates": ["2025-01-20", "2025-01-21"],
  "groups": [
    {
      "group_name": "BAJAS COPPEL",
      "group_id": 1,
      "data": [
        {
          "contract_name": "Contrato A",
          "contract_id": 1,
          "daily_data": [
            {
              "date": "2025-01-20",
              "total": 150,
              "connected": 145,
              "disconnected": 5,
              "percentage_connected": 96.7
            }
          ]
        }
      ]
    }
  ]
}
```

## Error Handling

Códigos HTTP estándar:

- `200`: OK
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Server Error

**Error Response:**
```json
{
  "error": {
    "status": 400,
    "message": "Validación fallida",
    "details": {
      "field": ["Error message"]
    }
  }
}
```

## Rate Limiting

- Usuarios anónimos: 100 requests/hora
- Usuarios autenticados: 1000 requests/hora

Header: `X-RateLimit-Remaining`, `X-RateLimit-Limit`

## Paginación

- Tamaño de página por defecto: 20
- Máximo: 100

Query: `?page=1&page_size=50`

---

*Generado: 27/01/2025*
