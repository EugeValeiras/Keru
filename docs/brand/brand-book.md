# Keru — Brand book v1

> Keru es un marketplace de cuidadores: conecta familias con cuidadores profesionales y
> acompaña el cuidado con registros de salud en vivo. Este documento define la marca —
> personalidad, identidad visual y tono de voz — y es la fuente de verdad para las tareas
> de rebranding (KER-20 a KER-24). **Acá se decide; en la webapp se implementa.**
>
> Vista rápida de todo lo definido acá: [`preview.html`](./preview.html) (autocontenida,
> abrila en el navegador).

---

## 1. Personalidad

### La idea en una línea

**Keru es la calma de saber que alguien que sabe está cuidando a quien querés.**

Keru vive en un momento emocionalmente cargado: una familia que confía el cuidado de su
mamá, su abuelo o su hijo a una persona que todavía no conoce. La marca tiene que sostener
dos cosas a la vez, sin que una tape a la otra:

- **Calidez humana** — esto es cuidado, no logística. La familia tiene que sentir hogar.
- **Respaldo profesional** — hay identidad verificada, antecedentes, certificaciones,
  métricas clínicas. La familia tiene que sentir que esto es serio.

### Direcciones exploradas

| Dirección | Descripción | Por qué sí / por qué no |
|---|---|---|
| **A. "Casa de té"** | Crema y terracota dominantes, violeta casi ausente, serif en todo, fotografía cálida. | Máxima calidez, pero pierde el equity del violeta actual y desliza hacia lifestyle/decoración. El respaldo profesional se diluye: parece una marca de bienestar, no una plataforma con verificación de antecedentes. **Descartada.** |
| **B. "Clínica boutique"** | Violeta profundo + azules fríos, grotesk geométrica, mucho blanco, iconografía técnica. | Máxima seriedad, pero enfría justo donde Keru compite: la confianza *cálida*. Se parece a una prepaga u ortodoncia premium; intimida a la familia que llega angustiada. **Descartada.** |
| **C. "Abrazo profesional"** ⭐ | El violeta actual evoluciona a un violeta orquídea más cálido y profundo; entra un acento terracota puntual (lo humano); los neutros toman temperatura (greige, crema); serif con carácter para la voz de marca + sans humanista para la UI. | Conserva el reconocimiento del violeta (equity de v1), suma la calidez que hoy falta sin resignar seriedad, y deja los semánticos reservados a estados clínicos — regla de v1 que se mantiene intacta. **Elegida.** |

### Racional de la elección

"Abrazo profesional" gana porque es una **evolución, no un reemplazo**: el violeta sigue
siendo el color de Keru (nadie que use la app hoy va a sentir que le cambiaron la marca),
pero se templa — menos neón digital, más ciruela — y gana un compañero cálido, el
terracota, que aparece **en pequeñas dosis** justo donde está lo humano: el punto del
logo, el corazón de favoritos, los momentos de celebración. La estructura fría de v1
(grises azulados, Inter en todo) se reemplaza por neutros con temperatura y una serif
que habla como persona, no como sistema.

### Atributos de personalidad

| Keru es… | Keru no es… |
|---|---|
| Cálido, cercano, de entrecasa | Empalagoso, infantil, ñoño |
| Directo y claro | Frío, burocrático, corporativo |
| Profesional con evidencia (badges, métricas) | Alarmista ni clínico-hospitalario |
| Sereno: transmite que todo está bajo control | Eufórico, gritón, promocional |

---

## 2. Logo

Assets en [`assets/`](./assets/):

| Archivo | Uso |
|---|---|
| [`keru-logo.svg`](./assets/keru-logo.svg) | Wordmark "keru" — header sobre fondo claro, docs, emails |
| [`keru-logo-blanco.svg`](./assets/keru-logo-blanco.svg) | Wordmark para fondos oscuros o violeta (hero, footer oscuro) |
| [`keru-isotipo.svg`](./assets/keru-isotipo.svg) | La "k" sola — espacios chicos, avatar de marca, loader |
| [`keru-favicon.svg`](./assets/keru-favicon.svg) | Isotipo en negativo sobre contenedor violeta `rx=16` — favicon y app icon |

### Construcción y concepto

El wordmark es **monolínea dibujado a mano** (paths SVG, no depende de ninguna tipografía
instalada): trazo de 9 unidades, terminales redondeadas, minúsculas — Keru habla en
minúscula, como se habla en casa.

La **"k" es el isotipo**: el trazo vertical con la pierna es *quien sostiene* (el
cuidador), y el brazo superior se reemplaza por un **punto terracota** — *la persona
cuidada*, siempre arriba, siempre lo primero que se ve. Es el único elemento no violeta
del logo: lo humano como acento, literal.

### Reglas de uso

