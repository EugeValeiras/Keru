# Constitución de Keru

> **Qué es este documento.** Las reglas **no-negociables** del proyecto: principios de producto, arquitectura, y los requisitos que ningún cambio puede violar sin una decisión explícita registrada acá. Ante cualquier duda de "¿esto se puede hacer así?", la respuesta está en este archivo o en el caso de uso correspondiente en `Keru-Casos-de-Uso-MVP.md`.
>
> **Fuentes de verdad.** Producto → `Keru-Casos-de-Uso-MVP.md`. Arquitectura → `addl/docs/architect/residual-design.md` (58 NFRs, componentes IDesign, deploys). Este documento **condensa** ambas en reglas ejecutables; ante conflicto, mandan las fuentes.
>
> **Última actualización:** 2026-07-20.

---

## 1. Visión y alcance

Keru es un marketplace de cuidadores que conecta pacientes y familias con cuidadores profesionales: buscar por zona/tipo/reputación, contratar en línea, registrar métricas de salud durante el servicio, y que la familia vea la evolución desde cualquier lugar.

**Objetivo del MVP:** validar el circuito completo de punta a punta — *registrarse → aprobar cuidador → buscar → contratar → registrar dato clínico → la familia lo consulta → alerta si está fuera de rango → calificar*.

**Entregable de esta etapa:** **solo backend** (API). Los clientes (app móvil, web, back-office) quedan fuera de esta etapa pero el diseño los contempla.

---

## 2. Principios de producto (no-negociables)

1. **Móvil y web.** Toda funcionalidad clínica y de notificación es plenamente funcional en web; el móvil no es requisito para operar.
2. **Seguimiento sin demora perceptible.** Un registro cargado por un actor se ve en la vista del paciente casi al instante (§1 "tiempo real").
3. **Trazabilidad clínica total.** Todo registro clínico persiste **fecha/hora + autor con su rol**. Nada se edita silenciosamente: una corrección conserva la traza (borrado = *tombstone con traza*, nunca *hard delete*).
4. **Control de acceso por rol Y por vínculo.** El permiso no es de la cuenta: es del par **(cuenta, rol-en-vínculo/asignación)**. Un cuidador solo opera sobre pacientes **asignados**; un familiar solo sobre pacientes a los que está **vinculado**.
5. **Aprobación previa de cuidadores.** Ninguna cuenta de cuidador es visible en el marketplace ni puede recibir solicitudes sin aprobación previa del administrador (UC-19).
6. **Reputación bidireccional.** Familia↔cuidador se califican mutuamente; una reseña no requiere la otra (en el MVP; ver NFR de reveal simultáneo en §5).
7. **Alertas obligatorias con campana.** Toda alerta queda **siempre** en el centro de notificaciones in-app; el push es adicional, nunca el único registro. La campana es la garantía.
8. **Una cuenta, varios pacientes.** Una cuenta administra 1..n perfiles de paciente; toda operación se hace en el contexto de **un perfil concreto**, nunca de la cuenta en general.
9. **Deep links de invitación.** El link de invitación abre la app si está instalada o la web si no, con la misma confirmación (UC-03).
10. **Datos de salud sensibles.** Privacidad por diseño: cifrado en tránsito y reposo, mínimos privilegios, residencia de datos clínicos in-country.

---

## 3. Arquitectura (IDesign residual)

El sistema se descompone en **5 dominios** (= los 5 "Manager services" del diseño residual). En esta etapa se despliegan como **monolito modular (1 deploy)**, con los límites preparados para separar por deploy el día que la escala lo pida.

| Dominio (módulo) | Qué hace | Casos de uso |
|---|---|---|
| **Membership** | Alta, login, vínculos familiares, aprobación de cuidadores | UC-01..04, UC-19, UC-22 |
| **Hiring** | Buscar, contratar, ciclo de vida de la contratación e historial | UC-05..10, UC-16 |
| **CareRecord** ⭐ | Registrar clínico (vitales/medicación/novedades) + alertas | UC-12, UC-13, UC-18, UC-20 |
| **CareConsult** | Lectura clínica: estado, historial, gráficos | UC-14, UC-15 |
| **Reputation** | Reseñas bidireccionales | UC-17, UC-21 |

### 3.1 Capas (estereotipos)
- **Client** → puerta de entrada (fuera del backend en esta etapa).
- **Manager** → orquesta un workflow, *con estado por workflow*. El "qué/porqué".
- **Engine** → cálculo puro, *sin estado*. El "cómo" (`MatchingEngine`, `AlertEngine`, `PermissionEngine`).
- **ResourceAccess** → verbos atómicos sobre datos. *Sin estado*.
- **Resource** → la base/infra (Postgres, read model, proveedores externos).
- **Utility** → transversal (`PubSubUtility` sobre outbox, `AuditUtility`).

