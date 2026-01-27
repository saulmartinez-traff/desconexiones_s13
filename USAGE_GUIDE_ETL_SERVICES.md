# Guía de Uso - Servicios ETL y Cliente HTTP

## 📍 Descripción General

Este documento proporciona ejemplos de uso para los servicios creados en Phase 3:
- `VehicleETLService` - Importar datos de vehículos desde endpoint
- `RegisterService` - Gestionar registros de desconexiones
- `EndpointClient` - Cliente HTTP para consumir el endpoint externo

## 🚗 VehicleETLService

### Ubicación
```
backend/apps/vehicles/services.py
```

### Ejemplo 1: Importar datos de vehículos

```python
from apps.vehicles.services import VehicleETLService
from core.http_client import EndpointClient

# 1. Obtener datos del endpoint
with EndpointClient() as client:
    response = client.get_vehicles(page=1, page_size=100)
    vehicles_data = response['data']

# 2. Importar a la base de datos
result = VehicleETLService.import_vehicle_data(vehicles_data)

print(f"Vehículos importados: {result['created']}")
print(f"Vehículos actualizados: {result['updated']}")
print(f"Errores: {result['failed']}")
if result['errors']:
    for error in result['errors']:
        print(f"  - {error}")
```

### Ejemplo 2: Sincronizar todos los vehículos

```python
from apps.vehicles.services import VehicleETLService
from core.http_client import EndpointClient

def sync_all_vehicles():
    """Sincronizar todos los vehículos paginando el endpoint"""
    total_synced = {"created": 0, "updated": 0, "failed": 0}
    
    page = 1
    total_pages = 1
    
    with EndpointClient() as client:
        while page <= total_pages:
            response = client.get_vehicles(page=page, page_size=100)
            
            result = VehicleETLService.import_vehicle_data(response['data'])
            
            # Acumular resultados
            for key in total_synced:
                total_synced[key] += result[key]
            
            total_pages = response['total_pages']
            page += 1
    
    return total_synced

# Ejecutar sincronización
result = sync_all_vehicles()
print(f"Total: Created={result['created']}, Updated={result['updated']}, Failed={result['failed']}")
```

### Estructura esperada de endpoint

```json
{
  "data": [
    {
      "vehicle_id": 12345,
      "vin": "1HGCM82633A123456",
      "license_nmbr": "ABC1234",
      "status": 1,
      "last_communication_time": "2024-01-15T14:30:00Z",
      "latitude": 25.2048,
      "longitude": -77.3364,
      "speed": 45.5,
      "client_id": 1,
      "client_name": "BAJAS COPPEL",
      "group_id": 101,
      "group_name": "Grupo A",
      "geofence_name": "Base Centro"
    }
  ],
  "total": 5000,
  "page": 1,
  "page_size": 100,
  "total_pages": 50
}
```

## 📋 RegisterService

### Ubicación
```
backend/apps/registers/services.py
```

### Ejemplo 1: Crear un registro de desconexión

```python
from apps.registers.services import RegisterService
from apps.vehicles.models import Vehicle

# Obtener vehículo
vehicle = Vehicle.objects.get(vehicle_id=12345)

# Crear registro
register = RegisterService.create_register(
    vehicle=vehicle,
    report_date='2024-01-15',
    platform_client='API',
    distribuidor=vehicle.distribuidor,
    last_connection=timezone.now() - timedelta(hours=2),
    problem='Vehículo sin conexión por 2 horas',
    type_='DESCONEXION',
    last_status='OFFLINE',
    comentario='Detectado automáticamente'
)

print(f"Registro creado: {register.id}")
```

### Ejemplo 2: Actualizar un registro con auditoría

```python
from apps.registers.services import RegisterService
from apps.registers.models import Register

# Obtener registro
register = Register.objects.get(id=1)

# Actualizar con tracking automático
RegisterService.update_register(
    register=register,
    problem='Vehículo sin conexión por 3 horas',
    last_status='OFFLINE_3H',
    comentario='Actualización de estado'
)

print(f"Registro actualizado. Cambios registrados en bitacora.")
```

### Ejemplo 3: Detectar desconexiones automáticamente

```python
from apps.registers.services import RegisterService
from core.http_client import EndpointClient

# Obtener datos del endpoint
with EndpointClient() as client:
    response = client.get_vehicles(page=1, page_size=100)
    vehicles_data = response['data']

# Detectar desconexiones
new_registers = RegisterService.detect_disconnections(vehicles_data)

print(f"Desconexiones detectadas: {len(new_registers)}")
for register in new_registers:
    print(f"  - {register.vehicle.vin}: {register.problem}")
```

