---
title: "RDAG -- Identifier Scheme and Stability Rule"
version: 0.1.0
date: 2026-05-26
status: Draft (Phase 0a)
---

# RDAG -- Identifier Scheme and Stability Rule

This file defines the canonical identifiers that let the emitted artifacts
trace to each other **by reference** (residue lineage, `rdag-standard.md` §6),
and the stability rule that keeps a cited identifier valid across SAD
iterations. It is the file an emitter loads to mint IDs correctly; it carries no
doctrine (see `rdag-standard.md`) and no schema (see `../contracts/`).

A citation is only as strong as the stability of what it points at. Constitution
Check questions 4-6 (`rdag-standard.md` §6) resolve cited IDs against the
emitted artifacts; if IDs drift, the gate silently passes on stale evidence.
This file exists to prevent that.

## 1. Global identifiers (unique across the whole handoff)

These cross artifact boundaries and MUST be unique within one handoff (one
consuming project / bounded context). They are the only IDs that may be cited
from another artifact.

| ID | Format | Minted in (SAD sub-skill) | Points at | Cited from |
|---|---|---|---|---|
| Use case | `UC-NNN` (3 digits) | use cases (S5) | -- | spec.md, catalog "Used by" |
| Stressor | `S-NN` | SAD: Stressor Catalog (S3) | -- | catalog (Stressors-absorbed, inline) |
| Coupling | `C-NN` | SAD: Contagion (S4) | one or more `S-NN` | nfr-register (Source) |
| NFR | `NFR-NN` | NFR register (S5) | one `C-NN` (or topology row); `Applies-to` = `System` or a UC set | use cases (by ref), plan.md |
| ADR | `ADR-NNN` (3 digits) | ADRs | services, `S-NN`, runtime/protocol | catalog, plan.md |
| Unstressed surface | `U-NN` | SAD: Empirical Test (S6) | the gap left open | SAD-side (Backstage); a use-case `NC` may note it |
| Service | `*Manager` / `*Engine` / `*Access` name; Resource name | Service Grouping Map (S5) | its Structural `S-NN`(s) | use cases, catalog, spec.md, plan.md |

Notes:

- **The service name is the identity of its Structural residue.** No separate
  residue ID is minted; a service traces to the `S-NN` stressors it absorbs (R-18).
- **Stressor type is a field, not part of the ID.** R-13 types (Structural /
  Topological / Business / Combined) live in the SAD's stressor analysis and
  travel with the `S-NN`. For Tier 1, the catalog's Stressors-absorbed field
  lists only **Structural** `S-NN` (R-18) -- exactly what Constitution Check
  question 4 needs -- so a re-classification does not change the ID.
- **All NFRs live in one register; scope is a field, not a location.** Every
  NFR is defined exactly once as `NFR-NN` in the NFR register (S5), with an
  `Applies-to` field whose value is either `System` -- a *global* NFR, e.g. "all
  response times < 1s", not tied to any use case -- or an enumerated use-case
  set, e.g. `UC-001, UC-002` (*scoped* to those, even if there are only two; a
  bounded UC set is never "global"). **Only system-wide is global.** Use cases
  **reference** their applicable NFRs by id and never copy the definition.
  **Normalization is structural:** a single definition site makes duplication
  impossible. Every NFR carries `C-NN` / topology lineage (R-15) regardless of
  its `Applies-to`.

## 2. Document-scoped identifiers (unique only within their document)

These never cross artifact boundaries and carry no global stability guarantee.
Do not cite them from another artifact.

| ID | Format | Scope |
|---|---|---|
| Operation | `Op-A`, `Op-B`, ... | within one use case |
| Business rule | `BR-N` | within one use case |
| Acceptance criterion | `AC-N` | within one use case |
| Functional requirement | `FR-NNN` | within one spec.md |
| Needs-clarification | `NC-N` | within one use case |

`BR-1` in `UC-001` and `BR-1` in `UC-002` are different rules. To reference one
unambiguously across documents, qualify it: `UC-002 / BR-9`.

NFRs are **not** document-scoped: they live in the single global register (§1)
with an `Applies-to` field, so a use-case-only NFR is still `NFR-NN`, not
`NFR-N`. A use case lists the `NFR-NN` ids that apply to it; it never defines an
NFR inline.

## 3. The append-only stability rule

> A global identifier is **minted once and never renumbered or reused.** A new
> SAD iteration may **add** a new ID or **deprecate** an existing one. It MUST
> NOT delete-and-reuse a number, nor renumber an existing ID.

This is what makes a `spec.md` that cited `S-07` last quarter still correct
after a fresh SAD run -- and it is the foundation of **Architecture Release
coexistence** (`rdag-standard.md` §11): a `Current` and a `Target` release can
both be valid at once precisely because an id never changes meaning between
them.

> **Architecture Release id.** A whole Tier-1 set is versioned as a release,
> emitted into an **immutable directory** named by semver
> (`architecture/arch-X.Y.Z/`). It is not a per-artifact id; it versions the set
> via the **path**. Cross-version change is recorded in the new release's
> **migration delta** (manifest), not by mutating any file -- each release
> directory is a frozen snapshot (`rdag-standard.md` §11).

- **Add.** New residues, stressors, couplings, NFRs, use cases, ADRs, or
  surfaces take the next free number in their series. Numbering is per-series
  and monotonic, never reset.
- **Deprecate.** An ID that no longer applies stays in its artifact, marked
  `Deprecated (<iteration>, <reason>)`, retained for at least one quarter so a
  stale citation surfaces a clean diagnostic instead of a dangling reference.
  This mirrors the catalog amendment discipline (a removed service keeps a
  deprecation note).
- **Rename.** Prefer **deprecate-old + add-new** over an in-place rename. If a
  service must be renamed, it is a catalog amendment that records the
  `old -> new` mapping and carries a search-and-replace plan across active
  spec/plan documents; the old name is deprecated, never silently repointed.

## 4. Reference resolution

A citation resolves **within the handoff (Tier 1)** as follows; the full SAD
analysis (published via Backstage) is the provenance, not a shipped handoff file:

- `S-NN` -> the service catalog's Stressors-absorbed field (id + Structural type, inline).
- `C-NN` -> the nfr-register's Source field.
- `NFR-NN` -> the NFR register (and through it, its `C-NN`).
- `ADR-NNN` -> `ADR-NNN.md` (the decision and whether it is binding).
- `U-NN` -> the SAD's empirical test (Backstage); not a Tier-1 handoff artifact.
- service name -> `service-catalog.md` (the entry, and its `S-NN` lineage).

A citation that does not resolve at the pinned version is a **broken trace** --
a Constitution Check failure (questions 4-6), not a warning. The handoff
manifest (`../contracts/handoff-manifest-contract.md`) is what makes "the
pinned version" unambiguous: all emitted artifacts in one handoff share one
release stamp, so cross-references are always resolved within a coherent set.

## 5. Relationship to existing conventions

- `UC-NNN`, `NFR`, `BR`, `AC`, `NC`, `FR` already appear in spec-kit use cases
  and specs; RDAG adopts them rather than inventing parallels. RDAG adds the
  lineage series (`S`, `C`, `U`) and the global/scoped distinction.
- 3-digit `UC-NNN` and `ADR-NNN` align with spec-kit's sequential branch
  numbering (`001-*`, `002-*`).
