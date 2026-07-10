---
name: behavior-reconstruction
description: Sub-skill of the `recon` meta-skill. Produces the `behavior-reconstruction.md` fragment -- the use cases / flows the system observably runs, traced from R1's entry points through handlers, jobs, schedulers, and tests, every flow anchored to `file:line` along its call path. Invoke as gate R2, only after R1 (`system-cartography`) is `[x] approved`; refuse if R1 is not approved.
task_types: [behavior-reconstruction, flow-analysis, reverse-engineer, observed-use-cases]
shared_refs:
  - ../../shared/constitution.md
  - ../../shared/evidence-anchoring.md
  - ../../shared/glossary.md
  - ../../templates/behavior-reconstruction.md
---

# behavior-reconstruction (R2)

Second sub-skill of the meta-skill, and the second of the four sequential producers. It turns R1's **static inventory** (entry points, services/modules, data stores, integrations) into **observed behavior**: the use cases and flows the system actually runs. A flow starts at one of R1's entry points and follows the call chain -- handler to service to repository to store -- until it reaches its **effects**: rows written, events emitted, external calls made. R1 told you the parts; R2 tells you what the parts *do* when the system runs. The fragment fills the SAD's *audit* plane alongside R1.

Tests are **first-class evidence** here, not an afterthought. The production path often only implies a behavior (a branch reached through dynamic dispatch, an error case wired through middleware); a test that exercises that path encodes the intended behavior *explicitly* and is a re-checkable anchor (`tests/...:NN`) just like a `file:line`. The golden rule of R1 carries straight through (RE-01): **anchor every step of every flow**, along its call path -- an unanchored flow is the classic confabulation (narrating an event-driven saga from an unused stub). And R2 is **descriptive, never prescriptive** (RE-03): describe what the system *does*, never what it *should* do. No "this flow should be split", no renamed handlers, no proposed retries. Record the behavior with anchors and stop; the redesign is the SAD's job, downstream.

**Documentation is a goldmine of use cases -- but a lead, not a proof (RE-01 §6).** Real brownfields carry READMEs, `CLAUDE.md` / `AGENTS.md`, `docs/**`, and especially `*.puml` sequence diagrams and `*.http` request specs -- which are *literally* use-case specifications. R2 mines **all** of them (no information in the repo is discarded), but documentation declares what the authors *say* happens, and the code is the source of truth. So every declared flow resolves into one of two outcomes: **confirmed** against a handler/test → it enters as an **observed** flow (the diagram was the lead, the code is the proof); or **declared with no implementing code** → it is captured as **`⚑ declared (not observed)`** in its own section -- an intended-but-unbuilt use case (a milestone), never mixed into observed flows and never dropped, because losing sight of an intended capability is worse than carrying one a stakeholder may later cut. (Where a doc *contradicts* the code, state what the code does and note the discrepancy.)

---

## When to invoke

- R1 (`system-cartography`) is `[x] approved` and the operator wants to know **what the system actually does** -- the use cases / flows it observably runs.
- The request is "map the flows", "trace what happens when X is called", "reconstruct the behavior / use cases", "follow the request from the endpoint to the database".
- You have R1's entry points in hand and need to walk each one through the call chain to its effects.

## When NOT to invoke

- **R1 is not yet approved.** R2 seeds its flows from R1's entry points; without an approved inventory there is nothing to trace from. Route back to R1 (refuse -- see Pre-conditions).
- The operator asks to **redesign, optimize, or "fix" a flow** (add a queue, split a handler, propose retries). That is prescriptive -- RE-03 forbids it. Recon describes; the SAD prescribes. Route forward to the SAD.
- The project is **greenfield** -- there is no running system whose behavior can be observed. There is nothing to reconstruct.
- A line-level **bug hunt or code review** of a single flow. R2 reconstructs architecture-level behavior, not defect-level review.

## Pre-conditions

**Requires gate R1 (`system-cartography.md`) `[x] approved`** in the `FLOW.md` gate tracker. This is enforced per the root `SKILL.md` §Gate approval protocol: **verify the tracker, not just the file's existence.** A `system-cartography.md` can sit on disk while R1 is still `[?] awaiting review` or `[i] iterating`; producing R2 on top of an unapproved R1 is the premature-advance error RE-05 exists to prevent.

Before producing the fragment:

