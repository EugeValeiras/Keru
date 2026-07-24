# Evaluación — Reducir el polling de notificaciones: refetch-por-push / SSE / WebSocket / polling inteligente

- **Fecha:** 2026-07-24
- **Autor:** agente (claude) bajo supervisión de Eugenio Valeiras
- **Tarea:** KER-73 (docs-first)
- **Decisión asociada:** `addl/docs/adr/ADR-0004-canal-de-notificaciones-refetch-por-push-ahora-sse-diferido.md`
- **Back-channel al SAD (needs-architecture):** `docs/developer/back-channel/2026-07-24-notification-stream-sse.md`
- **Estado:** Propuesta para aprobación

---

## 1. Motivación y observación

Eugenio observó (2026-07-24) que el front hace muchos llamados a `GET /api/v1/notifications/unread-count` y propuso un WebSocket. Este documento evalúa esa idea **antes** de invertir, siguiendo el proceso ADDL (docs-first): pasar de polling a un canal persistente es un **cambio de arquitectura**, no una decisión Tier-2 absorbible sin registro.

## 2. Estado actual (verificado en el código)

### 2.1 Los tres pollers

| Poller | Archivo | Intervalo | Endpoint | Pausa en `hidden` | Refetch on-focus |
|---|---|---|---|---|---|
| Campana (badge de no-leídas) | `Keru-Webapp core/notifications/notification.store.ts:7` | 45 s | `GET /notifications/unread-count` | Sí | Sí (`visibilitychange`) |
| Solicitudes del cuidador | `Keru-Webapp core/hiring/caregiver-requests.store.ts:6` | 60 s | `GET /caregiver/requests` (cuenta `pending` en cliente) | Sí | Sí |
| Dashboard del paciente | `Keru-Webapp features/care/patient-dashboard-page.ts:19` | 45 s | `GET` de estado del paciente (UC-14) | Sí | Sí |

Los tres comparten el mismo patrón: `setInterval` + guarda `!document.hidden && isAuthenticated()` + refetch en `visibilitychange`. Es decir, **el polling ya está optimizado**: una pestaña de fondo no consume nada, y volver al foco refresca al instante.

### 2.2 Lo que YA existe (reusable)

- **Web Push (VAPID / RFC 8292) end-to-end.** `libs/care-record/src/resource-access/web-push.transport.ts` (`WebPushTransport.deliver`), suscripciones por cuenta revocables (`push-subscription.access.ts`), `GET/POST/DELETE /notifications/push/*`, y `public/sw.js` que recibe el push y muestra la notificación del navegador. La entrega es **best-effort adicional**; la campana in-app es la garantía (constitution §2.7, NFR-09).
- **Camino de entrega post-commit.** `CareRecordManager` persiste la notificación de campana **atómicamente** con el cambio de estado y luego, **después del commit**, dispara `dispatchPush(...)`. Ese punto post-commit es el **hook natural** para cualquier "empujón" adicional (refetch o SSE).
- **Redis 7 + BullMQ.** El outbox es una tabla Postgres (`outbox-event.entity.ts`) drenada por un worker BullMQ sobre Redis. El estado de verdad es Postgres; **Redis es solo el mecanismo** (`pubsub.util.ts`). La denylist de `jti` (NFR-41) ya **reutiliza el cliente ioredis subyacente de BullMQ** (`token-revocation.util.ts`), así que hay una conexión Redis disponible para pub/sub sin sumar dependencia.
- **NFR-41 (logout revoca el canal).** El logout server-side deslista el `jti` y revoca las push subscriptions de la sesión vía el evento outbox `SessionRevoked` (constitution §NFR-33/41).

### 2.3 Lo que NO existe

- **Sin infra WebSocket:** no hay `socket.io`, `@nestjs/websockets` ni `ws` en `package.json`. Solo `web-push` y `rxjs`.
- **Sin canal server→cliente en vivo:** el SAD naive lo dice explícito — la frescura se asume cubierta por *escrituras síncronas + lecturas iniciadas por el cliente*, "no eventing, streaming, or push architecture" (`residual-design.md`, `naive-architecture.md §Freshness`). El único canal server→cliente es el device-push (adicional, NFR-09).

