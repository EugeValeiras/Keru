---
title: "RDAG Contract -- service-catalog.md"
version: 0.1.0
date: 2026-05-26
status: Draft (Phase 0b)
---

# RDAG Contract -- `service-catalog.md`

The service catalog is the **authority** named by the drop-in principle
(`../standard/rdag-standard.md` §6, "Catalog as authority"): a service absent
from it does not exist for `/speckit-specify` or `/speckit-plan`. This contract
defines the catalog's schema and the field-by-field mapping that produces it
from a SAD. It is the file an emitter loads to generate the catalog; doctrine
lives in the standard, IDs in `../standard/rdag-id-scheme.md`.

**Emitted from:** SAD `Static Architecture` + `Service Grouping Map` (S5),
with residue lineage drawn from the `Stressor Catalog` (S3). **Landing zone in
the consumer:** the path the consumer's constitution names as the catalog
authority, inside the release directory: `architecture/arch-X.Y.Z/system-design/service-catalog.md`.

## 1. File schema

```text
# Service Catalog
<metadata table: Version, Owner, Status, Release stamp (from handoff manifest)>
## Changelog            -- append-only, one entry per handoff release
## Conventions          -- the Manager/Engine/Access suffix reminder (Lowy)
## Static Diagram       -- Mermaid, from SAD Static Architecture
## Catalog Entries
### Managers            -- one entry per `*Manager` service
### Engines             -- one entry per `*Engine` service
### ResourceAccess      -- one entry per `*Access` service
### Resources           -- one entry per Resource (leaf)
## Amendment Process
## Anticipated Future Services  -- informational, NOT authorized for use
```

## 2. Per-entry fields

Every service entry (Manager / Engine / ResourceAccess) carries:

| Field | Required | Meaning |
|---|---|---|
| **Category** | yes | Manager / Engine / ResourceAccess. Constrains call rules. |
| **Status** | yes | `Active` within this release (the catalog is a frozen snapshot inside its `arch-X.Y.Z/` directory), or `Deprecated (scheduled for removal in a future release)` as a forward notice. Cross-version add / remove / supersede is recorded in the manifest **migration delta** (`rdag-standard.md` §11), never by mutating this file. |
| **Introduced in** | yes | The `UC-NNN` where the service first appeared. |
| **Stressors absorbed** | yes | The list of **Structural** `S-NN` this service is the residue of. This is the lineage that Constitution Check question 4 resolves. >=1 required (R-18). |
| **Residue (narrative)** | yes | Prose statement of the residue: the coherent capability that survives the absorbed stressors, and why it is isolated. **Derived from the `S-NN` above** -- not a separate "volatility" judgment, and not computed from a prediction of change. |
| **Used by** | yes | The `UC-NNN` list that touches the service. |
| **May call** | yes | Downward targets allowed by the closed architecture (R-03/R-04). |
| **May NOT call** | yes | The forbidden edges, stated explicitly (e.g. an Engine may not call a Manager or a Resource directly). |
| **State** | yes | Manager: stateless (workflow state is per-instance, not service state). Engine/RA: stateless (mandatory). |
| **Binding ADRs** | if any | `ADR-NNN` ids whose runtime/protocol decision constrains this service (Architecture Supremacy, `../standard/rdag-standard.md` §4). |

A **Resource** entry carries: Type (Resource / Resource-external-system),
Owner, Accessed-by (the single `*Access` ResourceAccess that may reach it --
one ResourceAccess per Resource, R-24), and a Schema-management note. A Resource defers its concrete technology
to the implementation half (the seam): name the Resource and its role, not the
product. "Technology: per constitution Tech Stack" is the correct phrasing.

## 3. Field-by-field mapping (SAD -> catalog)

| Catalog field / section | SAD source | Rule |
|---|---|---|
| Service name + category (suffix) | `Service Grouping Map` (S5) -- the authority of names (R-25) | Names come from here (Lowy suffix convention), with S4->S5 parity. 1 Manager = 1 service. |
| Static Diagram | `Static Architecture` (S5) | Render the component set and the legal call edges as Mermaid. |
| Stressors absorbed (`S-NN`) | `Static Architecture` residue-mapping -> `Stressor Catalog` (S3) | Each component maps to the Structural stressors it absorbs (R-18). Residue-mapping, not a matrix column. |
| Residue (narrative) | derived from the absorbed `S-NN` (and the residue's description in `Static Architecture`) | State the coherent capability that survives those stressors; do not restate the id list, and do not frame it as predicted "volatility". |
| Used by (`UC-NNN`) | `Use Cases` (S5) | The UCs whose call chain touches the service. |
| May call / May NOT call | closed-architecture call rules (R-03/R-04) + the call graph in `Static Architecture` | Derive both the allowed and the forbidden edges; state both. |
| State | the IDesign category invariant | Not a SAD choice -- fixed by category. |
| Resource (per RA) | `Static Architecture` | One RA per Resource (R-24); name the Resource, defer the tech. |
| Binding ADRs | the SAD's ADRs | Only ADRs whose decision constrains this service's runtime/protocol. |
| Changelog / Version | `handoff-manifest` + Amendment Process | Append-only; version pinned by the release stamp (see below). |

## 4. Residue lineage -- the strengthening over a plain catalog

The decomposition driver is the **residue**, not predicted volatility. A catalog
that records only a prose description of what a service isolates lets the gate
ask just "is it credible?" (a judgment). Here the prose **Residue (narrative)**
is *derived from* the **Stressors absorbed** (`S-NN`), and recording those ids
makes Constitution Check question 4 mechanical: every service must list >=1
Structural `S-NN` in its Stressors-absorbed field (Structural by R-18 -- only
Structural residues become services). The prose stays for human readers; the ids
carry the enforcement (`rdag-standard.md` §1). The full stressor analysis is
SAD-side (published via Backstage), not a handoff artifact. There is no
independent "volatility" calculation -- the field never existed in this method.

## 5. Versioning and amendments

- The catalog version is **pinned by the handoff manifest's release stamp**
  (CHK-14) so the catalog, nfr-register, and use cases a spec cites are always a
  coherent set.
- The catalog keeps an **append-only Changelog**, one entry per release,
  describing services added / deprecated / re-traced.
- Adding, renaming, removing, or merging a service is an **architecture-team
  amendment**, never inline invention in `plan.md`. A `/speckit-plan` that needs
  an absent service stops and raises a catalog amendment request -- the formal
  back-channel (`rdag-standard.md` §6, "Catalog as authority").
- Id stability per `../standard/rdag-id-scheme.md` §3: deprecate, never
  delete-and-reuse; renames record the `old -> new` mapping.

## 6. Conformance

This contract is checked by: **CHK-06** (naming), **CHK-07** (every service
traces to a Structural `S-NN`), **CHK-09/10** (call rules and use-case
coverage), **CHK-11** (cited ids resolve), **CHK-12** (binding ADRs locatable),
**CHK-13** (append-only ids). See `../standard/rdag-conformance.md`.

## 7. Related files

- `../standard/rdag-standard.md` -- catalog authority, call rules, Supremacy.
- `../standard/rdag-id-scheme.md` -- `S-NN`, `ADR-NNN`, service-name identity.
- the SAD (published via Backstage) -- the full stressor analysis behind each `S-NN`.
- `use-case-contract.md` -- "Used by" and the verbatim call-chain sections.
- `handoff-manifest-contract.md` -- the release stamp that pins the version.
