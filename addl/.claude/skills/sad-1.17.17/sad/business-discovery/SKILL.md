---
name: business-discovery
description: Entry sub-skill of the `sad` meta-skill. Produces the Business View and the Naïve Architecture fragments of a SAD. Invoke when starting a new SAD from a PRD/SRD or from stakeholder input; refuse to invoke when a naïve architecture already exists for this project.
task_types: [discover, frame, naive-architecture, business-view]
shared_refs:
  - shared/constitution.md
  - shared/idesign-vocabulary.md
  - shared/glossary.md
  - sad/template.md
  - sad/synthesis-explanation.md
---

# business-discovery (S1)

Entry sub-skill of the meta-skill. Produces two fragments that fill the first two sections of the SAD: Business View (objective, pain points, goals) and Naïve Architecture (the simplest IDesign-compliant decomposition that solves the problem as stated). The naïve architecture is the **control baseline** against which the residual architecture will be measured in the empirical Ri test (S6).

This sub-skill does NOT make the architecture clever. The naïve architecture must be deliberately naïve: it solves the problem as the PRD/SRD describes, with no consideration of stress, change, or future-proofing. Cleverness here destroys the empirical baseline.

---

## When to invoke

- A new SAD is being produced for a project that does not yet have a Business View or Naïve Architecture fragment.
- The PRD or SRD has stabilized enough that stakeholders can answer "what is the system for, what hurts today, what does success look like".
- Naïve architecture is needed as the control for the empirical Ri test downstream.

## When NOT to invoke

- A naïve architecture fragment already exists for this project (use `flow-analysis` S2 next).
- The user is requesting "the right" architecture or "the improved" architecture -- this sub-skill produces the naïve baseline, not the residual architecture. Direct them to the full meta-skill flow.
- No PRD/SRD and no stakeholders accessible -- the sub-skill cannot generate a plausible business view from nothing.
- The request is to update an existing Business View. This sub-skill produces from scratch; updates are handled separately.

## Pre-conditions

None. This is the entry skill. The only required input is access to a PRD / SRD or to stakeholders who can answer business-framing questions.

## When a prior implementation exists (Phase-0 as evidence)

A common real-world entry: the project is greenfield (no SAD yet) but a **Phase-0 implementation already exists**, and the user brings a document that mixes three planes -- business framing, an audit of the existing Phase-0, and anticipated stressors ("gaps"). This is NOT the "naïve already exists -> refuse" case above; it needs a deliberate split. Separate the three planes before producing anything:

- **Business framing** -> feeds S1 (this sub-skill): objective, pain points, goals.
- **Audit of the existing implementation** -> NOT the baseline. Route to `sad-auditor` if a rule-compliance read is wanted, or hold as input. The existing implementation is a **residual candidate** that S6 measures against the naïve, never the control.
- **Anticipated stressors / gaps** -> hold for S3 `stressor-analysis`; do not bake them into the naïve.

Clarify with the user which of three entry modes applies:

- **(a) Audit the existing Phase-0** -> route to `sad-auditor`; not an S1 task.
- **(b) Fresh SAD** -> produce the naïve baseline from the business framing as if greenfield; the Phase-0 is evidence for S6, not the baseline.
- **(c) SAD for the next phase (Phase-1)** -> business framing for Phase-1 -> naïve baseline for Phase-1; the Phase-0 implementation is a residual candidate S6 will measure.

In all modes the **naïve architecture stays the control** (deliberately naïve, R-09 no speculative design). The existing implementation never becomes the baseline -- treating it as the baseline would destroy the empirical Ri test (S6), because the residual would be measured against an already-strong starting point with no naïve to improve over.

## When a Developer back-channel routes a re-land (a landed release as evidence)

A third real-world entry, distinct from the Phase-0 *code* case above and the
multi-initiative pile below: a downstream **Developer** (implementing a prior landed
release through spec-kit) hit a use case the release does not cover and raised a
**back-channel request** -- a `needs-architecture` gap it refused to invent inline
(the Architecture Supremacy Rule, `sdd-interface/standard/rdag-standard.md` §4). The
resolution is an architecture **RE-LAND**: you
re-architect to cover the new use case and emit the NEXT release. The orchestrator
(ADDL) cuts a branch, runs you on it, and merges the new release back -- you own
NONE of that git; you produce the architecture.

The input is NOT a free-form three-plane document but two **structured artifacts**:

- **The current landed release** at `architecture/arch-X.Y.Z/` (service-catalog,
  nfr-register, decisions/ADR-*, use-cases, residues). It is the as-built you carry
  forward -- and, exactly as in the Phase-0-as-evidence case above, a **residual
  candidate S6 measures, NEVER the naïve baseline** (adopting it as the baseline
  destroys the Ri test, R-09). Read it: the new release keeps its services, NFRs,
  residues, and binding ADRs intact unless the gap genuinely supersedes one.