**Nota**: `detect_disconnections` utiliza un umbral de 5 minutos de inactividad. Puede ajustarse en el código.

### Ejemplo 4: Obtener registros recientes

```python
from apps.registers.services import RegisterService

# Últimos 7 días
recent = RegisterService.get_recent_disconnections(days=7)

for register in recent:
    print(f"{register.report_date}: {register.vehicle.vin} - {register.problem}")

# Personalizados
from datetime import timedelta
recent_3days = RegisterService.get_recent_disconnections(days=3)
```

### Ejemplo 5: Obtener desconexiones de un vehículo

```python
from apps.registers.services import RegisterService
from apps.vehicles.models import Vehicle

# Obtener vehículo
vehicle = Vehicle.objects.get(vehicle_id=12345)

# Obtener todos sus registros
registers = RegisterService.get_vehicle_disconnections(vehicle)

print(f"Registros de {vehicle.vin}: {registers.count()}")
for register in registers:
    print(f"  - {register.report_date}: {register.type}")
```

### Ejemplo 6: Acceder a la auditoría (Bitacora)

```python
from apps.registers.models import Register

# Obtener registro
register = Register.objects.get(id=1)

# Obtener historial de cambios
bitacora_entries = register.bitacora_entries.all()

for entry in bitacora_entries:
    user_info = entry.user.user_name if entry.user else "Sistema"
    print(f"{entry.created_at} - {user_info}: {entry.comentario}")
```

## 🌐 EndpointClient

### Ubicación
```
backend/core/http_client.py
```

### Configuración requerida en settings.py

```python
# settings.py
EXTERNAL_ENDPOINT_URL = os.getenv('EXTERNAL_ENDPOINT_URL', 'https://api.example.com')
EXTERNAL_ENDPOINT_API_KEY = os.getenv('EXTERNAL_ENDPOINT_API_KEY', '')
```

### Ejemplo 1: Usar el cliente con context manager (recomendado)

```python
from core.http_client import EndpointClient

with EndpointClient() as client:
    # Obtener vehículos con paginación
    response = client.get_vehicles(page=1, page_size=50)
    
    print(f"Total vehículos: {response['total']}")
    print(f"Página: {response['page']} de {response['total_pages']}")
    
    for vehicle in response['data']:
        print(f"  - {vehicle['vin']}: {vehicle['client_name']}")
```

### Ejemplo 2: Usar el cliente sin context manager

```python
from core.http_client import EndpointClient

client = EndpointClient(timeout=60)

try:
    # Obtener todos los vehículos (sin filtros)
    response = client.get_vehicles(page_size=100)
    
    # Procesar respuesta
    for vehicle in response['data']:
        print(vehicle['vehicle_id'])

finally:
    client.close()  # Importante: cerrar sesión
```

### Ejemplo 3: Obtener un vehículo específico

```python
from core.http_client import EndpointClient

with EndpointClient() as client:
    vehicle = client.get_vehicle_by_id(12345)
    
    print(f"VIN: {vehicle['vin']}")
    print(f"Ubicación: {vehicle['latitude']}, {vehicle['longitude']}")
```

### Ejemplo 4: Manejar excepciones

```python
from core.http_client import EndpointClient, EndpointConnectionError, EndpointResponseError

try:
    with EndpointClient() as client:
        vehicles = client.get_vehicles()
except EndpointConnectionError as e:
    print(f"Error de conexión: {e}")
    # Reintentar después
except EndpointResponseError as e:
    print(f"Respuesta inválida del endpoint: {e}")
    # Registrar error
except Exception as e:
    print(f"Error inesperado: {e}")
```

## 🔄 Flujo de Integración Completo

### Opción 1: Sincronización manual

```python
from apps.vehicles.services import VehicleETLService
from apps.registers.services import RegisterService
from core.http_client import EndpointClient

def full_sync():
    """Sincronizar vehículos y detectar desconexiones"""
    
    with EndpointClient() as client:
        # Obtener datos
        response = client.get_vehicles(page=1, page_size=100)
        vehicles_data = response['data']
        
        # 1. Importar vehículos
        import_result = VehicleETLService.import_vehicle_data(vehicles_data)
        print(f"Vehículos importados: {import_result['created']} creados, {import_result['updated']} actualizados")
        
        # 2. Detectar desconexiones
        new_registers = RegisterService.detect_disconnections(vehicles_data)
        print(f"Desconexiones detectadas: {len(new_registers)}")
    
    return {
        "vehicles": import_result,
        "disconnections": len(new_registers)
    }

# Ejecutar
result = full_sync()
```

