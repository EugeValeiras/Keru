---
name: sad
version: 1.17.17
description: Use this skill to design or document software architecture as a Software Architecture Document (SAD) synthesizing Juval Lowy's IDesign (volatility-based decomposition) with Barry M O'Reilly's Residuality Theory (stress-driven decomposition). Produces a single integrated SAD per project via a chain of seven sequential sub-skills plus one cross-cutting auditor. Invoke when starting a new architecture from a PRD/SRD, refactoring an existing one for criticality, or running an architectural audit. Routes to the appropriate sub-skill based on the request.
task_types:
  - design-software-architecture
  - produce-sad
  - architecture-design
  - stress-architecture
  - audit-architecture
  - validate-architecture
  - residual-design
  - sad
shared_refs:
  - shared/constitution.md
  - shared/architectural-walking.md
  - shared/glossary.md
  - shared/idesign-vocabulary.md
  - shared/decomposition-discipline.md
  - shared/stressor-frameworks.md
  - shared/kauffman-nkp.md
  - shared/style-conventions.md
  - sad/synthesis-explanation.md
  - sad/template.md
  - sad/adr-template.md
---

# sad

**Version: 1.17.17** (2026-07-01). This is the single source of truth for the meta-skill version (it matches the git tag and the packaged bundle). The sub-skills do not carry their own version -- they are versioned as part of this meta-skill.

> **On invocation, state the version.** The first time this skill is activated in a session, announce: `sad v1.17.17`. This lets the operator confirm which version is running before any SAD work begins.

The meta-skill that produces a Software Architecture Document (SAD). One project produces one SAD via a chain of seven sequential sub-skills and one cross-cutting auditor. The synthesis fuses two methods that cover each other's blind spots: Juval Lowy's IDesign provides the **vocabulary** (Manager / Engine / ResourceAccess / Resource / Utility / Client, closed architecture, atomic business verbs); Barry M O'Reilly's Residuality Theory provides the **method** (stressor analysis, contagion matrix, criticality goal, empirical Ri test).

Before invoking any sub-skill, read `shared/architectural-walking.md` -- the lateral cognitive mode mandated by R-22 is required for the workflows to produce criticality rather than checklist output. The synthesis decisions, normative template, and worked examples live in this directory.

---

## Required mindset (R-22)

