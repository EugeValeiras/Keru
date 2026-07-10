---
title: "RDAG Contract -- nfr-register.md"
version: 0.1.0
date: 2026-05-26
status: Draft (Phase 0b)
---

# RDAG Contract -- `nfr-register.md`

The NFR register is the **single home for every non-functional requirement**.
There is no inline NFR anywhere else: use cases reference register entries by id,
never define them. This makes normalization structural -- a single definition
site means duplication is impossible (`../standard/rdag-id-scheme.md` §1). The
register is authoritative for the `NFR-NN -> C-NN` lineage and for each NFR's
`Applies-to` scope. Doctrine in `../standard/rdag-standard.md`.

**Emitted from:** SAD `NFRs` (S5), derived from the SAD's S4 coupling analysis.
**Landing zone:** the path the consumer's constitution names (suggested:
inside the release directory, e.g. `architecture/arch-X.Y.Z/system-design/nfr-register.md`).

## 1. File schema

```text
# NFR Register
<metadata table: Version (release stamp from handoff manifest), Owner, Status>
## Purpose
## NFRs                 -- one entry per NFR-NN
```

## 2. Per-NFR entry fields

| Field | Required | Meaning |
|---|---|---|
| **Id** | yes | `NFR-NN`, append-only. There is no `NFR-N` document-scoped form. |
| **Statement** | yes | The requirement, **technology-agnostic and measurable** (e.g. "p99 response time < 1s"), never an implementation ("use a Redis cache"). |
| **Applies-to** | yes | `System` (global) or an enumerated use-case set (e.g. `UC-001, UC-002`). Only system-wide is `System`; a bounded UC set is never global. |
| **Source** | yes | The `C-NN` this NFR traces to (R-15), recorded inline -- self-contained for the gate. Every NFR has a real structural cause; the full coupling analysis is SAD-side (Backstage). |
| **Measurable target** | yes | The threshold / metric, stack-agnostic. *How* it is measured (OTel, etc.) is the implementation half. |
| **Status** | yes | `Active` or `Deprecated (<release>, <reason>)`. |

## 3. Field-by-field mapping (SAD -> NFR register)

| Field | SAD source | Rule |
|---|---|---|
| Id (`NFR-NN`) | each NFR in `NFRs` (S5) | Mint append-only; one register, no per-UC inlining. |
| Statement | the NFR text in S5 | Keep technology-agnostic; strip any implementation. |
| Applies-to | the **reach of the inducing coupling** | A coupling that spans the system -> `System`; a coupling confined to a use-case set -> that set. Scope follows the cause. |
| Source (`C-NN`) | the coupling that induces the NFR (SAD S4 coupling analysis) | Carry the `C-NN` inline; no NFR without one. The full coupling analysis is SAD-side (Backstage). |
| Measurable target | the target stated in S5 | If S5 left it `TBD`, carry it as a `NEEDS CLARIFICATION` rather than inventing a number. |

## 4. Normalization (structural)

- Every NFR is defined **exactly once** here. Use cases and `plan.md` reference
  `NFR-NN` ids; they never restate the requirement.
- `Applies-to` is the scope field that replaces the idea of "global vs specific
  lists". A reader gets all NFRs for `UC-002` by selecting entries whose
  `Applies-to` is `System` or contains `UC-002`.
- Because there is one definition site, the "no NFR in two scopes" invariant
  cannot be violated by construction.

## 5. The seam

The register states the requirement and its measurable target; it does **not**
state how the target is met or measured. Caching strategy, metric pipeline,
replica topology -- those are the implementation half. If an NFR's target can
only be honored by an architectural decision (e.g. a runtime that guarantees
ordering), that decision is an ADR and binds per Architecture Supremacy
(`../standard/rdag-standard.md` §4).

## 6. Conformance

Checked by: **CHK-08** (every `NFR-NN` traces to a resolvable `C-NN`, carries an
`Applies-to`, defined once), **CHK-11** (cited ids resolve), **CHK-13**
(append-only ids). See `../standard/rdag-conformance.md`.

## 7. Related files

- `../standard/rdag-standard.md` -- NFR traceability (§6) and gate question 5.
- the SAD (published via Backstage) -- the full coupling analysis behind each `C-NN`.
- `use-case-contract.md` -- use cases reference applicable `NFR-NN` ids.
- `handoff-manifest-contract.md` -- the release stamp pinning the version.
