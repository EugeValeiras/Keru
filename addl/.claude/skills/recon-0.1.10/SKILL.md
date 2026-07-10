---
name: recon
version: 0.1.10
description: Use this skill to reverse-engineer an existing, running, poorly-documented codebase and reconstruct it from the code itself -- the brownfield front door for understanding a system before any architecture, onboarding, or review work. Invoke when someone is handed a brownfield, legacy, or inherited repo with little or no documentation (no PRD/SRD, no architecture doc, no useful README) and needs to figure out what it actually is, what it does, who it serves, why it exists, and where it hurts. Covers reverse-engineering or onboarding an undocumented or inherited system; mapping the inventory (entry points, modules, data stores, external integrations, build/deploy) and the observable behavior and flows traced to real handlers, jobs, and tests; reconstructing business intent (objective, users, pain points, goals) with confidence flags; and auditing the as-built plus its observed stressors (incidents, churn, coupling, hacky bits). It can also package three-plane Phase-0 evidence to hand to a SAD, and detect drift between an existing architecture doc and the code running now. Runs as a gated R1-R4 chain plus a cross-cutting auditor; every claim is anchored to file:line or a commit -- reconstruction from evidence, not narration. Do NOT use for greenfield design from a PRD, line-level bug or security review, or proposing a new, better, or refactored architecture (that is downstream design work).
task_types:
  - reverse-engineer
  - onboard-brownfield
  - reconstruct-architecture
  - system-cartography
  - behavior-reconstruction
  - reconstruct-business-view
  - asbuilt-audit
  - detect-architecture-drift
  - phase0-evidence
  - recon
shared_refs:
  - shared/constitution.md
  - shared/evidence-anchoring.md
  - shared/glossary.md
  - templates/system-cartography.md
  - templates/behavior-reconstruction.md
  - templates/reconstructed-business-view.md
  - templates/asbuilt-stressors.md
  - templates/phase0-evidence.md
---

# recon

**Version: 0.1.10** (2026-06-19). This is the single source of truth for the meta-skill version (it matches the directory name `recon-0.1.10/` and the packaged bundle). The sub-skills do not carry their own version -- they are versioned as part of this meta-skill.

> **On invocation, state the version.** The first time this skill is activated in a session, announce: `recon v0.1.10`. This lets the operator confirm which version is running before any recon work begins.

The meta-skill that reverse-engineers a running, under-documented system into the **three-plane Phase-0 evidence** a SAD consumes. ADDL's normal chain starts from a PRD/SRD; the most common real-world case -- a project that already exists, already runs, with little or no documentation -- falls outside that. The SAD already has the *reception socket* for an existing system (its "When a prior implementation exists (Phase-0 as evidence)" mode): it accepts a document of three planes -- a **business framing** (feeds S1a), an **audit of the existing implementation** (a *residual candidate* that S6 measures, never the baseline), and **anticipated stressors / gaps** (held for S3). What was missing is a producer that **generates those three planes from the code itself** instead of asking a human to write them by hand. `recon` is that producer. The SAD is left untouched -- this is not a patch to the SAD; it is the role that feeds it.

## The golden rule -- anchor to evidence (RE-01)

Reverse engineering is exactly where a language model invents structure with confidence. Read `shared/evidence-anchoring.md` before producing any fragment. **Every assertion in every fragment cites `file:line` or a commit, or it is degraded** -- deleted, or kept and marked `⚠ unverified`. What is not anchored to the code does not survive as a finding. This single rule is what separates a recon fragment (a set of pointers into the system, each checkable in one click) from a confabulation (a plausible story about a system that may not exist). Without it the skill is worse than useless -- it manufactures false confidence. The other four rules (RE-02..RE-05, `shared/constitution.md`) are this discipline extended to inferred intent, redesign-avoidance, observed stress, and tracker & workspace coherence.

**Documentation is swept, but ranked below code (RE-01 §6).** A brownfield often does carry docs (README, `docs/**`, `*.puml`, `CLAUDE.md`); *no information in the repo is discarded -- all of it is valuable*, but documentation is a **lead**, the code is the **proof**. A doc declares what the authors *say*; for the *audit* plane (R1/R2) a claim resting only on a doc is `⚑ declared (not observed)` -- an intended-but-unbuilt **milestone**, captured in its own section (never dropped, never mixed with observed facts) for a downstream reader to keep or cut -- until a code anchor confirms it. The completeness duty: enumerate every doc artifact with a command + count, account for each. See `shared/evidence-anchoring.md` §6.

---

## The four sequential sub-skills + auditor

Each sub-skill produces **exactly one fragment**, parks it at its gate `[?]`, and **STOPS** for human review. After R1..R4 are approved, their content **is** the SAD's three-plane Phase-0 evidence; the optional `handoff-assembler` packages them into a single `phase0-evidence.md` for copy-paste into a new SAD project. The cross-cutting auditor (`recon-auditor`) can run at any gate, end-to-end, or in diff (drift) mode.