The architect operates in **lateral mode**, not linear. Per `shared/architectural-walking.md` §4 and constitution R-22: ask "what could break this structure?", not "what is the correct structure?". Treat refusal conditions as reflective gates, not checklists. Defended abstractions are stressors-in-disguise. "Architecture is the practice of being consistently wrong until you reach a point of being a little bit less wrong" (O'Reilly L1450-1452).

The auditor cannot mechanically check mode; the auditor checks the SHAPE of output. Linear-mode execution produces thin output that passes hygiene but fails the empirical Ri test (S6).

---

## The seven sequential sub-skills + auditor

Each sub-skill produces a fragment for user review and approval. After all six prior fragments are approved, the assembler (S7) integrates them into the final `sad.md`. The cross-cutting auditor (`sad-auditor`) can run at any gate or end-to-end.

**Gates are per fragment, not per sub-skill** (one fragment = one gate = one approval). All sub-skills produce a single fragment except S1, which produces two (`business-view.md` then `naive-architecture.md`) and therefore has two gates, **S1a** and **S1b**, with a human checkpoint between them. The executor never emits two fragments in one turn.

| # | Sub-skill | Produces (SAD section) | Pre-conditions |
|---|---|---|---|
| S1a | `business-discovery` | Business View | None (entry skill) |
| S1b | `business-discovery` | Naïve Architecture | S1a (Business View) approved |
| S2 | `flow-analysis` | Flow Analysis | Naïve Architecture exists |
| S3 | `stressor-analysis` | Stressor Catalog (typed Structural / Topological / Business / Combined) | Flow Analysis exists |
| S4 | `contagion-analysis` | Contagion Matrix + NKP Totals + Hyperliminal Coupling Map + Topological Residue Map + Business Residues Log + Looping Signals | Stressor Catalog has at least one Structural residue |
| S5 | `residual-design` | Derived NFRs + Static Architecture (IDesign) + Use Cases with Residue Mapping + C4 model as one Structurizr DSL workspace (System Context + Container + per-Container Component + Deployment views) | Contagion analysis complete |
| S6 | `empirical-test` | Empirical Test (Ri) + Unstressed Surfaces | Residual design complete; fresh test stressor list available |
| S7 | `sad-assembler` | Final integrated `sad.md` | All six prior fragments approved |
| -- | `sad-auditor` (cross-cutting) | `audit-iter-N.md` -- violations, traceability gaps, fix proposals | At least one fragment exists |
| S8a | `speckit-handoff` -- **emit** (downstream) | The RDAG handoff staged at `handoff/arch-X.Y.Z/` (7 artifact types + manifest + constitution scaffold + plan-template wiring + Sync Impact Report). **Never touches the consumer.** | S7 assembled AND S6 Ri passing |
| S8b | `speckit-handoff` -- **land** (gated) | The staged release **landed** into the consumer (`architecture/arch-X.Y.Z/` + `.specify/memory/constitution.md` scaffold + `plan-template-constitution-check.md` wiring) + CHK-01 diff at landing. | S8a `[x]` approved AND explicit operator authorization |

The sub-skills live as directories under `sad/` -- each has its own `SKILL.md` with workflow, output contract, refusal conditions, references.

**S8 is downstream, not sequential.** It is invoked only after the SAD is assembled and Ri-passing, to translate the finished architecture into the artifacts a spec-kit project consumes (per `sdd-interface/standard/` + `sdd-interface/contracts/`). It does not do architecture; it transcribes it. It emits files to a staging directory and never edits the consumer repository -- applying them (especially the constitution principle) is a separate, gated integration step. See `sad/speckit-handoff/SKILL.md`.

### Gate approval protocol

The sub-skills are sequential and each consumes the prior fragment. Approval between gates is **enforced, not assumed**:

1. The project workspace has a **gate tracker** (the table in `FLOW.md` §Current session), one row per gate -- **S1a, S1b, S2-S7** (gates are per fragment) -- each `[ ]` pending until the user signs off.
2. **Before producing any fragment, the sub-skill verifies its prior gate is `[x] approved` in the gate tracker** -- not merely that the prior fragment file exists. A file can exist while still `[?] awaiting review` or `[i] iterating`; producing the next fragment on top of an unapproved one is the premature-advance error.
3. If the prior gate is not `[x] approved`, the sub-skill refuses and points the user to the open gate. (S1 has no prior gate; it is the entry.)
4. On user sign-off, mark the gate `[x] approved` with the date in the tracker table, **then run the bundled `scripts/fragment-checks/reconcile_flow.py <FLOW.md> --fix`** so the Mermaid `Sn` and gate `Gn` nodes are re-derived from the table in the **same** step. The table is authoritative and the script never edits it; it only rewrites the diagram nodes (label mark + `:::class`) to match. This makes the transition atomic and kills the recurrent table-updated-but-diagram-stale drift (feedback F-01) that otherwise needs manual reconciliation every gate. Then advance.

This makes "we are still on step N" a checked precondition rather than a thing the user has to catch. Each sub-skill's `Pre-conditions` references this protocol.

### Recommended auditor cadence

The `sad-auditor` is most valuable when run proactively, not only when the user remembers to ask. Recommended cadence:

- **`by-fragment` at every gate**, before the user approves a fragment -- the cheap, routine check.
- **`by-fragment` at the close of S5** specifically: S5 produces the most structure (taxonomy + call rules + C4 + deployment + Service Grouping Map) and is where level-mixing, hot-Manager, and grouping errors surface.
- **`by-fragment` (or `diff`) immediately after any structural change is applied** -- a Manager split, a rename, a merge. The structural-consistency checks (`sad-auditor` §2.7) catch incomplete ripple in one pass instead of across iterations. Do not advance to the next gate with an un-audited structural change.
- **`end-to-end` after S7** assembly, before shipping.

In a real run, the most impactful findings (a hot-Manager split, an incomplete ripple, a C4 level-mixing) tend to come from audits, not from the linear flow. Running the auditor on this cadence converts those from late surprises into gate-time corrections.

---

## Orchestration -- routing, state, and handoff

The router is an **orchestrator**, not a lookup table. It reads state, reports position, routes, delegates with an explicit handoff, closes each gate, and rewinds the cursor when an upstream gate reopens. This protocol is **runtime-agnostic**: it describes how a single LLM navigates the sub-skills today, and it is the same contract a multi-agent runtime would use (see §Running as agents). On every invocation:

### Step 1 -- Read state first (do not route blind)

Before routing, read the **gate tracker** (`FLOW.md` §Current session). Two cases:
- **No workspace / tracker yet and the request is a new SAD** -> bootstrap: create the Architect's workshop folder (`<root>/docs/architect/`) and the deliverable folder (`<root>/docs/sad/`), copy the bundled `FLOW.md` template into `docs/architect/`, initialize the gate tracker with **S1a, S1b, S2-S7** all `[ ]` (gates are per fragment). Then route to S1. (The `FLOW.md` tracker, the `S1a-S6` working fragments, and the audit reports live in `docs/architect/`; only the assembled `sad.md`, `use-cases/`, and `arch-X.Y.Z/` releases that the stakeholder consumes live in `docs/sad/`.)
- **Tracker exists** -> read which gates are `[x] approved`, `[?] awaiting review`, `[i] iterating`, `[!] blocked`.

**Artifact existence is verified, not asserted by the log.** Extend "Gate Approval Is Enforced State" -- for every gate the tracker reports as `[?]` / `[x]` / `[i]`, the router MUST check that the gate's named artifact(s) exist on disk before reporting position. A gate whose artifact files are absent is **automatically degraded to `[ ]`** (with a note in the report: "tracker said `[?]` but `<file>` not on disk -- degraded to pending"). The tracker is a working note, not the source of truth -- disk is. This catches a Log that claims emission without files.

**Mermaid diagram is reconciled from the table, deterministically.** As the first action of the turn, run the bundled `scripts/fragment-checks/reconcile_flow.py <FLOW.md> --fix`. The Gate tracker **table** is authoritative; the script re-derives every Mermaid `Sn`/`Gn` node from it and rewrites only the diagram (never the table). This self-heals any drift left by an out-of-band, table-only mutation (UI/orchestrator that touched the row but not the diagram -- feedback F-01 Target B). It is orthogonal to R-26: R-26 is a property of the **table** (which the script never edits), so reconciling the diagram cannot mask a real tracker inconsistency.

**Tracker coherence is verified, not assumed (R-26 -- NON-NEGOTIABLE).** Walk the gate tracker top-down and verify the three R-26 invariants:

1. **Contiguous approval chain.** Every `[x]` has every prior gate `[x]`.
2. **Active gates require approved priors.** Every `[~]` / `[?]` / `[i]` has every prior gate `[x]` -- active work cannot float above an unapproved prior.
3. **Single active gate.** AT MOST ONE gate is in `[~]` / `[?]` / `[i]` at any time -- only the first gate after the last `[x]` may be active. Everything further downstream is `[ ]` (or `[!]`).

Any violation is a **tracker inconsistency** -- report it next to position ("Gates approved: S1a, S2; inconsistency: S2 `[x]` while prior S1b is `[?]`" / "two active gates: S1b `[?]` and S3 `[?]`") and **refuse to route** until the operator resolves it (revert the offending gate to `[ ]`, or approve every missing prior). The Gate Approval Protocol checks approval **at producer time**; R-26 checks tracker coherence **at every read**. Both refusals exist precisely because an out-of-band actor (UI bug, manual edit, buggy orchestrator, fixture) can mutate the tracker into an incoherent state without ever invoking the executor. The single-active-gate rule (invariant 3) is what keeps the workflow single-threaded -- only one decision pending at a time. No `--force`.

### Step 2 -- Report position

State it back before acting: e.g. "Gates approved: S1a, S1b, S2. Current: S3 awaiting. Next: stressor-analysis." This makes "where are we" explicit instead of inferred -- the operator can correct a wrong read before any fragment is produced.

### Step 3 -- Route, and confirm against state

Map the request to a sub-skill, then **check it against the tracker**:

| User says | Routes to |
|---|---|
| "Design the architecture for X / produce a SAD for Y" | Start at S1 `business-discovery` |
| "We already have the business view; let's map the flows" | S2 `flow-analysis` |
| "Stress my architecture / generate stressors / find what could break this" | S3 `stressor-analysis` |
| "Build the contagion matrix / find hyperliminal couplings" | S4 `contagion-analysis` |
| "Express the residual architecture in IDesign terms / derive NFRs / produce C4 diagrams" | S5 `residual-design` |
| "Run the empirical test / compute Ri / find unstressed surfaces" | S6 `empirical-test` |
| "Assemble the SAD / integrate the fragments / publish" | S7 `sad-assembler` |
| "Audit this SAD / check the architecture against the rules / validate a fragment" | `sad-auditor` |
| "Hand off / emit the spec-kit artifacts / stage the RDAG handoff" | **S8a** `speckit-handoff` -- emit (only after S7 assembled + S6 Ri passing). Writes to `handoff/arch-X.Y.Z/` only. |
| "Land the handoff / apply it to the consumer / integrate" | **S8b** `speckit-handoff` -- land (only after S8a `[x]` + explicit operator authorization). Writes the consumer's `architecture/` + `.specify/`. |

If the requested sub-skill's **prior gate is not `[x] approved`**, do NOT delegate -- surface the gap ("S3 needs S2 approved; S2 is still awaiting review") and let the operator approve or redirect. This is the router-side complement to each sub-skill's own gate pre-condition (Gate approval protocol).

### Step 4 -- Delegate with the handoff contract

Hand the sub-skill exactly what its **Handoff contract** declares it consumes (each sub-skill `SKILL.md` has a `## Handoff contract` section: Consumes / Produces / Lateral context). Pass not only the prior fragment but the **lateral context** -- the "why" behind the prior decisions -- so the next phase does not silo (R-22). In single-LLM mode this is reading the right inputs; in agent mode it is the message payload.

### Step 5 -- On completion: audit, present, close the gate

When the sub-skill emits its fragment: run `sad-auditor` `by-fragment` (per the cadence above -- this is a flow step, not a suggestion), present the fragment + audit findings to the operator, and on sign-off mark the gate `[x] approved` in the tracker before advancing. **One fragment per turn:** the sub-skill stops at each fragment's gate. S1 specifically emits `business-view.md`, stops at S1a for approval, and only then emits `naive-architecture.md` for S1b -- it does NOT produce both in one turn.

For the precise ownership boundary between executor and external orchestrator (e.g. a UI like `ui-sad` that sends `[SAD]`-prefixed messages), see **Gate state machine (canonical)** below. In short: the executor never re-mutates a transition the orchestrator already did, and the producer transitions (`[ ]` -> `[~]` -> `[?]`) still belong to the executor -- including **after a reopen**.

### Step 6 -- Backtracking and iteration (the flow is not forward-only)

A SAD is iterative by nature (R-22; O'Reilly "consistently wrong until you reach a point of being a little bit less wrong"). The router must handle going *back*, governed by one rule:

> **Reopen rule.** Reopening gate `Sn`:
> (a) marks **`Sn` itself** back to `[ ]` pending -- the fragment file on disk is retained as the `(iter N)` reference (rename or annotate per FLOW.md "Iteration patterns"); a fresh fragment will be produced on the next pass;
> (b) marks every downstream gate that consumed `Sn`'s output back to `[ ]` pending -- **stale, not deleted** (same annotation rule);
> (c) moves the **`Current step:` line** in `FLOW.md §Current session` back to `Sn`.
>
> When the operator triggers the reopen (via a UI action, a `/reopen` command, or a direct `FLOW.md` edit that flips `[x]` to `[ ]` and clears the date), apply steps (a)-(c) **without asking the operator for confirmation** about the cursor or about retaining the prior fragment -- the reopen action itself is the consent. The operator can override any of these in a follow-up turn.
>
> Forward motion then resumes from `Sn` and must re-traverse every stale gate in order, re-generating and re-approving each fragment, until it catches back up to where the walk was. You cannot jump from `Sn` straight to the front.
>
> The transitions themselves -- `[x]` -> `[ ]` and the downstream cascade -- are formally specified in **Gate state machine (canonical)** below, including which side belongs to which party (orchestrator vs executor) and what the executor still owes after the reopen.

Three cases:

1. **Gate rejection (no cascade).** The operator rejects the fragment at the current gate. Mark it `[i] iterating`; the executor re-works that one fragment. Nothing downstream exists yet -- the gate was blocking it -- so there is no cascade.
2. **Upstream ripple (cascade).** A later phase reveals an earlier fragment is wrong (e.g. S5 finds S3 missed a Structural stressor; S5 finds an IDesign override S4 missed). Apply the reopen rule from the *earliest* affected gate: reopen S3 -> S4 and S5 go `[ ]` -> cursor moves to S3 -> re-walk S3, S4, S5 forward. The canonical loops are tabulated in FLOW.md "Iteration patterns" (S4->S3, S5->S4, S6->S3, S7->S5).
3. **Full re-pass.** After S6, the Ri verdict says iterate. Start iteration N+1 with a fresh, disjoint test-stressor list; annotate prior nodes `(iter N)`; never delete history -- the auditor and the Ri trend read it.

The gate tracker states `[i] iterating` and `[!] blocked` exist for exactly this. The router keeps the tracker honest so "we went back to S3" is recorded state, not something the operator must remember. In agent mode the cursor move is a message resuming the persistent executor at `Sn` (context intact), and the auditor re-runs fresh on each re-emitted fragment.

---

### Gate state machine (canonical)

The gate tracker is a state machine that **two parties** write to. This table is
the **single source of truth** for which transition belongs to whom and what
side-effects it carries; every ownership reference elsewhere in this file
resolves here. Two notes (Step 5 disk-trust; Step 6 Reopen rule) compress to
this table -- read it once and the rest is consequence.

| FROM | TO | Owner | Trigger | Side-effects |
|---|---|---|---|---|
| `[ ]` | `[~]` | **executor** | sub-skill starts producing the fragment | mark in_progress |
| `[~]` | `[?]` | **executor** | fragment emitted; parking at the gate | await operator review |
| `[?]` | `[x]` | **orchestrator** | operator approves | stamp `approved-on` date; advance `Current step:` to the next gate |
| `[?]` or `[~]` | `[i]` | **orchestrator** | operator requests changes | hold; the executor will resume the iteration |
| `[i]` | `[~]` | **executor** | re-entering the gate to iterate | mark in_progress again |
| `[x]` | `[ ]` | **orchestrator** | reopen (UI button / `/reopen` / manual `[x]` -> `[ ]` edit) | preserve the fragment as `Sn.iter-N.md` per FLOW.md "Iteration patterns"; cascade every downstream gate that consumed Sn's output to `[ ]` (stale, not deleted); move `Current step:` back to Sn; the reopen action **is** the consent -- do NOT re-prompt |
| `[x]` | `[i]` | **orchestrator** | post-S5 impact outcome `iterating Sn` (Create-ADR / Add-Use-Case, see §Post-S5 actions) | legal ONLY when Sn is the **frontier**: the last `[x]` with every downstream gate `[ ]`. If any downstream gate is beyond `[ ]`, the assessment MUST escalate to `reopen Sn` instead. Preserves R-26: priors stay `[x]`, Sn becomes the single active gate |
| `[ ]` <-> `[!]` | -- | **orchestrator** | block / unblock | record the blocker |

**Reading the table.**

- **Disk is the source of truth.** When the orchestrator (a UI like `ui-sad`, a
  `/reopen` command, or a manual edit) has already mutated `FLOW.md`, the
  executor **trusts the disk state and does NOT re-mutate**. Its job is to
  **react** -- route to the next sub-skill, re-emit the iterated fragment, or
  run the auditor, as the `[SAD]`-prefixed message indicates.
- **Producer transitions apply after a reopen.** Orchestrator-owned
  `[x]` -> `[ ]` does **NOT** carry the executor's `[ ]` -> `[~]` -> `[?]` --
  those still belong to the executor, exactly as in any other iteration.
  Skipping them is the **most common post-reopen mistake**: it leaves the gate
  at `[ ]` while a fresh fragment sits on disk, blocking the operator's next
  action. The orchestrator owning the operator transition (`[x]` -> `[ ]`) does
  NOT make it own the subsequent producer transitions.
- **Iteration history.** A reopen preserves prior fragments; they are never
  deleted. The latest iteration is canonical; earlier ones are dated history
  (see FLOW.md "Iteration patterns").
- **Post-S5 amendments enter here.** The `[x]` -> `[i]` row exists for exactly
  one trigger: the `iterating Sn` outcome of a post-S5 operator action
  (Create-ADR / Add-Use-Case, §Post-S5 actions). Its frontier restriction is
  what keeps the amendment compatible with R-26 below -- an `[i]` behind an
  approved downstream gate would break invariants 1-3, so a non-frontier
  amendment must travel as a `reopen Sn` cascade instead.
- **Tracker coherence (R-26, NON-NEGOTIABLE).** Three invariants must hold at
  every read: (1) the chain of `[x]` is contiguous from the top; (2) every
  active gate (`[~]` / `[?]` / `[i]`) has all priors `[x]`; (3) at most ONE
  gate is active at any time -- only the first gate after the last `[x]` may
  be active. Together these make the workflow single-threaded: at any moment
  there is at most one decision pending for the operator. Any read showing an
  `[x]` on a non-`[x]` prior, an active gate on an unapproved prior, or two
  active gates is a violation, and Step 1 refuses to advance. R-26 is the
  state-shape rule the table preserves; the table specifies transitions, R-26
  specifies legal configurations.

### Subagent orchestration

When invoked from an orchestrator UI (`ui-sad` / ADDL / equivalent), the router parent **SHOULD** delegate gate production to an `Agent` tool subagent rather than producing the fragment in its own context:

| Role / `subagent_type` | Spawned when |
|---|---|
| `Architect` | Parent transitions the gate `[ ] -> [~]` and dispatches. Produces the gate's fragment (S1a, S1b, S2-S7, S8a, S8b). |
| `Architect-Auditor` | After the `Architect` subagent returns; before the parent transitions `[~] -> [?]`. Runs `sad-auditor` against the just-emitted fragment. |

**Binding to the Agent tool.** When the orchestrator UI exposes a custom-agent registry (`.claude/agents/<Name>.md`), the parent **MUST** invoke each subagent with `subagent_type` set to the role name verbatim (`Architect`, `Architect-Auditor`) -- not `general-purpose` with the role mentioned in the `description` field. The role-namespaced labels below are identifier-typed, not free-form labels; the `description` field carries the per-gate task, not the role. Reference templates for the two SAD agent files live under `agents/` in this skill; orchestrator UIs are responsible for installing them into the active workspace's `.claude/agents/` before the parent's first turn. When no custom-agent registry is available (manual CLI session, no UI), this binding is advisory and the parent falls back to the single-LLM topology described in §Running as agents.

The parent's writes are limited to:

1. `FLOW.md` Gate tracker mutations: `[ ] -> [~]` when production starts, `[~] -> [?]` when the subagent returns and the fragment is parked at the gate. The orchestrator-owned transitions (`[x]`, `[i]`, the `[x] -> [ ]` reopen) are handled by the UI before the parent ever sees an inject -- per the canonical state machine table above.
2. After a reopen: rename the prior fragment to `Sn.iter-N.md` per the `[x] -> [ ]` row of the canonical state machine table **before** spawning the new `Architect` subagent. The rename is parent-owned because it preserves iteration history independently of the next subagent's choices.

The parent does **NOT** write fragment content or audit content directly. This separation is the project's cognitive equivalent of re-loading Claude per gate, without the operational cost: the parent stays small and stable (orchestration moves only), each subagent gets a fresh context window scoped to a single gate.

If the orchestrator runs as a single agent (no UI, no `Agent` tool available -- e.g. a manual CLI session), this subsection is advisory; the canonical gate machine and ownership boundary in §Gate state machine (canonical) still apply, and the topology defaults to §Running as agents below (the persistent-executor base topology).

**Role-namespaced `subagent_type`.** The roles above (`Architect`, `Architect-Auditor`) follow a `<Role>` / `<Role>-Auditor` convention. Future roles take the same shape: `Developer` for downstream consumers that wrap spec-kit production, `Developer-Auditor` for consumer-side audit mechanisms (Constitution Check Q1-Q6, plan-template conformance -- distinct from the SAD `sad-auditor`). The role prefix prevents `subagent_type` collision when `Architect` and `Developer` subagents coexist in the same parent session.

## Running as agents (optional runtime -- design, not yet implemented)

The orchestration above is runtime-agnostic. It can run as a single LLM navigating these documents (the default today), or as a multi-agent system. The naive case for agents is **context isolation** -- each sub-skill is large, and one LLM holding all eight + `shared/` + the SAD-in-progress saturates on a big SAD. But isolating *every* phase fights the skill's core asset: the **architectural walk** (R-22), the accumulated lateral reasoning across phases. The base topology is therefore deliberately minimal.

### The boundary principle

Only **one** agent boundary helps; the rest are pure cost.

- **executor <-> auditor is a feature.** The auditor judges output SHAPE from *outside* (R-22); fresh context is exactly what makes an external audit more rigorous than self-audit. Worth isolating.
- **phase <-> phase is pure cost.** Splitting S1..S7 across agents serializes the walk into lossy messages -- the canonical drift source (constraint #2). Its only upside, fresh context, is marginal: what must stay live in context is **the walk** (accumulated fragments + the "why"), not the sub-skill doctrine, and the doctrine is loadable on demand *within one agent* (the executor reads `stressor-analysis/SKILL.md` when it reaches S3 and lets it age out after). A single executor keeps the walk and rotates the doctrine by construction.

> **When run under an orchestrator UI** (`ui-sad` / ADDL / equivalent), use the
> **Subagent orchestration** variant defined above (parent stays small + stable,
> per-gate ephemeral `Architect` / `Architect-Auditor` subagents). The
> base topology below is the **single-LLM default** (no UI present, no
> `Agent` tool available -- e.g. a manual CLI session).

### Base topology -- one persistent executor + one fresh auditor + router

- **Router** = the orchestrator (the 5 steps above), played by the main LLM acting as the operator's proxy: reads the gate tracker, reports position, routes, delegates, closes gates.
- **Executor agent** (persistent, spawned once): carries the walk across all phases. It produces *one fragment at a time* and **stops at that fragment's gate** -- it never produces the next fragment, even within the same sub-skill, until the operator approves. Example, S1: emit `business-view.md` only -> stop at gate S1a -> [operator approves] -> emit `naive-architecture.md` -> stop at gate S1b -> [operator approves] -> advance to S2. It does NOT emit both S1 fragments in one turn. Resumed via same-id messaging so its context (the walk) stays intact across gates.
- **Auditor agent** (fresh per fragment): runs `by-fragment` in clean context -- more rigorous precisely because it is outside the walk.

The cycle: router spawns the executor once; executor emits a fragment and returns; router runs the auditor (fresh) on it and presents fragment + findings to the operator; on sign-off the router marks the gate `[x]` and sends "gate approved, continue" back to the *same* executor (context intact). The walk persists, the audit stays external, the human gate stays between every fragment.

### Hard constraints (do not sacrifice these for autonomy)

1. **Human-in-the-loop at every gate stays.** The chain is NOT autonomous; it pauses at each gate for operator approval (Gate approval protocol). An agent chain that auto-advances through gates breaks the skill's core discipline.
2. **Coherence is the risk.** Any isolation adds drift surface. The deterministic consistency checks (`sad-auditor` §2.7, R-13 count, Ri arithmetic) become *more* critical with agents, not less.
3. **The handoff carries the "why".** Per R-22 the lateral reasoning must propagate, not just the artifact. A single persistent executor makes this nearly free -- the walk never crosses an agent boundary; the Handoff contracts (each sub-skill's `## Handoff contract`) become its internal notes rather than lossy inter-agent messages.

### Saturation escape hatch

The base topology can saturate on a very large SAD -- by S6/S7 the executor holds every fragment. But those phases need everything in context anyway (S6 compares Y vs X vs S; S7 reconciles all six fragments), so they cannot be isolated regardless. The fix is not "an agent per phase"; it is an **ephemeral sub-agent for a heavy, bounded, mechanical task** (e.g. generating the S4 N x N contagion matrix) that returns only its result and dies. That is a point optimization, not the base topology.

Implementing the Handoff contracts in doctrine first (single-LLM mode) is the prerequisite; the agent runtime is a later layer on top, justified only when a real SAD's context size demands it.

---

## The doctrine -- constitution R-01 to R-27

The full rule set lives in `shared/constitution.md` (canonical). Each sub-skill cites by `R-NN`. Key rules every sub-skill respects:

| Rule family | Rules | Scope |
|---|---|---|
| Decomposition principles | R-01 (residue is the unit), R-21 (criticality goal), R-22 (lateral mindset) | All sub-skills |
| IDesign service hierarchy | R-02 (typing), R-03 (closed architecture), R-04 (4 legitimate exceptions; Client/Resource do NOT call Utility -- tightening per 2026-05-10) | S1, S5 |
| Naming and hygiene | R-05 (no tech vocab), R-06 (Pascal case + suffix), R-07 (atomic business verbs in RA contracts only) | S1, S5 |
| Anti-design | R-09 (no speculative design), R-10 (no solutions masquerading), R-11 (almost-expendable Manager), R-12 (interface stability) | S1, S5 |
| Stressor analysis discipline | R-13 (typed residues), R-17 (Combined recorded as Looping Signals), R-18 (no component without Structural residue), R-19 (no deployment unit without Topological residue), R-20 (no probability/cost before matrix closure) | S3, S4, S5 |
| Integration discipline | R-14 (IDesign override on cross-layer merge), R-15 (NFR traceability), R-16 (use cases document, not drive) | S4, S5 |
| Representation discipline | R-23 (C4 expressed as one Structurizr DSL workspace + per-level scope; System Context / Container / Component-per-container / Deployment / optional Dynamic views derived from one model) | S5, S7 |
| Smallest-set residue discipline | R-24 (extend existing ResourceAccess before introducing new Resources; Lowy "in theory just another Manager" baseline) | S3, S5 |
| Service grouping | R-25 (actor-style grouping: one Manager = one service / deployment unit; deliberate synthesis decision) | S4, S5 |
| Workflow integrity | R-26 (gate-tracker coherence, NON-NEGOTIABLE: contiguous `[x]` chain, active gates require approved priors, single active gate) | Router, all gates |
| Business framing completeness | R-27 (Open Questions surfaced via multi-lens PRD scan attested by a Lens Coverage Ledger -- every lens L1-L12 emits a verdict; gate S1a warns + requires acknowledgment while any question is `Open`) | S1 |

---

## The output -- `sad.md`

The final SAD is a single markdown file per project, structured per `sad/template.md`. Sections:

- Methodological Note
- Business View
- Architectural Stress Analysis (Naïve + Flow + Stressor Catalog + Contagion Matrix + NKP + Hyperliminal Coupling Map + Topological Residue Map + Business Residues Log + Looping Signals + Derived NFRs + Empirical Test)
- Analysis and Design (Behavioral Diagrams [PlantUML] with Use Case Residue Mapping + General NFRs + Structural Diagrams: Static Architecture [PlantUML] + C4 Model (one Structurizr DSL workspace: System Context + Container + per-Container Component + Deployment views))
- Technical Considerations
- Restrictions (Pub/Sub + Event Schema + Decomposition Discipline rules)
- Appendices (References + ADRs + Audit Status + Stressor Source Frameworks + Glossary)

Worked examples in `sad/examples/`:
- `ev-charging-sad.md` -- canonical worked example from O'Reilly's book (Chapter "A Worked Example").
- `trademe-sad.md` -- worked example from Lowy's *Righting Software* Chapter 5, with iteration-1 Ri = 0.83.

---

## Per-project workspace convention

When running the meta-skill on a real project, the workspace splits **deliverable** from **workshop** (the line is what the stakeholder consumes, NOT the gate boundary):

- `<project-root>/docs/sad/` holds **only the SAD deliverable**: the assembled final `sad.md` (S7), the `use-cases/`, and the `arch-X.Y.Z/` release dirs.
- `<project-root>/docs/architect/` is the **Architect role's workshop**: the `S1a-S6` working fragments (`business-view.md` ... `empirical-test.md`) that get assembled into `sad.md`, the `FLOW.md` gate tracker, and the audit reports (`audit-iter-N.md` per iteration, `audit-handoff-arch-X.Y.Z.md` at handoff).

ADRs go to `<project-root>/docs/adr/ADR-XXXX-<short-name>.md` using `adr-template.md`. Each lifecycle role owns its own `docs/<role>/` workshop the same way -- e.g. the brownfield Reverse-Engineer's `recon-*` writes under `docs/reverse-engineer/`; the Architect additionally publishes its deliverable to `docs/sad/`.

The meta-skill repo's own `sad/examples/trademe-workspace/` is preserved as a didactic artifact -- it shows the fragment-by-fragment evolution of a SAD.

---

## Post-S5 actions (operator-driven artifacts with impact assessment)

Two artifacts can be emitted by the operator at any point AFTER S5 has produced
`residual-design.md` -- once the C4 diagrams and Residue Mapping exist,
decisions and use cases have something to land on. They are NOT gates; they are
operator actions that may FORCE a gate to iterate or reopen.

| Action | Workspace output path | Template / contract |
|---|---|---|
| **Create-ADR** | `<project-root>/docs/adr/ADR-XXXX-<short-name>.md` | `sad/adr-template.md` |
| **Add-Use-Case** | `<project-root>/docs/sad/use-cases/uc-NNN-<slug>.md` (pre-S8a draft; use cases are part of the deliverable). Post-S8a, additionally transcribed to staging per §Post-S8a propagation below. | `sdd-interface/contracts/use-case-contract.md` |

### Preconditions (both actions)

1. **S5 MUST be in state `[x]` approved, `[?]` awaiting_review, or `[i]` iterating.**
   Before S5 there is no residual-design and no C4; an ADR cannot reference
   diagrams that do not exist, a use case cannot map services to residues
   without contagion-analysis approved. The router and any orchestrator UI MUST
   refuse the action otherwise.
2. **R-26 invariants MUST hold** at the moment of dispatch. The action runs
   against a coherent tracker.

### Template conformance (both actions)

The artifact body conforms to the FULL existing schema -- no omitted sections:

- **ADR** -- the complete `sad/adr-template.md` structure: metadata table,
  Options Considered, Decision, plus the `## Impact assessment` section below.
- **UC** -- the complete `use-case-contract.md` section 1 schema: metadata
  table, sections 1-13, with the Architectural Context block carrying the Call
  Chain (Mermaid, layer rules R-03/R-04), Services touched (catalog names ONLY
  -- Service Grouping Map authority), and Residue (`S-NN` per service); NFRs
  referenced by id, never inlined.

Shape reference: the worked examples in
`sdd-interface/examples/ev-charging/arch-1.0.0/` (`use-cases/uc-001-charge-session.md`,
`decisions/ADR-001.md`).

### Impact assessment (normative, both actions)

After the artifact is emitted, the parent (or `Architect` subagent in the
parent's place when an orchestrator is installed) **MUST** run an impact
assessment BEFORE returning control to the operator. The assessment is a short
section appended to the workspace artifact under the heading
`## Impact assessment` with exactly these three fields:

- **`Affected gates:`** -- comma-separated `Sn` ids (may be empty).
- **`Outcome:`** -- exactly one of `no-op` | `iterating Sn` | `reopen Sn`.
  Exactly one Sn id per outcome (the upstream-most affected gate).
- **`Rationale:`** -- 1-3 sentences citing the specific diagram, residue,
  stressor, or NFR that the new decision / use case touches or invalidates.

Mapping outcome -> FLOW.md transition (orchestrator-owned, per
§Gate state machine (canonical) -- the artifact itself NEVER mutates the
tracker):

| Outcome | FLOW.md transition | When to choose |
|---|---|---|
| `no-op` | none | The artifact is captured by existing residues / catalog / NFRs; the SAD already accounts for it. May carry a documentation side-effect (see the absorbed-stressor cue below). |
| `iterating Sn` | `Sn: [x] -> [i]` per the `[x]` -> `[i]` row of the canonical table -- **frontier only**: legal ONLY when Sn is the last `[x]` and every downstream gate is `[ ]`. No downstream cascade. | The artifact changes a detail INSIDE Sn's fragment (a deployment node, a residue mapping cell, an NFR entry) but does not invalidate downstream fragments -- and nothing downstream is approved. If a downstream gate is beyond `[ ]`, escalate to `reopen Sn`. |
| `reopen Sn` | `Sn: [x] -> [ ]` + downstream cascade to `[ ]` (per the `[x]` -> `[ ]` row of the canonical table) | The artifact invalidates an upstream decision that downstream fragments depend on, or amends a non-frontier gate. |

### Create-ADR -- specific rules

- **Naming.** `ADR-XXXX-<short-name>.md` where `XXXX` is the next zero-padded
  sequence in `docs/adr/`. Scan the directory; do not assume.
- **Body.** Conforms to `sad/adr-template.md` per §Template conformance. The
  `## Impact assessment` block is REQUIRED on every ADR created via this action.
- **Technology is an architecture decision.** The `Rationale:` MUST enumerate
  the concrete artifacts the decision forces to regenerate (which C4 diagram,
  which NFR rows, which `sad.md` sections). Regeneration happens only through
  the outcome: `iterating S5` re-emits the amended `residual-design.md`
  (diagrams included); once S7 is `[x]` (sad.md assembled), the only legal
  route is `reopen` with cascade -- downstream documentation never drifts from
  the decision.
- **Worked examples (the three impact classes):**
  - *"Use Apache Pulsar as the message bus."* New container in C4 Container;
    new node in C4 Deployment; new ResourceAccess + Resource in the Static
    Architecture. -> **`Outcome: reopen S5`**.
  - *"Choose Postgres (not MySQL) as the Resource for LinksDB."* Only the
    Deployment diagram of S5 changes (and an NFR row for storage SLO); static
    architecture and Service Grouping Map unchanged. -> **`Outcome: iterating
    S5`** -- but ONLY while S5 is the frontier. With S6+ already approved, the
    correct outcome is **`reopen S5`** (the Ri evidence and assembled SAD
    consumed the old deployment view).
  - *"Adopt 90-day data-residency policy for EU tenants."* Already covered by
    an existing NFR-NN with Source; no diagram changes. -> **`Outcome: no-op`**.

### ADR lifecycle (status is binding)

An ADR carries a `Status` (`DRAFT` / `PROPOSED` / `ACCEPTED` / `DECLINED` /
`SUPERSEDED`). The transition between statuses is an **operator decision the
orchestrator owns** -- the same ownership split as a gate state: the producing
subagent writes the ADR body; the operator (via the ADDL ADR panel, or a human
editing the `| **Status** |` cell) sets the status. The executor MUST NOT change
an ADR's `Status` on its own initiative.

**The binding rule.** An `ACCEPTED` ADR is binding. Its decision MUST be
reflected in the architecture before S7 (assembly) can pass:

- If its `## Impact assessment` `Outcome` is `iterating Sn` or `reopen Sn`, the
  named gate's fragment MUST be re-emitted to incorporate the decision, and MUST
  cite the ADR by id (e.g. `residual-design.md`: "the `IdentityService`
  container ... removed by **ADR-0001**"). The ADR id appearing in the affected
  fragment is the deterministic proxy for "incorporated".
- If its `Outcome` is `no-op`, the ADR is governance-only and binds nothing
  structurally (it is still listed in §Appendices, but it does not gate
  assembly).
- A `DECLINED` / `SUPERSEDED` ADR does not bind: it records a decision the
  architecture deliberately does not (or no longer) follows.

Approving S7 while an `ACCEPTED`, non-`no-op` ADR is not yet reflected in its
impact gate's fragment is a violation (`check_adr_applied.py`, see §sad-auditor
and `scripts/fragment-checks/`). Resolve it by applying the impact (re-emit the
gate so it cites the ADR) or by changing the ADR's status away from `ACCEPTED`.

**Cite the ADR by id, never its Status.** When a fragment narrates an ADR's
effect, reference it as `ADR-NNNN` only (e.g. `residual-design.md`: "the
`IdentityService` container is removed by **ADR-0001**"). Do NOT transcribe the
ADR's `Status` (`DRAFT` / `PROPOSED` / `ACCEPTED` / `DECLINED` / `SUPERSEDED`)
into the prose -- the status is operator-owned and mutates after this fragment is
written (e.g. the operator accepts the ADR), so any inline status goes stale and
trips a false auditor mismatch ("PROPOSED rather than ACCEPTED") even when the
architecture is correct. The ADR file's `| **Status** |` cell is the single
source of truth; only the assembler's §Appendices ADR table shows a Status, read
live from the ADR file at assembly time. Enforced by
`scripts/fragment-checks/check_adr_status_prose.py`.

### Add-Use-Case -- specific rules

- **Naming.** `uc-NNN-<slug>.md` where `NNN` is the next zero-padded sequence
  in the target use-cases directory and `<slug>` is lowercase-kebab.
- **Phase.** Pre-S8a: the UC drafts to `docs/sad/use-cases/`.
  Post-S8a: see §Post-S8a propagation below -- never written directly into the
  consumer.
- **Body.** Conforms to the use-case-contract structure per §Template
  conformance. The `## Impact assessment` block is REQUIRED on every UC created
  via this action (it is OPTIONAL when the UC is emitted as a primary UC inside
  `residual-design.md` during S5).
- **Decision cues (evaluate in order):**
  1. Does the UC introduce a service NOT in the Service Grouping Map? ->
     **`Outcome: reopen S5`** (catalog amendment per `use-case-contract.md` §6
     first bullet -- the catalog is amended by re-working S5, never by
     inventing the service inside the UC).
  2. Does the UC surface a stressor never seen in S3 that existing residues do
     NOT absorb? -> **`Outcome: reopen S3`** (per `use-case-contract.md` §6
     third bullet -- the canonical re-entry from a UC into stressor analysis).
  3. Does the UC surface a NEW stressor that existing residues DO absorb
     (S6-style check: thrown against the residual architecture it produces
     zero component changes)? -> **`Outcome: no-op`** with a documentation
     side-effect: append the stressor, typed per R-13, to a separate Stressor
     Catalog subsection `Post-S5 additions -- absorbed` with provenance
     (`via UC-NNN, absorbed by <component>`). No gate transitions. The
     subsection is separate precisely so the deterministic checks (R-13 count
     vs S4 matrix dimension) stay coherent -- this mirrors how S6 records test
     stressors that pass.
  4. Does the UC combine existing services in a new call chain but introduce no
     new stress? -> **`Outcome: iterating S5`** (Residue Mapping gets a new
     row; static architecture unchanged; frontier restriction applies).
  5. Does the UC merely reword an existing primary use case in
     `residual-design.md`? -> **`Outcome: no-op`**.

This is the operationalization of the "future add-use-case skill" forward
reference in `sdd-interface/contracts/use-case-contract.md` §6.

### Post-S8a propagation (both actions)

When S8a is `[x]` (a handoff release exists), the workspace artifact alone is
not enough -- the handed-off artifact set must follow, by the outcome:

- **Outcome `reopen Sn`:** the cascade reaches S8a; on the re-walk, S8a emits a
  **new release** (`arch-X.Y+1.Z` -- releases are immutable, a new release is a
  new directory) and the artifact travels inside that release in its contract
  format. The old release is never patched.
- **Outcome `no-op` / `iterating Sn`:** the current release stays valid; the
  action ALSO transcribes the artifact, append-only (CHK-13), into the staging
  directory `handoff/arch-X.Y.Z/`:
  - ADR -> `decisions/ADR-NNN.md` per `sdd-interface/contracts/adr-contract.md`
    (next `NNN` by directory scan; if `Binding: Yes`, sweep the binding-ADR
    reference -- append-only (CHK-13) -- into EVERY handoff artifact that
    ENUMERATES the binding-ADR set or count, so the release stays internally
    consistent: the handoff manifest's "Binding ADRs" section (its recited
    "N binding ADRs" count is reconciled against the enumerated tally by
    `check_handoff.py`, CHK-14), the constrained services' "Binding ADRs" field
    in `service-catalog.md` (referenced-from-catalog, CHK-12), and the
    "Binding ADRs (this release)" line in `integration/constitution.scaffold.md`.
    Do NOT edit the agnostic principle text
    (`integration/principle-decomposition-by-residue.md`) -- injecting a concrete
    ADR into its clauses would violate CHK-05; artifacts that only point at the
    manifest's list rather than enumerating their own set
    (`integration/plan-template-constitution-check.md` question 6,
    `integration/sync-impact-report.md`) need no edit. INVARIANT: after the
    sweep no enumerating artifact may still show a set / an `N binding ADRs`
    count that excludes the new one while the manifest lists it -- that
    stale-half state is the RDAG coherence defect CHK-14 flags in `handoff`-mode
    (binding-ADR locatability stays CHK-12));
  - UC -> `use-cases/uc-NNN-<slug>.md` per the use-case contract.

  The consumer (`architecture/arch-X.Y.Z/`) is updated ONLY via the gated
  re-land (S8b pattern: explicit operator authorization). The skill never
  writes the consumer directly.

The `## Impact assessment` block lives on the **workspace** artifact only --
the RDAG transcription does not carry it (the consumer does not consume gate
tracker state).

### Orchestrator delegation

When invoked from an orchestrator UI exposing a custom-agent registry
(`.claude/agents/`), the parent **SHOULD** invoke an `Architect` subagent
(`subagent_type: Architect`) to write the artifact AND run the impact
assessment, per §Subagent orchestration. The parent owns the FLOW.md transition
derived from the subagent's `Outcome:` field. When no registry is available,
the parent runs the assessment in its own context (single-agent fallback, same
wording substitution as §Subagent orchestration).

---

## When NOT to invoke this skill

- Project is genuinely simple, short-lived, or well-understood. The overhead of stressor analysis is not justified for a 2-week throwaway. (O'Reilly L2667-2672 / `architectural-walking.md` §9.)
- The user wants a code review or a low-level technical decision (not an architecture). Route to general engineering tooling.
- The user wants an ADR for a single decision and **no SAD lifecycle is in flight**. Use `sad/adr-template.md` directly without invoking the full SAD chain. If a SAD IS mid-lifecycle (S5 in `[x]` / `[?]` / `[i]`), the ADR goes through the **Create-ADR** action instead (§Post-S5 actions) so its impact on the gates is assessed, not skipped.

If the user's context is hyperliminal (a complicated software system inside a complex non-ergodic context), the meta-skill applies. If the user is uncertain about whether their context warrants it, default to invoking with awareness that the skill can be partially used (e.g., stop after S3 stressor analysis to surface stress without building the full SAD).

---

## References

- `shared/constitution.md` -- the 26 active rules (R-01 to R-27, R-08 intentionally absent).
- `shared/architectural-walking.md` -- the lateral cognitive mode (R-22) the workflows assume.
- `shared/idesign-vocabulary.md` §9 -- the workflow Manager pattern baseline vs elaboration (R-24).
- `shared/decomposition-discipline.md` -- the 8 guardrail rules.
- `shared/stressor-frameworks.md` -- the 6 frameworks used in S3.
- `shared/kauffman-nkp.md` -- the NKP theory underlying S4 readings.
- `sad/synthesis-explanation.md` -- the seven synthesis decisions; read before S1.
- `sad/template.md` -- the normative SAD structure.
- `sad/adr-template.md` -- the ADR template + decision tree for when to use ADRs.
- `sad/examples/` -- worked examples.

Source books: `righting-software-md/` (Lowy), `residuality/residuality-md/` (O'Reilly). Training material: `training/` (IDesign Inc Virtual Method 2015).
