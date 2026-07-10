---
name: plan
description: D3 of the developer meta-skill -- the governance gate. Invokes spec-kit's /speckit-plan to produce the implementation plan, then runs the RDAG Constitution Check (Q1-Q6) against the landed release. Q1-Q4 are non-waivable; a No routes to a back-channel request, never an inline fix.
task_types:
  - plan-feature
  - drive-speckit-plan
  - constitution-check
shared_refs:
  - shared/constitution.md
  - shared/glossary.md
---

# plan -- D3 (implementation plan + Constitution Check)

The governance heart of the Developer chain. Drives **spec-kit `/speckit-plan`** to produce the plan, then runs the **Constitution Check (Q1-Q6)** -- the runtime expression of D-01 Architecture Supremacy. This is where the implementation is held to the binding architecture before any task or line of code exists.

## When to invoke

- D2 approved for a feature; ready to plan it.
- To re-plan after a D3 reopen or after a Constitution Check failure was resolved (catalog amended / ADR raised).

## When NOT to invoke

- D2 not approved.
- To write the plan by hand -- `/speckit-plan` owns the content.

## Pre-conditions

- D2 `[x]` approved for this feature; the feature `spec.md` carries the verbatim Architectural Context.

## Handoff contract

- **Consumes:** the feature `spec.md`, `system-design/service-catalog.md`, `system-design/nfr-register.md`, the relevant `decisions/ADR-*.md` (binding), and the landed `plan-template-constitution-check.md` wiring.
- **Produces:** `specs/NNN-<slug>/plan.md` (+ spec-kit's `research.md`, `data-model.md`, `contracts/`, `quickstart.md`) -- gate **D3** -- with the Constitution Check section answered.
- **Carry-forward:** the Q1-Q6 verdicts and the task-relevant constraints (binding ADRs, NFR scopes) so D4's tasks stay conformant.

## Workflow

1. **Confirm the governed entry, then invoke spec-kit.** First run `scripts/fragment-checks/check_entry.py .` (A5): the Q1-Q6 override template and the D1 pin must be present, or `/speckit-plan` would fall back to spec-kit's stock template and the Constitution Check would be silently absent. Then run `/speckit-plan`; the landed override makes spec-kit answer the Constitution Check inline. (`/speckit-analyze` does NOT belong here -- it is read-only and runs at the D4->D5 boundary, after `tasks.md` exists; see `implement`.) After the plan exists, `check_entry.py . --plan specs/NNN-<slug>/plan.md` confirms it actually carries the gate (proof it was not produced by a bypassing direct `/speckit-plan`).
2. **Run the Constitution Check (Q1-Q6) -- now fully deterministic.** Run `scripts/fragment-checks/check_constitution.py specs/NNN-<slug>/plan.md architecture/arch-X.Y.Z/`. It mechanically verifies Q1 catalog membership, Q2 naming suffix, **Q3 call-chain layering** (the call graph is parsed and every illegal transition rejected -- no longer heuristic), Q4 `S-NN` presence, Q5 `C-NN` presence, and **Q6 binding-ADR conformance** -- for each `Binding: Yes` ADR it evaluates the ADR's own *Conformance check* condition against the plan's call graph and transport (e.g. no synchronous Manager->Manager call; the mandated mechanism actually named), not mere id citation.
   - **Q1** every plan service in catalog / **Q2** category suffix / **Q3** layer rules (no Manager->Manager sync, no Client->ResourceAccess, no Engine->Manager) / **Q4** ≥1 `S-NN` per service / **Q5** each NFR cites a `C-NN` / **Q6** runtime/protocol/middleware conforms to binding ADRs.
   - **Q1-Q4 NON-WAIVABLE** (excluded from Complexity-Tracking waivers); **Q5-Q6 NON-WAIVABLE** per RDAG.
3. **On any No -- back-channel, never inline (D-01).** Emit the precise request using `developer/templates/back-channel-request.md`: Q1 No -> *catalog amendment request* (Form A); Q4/Q5 No -> *residue-analysis request* (Form C; the architecture is incomplete); Q6 No -> conform the plan or raise an *ADR request* (Form B). STOP; do not edit the plan to mask the gap. If the resolution requires changing the architecture, that is the impact-on-add `needs-architecture` path (an upstream SAD reopen), surfaced for the operator.
4. **Impact-on-add (new ADR during planning).** If planning surfaces an implementation decision worth an ADR, emit it with an `## Impact assessment` (Affected / Absorption / Rationale) -- scaffold `developer/templates/impact-assessment.md`. `absorbed` (a Tier-2 decision conforming to binding ADRs) -> record it and proceed; `needs-architecture` -> back-channel to the SAD.
5. **STOP at the gate.** Park D3 at `[?]` only when Q1-Q6 are all **yes** (or their resolutions are recorded). Do not begin D4 with an open Constitution Check.

## Output contract

- `specs/NNN-<slug>/plan.md` with the Constitution Check section: Q1-Q6 each `yes`/`no` + the resolving evidence (catalog/nfr/ADR ids).
- `scripts/fragment-checks/check_constitution.py` output verbatim + a 2-4 line summary (Q-verdicts, any back-channel request).

## Refusal conditions

| Trigger | Rule | Response |
|---|---|---|
| Any of Q1-Q4 answered No and unresolved | D-01 (non-waivable) | refuse to pass the gate; back-channel request |
| Q6 No (plan contradicts a binding ADR) | D-01 | refuse; conform or raise an ADR request |
| Operator asks to waive a non-waivable Q | D-01 | refuse; non-waivable means non-waivable |
| A plan service is invented to satisfy Q1 | D-01 / D-03 | refuse; catalog is the sole authority |

## References

- `shared/constitution.md`, `shared/glossary.md`
- `scripts/fragment-checks/check_entry.py` (A5 entry guard), `scripts/fragment-checks/check_constitution.py`, `scripts/fragment-checks/check_ids.py`, `scripts/fragment-checks/check_scope.py`
- Templates: `developer/templates/back-channel-request.md`, `developer/templates/impact-assessment.md`
- SAD `sdd-interface/standard/rdag-standard.md` §6 (Q1-Q6), §4 (Architecture Supremacy), `sdd-interface/examples/ev-charging/arch-1.0.0/integration/plan-template-constitution-check.md`
