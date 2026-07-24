# ADR-0003 — Modelo de identidad: una sola fuente de verdad de nombre/avatar entre la cuenta y su perfil de dominio

- **Estado:** Aceptado (2026-07-23)
- **Decisores:** Eugenio Valeiras (product owner) + agente supervisor
- **Referenciado desde:** `constitution.md §2 (principio de identidad)`, `§3.3 (dueño de escritura)`, `§7 (decisión abierta UC-02 A3 acotada)`; `Keru-Casos-de-Uso-MVP.md` UC-01/02/22/23 y §5 (modelo de dominio)
- **Tareas:** KER-54 (esta decisión). Base de KER-50 (authz + identidad de paciente) y KER-51 (editar ficha/avatar).

## Contexto

El usuario reportó (3 veces) que **la cuenta y su perfil de dominio no comparten identidad**. Verificado en el código (2026-07-23):

- **Cuidador:** `Caregiver.accountId` vincula el perfil a la `Account`, pero `Caregiver.displayName` y `Caregiver.photoUrl` están **duplicados** respecto de `Account.displayName` / `Account.photoUrl` (KER-41). El registro (`registerCaregiver`) y la edición del aprobado (`updateApprovedCaregiver`, foto) escriben el perfil por su cuenta; `PATCH /accounts/me` (UC-23) escribe la cuenta. Los dos **divergen**: el avatar del "usuario cuidador" (header, `Account`) y el del "perfil de cuidador" (marketplace/ficha, `Caregiver`) pueden diferir.
- **Paciente:** `Patient` **no** tiene link a ninguna `Account` (entidad disjunta) y tiene `fullName`/`photoUrl` propios. Una cuenta con rol `'patient'` (del signup) y un perfil de paciente son cosas **desconectadas**.

**Expectativa del usuario (requisito):** la cuenta y su perfil de dominio deben mostrar la **misma** información de identidad (nombre, avatar). Debe haber **una sola fuente de verdad**, no campos duplicados que deriven ni entidades desconectadas.

Restricción de arquitectura relevante: **§3.5** prohíbe relaciones/FKs y JOINs **entre dominios distintos** (para poder mudar la partición clínica). **No** prohíbe joins **intra-dominio**. `Account` y `Caregiver` viven **ambos** en el dominio **Membership** (`libs/membership`), por lo que resolver la identidad del cuidador desde su cuenta con un join intra-Membership es **legítimo**.

## Decisión

### 1. Principio de identidad (nuevo, no-negociable)
La identidad visible (**nombre + avatar**) de la **persona detrás de un login** tiene su **fuente canónica en la `Account`**. Un perfil de dominio que representa a **esa misma persona** **no duplica** nombre/foto: los **deriva** de su `Account`. Un perfil que representa a **alguien que puede no tener login** (Paciente) es él mismo la fuente única de su identidad. **Membership** es el dueño único de escritura de la identidad (§3.3).

### 2. Cuidador — identidad derivada de la cuenta (Opción A)
`Caregiver` **deja de tener** `displayName`/`photoUrl` propios. Su identidad visible (header, cards del marketplace, ficha, perfil propio) se **resuelve desde su `Account`** por `accountId`, con un **join intra-dominio** dentro de `CaregiverAccess` (Membership). Hiring sigue leyendo el perfil de cuidador **enriquecido** por la read-replica de `CaregiverAccess` — **sin nuevo acoplamiento cross-dominio** (§3.5 intacto: Hiring nunca joina `account`; recibe la vista ya resuelta por Membership).

El **único punto de escritura** del nombre/foto de un cuidador pasa a ser **`PATCH /accounts/me`** (UC-23). Editar en `/perfil` se refleja en el header **y** en el marketplace/ficha **por construcción** (hay un solo lugar donde vive el dato).

- **Registro de cuidador (UC-02):** ya **no** pide `displayName` (usa el de la cuenta). Si el formulario ofrece subir una foto, esa foto se setea en la **`Account`** (Membership es dueño de ambas), no en el perfil.
- **Back-office (`listPaged`, UC-19):** el filtro por nombre que consultaba `caregiver.displayName` ahora resuelve el nombre por **join con `account`** (intra-dominio).

#### Sub-decisión registrada (no silenciosa): nombre editable vs. re-verificación
Unificar el nombre implica que un cuidador **aprobado puede cambiar su nombre visible** vía su cuenta — antes **UC-02 A3** lo bloqueaba (lo trataba como credencial revisada). Se **acota** la decisión abierta de **§7 (UC-02 A3)** a **certificaciones y especialidades**: **nombre y foto no son credenciales verificadas** (la **insignia de identidad**, NFR-19/UC-19, es un artefacto separado que **no** se toca por editar el nombre), por lo que un cambio de nombre/foto **no** dispara re-verificación. **Justificación:** feedback del usuario (3×) pidiendo identidad unificada, y el nombre de la cuenta ya es libremente editable (UC-23). La re-verificación de **credenciales** (certificaciones/especialidades) sigue como decisión abierta en §7.

