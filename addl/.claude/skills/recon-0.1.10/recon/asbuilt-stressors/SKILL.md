---
name: asbuilt-stressors
description: Sub-skill of the recon meta-skill; produces the asbuilt-stressors.md fragment -- the existing implementation typed in IDesign terms (a residual candidate for the SAD's empirical test, never the baseline) plus the stressors the system has actually shown (incidents, churn, co-change, HACK/FIXME, bug-fix clusters), each anchored, with anticipated stressors segregated. Invoke as R4 after R3 is approved.
task_types: [asbuilt-stressors, asbuilt-audit, observed-stressors, residual-candidate, phase0-stressors]
shared_refs:
  - ../../shared/constitution.md
  - ../../shared/evidence-anchoring.md
  - ../../shared/glossary.md
  - ../../templates/asbuilt-stressors.md
---

# asbuilt-stressors (R4)

The final producer sub-skill of the meta-skill, and the one that yields the two highest-value outputs for the downstream SAD. R4 has two jobs. First, it **types the as-built**: every significant component R1 inventoried gets the closest IDesign role *as it actually behaves*, anchored. That typing is the **residual candidate** the SAD's S6 measures against its independently-built naïve baseline -- it is evidence, never the baseline (RE-03; treating it as the baseline would destroy the empirical Ri test). Second, it surfaces the **observed stressors**: the points of architectural stress *this specific system has already testified to* -- incidents, churn hotspots, co-change/contagion, `HACK`/`FIXME` markers, reverts, bug-fix clusters -- each anchored (RE-04).

The observed stressors are recon's unique contribution. The SAD's S3 (`stressor-analysis`) generates *anticipated* stressors by method -- it does that well, from the domain, without ever having watched the system run. What S3 **cannot** generate is the stress this code has actually shown in production and in its own history, because that requires having watched *this* system live. That is exactly what R4 supplies. So the discipline is sharp: observed stressors (anchored to the system's own testimony) go in `## Observed stressors`; stressors you merely *suspect* go in a separate, clearly-labelled `## Anticipated (not observed)` section. Mixing the two robs the SAD of the one signal recon is uniquely able to give it -- it cannot tell which stressors it must take seriously (the system already broke this way) from the ones it would have generated anyway.

Typing is **descriptive** (RE-03), and that is harder than it sounds because a competent engineer reading messy code naturally thinks in fixes. Record a God-class as a `Manager` that *also* does `Engine` and `ResourceAccess` work inline -- anchored, with the line count and dependency fan-out -- and **stop there**. Do NOT propose splitting it into three services, do NOT rename it to something "more correct", do NOT draw a target architecture. The SAD derives the split (if any) from the stressors; R4 holds up an honest mirror so S6 has clean evidence to measure. Describe the mess; name the coupling you observe; do not prescribe the cure.

---

## When to invoke

- The operator says "type the as-built in IDesign terms", "find the observed stressors", "where does this system actually hurt", "produce the residual candidate", or similar -- **and R3 is approved**.
- R1, R2, and R3 fragments are approved and you are advancing to the final producer gate before the SAD handoff.
- You need the two planes only R4 produces: the IDesign typing (-> SAD S6) and the observed stressors (-> SAD S3).

## When NOT to invoke

- **R3 is not yet `[x] approved`** in the tracker. R4 consumes R1's hot-module pointers and R2's convergence points; building it on an unapproved chain is the premature-advance error. Refuse and point at the open gate.
- The operator asks you to **propose a refactor, a "should decouple", or a target architecture**. RE-03 forbids it -- that is the SAD's job, derived downstream from the stressors R4 surfaces. Describe what is; route forward to the SAD for what should be.
- The operator asks you to **invent stressors** ("list the likely problems") with no evidence. A stressor with no anchor is not observed -- it is anticipated, and goes (if at all) in the segregated section, labelled as a hypothesis (RE-04).
- A line-level bug hunt or code review. R4 reconstructs architecture-level stress, not defect-level review.

## Pre-conditions

R4 requires **R3 `[x] approved`** in the gate tracker (`FLOW.md` §Current session) -- and transitively R1 + R2, since the approval chain is contiguous (RE-05). Per the root `SKILL.md` §Gate approval protocol, verify the prior gate is approved **in the tracker**, not merely that the prior fragment file exists on disk: a file can sit at `[?] awaiting review` or `[i] iterating`. If R3 is not `[x]`, refuse and surface the open gate ("R4 needs R3 approved; R3 is still awaiting review"). No `--force`.

Also honor the disk-wins rule: if the tracker says a prior gate is approved but its fragment is absent on disk, that gate is degraded to `[ ]` and R4 cannot proceed until it is genuinely re-produced and approved.

## Handoff contract

Runtime-agnostic (a single LLM reads these; an agent receives them as message payload):

- **Consumes:** the approved R1 `system-cartography.md`, R2 `behavior-reconstruction.md`, and R3 `reconstructed-business-view.md`, plus their carry-forward notes. The two most load-bearing inputs:
  - **R1's hot/large-module pointers** -- which modules looked big, coupled, or central. These tell R4 where to point churn and contagion analysis and which components most need typing.
  - **R2's convergence points** -- the flows where many paths meet (shared handlers, the one class every use case touches). Co-change and contagion concentrate here.
- **Produces:** `asbuilt-stressors.md` (per `../../templates/asbuilt-stressors.md`) behind gate **R4**, then STOPS for human review. One fragment per turn.
- **Carry-forward (which plane each part feeds):** the **IDesign typing** is a *residual candidate* for the SAD's **S6** (evidence, never the baseline); the **Observed stressors** list is held for the SAD's **S3** (the part S3 cannot generate itself); the **Anticipated** list overlaps with what S3 produces by method and is flagged as such.

---

## Workflow

READ-ONLY over the target repo; writes only `asbuilt-stressors.md` under `docs/reverse-engineer/`. Every claim anchored (RE-01); descriptive only (RE-03); observed strictly separated from anticipated (RE-04).

### Step 1 -- Type the as-built (residual candidate)

For each significant component from R1's inventory (start with the hot/large/coupled modules R1 flagged), assign the **closest IDesign role as it actually behaves** -- Manager (workflow/orchestration), Engine (stateless activity/logic), ResourceAccess (state access), Resource (the store itself), Utility (cross-cutting infra), Client (entry point). The role vocabulary is the SAD's R-02 service hierarchy (see References).

- Type by **behavior, not by name**. A class named `...Service` that parses HTTP, prices, persists, and emails is a `Manager` that *also* does `Engine` + `ResourceAccess` work -- record exactly that in the Notes column ("mixes Manager+Engine+RA"). When one unit straddles roles, say so; do not pick one and hide the rest.
- **Anchor every row** (`file:line`, line range for a span, or a command + output for a metric) and use the **existing code name** -- `OrderManager` because the file is `src/OrderManager.cs:1`, not `OrderProcessingService` because that would be "more IDesign-correct". Renaming is a design act (RE-03).
- This is descriptive: it records how the as-built *maps onto* IDesign vocabulary so S6 can measure it -- **not** how it ought to be decomposed. Do not split, merge, or rename.

### Step 2 -- Measure observed coupling / contagion

Report modules that change together, measured from history -- focus on R2's convergence points first.

```bash
# Co-change / contagion: per-commit file sets; pairs that recur are coupled
git log --format= --name-only
# (group by commit; tally which file pairs co-occur across commits)
```

Report each recurring pair **descriptively** with its evidence ("changing A forced changing B, observed across commits `<sha1>`, `<sha2>`, `<sha3>` -- N of M commits"). State the strength as a count, not a verdict. Do NOT write "A and B should be decoupled" -- that is the SAD's call to derive (RE-03).

### Step 3 -- Surface OBSERVED stressors (the system's own testimony)

A stressor counts as observed only if you can point at the place in the repo or its history where the stress already showed itself. Use whichever sources apply; **each row carries its anchor**:

```bash
# Churn hotspots -- the raw signal: files that change far more than neighbours
git log --format= --name-only | sort | uniq -c | sort -rn | head -30

# Bug-fix clusters on a suspect module
git log --oneline --grep="fix\|bug\|hotfix\|charge\|race" -- <path>

# In-code stress markers
grep -rn "HACK\|FIXME\|XXX\|workaround\|race\|deadlock" src/

# Reverts (a change that had to be undone is testimony of stress)
git log --oneline --grep="revert"
```

Other testimony: production incident docs in the repo (`docs/incidents/*`), performance TODOs, retry/circuit-breaker code that marks a known failure mode. Capture command output **verbatim** -- the command IS the anchor; a reader re-runs it. A churn count alone is weak (a config registry legitimately grows); the strongest rows *converge* several anchors (a `// HACK` comment + a bug-fix cluster + an incident doc on the same file).

### Step 4 -- Record ANTICIPATED (not observed) stressors -- SEPARATE section

Stressors you suspect but **cannot anchor** to this system's evidence go in `## Anticipated (not observed)`, never in the observed list. Give the *reasoning* (not evidence) for each. This section may be empty -- do not pad it. The SAD's S3 generates these by method; R4 just flags what it sensed. The test: "can I point at where this stress already showed itself?" If no, it is anticipated.

### Step 5 -- Write handoff notes

State which plane each part feeds: the IDesign typing -> **S6** residual candidate (evidence, not the baseline); the Observed list -> **S3** (the part S3 cannot generate itself); the Anticipated list overlaps with S3's method output.

### Step 6 -- Gaps & `⚠ unverified`

Stress that only runtime/operational data would reveal -- load behavior, production error rates, latency under concurrency -- is knowable only with ops/observability access, not from the repo. Mark each such item `⚠ unverified` and say what anchor is missing. Do not promote a guess about load to the Observed section.

### Step 7 -- STOP at gate R4

Emit the single fragment, park it at gate R4 `[?]`, and STOP for human review. Do not advance. Once R4 is approved, the four fragments (R1 + R2 + R3 + R4) **together ARE** the SAD's three-plane Phase-0 evidence: R3 -> business framing (S1a); R1 + R2 + R4's typing -> the as-built audit / residual candidate (S6); R4's observed stressors -> S3. The optional `handoff-assembler` packages them into a single labelled `phase0-evidence.md`; it does not add content.

---

## Output contract

A single Markdown fragment, `asbuilt-stressors.md`, per `../../templates/asbuilt-stressors.md`, written to the project workspace (`docs/reverse-engineer/`). Sections:

- `## As-built IDesign typing (residual candidate)` -- the typing table (component / observed role / closest IDesign type / anchor / notes), descriptive, every row anchored. Feeds SAD **S6** as evidence (never the baseline).
- `## Observed coupling / contagion` -- co-change pairs with evidence and strength count, descriptive.
- `## Observed stressors` -- each row anchored to the system's testimony. Feeds SAD **S3**.
- `## Anticipated (not observed)` -- segregated, labelled, reasoning only. MUST be a section separate from Observed.
- `## Handoff notes` -- which plane each part feeds.
- `## Gaps & unverified` -- runtime-only stress marked `⚠ unverified`.

The `## Observed stressors` and `## Anticipated (not observed)` sections MUST be **separate** (RE-04, deterministic check). No frontmatter -- the fragment is meant to be inlined by the `handoff-assembler`.

---

## Refusal conditions

| # | Trigger | Rule | Returned message |
|---|---|---|---|
| 1 | R3 (and transitively R1/R2) is not `[x] approved` in the tracker. | RE-05, Pre-conditions | Stop. "R4 needs R3 approved; R3 is `<state>`." Point at the open gate; do not produce the fragment. No `--force`. |
| 2 | The request (or a draft row) proposes a redesign -- "should decouple", "split this Manager", a target architecture, or a "better" name. | RE-03 | Refuse the prescription. Recon describes what is; the SAD derives the redesign from the stressors. Record the as-built (mixed roles and all), anchored, and stop. |
| 3 | An observed stressor row has no evidence anchor. | RE-04, RE-01 | Drop it, or move it to `## Anticipated (not observed)` and label it a hypothesis. An unanchored stressor is not observed. |
| 4 | An anticipated/speculative stressor is placed in the `## Observed stressors` section ("probably struggles under load"). | RE-04 | Segregate it into `## Anticipated (not observed)`. The two epistemic classes must not mix -- it robs the SAD's S3 of the signal only recon supplies. |
| 5 | The typing re-decomposes the as-built into the "correct" components instead of typing what exists (renames, splits, invents components not in the code). | RE-03 | Type the components that exist, by their existing names, as they behave (note mixed roles). Decomposition is the SAD's call, derived downstream -- not recon's to assert. |

---

## Why these rules

- **Observed stressors are the signal only recon supplies.** S3 already generates anticipated stressors by method, from the domain, without the running system. The one thing it cannot do is know how *this* code actually broke -- that needs having watched it live. Mixing speculation into the observed list buries that unique signal under noise the SAD could have produced itself; segregation keeps it legible.
- **Typing, not redesigning, keeps the residual candidate honest as S6 evidence.** The SAD measures the residual against a naïve baseline it builds independently. If R4 smuggles in a redesign, it contaminates that baseline and pre-empts the stressor analysis that is supposed to *derive* whether the redesign is justified. An honest mirror is the only useful S6 input.
- **"This probably struggles under load" reads like analysis but is an unanchored guess.** It passes a human's "sounds right" filter and is nearly unfalsifiable. RE-04 forces every observed claim to point at the system's own testimony, so a reader can check it in one click -- and forces every guess into a section that announces itself as a guess.

---

## References

- `../../shared/constitution.md` -- **RE-01** (every claim anchored or degraded), **RE-03** (descriptive, not prescriptive -- type, do not redesign), **RE-04** (observed stressors only; anticipated segregated), **RE-05** (tracker coherence). RE-02 is R3's; R4 does not use it.
- `../../shared/evidence-anchoring.md` -- **§1** (anchor forms + the churn / co-change / HACK-grep / bug-fix-cluster commands) and **§4** (observed vs anticipated -- the test for "observed").
- `../../shared/glossary.md` -- *residual candidate*, *observed stressor*, *coupling / contagion (observed)*.
- `../../templates/asbuilt-stressors.md` -- the fragment shape this sub-skill fills (the Observed / Anticipated sections it must keep separate).
- `../../SKILL.md` -- the root: the gate approval protocol, the gate state machine (RE-05), and that R4 feeds **two** SAD planes (typing -> S6; observed stressors -> S3).
- `sad-*/shared/constitution.md` **R-02** (service hierarchy) -- the IDesign role vocabulary (Manager / Engine / ResourceAccess / Resource / Utility / Client) used for the as-built typing.
