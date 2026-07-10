---
name: specify
description: D2 of the developer meta-skill. Invokes spec-kit's /speckit-specify (and /speckit-clarify) to produce a feature spec from a target UC-NNN, then reviews it so the use-case's Architectural Context is preserved verbatim and every service/ID reference resolves to the landed release.
task_types:
  - specify-feature
  - drive-speckit-specify
shared_refs:
  - shared/constitution.md
  - shared/glossary.md
---

# specify -- D2 (feature spec)

Drives **spec-kit `/speckit-specify`** to produce one feature spec, seeded from a use-case in the landed release. spec-kit writes the spec; this gate makes sure it stays faithful to the architecture.

## When to invoke

- D1 approved and the operator named a target `UC-NNN` to implement.
- To re-specify a feature after a D2 reopen.

## When NOT to invoke

- D1 not approved (no confirmed, pinned release).
- To write the spec by hand -- `/speckit-specify` owns the content.

## Pre-conditions

- D1 `[x]` approved; a target `UC-NNN` named that exists in the pinned `architecture/arch-X.Y.Z/use-cases/`.

## Handoff contract

- **Consumes:** the target `uc-NNN-<slug>.md` (its **Architectural Context** block: Call Chain, Services touched, Residue), `system-design/service-catalog.md` (to validate the services), and the pin from D1.
- **Produces:** `specs/NNN-<slug>/spec.md` (gate **D2**) -- spec-kit's feature spec, with the UC's Architectural Context preserved.
- **Carry-forward:** the services this feature touches + their `S-NN` lineage and any binding ADRs they reference, so D3's plan + Constitution Check has them in hand.

## Workflow

1. **Invoke spec-kit (inside the orchestrator's worktree).** The orchestrator has already cut a git worktree on a fresh `NNN-<slug>` branch from the clean base. Run `/speckit-specify` **in that worktree** with `SPECIFY_FEATURE_DIRECTORY=specs/NNN-<slug>` set so spec-kit's `specs/NNN-<slug>/` matches the branch (the command names the dir itself + writes `.specify/feature.json` for downstream gates; it does not take `--short-name`) -- seeded from the target `UC-NNN` and its description. **Do not create or switch a git branch yourself** (the orchestrator owns it). Let spec-kit produce `spec.md`. If it leaves ambiguities, run `/speckit-clarify`. (See `SKILL.md` -- the Consumer-repo git lifecycle section.)
2. **Preserve Architectural Context verbatim.** The spec MUST carry the UC's three-section Architectural Context (Call Chain / Services touched / Residue) **byte-identical** under an "Architectural Context" heading. Run `scripts/fragment-checks/check_arch_context.py specs/NNN-<slug>/spec.md architecture/arch-X.Y.Z/use-cases/uc-NNN-*.md`.
3. **Resolve references (deterministic).** Run `scripts/fragment-checks/check_ids.py` over the spec: every service named is in the catalog (D-01 Q1 preview), every `UC/S/C/NFR/ADR` id resolves to the pin (D-03).
4. **No scope drift beyond the UC (deterministic).** Run `scripts/fragment-checks/check_scope.py specs/NNN-<slug>/spec.md architecture/arch-X.Y.Z/use-cases/uc-NNN-*.md`: every service the spec names must be in the UC's "Services touched" (the catalog is the universe of available services; the UC is what THIS feature may touch), and every NFR it references must be in the UC's Applicable NFRs. A wider scope is not a Developer decision -- add/extend the UC in Phase A.
5. **Impact-on-add (if the feature is a NEW UC).** If this is not a pre-existing `UC-NNN` but a use-case discovered now, emit an `## Impact assessment` (Affected / Absorption / Rationale) -- scaffold `developer/templates/impact-assessment.md`. `absorbed` -> it gets the next `UC-NNN` and proceeds; `needs-architecture` -> STOP and raise a back-channel request (`developer/templates/back-channel-request.md`; no architecture reopen forced from here).
6. **STOP at the gate.** Park D2 at `[?]`. Do not begin D3.

## Output contract

- `specs/NNN-<slug>/spec.md` (spec-kit's structure) with the verbatim Architectural Context block.
- The check verdicts (arch-context preserved, IDs resolve) + a 2-4 line summary.

## Refusal conditions

| Trigger | Rule | Response |
|---|---|---|
| Target `UC-NNN` not in the pinned release | D-03 | refuse; pick a real UC or raise impact-on-add for a new one |
| A service in the spec is absent from the catalog | D-01 (Q1) | catalog amendment request; do not invent it |
| Architectural Context altered, not verbatim | D-01 | refuse; preserve it byte-identical |

## References

- `shared/constitution.md`, `shared/glossary.md`
- `scripts/fragment-checks/check_arch_context.py`, `scripts/fragment-checks/check_ids.py`, `scripts/fragment-checks/check_scope.py`
- Templates: `developer/templates/impact-assessment.md`, `developer/templates/back-channel-request.md`
- SAD `sdd-interface/contracts/use-case-contract.md`
