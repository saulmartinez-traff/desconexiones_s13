# ⚡ Quick Start - S13 Desconexiones

**Tiempo estimado:** 15 minutos  
**Requisitos previos:** Python 3.9+, Node.js 16+, MySQL 8.0+

---

## 🚀 Inicio Rápido (Primeros 5 minutos)

### 1️⃣ Clonar & Navegar

```bash
cd desconexiones_s13
```

### 2️⃣ Backend Setup

```bash
# Ir a backend
cd backend

# Crear virtual environment
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Mac/Linux)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3️⃣ Configurar Base de Datos

```bash
# Copiar template de variables
copy .env.example .env

# Editar .env (abrir con editor de texto)
# Cambiar:
# DB_ENGINE=mysql
# DB_NAME=desconexiones_s13
# DB_USER=root
# DB_PASSWORD=tu_password
# DB_HOST=127.0.0.1
# DB_PORT=3306
```

### 4️⃣ Crear Base de Datos (MySQL)

```bash
# En terminal MySQL:
mysql -u root -p

CREATE DATABASE desconexiones_s13 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'desconexiones'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON desconexiones_s13.* TO 'desconexiones'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 5️⃣ Migraciones & Admin User

```bash
# Aplicar migraciones
python manage.py migrate

# Crear superuser (admin)
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: admin123

# (Opcional) Cargar fixtures iniciales
python manage.py loaddata initial_data.json
```

### 6️⃣ Ejecutar Backend

```bash
# Iniciar servidor Django
python manage.py runserver

# Deberías ver:
# Starting development server at http://127.0.0.1:8000/
# Quit the server with CTRL-BREAK.
```

---

## 🎨 Frontend Setup (5 minutos)

```bash
# Abrir nueva terminal
cd frontend

# Instalar dependencias
npm install

# Ejecutar desarrollo
npm run dev

# Deberías ver:
# VITE v5.0.0 ready in 234 ms
# ➜  Local: http://localhost:5173/
```

---

## ✅ Verificación

### Endpoints Listos?

```bash
# Terminal 1 (Backend corriendo)
curl http://localhost:8000/api/auth/token/ -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Deberías ver:
# {"access":"eyJ0eXAiOiJKV1QiLCJhbGc...","refresh":"eyJ0eXAi..."}
```

### Frontend Corriendo?

Abre: http://localhost:5173 en el navegador

---

## 📝 Primeros Pasos de Desarrollo

### 1. Crear Algunos Datos de Prueba

```bash
cd backend

# Acceder a shell interactivo
python manage.py shell

# Dentro de shell:
from apps.organization.models import Distribuidor, Client, Group
from apps.vehicles.models import Vehicle, Geofence

# Crear distribuidor
dist = Distribuidor.objects.create(
    distribuidor_id="DIST-001",
    name="Distribuidora Test",
    contact_name="Juan",
    contact_email="juan@test.com",
    contact_phone="+52 5555555555"
)

# Crear cliente
client = Client.objects.create(
    client_id="CLI-001",
    distribuidor=dist,
    name="Cliente Test",
    contact_name="Roberto"
)

# Crear grupo
group = Group.objects.create(
    group_id="GRP-001",
    client=client,
    name="Flota Test"
)

# Crear vehículo
vehicle = Vehicle.objects.create(
    vehicle_id="VEH-001",
    vin="WBADO8104K0909217",
    latitude=25.6866,
    longitude=-100.3161,
    group=group,
    distribuidor=dist,
    is_connected=True
)

print("✅ Datos de prueba creados!")
exit()
```

### 2. Probar Endpoints

```bash
# Script de testing automático (requiere requests)
pip install requests

python test_api.py

# Deberías ver:
# ✅ Login successful
# ✅ Found N groups
# ✅ Found N vehicles
# ✅ TEST SUITE COMPLETED
```

### 3. Acceder a Admin

- URL: http://localhost:8000/admin
- Usuario: admin
- Contraseña: admin123

### 4. Documentación API Interactiva

```bash
# Swagger/OpenAPI (próximamente)
# http://localhost:8000/api/schema/swagger/
```

