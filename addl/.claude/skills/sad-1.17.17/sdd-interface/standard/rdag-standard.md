---
title: "RDAG -- Residue-Driven Architecture Governance (Standard)"
version: 0.1.0
date: 2026-05-26
status: Draft (Phase 0a)
---

# RDAG -- Residue-Driven Architecture Governance

RDAG is the **architecture half of a project constitution**. It is a portable,
stack-agnostic doctrine module that a Spec-Driven Development (SDD) project --
e.g. a spec-kit repository -- composes into its `constitution.md` so that every
generated `spec` and `plan` respects an architecture produced by the SAD
meta-skill (this repository).

This file is the **canonical source** of the doctrine. Its normative principle
(see Section 6) is *copied into* a host project's constitution at integration
time; from then on the host's own constitution is what `/speckit-plan` reads.
No spec-kit project ever loads files from this repository at runtime. See
`rdag-id-scheme.md` for identifiers and `rdag-conformance.md` for the conformance
checklist and completeness test. Per-artifact schemas live under
`../contracts/`.

## 1. Why "by Residue", not "by Volatility"

IDesign (Lowy, *Righting Software*) frames decomposition as encapsulating
**areas of volatility** -- what you predict will change. Residuality Theory
(O'Reilly, *Residues*) does not predict: it stresses the naive architecture
against the stressor environment and keeps the components that remain coherent
under contagion. Those survivors are the **residues**, and criticality (NKP
balance) is the goal, validated empirically by the Residual Index (Ri).

In this synthesis, **residuality is the method** (how the structure is found)
and **IDesign is the vocabulary** (how it is named and constrained). A service
*is* a Structural residue; what IDesign would call the "volatility" a service
encapsulates is, in this method, only a description of that residue -- derived
from the stressors the residue absorbs, never a separately calculated
prediction. The driver and the evidence are the **stressor and the residue** --
not a guess about future change.

Consequence for governance: a gate that asks *"is the encapsulated volatility
credible?"* is weak -- "credible" is a human judgment. RDAG instead asks *"does
this service trace to a typed Structural residue listed in the catalog, and
did that residue pass the Ri test?"* -- a question resolvable against an emitted
artifact. This is the source of the standard's strength.

> Citations: O'Reilly *Residues* (residue, stressor, contagion, criticality, Ri);
> Lowy *Righting Software* L2167 ("in theory just another Manager"); this repo's
> constitution R-13 (stressor typing), R-18 (no component without a Structural
> residue), R-24 (smallest-set residue), R-25 (actor-style grouping).

## 2. The two-half model

A project constitution has two halves, and the responsibility for getting it
right is **shared**:

- **Architecture half (RDAG -- ours, portable).** How the system is decomposed
  into services, the service taxonomy and call rules, the catalog as authority,
  the residue/stressor/coupling traceability, and the architecture quality
  attestation. Identical across projects regardless of technology.
- **Implementation half (theirs -- per stack).** Language, runtime framework,
  testing strategy, API wire format, observability stack, and the concrete
  technology bound to each Resource. Specific to the stack the team chooses.

RDAG defines only the architecture half and the **seam** between the two.

## 3. The seam

The seam is **not a static line**. It is a default partition plus an override
mechanism (Section 5).

| Architecture half (RDAG) | Implementation half (per stack) |
|---|---|
| Decomposition by residue | Language / runtime / framework |
| Service taxonomy (Manager/Engine/ResourceAccess/Resource) + call rules | How a service is materialized (class, module, function) |
| Catalog as authority + amendment discipline | Concrete technology bound to each Resource (Postgres, Kafka, S3, ...) |
| Traceability service<->stressor and NFR<->coupling (by ID) | Testing, observability, idiomatic conventions |
| Constitution Check questions (the `/speckit-plan` gate) | Language and stack best practices |
| Criticality / Ri attestation | -- |

The seam is **already latent** in working SDD repos: a service catalog that
names a Resource and defers its technology to the constitution's tech stack
("Technology: PostgreSQL (per constitution Tech Stack)") is the seam at work --
RDAG says *which* Resource and *why* (the residue); the implementation half says
*with what* it is built.

## 4. Architecture Supremacy Rule

> **The architecture always prevails.** When the architecture half and the
> implementation half conflict, the architecture half wins -- not only on
> decomposition, but on **any concern the architecture has explicitly decided
> through an ADR**, including runtime, protocol, or middleware (e.g. a sidecar
> runtime such as Dapr, a messaging protocol, a saga engine). An ADR **promotes**
> a concern that would otherwise belong to the implementation half into a
> binding architecture constraint. The implementation half is free only in the
> space the architecture has *not* claimed (its residual freedom).

Rationale: choices that look like implementation are often architectural. A
distributed-application runtime decides how the call rules and the actor-style
service grouping (R-25) are realized: its pub/sub maps to queued
Manager-to-Manager communication, its state building block to ResourceAccess,
its actor model to "one Manager = one service". Selecting it is therefore an
architectural decision -- and once captured in an ADR, it binds.

This rule moves the seam: an ADR is the lever that reclaims implementation
territory for architecture. See `../contracts/adr-contract.md` for how a binding
ADR is expressed and traced.

## 5. Agnosticism Rule (reconciled with Supremacy)

> **The standard contains zero stack assumptions.** If the words `gRPC`,
> `.NET`, `PostgreSQL`, `Dapr` -- or any concrete technology -- appear in the
> RDAG standard (this file, `rdag-id-scheme.md`, `rdag-conformance.md`), it is
> broken. The standard speaks only architecture vocabulary.

This does **not** contradict Section 4. The distinction is by layer:

- **The standard (this `standard/` folder)** is portable doctrine and stays
  agnostic -- it never names a technology.
- **Per-project instance artifacts (`contracts/` outputs: ADRs, catalog,
  ...)** may name a concrete runtime or protocol; when an ADR does, that
  decision binds the implementation per Section 4.

So agnosticism governs the reusable doctrine; supremacy governs concrete
per-project decisions. They never overlap.

## 6. The drop-in principle (normative -- copy into the host constitution)

The block below is the **architecture-half principle** a host project inserts
into its `constitution.md`, under whatever principle number fits its document.
It is the only RDAG text that crosses into the consumer repository. It is
stack-agnostic by construction (Section 5).

---

### Principle: Service Decomposition by Residue

**Decomposition driver.** Services MUST encapsulate **residues** -- the
components that survive coherent under stressor contagion -- not units of
functionality and not predicted volatility. A service exists because a typed
Structural stressor (or set of them) requires a place to be absorbed. Reuse and
locality are consequences of correct residue encapsulation, never the
justification for a service.

- Service names MUST NOT describe a function or a domain verb
  (`MarketingService`, `ProcessOrderService` are review blockers).
- Service names MUST denote what is encapsulated, suffixed by their IDesign
  category, per Lowy: `<Thing>Manager` / `<Thing>Engine` / `<Thing>Access`
  (e.g. `ChargeSessionManager`, `AuthEngine`, `CustomerAccess`).

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

**Catalog as authority.** The set of services that may be referenced by any
spec or plan is fixed by the **service catalog** at the Architecture Release the
spec/plan declares (see Architecture versioning). A service absent from that
release's catalog does not exist for `/speckit-specify` and `/speckit-plan`.
Adding, renaming, removing, or merging a service is an architecture-team activity
via the catalog amendment process -- never inline invention in `plan.md`.

**Architecture versioning.** Each architecture is an immutable, versioned
**Architecture Release** -- the catalog and the artifacts it anchors, emitted
into a directory named by semver (`architecture/arch-X.Y.Z/`). The constitution
records the **Current** release directory and, during a migration, the
**Target**. A spec or plan declares the release it builds against and is gated
against that release directory; ids are append-only across releases, so a spec
built against an earlier release stays valid. A new release does **not**
invalidate the current one -- both directories are physically present and
**coexist** until a migration plan completes, after which the new release
becomes Current and the prior is Superseded (retained, not deleted). Moving
Current/Target is a **governed amendment** -- the version pointer moves; these
rules do not. (Full protocol: section 11.)

**Use cases as call chains.** Every feature submitted to `/speckit-specify`
MUST reference a use-case document that declares (a) the call chain as a graph,
(b) the services touched with their category, and (c) the residue each touched
service absorbs. The generated `spec.md` MUST preserve those three sections
**verbatim** under an "Architectural Context" heading.

**Residue lineage (traceability).** Architecture decisions carry their evidence
by reference:

- Every service in the catalog MUST list at least one **Structural** stressor
  identifier (`S-NN`) in its Stressors-absorbed field -- by R-18 every id there
  is Structural (only Structural residues become services). The full stressor
  analysis lives in the SAD (published separately, e.g. via Backstage); the
  catalog carries the resolvable conclusion.
- Every NFR MUST record a **coupling** (or topology) identifier (`C-NN`) in its
  Source field. NFRs live in one register, each carrying an `Applies-to` scope
  that is either `System` (global) or an enumerated use-case set; use cases
  reference applicable NFRs by id and never copy them. The full coupling analysis
  lives in the SAD.
- Known **unstressed surfaces** from the SAD's empirical test are documented
  risk; a plan that knowingly builds on one MUST flag it.

**Binding ADRs.** A runtime, protocol, or middleware decision captured in an
ADR is a binding architecture constraint (Architecture Supremacy). The
implementation half MUST conform to it and MUST NOT substitute an alternative.

**Constitution Check questions (gate at `/speckit-plan`).** The gate MUST answer:

1. Is every service in `plan.md` present in the service catalog?
2. Does each service name follow the category suffix (`*Manager` / `*Engine` /
   `*Access`)?
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

## 7. How RDAG composes into a host constitution

RDAG is a **principle module**, not a whole constitution. The host keeps its
implementation principles (language, testing, observability, ...) and inserts
the Section 6 block alongside them. When an implementation principle collides
with the architecture half over *how the system is decomposed* or over a
*binding ADR*, the Architecture Supremacy Rule resolves it: architecture wins;
implementation chooses only the *how* within the space architecture left open.

The host adopts the principle by **copying** the Section 6 text into its
constitution and recording the RDAG version it adopted. RDAG is versioned here;
when it changes, host projects re-sync the block the same way they amend any
constitution principle (their own governance process applies).

## 8. The completeness test (acceptance criterion)

RDAG and the emitted artifacts are sufficient only if they pass this test:

> Could a spec-kit project implement the system **correctly** using only the
> emitted artifacts plus this standard, **without reading the full SAD**?

A "no" for any case means an artifact or a field is missing. This test, not "which
gate needs it", is the inclusion filter for the artifact set. See
`rdag-conformance.md`.

## 9. Related files

- `rdag-id-scheme.md` -- canonical identifiers (`UC`/`S`/`C`/`NFR`/`ADR` and
  service names) and the append-only stability rule that keeps cited IDs valid
  across SAD iterations.
- `rdag-conformance.md` -- the conformance checklist a host constitution must
  satisfy, plus the completeness test (Section 8) operationalized.
- `../contracts/` -- one contract file per emitted artifact: schema plus the
  field-by-field mapping from the SAD.

## 10. Cross-references to this repository's doctrine

- Decomposition by residue and stressor typing: constitution R-13, R-18.
- NFR traceability to coupling: R-15.
- Smallest-set residue (extend RA before new Resource): R-24.
- Actor-style service grouping (1 Manager = 1 service): R-25.
- Architecture overrides matrix-driven merge signals (precedent for Supremacy):
  R-14.
- Closed architecture / call rules: R-03, R-04.

## 11. Architecture Release Versioning and Migration

An architecture is not frozen: a use case can impact the design, the SAD is
re-run, and a new architecture results. The consumer's constitution must absorb
this **without invalidating in-flight work and without going inconsistent**.
This section defines how. It builds on the append-only id rule
(`rdag-id-scheme.md` §3), which is the foundation that makes coexistence safe.

**Architecture Release = an immutable, versioned directory.** A release is the
full Tier-1 set (catalog + nfr-register + use-cases + ADRs + manifest) emitted
into a directory named by semver: `architecture/arch-X.Y.Z/`. A published
release is **immutable** -- a change does not edit its files; it produces a
**new release directory** (`arch-X.Y.Z+1`). The version lives in the **path**,
so distinct versions are distinct files, never an in-place rewrite.

**The Current Architecture record.** The consumer's constitution carries a
governed record naming the **Current** release directory and, during a
migration, the **Target**. This pointer is the only version-bearing thing in the
constitution that moves; the principle's rules do not. Adopting a new Current,
or opening a migration to a Target, is a **governed amendment** (the host's
process: version bump + Sync Impact Report + owner approval).

**Coexistence is literal.** A new release does not invalidate the current one --
both directories are **physically present**. `Current` (vigente -- what feature
work gates against) and `Target` (the new release -- what the migration plan
gates against) are both valid. A spec built against `arch-1.0.0` keeps reading
the frozen `arch-1.0.0/` files; the migration plan reads `arch-2.0.0/`. No
overwrite, no view to reconstruct. Append-only ids guarantee a name / `S-NN` /
`C-NN` / `NFR-NN` means the same thing across the two directories.

**Migration delta.** A new release's manifest records the **delta** from the
prior release: services added / removed / superseded, NFRs added, ADRs added /
superseded. The delta is what a spec-kit **migration plan** consumes to move the
implementation from `Current` to `Target`. There are no per-entry "lifecycle
states" mutating a shared file -- each release is a frozen snapshot, and the
delta between two snapshots is the cross-version record.

**The migration flow.**

1. `arch-1.0.0/` ships; constitution: `Current = arch-1.0.0`.
2. A use case impacts the architecture; the SAD is re-run; `arch-2.0.0/` is
   emitted (a new directory) with the `1.0.0 -> 2.0.0` delta in its manifest.
3. Governed amendment: `Current = arch-1.0.0`, `Target = arch-2.0.0` (migration
   open). `arch-1.0.0/` stays vigente; feature work continues against it.
4. A migration plan gates against `Target` (`arch-2.0.0/`) and moves the
   implementation.
5. On completion, governed amendment: `Current = arch-2.0.0`; `arch-1.0.0 ->
   Superseded` (the directory is retained, not deleted; prunable after a
   retention window).

**Gate during migration.** A spec/plan declares the Architecture Release it
builds against; the Constitution Check (section 6, Q1-Q6) resolves ids against
**that release directory**. Feature plans declare `Current`; migration plans
declare `Target`. A plan referencing a service absent from its declared
release's catalog fails Q1 -- and if the service exists only in the other
release, the resolution is "drive / await the migration", not inline invention.
