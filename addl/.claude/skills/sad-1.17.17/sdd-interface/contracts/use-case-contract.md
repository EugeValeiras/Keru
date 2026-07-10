---
title: "RDAG Contract -- uc-NNN-*.md (use case)"
version: 0.2.0
date: 2026-06-11
status: Draft (Phase 0b)
---

# RDAG Contract -- `uc-NNN-*.md` (use case)

The use case is the artifact `/speckit-specify` consumes **directly**: a feature
references a use case, and the generated `spec.md` preserves the use case's
architectural sections **verbatim**. This is where the architecture travels with
the feature into implementation. This contract defines the use-case schema, the
verbatim-preservation rule, and the mapping from the SAD. Doctrine in
`../standard/rdag-standard.md` §6 ("Use cases as call chains"); ids in
`../standard/rdag-id-scheme.md`.

**Emitted from:** SAD `Use Cases` (S5), with services from `Static Architecture`
/ `Service Grouping Map` and NFR references from the NFR register. **Landing
zone:** the path the consumer's constitution names (in the spec-kit demo:
`architecture/arch-X.Y.Z/use-cases/uc-NNN-*.md`).

## 1. File schema

```text
# UC-NNN -- <Title>
<metadata table: Use Case ID, Title, Status, Owner, Classification>
## 1. Business Context
## 2. Actors
## 3. Operations in Scope        -- Op-A, Op-B, ...
## 4. Architectural Context      -- THE verbatim block (see §2)
## 5. Main Flows                 -- per operation
## 6. Alternative Flows
## 7. Postconditions
## 8. Business Rules             -- BR-N
## 9. Acceptance Criteria        -- AC-N
## 10. Applicable NFRs           -- referenced NFR-NN ids (see §4)
## 11. NEEDS CLARIFICATION       -- NC-N
## 12. Related Documents
## 13. Impact assessment         -- conditional; see note below
```

Section 13 is OPTIONAL when the UC is a primary UC emitted in S5 inside
`residual-design.md`, and REQUIRED when the UC is added via the
**Add-Use-Case** action (`SKILL.md` Post-S5 actions). It carries three verbatim
fields -- `Affected gates:`, `Outcome:` (`no-op` | `iterating Sn` |
`reopen Sn`), `Rationale:` -- on the **workspace** copy of the UC; the
transcription staged for the consumer does not carry it (the consumer does not
consume gate tracker state).

## 2. The Architectural Context block (verbatim into spec.md)

This block, and only this block, is copied verbatim by `/speckit-specify` into
the `spec.md` under an "Architectural Context" heading. It has exactly three
subsections:

| Subsection | Content | Rule |
|---|---|---|
| **Call Chain** | A Mermaid graph: `Client -> Manager -> Engine -> ResourceAccess -> Resource`. | Must respect the layer rules (R-03/R-04): no Manager->Manager sync, no Client->ResourceAccess, no Engine->Manager, no Engine->Resource. |
| **Services touched** | A table: service, category, role in this UC. | **Every service MUST exist in `service-catalog.md`.** Names come from the catalog (Service Grouping Map authority). No service may be introduced here that is not in the catalog. |
| **Residue** | Per touched service, the `S-NN`(s) it absorbs in this UC's context. | Consistent with the catalog's Stressors-absorbed lineage; the full stressor analysis is SAD-side (Backstage). This is the residue each service is, not a re-description. |

`/speckit-plan` MUST NOT introduce a service absent from "Services touched"
unless a catalog amendment authorizes it (`../standard/rdag-standard.md` §6).

## 3. Field-by-field mapping (SAD -> use case)