| Gate | Sub-skill | Fragment | Produces | Feeds SAD plane | Pre-conditions |
|---|---|---|---|---|---|
| **R1** | `system-cartography` | `system-cartography.md` | Inventory: entry points, services/modules, data stores, external integrations, build/deploy topology, runtimes | *audit* | None (entry skill) |
| **R2** | `behavior-reconstruction` | `behavior-reconstruction.md` | What it actually does: use cases / flows observed from routes, handlers, jobs, schedulers, tests | *audit* | R1 approved |
| **R3** | `business-reconstruction` | `reconstructed-business-view.md` | Inferred objective / users / pain points / goals, each with confidence + evidence (RE-02) | *business framing* -> **S1a** | R1 + R2 approved |
| **R4** | `asbuilt-stressors` | `asbuilt-stressors.md` | IDesign typing of the as-built + observed coupling/contagion + observed stressors (RE-04) | *residual candidate* (-> **S6**) + *stressors* (-> **S3**) | R3 approved |
| -- | `recon-auditor` (cross-cutting) | `audit-iter-N.md` / `audit-drift-<ref>.md` | RE-01..RE-05 checks; drift between code and a prior SAD/recon | -- | At least one fragment exists (by-gate / end-to-end); a prior SAD or recon (diff) |
| -- | `handoff-assembler` (optional) | `phase0-evidence.md` | The three planes labelled for the SAD (`## Business framing -> S1a`, `## As-built audit -> S6 evidence`, `## Observed stressors -> S3`) | the full handoff | R1..R4 approved |

The sub-skills live as directories under `recon/` -- each has its own `SKILL.md` with When to invoke / When NOT to invoke / Pre-conditions / Handoff contract / Output contract / Refusal conditions / References.

### Gate approval protocol

The sub-skills are sequential and each consumes the prior fragment. Approval between gates is **enforced, not assumed**:

1. The project workspace has a **gate tracker** (the table in `FLOW.md` §Current session), one row per gate -- **R1, R2, R3, R4** -- each `[ ]` pending until the operator signs off.
2. **Before producing any fragment, the sub-skill verifies its prior gate is `[x] approved` in the tracker** -- not merely that the prior fragment file exists. A file can exist while still `[?] awaiting review` or `[i] iterating`; producing the next fragment on top of an unapproved one is the premature-advance error.
3. If the prior gate is not `[x] approved`, the sub-skill refuses and points the operator to the open gate. (R1 has no prior gate; it is the entry.)
4. On operator sign-off, mark the gate `[x] approved` with the date, then advance.

This makes "we are still on R2" a checked precondition rather than something the operator has to catch. Each sub-skill's `Pre-conditions` references this protocol.

### Recommended auditor cadence

The `recon-auditor` is most valuable run proactively, not only when the operator remembers to ask:

- **`by-gate` at every gate**, before the operator approves a fragment -- the cheap, routine check. This is where RE-01 (unanchored claims) and RE-02 (un-flagged intent) get caught before they propagate.
- **`by-gate` at the close of R3** specifically: R3 is the inference-heavy gate (business intent reconstructed from code), so it is where mis-calibrated confidence and intent-stated-as-fact surface.
- **`end-to-end` after R4**, before the handoff -- the full RE-01..RE-05 pass over all four fragments + tracker coherence.
- **`diff` (drift) periodically once the SAD exists** -- re-run recon over the evolved code and diff against the prior SAD/recon. This is the capability that keeps the architecture honest over time; see §The drift loop.

---

## Orchestration -- routing, state, and handoff

The router is an **orchestrator**, not a lookup table. It reads state, reports position, routes, delegates with an explicit handoff, closes each gate, and rewinds the cursor when an upstream gate reopens. This protocol is **runtime-agnostic**: it describes how a single LLM navigates the sub-skills today, and it is the same contract a multi-agent runtime uses (see §Subagent orchestration). On every invocation:

### Step 1 -- Read state first (do not route blind)

Before routing, read the **gate tracker** (`FLOW.md` §Current session). Two cases:

- **No workspace / tracker yet and the request is a new recon** -> bootstrap: create the recon workspace (`<target-root>/docs/reverse-engineer/`), copy the bundled `FLOW.md` template, initialize the gate tracker with **R1, R2, R3, R4** all `[ ]`. Then route to R1. (Recon writes its whole flow — tracker, fragments, audit reports — into the *target* repo's `docs/reverse-engineer/`, its own role folder; `docs/architecture/` is reserved for the SAD deliverable that recon's evidence later feeds. ADDL lists both.)
- **Tracker exists** -> read which gates are `[x] approved`, `[?] awaiting review`, `[i] iterating`, `[!] blocked`.

**Artifact existence is verified, not asserted by the log (disk wins).** For every gate the tracker reports as `[?]` / `[x]` / `[i]`, the router MUST check that the gate's named fragment exists on disk before reporting position. A gate whose fragment file is absent is **automatically degraded to `[ ]`** (with a note: "tracker said `[?]` but `<file>` not on disk -- degraded to pending"). The tracker is a working note; disk is the source of truth.

**Tracker coherence is verified, not assumed (RE-05 -- NON-NEGOTIABLE).** Walk the tracker R1 -> R2 -> R3 -> R4 and verify the three invariants:

1. **Contiguous approval chain.** Every `[x]` has every prior gate `[x]`.
2. **Active gates require approved priors.** Every `[~]` / `[?]` / `[i]` has every prior gate `[x]`.
3. **Single active gate.** AT MOST ONE gate is in `[~]` / `[?]` / `[i]` -- only the first gate after the last `[x]` may be active.

