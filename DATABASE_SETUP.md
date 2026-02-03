# Guía de Configuración de Base de Datos

## Configuración Inicial

Como estás en un ordenador diferente, necesitas configurar la base de datos desde cero.

### 1. Verificar que MySQL esté instalado y corriendo

```bash
# Verificar versión de MySQL
mysql --version

# Si no está instalado, descarga desde:
# https://dev.mysql.com/downloads/mysql/
```

### 2. Crear la Base de Datos

```bash
# Conectar a MySQL
mysql -u root -p

# Crear base de datos
CREATE DATABASE desconexiones_s13 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Crear usuario (opcional, puedes usar root)
CREATE USER 'desconexiones'@'localhost' IDENTIFIED BY 'tu_password_seguro';
GRANT ALL PRIVILEGES ON desconexiones_s13.* TO 'desconexiones'@'localhost';
FLUSH PRIVILEGES;

# Salir
EXIT;
```

### 3. Configurar archivo .env

```bash
cd backend

# Copiar ejemplo
copy .env.example .env

# Editar .env con tus credenciales
```

Contenido del `.env`:
```env
# Database
DB_ENGINE=mysql
DB_NAME=desconexiones_s13
DB_USER=root  # o 'desconexiones' si creaste usuario
DB_PASSWORD=tu_password
DB_HOST=127.0.0.1
DB_PORT=3306

# API de Telemetría
TELEMETRY_API_URL=http://api.ejemplo.com/telemetry  # Reemplazar con URL real

# Django
SECRET_KEY=tu-secret-key-super-segura-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# ETL
ETL_BATCH_SIZE=100
ETL_PAGE_SIZE=1000
ETL_TIMEOUT=30
VIN_FILTER_PATTERN=SZ
```

### 4. Activar entorno virtual e instalar dependencias

```bash
# Activar entorno virtual
.venv\Scripts\activate

# Instalar dependencias faltantes
pip install python-json-logger

# Verificar que todas las dependencias estén instaladas
pip install -r requirements.txt
```

### 5. Aplicar migraciones

```bash
# Aplicar migraciones
.venv\Scripts\python.exe manage.py migrate

# Deberías ver algo como:
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, organization, registers, sessions, vehicles
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   ...
```

### 6. Crear superusuario

```bash
.venv\Scripts\python.exe manage.py createsuperuser

# Ingresar:
# Username: admin
# Email: admin@example.com
# Password: (tu password)
```

### 7. Verificar que todo funcione

```bash
# Ejecutar servidor
.venv\Scripts\python.exe manage.py runserver

# Deberías ver:
# Starting development server at http://127.0.0.1:8000/
```

Abrir navegador en: http://127.0.0.1:8000/admin

## Troubleshooting

### Error: Access denied for user 'root'@'localhost'

**Solución:**
1. Verifica que la contraseña en `.env` sea correcta
2. Verifica que MySQL esté corriendo
3. Intenta resetear la contraseña de MySQL:

```bash
# En MySQL
ALTER USER 'root'@'localhost' IDENTIFIED BY 'nueva_password';
FLUSH PRIVILEGES;
```

### Error: Can't connect to MySQL server

**Solución:**
1. Verifica que MySQL esté corriendo:
   - Windows: Busca "Services" → MySQL → Start
2. Verifica el puerto en `.env` (default: 3306)
3. Verifica el host (debe ser `127.0.0.1` o `localhost`)

### Error: No module named 'MySQLdb'

**Solución:**
```bash
pip install mysqlclient
```

Si falla en Windows, instala:
```bash
pip install pymysql
```

Y agrega en `settings.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

### Error: Unable to configure formatter 'json'

**Solución:**
```bash
pip install python-json-logger
```

## Próximos Pasos

Una vez que la base de datos esté configurada:

1. **Ejecutar ETL** para poblar datos:
```bash
.venv\Scripts\python.exe manage.py shell

>>> from services.etl_service import ETLService
>>> etl = ETLService(api_url='TU_URL_API_AQUI')
>>> stats = etl.run_etl(max_pages=1)  # Prueba con 1 página primero
>>> print(stats)
```

2. **Verificar datos** en el admin:
   - http://127.0.0.1:8000/admin
   - Login con superusuario
   - Verificar que existan: Clients, Groups, Vehicles, Registers

3. **Probar frontend**:
```bash
cd frontend
npm run dev
```

## Notas Importantes

- **URL de API**: Necesitas la URL real de la API de telemetría para que el ETL funcione
- **Paginación**: La API debe soportar parámetros `page` y `page_size`
- **Estructura de respuesta**: La API debe retornar: `{data: [], total, page, page_size, total_pages}`
- **Campos requeridos**: `vehicle_id`, `vin`, `client_id`, `client_name`, `group_id`, `group_name`, `last_communication_time`, `latitude`, `longitude`, `speed`, `geofence_name`
