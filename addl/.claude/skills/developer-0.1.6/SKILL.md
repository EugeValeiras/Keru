---
name: developer
version: 0.1.6
description: Use this skill to drive the implementation of a finished, Ri-passing Software Architecture Document (SAD) by orchestrating spec-kit (GitHub's spec-driven-development toolkit) under architecture governance. It is the Developer role of the ADDL lifecycle: it consumes the RDAG handoff that the SAD's S8b step landed (architecture/arch-X.Y.Z/ + .specify/memory/constitution.md) and walks a gated chain -- intake, specify, plan (Constitution Check), tasks, implement -- invoking spec-kit's own skills to PRODUCE each artifact while this skill REVIEWS and GATES them. Invoke when a landed architecture release is ready to implement. Do NOT use to design architecture (that is the SAD skill), to reverse-engineer a codebase (recon), or to author spec/plan/tasks/code content by hand (spec-kit owns that).
task_types:
  - implement-architecture
  - drive-spec-kit
  - spec-driven-development
  - constitution-check
  - gate-implementation
shared_refs:
  - shared/constitution.md
  - shared/glossary.md
---

# developer

**Version: 0.1.6** (2026-06-28). This is the single source of truth for the meta-skill version (it matches the git tag and the packaged bundle). The sub-skills do not carry their own version -- they are versioned as part of this meta-skill.

> **On invocation, state the version.** The first time this skill is activated in a session, announce `developer v0.1.6` so the operator can confirm which contract is in force.

The meta-skill that **implements** a finished architecture by orchestrating **spec-kit** under **architecture governance**. It is the Developer phase of the ADDL lifecycle -- the half that runs *after* the SAD is assembled (S1a-S7) and its handoff is emitted and landed (S8a/S8b).

This skill does **not** generate spec/plan/tasks/code content. **spec-kit and its own skills do.** This skill is the **interface + governance layer**: it tells the Developer which spec-kit skill to invoke at each gate, reviews what spec-kit produced, enforces the RDAG Constitution Check, and stops at each gate so the operator can approve. The division is deliberate and non-negotiable:

- **spec-kit produces** -- `spec.md`, `plan.md`, `tasks.md`, the implementation (`/speckit-specify`, `/speckit-clarify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-analyze`, `/speckit-implement`).
- **developer governs** -- which spec-kit skill runs per gate, the human-in-the-loop review, the Constitution Check (Q1-Q6), ID resolution against the landed release, and the impact-on-add rule for new ADRs/UCs.

We invoke and review; spec-kit implements. We leverage **every** spec-kit skill available to reach implementation -- we never re-derive its doctrine.

## The golden rule -- D-01 Architecture Supremacy

> **The landed architecture release is binding. Implementation conforms to it; it never silently overrides it.** Services, NFRs, and binding decisions come from the landed `architecture/arch-X.Y.Z/`. The Developer NEVER invents a service, an NFR, or a binding decision inline. When the plan needs something the architecture does not provide, the Developer raises a **back-channel request** (catalog amendment / ADR request / residue-analysis request) -- it does not decide unilaterally.

This is the Developer's analogue of recon's RE-01 (anchor to code) and the SAD's residue discipline. It is enforced at D3 by the **Constitution Check (Q1-Q6)**. See `shared/constitution.md` for the full rule set (D-01..D-03).

## Input -- what the Developer consumes

The Developer reads the **RDAG handoff** that S8b landed in the consumer workspace (see the SAD skill `sdd-interface/standard/`). It is an **immutable, versioned** release:

```
architecture/arch-X.Y.Z/
  handoff-manifest.md                # entry point: release stamp, Ri attestation (Passing), landing map
  system-design/
    service-catalog.md               # services + category (*Manager/*Engine/*Access), Stressors-absorbed (S-NN), call rules
    nfr-register.md                   # NFRs, Source coupling (C-NN) inline, Applies-to scope
  use-cases/
    uc-NNN-<slug>.md                  # Architectural Context block: Call Chain + Services touched + Residue
  decisions/
    ADR-NNN.md                        # binding runtime/protocol/middleware decisions
  integration/
    principle-decomposition-by-residue.md   # the agnostic principle landed into the constitution
    plan-template-constitution-check.md      # the Q1-Q6 gate wiring
    sync-impact-report.md                    # (insert/replace mode) reconciliations table
.specify/memory/constitution.md       # the landed constitution (CHK-01: principle byte-identical)
```

**Global IDs are append-only -- never renumber, never reuse** (`rdag-id-scheme.md`): `UC-NNN`, `S-NN` (stressor), `C-NN` (coupling), `NFR-NN`, `ADR-NNN`, `U-NN` (unstressed surface), plus service names (`*Manager`/`*Engine`/`*Access`). A spec or plan built against `arch-1.0.0` stays valid when `arch-2.0.0` ships.

## The two-phase cycle -- FLOW (ours) <-> workflow (spec-kit's)

The Developer is a loop of two deterministic phases that do **not** replace each other; the status panel shows both (the canonical tracker is `FLOW.md`).

- **Phase A -- FLOW (ours).** The only phase where governance state is tracked and where a UC or ADR may be added. It prepares a spec through **two interaction points**: (1) the **constitution gate** -- the SAD/Architect handoff principle, completed via `/speckit-constitution`, CHK-01 byte-identical, Q1-Q6 wired, and **APPROVED by the operator** before any spec may be implemented; and (2) **UC selection** -- pick the target `UC-NNN`, adding it (or an implementation ADR) here if needed. Selecting a UC and saying "implement with spec-kit" is the **entry point**: it seeds `/speckit-specify` and the workflow starts; FLOW then freezes.
- **Phase B -- workflow (spec-kit's).** spec-kit owns the deterministic gates (`/speckit-specify` -> `/speckit-plan` -> `/speckit-tasks` -> `/speckit-implement`). We do **not** run a parallel gate machine and do **not** mirror its state: the workflow's state IS the source artifacts (`specs/NNN-slug/spec.md|plan.md|tasks.md` + code), read directly via `gate_driver.py`. Our only jobs here are deterministic movement (the driver) and evaluation/analysis/audit that invoke spec-kit's own skills (`/speckit-analyze`) plus our `check_*.py`. **No UC/ADR is added during Phase B.**

When the workflow completes (feature implemented, tests green, conformance holds), control returns to Phase A for the next UC. The gate ids below name the steps: **D1 is Phase A**; **D2..D5 are the Phase B steps** we interface with and display.

## The five sequential sub-skills + auditor (the D1..D5 gate chain)

> Heading shape mirrors `sad-*` / `recon-*` so an orchestrator (ADDL) parses this gate
> table generically (`## The N sequential sub-skills`, columns located by header name).
> The cross-cutting `developer-auditor` can run at any gate or end-to-end.

| Gate | Sub-skill | spec-kit skill invoked | Produces (spec-kit owns content) | Pre-conditions |
|---|---|---|---|---|
| **D1** | `intake` | `/speckit-constitution` (completes the constitution) | `intake.md` -- readiness note: handoff landed + RDAG-conformant, constitution completed (CHK-01) + **APPROVED**, Q1-Q6 wiring installed, release pin, target `UC-NNN` selected (UC/ADR adds happen here) | A landed `architecture/arch-X.Y.Z/` exists |
| **D2** | `specify` | `/speckit-specify` (+ `/speckit-clarify`) | `specs/NNN-<slug>/spec.md` for one feature, seeded from a `UC-NNN`; preserves the UC's **Architectural Context verbatim** | D1 approved; a target `UC-NNN` named |
| **D3** | `plan` | `/speckit-plan` | `specs/NNN-<slug>/plan.md` (+ research/data-model/contracts/quickstart); the **Constitution Check Q1-Q6** runs (wired by the landed plan-template) | D2 approved |
| **D4** | `tasks` | `/speckit-tasks` | `specs/NNN-<slug>/tasks.md` -- ordered, TDD-first, each task traced to spec/plan | D3 approved (Q1-Q6 all yes) |
| **D5** | `implement` | `/speckit-implement` (run `/speckit-analyze` first) | code + tests in the consumer repo; verifies tests green + Constitution conformance holds | D4 approved |

## Invoking spec-kit -- the verified contract

The spec-kit surface is pinned by analysis, not assumption. Always install/init spec-kit from the upstream git repo (`git+https://github.com/github/spec-kit.git`) -- local packages go stale. Specifics the orchestrator MUST honor:

- **Invocation names use a hyphen** (`/speckit-plan`), the Claude-skill name; the dot form (`speckit.plan`) is only the workflow-engine id, never used to invoke.
- **`/speckit-clarify`** is optional and runs at D2 **before** `/speckit-plan` (only if the spec carries `[NEEDS CLARIFICATION]`).
- **`/speckit-analyze`** is read-only and runs at the **D4->D5 boundary** -- after `tasks.md` exists, before `/speckit-implement` -- NOT at D3.
- **Tests are OPTIONAL in `/speckit-tasks` by default.** D-02 requires the Developer to explicitly direct it toward a TDD-first task list; otherwise `tasks.md` ships without tests and D5 cannot pass honestly.
- **Branch-per-feature is ORCHESTRATED, not self-driven.** spec-kit is branch-per-feature, but the **orchestrator owns the git**: before D2 it cuts a git **worktree** on a fresh `NNN-<slug>` branch from the clean **base** branch, and the executor runs `/speckit-specify` **inside that worktree** with `SPECIFY_FEATURE_DIRECTORY=specs/NNN-<slug>` set so spec-kit creates `specs/NNN-<slug>/` matching the branch. **Do NOT `git checkout -b`, switch, merge, push, or open a PR yourself** -- the orchestrator owns every branch mutation; you only fill the worktree spec-kit's skills produce. The `/speckit-specify` **command** names the spec dir itself (honoring `SPECIFY_FEATURE_DIRECTORY` as the explicit override) and writes `.specify/feature.json` for downstream gates; it does **not** take `--short-name`, a flag of the `create-new-feature.sh` *script* the command does not drive. D3-D5 then resolve the active feature via `SPECIFY_FEATURE` / `.specify/feature.json`. The Developer's `docs/developer/` workshop is parallel to (not a replacement for) spec-kit's `specs/` and feature branch. See **the Consumer-repo git lifecycle section** below for the full contract.

**Routing is deterministic, not a judgement call.** Do not decide the next call by eye. Run the deterministic gate driver and obey what it returns:

```
scripts/fragment-checks/gate_driver.py <workspace> --feature <NNN-slug> [--json]
```

It resolves the workspace state, reports the current gate, emits the exact next `/speckit-*` call with its preconditions and governance directives (e.g. the D-02 TDD directive at D4), names the deterministic checks to run at that gate, and blocks (exit 1) when a precondition is unmet. The LLM's only non-deterministic act is performing the one generative spec-kit invocation the driver names.

**Constitution Check Q1-Q6** (the governance heart, runs at D3 against the landed release; **Q1-Q4 NON-WAIVABLE**, Q5-Q6 NON-WAIVABLE per RDAG):

1. **Q1** -- every service in `plan.md` is present in `service-catalog.md` at the pinned release. (No -> catalog amendment request.)
2. **Q2** -- each service name carries the category suffix (`*Manager`/`*Engine`/`*Access`).
3. **Q3** -- the call chain respects layer rules (no Manager->Manager sync, no Client->ResourceAccess, no Engine->Manager).
4. **Q4** -- each service lists ≥1 Structural `S-NN` in Stressors-absorbed.
5. **Q5** -- each NFR records a `C-NN` (coupling/topology) in its Source.
6. **Q6** -- the plan's runtime/protocol/middleware conforms to all binding ADRs.

A "No" routes to a **back-channel request**, never an inline fix (D-01 Architecture Supremacy).

## Adds and reopens -- what is allowed, and when

**Adding a UC or ADR is a Phase A activity only.** Before a workflow starts, the Developer may add a UC (a feature to implement that the landed use-cases do not yet cover) or an implementation-level ADR. Every add runs an **impact assessment against the landed architecture**:

- **Absorbed** (fits the existing catalog / residues / binding ADRs) -> proceed. The UC becomes a target to implement; the ADR is a Tier-2 (implementation) decision that conforms. **No architecture reopen.**
- **Not absorbed** (needs a service absent from the catalog, contradicts a binding ADR, or implies a new residue) -> an **architecture concern**: raise a catalog-amendment / ADR / residue request back to the SAD (an upstream reopen). The Developer does not force it through.

The `## Impact assessment` block has three fields -- `Affected:` (catalog services / NFRs / binding ADRs touched), `Absorption:` one of `absorbed` | `needs-architecture`, `Rationale:` (1-3 sentences). **During Phase B (a running workflow) no UC/ADR is added** -- a gap discovered mid-implementation is surfaced, the workflow stops, and the add is handled back in Phase A (or escalated upstream).

**Constitution drift is the one in-workflow reopen.** If the constitution is changed while a workflow is executing, it can invalidate artifacts spec-kit already produced. Run an impact assessment against the generated `spec.md` / `plan.md` / `tasks.md` / code (`/speckit-analyze` flags constitution conflicts as CRITICAL; `check_constitution.py` re-checks the plan); **reopen and regenerate** the impacted step(s) so the artifacts match the changed constitution before continuing. Adding a UC/ADR is never an in-workflow reopen -- only constitution drift is.

## Orchestration -- read state, route, delegate, gate

The router is an **orchestrator**, not a lookup table. On every invocation:

1. **Read state first (do not route blind).** Resolve the tracker `docs/developer/FLOW.md`. Bootstrap case: it does not exist -> create `docs/developer/` and initialize the tracker with D1..D5 `[ ]`. Existing case: read which gates are in which states. **Disk wins:** a gate marked `[?]`/`[x]`/`[i]` whose named artifact is absent on disk degrades to `[ ]`.
2. **Report position** before routing (e.g. "D1 approved, D2 awaiting review for uc-001").
3. **Route, confirm against state.** Map the request to a sub-skill; verify the prior gate is `[x]` approved before producing.
4. **Delegate with the handoff contract.** Pass the landed release path, the target `UC-NNN`, and the prior approved artifacts. The carry-forward is the **why**: the service<->`S-NN` lineage and the binding ADRs that constrain this feature (R-22: the architecture's lateral reasoning must survive into implementation).
5. **On completion: review, present, close the gate.** The Developer-Auditor (or the operator) reviews; the gate moves to `[x]` only on operator approval.
6. **Backtracking.** A reopen sets the gate to `[ ]`, cascades downstream within the Developer chain (D2 reopen resets D3,D4,D5 for that feature), moves the cursor back, and preserves the prior artifact as `Dn.iter-N.md`. A reopen that crosses *back into architecture* is the impact-on-add `needs-architecture` path, not a Developer reopen.

## Gate state machine (canonical)

| FROM | TO | Owner | Trigger | Side-effects |
|---|---|---|---|---|
| `[ ]` | `[~]` | **executor** | sub-skill starts (invokes the spec-kit skill) | mark in_progress |
| `[~]` | `[?]` | **executor** | spec-kit artifact produced + parked | await review |
| `[?]` | `[x]` | **orchestrator** | operator approves | stamp date; advance cursor |
| `[?]`/`[~]` | `[i]` | **orchestrator** | request changes | hold; executor re-invokes spec-kit |
| `[i]` | `[~]` | **executor** | re-entering | mark in_progress |
| `[x]` | `[ ]` | **orchestrator** | reopen | cascade downstream; move cursor back |

States: `[ ]` pending / `[~]` in progress / `[?]` awaiting review / `[x]` approved / `[!]` blocked / `[i]` iterating. The executor never re-mutates a transition the orchestrator already did. Producer transitions (`[ ]`->`[~]`, `[~]`->`[?]`) stay the executor's even after a reopen.

## Subagent orchestration

When wrapped by ADDL (or any multi-agent runtime), the parent is the **orchestrator**, the production work goes to subagents named by role so they never collide with other lifecycle phases:

- **`Developer`** -- drives one gate: invokes the gate's spec-kit skill, reviews the output against this skill's contract, parks the gate at `[?]`. Invoked with `subagent_type: Developer` when the templates in `agents/` are installed into `.claude/agents/`; fallback to `general-purpose` + the role as a `description` prefix otherwise.
- **`Developer-Auditor`** -- runs the `developer-auditor` sub-skill (by-gate / end-to-end / diff-drift), validating Q1-Q6, ID resolution, spec<->plan<->tasks<->code consistency, and Architectural-Context preservation. Same binding.

The parent authors **no** artifact content: in the workshop it writes **only** `FLOW.md` mutations and, on reopen, the rename of the prior artifact to `Dn.iter-N.md`. Everything else -- the spec/plan/tasks/code (spec-kit) and the audit report (Developer-Auditor) -- a subagent or spec-kit writes. The parent does NOT write artifact content directly. **Git acts are the orchestrator's, separate from content authorship:** cutting the feature worktree, committing each approved gate's artifact, and the authorized D5 integrate are recording/placement acts the parent performs (see the Consumer-repo git lifecycle section below) -- never content the executor produces.

## Running as a single LLM

With no UI / multi-agent tool, the router, the Developer, the Developer-Auditor, and spec-kit's skills are all driven by one LLM reading state, routing, invoking the spec-kit skill for the gate, stopping at the gate, and auditing. The canonical gate machine and the Constitution Check still apply.

## Per-project workspace convention

One role per lifecycle phase, each owning `docs/<role>/`. The Developer's workshop is **`docs/developer/`**:

```
<consumer-root>/docs/developer/
  FLOW.md                    # the D1..D5 gate tracker
  intake.md                  # D1
  Dn.iter-N.md               # archived iterations after a reopen
  audit-iter-N.md            # Developer-Auditor reports
```

The **deliverables spec-kit produces** live where spec-kit puts them -- `specs/NNN-<slug>/` (spec/plan/tasks) and the consumer's source tree (code) -- NOT under `docs/developer/`. The Developer reads `architecture/arch-X.Y.Z/` + `.specify/` (the landed handoff) but **never edits** them; they are the binding input.

## Consumer-repo git lifecycle

The orchestrator owns the git plane so features stay isolated and the base stays
clean. The two planes split (this is a **rule**, not just a layout):

- **Orchestration plane** -- `docs/developer/` (FLOW.md tracker, intake.md, audits,
  back-channel requests, iteration archives) -- lives on the **base** branch.
- **Deliverable plane** -- spec-kit's `specs/NNN-<slug>/` + the `src/`/`tests/` code --
  lives in the **feature worktree** on the `NNN-<slug>` branch.

Lifecycle, per feature:

1. **Cut (at D2 entry).** The orchestrator cuts a worktree on a fresh `NNN-<slug>`
   branch from the clean base. The executor runs `/speckit-specify` **inside** that
   worktree with `SPECIFY_FEATURE_DIRECTORY=specs/NNN-<slug>` set (the lever the
   command honors to pin the spec dir to the branch; the command writes
   `.specify/feature.json` for downstream resolution) and never creates or switches
   the branch. Cutting from the base (never from the prior feature's HEAD) is what
   keeps features from stacking.
2. **Commit (at each gate approval; D5 per increment).** The orchestrator commits
   the just-approved artifact deterministically: **D1 governance** (constitution +
   arch-pin + intake) to the **base**; **D2-D4 deliverables** (spec / plan / tasks)
   to the **feature branch**, one commit per approved gate. **D5** (code+tests)
   commits **once per reviewed increment** to the feature branch -- many commits land
   across D5 as the operator reviews each orchestrator-named task range, the last when
   every task is `[X]` and D5 is fully approved. The executor does not commit; it
   produces, the orchestrator records.
3. **Integrate (terminal, AUTHORIZED).** Approving **D5 does NOT auto-integrate.** The
   feature lives on its branch until the **operator explicitly authorizes** Integrate
   -- with a remote: push + open a PR against the base (review/CI gate the merge);
   without one: a local `--no-ff` merge into the base. This is an outward act and
   mirrors the SAD `S8a -> S8b` "**land = explicit authorized trigger, never auto**"
   rule: the executor must **not** merge, push, or open a PR on its own. After
   integration the active feature is cleared and the flow returns to Phase A; the
   next UC cuts a fresh worktree from the advanced base.
4. **Back-channel = branch-isolated exploration.** A new-UC impact-on-add that returns
   `needs-architecture` STOPs with no spec (D-01): the partial exploration sits in its
   worktree (isolated from the base), and the back-channel request is raised. Its only
   resolution is an **upstream re-land** (a new `arch-X.Y.Z`); the abandoned branch is
   discarded on resolve and the feature is **regenerated fresh** as `absorbed` against
   the re-landed architecture (never rebased). The Developer never invents the missing
   architecture to "unblock" the branch.

Multi-developer: each developer runs the role against their own clone; features are
independent branches off the shared base, integrated via PRs. The Developer gates
governance and owns the producer transitions; the orchestrator owns the git acts.

## When NOT to invoke

- No landed architecture release (`architecture/arch-X.Y.Z/` absent) -- there is nothing binding to implement against; run the SAD + S8a/S8b first.
- To design or change the architecture -- that is the SAD skill (reopen S1a-S7).
- To author spec/plan/tasks/code content by hand -- that is spec-kit's job; this skill orchestrates it.
- To reverse-engineer an existing codebase -- that is recon.

## References

- `shared/constitution.md` -- rules D-01..D-03.
- `shared/glossary.md` -- vocabulary (handoff, residue, Constitution Check, absorbed, back-channel request).
- `developer/intake/`, `developer/specify/`, `developer/plan/`, `developer/tasks/`, `developer/implement/` -- the five gate sub-skills.
- `developer/developer-auditor/` -- the cross-cutting auditor.
- `agents/Developer.md`, `agents/Developer-Auditor.md` -- the subagent templates ADDL installs.
- `scripts/fragment-checks/check_constitution.py`, `scripts/fragment-checks/check_ids.py`, `scripts/fragment-checks/check_arch_context.py` -- deterministic checks.
- The SAD skill `sdd-interface/standard/` (rdag-standard, rdag-conformance, rdag-id-scheme) -- the input contract this skill consumes.