### 3.2 Reglas de llamada (Call Rules) — arquitectura cerrada
- ✅ Client → Manager (única puerta de entrada).
- ✅ Manager → Engine, Manager → ResourceAccess, Manager → Utility.
- ✅ Engine → ResourceAccess (solo lectura para no-dueños).
- ✅ ResourceAccess → Resource (única capa que toca Resources).
- ✅ Manager → Manager **solo encolado** (vía `PubSubUtility`/outcome outbox), nunca síncrono.
- ❌ Client → Engine/ResourceAccess/Resource/Utility.
- ❌ ResourceAccess → ResourceAccess, Engine → Engine (sin llamadas de costado).
- ❌ Cualquier llamada **hacia arriba** (regla dura).

### 3.3 Dueño único de escritura
Solo **Membership** escribe vínculos/roles; solo **Hiring** escribe asignaciones; solo **Reputation** escribe reseñas; solo **CareRecord** escribe registros clínicos/rangos/alertas. Los demás leen por réplica de solo-lectura.

### 3.4 Acceso a datos — REGLA NO-NEGOCIABLE (disciplina Löwy / IDesign)
**Todo acceso a la base de datos se hace ÚNICAMENTE a través de un ResourceAccess.** Ningún Manager, Engine ni Controller puede:
- inyectar un `Repository` (`@InjectRepository`) ni un `DataSource` (`@InjectDataSource`);
- ejecutar queries (`.find/.save/.update/.delete/.query/createQueryBuilder`).

Los Managers orquestan; los ResourceAccess son la **única** capa que toca Resources. La transacción atómica se abre con la **`TransactionUtility`** (no con `DataSource` crudo): dentro del `run`, todo verbo sigue pasando por ResourceAccess.
- **Excepción:** las Utilities de infraestructura transversal (`AuditUtility`, `PubSubUtility`) gestionan su propia tabla de infraestructura (`audit_log`, `outbox_event`). La regla aplica a datos de **negocio/dominio**.

### 3.5 Sin acoplamiento físico entre particiones — REGLA NO-NEGOCIABLE
Para que la partición clínica pueda mudarse a su propia instancia (residencia in-country, NFR-45) sin reescribir dominio, está **prohibido**:
- relaciones/FKs de TypeORM (`@ManyToOne/@OneToMany/@JoinColumn`) entre entidades de **dominios distintos** — las referencias cruzadas son **columnas UUID planas**;
- JOINs SQL entre tablas de dominios distintos — los datos de otro dominio se leen con llamadas separadas a su ResourceAccess (réplica de solo-lectura).

### 3.6 Fitness functions (se enforzan en CI)
El build **falla** si:
- Un módulo importa una capa superior (llamada hacia arriba).
- Un Engine referencia otro Engine, o un ResourceAccess otro ResourceAccess.
- Un Client importa un Engine/RA/Utility.
- Existe una llamada síncrona Manager→Manager (deben ir por `PubSubUtility`).
- Un servicio no-dueño referencia un verbo de escritura de otro dominio.
- **Un Manager/Engine/Controller inyecta `@InjectRepository` o `@InjectDataSource`** (§3.4: DB solo vía ResourceAccess).
- Un verbo mutante de ResourceAccess no lleva parámetro de **operation-identity** (idempotencia, NFR-34).
- La evaluación de alertas lee del read model en vez del store clínico de escritura.
- Un registro clínico se commitea sin su obligación de alerta en la misma transacción (outbox).

### 3.7 Autorización — fuente única (PermissionEngine + Ports & Adapters)
La autorización (¿esta cuenta puede leer/registrar sobre este paciente?) la decide **un único** `PermissionEngine`; **ningún Manager decide permisos por su cuenta**. El engine no sabe de dónde salen los datos: depende de un **contrato** (`AuthorityProvider`, patrón *port*) que responde "¿qué rol tiene la cuenta en el vínculo?" y "¿tiene asignación vigente en `at`?" (NFR-30: evaluado al momento de la medición).

