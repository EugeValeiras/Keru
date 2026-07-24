# ADR-0004 — Canal de notificaciones: refetch-por-push ahora (absorbido), SSE diferido (needs-architecture), WebSocket reservado

- **Estado:** Propuesto (2026-07-24) — pendiente de aprobación del product owner
- **Decisores:** Eugenio Valeiras (product owner) + agente supervisor
- **Referenciado desde:** `constitution.md §2.7 / NFR-09 (independencia de canal)`, `NFR-42 / OQ-6 (frescura 3-5 s)`, `NFR-41 (logout revoca canal)`, `ADR-0001 (topología monolito + señal de split)`
- **Documento de evaluación:** `addl/docs/documents/2026-07-24-evaluacion-canal-notificaciones.md`
- **Back-channel al SAD:** `docs/developer/back-channel/2026-07-24-notification-stream-sse.md`
- **Tareas:** KER-73 (esta decisión, docs-first). La implementación de Fase 1 va en un ticket siguiente.

## Contexto

El front hace polling de `GET /api/v1/notifications/unread-count` (campana, 45 s) y hay otros dos pollers (solicitudes del cuidador 60 s, dashboard del paciente 45 s). Eugenio propuso un WebSocket. Verificado en el código (2026-07-24):

- Los tres pollers ya están **pausados con la pestaña oculta** y refrescan on-focus: el mayor desperdicio (pestañas de fondo) ya está eliminado.
- **Ya existe Web Push** (VAPID) end-to-end con entrega post-commit (`CareRecordManager.dispatchPush`), revocado en logout (NFR-41). No hay infra WebSocket. Hay Redis 7 + BullMQ (su ioredis es reusable para pub/sub).
- El costo del polling, **modelado** (no hay APM ni usuarios de producción — ADR-0001), es bajo en escala MVP: `unread-count` es un `COUNT` indexado; ~2,2 rps por cada 100 sesiones en foco. El pedido no ataca un problema de **carga** medido, sino de **frescura**: el badge puede atrasarse ≤45 s, y NFR-42/OQ-6 fija un bound de 3-5 s que el push cumple pero el badge por polling no.

Pasar de polling a un canal persistente es un **cambio de arquitectura** (proceso ADDL): no se decide arbitrariamente ni se absorbe en silencio como Tier-2. Este ticket es docs-first: produce la evaluación + esta decisión; la implementación es un ticket aparte.

## Decisión

1. **Fase 1 — ahora (absorbida, Tier-2):** cerrar la brecha de frescura del badge **reusando el Web Push existente**. El service worker (`sw.js`), al recibir un push, hace `postMessage('refresh-notifications')` a las pestañas abiertas; un servicio del shell invalida el signal del `NotificationStore` y refetchea `unread-count`/lista. El **polling permanece como piso** garantizado. Sin infra nueva de servidor, sin cambio de call rules, sin servicio nuevo. Se combina con tuning de polling (Opción D: intervalos + on-focus, ya presente). Va en un **ticket de implementación siguiente** con su propia verificación.

2. **Fase 2 — diferida y condicionada (needs-architecture):** si se decide reducir el polling steady-state con un canal en vivo, la opción es **SSE** (`@Sse()`), **no WebSocket** — el payload (contador + lista bajo demanda) es unidireccional. SSE queda **marcado `needs-architecture`**: introduce una superficie de streaming server→cliente ausente del service catalog y un residuo nuevo (conexión sostenida, fan-out, backpressure) que el SAD naive excluyó explícitamente. Por regla D-01 (Architecture Supremacy) **no se absorbe inline**: se emite el **back-channel al SAD** (enmienda de catálogo + NFR de streaming). Precondición dura antes de invertir: instrumentar NFR-42 (prerrequisito ya listado en ADR-0001) y **medir** el RPS real y la brecha de frescura.

3. **WebSocket — reservado:** solo se justifica cuando aterrice una feature genuinamente bidireccional / tiempo-real-pesada (vitales en vivo, presencia, chat). Para un badge es sobre-ingeniería.

4. **Requisitos transversales de cualquier canal persistente (Fase 2):** auth por JWT **sin secretos en la URL** (fetch-stream con `Authorization` o ticket corto de un solo uso); tear-down en logout (NFR-41); fan-out multi-instancia por Redis pub/sub (reusa el ioredis de BullMQ; Postgres sigue siendo la verdad, §3.5 preservado); **degradación graceful a polling** (NFR-09/I6: la campana in-app es la garantía, un canal en vivo nunca es el único registro); no degradar el Web Push existente; e2e con el canal mockeado (sin timers reales).

## Racional

- El pedido nace de una observación de *cantidad de llamados*, pero el llamado es barato y ya está pausado-en-hidden; el valor real y escala-independiente es **frescura**, que la Opción A entrega a costo ~cero reusando lo que ya hay. Empezar por A/D respeta el "smallest set" y evita over-engineering para un badge.
- Un canal persistente **cambia la forma del costo** (requests/seg → conexiones sostenidas + fan-out): un compromiso que solo conviene tomar con una medición que hoy no existe. Por eso SSE se difiere y se condiciona a instrumentar NFR-42 primero.
- SSE domina a WS para este payload: mismo beneficio de frescura, unidireccional, autenticable con el mismo JWT y cerrable en logout, sin gateway ni adapter. WS agrega bidireccionalidad que un contador no necesita.
- Tratar SSE como `needs-architecture` (y no como Tier-2) es lo que exige el proceso: la superficie de streaming no está en el catálogo y el SAD naive la excluyó — reabrirla es del SAD, no del developer (D-01).

## Consecuencias

- **Positivo:** frescura del badge en ~1 s para usuarios con push, ya; cero deuda de infra; el polling sigue como piso a prueba de fallos (NFR-09). La decisión pesada (canal persistente) queda registrada, condicionada y con su back-channel, no tomada a ciegas.
- **Negativo asumido:** la Fase 1 no reduce el polling steady-state (queda como fallback) y no mejora la frescura de quien negó el push (sigue con ≤45 s, aceptable: la campana es el piso). Los pollers de requests/dashboard no ganan frescura hasta la Fase 2.
- **Reversibilidad:** alta. La Fase 1 es aditiva (un `postMessage` + un listener); quitarla deja el polling intacto. La Fase 2 no se implementa sin aprobación arquitectónica.
- **Trazabilidad:** UC-18; NFR-09 (preservado), NFR-42/OQ-6 (mejorado para el badge), NFR-41 (preservado; SSE lo extendería), ADR-0001 (instrumentar NFR-42 es prerrequisito compartido).

## Impact assessment (regla impact-on-add, proceso developer v0.1.6)

- **Affected:** `NotificationController` / `CareRecordManager` (camino de entrega post-commit), `sw.js` + shell (cliente), `NotificationStore` / `CaregiverRequestsStore` / `PatientDashboard` (pollers). NFRs: NFR-09, NFR-42, NFR-41.
- **Absorption:** Fase 1 (A+D) = **absorbed** (Tier-2). Fase 2 (B/SSE) = **needs-architecture**. WS = **needs-architecture**.
- **Rationale:** A/D reusan componentes existentes sin tocar call rules; el canal de streaming sostenido es un residuo nuevo ausente del catálogo y excluido por el SAD naive, así que reabre S3/S5 vía back-channel, no se absorbe inline (D-01 Architecture Supremacy).