---

## 🔍 Estructura del Código

```
desconexiones_s13/
├── backend/
│   ├── core/              # Configuración Django
│   ├── apps/
│   │   ├── organization/  # Users, Clientes, Grupos
│   │   ├── vehicles/      # Vehículos, Geocercas
│   │   ├── registers/     # Desconexiones, Auditoría
│   │   └── auth/          # Permisos, JWT
│   ├── services/          # Lógica de negocio
│   ├── middleware/        # Middleware personalizado
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── atoms/         # Componentes base
│   │   ├── molecules/     # Composiciones
│   │   ├── organisms/     # Componentes complejos
│   │   ├── pages/         # Vistas principales
│   │   ├── hooks/         # Custom hooks
│   │   ├── services/      # API clients
│   │   ├── styles/        # Tema y estilos
│   │   ├── constants/     # Constantes
│   │   ├── utils/         # Utilidades
│   │   ├── App.jsx
│   │   └── index.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
└── docs/
    ├── ARCHITECTURE.md    # Guía técnica
    ├── API_SPEC.md        # Especificación API
    ├── API_ENDPOINTS.md   # Ejemplos de uso
    ├── SETUP_GUIDE.md     # Setup detallado
    └── ERD.md             # Diagrama de BD
```

---

## 🛠️ Comandos Útiles

### Backend

```bash
cd backend

# Ejecutar servidor
python manage.py runserver

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Shell interactivo
python manage.py shell

# Crear superuser
python manage.py createsuperuser

# Limpiar BD (cuidado!)
python manage.py flush

# Cargar fixtures
python manage.py loaddata initial_data.json

# Ejecutar tests
pytest

# Ver coverage
pytest --cov=apps
```

### Frontend

```bash
cd frontend

# Desarrollo
npm run dev

# Build
npm run build

# Preview build
npm run preview

# Lint code
npm run lint

# Format code
npm run format
```

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'django'"

```bash
# Asegúrate de estar en el venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstala dependencias
pip install -r requirements.txt
```

### Error: "Connection refused" en localhost:8000

```bash
# Verifica que Django esté corriendo
# Revisa que el puerto 8000 esté disponible
# Intenta:
python manage.py runserver 8001
```

### Error: "No database" en migraciones

```bash
# Verifica que MySQL está corriendo
# Verifica la configuración en .env
# Intenta crear la BD manualmente (ver arriba)
```

### Error de CORS en frontend

```bash
# Verifica que frontend corre en puerto 5173
# Verifica que backend tiene CORS configurado
# En core/settings.py CORS_ALLOWED_ORIGINS incluye 5173
```

---

## 📊 Próximos Pasos

### Corto Plazo (Esta semana)
1. ✅ Backend corriendo localmente
2. ✅ Frontend corriendo localmente
3. [ ] Crear usuarios de prueba
4. [ ] Probar endpoints básicos
5. [ ] Revisar documentación

### Mediano Plazo (Próximas 2 semanas)
1. [ ] Integrar frontend con API
2. [ ] Implementar login/logout
3. [ ] Crear página de concentrado
4. [ ] Crear página de resumen
5. [ ] Tests básicos

### Largo Plazo (Mes siguiente)
1. [ ] Analytics y reportes
2. [ ] Docker setup
3. [ ] CI/CD pipeline
4. [ ] Deployment a producción

---

## 📚 Recursos Útiles

- **Django Docs:** https://docs.djangoproject.com/
- **DRF Docs:** https://www.django-rest-framework.org/
- **React Docs:** https://react.dev/
- **Vite Docs:** https://vitejs.dev/
- **JWT Auth:** https://django-rest-framework-simplejwt.readthedocs.io/

---

## 🆘 Ayuda

Consulta:
- `SETUP_GUIDE.md` - Configuración detallada
- `ARCHITECTURE.md` - Diseño del sistema
- `API_ENDPOINTS.md` - Ejemplos de API
- `ROADMAP.md` - Plan de desarrollo

---

**¡Listo para desarrollar!** 🎉

Si tienes problemas, revisa la documentación o abre un issue.
