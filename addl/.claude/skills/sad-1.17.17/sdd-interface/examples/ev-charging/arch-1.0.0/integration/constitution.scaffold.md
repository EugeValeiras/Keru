<!--
STATUS: SCAFFOLD (emitted by speckit-handoff S8, scaffold mode, for arch-1.0.0).
- Architecture half: LANDED -- "Principle: Service Decomposition by Residue",
  verbatim from principle-decomposition-by-residue.md (RDAG 0.1.0). Do not edit
  its clauses (synced from the Architecture Release).
- Implementation half: PENDING -- the dev team fills the [TODO] principles below.
- Not yet ratified. Intentionally incomplete (not inconsistent): /speckit-plan
  gates against the architecture half now; implementation principles take effect
  as they are filled.
Drop this file at the consumer's .specify/memory/constitution.md (scaffold mode).
If the consumer already has a constitution WITH implementation principles, do NOT
use this file -- use insert/replace (the principle block + sync-impact-report).
If a SAD-workflow constitution is found there, it is NOT the consumer's: preserve
it aside (docs/architect/sad-workspace-constitution.md) and drop this.
-->

# EV Charging Network -- Project Constitution

> **Status: SCAFFOLD -- ready to define the implementation.** The **architecture
> half** below is landed from SAD `arch-1.0.0` and is authoritative now. The
> **implementation half** is **PENDING**: the dev team replaces each `[TODO]`
> with a concrete principle, then ratifies. `/speckit-plan` gates against the
> architecture half; implementation principles activate as filled. Signposted
> starting state, not silent inconsistency.

## Current Architecture

`arch-1.0.0` -- **Status: Current**. Authority: `architecture/arch-1.0.0/`
(service-catalog, nfr-register, use-cases, ADRs). No migration in progress.
Adopted from RDAG 0.1.0. Moving Current/Target is a governed amendment.

**Binding ADRs (this release):** `ADR-001` (Dapr pub/sub) -- see
`architecture/arch-1.0.0/decisions/`. These constrain the implementation half;
the principle's clauses below remain agnostic (CHK-05). The list above is the
project-specific binding, NOT part of the principle text.

---

# Architecture half

*Landed from the SAD. Do not edit the normative clauses; synced from the
Architecture Release. Amending it = a new arch release, not a local edit.*

## Principle: Service Decomposition by Residue

**Decomposition driver.** Services MUST encapsulate **residues** -- the
components that survive coherent under stressor contagion -- not units of
functionality and not predicted volatility. A service exists because a typed
Structural stressor (or set of them) requires a place to be absorbed. Reuse and
locality are consequences of correct residue encapsulation, never the
justification for a service.

- Service names MUST NOT describe a function or a domain verb (`MarketingService`,
  `ProcessOrderService` are review blockers).
- Service names MUST denote what is encapsulated, suffixed by their IDesign
  category, per Lowy: `<Thing>Manager` / `<Thing>Engine` / `<Thing>Access`.

**Service categories.** Every service belongs to exactly one category, which
constrains what it may do and who may call it:

| Category | Encapsulates | May call |
|---|---|---|
| **Manager (`*Manager`)** | A use-case workflow (the orchestration residue). | Engines, ResourceAccess (downward); other Managers only via queue / pub-sub. |
| **Engine (`*Engine`)** | A business activity / rule set. Stateless. | ResourceAccess (downward); other Engines only via queue / pub-sub. |
| **ResourceAccess (`*Access`)** | I/O to one Resource. One ResourceAccess per Resource. | Its underlying Resource only. |
| **Resource** | The actual store, queue, or external system. | n/a -- leaf. |

**Layer discipline (closed architecture).**

- Clients call only Managers -- never Engines or ResourceAccess directly.
- Managers MUST NOT call other Managers synchronously; cross-Manager
  communication goes through a queue or pub-sub topic.
- Managers MAY skip the Engine layer and call a ResourceAccess directly when no
  business rule applies (e.g. a read-only listing).
- Engines MUST NOT call Managers and MUST be stateless -- state lives in a
  ResourceAccess.
- Any other reversal of layer order is a review blocker.

**Catalog as authority.** The set of services that may be referenced by any spec
or plan is fixed by the **service catalog** at the Architecture Release the
spec/plan declares (see Architecture versioning). A service absent from that
release's catalog does not exist for `/speckit-specify` and `/speckit-plan`.
Adding, renaming, removing, or merging a service is an architecture-team activity
via the catalog amendment process -- never inline invention in `plan.md`.

