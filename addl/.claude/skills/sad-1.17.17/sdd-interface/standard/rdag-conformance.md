---
title: "RDAG -- Conformance Checklist and Completeness Test"
version: 0.1.0
date: 2026-05-26
status: Draft (Phase 0a)
---

# RDAG -- Conformance Checklist and Completeness Test

This file makes "mechanically checkable" (`rdag-standard.md` §1) concrete. It
lists the assertions a host constitution and an emitted artifact set must
satisfy, phrased so a validator -- a future emitter self-check, this repo's
`sad-auditor`, or a `/speckit-analyze` extension -- can verify them. It defines
no doctrine (see `rdag-standard.md`) and no IDs (see `rdag-id-scheme.md`).

Each assertion has a `CHK-NN` id. A failing assertion is a **blocker**, not a
warning: host-conformance failures block integration; artifact-set failures
block emission; the in-repo gate failures (questions 4-6) block `/speckit-plan`.

> **Deterministic subset is script-backed.** The mechanical core of the
> artifact-set checks -- the manifest Artifact-inventory matching the files
> actually emitted (CHK-11), recited "N services" / "N binding ADRs" counts
> matching their enumerated tallies (CHK-14), and every enumerated binding ADR
> being locatable as a `decisions/ADR-*.md` file (CHK-12) -- is reconciled by the
> tested hard-fail script `scripts/fragment-checks/check_handoff.py`. It is
> self-contained over the emitted handoff dir (it never opens the SAD) and runs
> green on `sdd-interface/examples/ev-charging/arch-1.0.0/`. The remaining CHK-NN
> (naming, residue/coupling lineage, call rules, the completeness test CHK-T)
> stay heuristic prose review. Mechanical+deterministic step -> tested script,
> not LLM prose (`shared/mechanical-determinism-snippet.md`).

## 1. Host-constitution conformance (checked at integration time)

The consuming project's constitution must satisfy these for RDAG to have teeth.

- **CHK-01** -- The Section 6 principle block is present **in the file
  `/speckit-plan` actually reads**, copied verbatim from the adopted RDAG
  version. Verified by a **mechanical diff** of the landed principle against the
  emitted `integration/principle-decomposition-by-residue.md` -- run by S8 at
  **landing** (Phase 2), not deferred to a later audit. The host may renumber
  the principle and adjust surrounding prose; the normative clauses are byte-
  identical (no rewrite, no condensation).
- **CHK-02** -- The host records which RDAG version it adopted.
- **CHK-03** -- The six Constitution Check questions are wired into the
  `/speckit-plan` gate, and a "no" on any of them blocks the plan and is
  **not** resolvable via a Complexity Tracking entry. The wiring is **delivered**
  by S8 as `integration/plan-template-constitution-check.md` (a two-tier block:
  Tier 1 Q1-Q6 architecture, NON-WAIVABLE, excluded from Complexity Tracking;
  Tier 2 implementation, waivable). Applying it to the consumer's
  `plan-template.md` makes CHK-03 true by construction; without it, CHK-03 is
  merely asserted.
- **CHK-04** -- No implementation-half principle contradicts the architecture
  half on how the system is decomposed or on a binding ADR (Architecture
  Supremacy honored). A host **competing decomposition principle** (canonical
  case: "Service Decomposition by Volatility") is a CHK-04 conflict: the
  Residue principle **supersedes** it (S8 insert/replace merge sub-flow); the
  two are NOT merged.
- **CHK-05** -- The adopted principle text contains zero concrete-technology
  terms. Concrete bindings (Dapr, brokers, ...) live in the consumer's
  **Current Architecture** record, NEVER inside the principle's normative
  clauses.

## 2. Artifact-set conformance (checked at emission time)

Mechanical assertions over the emitted artifacts. Most are regex- or
lookup-checkable.

- **CHK-06** -- Every service name matches the category suffix
  `(Manager|Engine|Access)$` (Lowy convention) or is a declared Resource entry.
  No functional/verb names.
- **CHK-07** -- Every service in the catalog lists at least one **Structural**
  `S-NN` in its Stressors-absorbed field (Structural by R-18). Self-contained:
  the full stressor analysis is SAD-side (Backstage), not a handoff artifact.
- **CHK-08** -- Every `NFR-NN` records a `C-NN` (or a topology row) in its
  Source field (R-15), carries an `Applies-to` value (`System` or an enumerated
  use-case set), and is defined in the register exactly once (use cases
  reference it by id, never define it inline). The full coupling analysis is
  SAD-side.
- **CHK-09** -- Every call edge in every use case respects the layer rules:
  no Manager->Manager synchronous, no Client->ResourceAccess, no
  Engine->Manager, no Engine->Resource.
- **CHK-10** -- Every use case declares Call Chain + Services touched (with
  category) + Residue, and every service it touches exists in the catalog.
- **CHK-11** -- Every cited global ID (`rdag-id-scheme.md` §1) resolves at the
  manifest-pinned version. No broken traces.
- **CHK-12** -- Every binding ADR's runtime/protocol/middleware decision is
  referenced from the catalog (or manifest), so Constitution Check question 6
  can locate it.
- **CHK-13** -- Global IDs are append-only relative to the previous handoff: no
  renumber, no reuse; deprecated IDs are retained with their note.
- **CHK-14** -- The handoff manifest pins one coherent release stamp shared by
  every emitted artifact in the set.
- **CHK-16** -- Each release is an **immutable versioned directory**
  `architecture/arch-X.Y.Z/`; its manifest declares the semver and status
  (`Current` or `Target`). A published release directory is never edited in
  place -- a changed architecture is a **new directory** (`rdag-standard.md`
  §11).
- **CHK-17** -- When a release supersedes a prior one, its manifest carries a
  **migration delta** (services added / removed / superseded, new NFRs, new /
  superseded ADRs). The prior release directory is **retained**, not deleted, so
  the two coexist during migration.

## 3. Emission precondition

- **CHK-15** -- A handoff is emitted only from a SAD whose S6 Residual Index is
  passing and whose S7 assembly is complete. An un-validated SAD has no right to
  generate downstream architecture. (Strength gate on the producer side.)

## 4. The completeness test (the inclusion filter)

This operationalizes `rdag-standard.md` §8. It is the test that decides whether
the artifact set is sufficient -- a stricter filter than "which gate needs it".

- **CHK-T** -- For each use case, walk every operation (`Op-A`..`Op-N`) and
  confirm that **using only the emitted set plus this standard, without opening
  the SAD**, a reader can determine:
  1. which services the operation touches and their categories;
  2. the residue (`S-NN`) each touched service absorbs;
  3. the NFRs that apply and their `C-NN` lineage;
  4. any binding ADR that constrains the runtime/protocol of the operation;
  5. the data shapes and acceptance criteria needed to implement it;
  6. whether the operation builds on an unstressed surface (`U-NN`).

  Any item that cannot be answered from the emitted set is a missing artifact or
  a missing field -- fix the contract, not the instance.

## 5. Who runs what, when

| Assertions | When | Who |
|---|---|---|
| CHK-01..05 | integration (adopting RDAG into a project) | architect / setup step |
| CHK-06..15, CHK-T | emission (handoff from a SAD) | the emitter (S8) + `sad-auditor` |
| CHK-11/12/14 deterministic subset | emission (close of S8a) | `scripts/fragment-checks/check_handoff.py` (tested hard-fail) |
| CHK questions 4-6 (`rdag-standard.md` §6) | every `/speckit-plan` | spec-kit, against its own constitution |
