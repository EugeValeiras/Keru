# Back-channel request al SAD — Superficie de streaming server→cliente (SSE) para notificaciones

- **Fecha:** 2026-07-24
- **Emisor:** developer (agente claude) bajo supervisión de Eugenio Valeiras
- **Tarea:** KER-73
- **Tipo:** catalog amendment + NFR request (needs-architecture)
- **Estado:** Abierto — **no** desbloquea implementación hasta un re-land upstream (`arch-X.Y.Z`)
- **Origen:** `addl/docs/adr/ADR-0004-canal-de-notificaciones-refetch-por-push-ahora-sse-diferido.md` (Fase 2), evaluación en `addl/docs/documents/2026-07-24-evaluacion-canal-notificaciones.md`

## Por qué es un back-channel (D-01 Architecture Supremacy)

La Opción B (SSE) para reducir el polling steady-state introduce algo que **el service catalog no provee**: un canal de **streaming server→cliente sostenido**. El `NotificationAccess` residual expone solo el device-push (`NotifyDevice`, adicional, NFR-09), y el SAD naive declara explícitamente que la frescura se cubre con *lecturas iniciadas por el cliente*, "no eventing, streaming, or push architecture" (`residual-design.md`, `naive-architecture.md §Freshness`). El developer **no inventa** la superficie ni el NFR inline; los solicita al SAD.

## Qué se solicita

1. **Enmienda de catálogo:** una superficie de streaming server→cliente (p. ej. `NotificationStreamAccess` o un endpoint `@Sse('/notifications/stream')` bajo CareRecord) que empuje `{type:'unread', count}` / `{type:'notification'}` a la cuenta del token. Categoría y call rules a decidir por el SAD.
2. **NFR nuevo (residuo de conexión sostenida):** contrato para el residuo que esta superficie abre — storms de reconexión, fan-out multi-instancia, backpressure, límite de conexiones por instancia. Debe articularse con NFR-42 (frescura), NFR-41 (revocación en logout) y §3.5 (sin acoplamiento físico entre particiones).
3. **Encaje con la señal de split (ADR-0001):** un canal con fan-out por Redis toca el escalado multi-instancia; evaluar si adelanta o reordena la señal de split de la unidad clínica.

## Residuo que abre (para el análisis del SAD)

- Conexión HTTP sostenida por sesión en foco → presión de conexiones concurrentes (memoria + event-loop) en vez de RPS.
- Fan-out multi-instancia: cada instancia solo ve a sus clientes conectados → hace falta pub/sub (Redis, reusando el ioredis de BullMQ) para que un evento en la instancia X llegue al cliente conectado a la instancia Y.
- Backpressure / clientes lentos / reconexión (EventSource re-conecta solo; hay que idempotencia del último `count`).
- Auth de `EventSource` sin headers → **restricción dura: sin secretos en la URL del stream** (fetch-stream con `Authorization` o ticket corto de un solo uso).

## Precondición de medición (antes de invertir)

Instrumentar NFR-42 (record→visible / record→delivered), hoy sin métricas — es además el prerrequisito de la señal de split 1 de ADR-0001. Con eso, **medir** el RPS real de `unread-count` y la brecha de frescura antes de aprobar la construcción del canal. Sin medición, la Fase 1 (refetch-por-push, ya absorbida) es suficiente.

## Resolución esperada

Un re-land del SAD (`arch-X.Y.Z`) que aterrice la superficie + su NFR, contra el cual la implementación de Fase 2 se regenera fresca como `absorbed`. Hasta entonces, este request queda **abierto** y la implementación del canal persistente **no** procede (solo la Fase 1 del ADR-0004).