- **Zona de seguridad**: alrededor del logo, aire mínimo igual a la altura del punto (¼ de la altura del wordmark).
- **Tamaño mínimo**: wordmark 72px de ancho; por debajo de eso usar el isotipo.
- **Colores permitidos**: tinta (`#2B2733`) sobre claro; blanco sobre violeta/oscuro. El punto siempre terracota (`#D96A3D` sobre claro, `#EDA57F` sobre oscuro).
- **No**: no rotar, no estirar, no cambiar el punto de color, no aplicar sombras ni degradés, no recomponer el espaciado entre letras.

---

## 3. Paleta v2

Principio heredado de v1 que **se mantiene**: el violeta es el único color de marca fuerte
(CTAs, favoritos, badge de campana, filtros activos); **los estados clínicos usan los
semánticos, nunca el violeta**. Novedad de v2: el terracota es acento *emocional*
(favoritos, celebraciones, el punto del logo) — nunca acción primaria ni estado clínico.

### Primario — violeta orquídea

Evoluciona el violeta v1 (Tailwind violet, frío y neón) hacia un violeta más cálido
(más rojo, menos azul) y menos saturado en pantalla.

| Token | Hex | Uso |
|---|---|---|
| `primary-50` | `#F7F4FC` | Fondos tenues, hover de items |
| `primary-100` | `#EFE9F9` | Fondos de badge primario, seleccionado |
| `primary-200` | `#DFD2F2` | Bordes activos suaves |
| `primary-300` | `#C5ADE7` | Decorativo, ilustración |
| `primary-400` | `#A783D8` | Focus ring, decorativo fuerte |
| `primary-500` | `#8A5CC7` | Marca en superficies grandes, iconos activos |
| `primary-600` | `#7443B0` | **CTA / acción primaria** (AA sobre blanco) |
| `primary-700` | `#5D3492` | Hover de CTA, texto violeta sobre tenues |
| `primary-800` | `#482872` | Fondos oscuros de marca (hero, footer) |
| `primary-900` | `#341D52` | Fondo de marca profundo |

Mapeo desde v1: `#8b5cf6 → #8A5CC7` (500), `#7c3aed → #7443B0` (600), `#6d28d9 → #5D3492` (700).

### Acento — terracota abrazo

| Token | Hex | Uso |
|---|---|---|
| `accent-50` | `#FDF4EF` | Fondo tenue de momentos cálidos |
| `accent-100` | `#FAE5D9` | Badge cálido |
| `accent-200` | `#F5CBB2` | Decorativo |
| `accent-300` | `#EDA57F` | Punto del logo sobre oscuro, ilustración |
| `accent-400` | `#E38357` | Corazón de favorito activo |
| `accent-500` | `#D96A3D` | **Acento pleno**: punto del logo, celebraciones |
| `accent-600` | `#B85430` | Texto terracota sobre claro (AA sobre blanco) |
| `accent-700` | `#944226` | Texto terracota sobre tenues |

### Neutros con temperatura

Los grises azulados de v1 se reemplazan por neutros greige (base cálida con un dejo violeta).

| Token | Hex | Uso |
|---|---|---|
| `ink-900` | `#2B2733` | Texto principal, wordmark |
| `ink-700` | `#4B4454` | Texto secundario fuerte, labels |
| `ink-500` | `#6F6779` | Texto secundario (AA ≥4.5:1 sobre blanco y tenues claros) |
| `ink-300` | `#D9D4DE` | Bordes, divisores, iconos deshabilitados |
| `ink-200` | `#E9E5EC` | Bordes suaves, fondos deshabilitados |
| `surface` | `#FFFFFF` | Cards, modales, superficies elevadas |
| `canvas` | `#FAF8F5` | Fondo general de la app (blanco cálido; v1 usaba `#fafafb` frío) |
| `sand-100` | `#F3EEE7` | Fondo cálido secundario: empty states, ilustraciones, onboarding |

### Semánticos (estados clínicos y de sistema)

Templados respecto de v1 (rojos y verdes menos ácidos), siempre con su tenue asociado.
Reservados a estado: alertas de salud, errores, éxitos, advertencias. Nunca decorativos.

| Token | Hex | Tenue | Uso |
|---|---|---|---|
| `danger-600` | `#C23B2E` | `danger-50 #FCEEEC` | Errores, alertas clínicas fuera de rango |
| `success-600` | `#1B7A55` | `success-50 #E9F6EF` | Éxitos, verificaciones ✓, métricas en rango |
| `warning-600` | `#935F10` | `warning-50 #FBF3E2` | Advertencias, pendientes de revisión |
| `info-600` | `#3B69B0` | `info-50 #EDF2FA` | Información neutral del sistema |

Los `-600` están elegidos para dar ≥4.5:1 sobre blanco y sobre su tenue `-50`
(objetivo WCAG AA 1.4.3; KER-20 lo valida token por token al implementar).

