# Checklist de Migración - Phase 3

## 🎯 Antes de migrar

### Verificaciones previas
- [ ] Backup de base de datos actual (`mysqldump` o `pg_dump`)
- [ ] Entorno de desarrollo limpio
- [ ] Todos los cambios committed en git
- [ ] No hay cambios sin guardar

### Verificar settings.py
```python
# settings.py debe tener:
EXTERNAL_ENDPOINT_URL = os.getenv('EXTERNAL_ENDPOINT_URL')
EXTERNAL_ENDPOINT_API_KEY = os.getenv('EXTERNAL_ENDPOINT_API_KEY')
```

### Variables de entorno
```bash
# .env o en deployment
export EXTERNAL_ENDPOINT_URL="https://api.example.com"
export EXTERNAL_ENDPOINT_API_KEY="your-api-key"
```

## 🔄 Pasos de Migración

### Paso 1: Crear migraciones Django

```bash
cd backend

# Crear migraciones para cambios de modelos
python manage.py makemigrations vehicles
python manage.py makemigrations organization
python manage.py makemigrations registers

# Verificar migraciones generadas
python manage.py showmigrations

# Ver el SQL que se ejecutará (importante revisar)
python manage.py sqlmigrate vehicles 0002  # Cambiar número según corresponda
python manage.py sqlmigrate organization 0002
python manage.py sqlmigrate registers 0002
```

**Notas importantes:**
- Las migraciones pueden requerir `--no-input` si hay cambios en modelos con FK
- Revisar carefully el SQL generado para verificar que no se perderán datos importantes

### Paso 2: Backup previo a migración

```bash
# MySQL
mysqldump -u root -p desconexiones_s13_db > backup_phase3_$(date +%Y%m%d_%H%M%S).sql

# PostgreSQL
pg_dump desconexiones_s13_db > backup_phase3_$(date +%Y%m%d_%H%M%S).sql

# SQLite (desarrollo)
cp db.sqlite3 db.sqlite3.backup_phase3
```

### Paso 3: Ejecutar migraciones

```bash
# Aplicar migraciones
python manage.py migrate

# Verificar que completaron sin errores
python manage.py showmigrations
# Debería mostrar [X] en todas las migraciones

# Verificar integridad de datos
python manage.py check
```

### Paso 4: Verificar estado de BD

```bash
# Conectar a DB
python manage.py dbshell

# MySQL
SELECT * FROM vehicles_vehicle LIMIT 1;
SELECT * FROM vehicles_geofence LIMIT 1;
SELECT * FROM registers_register LIMIT 1;
SELECT * FROM registers_bitacora LIMIT 1;

# PostgreSQL
\dt  -- List all tables
SELECT COUNT(*) FROM vehicles_vehicle;
```

### Paso 5: Cargar datos iniciales (si aplica)

```bash
# Si hay fixtures
python manage.py loaddata fixtures/initial_data.json

# O importar datos del endpoint
python manage.py shell
```

En el shell:
```python
from apps.vehicles.services import VehicleETLService
from core.http_client import EndpointClient

with EndpointClient() as client:
    response = client.get_vehicles(page=1, page_size=100)
    result = VehicleETLService.import_vehicle_data(response['data'])
    print(f"Importados: {result['created']}")
```

### Paso 6: Verificaciones post-migración

```bash
# Ejecutar tests
python manage.py test

# Verificar que el servidor inicia
python manage.py runserver

# Probar endpoints principales
curl http://localhost:8000/api/vehicles/
curl http://localhost:8000/api/registers/
```

## 📊 Cambios esperados en DB

### Modelos removidos o simplificados

#### Geofence
- ❌ Eliminados: polygon_coordinates, circle_coordinates, layer_name, type
- ✅ Mantenido: geo_name (unique), created_at, updated_at

#### Vehicle
- ❌ Eliminados: is_active, is_connected, latitude (Decimal), longitude (Decimal)
- ✅ Mantenido: vehicle_id, vin, group_id, distribuidor_id, geofence_id, contrato_id
- ✅ Cambiado: last_latitude, last_longitude (a FloatField)

#### Register
- ❌ Eliminados: disconnection_type, problem_type, final_status enums, responsible_id, comment, created_by, speed
- ✅ Mantenido: vehicle_id, report_date, platform_client, distribuidor_id, last_connection, problem, type, last_status

#### Bitacora
- ❌ Eliminados: action (enum), field_changed, old_value, new_value, ip_address, user_agent
- ✅ Mantenido: register_id, user_id, comentario, created_at

#### User
- ❌ Eliminados: role, phone, last_login_ip, is_active
- ✅ Mantenido: username, email (now user_name, user_email), password

#### Distribuidor
- ❌ Eliminados: contact_email, contact_phone, address, is_active
- ✅ Mantenido: distribuidor_id, distribuidor_name

#### Client
- ❌ Eliminados: contact_person, contact_email, contact_phone, is_active
- ✅ Mantenido: client_id, client_description

#### Group
- ❌ Eliminados: vehicle_count, is_active, unique_together, update_vehicle_count method
- ✅ Mantenido: group_id, group_description, client_id

## ⚠️ Posibles Problemas y Soluciones

### Problema 1: Foreign Key constraint violation

**Error:**
```
Error: Cannot delete or update a parent row: a foreign key constraint fails
```

