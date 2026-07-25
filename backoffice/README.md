# Keru · Back-office

Consola de administración (zona no-pública). Arquitectura **BFF**: el browser solo habla con una
capa Node (BFF) que guarda el JWT en una cookie **httpOnly** y proxya al backend real de Keru.

```
Browser (Angular + Material)
   │  cookie httpOnly (el token nunca está en JS)
   ▼
BFF (NestJS, :3001)   /bff/auth/*  +  proxy /bff/api/* -> Keru API
   ▼
Keru API (:3000, zona no-pública)
```

## Estructura
- `bff/` — NestJS. Auth por cookie (`/bff/auth/login|logout|me`) + proxy autenticado (`/bff/api/*`).
- `web/` — Angular 20 (standalone + signals) + Angular Material. Pantallas UC-19.

## Correr en desarrollo (3 procesos)

```bash
# 1. Backend real de Keru (desde la raíz del repo)
npm run infra:up && npm run seed && npm run start:dev     # :3000

# 2. BFF
cd backoffice/bff && npm install && npm run start:dev     # :3001

# 3. Web (Angular con proxy /bff -> BFF)
cd backoffice/web && npm install && npm start             # :4200
```

Abrí `http://localhost:4200`. Login con la cuenta admin del seed: `admin@test.com` / `S3gura!123`.

## Correr con Docker (independiente del compose de Keru)

El back-office tiene su **propio `docker-compose.yml`** — no depende del compose de la raíz. Levanta 2 contenedores: `web` (nginx sirve el build de Angular + proxya `/bff`) y `bff`. El BFF alcanza la API real de Keru en el host vía `host.docker.internal:3000`.

```bash
# 1. La API de Keru corriendo en el host (desde la raíz del repo)
npm run app:up        # o  npm run infra:up && npm run seed && npm run start:dev

# 2. El back-office (desde backoffice/)
cd backoffice
docker compose up --build      # web en http://localhost:8080
docker compose down            # bajar
```

Abrí `http://localhost:8080`. Es un deployable autocontenido (zona no-pública): el browser solo ve el `web`, que proxya al `bff`, que es el único que habla con la API real.

## Pantallas implementadas
- **Panel** — métricas operativas (cuidadores por estado, solicitudes, asignaciones).
- **Cuidadores** — listado con filtro por estado + búsqueda por nombre/zona + barrido de vencidos.
- **Detalle (UC-19)** — documentación completa + **aprobar** / **rechazar con motivo** / **verificar insignias** + **desactivar/reactivar** (dispara el ripple a Hiring).
- **Rangos clínicos (UC-18)** — editar el rango de cada métrica (con plausibilidad) + historial de versiones.
- **Auditoría** — visor del audit log.

## Pantallas · detalle histórico (Fase 1 · UC-19)
- **Login** — solo administradores (un login con otro rol se rechaza en el BFF).
- **Cuidadores** — listado con filtro por estado (pendientes/aprobados/rechazados/todos) + botón de barrido de vencidos.
- **Detalle** — documentación completa (certificaciones con institución/año, disponibilidad, tarifas) + **aprobar** / **rechazar con motivo** / **verificar insignias** (los 3 niveles independientes).
- **Auditoría** — visor del audit log.

## Variables de entorno (BFF)
Ver `bff/.env.example`: `KERU_API_URL`, `COOKIE_NAME`, `COOKIE_SECURE` (true en prod/HTTPS), `WEB_ORIGIN`.

## Producción (pendiente)
El BFF servirá el build de `web/` como estáticos (un solo deployable en la zona no-pública). Hoy en dev,
`ng serve` proxya `/bff` al BFF.