**Architecture versioning.** The catalog and the artifacts it anchors form a
versioned **Architecture Release** (semver `arch vX.Y.Z`). The constitution
records the **Current** release and, during a migration, the **Target**. A spec
or plan declares the release it builds against and is gated against that
release's view; ids are append-only across releases, so a spec built against an
earlier release stays valid. A new release does **not** invalidate the current
one -- they **coexist** until a migration plan completes, after which the new
release becomes Current and the prior is Superseded (retained, not deleted).
Moving Current/Target is a **governed amendment** -- the version pointer moves;
these rules do not.

**Use cases as call chains.** Every feature submitted to `/speckit-specify` MUST
reference a use-case document that declares (a) the call chain as a graph, (b) the
services touched with their category, and (c) the residue each touched service
absorbs. The generated `spec.md` MUST preserve those three sections **verbatim**
under an "Architectural Context" heading.

**Residue lineage (traceability).**

- Every service in the catalog MUST list at least one **Structural** stressor
  identifier (`S-NN`) in its Stressors-absorbed field (by R-18 every id there is
  Structural). The full stressor analysis lives in the SAD (published separately,
  e.g. via Backstage); the catalog carries the resolvable conclusion.
- Every NFR MUST record a **coupling** (or topology) identifier (`C-NN`) in its
  Source field. NFRs live in one register, each with an `Applies-to` scope
  (`System` or an enumerated use-case set); use cases reference NFRs by id. The
  full coupling analysis lives in the SAD.
- Known **unstressed surfaces** from the SAD's empirical test are documented
  risk; a plan that knowingly builds on one MUST flag it (here: `U-01` dynamic
  energy economics).

**Binding ADRs.** A runtime, protocol, or middleware decision captured in an ADR
is a binding architecture constraint (Architecture Supremacy). The implementation
half MUST conform to it and MUST NOT substitute an alternative.

> (The principle stays **agnostic** -- no concrete technology in its clauses,
> CHK-05. The current binding ADRs of this release -- e.g. `ADR-001` for Dapr
> pub/sub -- are listed in the **Current Architecture** record above and detailed
> in `architecture/arch-1.0.0/decisions/`.)

**Constitution Check questions (gate at `/speckit-plan`).** The gate MUST answer:

1. Is every service in `plan.md` present in the service catalog?
2. Does each service name follow the category suffix (`*Manager` / `*Engine` / `*Access`)?
3. Does the call chain respect the layer rules (no Manager->Manager sync, no
   Client->ResourceAccess, no Engine->Manager)?
4. Does each service list at least one Structural stressor identifier (`S-NN`)
   in its Stressors-absorbed field?
5. Does each NFR record a coupling (or topology) identifier (`C-NN`) in its
   Source field?
6. Does the plan's runtime / protocol / middleware conform to all binding ADRs?

A "no" on any question is **not** resolvable via a Complexity Tracking entry. It
triggers an architecture-team review (a catalog or ADR amendment request) and
blocks the plan until the discrepancy is resolved.

---

# Implementation half

*PENDING -- the dev team defines these. Replace each `[TODO]` with a concrete
principle. None may contradict the architecture half (Architecture Supremacy);
binding ADRs constrain runtime/protocol -- conform, do not re-decide.*

## [TODO] Implementation: Language & Runtime
## [TODO] Implementation: Testing strategy
## [TODO] Implementation: API & contract conventions
## [TODO] Implementation: Observability
## [TODO] Implementation: Persistence & data
## [TODO] Implementation: Security & authorization

---

## Governance

- The **architecture half** is synced from the SAD release; amending it is an
  architecture-team activity (a new `arch-X.Y.Z` release + Sync Impact Report,
  then update the Current/Target pointer here).
- The **implementation half** is owned by the dev team (fill/amend a `[TODO]`
  per this project's amendment process).
- **Ratify** (drop `-draft`) only once the implementation half is filled and no
  implementation principle contradicts the architecture half.

**Version**: 0.1.0-draft (SCAFFOLD) | **Architecture**: arch-1.0.0 (Current) | **Implementation**: PENDING | **Adopted RDAG**: 0.1.0