Any violation is a **tracker inconsistency** -- report it next to position ("Gates approved: R1; inconsistency: R3 `[x]` while prior R2 is `[?]`") and **refuse to route** until the operator resolves it (revert the offending gate to `[ ]`, or approve every missing prior). No `--force`. The single-active-gate rule keeps the workflow single-threaded -- only one decision pending at a time.

### Step 2 -- Report position

State it back before acting: e.g. "Gates approved: R1, R2. Current: R3 awaiting review. Next: business-reconstruction." This makes "where are we" explicit instead of inferred -- the operator can correct a wrong read before any fragment is produced.

### Step 3 -- Route, and confirm against state

Map the request to a sub-skill, then **check it against the tracker**:

| Operator says | Routes to |
|---|---|
| "Onboard / reverse-engineer / document this existing repo" / "what is this system" | Start at R1 `system-cartography` |
| "We have the inventory; map what it actually does / the flows" | R2 `behavior-reconstruction` |
| "Reconstruct the business view / why does this exist / who is it for" | R3 `business-reconstruction` |
| "Type the as-built in IDesign terms / find the observed stressors / where does it hurt" | R4 `asbuilt-stressors` |
| "Audit this fragment / check the anchors / validate against RE-01..RE-05" | `recon-auditor` (by-gate or end-to-end) |
| "Has the architecture drifted / diff the code against the SAD / what went stale" | `recon-auditor` (diff / drift mode) |
| "Package the Phase-0 evidence / assemble the handoff for the SAD" | `handoff-assembler` (only after R4 `[x]`) |

If the requested sub-skill's **prior gate is not `[x] approved`**, do NOT delegate -- surface the gap ("R3 needs R2 approved; R2 is still awaiting review") and let the operator approve or redirect. This is the router-side complement to each sub-skill's own gate pre-condition.

### Step 4 -- Delegate with the handoff contract

Hand the sub-skill exactly what its **Handoff contract** declares it consumes (each sub-skill `SKILL.md` has a `## Handoff contract` section: Consumes / Produces / Carry-forward context). Pass not only the prior fragment but the **carry-forward context** -- e.g. R1 passes which modules looked hot or coupled so R4 knows where to point its churn/contagion analysis. In single-LLM mode this is reading the right inputs; in agent mode it is the message payload.

### Step 5 -- On completion: audit, present, close the gate

When the sub-skill emits its fragment: run `recon-auditor` `by-gate` (per the cadence above -- a flow step, not a suggestion), present the fragment + audit findings to the operator, and on sign-off mark the gate `[x] approved` in the tracker before advancing. **One fragment per turn:** the sub-skill stops at each gate. The executor never emits two fragments in one turn.

### Step 6 -- Backtracking and iteration (the flow is not forward-only)

Recon is iterative: reading R2's flows often reveals R1 missed an entry point; reconstructing R3's intent often sends you back to R2 for a flow you skimmed. The router handles going *back*, governed by one rule:

> **Reopen rule.** Reopening gate `Rn`:
> (a) marks **`Rn` itself** back to `[ ]` pending -- the fragment file on disk is retained as the `(iter N)` reference (rename or annotate per FLOW.md "Iteration patterns"); a fresh fragment is produced on the next pass;
> (b) marks every downstream gate that consumed `Rn`'s output back to `[ ]` pending (stale, not deleted);
> (c) moves the **`Current step:` line** in `FLOW.md §Current session` back to `Rn`.
>
> When the operator triggers the reopen (a UI action, a `/reopen`, or a direct `FLOW.md` edit flipping `[x]` to `[ ]`), apply (a)-(c) **without re-prompting** -- the reopen action is the consent. Forward motion then re-traverses every stale gate in order; you cannot jump from `Rn` straight to the front.

Two cases:

1. **Gate rejection (no cascade).** The operator rejects the fragment at the current gate. Mark it `[i] iterating`; the executor re-works that one fragment. Nothing downstream exists yet, so there is no cascade.
2. **Upstream ripple (cascade).** A later gate reveals an earlier fragment is wrong (R3 finds R1 missed a whole data store; R4 finds R2 mis-read a flow). Apply the reopen rule from the *earliest* affected gate: reopen R1 -> R2/R3/R4 go `[ ]` -> cursor moves to R1 -> re-walk forward.

The states `[i] iterating` and `[!] blocked` exist for exactly this. The router keeps the tracker honest so "we went back to R1" is recorded state, not something the operator must remember.

### Gate state machine (canonical)

The gate tracker is a state machine **two parties** write to. This table is the single source of truth for which transition belongs to whom.

| FROM | TO | Owner | Trigger | Side-effects |
|---|---|---|---|---|
| `[ ]` | `[~]` | **executor** | sub-skill starts producing the fragment | mark in_progress |
| `[~]` | `[?]` | **executor** | fragment emitted; parking at the gate | await operator review |
| `[?]` | `[x]` | **orchestrator** | operator approves | stamp `approved-on` date; advance `Current step:` to the next gate |
| `[?]` or `[~]` | `[i]` | **orchestrator** | operator requests changes | hold; the executor resumes the iteration |
| `[i]` | `[~]` | **executor** | re-entering the gate to iterate | mark in_progress again |
| `[x]` | `[ ]` | **orchestrator** | reopen (UI button / `/reopen` / manual `[x]`->`[ ]` edit) | preserve the fragment as `Rn.iter-N.md`; cascade every downstream gate that consumed Rn's output to `[ ]` (stale, not deleted); move `Current step:` back to Rn; the reopen action **is** the consent -- do NOT re-prompt |
| `[ ]` <-> `[!]` | -- | **orchestrator** | block / unblock | record the blocker |

