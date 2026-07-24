# Verificación aislada por tarea (KER-60)

> **En una línea.** Cada tarea, al verificarse, levanta su **propio** stack en Docker con
> **puertos efímeros** y corre las suites contra él, sin pisar a otras tareas ni a los servers
> de dev. N verificaciones pueden correr **en paralelo** sin colisión de nombres ni puertos.

## Por qué

Las tareas concurrentes compartían los servers locales (`:3000` API, `:4200` webapp) y se
pisaban entre sí: conflictos de puerto, "servers zombie" y **falsos rojos** que costaron
sesiones enteras de supervisión (ver la memoria `keru-verify-gate` del proyecto). Con
`:3000/:4200` dados de baja (migración a AWS + CICD), la verificación local necesita
**aislamiento por tarea**. Este harness lo da: un `docker compose -p keru-<tarea>` por
verificación, con puertos de host efímeros que se **descubren** en runtime.

## Qué levanta

| Pieza | Cómo corre | Puerto |
|---|---|---|
| Postgres + Redis + floci (emulador AWS) | Docker (`docker compose -p keru-<tarea>`) | **efímero** (`*_HOST_PORT=0`) |
| API (NestJS, imagen del compose) | Docker (profile `app`, migraciones al bootear) | **efímero** (`API_PORT=0`) |
| Webapp (Angular) | `ng serve` en puerto efímero, con `--proxy-config` generado al vuelo | **efímero** (`--port 0`) |

La webapp va por `ng serve` (no el nginx del compose): más liviano, espeja el job e2e del CI,
y permite 2 stacks concurrentes sin buildear la imagen de la webapp.

## Flujo (scripts/verify-isolated.mjs)

1. Deriva un **project name** único (`keru-<rama/tarea sanitizada>`) y resuelve los worktrees
   hermanos de `Keru-API` y `Keru-Webapp` de la misma tarea (mismo patrón que
   `run-webapp-e2e.mjs`: `KERU_API_DIR`/`KERU_WEBAPP_DIR` → worktree hermano → checkout base).
2. `docker compose -p <proj> --profile app up -d --wait --build api` — la `api` arrastra
   `postgres`+`redis`+`floci` por `depends_on`. Puertos de host **efímeros** por env.
3. **Descubre** los puertos con `docker compose -p <proj> port <svc> <puertoInterno>`
   (`api 3000`, `postgres 5432`, `redis 6379`, `floci 4566`) y espera `GET /api/v1/health`.
4. **Seedea** la API aislada (`npm run seed`, ts-node — el mismo paso del CI) apuntando a los
   puertos dinámicos.
5. Corre las suites contra ese stack:
   - **unit** — `npm test` (jest) en Keru-API.
   - **api-e2e** — `npm run test:e2e` (jest + supertest); bootea su propio Nest contra el
     `postgres`/`redis` dockerizados. Usa su DB `keru_e2e` (la recrea el `globalSetup`),
     aislada de la data del seed.
   - **web-e2e** — genera `proxy.conf.<proj>.json` (`/api`→apiPort, `/media`→flociPort),
     levanta `ng serve --port 0` con ese proxy, y corre Playwright con
     `E2E_BASE_URL=http://127.0.0.1:<puertoWebapp>`.
6. **Teardown SIEMPRE** (éxito, fallo o Ctrl-C): mata el `ng serve` (árbol de procesos) y
   `docker compose -p <proj> down -v --remove-orphans`, y borra los temporales. `docker ps`
   queda limpio: sin contenedores, volúmenes ni puertos colgados.

## Uso

Desde el **paraguas** (este repo), con los worktrees hermanos de la tarea presentes:

```bash
# Todo (unit + api-e2e + web-e2e/Playwright)
node scripts/verify-isolated.mjs --full

# Solo el gate automático (unit + api-e2e; Playwright fuera del gate — ver abajo)
node scripts/verify-isolated.mjs --gate

# Suites puntuales / debug
node scripts/verify-isolated.mjs --suite=api-e2e --api-e2e-args=invitation
node scripts/verify-isolated.mjs --suite=web-e2e --web-e2e-args=circuito.spec.ts
node scripts/verify-isolated.mjs --full --keep     # no hace teardown (inspección)
```

