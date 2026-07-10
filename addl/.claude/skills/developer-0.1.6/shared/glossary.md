---
title: Glossary -- Developer meta-skill
version: 0.1.1
date: 2026-06-27
---

# Developer glossary

Vocabulary used across the Developer gate sub-skills and the auditor. Terms from
the SAD/RDAG side are defined as the Developer consumes them, not re-derived.

- **Landed release** -- the immutable `architecture/arch-X.Y.Z/` directory (+ the
  consumer's `.specify/memory/constitution.md`) that the SAD's S8b step wrote into
  the consumer workspace. The Developer's binding input; never edited here.
- **Handoff manifest** -- `architecture/arch-X.Y.Z/handoff-manifest.md`: the
  release stamp, the Ri attestation (`Passing`), and the landing map. The entry
  point for intake (D1).
- **RDAG** -- the Residue-Driven Architecture Governance standard (SAD skill
  `sdd-interface/standard/`): the conformance checks (CHK-NN), the ID scheme, and
  the Constitution Check that govern this handoff.
- **Constitution Check (Q1-Q6)** -- the six questions every plan must answer at D3,
  wired into spec-kit's plan template by the landed
  `plan-template-constitution-check.md`. Q1-Q4 non-waivable (catalog, naming,
  call-chain, structural-stressor lineage); Q5-Q6 non-waivable (NFR coupling,
  binding ADRs). The runtime expression of D-01.
- **Service catalog** -- `system-design/service-catalog.md`: the closed set of
  services a spec/plan may reference, each with a category suffix
  (`*Manager`/`*Engine`/`*Access`) and a `Stressors-absorbed` field listing its
  Structural `S-NN`.
- **Architectural Context** -- the three-section block in a `uc-NNN-*.md`
  (Call Chain, Services touched, Residue). D2 must preserve it **verbatim** in the
  feature `spec.md`; `check_arch_context.py` verifies the preservation.
- **Binding ADR** -- a decision in `decisions/ADR-*.md` marked `Binding: Yes`. The
  implementation's runtime/protocol/middleware must conform (Q6); it is never
  substituted (Architecture Supremacy).
- **FLOW phase (Phase A)** -- the Developer-owned phase before a workflow runs:
  the constitution gate (approved) + UC selection. The only phase where a UC or ADR
  may be added, and the only phase tracked in `FLOW.md`.
- **Workflow phase (Phase B)** -- spec-kit's deterministic pipeline
  (`/speckit-specify` -> `/speckit-plan` -> `/speckit-tasks` -> `/speckit-implement`)
  for the selected UC. spec-kit owns the gates; the Developer provides deterministic
  movement (`gate_driver.py`) + evaluation/analysis/audit and reads state directly
  from the source artifacts (never a mirror in `FLOW.md`).
- **Entry point** -- selecting a UC and saying "implement with spec-kit"; it seeds
  `/speckit-specify` and starts the workflow, freezing the FLOW phase.
- **Architecture half / implementation half** -- the constitution's two halves with
  two owners. The **architecture half** (the principle + binding rules) is filled by
  the **handoff** (the Architect), landed verbatim; the Developer never edits it
  (changing it is an upstream re-land of a new `arch-X.Y.Z`). The **implementation
  half** is the **Developer's** (`[TODO]` principles: language/runtime, testing, API,
  observability, persistence, security). At the Phase A approval gate the Developer
  adds ONLY implementation-half content; `check_principle.py` guards that the
  architecture half is untouched (CHK-01).
- **Constitution gate** -- the FLOW-phase requirement that the constitution
  (architecture half landed verbatim + implementation half filled by the Developer,
  CHK-01 clause-level, Q1-Q6 override spliced in) is **APPROVED** -- once the
  implementation half is filled and contradicts nothing in the architecture half --
  before any spec may be implemented. Closes the hook of the SAD/Architect handoff.
- **Constitution drift** -- a constitution change during a running workflow; the one
  in-workflow reopen trigger (impact-assess the generated artifacts, regenerate the
  impacted step(s)). Adding a UC/ADR is never an in-workflow reopen.
- **Absorbed** -- a new ADR/UC added in the FLOW phase (Phase A) that fits the landed
  catalog / residues / binding ADRs. Proceeds without an architecture reopen.
- **needs-architecture** -- a new ADR/UC that the landed release cannot absorb
  (a service not in the catalog, a contradiction of a binding ADR, a missing
  residue). Routes a back-channel request to the SAD; not forced through.
- **Back-channel request** -- the Developer's only legal response to a gap in the
  architecture: a *catalog amendment request* (new service), an *ADR request*
  (new binding decision), or a *residue-analysis request* (missing `S-NN`/`C-NN`
  lineage). Never an inline invention.
- **spec-kit skill** -- one of spec-kit's own production commands
  (`/speckit-specify`, `/speckit-clarify`, `/speckit-plan`, `/speckit-analyze`,
  `/speckit-tasks`, `/speckit-implement`). The Developer invokes these; it does not
  re-implement them.
- **Gate / fragment** -- a Developer gate is `D1..D5`; its tracked artifact is
  either the governance note `intake.md` (D1) or the spec-kit deliverable under
  `specs/NNN-<slug>/` (D2..D5). The tracker is `docs/developer/FLOW.md`.
- **Pin** -- the `arch-X.Y.Z` version a Developer build targets, recorded at D1.
  All ID resolution (D-03) is against the pinned release.
- **Orchestrator** -- the parent that drives the role: reads `FLOW.md` state, routes to
  the gate sub-skills, gates each transition for operator approval, and owns the **git
  acts** (cutting the feature worktree, committing each approved gate, the authorized
  integrate). It authors no artifact content. When wrapped by ADDL it is the wrapping
  runtime; running as a single LLM it is the same agent that also performs production.
- **Executor** -- the producer role (the `Developer` subagent, or the single LLM acting
  as one) that invokes the gate's spec-kit skill **inside the orchestrator's worktree**
  and parks the gate at `[?]`. It produces artifact content; it never mutates git (no
  branch, commit, merge, push, or PR) -- the orchestrator records what it produces.
- **Consumer repo** -- the git repository the Developer implements into. Must be its
  own git repo before D1 (spec-kit is branch-per-feature; the orchestrator cuts a
  worktree per feature).
- **Base branch** -- the branch the workspace is standing on (normally `main`/`master`).
  Every feature branch is cut from it; D5 integrates back into it. The orchestration
  plane (`docs/developer/`) lives here.
- **Feature worktree / branch (`NNN-<slug>`)** -- a git worktree on a fresh branch, cut
  by the orchestrator from the base for one feature; holds the deliverable plane
  (`specs/NNN-<slug>/` + `src/`/`tests/`) through D2-D5. Discarded on integrate or on a
  back-channel resolve.
- **Integrate** -- the authorized, terminal per-feature act after D5 approval: merge the
  feature branch into the base (PR via remote, or local `--no-ff` merge). Never auto;
  the operator authorizes it (mirror of SAD S8b land).