- **The back-channel request** at `docs/developer/back-channel-<NNN-slug>.md`. It
  names the PRECISE gap in one of three forms -- **Form A** (a service absent from
  the catalog), **Form B** (an ADR / binding decision needed), or **Form C** (a
  missing structural `S-NN` residue or `C-NN` coupling). This is the new use case's
  requirement the re-land MUST close; treat it as the framing's new demand, NOT as a
  decision already made (the Developer correctly declined to make it -- you rule on
  it).

Run as entry mode **(c)** (SAD for the next phase): the existing release is the
residual candidate; the new use case + its gap drive the next release's framing.
Carry the existing architecture forward, close the named gap with real architecture
(the new service / ADR / residue the Developer could not invent inline), and emit
the NEXT release -- a minor bump for an additive use case (e.g. `arch-1.0.0` ->
`arch-1.1.0`). The naïve (S1b) stays the control (R-09). When the release lands
(S8b), the operator resolves the back-channel and the Developer re-enters against it
-- the previously-blocked add is now absorbed by the new release's residues.

## Rich documentation input (multi-initiative)

A second common real-world entry, distinct from a single PRD/SRD and from the Phase-0 code case above:
the source is a **folder of accumulated documentation for ONE product that grew over time**, where
features were added as separate **initiatives** -- several business-view-format initiative docs, plus
many use cases (often with sequence diagrams), plus design diagrams (C4, frequently as images). The
product is real and documented; the job is to synthesize one coherent SAD from the pile, not to invent
one from a blank page.

This is the **over-documented sibling of the brownfield code case**: do NOT reverse-engineer (that is
the `recon-*` skill's job for *under*-documented code) -- the framing, use cases, and design are already
written. The work is to **reconcile, route by altitude, and surface the contradictions** a product that
grew by accretion inevitably accumulates.

- **Produce ONE business view, synthesized across the initiatives.** Read every initiative doc and
  reconcile them into a single objective / pain points / goals / invariants for the product as a whole.
  Dedupe overlapping framing. Where two initiatives genuinely conflict, do NOT silently merge -- that
  conflict is an Open Question (below). The business view stays high-level (goals are outcomes, not
  mechanisms, per Step 1.1); it does NOT absorb use-case detail.

- **Run the R-27 Open Questions pass (Step 1.2) CROSS-document.** The lens sweep runs over the *whole
  corpus*, not one doc -- and two lenses do the heaviest lifting here, applied *across* initiatives:
  **L10 (internal conflict)** and **L11 (stale / unexamined premise)**. A product grown by accretion
  routinely carries an early initiative's premise that a later one has silently superseded (a scope
  call, pricing assumption, or "validated by X" claim that no longer holds). Surfacing those
  cross-initiative contradictions as Open Questions is the single highest-value thing this pass does for
  a grown product -- flag where the docs disagree, do not paper over it. Set each such OQ's `Source` to
  the conflicting initiatives (e.g. `init-billing.md §2 vs init-trials.md §4`).

- **Route the fine use-case detail forward -- it does NOT go in the business view.** The input use cases
  (their flows, business rules, acceptance criteria, sequence diagrams) are carried forward as evidence,
  preserved at the gates that own them: their flows inform **S2** (flow-analysis); at **S5** they SEED
  the SAD's *Use Cases with Residue Mapping* (see `residual-design` Step 4) -- the architect preserves
  each input use case's Main/Alternative Flows, Business Rules, and Acceptance Criteria **verbatim**
  (anchored to its source, e.g. `init-billing.md §UC-3`; gaps marked `NEEDS CLARIFICATION`) and ADDS the
  Residue Mapping the input docs cannot supply. The fine detail is preserved **at the use-case artifact,
  not compressed into the business document** -- cramming it up into the business view would break the
  altitude separation and the empirical baseline.