| Section | SAD source | Rule |
|---|---|---|
| Business Context, Actors, Operations | `Use Cases` (S5) | Narrative; operations get `Op-A..N` ids (document-scoped). |
| Call Chain | the UC's call chain in `Use Cases` / C4 (S5) | Render as Mermaid; obey layer rules. |
| Services touched | the services the chain touches, from `Static Architecture` / `Service Grouping Map` | Names = catalog names (parity); every one must be in the catalog. |
| Residue (`S-NN` per service) | the catalog's service->`S-NN` lineage | Cite the same `S-NN`; do not re-derive. |
| Main / Alternative Flows | `Use Cases` (S5) | Step-by-step per operation. |
| Business Rules (`BR-N`), Acceptance Criteria (`AC-N`) | `Use Cases` (S5) | Document-scoped ids. |
| Applicable NFRs | the NFR register entries whose `Applies-to` is `System` or contains this `UC-NNN` | Reference by `NFR-NN`; never inline (see §4). |
| NEEDS CLARIFICATION (`NC-N`) | S6 unstressed surfaces (`U-NN`) and open questions relevant to this UC | A `NC-N` may point at a `U-NN` when the gap is an unstressed surface. |

## 4. NFRs are referenced, never inlined

Section 10 lists `NFR-NN` ids only -- the requirement text lives once in
`nfr-register.md` (normalization, `nfr-register-contract.md` §4). A use case
selects the register entries whose `Applies-to` is `System` or contains its
`UC-NNN`. This is a deliberate divergence from the demo's inline-NFR style: it
prevents the same NFR drifting between two use cases.

## 5. Verbatim preservation -- why it matters

If `/speckit-specify` could paraphrase the Call Chain or Services touched, the
architecture would silently mutate on its way into the spec. Verbatim copy makes
the spec's Architectural Context provably identical to the use case, so the
`/speckit-plan` gate checks a faithful copy, not a paraphrase. The contract
between architecture and feature work is byte-level on these three subsections.

## 6. The use-case set is open -- architecture seeds, the team extends

Unlike the service catalog (a closed authority), the use-case set is **not
closed by architecture**. The SAD emits the **primary** use cases -- the ones
that drove the residue analysis and shaped the architecture. The feature team
adds more over time, and MUST be able to: a new use case composes existing
catalog services into a new call chain.

A team-authored use case still obeys this contract: its Services touched must be
in the catalog, its Architectural Context is verbatim-preserved, its NFRs are
referenced by id. When a new use case needs something the architecture has not
provided, it does not invent it -- it raises a back-channel request
(`../standard/rdag-standard.md` §6):

- needs an absent service -> catalog amendment request;
- needs an unmade runtime/protocol decision -> ADR request;
- **surfaces a stressor the analysis never saw** -> a residue-analysis request
  that may open a new `S-NN` (and, if Structural, a new residue/service).

That last path is the seam back into the method itself, operationalized by
`SKILL.md` Post-S5 actions (Add-Use-Case): the `## Impact assessment` block on
a newly added UC carries the `Outcome:` field that drives the FLOW.md
transition -- `reopen S3` when a new unabsorbed stressor surfaces, `reopen S5`
when a new service is needed, `iterating S5` when only the Residue Mapping
changes (frontier only -- with downstream gates approved it escalates to
reopen), `no-op` when the UC is a reword or its new stressor is absorbed by
existing residues (recorded in the Stressor Catalog's
`Post-S5 additions -- absorbed` subsection). The orchestrator applies the
outcome's FLOW.md transition per `SKILL.md` Gate state machine (canonical);
the UC itself never mutates the tracker.

## 7. Conformance

Checked by: **CHK-09** (call-chain layer rules), **CHK-10** (the three
subsections present; every touched service in the catalog), **CHK-11** (cited
`S-NN`, `NFR-NN` resolve), **CHK-13** (append-only `UC-NNN`). See
`../standard/rdag-conformance.md`. The verbatim copy itself is a host-side
behavior of `/speckit-specify`, asserted at integration (CHK-03 wiring).

## 8. Related files

- `../standard/rdag-standard.md` -- use-cases-as-call-chains (§6), gate questions.
- `catalog-contract.md` -- the catalog every touched service must be in; the
  Stressors-absorbed lineage the Residue section mirrors.
- `nfr-register-contract.md` -- the NFRs this use case references by id.
- the SAD (published via Backstage) -- the full stressor analysis behind the
  Residue `S-NN`, and the empirical test's `U-NN` a `NC-N` may note.
