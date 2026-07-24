# Order-flake de `email-verification.spec.ts` en la suite Playwright full (KER-72)

> **En una línea.** El rojo intermitente de `email-verification.spec.ts` no era la feature ni el
> throttle: era **axe muestreando el texto de las cards del marketplace a mitad del fade-in
> escalonado** (`.kr-stagger`, `opacity < 1`). Con la card semitransparente, axe compone el color
> con el fondo blanco y el contraste cae por debajo de AA → `color-contrast` (serious) transitorio.

## Síntoma

`Keru-Webapp/e2e/email-verification.spec.ts` (el test "tras el self-signup aparece el banner de
verificación con reenviar") fallaba **order/data-flaky**: aislado pasaba, pero en la suite completa
a veces caía y "pasaba al re-run". Rompió falsamente los CI de KER-49/52/55/71.

## Evidencia (ground truth)

Reproducido en el verify aislado corriendo la suite **full** con `--retries=0` y un volcado
temporal de los datos que axe computa. La violación real:

```
color-contrast (serious)  fgColor=#7d7686  bgColor=#fefefe  contrastRatio=4.33  (esperado 4.5:1)
→ .p-6.hover:shadow-card-hover.transition-shadow:nth-child(10|11) > … .text-ink-500…
```

- `#7d7686` **no es un token**: es `--color-ink-500` (`#6f6779`, el texto atenuado de la card:
  zona, "Sin reseñas", modalidades, "/hora") **compuesto al ~90 % de opacidad sobre blanco**.
  `#6f6779` da 5.40:1 sobre blanco en reposo, pero al 90 % de opacidad blende a `#7d7686` = 4.33:1.
- Los nodos que fallan son las cards **9ª/10ª/11ª**.

## Causa raíz

La grilla del marketplace entra con `.kr-stagger` (fade-in `opacity 0→1`, `kr-rise` en
`src/styles.css`). El escalón es de 45 ms hasta la 8ª card; **de la 9ª en adelante entran juntas
con el retardo máximo** (`animation-delay: 360ms` + `0.35s` de duración ⇒ cierran a ~710 ms).

`expectAxeClean` esperaba red quieta + fuentes + imágenes + fondo de la primera card + `400ms`.
Ese settle **no alcanza** para que las cards tardías cierren su fundido: cuando hay muchos
cuidadores en la página 1 (estado que varía según qué dejaron los specs previos → de ahí el
carácter *order/data*), axe corre con las cards 9+ todavía a `opacity ~0.90` y su texto atenuado
compuesto contra el blanco cae a 4.33:1. Con pocas cards (aislado) el fundido ya cerró → verde.

Es el **mismo mecanismo** que el nodo `kr-badge[tone=success]` que el supervisor vio en otro run
(run 30121477482): el badge success a mitad del fade-in también compone sus colores y su margen
(4.77:1 en reposo) no sobrevive el `opacity < 1`. No es una violación AA real en reposo de ninguno
de los dos: es un artefacto de muestreo a mitad de animación.

`reducedMotion: 'reduce'` (playwright.config) debería apagar `.kr-stagger`; en el harness
observamos el fundido corriendo igual (de ahí `opacity 0.90`), así que **no dependemos** de esa
emulación: el fix espera explícitamente a que el fundido cierre.

## Fix

**Raíz (infra de test, sin tocar producción)** — `e2e/email-verification.spec.ts`,
`expectAxeClean`: antes de correr axe, esperar a que el marketplace esté **asentado**:

- no queden skeletons (`.kr-shimmer`),
- toda card (`.p-6.transition-shadow`) tenga su fondo real pintado,
- **toda la entrada escalonada esté en `opacity: 1`** (`.kr-stagger > *`) — el fundido cerrado.

Es una espera determinista (poll hasta `opacity === '1'`), no un timeout fijo: sirve tanto si el
fade corre como si `reducedMotion` lo apaga. Con esto axe muestrea siempre cards opacas → sin
falso rojo, sin bajar cobertura (el gate axe AA sigue igual de estricto).

**Endurecimiento de margen (a pedido del supervisor)** — `kr-badge` alinea los tonos de estado al
patrón que ya usaba `primary` (`bg-100 + text-700`): `success/warning/danger` pasan de
`text-{tono}` (-600, ~4.7:1 sobre el -50) a `text-{tono}-700` (≥6.9:1). Nuevos tokens
`--color-{success,warning,danger}-700` en `src/styles.css`. No cambia comportamiento; deja el
badge robusto por diseño (defensa en profundidad frente al mismo transitorio).

### El mismo transitorio afectaba a otro spec (`signup-invitacion`)

El motion de entrada es transversal: las pantallas de auth entran con `.kr-auth-enter` (opacity
0→1) igual que el marketplace con `.kr-stagger`. `reducedMotion: 'reduce'` (playwright.config)
**debería** apagarlo, pero en el harness observamos el fundido corriendo igual (el `use` tampoco es
100 % fiable, ver `e2e/context-options.ts`). Por eso `signup-invitacion.spec.ts` caía con el mismo
`color-contrast` serious en un enlace (`.mt-2 > a`) al muestrear a mitad de su entrada.

El patrón de fix es genérico y reutilizable: **antes de correr axe, esperar a que terminen las
animaciones de ENTRADA finitas**, ignorando las infinitas decorativas (shimmer/breathe):

```ts
await page.waitForFunction(() =>
  document.getAnimations().every((a) => {
    const iterations = a.effect?.getComputedTiming().iterations ?? 1;
    return iterations === Infinity || a.playState === 'finished' || a.playState === 'idle';
  }),
);
```

Cualquier spec que corra axe sobre una pantalla con motion de entrada debería asentar así (o, como
`email-verification`, esperando `opacity: 1` en los contenedores que entran). Si el `reducedMotion`
del harness se vuelve fiable, estas esperas son no-ops (sin animaciones → `getAnimations()` vacío).

## Sobre el throttle compartido (ya estaba mitigado)

La hipótesis original (los specs previos agotan el rate-limit `auth` compartido y el resend 429ea,
conteo 1 vs 3) **ya está resuelta en infra**, sin cambio en KER-72:

- Guard global con bypass por env: `libs/core/src/throttling/throttling.config.ts` →
  `skipIf: () => process.env.THROTTLE_SKIP === 'true'` (lazy, por request).
- Ambos entornos e2e ya lo setean: el CI dockerizado (`Keru-Webapp/.github/workflows/ci.yml`
  pasa `THROTTLE_SKIP: "true"` al `up`, y el compose lo propaga) y el verify aislado
  (`scripts/verify-isolated.mjs`). El límite real se sigue testeando en
  `apps/keru-api/src/throttling.spec.ts` (que fuerza `THROTTLE_SKIP=false`).

Con el throttle salteado, signup/resend son deterministas: la clave compartida no acopla specs y
el 429 por orden no puede ocurrir en CI.

## Verificación

Suite Playwright **full** contra el verify aislado / el CI dockerizado, en orden real:

```bash
node scripts/verify-isolated.mjs --suite=web-e2e   # suite full, orden real
```

Esperado: `email-verification.spec.ts` verde y estable, **sin depender de re-run** (sin línea
`flaky`, sin `retry #1`), corriendo después de otros specs.