**Reading the table.**

- **Disk is the source of truth.** When the orchestrator (a UI, a `/reopen`, a manual edit) has already mutated `FLOW.md`, the executor **trusts disk and does NOT re-mutate**. Its job is to **react** -- route to the next sub-skill, re-emit the iterated fragment, or run the auditor.
- **Producer transitions apply after a reopen.** Orchestrator-owned `[x]`->`[ ]` does NOT carry the executor's `[ ]`->`[~]`->`[?]` -- those still belong to the executor. Skipping them (leaving the gate `[ ]` while a fresh fragment sits on disk) is the most common post-reopen mistake.
- **Tracker coherence (RE-05, NON-NEGOTIABLE).** Three invariants at every read: contiguous `[x]` chain; active gates have approved priors; at most one active gate. Any violation -> Step 1 refuses to advance.

### Subagent orchestration

When invoked from an orchestrator UI (ADDL / `ui-sad` / equivalent), the router parent **SHOULD** delegate gate production to an `Agent` tool subagent rather than producing the fragment in its own context:

| Role / `subagent_type` | Spawned when |
|---|---|
| `Reverse-Engineer` | Parent transitions the gate `[ ]` -> `[~]` and dispatches. Produces the gate's fragment (R1, R2, R3, R4). |
| `Reverse-Engineer-Auditor` | After the `Reverse-Engineer` subagent returns; before the parent transitions `[~]` -> `[?]`. Runs `recon-auditor` against the just-emitted fragment. |

**Binding to the Agent tool.** When the orchestrator UI exposes a custom-agent registry (`.claude/agents/<Name>.md`), the parent **MUST** invoke each subagent with `subagent_type` set to the role name verbatim (`Reverse-Engineer`, `Reverse-Engineer-Auditor`) -- not `general-purpose` with the role in the `description`. The role-namespaced labels are identifier-typed; the `description` field carries the per-gate task (gate id + sub-skill + target path), not the role. Reference templates for the two agent files live under `agents/` in this skill; orchestrator UIs install them into the active workspace's `.claude/agents/` before the parent's first turn (static discovery at startup). When no registry is available (manual CLI session), this binding is advisory and the parent falls back to the single-LLM topology.

The parent's writes are limited to `FLOW.md` Gate tracker mutations (`[ ]`->`[~]`, `[~]`->`[?]`) and, after a reopen, renaming the prior fragment to `Rn.iter-N.md` before spawning the new `Reverse-Engineer`. The parent does **NOT** write fragment content or audit content directly. The role prefix (`Reverse-Engineer` / `Reverse-Engineer-Auditor`) prevents `subagent_type` collision when recon and SAD (`Architect` / `Architect-Auditor`) agents coexist in the same parent session.

### Running as a single LLM (default today)

With no UI and no `Agent` tool (a manual CLI session), the router, executor, and auditor are all the one LLM navigating these documents: read the tracker, report position, read the sub-skill `SKILL.md`, produce the one fragment, stop at the gate, run the auditor read against it, present, and on approval mark `[x]` and advance. The human gate stays between every fragment. The canonical gate machine and RE-05 still apply.

---

## The drift loop -- keeping the architecture honest over time

The most durable value of recon is not the first onboarding pass; it is **drift detection**. Once a SAD exists (whether authored fresh or via a recon handoff), the code keeps moving and the SAD goes stale. `recon-auditor` in **diff mode** re-runs recon over the evolved code and diffs the new observations against the prior SAD/recon: which entry points are new, which data stores moved, which stressors materialized, where the documented architecture no longer matches the running one. Output: `audit-drift-<ref>.md`. This converts "the docs are out of date" from a vague worry into an anchored, dated report of exactly what changed and where the SAD is now lying. Findings are **advisory** -- the operator decides whether the drift warrants reopening a SAD gate.

---

## The doctrine -- constitution RE-01 to RE-05

The full rule set lives in `shared/constitution.md` (canonical). Each sub-skill cites by `RE-NN`.

| Rule | Scope | Mechanism | Defends |
|---|---|---|---|
| **RE-01** Evidence anchoring | R1, R2, R3, R4 | both | Against confident fabrication -- every claim falsifiable on disk (`file:line` / commit, or `⚠ unverified`); documentation is a lead ranked below code, with declared-but-unbuilt items kept as `⚑ declared (not observed)` (§6) |
| **RE-02** Inferred intent, labelled | R3 | both | Against deduction dressed as fact -- intent carries confidence + evidence |
| **RE-03** Descriptive, not prescriptive | R1, R2, R4 | heuristic | The SAD's naïve baseline + empirical Ri test -- recon is a mirror, never a redesign |
| **RE-04** Observed stressors only | R4 | both | The signal only recon can supply -- stress this specific system has shown; speculation segregated |
| **RE-05** Tracker & workspace coherence | Router, all gates | deterministic | One-fragment-then-STOP as a state invariant (mirror of SAD R-26) + recon writes only under `docs/reverse-engineer/`, never the SAD's `docs/architecture/` |