- **Treat the input design diagrams (C4 / sequence) as Phase-0 evidence, NEVER the baseline.** They
  describe the grown product's as-is architecture, so -- exactly as in the Phase-0-as-evidence case above
  -- they are a **residual candidate S6 measures**, not the control. The naïve architecture (S1b) stays
  deliberately naïve, derived from the synthesized framing while *ignoring* the existing design; copying
  the existing C4 as the baseline destroys S6's Ri test (R-09). The architect MAY read the diagrams
  (reference for S5's own C4 output, and input to S6) but does not adopt them as the naïve. The (b) / (c)
  entry modes above apply: **(b)** = re-architect the product fresh with the existing design as S6 evidence
  (the usual choice for a grown product); **(c)** = SAD scoped to the next initiative, prior initiatives as
  residual candidate.

**Lateral context to carry forward (in addition to the single-PRD carry-forward):** which use cases came
from which initiative (so S5 can seed them); the cross-initiative contradictions logged as Open
Questions; the existing design diagrams held for S6 as residual candidate.

## Handoff contract

Runtime-agnostic interface (single-LLM reads these; an agent passes them as message payload):

- **Consumes:** PRD/SRD or stakeholder input (entry sub-skill -- no prior fragment). If a Phase-0 implementation exists, the three-plane split (see above). On a **Developer back-channel re-land**, a landed release (`architecture/arch-X.Y.Z/`) as residual-candidate evidence + the back-channel request as the gap to close (see above).
- **Produces:** two fragments behind **two gates** -- `business-view.md` (objective, pain points, goals, **invariants**, **open questions**) at gate **S1a**, then, only after S1a is approved, `naive-architecture.md` (IDesign-typed component list + "explicitly ignores" list) at gate **S1b**. One fragment = one gate; do not emit both in one turn.
- **Lateral context to carry forward:** which goals are invariants vs ordinary; the **deferred volatilities** logged in §Open Questions (sensed stressors the architect deliberately routed to S3, so S3 picks them up -- distinct from the gating open questions); why the naive was kept deliberately narrow.

---

## Workflow

### Step 1 -- Business View

Read the PRD/SRD if provided. If not, conduct or document an interview with the product owner / project sponsor to gather:

- **Objective.** One paragraph stating what the system is and what it does. No technology, no implementation. Anchored on the business outcome.
- **Pain Points.** Bulleted list of current problems the system is meant to address. Each pain point is concrete (not "things are slow" but "manual reconciliation takes 6 hours per day").
- **Goals.** Itemized list of what success looks like. Each goal is observable.

Then run the **hygiene pass** (1.1), the **Open Questions discovery pass** (1.2, R-27), capture **Invariants** (1.3), and apply optional **source grounding** (1.4) before stopping at gate S1a (1.5).

#### 1.1 Business View hygiene pass

Stakeholders routinely paste goals with implementation vocabulary baked in (especially when copying from an engineering master doc). R-05 forbids technology vocabulary in *component names*, but the same leakage shows up at the *goal* level and R-05 does not cover it. Run this hygiene pass over every objective / pain point / goal before writing the fragment. **Goals are observable outcomes, not mechanisms.** Reject and rewrite any goal that contains:

- **SCREAMING_CASE tokens** (e.g. `MAX_DAILY_DRAWDOWN_EXCEEDED`) -- these are alert codes / constants, not outcomes. Rewrite as the outcome ("the operator is notified when daily loss exceeds the configured limit").
- **Component / module names** (e.g. "the risk management module", "the matching service") -- name the outcome, not the part that delivers it.
- **Transport / mechanism vocabulary** (e.g. "publishes alerts", "via pub/sub", "writes to the queue") -- describe what must be true, not how it is moved.
- **Technology names** (vendors, frameworks, protocols, datastores) -- same rule as R-05, applied to prose.

The test for each goal: *could this be true under a completely different implementation?* If the wording pins one implementation, it is leaking. Rewriting is mandatory; a leaked goal biases the naïve decomposition (Step 2) toward a pre-baked solution and contaminates the S6 baseline.

#### 1.2 Open Questions discovery pass (multi-lens PRD ambiguity scan) -- R-27

The PRD's gaps are first-order architectural information. To produce a good architecture downstream there must be as few open doubts as possible going into S1b: every detail of the PRD must be understood, and the details that cannot be understood from the document alone must be **named, not skipped**. Ambiguity hides in far more than the explicit `TBC` markers, so the discovery is **systematic, not incidental** -- run the full lens catalogue below over the objective, pain points, goals, and the whole source document. This is the S1 analogue of the S3 stressor frameworks: multiple lenses so nothing is missed by reading only for the obvious (R-22 lateral mode -- an ambiguity is evidence of incomplete understanding to engage with, not a defect to patch away).

**Lexical lenses (scan for these tokens):**

| Lens | Signal | Catches |
|---|---|---|
| **L1 -- Marker** | `TBC`, `TBD`, `to be confirmed/defined`, `pending`, `unconfirmed`, `unknown`, `?`, `(?)` | Doubts the PRD already admits explicitly |
| **L2 -- Hedge** | `maybe`, `should probably`, `we assume`, `presumably`, `likely`, `we think`, `if possible` | Decisions that look made but are not |
| **L3 -- Unquantified target** | `~`, `indicative`, `approximately`, `target`, or NFRs with no number (`fast`, `scalable`, `real-time`, `high volume`) | Real thresholds left undefined |

**Semantic / lateral lenses (read for these, R-22):**

| Lens | Question | Catches |
|---|---|---|
| **L4 -- Undefined term** | Is this term/acronym used but never defined, or does it admit >1 reading? | Ambiguous business vocabulary |
| **L5 -- Silent actor / ownership** | Who triggers / approves / configures this? When? | Actions with no owner (e.g. "commission is frozen" -- by whom? how is it cleared?) |
| **L6 -- Lifecycle / state gap** | Is a state named with no entry/exit transition? A flag with undefined semantics? | Irreversible or rule-less states/flags (e.g. `NoBonus? TBC`) |
| **L7 -- Edge / failure silence** | What happens on empty / negative / concurrent / failure / partial? | The unhappy path the PRD does not mention |
| **L8 -- Scope boundary** | In/out of scope clear? "Phase 2" deferrals? Per-brand/tenant divergence? Rollout order? | Blurry system boundaries |
| **L9 -- External / in-flight dependency** | Does this depend on external or in-flight work whose status is unconfirmed? | Pending platform migration, third-party data availability |
| **L10 -- Conflict / measurability** | Do two requirements contradict? Does the data to measure each goal exist? | Contradictions and non-measurable goals |
| **L11 -- Stale / unexamined premise** | Does a decision the PRD presents as *settled* (in/out-of-scope call, stated assumption, "validated by X" claim) rest on a premise another part of the document -- or known domain reality -- contradicts or has outgrown? | Settled decisions on stale/unverified premises (an out-of-scope item whose rationale conflicts with the core flow; an Assumptions-section claim asserted without confirmation). Forces an explicit walk of the Assumptions section and every Out-of-Scope rationale. |
| **L12 -- Regulatory / compliance / privacy silence** | Does this feature touch personal data, money movement, consent, jurisdiction, audit, AML, or responsible-gambling -- and is the document silent on the governing constraint? | Compliance dimensions the PRD never addresses (cross-player personal/financial-data exposure; self-exclusion/closure handling of balances; AML on payouts). Distinct from L7 (technical unhappy path) and L8 (scope boundary). |

**Triage (mandatory -- not every ambiguity is an Open Question).** Classify each candidate into exactly one:

1. **Open Question** -- needs a stakeholder answer the architect cannot supply -> goes to `### Open Questions` (one card per question), **gates S1a** (Step 1.5).
2. **Deferred volatility** -- a stressor the architect *has* sensed and will deliberately address in S3 -> listed as carry-forward context, **does NOT gate**.
3. **Resolvable now** -- answerable from a careful reading of the PRD itself -> resolve it, it is not an OQ.

This split is what prevents the two failure modes: inflating the gate with non-blocking stressors, or burying a genuine blocker among deferrals. Record each Open Question as a **card** (template §Business View Open Questions): a `#### OQ-N - <Status> -- <short title>` heading, a `**Question:**` paragraph, an optional `**Answer:**` (present once a stakeholder gives one -- even partially), and a `<sub>**Affects:** ... -- **PRD:** ...</sub>` footer naming the goal / invariant / downstream decision it touches and the source (`PRD:L<n>` or `stakeholder`). **Status** is one of `Open` (no answer yet), `Open (partial)` (a partial stakeholder answer is recorded but the question still needs more), or `Resolved` (answered -- cite the source); `Open` and `Open (partial)` both gate S1a, `Resolved` does not. The card format lets a partial stakeholder answer ride alongside the still-open question -- the operator can later EXPAND it without losing what was already given. If the lenses genuinely surface nothing, state "None" -- do not invent questions (R-09).

**Forcing function -- the Lens Coverage Ledger (mandatory).** The single biggest failure mode of this pass is **satisficing**: catching the obvious explicit markers (L1) and the loud scope/dependency lenses (L8/L9), then stopping -- so the high-value findings that live in the quiet semantic lenses (L5 ownership, L7 edge silence, L10 internal conflict, L11 stale premise, L12 compliance silence) escape silently. The RAF smoke test demonstrated this: a first pass found 10 questions; a deliberate full sweep found 23, including a contradiction in the PRD's own safe-model rule (L10) that the first pass never saw (`evals/smoke-test-3-raf/audit-s1a-iter-2.md`).

To make silent omission impossible, the discovery pass is **not complete** until you have written a **Lens Coverage Ledger** that gives every lens L1-L12 an explicit verdict. A verdict is either the OQ IDs that lens produced or the literal word `none`. You may not leave a lens row out and you may not leave a verdict blank -- a missing or blank lens is an incomplete sweep, and the auditor flags it deterministically. `none` is a legitimate verdict, but writing it is a positive assertion that you applied the lens and it genuinely found nothing (do not rubber-stamp `none` to skip work -- the heuristic check spot-checks `none` verdicts against the PRD). Walk the lenses **one at a time, in order**, and write the verdict as you go; do not declare the pass done from memory. Attribute each OQ to the lens that **literally fired**, not the nearest plausible one: an OQ may list more than one lens only if each genuinely caught it. A decorative attribution (mapping a domain-reasoned OQ onto a lexical lens that did not actually trip) understates the real coverage gap and is a verdict-genuineness concern the auditor spot-checks.

```
| Lens | Verdict (OQ IDs, or `none`) |
|---|---|
| L1 Marker | OQ-... |
| L2 Hedge | none |
| ... | ... |
| L10 Conflict / measurability | OQ-... |
| L11 Stale / unexamined premise | OQ-... |
| L12 Regulatory / compliance / privacy silence | none |
```

Output the ledger to `business-view.md` as a `#### Lens Coverage Ledger` subsection of §Open Questions (template §Business View Open Questions). **Before parking at gate S1a, run the bundled `scripts/fragment-checks/check_fragment.py business-view.md`** -- it hard-fails if any lens L1-L12 is missing or carries a blank verdict, and on any OQ that is missing its Status (in the heading), its `**Question:**`, or its Affects/Source footer (for legacy table-form fragments: any OQ row missing ID / Affects / Status / Source). This is the deterministic backstop against the satisficing failure mode above (the smoke-test S1a "stopped at L10" class); the auditor runs the same script, so failing it here means a guaranteed reopen.

#### 1.3 Invariants (non-negotiables) -- the regression guard, NOT a stable core

Some business properties must hold no matter what stressor hits the system: regulatory / legal / contractual non-negotiables. Examples: "personal data never leaves its home jurisdiction"; "funds always flow contractor -> system -> worker, never directly"; "an active commitment's rate is never changed after the fact". Capture these as a short **Invariants** list in the Business View.

Critical framing (R-01 / R-21): **invariants are acceptance criteria the empirical test (S6) verifies, NOT units of decomposition.** Do NOT create a component per invariant, and do NOT let invariants drive the naïve architecture -- that would be a stable-core-first / correctness-first approach, which R-21 subordinates to criticality. The decomposition stays residue-driven (R-01). Invariants exist so that S6 can check a distinct question from "did the system survive the stressor?": namely, "while surviving, did the residual architecture *violate a non-negotiable*?" A system can survive every stressor and still break an invariant in the process (survive an outage but route data cross-border); the invariant list is what catches that.

Each invariant is one observable property, grounded (where a PRD exists) to the requirement that mandates it (see §1.4). S6 verifies each against the residual under the test stressors; a violation is a **critical regression** (worse than the per-stressor regressions of S6 Step 6.1). If a project has no hard non-negotiables, the list is empty -- do not invent invariants (that is R-09 speculative design).

#### 1.4 Source grounding (optional)

When a PRD/SRD with stable line numbers exists, ground each Business View item (objective / pain points / goals / invariants / open questions) and -- later, in Step 2 -- each naive component to the requirement that motivates it, using the `PRD:L<n>` / `PRD §<x>` pattern (`shared/style-conventions.md` §7.1). This makes the SAD auditable against its source and is recommended in regulated contexts. It is optional: if there is no line-stable PRD, omit the refs (do not invent line numbers). Note the boundary: genuine stressors (S3) are NOT grounded to the PRD -- by definition they are not in it.

Output these to `business-view.md` (a fragment file that fills SAD §Business View).

#### 1.5 STOP -- gate S1a (Business View), human checkpoint

S1 produces two fragments and they get **two separate gates**, one per fragment (one fragment = one gate = one approval). The Business View is the foundation the Naïve Architecture is built on; if the framing is wrong, a naïve pass on top of it is wasted work.

So: after writing `business-view.md`, **stop**. Present it, run `sad-auditor` `by-fragment`, and mark gate **S1a** `[?] awaiting review`. Do NOT begin Step 2 (Naïve Architecture) until the operator approves S1a (`[x]`). Producing the naïve architecture in the same turn as the Business View is the error this checkpoint exists to prevent. (Root `SKILL.md` §Orchestration: gates are per fragment.)

**Open-questions warning at the gate (R-27).** Before presenting S1a for approval, count the `### Open Questions` cards still in `Status: Open` or `Status: Open (partial)` (a recorded partial answer does NOT clear the gate -- the question is still open). If any remain, the gate MUST NOT be approved silently: present an explicit warning -- "N open business questions remain unresolved" -- enumerate them, and state that proceeding to S1b means building the naïve baseline (and everything downstream) on top of unanswered framing. The operator may still proceed (parallel stakeholder threads, time-boxing), but only on **explicit acknowledgment**, which is recorded **in the S1a row's `Approved on` cell of the FLOW.md Gate tracker** (the tracker has no separate Notes column), appended after the date -- e.g. the S1a row becomes: `| S1a | business-view.md | [x] | 2026-06-13 (acknowledged: proceeding with 10 open questions) |`. The acknowledgment text must contain no `|` (it would break the table row). Approving S1a `[x]` with `Open` / `Open (partial)` entries and a bare date (no acknowledgment parenthetical) in the `Approved on` cell is an R-27 violation the auditor flags. Deferred volatilities do NOT count toward this warning -- only `Open` / `Open (partial)` questions do.

### Step 2 -- Naïve Architecture

Apply the **Four Questions** (Lowy L1107-1129; see `shared/idesign-vocabulary.md` §7) to extract candidate components:

- **Who** interacts with the system -> Client candidates.
- **What** is required of the system -> Manager candidates.
- **How** the system performs business activities -> Engine candidates.
- **How** the system accesses Resources -> ResourceAccess candidates.
- **Where** the system state is -> Resource candidates.

For each candidate component:

- Assign a type (`Manager`, `Engine`, `ResourceAccess`, `Resource`, `Utility`, `Client`) per R-02. See `shared/idesign-vocabulary.md` §1 for the canonical four layers (Client / Business Logic / ResourceAccess / Resource) plus the transversal Utilities Bar.
- Name it per R-06 (two-part Pascal case with valid suffix for Manager / Engine / Access; domain noun for Client and Resource; descriptive name for Utility).
- Verify the name has no technology vocabulary per R-05 (no Lambda, SQS, REST, Kafka, etc. in the name).
- Identify the volatility the component encapsulates -- a one-sentence justification per R-01 (residue-based decomposition; volatility is one input signal).

Produce the **Component Taxonomy table** filling the SAD's §Naïve Architecture section. The table columns:

| Layer | Component | Responsibility |
|---|---|---|

Add a minimal call topology diagram (Mermaid `flowchart TB`) showing the closed architecture (R-03): Client -> Manager -> Engine / ResourceAccess -> Resource. No Pub/Sub yet (Pub/Sub is for queued M-to-M async per R-04 (d), which is residue-driven, not naïve). This naive baseline is the **one** diagram in a SAD that stays Mermaid (`style-conventions` §6); the residual Static Architecture (S5) is PlantUML.

### Step 3 -- Validate against the constitution

Run the following checks before declaring the fragment ready:

> **Script-backed (run before parking S1b).** `scripts/fragment-checks/check_fragment.py naive-architecture.md` mechanically enforces the Taxonomy (R-02), tech-vocab (R-05), and naming (R-06) rows below; run it and fix any hard-fail before the gate. The remaining rows (R-03/R-04 call rules, R-07, R-11) stay auditor checks.

| Check | Rule | What to verify |
|---|---|---|
| Taxonomy | R-02 | Every component has a valid type. |
| Closed architecture | R-03 | No upward calls. No Manager-to-Manager sync. No Engine-to-Engine. No ResourceAccess-to-ResourceAccess. |
| Relaxing the Rules | R-04 | Utility callers are Manager / Engine / ResourceAccess only (not Client, not Resource). Manager-to-Engine is fine (R-04 (c)). Manager-to-RA is fine (R-04 (b)). Queued M-to-M is fine (R-04 (d)). |
| Hygiene | R-05 | No technology vocabulary in component names. |
| Naming | R-06 | Two-part Pascal case + valid suffix. |
| Atomic verbs | R-07 | Verbs appear only in ResourceAccess contract operations, never as service name prefixes. |
| Almost-expendable Manager | R-11 | Each Manager has workflow only; no business logic inside the Manager itself. (Heuristic.) |

If any deterministic check fails, do not write the fragment -- raise a refusal (see §Refusal conditions).

### Step 4 -- Note what the naïve architecture explicitly ignores

At the end of `naive-architecture.md`, add a short section explicitly listing what the naïve baseline does NOT account for. This is critical: it makes the baseline honest as a control for the empirical Ri test, and it gives the downstream `stressor-analysis` (S3) a starting menu of things to stress.

Example (EV charging):

> **What the naïve architecture explicitly ignores:** hardware faults, key fob loss, queues, damage, server failure, billing disputes, abandoned cars, privacy regulation, geographic variation, electricity supply failures, market shifts, competition.

The point is not to enumerate every possible stressor (that is S3's job) but to acknowledge that the naïve baseline is intentionally narrow.

**The naïve architecture is your first walk.** Per R-22 and `shared/architectural-walking.md`: you do not yet understand the domain; what you produce here is a map, not the territory. The "explicitly ignores" list is the first set of differences you have already noticed and chosen not to address yet. If the list is empty, you are in linear mode (defending an implicit claim that the naïve architecture covers everything). Lateral mode produces this list comfortably because being-wrong is the expected state.

---

## Open Questions resolution pass (operator-triggered, optional)

After S1a is parked (`[?]` / `[i]`) the operator may ask the Architect to take a pass at the
§Open Questions before approving -- answering what the **evidence already in hand** can answer, and
cleanly leaving the rest for a stakeholder. This is the S1 analogue of recon's R3 resolution pass. It
is **not** a new gate and does **not** change S1a's state; it edits `business-view.md` in place while
the gate waits. It is distinct from the operator simply acknowledging the open questions and proceeding
(R-27) -- here the goal is to *resolve* them, not to pass the gate over them.

For **each** `OQ-N` card with `Status: Open` or `Status: Open (partial)`, re-examine the question against
the evidence its own **Source** footer cites (the PRD/SRD line, `RESPONSE.md`, the `phase0-evidence`
section) and choose **exactly one** of two outcomes -- never a third:

1. **Answer (from cited evidence).** If the cited Source evidence -- or other framing evidence already
   in hand -- genuinely answers the question, set `Status: Resolved` and record the answer **plus its
   anchor** (`PRD:Ln` / `RESPONSE.md:Ln` / `phase0-evidence §...`) in the card's `**Answer:**`. If the
   answer changes the objective, users, goals, or invariants, update the affected Business View section to
   match so the fragment stays internally consistent. (When the operator instead supplies a partial
   stakeholder answer that does not fully resolve the question, record it in `**Answer:**` and keep
   `Status: Open (partial)` -- still gating -- so it can be expanded later.)
2. **Leave open (stakeholder-required).** If the question genuinely needs a stakeholder decision absent
   from all evidence -- it turns on business intent, a human decision, or external context not present in
   any source -- keep `Status: Open` with a one-line note on what the evidence cannot supply.

**The forbidden third outcome -- never do this:** invent or assert a stakeholder answer the evidence does
not support. An unanswerable question is *left open*, not *guessed*. A confident-sounding paragraph is
not an answer. This is R-09 (no speculative content) and R-27 (open questions need a real stakeholder
source) applied to the open questions themselves: a `Resolved` card is a claim and therefore **must**
cite where the answer came from; a card with no evidentiary source stays `Open` (or `Open (partial)`).

This pass is idempotent: re-running it re-examines only the cards still `Open` / `Open (partial)` and
leaves `Resolved` cards untouched unless new evidence overturns them. After the pass, the operator
re-reviews `business-view.md` and approves -- acknowledging (R-27) whatever genuinely remains
`Open` / `Open (partial)`.

## Output contract

Two fragment files in the project workspace, produced behind **two separate gates** and **never in the same turn**: write `business-view.md`, stop at gate **S1a** for approval, and only then write `naive-architecture.md` for gate **S1b**.

### `business-view.md`

Markdown fragment with the sections matching the SAD template §Business View:

- `### Objective`
- `### Pain Points`
- `### Goals`
- `### Invariants (non-negotiables)` -- the regression-guard table (1.3); omit only if the system has no hard non-negotiables (R-09).
- `### Open Questions` -- the unresolved-business-inputs table from the discovery pass (1.2, R-27), the non-gating "Deferred volatilities" carry-forward note, and the mandatory `#### Lens Coverage Ledger` giving every lens L1-L12 an explicit verdict; state "None" in the OQ table if the lenses surface nothing (the ledger is still required).

No frontmatter; the fragment is meant to be inlined into the SAD by `sad-assembler` (S7).

### `naive-architecture.md`

Markdown fragment with the SAD template §Naïve Architecture content:

- One paragraph describing the system in IDesign terms (Client / Manager / Engine / ResourceAccess / Resource).
- The Component Taxonomy table.
- A minimal Mermaid `flowchart TB` of the closed architecture.
- A short "What the naïve architecture explicitly ignores" subsection.

No frontmatter.

---

## Refusal conditions

The sub-skill refuses to write the fragment and returns the specific violation when:

| # | Trigger | Rule | Returned message |
|---|---|---|---|
| 1 | Any proposed component name contains technology vocabulary (case-insensitive: aws, azure, gcp, lambda, sqs, kafka, kubernetes, k8s, docker, postgres, mysql, mongodb, redis, dapr in Manager/Engine/RA names, grpc, rest, http, websocket, etc.). | R-05 | List the offending names and propose residue-named alternatives. |
| 2 | Any proposed component name violates the two-part Pascal case + valid suffix rule. | R-06 | List the offending names and the expected naming pattern. |
| 3 | Any proposed Manager is named for a use case (e.g., `AddCustomerManager`, `ProcessOrderManager`). | R-16 | Flag the use-case-driven naming and propose a residue-named alternative (e.g., `MembershipManager`, `OrderProcessingManager` -> `OrderManager` with the activities moved to Engines). |
| 4 | A proposed component has a contradictory type (e.g., a "Manager" that holds no workflow and just delegates -- expendable per R-11). | R-11 | Flag the expendable Manager and propose: either remove it, or articulate the workflow volatility it encapsulates. |
| 5 | A Client is proposed to call a Utility, an Engine, a ResourceAccess, or a Resource. | R-03 + R-04 (a) tightened | Reject the call topology. Client may only call Manager. |
| 6 | A Manager calls another Manager synchronously. | R-03 | Reject. Either use queued M-to-M (R-04 (d)) or rethink whether the two Managers should be one. (Note: naïve architectures should be simple enough that queued M-to-M rarely appears; if it does, the architecture may not be naïve enough.) |
| 7 | An Engine calls another Engine, or a ResourceAccess calls another ResourceAccess. | R-03 | Reject. Reframe via Manager orchestration or single ResourceAccess that joins resources. |
| 8 | The Business View has empty or template-placeholder content. | -- | Refuse to produce a stub naïve architecture from no input. Request stakeholder access or PRD/SRD. |
| 9 | A goal / pain point / objective contains implementation leakage: a SCREAMING_CASE token, a component/module name, transport vocabulary (pub/sub, queue, publishes), or technology names. | Step 1.1 (R-05 spirit, goal level) | List the leaking goals and rewrite each as an observable outcome ("could this be true under a different implementation?"). Do not proceed to Step 2 with leaked goals -- they bias the naïve decomposition. |
| 10 | Step 2 (Naïve Architecture) is attempted while gate **S1a** (Business View) is not yet `[x] approved` in the tracker. | Step 1.5, Orchestration (per-fragment gates) | Stop. Present `business-view.md` and wait for S1a approval. The naïve architecture is built on the Business View; producing it before the framing is approved is the premature-advance error this gate prevents. |
| 11 | Gate **S1a** is approved (`[x]`) while one or more `### Open Questions` cards are still `Status: Open` or `Status: Open (partial)` and no operator acknowledgment is recorded at the gate. | R-27, Step 1.5 | Do not pass S1a silently. Present the warning, enumerate the unresolved open questions (a recorded partial answer does not clear one), and require an explicit, recorded acknowledgment before advancing (or resolve the questions first). Deferred volatilities do not count. |
| 12 | `business-view.md` is emitted without a `#### Lens Coverage Ledger`, or the ledger omits a lens (fewer than L1-L12) or leaves a verdict blank. | R-27, Step 1.2 | Incomplete discovery sweep. Complete the ledger: every lens L1-L12 must carry an explicit verdict (OQ IDs or `none`). A blank or missing lens is treated as not-yet-applied, not as a clean result. |

---

## Worked example

See `sad/examples/ev-charging-sad.md` §1 (Naïve Architecture) for a complete worked example. The naïve EV charging architecture is intentionally minimal: one `ChargeSessionManager`, one `AuthEngine`, two `ResourceAccess` components (`CustomerAccess`, `ChargerAccess`), two `Resource` instances (`CustomerDB`, `Charger hardware`). The "What the naïve architecture explicitly ignores" subsection lists 12 categories of unaddressed stress -- the menu the downstream stressor analysis starts from.

---

## Why these rules

- **R-01 / R-21.** Naïve does not mean "wrong". The naïve architecture must be a coherent residue-based starting point that respects volatility as one input signal. Cleverness erodes the control baseline.
- **R-02, R-03, R-04.** The IDesign call rules are P-raising mechanisms (see `shared/kauffman-nkp.md` §5). Even the naïve baseline must respect them, or the contagion analysis will diagnose K issues that are really call-rule violations in disguise.
- **R-05, R-06, R-07.** Names communicate intent. A naïve architecture with leaky names (technology vocab, verb prefixes) misdirects every downstream sub-skill.
- **R-11.** Expendable Managers in the naïve architecture become hot columns in the Contagion Matrix later. Catch them now.
- **R-16.** Use-case-driven naming in the naïve architecture cascades into use-case-driven residues. Naïve does NOT mean use-case-organized.

---

## References

- `shared/constitution.md` -- R-01, R-02, R-03, R-04, R-05, R-06, R-07, R-09, R-11, R-16, R-21, R-27 (Open Questions surfaced + gate S1a warning).
- `shared/idesign-vocabulary.md` -- the four layers + Utilities Bar; component taxonomy; call rules table; the Four Questions §7.
- `shared/glossary.md` -- vocabulary for terms used in the Business View and Naïve Architecture sections.
- `sad/template.md` §Business View, §Naïve Architecture -- the SAD sections this sub-skill fills.
- `sad/synthesis-explanation.md` §6 Decision 1 -- the procedural ordering that places stress analysis after this sub-skill, not before.
- `sad/examples/ev-charging-sad.md` §1 -- worked example.
- `righting-software-md/righting-software-juval-lowy-only-need.md` L981-1075 (typical layers), L1107-1129 (four questions), L1163-1171 (almost-expendable Manager).
