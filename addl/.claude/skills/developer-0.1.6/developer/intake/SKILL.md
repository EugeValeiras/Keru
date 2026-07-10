---
name: intake
description: D1 (Phase A / FLOW) of the developer meta-skill. Confirms the landed RDAG handoff is conformant, completes the constitution via /speckit-constitution byte-identical (CHK-01) and gets it operator-APPROVED, installs the Q1-Q6 override plan-template, pins the release, and selects the target UC (adding a UC or implementation ADR here if needed -- the only phase where adds are allowed). Governance only -- starts no workflow.
task_types:
  - intake-handoff
  - confirm-readiness
shared_refs:
  - shared/constitution.md
  - shared/glossary.md
---

# intake -- D1 (handoff readiness)

The **Phase A (FLOW)** gate of the Developer cycle. It does **not** produce spec/plan/tasks/code -- it makes the project ready to implement a spec through the two FLOW interaction points: (1) the **constitution gate** -- confirm the handoff landed + conformant, the constitution completed (via `/speckit-constitution`) byte-identical (CHK-01) and **APPROVED by the operator**, and the Q1-Q6 override template installed; and (2) **UC selection** -- enumerate the UCs and pick the target, adding a UC or implementation ADR here if needed (this is the **only** phase where adds are allowed). It records the **pin** (the `arch-X.Y.Z` every later step resolves IDs against). Re-run when the constitution changes or when re-pinning a newer release.

## When to invoke

- After the SAD's S8b landed a release into the consumer workspace and implementation is about to begin.
- When re-pinning to a newer landed release (a migration: a new `arch-X.Y+1.Z` arrived).

## When NOT to invoke

- No `architecture/arch-X.Y.Z/` on disk -- there is nothing to implement against; run the SAD + S8a/S8b first.
- To change the architecture -- that is the SAD, not D1.

## Pre-conditions

- A landed `architecture/arch-X.Y.Z/` directory exists, **and** `.specify/memory/constitution.md` exists. (Entry gate otherwise -- no prior Developer gate required.)
- **The consumer workspace is its own git repository** (spec-kit is branch-per-feature; the orchestrator cuts a worktree per feature). If a fresh project, it is `git init`'d before D1. The **base branch** is whatever the workspace is standing on -- normally `main` or `master`; another name is allowed but the orchestrator surfaces it as a warning (confirm it is the intended integration target). Every feature branch is cut from this base, and D5 integrates back into it.

## Handoff contract

- **Consumes:** `architecture/arch-X.Y.Z/handoff-manifest.md` (release stamp, Ri attestation), `system-design/`, `use-cases/`, `decisions/`, `integration/`, and `.specify/memory/constitution.md`.
- **Produces:** `docs/developer/intake.md` (gate **D1**) -- the readiness note + the pinned release.
- **Carry-forward:** the pin (`arch-X.Y.Z`), the Ri attestation, and the list of available `UC-NNN` (so D2 can pick a target feature).

## Workflow

1. **Resolve the release.** Read `handoff-manifest.md`. Record the release version (the pin), the Ri attestation (must be `Passing`), and the landing map.
2. **Verify conformance + handoff form (deterministic first).** Run, against the landed release:
   - `scripts/fragment-checks/check_ids.py <arch-dir>` -- every cited global ID resolves within the release (D-03 self-consistency).
   - `scripts/fragment-checks/check_principle.py .specify/memory/constitution.md <arch-dir>/integration/principle-decomposition-by-residue.md` -- **CHK-01 at clause level**: the architecture-half principle CLAUSES are byte-identical to the landed principle (numbering / surrounding prose may differ, the clauses may not). This also guards that the Developer has not altered the handoff's half.
   - `scripts/fragment-checks/check_uc_structure.py <arch-dir>` -- **CHK-10**: every use case is well-formed (Architectural Context with Call Chain / Services touched / Residue; every touched service in the catalog). A malformed UC makes downstream scope checks unanchored.
   - `scripts/fragment-checks/check_adr_binding.py <arch-dir>` -- **CHK-12**: every `Binding: Yes` ADR has a populated Conformance check and is enumerated in the manifest, so Q6 can bind the plan to it.
   A failure here is the Architect's defect (a malformed handoff), raised back to the SAD -- not something the Developer patches locally.