---

## Doctrine: mechanical determinism

This is an **authoring / meta discipline** -- distinct from the RE-01..RE-05 *fragment* rules above
(which a produced fragment is audited against, and which stay deliberately five). It governs how the
skill's own steps and checks are *built*: when a step is mechanical, prefer code over prose. The
in-repo exemplar is the auditor's two RE-01 mechanical checks, which call
`tools/check-anchors.py` (tested by `tools/test-check-anchors.py`) rather than asking the LLM to
eyeball whether a cited line exists or whether its content matches the claim. (Both *violations* --
a line past EOF, and a `~ token` snippet not on its cited line -- hard-fail with a non-zero exit;
its `warn` rows are reserved for explicit *non*-violations, like prose tokens such as `node:20`,
precisely so a real violation never degrades into something read past.) The snippet check (0.1.4)
is the canonical case for *moving* work across the seam: the off-by-one false anchor -- the line
exists but proves the wrong fact -- was heuristic prose until the producer began pinning the proof
with a literal token, at which point it became mechanically decidable and was promoted to a
hard-failing script check.

The second exemplar is `tools/repo-census.py` (0.1.6), which draws the determinism boundary in the
sharpest place: **enumerating and typing every file** is mechanical and exhaustive -- a script does
it, so no file is lost because no human chose the list -- while **interpreting what each file means**
is judgement and stays with the R1 producer. Census = script; cartography = LLM; never the reverse,
because a script that inferred the architecture from file contents would be the very confabulation
recon exists to prevent. Its `coverage` mode makes "no information in the repo is discarded" a
hard-failing check, the way `check-anchors.py` makes "every anchor resolves" one.

The third exemplar is `tools/check-counts.py` (0.1.7): a count claim ("grep → 21 hits") is anchored
to a command, but the *number* is prose the producer types and can get wrong -- twice it did ("11
actor types" for 10, "22" for 21). Re-running a deterministic read-only command and comparing its
output is mechanical, so it is a script: the producer emits the claim as a ```` ```verify ```` block
(command + output) and the tool re-runs it (whitelisted, no shell) and hard-fails on a mismatch.
Deciding *which* command proves a claim stays judgement; re-running it does not. This is the count
analogue of what the snippet check did for line numbers -- and a reminder that the seam keeps moving
as more of "trust me" becomes "re-run it".

The fourth exemplar is `tools/check-workspace.py` (0.1.9): when the recon flow moved out of
`docs/architecture/` into its own role folder `docs/reverse-engineer/` (0.1.8), *which folder each
artifact belongs in* was left as prose -- restated across ~11 files and guarded only by the hope that
the producing subagent would not "correct" the path back. Which directory owns `FLOW.md` or
`audit-iter-N.md` is a simple, binary fact with no judgement, so it is a script, not a sentence: the
tool walks `docs/` and hard-fails on any recon-owned artifact that is not under `docs/reverse-engineer/`
(a file leaked into the SAD's `docs/architecture/` collides by name with the SAD deliverable). It is
the workspace analogue of the same seam -- a folder rule made executable rather than promised.

The fifth exemplar (0.1.10) turns the seam on *itself*: `evals/run-evals.py` adds no new check -- it
makes "the four checks actually catch the regressions they exist for" a hard-failing fact. It stands up
one clean R1 fixture that passes all four validators, then injects each false-anchor class in isolation
(past-EOF, off-by-one snippet, count drift, uncovered file, misplaced workspace artifact) and asserts the
matching validator flips to a non-zero exit. "Does our determinism still detect the bug it was built for?"
is itself mechanical and deterministic, so it is a tested script wired into the packager's self-test gate,
not a claim in a changelog. The model-driven half (R1-R4 routing / gate discipline) cannot be made
deterministic and stays prose, run by hand from `evals/recon-prompts.md`.

When a step is **mechanical and deterministic** -- the same input always
yields the same output and no judgement is involved (e.g. sanitizing or
transforming text, counting, format/lint checks, schema or ID validation) --
do NOT perform it in LLM prose. Encode it as a tested pure function or script
and invoke that. The check must **hard-fail** on violation (a non-zero exit or
a raised error), never a warning that can be read past.

This does NOT apply to heuristic or judgement work (design, interpretation,
ranking, writing) or to one-off trivia. Only mechanical, deterministic steps.

**Why.** LLM prose is non-deterministic and drifts silently between runs. A
prose instruction like "do not skip X" is unenforceable; a script that exits
non-zero when X is present is. Codified checks run identically every time and
can be re-run to prove correctness.

**How to apply.**
1. Before doing a repetitive check or transform by hand, ask: is the output
   fully determined by the input, with no judgement?
2. If yes, author (or call) a script / pure function for it, with a test and a
   hard-fail failure mode. Reference the script from the skill; do not inline
   the logic as prose steps.
3. If it needs judgement, or is genuinely one-off, leave it as prose -- do not
   over-engineer.

---

## The output -- the three planes (Phase-0 evidence for the SAD)

R1..R4, once approved, map directly onto the three planes the SAD's "When a prior implementation exists" mode accepts:

- **Business framing** (from R3) -> SAD **S1a** (`business-discovery`). The inferred objective / users / pain points / goals, each with confidence (RE-02).
- **As-built audit** (from R1 + R2 + R4's IDesign typing) -> a **residual candidate** the SAD's **S6** measures against the naïve baseline. Never the baseline itself (RE-03).
- **Observed stressors** (from R4) -> held for SAD **S3** (`stressor-analysis`), clearly separated from anticipated ones (RE-04).

The optional `handoff-assembler` packages these into a single `phase0-evidence.md` with the three sections labelled (`## Business framing -> S1a`, `## As-built audit -> S6 evidence`, `## Observed stressors -> S3`) for direct copy-paste into a new SAD project. The operator then opens a SAD project, chooses entry mode **β** (fresh SAD, existing impl as S6 evidence) or **γ** (SAD for the next phase), and S1a..S7 runs unchanged. The SAD is never patched.

---

## Per-project workspace convention

When running on a real target, fragments are produced in `<target-root>/docs/reverse-engineer/` -- the recon role's own folder, which ADDL lists alongside the SAD's `docs/architecture/`. The `FLOW.md` gate tracker lives there too. Audit reports go to `<target-root>/docs/reverse-engineer/audit-iter-N.md` (by-gate / end-to-end) and `audit-drift-<ref>.md` (diff mode). Recon **reads** the whole target repo but **writes** only under `docs/reverse-engineer/` -- it never mutates the target's source, and it never writes into `docs/architecture/` (that tree is the SAD deliverable's).

