# ADR-0001 — Stack técnico y topología de deploy: monolito modular (1 deploy)

- **Estado:** Aceptado (retroactivo, 2026-07-23)
- **Decisores:** Eugenio Valeiras (product owner) + agente supervisor
- **Referenciado desde:** `sad.md §Technical Considerations — Development technology`, `sad.md §Appendices — ADRs`, `constitution.md §3/§4`
- **Tareas:** KER-37 (registro retroactivo; conflicto detectado en la auditoría `docs/audit/addl-gaps-2026-07-22.md §4.2/§4.3`)

> **Nota de proceso.** El SAD exige registrar la selección de tecnología como ADR **antes** de implementar (§Technical Considerations: *"Technology selection is an architecture decision — record it as an ADR (with its impact assessment) before implementation"*). El stack se decidió e implementó sin ese ADR: este documento lo registra **retroactivamente** y deja constancia de la violación de proceso. No hay decisión nueva acá; se sincera la que ya rige el código.

## Contexto

El SAD (2026-07-11) dejó la tecnología sin decidir a propósito y diseñó **diez unidades desplegables sobre siete fronteras topológicas**, cada una trazada a un residuo topológico (§Deployment Unit Boundaries). Para el MVP —un solo desarrollador asistido por agentes, sin usuarios en producción, objetivo de validar el circuito de punta a punta— se optó por implementar los cinco Manager services como **monolito modular en un (1) deploy**, con los límites lógicos preparados para separarse.

## Decisión 1 — Stack

| Área | Elección | Versión en uso | Racional |
|---|---|---|---|
| Lenguaje / framework | **NestJS sobre Node 20** | NestJS 11 | DI nativa que mapea 1:1 los estereotipos IDesign (Manager/Engine/ResourceAccess como providers); monorepo Nest (`apps/keru-api` + `libs/{dominio}` + `libs/core`) hace baratos los límites de módulo y las fitness functions por lint. |
| Base de datos | **PostgreSQL** | pg 8 | Transacciones ACID para el outbox atómico (Decouple row 35); particiones lógicas *marketplace* / *clínico* como schemas separados, antesala de la separación física (NFR-45/48). |
| ORM / esquema | **TypeORM con migraciones versionadas** | TypeORM 0.3 | Migraciones explícitas (`libs/core/src/migrations`, KER-29); `synchronize` apagado por default (NFR-25). |
| Mensajería M→M | **Outbox en Postgres + BullMQ (Redis)** | BullMQ 5 | El canal durable es la tabla `outbox_event` en la partición dueña (§Restrictions — Pub/Sub); BullMQ solo despacha (retry + backoff + dead-letter durable en Postgres, KER-33). Broker reemplazable sin tocar dominio: los componentes de negocio solo ven `PubSubUtility`. |
| Contrato de eventos | **Un envelope por plataforma** | — | Cumple §Restrictions — Event Schema; sin schema registry (diferido con el split). |

## Decisión 2 — Topología: monolito modular con excepción registrada

**Se despliega 1 unidad** (`apps/keru-api`, API + worker en el mismo proceso). Esto es una **excepción explícita** a cuatro filas del Topological Residue Map que piden separación **física** hoy no cumplida:

| Fila | NFR | Qué exige | Estado en el monolito |
|---|---|---|---|
| 60 | NFR-46 — Independent scaling | Pool de escalado clínico separado del marketplace; la carga del marketplace jamás frena el path clínico | **No cumplido físicamente** (proceso compartido). Mitigación lógica: path de escritura clínica síncrono y mínimo; todo cross-domain va encolado. |
| 61 | NFR-47 — Failure isolation | La unidad clínica sigue operando caída la comercial; sin shared fate | **No cumplido físicamente** (shared fate por proceso). Mitigación: cero dependencias síncronas del path record→evaluate→deliver sobre los dominios comerciales. |
| 62 | NFR-48 — Security zones | Tres zonas con claves propias; back-office fuera de la red pública | **Parcial:** superficie admin separada solo a nivel de rutas/guards; sin claves por partición ni red separada. |
| 63 | NFR-49 — Change cadence | Pipelines de build/release separados; el marketplace deploya sin redeployar la unidad clínica | **No cumplido:** un solo pipeline, cada deploy redeploya todo. La fitness function "pipelines separados" es inaplicable al monolito. |

**Qué SÍ se preserva** (los límites que hacen barato el split futuro, verificados en la auditoría 2026-07-22):

- Cero FKs/JOINs cross-dominio (constitution §3.5); referencias cruzadas como UUID planos.
- Dueño único de escritura por dominio + lectura ajena como réplica read-only (§3.3).
- Manager→Manager **solo encolado** vía outbox (§3.2) — el transporte ya es asíncrono, mudarlo de proceso no cambia semántica.
- Particiones lógicas marketplace/clínico declaradas (schemas; su aplicación física está pendiente, auditoría §2.2).
- Fronteras de residencia/keys (filas 1/62) **diferidas, no negadas**: ninguna decisión de este ADR las bloquea.

## Decisión 3 — Señal medible de split

**El primer split es la unidad clínica (CareRecord)**, como fija constitution §4. Se dispara el trabajo de separación cuando ocurra **cualquiera** de:

1. **Latencia:** el bound instrumentado registro→alerta (NFR-42: 3–5 s configurables) rompe su p95 durante una ventana sostenida **y** el diagnóstico atribuye la degradación a carga de marketplace (búsquedas/scans) en el mismo proceso — la violación medible de NFR-46/47.
2. **Cadencia:** los deploys de marketplace superan ~1/semana sostenido con cambios que obligan a redeployar el path clínico sin tocarlo (violación operativa de NFR-49, fila 63).
3. **Cumplimiento:** se cierra OQ-5/DV-2 (jurisdicción/consentimiento) con un régimen que exige residencia o claves por partición **físicas** (filas 1/62, NFR-45/48) — el split deja de ser optimización y pasa a ser obligación legal.

Prerrequisito para la señal 1: instrumentar el bound 3–5 s (NFR-42, hoy sin métricas — auditoría §3, "próxima tanda").

## Impacto (impact assessment)

- **Positivo:** costo operativo mínimo para validar el MVP; una sola base y un solo pipeline; los límites lógicos ya pagan el precio de diseño del split (el residual no se re-litiga al separar).
- **Negativo asumido:** NFR-46/47/48/49 sin garantía física hasta el split; un incidente de marketplace puede degradar el path clínico (aceptado sin usuarios reales en producción).
- **Reversibilidad:** alta por construcción — el split es mover módulos a otro deploy + aplicar schemas/claves; las fitness functions de frontera (constitution §3.6) protegen esa reversibilidad en cada PR.

## Cumplimiento

La constitution §4 (stack) y §3 (arquitectura) condensan este ADR y no pueden contradecirlo; el índice de ADRs vive en `sad.md §Appendices`. Las cuatro filas exceptuadas se re-evalúan contra la señal de split en cada auditoría de cumplimiento.