- **Puerto (contrato):** `AuthorityProvider` vive en `libs/core` — no depende de ningún dominio.
- **Adapter real:** `KeruAuthorityProvider` vive en la **capa de composición** (`apps/keru-api/src/authorization/`) y lee vínculos (`AccountAccess`) y asignaciones (`HiringAccess`) como réplica de solo-lectura.
- **Cableado:** `AuthorizationModule` (global) provee el engine ya conectado al adapter y lo expone; los dominios inyectan `PermissionEngine`. Así se evita el ciclo con `core` (core no puede importar Membership/Hiring) y se mantiene una sola fuente de autorización.
- **Para tests:** se inyecta un `StubAuthorityProvider` (falso) sin tocar la base.

> Deuda conocida: `HiringManager` hace su chequeo de vínculo inline (`getLink`) en vez de vía `PermissionEngine`, porque importar el AuthorizationModule le crearía un ciclo. Es funcionalmente correcto pero es el único punto donde la autorización no pasa por el engine.

---

## 4. Stack técnico (decidido)

| Decisión | Elección | Notas |
|---|---|---|
| Lenguaje/framework | **NestJS** (Node 20) | Monorepo modular |
| Estructura | **Nest monorepo**: `apps/keru-api` (1 deploy) + `libs/{dominio}` + `libs/core` | Separable por deploy sin reescribir |
| Base de datos | **PostgreSQL** | Dos particiones lógicas: *marketplace* y *clínico+background* (schemas separados) |
| ORM | **TypeORM** | |
| Gestión de esquema | **Migraciones TypeORM versionadas** (`libs/core/src/migrations`, scripts `migration:*`) | `synchronize` puede alterar el store clínico en silencio (viola NFR-25): default apagado, opt-in explícito solo en bases descartables de dev/e2e (KER-29) |
| Outbox / mensajería | **Outbox en Postgres + BullMQ (Redis)** | Commit atómico registro+evento; dispatcher encolado MM→HM, HM→CRM, CRM→CCM |
| Read model (CareConsult) | Diferido en el MVP | Se lee del store clínico directo hasta que la escala pida proyección async |
| Topología de deploy | **1 deploy (monolito modular)** | Primer split futuro: unidad clínica (CareRecord) |

---

## 5. Requisitos no-funcionales críticos (condensado de los 58 NFRs)

Los que un desarrollador **debe** respetar en cada feature (referencia completa: `residual-design.md §Derived NFRs`):

- **NFR-34 — Idempotencia de plataforma.** Todo verbo mutante toma una *operation-identity* del cliente; efecto *at-most-once*. Es la regla de mayor apalancamiento.
  > **Alcance (aclaración).** La clave es obligatoria en toda operación con **efecto no-idempotente** — crea una entidad nueva, **cobra un pago**, o dispara una acción irreversible — sin importar si la origina el cliente, una cola o un **webhook** (una pasarela reentrega webhooks; sin clave = doble cobro). Los verbos **naturalmente idempotentes** (aprobar → sigue aprobado, marcar favorito, set de badges, transiciones de estado con precondición) no la requieren. Estado actual: la llevan los verbos de creación (paciente, cuidador, solicitud, registro clínico); la fitness function está **cableada como lint** (regla local `keru/operation-identity` en `eslint.config.mjs`): todo verbo create/submit/record/register de un ResourceAccess sin `operationId` rompe el build, salvo exención explícita `operation-identity: exempt — <porqué>` (at-most-once por restricción única, o transacción del verbo padre). La emisión de invitaciones queda eximida por diseño de UC-03 (token nuevo por emisión); su idempotencia es decisión pendiente (KER-13).
