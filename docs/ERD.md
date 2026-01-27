# Database Schema - S13 Desconexiones

## Diagrama ER (Entity-Relationship)

```
┌─────────────────┐
│   Distribuidores│
├─────────────────┤
│ distribuidor_id │ (PK)
│ distribuidor_name
│ contact_email
│ is_active
└────────┬────────┘
         │ (1:N)
         │
┌────────v─────────────────┐
│    Vehicles              │
├──────────────────────────┤
│ id                   (PK)│
│ vehicle_id           (UK)│
│ vin                  (UK)│
│ group_id         (FK)    │
│ distribuidor_id  (FK)    │
│ geofence_id      (FK)    │
│ contrato_id      (FK)    │
│ last_latitude           │
│ last_longitude          │
│ last_connection         │
│ is_connected            │
│ created_at              │
│ updated_at              │
└──────────┬───────────────┘
           │ (1:N)
           │
    ┌──────v───────────────┐
    │  Registers           │
    ├──────────────────────┤
    │ id              (PK) │
    │ vehicle_id   (FK)    │
    │ report_date         │
    │ problem             │
    │ final_status        │
    │ responsible_id (FK) │
    │ comment             │
    │ created_at          │
    └──────┬───────────────┘
           │ (1:N)
           │
    ┌──────v────────┐
    │  Bitacora      │
    ├────────────────┤
    │ id        (PK) │
    │ register_id(FK)
    │ user_id   (FK) │
    │ action         │
    │ comentario     │
    │ created_at     │
    └────────────────┘

Usuarios (Django Auth)
├── User Model (PK: id)
├── email
├── role
└── is_active


Organizacional
┌──────────────┐
│  Clients     │
├──────────────┤
│ id       (PK)│
│ client_id(UK)│
│ description  │
└────┬─────────┘
     │ (1:N)
     │
  ┌──v──────────┐
  │  Groups      │
  ├──────────────┤
  │ id       (PK)│
  │ group_id (UK)│
  │ client_id(FK)│
  │ description  │
  └──────────────┘

Geoespacial
┌─────────────────┐
│  Geofences      │
├─────────────────┤
│ id          (PK)│
│ geo_id      (UK)│
│ geo_name       │
│ geofence_type  │
│ polygon_coord  │
│ circle_coord   │
│ is_active      │
└─────────────────┘

Contractual
┌────────────────┐
│  Contratos     │
├────────────────┤
│ id        (PK) │
│ contrato_id(UK)│
│ vin        (UK)│
│ contrato       │
│ start_date     │
│ end_date       │
│ is_active      │
└────────────────┘
```

## Relaciones Clave

### Foreign Keys

```
Vehicles.group_id → Groups.id (ON DELETE PROTECT)
Vehicles.distribuidor_id → Distribuidores.id (ON DELETE PROTECT)
Vehicles.geofence_id → Geofences.id (ON DELETE SET NULL)
Vehicles.contrato_id → Contratos.id (ON DELETE SET NULL)

Registers.vehicle_id → Vehicles.id (ON DELETE CASCADE)
Registers.responsible_id → Users.id (ON DELETE SET NULL)
Registers.distribuidor_id → Distribuidores.id (ON DELETE PROTECT)

Bitacora.register_id → Registers.id (ON DELETE CASCADE)
Bitacora.user_id → Users.id (ON DELETE SET NULL)

Groups.client_id → Clients.id (ON DELETE PROTECT)
```

### Indexes

```
Vehicles:
  - (vehicle_id)
  - (vin)
  - (group_id, is_active)
  - (is_connected)
  - (last_connection)

Registers:
  - (vehicle_id, report_date)
  - (report_date)
  - (disconnection_type)
  - (final_status)
  - (responsible_id)

Bitacora:
  - (register_id, created_at)
  - (user_id, created_at)
  - (action)
```

## Tamaño Estimado

```
Vehicles: ~500 registros/año
Registers: ~50,000-100,000 registros/año
Bitacora: ~150,000-300,000 registros/año
```

---

*Última actualización: 27/01/2025*
