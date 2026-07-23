# Keru — Repo paraguas

Keru es un **marketplace de cuidadores** ("el Uber de los cuidadores"): conecta pacientes
y sus familias con cuidadores profesionales, permite contratarlos en línea, registrar las
métricas de salud del paciente durante el servicio, y que la familia consulte la evolución
y reciba alertas desde cualquier lugar.

Este repositorio **no contiene código de aplicación**: es el paraguas del proyecto. Acá viven
la documentación de producto y arquitectura (la fuente de verdad de *qué* hace el sistema),
la configuración de agentes (`.claude`, `addl`) y este mapa. El código vive en sub-repos que
se clonan **adentro de esta carpeta**.

> **¿5 minutos?** Leé [Mapa del sistema](#mapa-del-sistema) y [Correr todo en dev](#correr-todo-en-dev);
> el resto es referencia.

---

## Mapa del sistema

| Carpeta | Repo | Qué es |
|---|---|---|
| `./` | [EugeValeiras/Keru](https://github.com/EugeValeiras/Keru) | **Este paraguas**: casos de uso, constitution, diseño arquitectónico, skills de agentes |
| `Keru-API/` | [EugeValeiras/Keru-API](https://github.com/EugeValeiras/Keru-API) | **Backend NestJS 11** — API REST bajo `/api/v1`, contrato OpenAPI en `openapi.json` |
| `Keru-Webapp/` | [EugeValeiras/Keru-Webapp](https://github.com/EugeValeiras/Keru-Webapp) | **SPA Angular 20** — una sola app con 3 experiencias por rol (familia/paciente, cuidador, admin) |
| `Keru-App/` | — | Reservada para la app móvil (todavía sin código ni remoto) |

Los sub-repos están **ignorados** por este repo (ver `.gitignore`): cada uno tiene su propio
Git, su propio CI y su propio ciclo de PRs.

### Arquitectura en dos líneas

- **Backend**: monolito modular organizado en **5 dominios IDesign** (Membership, Hiring,
  CareRecord ⭐, CareConsult, Reputation), capas Manager → Engine → ResourceAccess → Resource,
  con los límites **enforzados por ESLint en CI** y preparados para separar por deploy.
  Postgres 16 + Redis 7 (outbox/BullMQ) + floci (emulador AWS local para SES/S3).
- **Frontend**: Angular 20 standalone, zoneless, signals, Tailwind v4 con design system propio
  (`shared/ui`). Cliente API híbrido: tipos generados desde `openapi.json` + servicios finos a mano.

El detalle vive en el README de cada sub-repo; el *porqué* de cada regla, en
[`constitution.md`](./constitution.md) y en
[`addl/docs/architect/residual-design.md`](./addl/docs/architect/residual-design.md).

---

## Correr todo en dev

Prerequisitos: **git**, **Docker** y **Node 20**.

```bash
# 1) Cloná los sub-repos adentro de esta carpeta
git clone https://github.com/EugeValeiras/Keru-API.git
git clone https://github.com/EugeValeiras/Keru-Webapp.git

# 2) Infra + seed + API con hot reload
cd Keru-API
npm install
npm run infra:up       # Postgres + Redis + floci en Docker
npm run seed           # datos de demo (cuentas + paciente Rosa Díaz)
npm run start:dev      # API en http://localhost:3000/api/v1

# 3) Webapp (en otra terminal)
cd Keru-Webapp
npm install
npm start              # http://127.0.0.1:4200 — proxy /api → localhost:3000
```

Cuentas seed (password `S3gura!123`): `familiar@test.com`, `cuidador@test.com`, `admin@test.com`.

| Qué | Dónde |
|---|---|
| Webapp (dev) | http://127.0.0.1:4200 |
| API | http://localhost:3000/api/v1 |
| Swagger UI | http://localhost:3000/api/docs |
| Bajar la infra | `npm run infra:down` (en `Keru-API`) |

## Correr en modo prod-like

El profile `app` del compose de `Keru-API` levanta el stack completo containerizado:
API (build multi-stage) + webapp compilada servida por nginx + toda la infra. El nginx
proxya `/api` → API y `/media` → floci, igual que el proxy de dev.

```bash
cd Keru-API
docker compose --profile app up -d --build   # (o npm run app:up)
npm run seed                                 # requiere Node 20 + npm install
# Webapp: http://localhost:8080 · API: http://localhost:3000/api/v1
docker compose --profile app down            # baja todo (o npm run app:down)
```

- Si ya tenés `npm run start:dev` ocupando el `:3000`, exportá `API_PORT=3001` antes del `up`.
- Circuito E2E completo contra este modo: en `Keru-Webapp`,
  `E2E_BASE_URL=http://localhost:8080 npm run e2e`.

---

## Flujo docs-first

En Keru **el documento manda y el código se deriva**. Las fuentes, en orden:

1. [`Keru-Casos-de-Uso-MVP.md`](./Keru-Casos-de-Uso-MVP.md) — los 20 casos de uso del MVP
   (UC-01..10, UC-12..22): comportamiento esperado, flujos alternativos, criterios de aceptación.
   **Fuente de verdad de producto.**
2. [`constitution.md`](./constitution.md) — las reglas no-negociables: principios de producto,
   call rules IDesign, dueño único de escritura, NFRs ejecutables. Ante "¿esto se puede hacer
   así?", la respuesta está acá.
3. [`addl/docs/architect/residual-design.md`](./addl/docs/architect/residual-design.md) — el
   diseño arquitectónico completo (58 NFRs, componentes, deploys) del que la constitution es
   el condensado.
4. [`docs/brand/brand-book.md`](./docs/brand/brand-book.md) — la identidad **"abrazo
   profesional"**: personalidad, paleta, tipografía (Fraunces/Figtree), tono de voz, motion.
   **Referencia de diseño obligatoria para toda tarea de UI** en la webapp (y futuras
   superficies): los tokens/estilos se derivan de acá, no se inventan por tarea.
   Vista rápida: [`docs/brand/preview.html`](./docs/brand/preview.html).

Todo cambio de comportamiento sigue la skill **`keru-feature`** (en `.claude/skills/`):
leer la constitution → analizar el caso de uso → **documentar el cambio en el UC antes de
codear** → escribir el test desde los criterios de aceptación → implementar respetando las
call rules. El CI de este repo verifica que los docs canónicos existan y que los links
relativos no se rompan (`.github/workflows/docs.yml`).

## Tablero Kanban: la fuente de trabajo

El trabajo del proyecto **no** se organiza en issues de GitHub sino en el tablero Kanban de
la suite propia (proyecto `keru`, tareas `KER-N`), con pipeline
*Backlog → In Development → PR Created → PR Approved → Testing → Done*.

- **Tablero (UI)**: http://localhost:3100 (levanta con la Kanban-API local; ver `workspace/Kanban`).
- **CLI**: `kanban tasks --project keru` lista el tablero; `kanban task show KER-N` arma el
  bundle de contexto completo de una tarea (descripción, criterios, memoria del proyecto).
- Cada tarea trabaja en un **worktree** propio (`.kanban/worktrees/`) y termina en PR sobre
  el repo que toque; las features nuevas entran como tarea antes que como código.

## Links

| Recurso | Link |
|---|---|
| Swagger UI (local) | http://localhost:3000/api/docs — contrato estático en `Keru-API/openapi.json` |
| Tablero Kanban (local) | http://localhost:3100 |
| CI del paraguas (docs + links) | https://github.com/EugeValeiras/Keru/actions |
| CI de Keru-API (build + lint de fronteras + jest) | https://github.com/EugeValeiras/Keru-API/actions |
| CI de Keru-Webapp (build + Playwright contra API dockerizada) | https://github.com/EugeValeiras/Keru-Webapp/actions |
| Scope original | [`Keru-Scope-MVP.docx.pdf`](./Keru-Scope-MVP.docx.pdf) |
