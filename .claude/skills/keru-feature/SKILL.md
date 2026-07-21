---
name: keru-feature
description: Usar SIEMPRE antes de sumar una feature nueva, modificar un flujo, o hacer cualquier cambio de comportamiento en el proyecto Keru (backend NestJS). Obliga a leer la constitution y analizar los casos de uso existentes para entender qué está creado y cómo, antes de escribir código. Se dispara ante pedidos como "agregá", "sumá una feature", "cambiá el flujo de", "modificá", "implementá el caso de uso", "quiero que ahora también...".
---

# Feature / cambio en Keru — flujo obligatorio docs-first

Keru es un backend NestJS (monolito modular, arquitectura IDesign residual). Todo cambio se hace **docs-first**: la spec del caso de uso es la fuente de verdad, el código se deriva de ella. Nunca al revés.

## Regla de oro
**No escribas ni modifiques código sin antes leer la constitution y la(s) spec(s) del/los caso(s) de uso afectado(s).** Si el flujo no está documentado, primero se documenta.

## Paso 1 — Leer las reglas no-negociables (obligatorio, siempre)
Leé `constitution.md` en la raíz del repo. Prestá atención especial a:
- **§2 Principios de producto** — control de acceso por rol Y vínculo, trazabilidad clínica, aprobación previa, alertas con campana, una cuenta/varios pacientes.
- **§3.2 Call Rules** — qué capa puede llamar a cuál (arquitectura cerrada). Nunca las violes.
- **§3.3 Dueño único de escritura** — qué módulo puede escribir qué.
- **§3.4 Fitness functions** — lo que rompe el build; tu cambio no puede disparar ninguna.
- **§5 NFRs críticos** — sobre todo NFR-34 (idempotencia: todo verbo mutante lleva operation-identity), NFR-30 (permiso al momento de la medición), outbox atómico, rangos versionados, términos pinneados.
- **§6 Fuera de alcance / §7 Decisiones abiertas** — no implementes nada de acá sin decisión explícita.

## Paso 2 — Analizar los casos de uso existentes (obligatorio)
1. Abrí `Keru-Casos-de-Uso-MVP.md` (la **fuente de verdad** de producto: los 21 casos de uso con actores, flujos, criterios de aceptación y modelo de dominio).
2. Identificá **a qué caso(s) de uso** toca el pedido. Si es una feature nueva, ¿extiende un UC existente (UC-NN) o es uno nuevo? Ubicá el/los UC por su número dentro de su módulo (A..H).
3. Leé la(s) sección(es) completa(s) del/los UC: descripción, flujo principal, flujos alternativos/excepciones, precondiciones/postcondiciones y criterios de aceptación. Cruzá con la §5 (modelo de dominio) y la §6 (NFR) del mismo documento.
4. Determiná **a qué módulo de dominio** pertenece (Membership / Hiring / CareRecord / CareConsult / Reputation) y **en qué capa** cae el cambio (Manager / Engine / ResourceAccess). Confirmá el dueño de escritura (constitution §3.3).

## Paso 3 — Entender lo ya construido
Antes de agregar, revisá qué existe en el código para **reutilizar, no duplicar**:
- Módulo del dominio en `libs/<dominio>/src/` (manager, engines, resource-access).
- Piezas compartidas en `libs/core/src/` (PermissionEngine, PubSub/outbox, Audit, bases TypeORM).
- Entidades y verbos ya definidos en el ResourceAccess correspondiente.
Si algo parecido ya existe, extendelo (regla del "smallest set"); no crees un componente nuevo salvo que un residuo estructural lo justifique.

## Paso 4 — Documentar primero (spec como contrato)
- **Cambio a un flujo existente:** editá el/los UC afectado(s) en `Keru-Casos-de-Uso-MVP.md` — actualizá descripción, flujo, flujos alternativos y criterios de aceptación. Si cambia el modelo, actualizá también la §5 (dominio) del mismo documento.
- **Feature nueva:** agregá un nuevo `UC-NN` dentro de su módulo en `Keru-Casos-de-Uso-MVP.md` (respetá el estilo existente: actor, referencia, descripción, precondiciones, flujo principal, alternativos, postcondiciones, criterios de aceptación). Recordá que **UC-11 está reservado** para pagos.
- Si el cambio toca una regla no-negociable, primero proponé el ajuste a `constitution.md` con su justificación.

## Paso 5 — Test antes que código
Traducí los **criterios de aceptación** y el flujo del UC a tests (E2E/integración) en formato Dado/Cuando/Entonces: un camino feliz + los alternativos + los de error. Deben fallar antes de implementar (red), y son el criterio de "listo".

## Paso 6 — Implementar respetando la arquitectura
- Respetá las Call Rules y el dueño único de escritura (Paso 1).
- Todo verbo mutante de ResourceAccess lleva `operationId` (idempotencia).
- Registros clínicos: commit atómico registro+alerta (outbox). Permiso evaluado al momento de la medición.
- Comunicación entre Managers de distinto dominio: **solo encolada** (PubSubUtility), nunca llamada síncrona.
- Corré el lint de fronteras (fitness functions) y los tests. El build no puede quedar rojo.

## Paso 7 — Cerrar
- Verificá que cada criterio de aceptación del UC quede cubierto por un test.
- Si tocaste un flujo, dejá el/los UC de `Keru-Casos-de-Uso-MVP.md` coherentes con lo implementado.
- Resumí qué UC/NFR cubrió el cambio (trazabilidad).

## Checklist rápido
- [ ] Leí `constitution.md` (call rules, dueño de escritura, NFRs, alcance).
- [ ] Identifiqué y leí el/los UC afectado(s) en `Keru-Casos-de-Uso-MVP.md`.
- [ ] Ubiqué módulo + capa + dueño de escritura.
- [ ] Revisé qué ya existe para reutilizar.
- [ ] Documenté el cambio en el UC (o creé el UC nuevo) ANTES de codear.
- [ ] Escribí/actualicé los tests (Dado/Cuando/Entonces) desde los criterios de aceptación.
- [ ] Implementé sin violar call rules ni fitness functions.
- [ ] Dejé la trazabilidad UC/NFR.
