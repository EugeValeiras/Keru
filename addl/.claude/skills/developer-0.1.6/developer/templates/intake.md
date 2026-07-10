---
title: Intake template -- D1 gate readiness note
version: 0.1.0
date: 2026-06-24
---

# D1 Intake -- <arch-X.Y.Z>

> Output template for the D1 (Phase A / FLOW) gate. The Developer writes the filled copy
> to `docs/developer/intake.md` in the consumer repo. D1 is governance only -- it produces
> no spec/plan/tasks/code; it makes the project ready to implement a UC through the two
> FLOW interaction points (the constitution gate + UC selection). Fill every field; leave
> a `[ ]` unchecked until its check passes. See `developer/intake/SKILL.md`.

## Release pin

- **Pin:** `arch-X.Y.Z` (the landed release every later gate resolves IDs against)
- **Ri attestation:** `Passing` | `<status>`  (from `handoff-manifest.md`; must be Passing)

## Conformance verdicts (deterministic -- paste the check output)

- [ ] **CHK-01 (clause-level principle):** `check_principle.py` -- architecture-half clauses byte-identical to the landed principle.
- [ ] **ID resolution (D-03):** `check_ids.py` -- every `UC/S/C/NFR/ADR`/service id resolves to the pin.
- [ ] **UC handoff form (CHK-10):** `check_uc_structure.py` -- every UC has Call Chain / Services touched / Residue, all touched services in the catalog.
- [ ] **Binding-ADR handoff form (CHK-12):** `check_adr_binding.py` -- every `Binding: Yes` ADR has a populated Conformance check and is enumerated in the manifest.
- [ ] **Q1-Q6 override installed + well-formed:** `check_override.py --build` then `--verify` -- the spliced gate keeps the stock plan-template sections AND carries Q1-Q6.

## Constitution gate (FLOW interaction point 1)

- **Implementation half filled:** `Yes` | `No`  (the Developer's `[TODO]` principles: language/runtime, testing, API conventions, observability, persistence, security)
- **No implementation principle contradicts the architecture half:** `Yes` | `No`  (Architecture Supremacy)
- [ ] **Constitution APPROVED** by the operator
- [ ] **Architecture half PINNED (A3):** `check_drift.py ... --pin .specify/memory/.arch-pin.json` (re-checked `--against` at every later gate; an architecture-half change blocks)

## UC selection (FLOW interaction point 2)

- **Available use cases:** `UC-001 <slug>`, `UC-002 <slug>`, ...
- **Selected target UC:** `UC-NNN <slug>`
- **Added this phase (the only phase where adds are allowed):**
  - New UC: `UC-NNN <slug>` | `none`
  - New implementation ADR: `ADR-NNN <slug>` | `none`
  - If anything was added, attach an `## Impact assessment` block (see `developer/templates/impact-assessment.md`).

## Summary (2-4 lines for the parent)

<What landed, what was approved, the selected UC, and the entry point: hand UC-NNN to
`/speckit-specify` to begin Phase B. Note any back-channel request raised.>
