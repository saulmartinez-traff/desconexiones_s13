# Setup Guide - S13 Desconexiones

Guía completa para ejecutar el sistema en desarrollo y producción.

## Requisitos Previos

- **Python 3.9+**
- **Node.js 16+ & npm**
- **MySQL 8.0** (desarrollo) o **PostgreSQL 12+** (producción)
- **Git**

## Setup del Backend (Django)

### 1. Clonar y Preparar Ambiente

```bash
# Clonar repositorio
git clone <repo_url>
cd desconexiones_s13/backend

# Crear ambiente virtual
python -m venv venv

# Activar ambiente
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate          # Windows
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar Base de Datos

**Opción A: MySQL (Desarrollo)**

```bash
# Crear base de datos en MySQL
mysql -u root -p
> CREATE DATABASE desconexiones_s13 CHARACTER SET utf8mb4;
> CREATE USER 'dev_user'@'localhost' IDENTIFIED BY 'secure_password';
> GRANT ALL PRIVILEGES ON desconexiones_s13.* TO 'dev_user'@'localhost';
> FLUSH PRIVILEGES;
```

**Opción B: PostgreSQL (Producción)**

```bash
# Crear base de datos
createdb desconexiones_s13
createuser dev_user
psql -c "ALTER USER dev_user WITH PASSWORD 'secure_password';"
psql -c "ALTER ROLE dev_user CREATEDB;"
```

### 4. Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env
# Configurar:
# - DEBUG=True (desarrollo)
# - DB_NAME, DB_USER, DB_PASSWORD
# - DB_ENGINE (mysql o postgresql)
# - SECRET_KEY (generar con: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
```

### 5. Migraciones

```bash
# Crear tabla de logs si no existe
mkdir -p ../logs

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
# username: admin
# email: admin@example.com
# password: (ingresar contraseña segura)

# Cargar datos iniciales (opcional)
python manage.py loaddata fixtures/initial_data.json
```

### 6. Ejecutar Servidor

```bash
# Desarrollo (hot reload)
python manage.py runserver

# Producción (con gunicorn)
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

**Acceso:**
- Admin: http://localhost:8000/admin
- API: http://localhost:8000/api/v1

## Setup del Frontend (React + Vite)

### 1. Instalar Dependencias

```bash
cd frontend
npm install
```

### 2. Variables de Entorno

```bash
# El archivo .env ya viene configurado
# Modificar si el backend está en otra dirección

# .env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_ENV=development
```

### 3. Ejecutar Servidor de Desarrollo

```bash
npm run dev
```

**Acceso:**
- App: http://localhost:5173

### 4. Build para Producción

```bash
npm run build
# Output en: frontend/dist/
```

## Flujo Completo de Desarrollo

### Terminal 1: Backend

```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

### Terminal 2: Frontend

```bash
cd frontend
npm run dev
```

### Terminal 3: Tests (Opcional)

```bash
cd backend
pytest tests/
```

## Crear Datos de Prueba

### Script de Población

```bash
# Desde backend/
python manage.py shell

# En el shell:
from apps.organization.models import Distribuidor, Client, Group
from apps.vehicles.models import Geofence, Vehicle, Contrato

# Crear distribuidor
dist = Distribuidor.objects.create(
    distribuidor_id=1,
    distribuidor_name="Distribuidor Demo",
    contact_email="dist@example.com"
)

# Crear cliente
client = Client.objects.create(
    client_id=1,
    client_description="BAJAS COPPEL"
)

# Crear grupo
group = Group.objects.create(
    group_id=1,
    group_description="BAJAS COPPEL",
    client=client
)

# Crear geocerca (Base)
geofence = Geofence.objects.create(
    geo_id=1,
    geo_name="Base Centro",
    geofence_type="POLYGON",
    polygon_coordinates=[
        [25.68, -100.31],
        [25.69, -100.31],
        [25.69, -100.32],
        [25.68, -100.32],
        [25.68, -100.31]
    ]
)

# Crear contrato
contrato = Contrato.objects.create(
    contrato_id=1,
    vin="3SZ1234567890ABCD",
    contrato="Contrato-001"
)

# Crear vehículo
vehicle = Vehicle.objects.create(
    vehicle_id=1,
    vin="3SZ1234567890ABCD",
    group=group,
    distribuidor=dist,
    geofence=geofence,
    contrato=contrato,
    last_latitude=25.6867,
    last_longitude=-100.3161
)

exit()
```

## Ejecutar Servicios (ETL)

```bash
# En Django shell o crear comando personalizado

from services.etl_service import ETLService
from services.geofence_service import GeofenceService
from services.business_rules import DisconnectionRules

etl = ETLService()
geofence_svc = GeofenceService()
rules = DisconnectionRules()

# Consumir telemetría
vehicles = etl.consume_telemetry_endpoint(max_pages=1)

# Aplicar filtros
filtered = etl.apply_vin_filter(vehicles)

# Validar datos
valid, invalid = etl.validate_data(filtered)

# Procesar en lotes
stats = etl.batch_process(valid, geofence_svc, rules)
print(f"Procesados: {stats}")
```

## Deployment - Producción

### Docker (Opcional)

```bash
# Crear Dockerfile en backend/
# Crear docker-compose.yml

docker-compose up -d
```

### Configuración de Producción

```bash
# Backend
DEBUG=False
ALLOWED_HOSTS=api.desconexiones.com,www.desconexiones.com
DB_ENGINE=django.db.backends.postgresql
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
```

### Nginx + Gunicorn

```nginx
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.desconexiones.com;
    
    client_max_body_size 100M;
    
    location /static/ {
        alias /path/to/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/media/;
    }
    
    location / {
        proxy_pass http://django;
    }
}
```

## Troubleshooting

### Error: "No module named 'django'"

```bash
# Asegurar que el venv está activado
source venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "Connection refused" (BD)

```bash
# Verificar que MySQL/PostgreSQL está corriendo
# Verificar credenciales en .env
# Verificar que la BD existe

mysql -u root -p -e "SHOW DATABASES;"
```

### Error: CORS

```bash
# Verificar CORS_ALLOWED_ORIGINS en settings.py
# Frontend URL debe estar en la lista

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:3000',
]
```

### Node Modules Corrupted

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Monitoreo y Logs

```bash
# Logs en tiempo real
tail -f logs/django.log

# Filtrar por nivel
grep ERROR logs/django.log

# Ver logs de servicios
tail -f logs/services.log
```

## Checklist Pre-Deployment

- [ ] Configurar `.env` con credenciales de producción
- [ ] Ejecutar `python manage.py collectstatic`
- [ ] Ejecutar migraciones: `python manage.py migrate --noinput`
- [ ] Crear superusuario en producción
- [ ] Configurar SSL/HTTPS
- [ ] Configurar backups de BD
- [ ] Configurar monitoreo (Sentry, DataDog, etc.)
- [ ] Pruebas de carga/stress
- [ ] Documentación de API actualizada

---

**Última actualización**: 27/01/2025
**Versión**: 0.1.0-alpha