---

## 4. Tipografía

Dos familias de Google Fonts, ambas con licencia libre (OFL) y **self-hosteables**
(requisito para no depender de terceros en producción):

| Rol | Familia | Pesos | Dónde |
|---|---|---|---|
| **Display** | [Fraunces](https://fonts.google.com/specimen/Fraunces) (serif "soft", eje óptico) | 600 | h1, h2, números grandes de marca, momentos emocionales (bienvenida, éxito de contratación) |
| **UI** | [Figtree](https://fonts.google.com/specimen/Figtree) (sans humanista, variable) | 400 / 500 / 600 / 700 | Todo lo demás: cuerpo, labels, botones, tablas, formularios |

**Regla de convivencia**: Fraunces es la *voz* de Keru — aparece poco y arriba (títulos de
página, heros, celebraciones). Figtree es la *conversación* — toda la UI operativa. Nunca
Fraunces en cuerpo de texto, botones ni formularios. Inter (v1) se retira.

### Escala tipográfica

| Uso | Familia/peso | Tamaño / interlínea |
|---|---|---|
| Display hero | Fraunces 600 | 40px / 1.1 (desktop) · 32px / 1.15 (mobile) |
| h1 página | Fraunces 600 | 28px / 1.2 |
| h2 sección | Fraunces 600 | 22px / 1.25 |
| h3 subsección | Figtree 600 | 18px / 1.3 |
| Cuerpo | Figtree 400 | 16px / 1.55 |
| Secundario | Figtree 400 | 14px / 1.5 |
| Label / botón | Figtree 600 | 14px / 1.2 |
| Caption / badge | Figtree 500 | 12px / 1.35 |

---

## 5. Iconografía

- **Estilo**: lineal, trazo `1.75px` en 24px (escala proporcional), terminales y uniones
  redondeadas — coherente con la monolínea del logo. Set de referencia:
  [Lucide](https://lucide.dev) (ISC, embebible como SVG inline).
- **Tamaños**: 20px en líneas de texto y botones, 24px en navegación y headers.
- **Color**: heredan el color del texto (`currentColor`). Activos en `primary-600`;
  nunca semánticos salvo que comuniquen estado.
- **Emojis**: v1 usa emojis como iconos (♥, 🔍). En v2 quedan **solo para contenido**
  (mensajes, celebraciones puntuales); la UI usa iconos del set.

---

## 6. Radios, sombras y elevación

La forma de Keru es **blanda**: esquinas generosas, sombras cálidas y difusas (tinta
`#2B2733`, nunca negro puro), sin bordes duros.

### Radios

| Token | Valor | Uso |
|---|---|---|
| `radius-tag` | `8px` | Badges, chips, snippets |
| `radius-control` | `12px` | Inputs, selects, textareas |
| `radius-card` | `20px` | Cards, modales, paneles (v1: 16px) |
| `radius-pill` | `9999px` | Botones, filtros, avatares |

### Elevación (sombras)

| Nivel | Token | Valor | Uso |
|---|---|---|---|
| 0 | — | sin sombra, borde `ink-200` | Superficies planas, tablas |
| 1 | `shadow-card` | `0 1px 2px rgb(43 39 51 / 0.05), 0 6px 20px rgb(43 39 51 / 0.07)` | Cards en reposo |
| 2 | `shadow-card-hover` | `0 2px 4px rgb(43 39 51 / 0.06), 0 12px 32px rgb(43 39 51 / 0.11)` | Hover de cards, dropdowns, popovers |
| 3 | `shadow-modal` | `0 8px 16px rgb(43 39 51 / 0.10), 0 24px 64px rgb(43 39 51 / 0.18)` | Modales, sheets |

Regla: la elevación comunica **interactividad o foco**, no jerarquía decorativa. Máximo
un nivel 3 visible por pantalla.

---

## 7. Tono de voz (es-AR)

Keru escribe como una persona que sabe de cuidado y te habla de frente: **cálido y
directo**. Voseo rioplatense natural, sin diminutivos empalagosos, sin jerga técnica ni
clínica innecesaria.

### Principios

1. **Primero qué pasó, después qué hacer.** Cada mensaje de estado da el hecho y el
   siguiente paso, en ese orden.
2. **Cálido sin empalagar.** Una calidez por mensaje alcanza (un "¡Listo!", no tres
   signos de exclamación).
3. **Nunca culpar a la persona.** "No encontramos…" en vez de "No ingresaste bien…".
4. **Lo clínico, serio y sin eufemismos.** Las alertas de salud son claras y accionables;
   ahí no hay chistes ni suavizantes.
5. **Voseo siempre**: "probá", "tocá", "revisá". Nunca "pruebe" ni "haz clic".

### Decimos / no decimos

| ✅ Decimos | ❌ No decimos |
|---|---|
| "Probá ampliar la zona" | "Intente modificar los parámetros de búsqueda" |
| "Algo salió mal de nuestro lado" | "Error inesperado del sistema (500)" |
| "Te avisamos apenas responda" | "Recibirá una notificación oportunamente" |
| "La presión de Rosa salió del rango esperado" | "¡Ups! 😅 Un valorcito raro" |

### Microcopy de referencia

**Vacíos** (siempre: qué está vacío + cómo llenarlo):

> **No encontramos cuidadores con esos filtros.**
> Probá ampliar la zona o aflojar el rango de tarifa.

> **Todavía no guardaste favoritos.**
> Tocá el corazón de una card y queda acá para cuando lo necesites.

> **Todavía no hay registros en este turno.**
> Cuando el cuidador cargue mediciones, las vas a ver acá al instante.

**Errores** (el hecho + el siguiente paso; sin códigos en la cara del usuario):

> **Algo salió mal de nuestro lado.** Ya lo estamos mirando; probá de nuevo en un rato.

> **Revisá la tarifa:** tiene que ser un número mayor a cero.

> **Demasiados intentos.** Esperá un minuto y volvé a probar.

**Éxitos** (celebrar corto y decir qué sigue):

> **¡Listo! Le mandamos tu solicitud a Carmen.** Te avisamos apenas responda.

> **Perfil actualizado.** Tus cambios ya se ven en el marketplace.

**Alertas clínicas** (serias, con dato y acción):

> **La presión de Rosa salió del rango esperado** (150/95 a las 16:30).
> Mirá el registro y, si hace falta, contactá al cuidador.

---

## 8. Implementación

- Esta identidad **no toca la webapp todavía**: KER-20 traduce estos tokens al
  `@theme` de Tailwind v4 en `Keru-Webapp/src/styles.css` y self-hostea las fuentes;
  KER-21 a KER-23 aplican por área; KER-24 hace QA visual y actualiza los docs.
- La comparación visual v1 → v2 (paleta, tipografía, logo, botones y card de cuidador)
  vive en [`preview.html`](./preview.html): un solo archivo, sin dependencias externas
  (fuentes embebidas en base64), se abre directo en el navegador.

---

## 9. Emails transaccionales (KER-55)

Los emails que manda Keru (invitación de vínculo UC-03, recuperación de contraseña UC-04 A4,
verificación de email UC-04 A5) usan una **plantilla HTML de marca** en vez de texto plano.

### Dónde vive

- **Plantilla:** `Keru-API/libs/core/src/email/email.templates.ts` — `renderBrandedEmail(content)`
  devuelve `{ html, text }` a partir de un mismo contenido (preheader, título, párrafos, CTA,
  notas y motivo). `EmailUtility` (`email.util.ts`) arma el `content` de cada email y envía
  **multipart** (parte HTML + parte texto plano) por SES. Es una **Utility** (constitution §3.1):
  el branding es **mejor esfuerzo**, no bloquea al que llama ni cambia la firma de los métodos.
- **Muestras para inspección visual:** `Keru-API/docs/email-samples/*.html` (regenerables con
  `WRITE_EMAIL_SAMPLES=1 npx jest email.samples`).

### Origen del logo

El wordmark se **embebe como data-URI SVG** con `alt="keru"` (el asset exacto de
[`assets/keru-logo.svg`](./assets/keru-logo.svg), minificado dentro del código). No depende de
la webapp corriendo ni de hosting de assets. **Límite conocido:** Gmail y Outlook bloquean las
imágenes `data:` (cualquier formato), así que ahí el logo cae al **texto `alt` "keru"**; la
identidad la sostienen igual el color de marca, la tipografía y el CTA, que sí renderizan en
todos los clientes. Apple Mail / iOS Mail / Thunderbird muestran el SVG. *Follow-up opcional:*
si se quiere el logo pixel-perfect también en Gmail, reemplazar el data-URI por un **PNG en una
URL pública estable** de assets.

### Reglas de compatibilidad de clientes de correo

- Estilos **100% inline** (no `<style>` ni CSS externo — Gmail/Outlook los descartan).
- Layout con **tablas**, ancho ~600px, sin JS.
- **Preheader** (preview text) oculto al inicio del cuerpo.
- **Contraste AA:** CTA violeta `primary-600` con texto blanco; cuerpo en `ink-700`; el logo
  lleva `alt`. Tipografía con fallbacks web-safe (Georgia por Fraunces en el título; Arial/Helvetica
  por Figtree en el cuerpo).
- Botón CTA **"bulletproof"** con fallback VML para el motor Word de Outlook.
- **Multipart siempre:** parte texto plano de respaldo con el mismo link/token (accesibilidad y
  deliverability).