**Solución:**
```bash
# Temporalmente deshabilitar FK (MySQL)
SET FOREIGN_KEY_CHECKS=0;
# Ejecutar migration
python manage.py migrate
# Re-habilitar FK
SET FOREIGN_KEY_CHECKS=1;
```

### Problema 2: Columna con data pero Django espera vacía

**Error:**
```
You are trying to change the null constraint on ... to null=False but the column is not NULL.
```

**Solución en settings para migration:**
```python
# En migration file
operations = [
    migrations.RunSQL(
        "UPDATE vehicles_vehicle SET new_field = 'default' WHERE new_field IS NULL;",
        reverse_sql="UPDATE vehicles_vehicle SET new_field = NULL;"
    ),
    migrations.AlterField(
        model_name='vehicle',
        name='new_field',
        field=models.CharField(max_length=255, null=False),
    ),
]
```

### Problema 3: Índices duplicados

**Solución:**
```bash
# PostgreSQL
DROP INDEX IF EXISTS idx_vehicle_id;

# MySQL
ALTER TABLE vehicles_vehicle DROP INDEX idx_vehicle_id;

# Luego ejecutar migrate
python manage.py migrate
```

## 🔍 Validación Post-Migración

### Script de validación

```python
# backend/scripts/validate_migration.py

from apps.vehicles.models import Vehicle, Geofence, Contrato
from apps.registers.models import Register, Bitacora
from apps.organization.models import User, Distribuidor, Client, Group

def validate():
    print("Validando migración...")
    
    # Verificar tablas existen
    tables = {
        'vehicles_vehicle': Vehicle,
        'vehicles_geofence': Geofence,
        'vehicles_contrato': Contrato,
        'registers_register': Register,
        'registers_bitacora': Bitacora,
        'organization_user': User,
        'organization_distribuidor': Distribuidor,
        'organization_client': Client,
        'organization_group': Group,
    }
    
    for table_name, model in tables.items():
        try:
            count = model.objects.count()
            print(f"✓ {table_name}: {count} registros")
        except Exception as e:
            print(f"✗ {table_name}: ERROR - {e}")
    
    # Verificar campos específicos
    print("\nVerificando campos...")
    
    vehicle = Vehicle.objects.first()
    if vehicle:
        assert hasattr(vehicle, 'last_latitude'), "Vehicle sin last_latitude"
        assert hasattr(vehicle, 'last_longitude'), "Vehicle sin last_longitude"
        print("✓ Vehicle fields OK")
    
    register = Register.objects.first()
    if register:
        assert hasattr(register, 'problem'), "Register sin problem"
        assert hasattr(register, 'type'), "Register sin type"
        print("✓ Register fields OK")
    
    # Verificar relaciones
    print("\nVerificando relaciones...")
    
    if Vehicle.objects.exists():
        vehicle = Vehicle.objects.select_related('group', 'distribuidor').first()
        assert vehicle.group is not None, "Vehicle sin group"
        assert vehicle.distribuidor is not None, "Vehicle sin distribuidor"
        print("✓ Vehicle relationships OK")
    
    print("\n✅ Validación completada exitosamente")

if __name__ == '__main__':
    validate()
```

Ejecutar:
```bash
python manage.py shell < scripts/validate_migration.py
```

## 🚀 Post-Migración

### Actualizar documentación

- [ ] Actualizar ERD.md con nuevos diagramas
- [ ] Actualizar API_ENDPOINTS.md si cambió algo
- [ ] Actualizar README.md si hay cambios en setup

### Comunicar cambios al equipo

```markdown
## Migration Phase 3 - Completed ✅

### Changes
- Simplified database schema
- Removed geospatial processing
- New ETL services for data import

### Breaking Changes
- None for API consumers (serializers adapted)
- Database schema changed (migration required)

### New Features
- VehicleETLService for endpoint data import
- RegisterService for disconnection management
- EndpointClient for HTTP communication

### Testing
- All endpoints tested ✅
- Services tested ✅
- Migration validated ✅
```

### Monitoreo

```python
# Configurar alertas
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/migration.log',
        },
    },
    'loggers': {
        'apps.vehicles.services': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        'apps.registers.services': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

## ✅ Checklist Final

### Antes de go-live en producción
- [ ] Migraciones testeadas en staging
- [ ] Backup de producción realizado
- [ ] Rollback plan definido
- [ ] Team notificado
- [ ] Maintenance window programado
- [ ] Monitoring activado
- [ ] Alertas configuradas
- [ ] Logs monitoreados
- [ ] Tests en producción ejecutados (health checks)
- [ ] Performance baseline medido

### Rollback (si algo sale mal)

```bash
# Revertir migrations
python manage.py migrate vehicles 0001  # Cambiar número según corresponda
python manage.py migrate organization 0001
python manage.py migrate registers 0001

# Restaurar DB
# MySQL
mysql -u root -p desconexiones_s13_db < backup_phase3_YYYYMMDD_HHMMSS.sql

# PostgreSQL
psql desconexiones_s13_db < backup_phase3_YYYYMMDD_HHMMSS.sql
```

## 📞 Soporte

Si hay problemas durante la migración:
1. Revisar logs: `tail -f /var/log/django/django.log`
2. Verificar database integrity
3. Ejecutar rollback si es necesario
4. Abrir issue en repo con detalles del error

---

**Última actualización:** 2024-01-15  
**Versión:** Phase 3 - Database Refactoring  
**Responsable:** Development Team
