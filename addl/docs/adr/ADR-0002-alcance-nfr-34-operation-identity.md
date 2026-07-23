# ADR-0002 — Alcance de NFR-34: operation-identity solo en efectos no-idempotentes

- **Estado:** Aceptado (retroactivo, 2026-07-23)
- **Decisores:** Eugenio Valeiras (product owner) + agente supervisor
- **Referenciado desde:** `constitution.md §5 (NFR-34)`, `residual-design.md NFR-34`, auditoría `docs/audit/addl-gaps-2026-07-22.md §4.4`
- **Tareas:** KER-37 (registro de la relajación hecha en el condensado)

## Contexto

El residual exige el contrato de idempotencia más amplio del sistema: *"**Every mutating verb** on every ResourceAccess takes a client-supplied operation identity; effect is at-most-once"* (NFR-34, Hyperliminal Coupling #42 — "the single highest-leverage P-raising contract in the system"). La constitution, al condensarlo, **relajó el alcance**: la clave es obligatoria solo en verbos con **efecto no-idempotente** (crear entidad, cobrar, acción irreversible), y los verbos naturalmente idempotentes (aprobar→sigue aprobado, favoritos, set de badges, transiciones con precondición) quedan exentos con comentario `operation-identity: exempt — <porqué>`. Esa relajación se hizo en el condensado sin registro; la auditoría 2026-07-22 la marcó como ambigüedad a no decidir en silencio.

## Decisión

Se **ratifica la relajación** como decisión registrada:

1. La operation-identity es obligatoria en toda operación con efecto no-idempotente, **sin importar el origen** (cliente, cola o webhook — una pasarela reentrega webhooks; sin clave = doble cobro).
2. Un verbo naturalmente idempotente puede eximirse **solo** con la exención comentada `operation-identity: exempt — <porqué>` (at-most-once garantizado por restricción única o por la transacción del verbo padre), visible en el code review y verificada por la regla lint `keru/operation-identity` (`eslint.config.mjs`), que rompe el build ante un verbo create/submit/record/register sin `operationId` ni exención.

## Racional

El objetivo del residuo #42 es **at-most-once observable**, no el ritual de la clave: en un verbo cuyo re-intento colapsa por semántica (idempotencia natural) o por restricción única, la clave agrega superficie sin agregar garantía. La exención comentada + lint conserva lo que el residual protege (ningún efecto duplicado silencioso) y deja la desviación auditable verbo por verbo.

## Consecuencias

- El residual (**"every mutating verb"**) queda formalmente desviado; este ADR es el registro de esa desviación. Ante un verbo dudoso, la regla dura es la del residual: se pone la clave.
- Los **verbos de pago futuros (UC-11) llevan clave siempre** — NFR-10 los exige idempotentes bajo NFR-34 y no admiten exención.
- La emisión de invitaciones queda eximida por diseño de UC-03 (token nuevo por emisión); su idempotencia sigue como decisión pendiente (KER-13), fuera de este ADR.
