# Constitution Principle (drop-in) -- Service Decomposition by Residue

> **Emitted by:** speckit-handoff (S8) at **RDAG 0.1.0**. This is the
> architecture-half principle to land in the consumer's **canonical**
> constitution `.specify/memory/constitution.md` (the file `/speckit-plan`
> reads). Insert it as a numbered principle alongside the implementation-half
> principles; copy the normative clauses verbatim (you may renumber the
> principle and adjust surrounding prose, never the clauses). Applying it is the
> gated integration step -- see `sync-impact-report.md`.

---

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
  risk; a plan that knowingly builds on one MUST flag it.

**Binding ADRs.** A runtime, protocol, or middleware decision captured in an ADR
is a binding architecture constraint (Architecture Supremacy). The implementation
half MUST conform to it and MUST NOT substitute an alternative.

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