## 3. El problema real: frescura, no carga

### 3.1 Costo actual del polling (modelado — no hay APM ni usuarios de producción)

No hay métricas en producción (ADR-0001: MVP "aceptado sin usuarios reales en producción") ni instrumentación de RPS. Modelamos el costo con la geometría del poller (pausado-en-hidden ⇒ solo cuentan las pestañas **en foco**):

```
RPS(unread-count)  ≈ F_fg / 45      # F_fg = sesiones de familia con la pestaña en foco
RPS(dashboard)     ≈ D_fg / 45      # solo mientras una vista de dashboard está abierta
RPS(requests)      ≈ C_fg / 60      # sesiones de cuidador con la bandeja en foco
```

| Sesiones en foco (F_fg) | RPS de `unread-count` |
|---|---|
| 100 | ≈ 2,2 |
| 1.000 | ≈ 22 |
| 10.000 | ≈ 222 |

Más las ráfagas on-focus (1 llamado por re-foco, con ritmo humano, acotadas). El endpoint `unreadCount(accountId)` es un **`COUNT` indexado** por `(recipient, read)` sin joins: costo sub-ms a pocos-ms por llamada.

**Lectura honesta:** en escala MVP/temprana el polling es **barato en términos absolutos**, y su mayor desperdicio (pestañas de fondo) ya está eliminado por la pausa-en-hidden. El argumento de *carga* para un canal recién se vuelve real a ~10k+ sesiones concurrentes en foco **y** si el `COUNT` o el overhead de conexión se miden como cuello de botella — nada de eso está instrumentado hoy.

### 3.2 El beneficio que SÍ es real e independiente de la escala: frescura

El badge puede atrasarse **hasta el intervalo de poll (≤45 s)** respecto de un evento real. NFR-42 / OQ-6 fijan un bound **configurable de 3-5 s** para `record→visible` y `record→delivered`: el **push** ya lo cumple (casi instantáneo), pero el **badge in-app por polling NO**. Cerrar esa brecha es el valor concreto del pedido — y no depende de la escala.

### 3.3 El verdadero trade-off arquitectónico

Un canal persistente **no elimina costo, lo cambia de forma**: se cambian `N/45` `COUNT` baratos por segundo por **N conexiones sostenidas** (presión de requests/seg → presión de conexiones concurrentes: memoria + slot de event-loop + fan-out). En un solo proceso Node/Nest, unos pocos miles de conexiones SSE ociosas son manejables; decenas de miles requieren tuning y el fan-out por Redis (multi-instancia). Ese costo solo se justifica una vez medido.

## 4. Las cuatro opciones

### A) Refetch disparado por Web Push (reuso de lo que ya hay)

El `push` handler de `sw.js` hace `clients.matchAll()` → `postMessage({type:'refresh-notifications'})`; un servicio del shell invalida el signal del `NotificationStore` → refetch de `unread-count`/lista. **Cero infra nueva de servidor.**

- **Frescura:** ~1 s para alertas reales (el push ya se dispara en el mismo instante del evento). Cobertura buena para el badge: el push llega justo cuando el badge debe moverse.
- **Límites:** requiere permiso de push otorgado (usuario que lo negó no gana nada extra — pero la campana por polling sigue como piso); best-effort/background.
- **Alcance:** ayuda al badge de campana directo; ayuda a `requests`/`dashboard` solo si esos eventos también emiten push (hiring ya empuja push al círculo).
- **Costo:** ~unas líneas en `sw.js` + un listener chico en el shell.
- **Absorción ADDL:** **absorbida** (Tier-2). No suma servicio ni cambia call rules; reusa el camino `NotificationAccess`/`WebPushTransport`.

### B) SSE — Server-Sent Events (`@Sse()` de Nest)