### Opción 2: Con Django Management Command

```python
# backend/apps/vehicles/management/commands/sync_vehicles.py

from django.core.management.base import BaseCommand
from apps.vehicles.services import VehicleETLService
from apps.registers.services import RegisterService
from core.http_client import EndpointClient

class Command(BaseCommand):
    help = 'Sincronizar vehículos y detectar desconexiones'
    
    def handle(self, *args, **options):
        with EndpointClient() as client:
            page = 1
            while True:
                response = client.get_vehicles(page=page, page_size=100)
                
                # Importar
                result = VehicleETLService.import_vehicle_data(response['data'])
                self.stdout.write(f"Página {page}: {result['created']} creados, {result['updated']} actualizados")
                
                # Detectar
                RegisterService.detect_disconnections(response['data'])
                
                if page >= response['total_pages']:
                    break
                page += 1
```

Ejecutar con:
```bash
python manage.py sync_vehicles
```

### Opción 3: Con Celery (recomendado para producción)

```python
# backend/apps/vehicles/tasks.py

from celery import shared_task
from apps.vehicles.services import VehicleETLService
from apps.registers.services import RegisterService
from core.http_client import EndpointClient

@shared_task
def sync_vehicles_task():
    """Task de Celery para sincronizar vehículos"""
    with EndpointClient() as client:
        response = client.get_vehicles(page=1, page_size=100)
        
        result = VehicleETLService.import_vehicle_data(response['data'])
        RegisterService.detect_disconnections(response['data'])
        
        return result

@shared_task
def detect_disconnections_task():
    """Task de Celery para detectar desconexiones"""
    with EndpointClient() as client:
        response = client.get_vehicles(page=1, page_size=100)
        new_registers = RegisterService.detect_disconnections(response['data'])
        
        return {
            "disconnections_detected": len(new_registers)
        }
```

En `celery.py`:
```python
# Ejecutar sync cada hora
app.conf.beat_schedule = {
    'sync-vehicles': {
        'task': 'apps.vehicles.tasks.sync_vehicles_task',
        'schedule': crontab(minute=0),  # Cada hora
    },
    'detect-disconnections': {
        'task': 'apps.vehicles.tasks.detect_disconnections_task',
        'schedule': crontab(minute='*/5'),  # Cada 5 minutos
    },
}
```

## 🐛 Debugging

### Ver logs

```python
import logging

logger = logging.getLogger('apps.vehicles.services')
logger.setLevel(logging.DEBUG)

# Los logs incluyen:
# - Importaciones completadas
# - Errores de procesamiento
# - Cambios en bitacora
```

### Inspeccionar base de datos

```python
from apps.vehicles.models import Vehicle
from apps.registers.models import Register
from apps.organization.models import Distribuidor, Group

# Ver vehículos importados
Vehicle.objects.all().count()
Vehicle.objects.filter(last_connection__isnull=False)

# Ver registros de desconexión
Register.objects.all().count()
Register.objects.filter(type='DESCONEXION')

# Ver auditoría
register = Register.objects.first()
register.bitacora_entries.all()
```

## ✅ Testing

```python
# backend/tests/test_etl_services.py

from django.test import TestCase
from apps.vehicles.services import VehicleETLService

class VehicleETLServiceTest(TestCase):
    def test_import_vehicle_data(self):
        endpoint_data = [{
            'vehicle_id': 1,
            'vin': 'VIN123456789ABCD',
            'latitude': 25.2048,
            'longitude': -77.3364,
            'client_id': 1,
            'client_name': 'Test Client',
            'group_id': 1,
            'group_name': 'Test Group',
            'geofence_name': 'Test Geofence',
            'last_communication_time': '2024-01-15T14:30:00Z'
        }]
        
        result = VehicleETLService.import_vehicle_data(endpoint_data)
        
        self.assertEqual(result['created'], 1)
        self.assertEqual(result['updated'], 0)
        self.assertEqual(result['failed'], 0)
```

## 📞 Soporte

- Para errores de conexión al endpoint, verificar:
  - `EXTERNAL_ENDPOINT_URL` en settings
  - `EXTERNAL_ENDPOINT_API_KEY` en environment
  - Conectividad de red
  
- Para errores de importación, verificar:
  - Que los datos del endpoint tengan los campos obligatorios
  - Que los valores sean válidos (ej: coordenadas numéricas)
  
- Para auditoría, verificar:
  - `Bitacora` model para historial de cambios
  - Logs de la aplicación en `/var/log/django/`