3. **Land + complete the constitution (two halves, two owners).** The constitution has an **architecture half** -- landed verbatim from the handoff (`constitution.scaffold.md` / the principle), which the Developer **NEVER edits** (changing it is an upstream re-land: a new `arch-X.Y.Z`, not a local edit) -- and an **implementation half** -- the Developer's own `[TODO]` principles (language/runtime, testing strategy, API conventions, observability, persistence, security). When the Developer operates on the constitution it **only adds implementation-half content**; it must not touch the architecture half. Use `/speckit-constitution` to fill the implementation half (clause-level CHK-01 then confirms the architecture clauses survived the reshape). Separately, **install the Q1-Q6 override** at `.specify/templates/overrides/plan-template.md` by **splicing** the landed two-tier block into a copy of spec-kit's current core `plan-template.md` (NOT a whole-file copy -- `resolve_template` replaces, so a partial override would strip Technical Context / Project Structure); verify the merged override with `check_override.py`. D1's job, not spec-kit's.
4. **Approve the constitution and PIN it (the gate).** Approve once the **implementation half is filled and no implementation principle contradicts the architecture half** (Architecture Supremacy). Operator-**APPROVED** is required before any spec is implemented; the constitution is standing across UCs until it changes. Once approved, **pin the architecture half**: `scripts/fragment-checks/check_drift.py .specify/memory/constitution.md <arch-dir> --pin .specify/memory/.arch-pin.json` records a sha256 of the frozen region (everything but the implementation half) + the binding ADRs. Every later gate re-checks `--against` that pin and BLOCKS on an architecture-half change -- which cannot come from the Developer (it is an upstream re-land). A later change to the implementation half is the Developer's and legitimate, but is flagged (NOTE) so the affected step is re-opened for an impact assessment.
5. **Enumerate UCs and select the target.** List the available `UC-NNN`. If the UC to implement does not exist, **add it here** (impact-assess against the landed release); an implementation **ADR** may also be added here. Adds are a Phase A activity only.
6. **STOP at the gate.** Write `intake.md`, park D1 at `[?]`. The entry point (handing the selected UC to `/speckit-specify`) begins Phase B.

## Output contract

- `docs/developer/intake.md` (scaffold: `developer/templates/intake.md`) with: the pin (`arch-X.Y.Z`), Ri attestation, CHK-01 verdict, ID-resolution verdict, Q1-Q6 override-install verdict, **constitution APPROVED + pinned (A3)** status, the enumerated `UC-NNN` list, and the selected target UC (plus any UC/ADR added this phase).
- A 2-4 line summary for the parent.

## Refusal conditions

| Trigger | Rule | Response |
|---|---|---|
| No landed release on disk | pre-condition | refuse; route to SAD/S8b |
| Consumer workspace is not a git repository | pre-condition | refuse; spec-kit is branch-per-feature -- `git init` (or open the repo's own checkout) before D1 |
| Ri attestation is not `Passing` | D-01 | refuse; the architecture is not implementation-ready |
| CHK-01 mismatch (constitution drifted from the principle) | D-01 | refuse; re-land (S8b) before building |
| Asked to author or change a constitution principle | D-01 | refuse; principles come from the landed release |

## References

- `shared/constitution.md`, `shared/glossary.md`
- `scripts/fragment-checks/check_ids.py`, `check_principle.py` (CHK-01), `check_uc_structure.py` (CHK-10), `check_adr_binding.py` (CHK-12), `check_override.py` (`--build` splice + `--verify`), `check_drift.py` (A3 pin `--pin` / re-check `--against`)
- Templates: `developer/templates/intake.md`, `developer/templates/impact-assessment.md` (if a UC/ADR is added this phase), `developer/templates/back-channel-request.md` (if an add is `needs-architecture`)
- SAD `sdd-interface/standard/rdag-conformance.md`, `handoff-manifest-contract.md`, `integration/plan-template-constitution-check.md`