### Flags

| Flag | Efecto |
|---|---|
| `--suite=unit,api-e2e,web-e2e` | Suites a correr (coma-separadas). Default: las tres. |
| `--gate` | Atajo: `unit,api-e2e` (lo que corre el gate de Kanban). |
| `--full` | Atajo: `unit,api-e2e,web-e2e`. |
| `--project=<name>` | Forzar el project name de docker compose (default: derivado de la tarea). |
| `--no-build` | Reusar la imagen ya buildeada (reruns rápidos). |
| `--no-install` | Nunca correr `npm ci` (default: solo si falta `node_modules`). |
| `--keep` | No hacer teardown (dejar stack + ng serve para inspección). |
| `--api-e2e-args="<filtro>"` | Filtro extra para el jest e2e. |
| `--web-e2e-args="<args>"` | Args extra para Playwright. |

Overrides por env equivalentes: `KERU_VERIFY_SUITE`, `KERU_VERIFY_PROJECT`, `KERU_API_DIR`,
`KERU_WEBAPP_DIR`.

## Wiring al gate de verify de Kanban

El `verifyCommand` de las tarjetas de Keru es `npm test`, que corre en el worktree del
paraguas. Un `package.json` **local y gitignoreado** (`/package.json`, ver `.gitignore`)
delega ese `npm test` en este harness:

```json
{ "scripts": { "test": "node scripts/verify-isolated.mjs --gate" } }
```

Así `kanban task verify KER-N` / `kanban task done KER-N` corren la verificación **aislada**
sin que ninguna otra tarjeta cambie su firma. El `package.json` es de máquina (cada worktree
del paraguas tiene el suyo); el harness (`scripts/verify-isolated.mjs`) sí se versiona.

**Playwright fuera del gate automático.** Como en `keru-verify-gate`, el gate por default corre
`unit + api-e2e` (rápido y determinístico). Playwright se corre a mano / en la demo con
`npm run verify:full`: es más pesado (Chromium + `ng serve`) y su valor está cubierto por el
job e2e del CI de la webapp.

## Aislamiento del compose (Keru-API/docker-compose.yml)

Para que N proyectos convivan, el compose se volvió **aislable** sin romper el CI:

- **Sin `container_name` fijos** — `docker compose -p <proj>` nombra los contenedores por
  proyecto; los volúmenes se prefijan por proyecto. Dos proyectos no colisionan.
- **Puertos de host por env con default = valor histórico** —
  `${POSTGRES_HOST_PORT:-5432}`, `${REDIS_HOST_PORT:-6379}`, `${FLOCI_HOST_PORT:-4566}`,
  `${API_PORT:-3000}`, `${WEBAPP_HOST_PORT:-8080}`. Con los defaults, **el dev y el CI quedan
  idénticos** (el job e2e de la webapp sigue haciendo `docker compose --profile app up -d
  --build api` y `curl localhost:3000`). Poniendo un puerto en `0` se publica **efímero** y se
  descubre con `docker compose -p <proj> port <svc> <puertoInterno>`.

## Concurrencia (demo)

Dos verificaciones en paralelo, cada una con su project name → puertos distintos, stacks
aislados, sin interferencia:

```bash
node scripts/verify-isolated.mjs --project=keru-demoA --suite=api-e2e &
node scripts/verify-isolated.mjs --project=keru-demoB --suite=web-e2e &
wait
docker ps        # limpio al terminar: sin contenedores colgados
```

La política del supervisor es **máx. 2 concurrentes** (recursos de la máquina).

## Windows

Docker Desktop + Git Bash / PowerShell. El harness usa `docker.exe`/`npm`/`ng` vía shell y no
pasa rutas del host a docker (todo efímero). El `ng serve` se mata con `taskkill /F /T` (árbol
de procesos); en POSIX, con `kill(-pid)` sobre el grupo.