---

## When NOT to invoke this skill

- The project is **greenfield** -- there is no existing implementation to read. Use the SAD directly from the PRD/SRD (`sad-*`). Recon has nothing to reconstruct from.
- A PRD/SRD already exists and is current. Recon's job is to *generate* the business framing from code when no document exists; if the document exists, take it to the SAD's S1a directly.
- The operator wants a **redesign, refactor plan, or "better" architecture**. That is the SAD's job (and RE-03 forbids recon from doing it). Recon describes what is; route forward to the SAD for what should be.
- A line-level **code review or bug hunt**. Recon reconstructs architecture-level understanding, not defect-level review. Route to general engineering tooling or `/code-review`.

If the operator is unsure whether their context warrants it: a system that *exists and runs but is poorly understood* is exactly recon's case. Recon can also be used partially -- stop after R1+R2 if all you need is a system map, without reconstructing business intent.

---

## References

- `shared/constitution.md` -- the 5 active rules (RE-01 to RE-05).
- `shared/evidence-anchoring.md` -- the how-to for anchoring, confidence calibration, the `⚠ unverified` quarantine, and **§6 documentation as evidence** (the completeness sweep, doc-vs-code ranking, and the `⚑ declared (not observed)` milestone). Read before producing any fragment.
- `shared/glossary.md` -- vocabulary (residual candidate, observed stressor, the three planes, gate, fragment, drift).
- `recon/system-cartography/SKILL.md` (R1), `recon/behavior-reconstruction/SKILL.md` (R2), `recon/business-reconstruction/SKILL.md` (R3), `recon/asbuilt-stressors/SKILL.md` (R4) -- the four sequential producers.
- `recon/recon-auditor/SKILL.md` -- the cross-cutting auditor (by-gate | end-to-end | diff).
- `recon/handoff-assembler/SKILL.md` -- optional; packages the three planes into `phase0-evidence.md`.
- `templates/` -- the fragment templates each producer fills.
- `tools/check-anchors.py` -- deterministic anchor validator (flags cited lines past a file's end, and `~ token` snippets not on their cited line); run by the `recon-auditor`'s two RE-01 mechanical checks.
- `tools/repo-census.py` -- deterministic file census + typed inventory (R1 Step 0) and the `coverage` "nothing is lost" check; run by the `recon-auditor`'s RE-01 census-coverage check.
- `tools/check-counts.py` -- re-runs every ```` ```verify ```` block's count command (whitelisted, no shell) and hard-fails on a mismatch; run by the `recon-auditor`'s RE-01 count-verification check.
- `tools/check-workspace.py` -- deterministic workspace-placement validator; walks `docs/` and hard-fails on any recon-owned artifact not under `docs/reverse-engineer/` (a recon file leaked into the SAD's `docs/architecture/`); run by the `recon-auditor`'s RE-05 workspace check.
- `agents/Reverse-Engineer.md`, `agents/Reverse-Engineer-Auditor.md` -- the two subagent role templates ADDL installs into the workspace `.claude/agents/`.
- `sad-*/SKILL.md` -- the downstream consumer; its "When a prior implementation exists (Phase-0 as evidence)" mode is recon's reception socket.

---

## Changelog

- **0.1.10** -- Eval harness (no new RE rule, no new validator; the mechanical-determinism seam turned
  on itself). New shipped `evals/` package: **`evals/run-evals.py`**, a deterministic false-anchor
  **mutation harness** that stands up one clean R1 fixture passing all four validators, then injects
  each regression class in isolation (past-EOF anchor, off-by-one snippet, count drift, uncovered file,
  misplaced workspace artifact) and asserts the matching validator hard-fails -- proving the determinism
  still catches the bug it was built for (offline, `--no-git`). Plus **`evals/recon-prompts.md`** (the
  model-driven R1-R4 routing / gate-discipline eval, run by hand) and `evals/README.md`. The packager
  self-test gate (`scripts/package_skill.py`) now also runs `evals/run-evals.py` when present, so the
  bundle can never ship with a red eval layer. SKILL.md gains a fifth mechanical-determinism exemplar.
- **0.1.9** -- Workspace placement made deterministic (closes what 0.1.8 left implicit). The 0.1.8
  relocation moved the recon flow into `docs/reverse-engineer/` but left *which folder owns each
  artifact* as **prose** -- restated across ~11 files and guarded only by the hope that the
  Reverse-Engineer subagent "does not correct the path back to `docs/architecture/`". A folder rule is
  mechanical and binary, so per §"Doctrine: mechanical determinism" it must be a tested, hard-failing
  script, not a sentence. **New tool `tools/check-workspace.py`** (+ `tools/test-check-workspace.py`):
  it walks `docs/` and hard-fails (`MISPLACED`, exit 1) on any recon-owned artifact (`FLOW.md`, the
  four R1-R4 fragments, `r1-inventory.json`, `audit-iter-N.md` / `audit-drift-<ref>.md`,
  `phase0-evidence.md`) that is not under `docs/reverse-engineer/` -- the canonical violation being a
  recon file leaked into the SAD's `docs/architecture/`, where it collides by name. The SAD's own
  files there are ignored. **RE-05** is broadened from *tracker coherence* to *tracker & workspace
  coherence* (both deterministic, both ALWAYS run); the auditor gains a 17th check
  (`recon-auditor` Consolidated count 16 -> 17). No new RE rule, no flag -- the existing structural-
  coherence rule now also pins the folder.
- **0.1.8** -- Workspace relocation (layout only; no rule, no flag): the **entire recon flow** --
  `FLOW.md` tracker, the four R1-R4 fragments, and the audit reports -- moves out of
  `docs/architecture/` into the recon role's own folder **`docs/reverse-engineer/`**. The driver:
  ADDL runs one lifecycle role per phase, each writing under `docs/`; sharing `docs/architecture/`
  with the SAD collided by name (`FLOW.md`, `audit-iter-N.md`). The rule now is uniform across roles
  -- **only the SAD deliverable** lives in `docs/architecture/`; everything else is per-role under
  `docs/<role>/`. Recon has no architecture deliverable of its own (its fragments are work-product
  evidence; only `phase0-evidence.md` crosses to a downstream SAD, and it does so by path, not by
  location), so it never writes into `docs/architecture/`. ADDL lists `docs/reverse-engineer/`
  alongside `docs/architecture/` so the operator sees both. This realigns the skill text so the
  Reverse-Engineer subagent does not "correct" the path back to `docs/architecture/`.
- **0.1.7** -- Count-claim verification: close the enumeration blind spot (RE-01 sharpening +
  mechanical determinism; no new rule). A count claim ("grep → 21 hits", "5 registrations", "11
  `Type()` strings") is anchored to a command but the **number is prose** the producer types -- and it
  drifts: R1 wrote "11 actor types" for 10 (0.1.3) and "22" for 21 (0.1.6 E2E), each caught only by a
  human re-running the grep. The snippet check (0.1.4) pins a *line's* content, the census (0.1.6) pins
  *file coverage* -- neither re-runs a tally. **New tool `tools/check-counts.py`** (+ test): the
  producer emits each count as a fenced ```` ```verify ```` block (command + verbatim output), and the
  tool **re-runs** the command (read-only whitelist — `grep`/`find`/`wc`/`git ls-files`/`git log`/… ,
  pipes only, **no shell**, no writes, no network) and hard-fails on any mismatch. Safety is the design
  centre: pipelines are shlex-tokenized and run as an argv `Popen` chain (`shell=False`), so
  redirections / `;` / `$(…)` can never execute; a non-whitelisted command is warned, never run.
  **evidence-anchoring §1** makes the `verify` block mandatory for count claims; **R1** emits its
  entry-point + actor tallies as `verify` blocks; **recon-auditor** adds the count check (15 → 16);
  constitution RE-01 (v1.3), glossary (v1.2), root SKILL (3rd determinism exemplar), FLOW, README,
  CLAUDE.md. Validated on the exact 0.1.6 actor-count miss: the true 21/10 re-verify clean, the false
  22 hard-fails.
- **0.1.6** -- Mechanical, exhaustive R1 file census + typed inventory (RE-01 sharpening + mechanical
  determinism; no new rule). The 0.1.5 completeness sweep was still LLM prose (run `find`, eyeball);
  enumerating + typing every file is mechanical and deterministic, so it becomes a tested script.
  **New tool `tools/repo-census.py`** (+ `tools/test-repo-census.py`): `census` enumerates
  `git ls-files` + untracked-not-ignored (deps / build caches excluded by a fixed list) and tags each
  file by type (`source:<lang>`, `test`, `config`, `docs`, `build-ci`, `iac-deploy`,
  `schema-migration`, `asset-binary`, `generated-lock`, and **`unclassified`** -- the safety net);
  `coverage` checks every censused file is accounted for in R1 and hard-fails on any uncovered file.
  **R1** gains **Step 0** (run the census → `r1-inventory.json`, the trackable typed worklist) and a
  `## Census coverage` section; the census *enumerates and types*, the producer *interprets* (the
  determinism boundary -- a script never infers the architecture). **recon-auditor** gains a
  deterministic census-coverage check (count 14 → 15). From the operator's dogfooding insight:
  mechanical tasks are scripts, not prose; nothing in the analyzed repo can be lost. Validated on the
  market-trading repos -- the census surfaces the source-less `feature` binary and a stray runtime log
  that a hand-picked file list missed.
- **0.1.5** -- Documentation as a weaker evidence class + the declared-not-built milestone (RE-01
  sharpening, no new rule). The premise "there is no documentation" is replaced by: a brownfield
  often *does* carry docs (README, `CLAUDE.md`/`AGENTS.md`, `docs/**`, `*.puml`, `*.http`), **no
  information in the repo is discarded -- all of it is valuable**, but documentation is a **lead**
  and code is the **proof** (docs go stale). Every doc-sourced claim resolves into one of three
  states: **confirmed** (doc + code → observed), **`⚑ declared (not observed)`** (doc declares it,
  code lacks it → a first-class, segregated *milestone*, anchored to the declaring doc + the
  confirmed absence, never dropped, for downstream to keep or cut), or **drift** (doc contradicts
  code). A **completeness sweep** (enumerate every doc artifact with a command + count, account for
  each) makes coverage auditable. **Where it lands:** `evidence-anchoring.md` §6 (new) + the
  `⚑` mark; `constitution.md` RE-01 body/verification (v1.2); `glossary.md` (v1.1; doc-vs-code
  anchor, `⚑`, completeness sweep); **R2** gains the documentation sweep (Step 1) + a
  `## Declared use cases (not observed)` section (Step 7) -- it had been citing the repo's 9 actor
  docs + 8 `.puml` sequence diagrams zero times; **R1** sweeps docs as corroboration (doc-only
  structural claim → `⚑`); **R3** treats declared-not-built as a strong *intent* signal under RE-02;
  **recon-auditor** adds 2 checks (count 12 → 14): a deterministic documentation check (sweep
  present + no doc-only audit claim + `⚑` segregation) and a heuristic genuineness/coverage check.
  From dogfooding the 2026-06-17 market-trading run, where the use-case plane (R2) ignored the
  richest functional content in the repo and the README's declared (unbuilt) automation pipeline
  was nearly lost.
- **0.1.4** -- RE-01 deterministic content check (no new rule). **Producer:** `evidence-anchoring.md`
  adds the `path:line ~ token` **snippet** anchor form -- pin each line-number with the literal text
  that proves the claim; `system-cartography` (R1) now makes it MANDATORY in multi-fact inventory
  cells and across sibling-file families (the dense-anchor sites). **Auditor:** `tools/check-anchors.py`
  gains a second deterministic check -- snippet-on-line -- so the **off-by-one false anchor** (the
  cited line exists but proves the wrong fact: `dapr.yaml:18` for a credential on line 17,
  `gateway/package.json:5` for `"type":"module"` on line 4) hard-fails mechanically with an
  off-by-one finger-point, instead of depending on a fallible heuristic read. This moves recon's
  highest-frequency false anchor across the deterministic/heuristic seam; the heuristic false-anchor
  walk now spends judgment only on *unsnippeted* anchors. Auditor check count 11 -> 12;
  `check-anchors.py` test count grows to cover the new path. From the 2026-06-17 market-trading R1
  re-audits, where off-by-one content false anchors forced three iterations -- one was wrongly
  cleared by the auditor "by analogy" without opening the line, the exact failure the snippet
  forecloses.
- **0.1.3** -- RE-01 sharpening (no new rule). **Producer:** `evidence-anchoring.md` + the
  `system-cartography` template now require **one anchor per fact** (pair each fact with its line
  inline -- no bare comma-list cells) and **no sibling-file line reuse** (re-walk web/ vs gateway/
  package.json + Dockerfile). **Auditor:** the RE-01 false-anchor check is split along the
  deterministic/heuristic seam -- a new **deterministic** sub-check runs `tools/check-anchors.py` to
  flag any cited line **past its file's end** (mechanical, exhaustive, script-backed), and the
  **heuristic** spot-check now walks **every** line of a multi-fact cell (not a sample) and re-verifies
  the whole sibling-file family when one anchor is wrong. Adds the `tools/check-anchors.py` validator
  (+ `tools/test-check-anchors.py`; 11 auditor checks total). From the 2026-06-16 market-trading R1 audit, where 5 same-shaped false
  anchors in the two inventory table sections survived an iteration (one was a past-EOF `:42` now
  caught deterministically; 2 missed by the spot-check, 1 wrongly cleared).
- **0.1.2** -- R3 (`business-reconstruction`): add the operator-triggered **Open-question resolution
  pass** -- the Reverse-Engineer re-investigates each §Open question and either resolves it with a
  file:line/commit anchor or marks it stakeholder-required; never fabricates an answer (RE-01/RE-02).
  No new rule, no breaking change.
- **0.1.1** -- RE-02: promote the R3 confidence-summary tally check from heuristic to deterministic
  in `recon-auditor`; `business-reconstruction` Step 8 now computes the tally from the rows. No new
  rule, no breaking change. (From the 2026-06-14 R3 smoke test, finding H1.)