### 3. Paciente — perfil-sin-login; decisión de vínculo cuenta↔paciente ABIERTA
El perfil de `Patient` **ya es la fuente única** de su propia identidad (`fullName`/`photoUrl`): **no hay duplicación que unificar**. Un paciente es un **perfil administrado, no necesariamente un login** (§2.8): se administra por `PatientLink` (roles `consent-holder`/`manager`/`viewer`). El nombre/avatar del **header** de una cuenta (UC-23, la persona que **administra**) y el de la **ficha** de un paciente (la persona **cuidada**) son **legítimamente distintos** — a menudo son personas distintas (administro el perfil de mi madre). No es el mismo bug que el del cuidador.

**DECISIÓN ABIERTA (no se resuelve acá; cruza KER-50):** ¿una cuenta con rol `'patient'` debe **vincularse** a un perfil de paciente "sí mismo" compartiendo identidad, o los pacientes son **siempre** perfiles-sin-login (y entonces el rol `'patient'` del signup se revisa)? **Hasta que Eugenio lo decida** rige el **status quo**: la identidad del paciente vive en `Patient`; el rol `'patient'` **no** auto-crea ni vincula un perfil; **KER-50** es dueño de la revisión de authz/rol. **No hay migración de identidad de paciente** (no hay nada que unificar ni backfillear).

> **Actualización (KER-50, 2026-07-24) — parte de authz/rol resuelta.** KER-50 cerró la revisión de authz que esta ADR le delegó: **administrar/registrar perfiles de paciente es capacidad del rol de cuenta `family`** (constitution §2.8), el **círculo** de un paciente se compone únicamente de cuentas `family` (invariante "solo cuentas `family` tienen vínculo con un paciente"; enforce con `RolesGuard` en `POST /patients` y `POST /invitations/:token/confirm`), y el rol **`'patient'` salió del self-signup** (`SIGNUP_ROLES = ['family','caregiver']`; sigue en `AccountRole` reservado para un eventual login-de-paciente). Quien cuida de sí mismo se registra como `family` y crea su propia ficha (§2.8). **Lo que queda abierto** es estrictamente más chico: si en el futuro se introduce un **login-de-paciente** que **comparta identidad** (nombre/avatar) con un perfil "sí mismo" — decisión de producto no forzada por el MVP. Sigue **sin migración de datos** de identidad de paciente.

### 4. Migración (solo cuidador), con backfill sin pérdida
1. **Backfill no-destructivo primero:** `UPDATE account a SET "photoUrl" = COALESCE(a."photoUrl", c."photoUrl") FROM caregiver c WHERE c."accountId" = a.id AND a."photoUrl" IS NULL AND c."photoUrl" IS NOT NULL` — ninguna foto seteada se pierde (si la cuenta ya tiene foto, gana la de la cuenta; si no, adopta la del cuidador).
2. **`displayName`:** la cuenta ya tiene `displayName` **no-null** (identidad de login del signup); **gana el de la cuenta**. El `caregiver.displayName` era un duplicado tipeado al registrar el perfil; se descarta al dropear la columna (el nombre visible pasa a ser el de la cuenta).
3. **Drop:** recién después se **dropean** `caregiver."displayName"` y `caregiver."photoUrl"`.

`down()` re-agrega las columnas (nullable) y re-backfillea desde la cuenta (`caregiver.x = account.x`) para no dejar la vista rota si se revierte.

## Racional

- **Opción A (derivar) sobre B (sincronizar copias) y C (resolver solo en el DTO):** A elimina la duplicación **de raíz** (no hay dos columnas que puedan divergir), que es exactamente lo que pidió el usuario. B (mantener columnas sincronizadas por dueño único) deja el dato duplicado y depende de que el sync nunca falle; C (view/DTO) deja las columnas huérfanas y editables. A es viable **sin** violar §3.5 porque la resolución es intra-Membership.
- **Sin coste de acoplamiento nuevo:** Hiring ya leía `Caregiver` cross-dominio vía `CaregiverAccess`; ahora recibe el mismo objeto **con la identidad ya resuelta** por Membership. El contrato de lectura de Hiring no cambia (sigue leyendo `.displayName`/`.photoUrl` del objeto que le devuelve `CaregiverAccess`).
- **Paciente distinto por diseño, no por omisión:** forzar identidad cuenta↔paciente rompería el caso "administro a otra persona" (§2.8) y el "paciente sin login". Por eso la parte de paciente es una **decisión de producto** (documentada y abierta), no un cambio de datos.

## Consecuencias

- **Coherencia (criterio del usuario):** editar nombre/foto en `/perfil` (UC-23) actualiza el header **y** el marketplace/ficha del cuidador; hay un solo dato.
- **Contrato:** `RegisterCaregiverDto` deja de exigir `displayName`; los DTOs de respuesta del cuidador siguen exponiendo `displayName`/`photoUrl` (ahora resueltos desde la cuenta). Se regeneran `openapi.json` + `schema.d.ts`.
- **KER-50 / KER-51:** consumen esta identidad unificada. La pregunta **paciente↔cuenta** la **resolvió KER-50** en su parte de authz/rol (administrar pacientes = capacidad `family`; `'patient'` fuera del self-signup; ver §3 arriba); solo queda abierto un eventual **login-de-paciente con identidad compartida**, no forzado por el MVP.
- **§7 acotado:** la decisión abierta de re-verificación (UC-02 A3) queda limitada a **certificaciones/especialidades** (nombre/foto salen de esa lista).
- **Riesgo:** el `caregiver.displayName` histórico que difería del de la cuenta se pierde al dropear (por diseño: gana la cuenta). El backfill de foto lo evita para las fotos.