- **NFR-30 — Autoridad al momento de la medición.** El permiso se evalúa al momento de medir/registrar, no al de sincronizar. Llegadas tardías no autorizadas se ponen en cuarentena, nunca se descartan en silencio.
- **Outbox atómico (Decouple row 35).** Registro clínico + obligación de alerta se escriben en **una transacción**.
- **NFR-36 — Semántica del tiempo.** Tiempo de medición ≠ tiempo de llegada; el historial ordena por tiempo de medición.
- **NFR-16 / NFR-39 — Métricas como datos.** Definición, unidad y bornes de plausibilidad viven en el catálogo; agregar una métrica es un dato, no un proyecto. Los valores llevan valor + unidad.
- **NFR-17 / NFR-28 — Rangos versionados.** Rango aplicable = estrato → override por paciente; efectivo-fechado, nunca sobrescrito; toda evaluación registra qué versión de rango aplicó.
- **NFR-03 / NFR-23 — Términos pinneados.** Las tarifas son efectivo-fechadas; una solicitud fija los términos contra los que se hizo; la aceptación se evalúa contra esos términos.
- **NFR-19 — Invitación.** Válida **30 minutos, un solo uso**, con desafío de identidad al invitado nombrado; el alta se notifica a todo el círculo; emisión y confirmación auditadas.
- **NFR-11 / NFR-26 / NFR-27 — Entrega observable, acuse y escalación de alertas.** Cada notificación persiste su **outcome de entrega por destinatario y canal** (campana `delivered` al persistir; push con el resultado real del envío — "aceptado por el proveedor" nunca es entregado); **entregada ≠ vista**: leerla registra el acuse. Una alerta **crítica** sin acuse del círculo dentro del umbral (`ALERT_ESCALATION_MINUTES`) se re-notifica una vez al círculo. **Anti-T7:** una alerta más nueva del mismo tipo/paciente **supersede** a la anterior no acusada y la saca del circuito de escalación/reenvío — un backlog nunca se convierte en tormenta de alertas obsoletas. El fan-out es idempotente por unique (alerta, destinatario).
- **NFR-14 — Reloj del ciclo de vida.** Toda transición de asignación tiene dueño (actor o timer); la finalización nunca se queda esperando a un actor.
- **NFR-20 / NFR-21 — Reseñas.** Solo con servicio **completado** (la elegibilidad se apoya en la razón terminal `completed`, nunca en la declaración de pago — Decouple row 49); selladas hasta que ambas partes envían o cierra la ventana; **una sola vez, inmutables**.
- **Residencia y aislamiento (NFR-45/46/47/48).** Datos clínicos in-country con claves propias; la unidad clínica sigue operando aunque el marketplace caiga; la carga del marketplace nunca frena el path de escritura/alerta clínico.

---

## 6. Fuera de alcance del MVP (guardarraíles)

**No** diseñar ni implementar:
- Chat en tiempo real familiar↔cuidador.
- Integración con dispositivos médicos / wearables.
- Facturación electrónica y reportes fiscales.
- Verificación automatizada de antecedentes con organismos externos (la verificación es interna/manual, UC-19).

**Pendiente de decisión** (no diseñar aún, pero no bloquear su incorporación futura):
- **Pagos por la plataforma** (Módulo C, **UC-11 reservado**). En el MVP el pago es **fuera de la plataforma**. El cierre de la contratación es independiente del pago: el solicitante completa el servicio y el cierre registra una **razón terminal** estructurada (`completed`, `cancelled-by-{requester|caregiver|admin}`, `no-show`, `end-of-life` — enum extensible, KER-31/KER-32). "Pagado" es una **declaración opcional posterior al cierre** (honor-mark, `paidDeclaredAt`) que no condiciona el cierre ni la elegibilidad de reseña (Decouple row 49, NFR-10/58), para no bloquear la landing futura de pagos.

---

## 7. Decisiones abiertas (NEEDS CLARIFICATION)

Registradas para no olvidarlas; ninguna bloquea el MVP (los contratos están parametrizados):

- **OQ-5 / DV-2:** jurisdicción, regulación y base de consentimiento sin decidir (afecta residencia). El contrato de consentimiento existe parametrizado.
- **UC-18 / NFR-18:** *quién* puede setear un rango por paciente y sus valores por defecto — hueco de negocio.
- **UC-05:** *cuándo* soporte puede asignar manualmente y qué consentimiento aplica.
- **UC-09:** modelo de período de servicio (fijo / recurrente / open-ended) — decisión de producto; el residual usa transiciones timer-driven.
- **DV-12:** qué es una "zona" fuera de CABA — no definido; aislado dentro de `ZoneAccess`.
- **UC-17:** ¿segunda reseña sobre el mismo servicio edita o se prohíbe? El residual la hace inmutable (una sola vez).
- **UC-02 A3:** cambio de **credenciales** (certificaciones/especialidades/nombre) de un cuidador **aprobado** — ¿dispara re-verificación, y de qué tipo (solo la credencial nueva o todo el perfil)? Hasta decidirlo, un perfil aprobado no puede editarlas; solo edita foto, disponibilidad, tarifas (efectivo-fechadas), zona y modalidades.

---

1. Antes de tocar código, leé el caso de uso afectado en `Keru-Casos-de-Uso-MVP.md` (fuente de verdad de producto). Usá la skill `keru-feature`, que institucionaliza este flujo.
2. Todo cambio de comportamiento se refleja **primero** en el UC (fuente de verdad) → luego en el test → luego en el código.
3. Los tests E2E (Playwright, a futuro) se derivan de los **criterios de aceptación** del UC en formato Dado/Cuando/Entonces; no se implementa un flujo cuyo resultado esperado no esté escrito.
4. Si una regla de acá estorba, no la violes: proponé un cambio a este documento con su justificación.