1. Read the gate tracker (`FLOW.md` §Current session). Confirm **R1 is `[x] approved`**.
2. Confirm the R1 fragment exists on disk (disk wins -- a gate marked `[x]` whose fragment is absent is degraded to `[ ]`; you cannot build R2 on a missing R1).
3. If R1 is not `[x] approved`, **refuse** (Refusal #1) and point the operator at the open R1 gate. R2 has exactly one prior gate; it is never the entry.

## Handoff contract

Runtime-agnostic interface (single-LLM reads these; an agent passes them as message payload):

- **Consumes:** the approved `system-cartography.md` (R1) and its **carry-forward notes** -- specifically R1's **entry points** (HTTP routes, CLI verbs, queue consumers, scheduled jobs, startup hooks) which become R2's flow seeds, and R1's **dense-logic seeds** (modules R1 flagged as hot or logic-heavy) which tell R2 where the significant flows likely run.
- **Produces:** `behavior-reconstruction.md` behind gate **R2** (per `templates/behavior-reconstruction.md`). One fragment, then STOP for human review.
- **Carry-forward context (lateral, for downstream gates):**
  - **Convergence points** -- which modules many flows pass through (shared handlers, common middleware, a single repository). A pointer for **R4** coupling/contagion analysis: a module on every flow's path is a coupling candidate.
  - **Domain-dense flows** -- which flows encode the most business logic (pricing, eligibility, state machines). A **seed for R3** intent reconstruction: the flow that does the most domain work is where the business objective is most legible.

---

## Workflow

All steps are **READ-ONLY**. R2 reads the whole target repo but writes only the one fragment under `docs/reverse-engineer/`. It never mutates the target's source.

### Step 1 -- Gather flow seeds: R1's entry points AND a documentation sweep

Two seed sources, both swept to completeness:

1. **R1's entry points.** Read the approved `system-cartography.md`. Every entry point R1 inventoried (route, CLI verb, consumer, scheduler, startup hook) is a candidate flow; order by importance as R1 ranked them. A flow with a real entry point but absent from R1 is either an entry point R1 missed (a sign R1 needs reopening -- Step 6) or not a flow.
2. **Declared flows from a documentation sweep (RE-01 §6).** Enumerate **every** information-bearing artifact -- READMEs, `CLAUDE.md` / `AGENTS.md`, `docs/**`, `*.puml` sequence diagrams, `*.http` request specs, intent-bearing comments -- and **state the command + count** so coverage is auditable and nothing escapes:

   ```bash
   find . -type f \( -name '*.md' -o -name '*.puml' -o -name '*.http' -o -name 'AGENTS*' \) \
     -not -path '*/node_modules/*' -not -path '*/.git/*' | sort   # then | wc -l for the count
   ```

   Read each one and extract every **declared use case / flow** it describes -- a `.puml` sequence diagram and a README "Critical Flows" list are use-case specs. These declared flows are candidates to **confirm against code** in Step 2; a declared flow with no implementing code becomes `⚑ declared (not observed)` (Step 7). The documentation is the lead; the code is the proof. *No artifact is skipped -- each is mined or explicitly noted as carrying nothing new.*

### Step 2 -- Trace each significant flow's call chain, anchoring each hop

For each significant flow, follow the call chain **step by step from the entry point to its effects**, and anchor every hop:

```
EntryHandler (file:line) -> Service.Method (file:line) -> Repository.Save (file:line) -> data store
```

Then record the **effects** -- rows written, events emitted, external calls made -- each anchored. You read every line you cite (RE-01: an anchor that lands near the claim but not on it is a *false anchor*, worse than none). Describe what the chain does; do not judge whether it is well-built (RE-03). Use the names the code uses, even bad ones -- renaming is a design act.

A flow **declared in the documentation** (Step 1's sweep) that you confirm here against a real handler/test enters as an **observed** flow -- cite the code anchor (the declaring doc may be cited too, as the lead). A declared flow you **cannot** find implementing code for is not forced into this section: it is held for Step 7 as `⚑ declared (not observed)`.

### Step 3 -- Capture background / scheduled / event-driven behavior

Flows not triggered by a synchronous request are still behavior: cron jobs, queue/topic consumers, timers, startup/shutdown hooks, background workers. For each, anchor both the **trigger** (the schedule expression, the subscription registration) and the **handler** (`file:line`). These are exactly the flows a request-only reading misses, and they often carry the highest-value domain logic (a nightly reconciliation, a lapsed-user mailer).

### Step 4 -- Mine the test suite for behavior the production path only implies

The test suite is evidence (RE-01). Where a behavior is reachable only through dynamic dispatch, a config branch, or an error path the production code wires indirectly, a test that exercises it **encodes the intended behavior explicitly** and anchors it (`tests/...:NN`). Record behavior the tests assert that the production path only implies. Note the inverse too: a significant flow with **no test** is itself a finding (absence of a test is a fact worth stating, not a redesign recommendation).

### Step 5 -- Note cross-flow convergence points

Record where flows **converge on the same module** -- a shared handler, common middleware (auth, logging, transaction wrapping), a single repository many flows write through. Descriptive only. This is the carry-forward pointer for R4: a module on the path of many flows is a coupling candidate R4 will measure.

### Step 6 -- Record gaps and `⚠ unverified`

Quarantine, do not silently drop:

- Flows that depend on **runtime config, external state, or dynamic dispatch** you could not resolve statically from the repo -- mark `⚠ unverified` and name the missing anchor (e.g. "handler bound by reflection from a config key not in the repo").
- **Entry points R1 listed for which no handler logic could be located.** This is a signal that **R1 may need reopening** (an entry point with no handler is either dead or mis-inventoried). Flag it explicitly; the operator decides whether to trigger the reopen (root `SKILL.md` §Backtracking).

A fragment dominated by `⚠ unverified` rows did not actually ground in the code -- go read more before parking the gate (the auditor reports that ratio).

### Step 7 -- Classify declared-but-unbuilt use cases (`⚑ declared (not observed)`)

Take every **declared flow** from Step 1's documentation sweep that Step 2 could **not** confirm against implementing code, and record it in the dedicated `## Declared use cases (not observed)` section -- never in the observed-flows section, never silently dropped (RE-01 §6). For each, anchor **both** sides: the **doc that declares it** (`README.md:NN`, a `.puml`, an `.http`) **and** the **confirmed absence in code** (the grep that returns no consumer, the missing handler, the source-less binary). This is the intended-but-unbuilt **milestone** -- captured so the operator and the downstream SAD can choose to keep or cut it, with eyes open. Distinguish it from a *contradiction* (doc says X, code does Y): a contradiction is recorded as an observed flow (what the code does) plus a noted discrepancy. A declared use case is `⚑`, not `⚠ unverified` -- it is positively anchored on both the declaration and the absence, not an un-anchored guess.

> Worth carrying because it is exactly what a use-case listing downstream must not lose: if it later proves out of scope it is dropped in one line, but if it is the team's actual roadmap it is the most valuable thing the docs hold.

### Step 8 -- STOP at gate R2

After writing `behavior-reconstruction.md`, **stop**. Present it, run `recon-auditor` `by-gate` (RE-01 anchor check across every flow hop; RE-03 prescription check), and mark gate **R2** `[?] awaiting review`. Do NOT begin R3 (`business-reconstruction`). One fragment per turn; the human gate stays between every fragment (RE-05).

---

## Output contract

One fragment file, `behavior-reconstruction.md`, in the project workspace (`<target-root>/docs/reverse-engineer/`), per `templates/behavior-reconstruction.md`:

- `## Observed use cases / flows` -- one subsection per significant flow, each with **Trigger/entry**, the step-by-step anchored **Path**, the anchored **Effects**, **Confirmed by** (a test, or the explicit absence of one), and **Notes / `⚠ unverified`**.
- `## Background / scheduled / event-driven behavior` -- the table of non-synchronous flows (trigger + handler anchored).
- `## Behavior evidenced only by tests` -- the table of behavior the tests assert that the production path only implies.
- `## Declared use cases (not observed)` -- declared in the documentation (README / `docs` / `.puml` / `.http`) but with no implementing code: each row `⚑ declared (not observed)` anchored to **both** the declaring doc **and** the confirmed absence in code (RE-01 §6). The intended-but-unbuilt milestones -- segregated, never mixed with observed flows, never dropped. May be empty.
- `## Cross-flow observations` -- shared handlers / middleware / convergence points (the R4 pointer).
- `## Gaps & unverified` -- `⚠ unverified` flows and any R1 entry points with no locatable handler. (Also state the documentation-sweep command + count here, so coverage is auditable -- RE-01 §6 completeness.)

**No frontmatter** -- the fragment is inlined into the SAD's *audit* plane by the `handoff-assembler`. Descriptive only (RE-03); every flow hop anchored (RE-01).

---

## Refusal conditions

The sub-skill refuses to write the fragment and returns the specific violation when:

| # | Trigger | Rule | Returned message |
|---|---|---|---|
| 1 | Gate **R1** (`system-cartography.md`) is not `[x] approved` in the tracker (it is `[ ]`/`[~]`/`[?]`/`[i]`, or the fragment is absent on disk and degraded to `[ ]`). | RE-05, root §Gate approval protocol | Stop. R2 traces flows from R1's entry points; producing it before R1 is approved is the premature-advance error. Point to the open R1 gate; approve R1 (or reopen and re-walk) first. |
| 2 | The operator asks to redesign, optimize, or "improve" a flow (add a queue/retry/cache, split a handler, propose a target call topology, rename a handler). | RE-03 | Recon is descriptive, not prescriptive. Record the observed flow with anchors; the redesign is the SAD's job downstream. Restate the request as a description of what the flow currently does, or route forward to the SAD. |
| 3 | A flow (or any hop in its path) is asserted with no anchor along its call path and no `⚠ unverified` mark. | RE-01 | An unanchored flow is confabulation. Either anchor each hop (`file:line` along the path, or a test that exercises it) or quarantine the flow with `⚠ unverified` naming the missing anchor. |
| 4 | A behavior is **claimed as observed** because a doc / comment / README / `.puml` asserts it, with no implementing code to back it (the publisher is an unused stub with zero call sites; the README pipeline has no consumer). | RE-01 §6 | Do not state it as observed, and do **not** silently drop it. Documentation is a lead, not proof. If the code *contradicts* it, state what the code observably does + note the discrepancy. If the code simply *lacks* it, move the claim to `## Declared use cases (not observed)` as `⚑ declared (not observed)`, anchored to the declaring doc **and** the confirmed absence -- it is an intended-but-unbuilt milestone, kept (not lost) for downstream to keep or cut. The executed path is the proof of *observed* behavior; the doc is proof of *declared intent*. |

---

## Why these rules

- **RE-01 (anchor every hop).** Behavior reconstructed without anchors is the single failure mode this whole skill exists to prevent: the model reads an entry point and a couple of files and narrates a coherent event-driven saga that the code does not run -- a stub field becomes "integrates with Stripe via a dedicated gateway", an unused `IBus` becomes "publishes domain events". Anchoring each hop along the call path makes every flow falsifiable in one click: open the file, go to the line, see whether the call actually happens. A flow is a chain of pointers into the code, not a story about it.
- **Tests are trustworthy evidence.** A passing test that drives a flow is a re-checkable anchor that encodes *intended* behavior explicitly -- often more legibly than the production path, which may reach the behavior only through indirection. Mining the test suite recovers behavior a static read of the production code would miss, and the *absence* of a test on a significant flow is itself an honest finding.
- **RE-03 (describe observed, not desired).** R2 feeds the SAD's *audit* plane, which is a **residual candidate** the SAD's S6 measures against an independently-built naïve baseline -- it is evidence, never the baseline. If R2 smuggles in redesign ("this flow should be async"), it contaminates that baseline and pre-empts the stressor analysis (S3) that is supposed to *derive* whether the change is justified. R2 holds up a clean, honest mirror of what runs; the empirical test downstream stays clean only if recon never prescribes.

---

## References

- `../../shared/constitution.md` -- **RE-01** (evidence anchoring, every flow hop), **RE-03** (descriptive not prescriptive -- no flow redesign), **RE-05** (tracker coherence / one-fragment-then-STOP).
- `../../shared/evidence-anchoring.md` -- anchor forms (`file:line`, range, commit, command+output), the `⚠ unverified` quarantine, **§6 documentation as evidence** (the completeness sweep, the doc-anchor-vs-code-anchor ranking, and `⚑ declared (not observed)`), and the recurring read-only commands for tracing entry points and call chains. Read before producing the fragment.
- `../../shared/glossary.md` -- vocabulary (flow, entry point, anchor, `⚠ unverified`, `⚑ declared (not observed)`, documentation vs code anchor, completeness sweep, convergence point, the *audit* plane).
- `../../templates/behavior-reconstruction.md` -- the exact fragment shape this sub-skill fills (no frontmatter).
- Root `../../SKILL.md` -- the gate machine, router, and §Gate approval protocol that enforce R2's R1 pre-condition and the one-fragment-then-STOP discipline.
- **R2 consumes R1.** `../system-cartography/SKILL.md` -- the prior gate; its entry points are R2's flow seeds and its dense-logic seeds point R2 at the significant flows. R2's carry-forward (convergence points, domain-dense flows) feeds R4 (coupling) and R3 (intent).