Canal server→cliente **unidireccional** sobre HTTP con el mismo JWT. Emite `{type:'unread', count}` / `{type:'notification'}` a la cuenta del token. Punto medio recomendado para un roadmap de tiempo-real liviano.

- **Frescura:** ~1 s, para todos (no depende del permiso de push).
- **Alcance:** un **canal compartido** puede servir a los tres pollers (badge + requests + dashboard).
- **Multi-instancia:** fan-out por **Redis pub/sub** reusando el ioredis de BullMQ; cada instancia reenvía a sus clientes.
- **Cierre en logout (NFR-41):** hay que **tear-down del stream** en `SessionRevoked` / al deslistar el `jti`.
- **Auth wrinkle:** `EventSource` no manda headers → hay que pasar el JWT por query o cookie, **lo cual choca con "sin secretos en la URL del stream"**. Preferir **fetch-stream con `Authorization`**, o un **ticket de stream corto y de un solo uso** (no el JWT crudo en la URL).
- **Costo:** superficie nueva server→cliente (un componente de streaming), wiring de Redis pub/sub, ciclo de vida de conexión, fallback a polling.
- **Absorción ADDL:** **needs-architecture.** Introduce una superficie de streaming **ausente del service catalog** (`NotificationAccess` es device-push, no streaming a clientes) y una conexión sostenida es un **residuo nuevo** (storms de reconexión, fan-out, backpressure) que el SAD naive excluyó explícitamente. Requiere **back-channel al SAD** (enmienda de catálogo + NFR), no un absorb inline (regla D-01 Architecture Supremacy).

### C) WebSocket (`@nestjs/websockets` + socket.io + `@socket.io/redis-adapter`)

Bidireccional, el más capaz y el más caro. Auth en el handshake, heartbeat/reconexión, adapter de Redis para fan-out multi-instancia, fallback a polling.

- **Cuándo se justifica:** solo con un roadmap de tiempo-real más amplio (vitales en vivo, presencia, chat). Para un **contador de badge** (unidireccional) es sobre-ingeniería.
- **Costo:** dependencias nuevas (gateway + adapter), la superficie más grande, más residuo que B.
- **Absorción ADDL:** **needs-architecture** (mayor que B).

### D) Polling más inteligente (lo más barato)

Subir el intervalo, refetch on-focus (**ya implementado**) y refetch al recibir un push (= A). Sin canal nuevo.

- **Absorción ADDL:** **absorbida.** Puro tuning de cliente + reuso. En la práctica, D = A + ajuste de intervalos.

## 5. Comparación

| Criterio | A) Refetch-por-push | B) SSE | C) WebSocket | D) Polling inteligente |
|---|---|---|---|---|
| Frescura del badge | ~1 s (si push on) | ~1 s (todos) | ~1 s (todos) | ≤ intervalo (≥45 s) |
| Infra nueva de servidor | Ninguna | Media (streaming + Redis fan-out) | Alta (gateway + adapter + deps) | Ninguna |
| Complejidad de cliente | Baja | Media (auth EventSource, reconexión) | Media-alta | Nula (ya está) |
| Reduce polling steady-state | No (queda como piso) | Sí (canal compartido) | Sí | Parcial (tuning) |
| Sirve a los 3 pollers | Parcial (si hay push) | Sí | Sí | No |
| Bidireccional | No | No | Sí | No |
| Encaje con escala (multi-inst.) | N/A | Redis pub/sub (reusa BullMQ) | Redis adapter | N/A |
| Absorción ADDL | **Absorbida (Tier-2)** | **needs-architecture** | **needs-architecture** | **Absorbida** |

## 6. Requisitos transversales del canal elegido (criterio 4)

Cualquier canal persistente (B o C), cuando se implemente, debe cumplir:

1. **Auth (JWT):** el mismo JWT que el resto de la API. Sin secretos en la URL del stream (usar fetch-stream con `Authorization` o ticket corto de un solo uso).
2. **Cierre/revocación en logout (NFR-41):** tear-down del stream en `SessionRevoked` / al deslistar el `jti`; coherente con la revocación de push subs existente.
3. **Escalado multi-instancia:** fan-out por **Redis pub/sub** reusando el ioredis de BullMQ (SSE) o el `@socket.io/redis-adapter` (WS). Postgres sigue siendo la verdad; Redis es el mecanismo (§3.5 se preserva).
4. **Degradación graceful a polling:** el polling **permanece como piso** (NFR-09 / I6: la campana in-app es la garantía, un canal en vivo nunca es el único registro). Si el canal cae, se sigue con polling sin pérdida.
5. **No degradar el Web Push existente:** el push adicional (UC-18) sigue intacto.
6. **Tests sin tiempos reales:** el e2e mockea el canal, no depende de timers reales.

## 7. Alcance del canal (criterio 5)

- **Fase 1 (A + D):** solo el badge de campana gana frescura por push; los otros pollers siguen con su polling optimizado (que ya es barato).
- **Fase 2 (B / SSE), si se aprueba:** canal **compartido** para los tres pollers (badge + requests + dashboard), justamente porque SSE amortiza mejor su costo sirviendo a varios consumidores. La decisión de incluir requests/dashboard se toma al aprobar la Fase 2, no ahora.

## 8. Recomendación

**Fase 1 — ahora, absorbida (Tier-2), en un ticket de implementación aparte: `D + A`.**
Mantener el polling como piso garantizado (NFR-09/I6) y sumar el **empujón Web-Push→postMessage→refetch** (A): cuando dispara una alerta real, el badge se actualiza en ~1 s en vez de ≤45 s. Cierra la brecha de frescura NFR-42 para el badge (usuarios con push) a costo ~cero y **sin arquitectura nueva**.

**Fase 2 — solo si dispara un trigger medido: `B (SSE)`, vía back-channel al SAD (needs-architecture).**
SSE (no WS: el payload es unidireccional) como canal compartido para los tres pollers, **después** de: (a) instrumentar NFR-42 (prerrequisito ya pendiente en ADR-0001) y **medir** el RPS de `unread-count` / la brecha de frescura reales; y (b) que el SAD aterrice la superficie de streaming como decisión de arquitectura (enmienda de catálogo + NFR). Ver el back-channel en `docs/developer/back-channel/2026-07-24-notification-stream-sse.md`.

**Reservar `C (WS)`** para cuando aterrice una feature genuinamente bidireccional/tiempo-real-pesada (vitales en vivo, presencia, chat): ahí el costo WS + Redis-adapter se justifica por algo más que un badge.

## 9. Trazabilidad

- **Casos de uso / NFR:** UC-18 (campana), NFR-09 (independencia de canal — preservada), NFR-42 / OQ-6 (frescura 3-5 s — mejorada para el badge), NFR-41 (logout revoca el canal — preservado; SSE lo extendería al tear-down del stream). ADR-0001 (señal de split / prerrequisito de instrumentar NFR-42).
- **Impacto (regla impact-on-add del proceso developer):**
  - **Affected:** `NotificationController`/`CareRecordManager` (camino de entrega), `sw.js` (cliente), `NotificationStore`/`CaregiverRequestsStore`/`PatientDashboard` (pollers). NFRs: NFR-09, NFR-42, NFR-41.
  - **Absorption:** Fase 1 (A+D) = **absorbed** (Tier-2, sin servicio nuevo, reusa el camino de push). Fase 2 (B/SSE) = **needs-architecture** (superficie de streaming + NFRs de fan-out). C (WS) = **needs-architecture** (mayor).
  - **Rationale:** A/D reusan componentes existentes y no cambian call rules; un canal de streaming sostenido es un residuo nuevo (superficie de conexión sostenida, fan-out, backpressure) ausente del catálogo y excluido explícitamente por el SAD naive, así que reabre S3/S5 vía back-channel, no se absorbe inline (D-01).
