---
name: business-reconstruction
description: Sub-skill of the recon meta-skill. Produces the reconstructed-business-view.md fragment -- the inferred objective / users / pain points / goals deduced from the implementation, git history, and naming, EACH labelled inferred with a confidence level (high/medium/low) and the evidence behind it (RE-02). Feeds the SAD's business framing plane -> S1a. Invoke as gate R3 after R1 + R2 are approved; refuse if the priors are not approved or if a real PRD/SRD already exists.
task_types: [business-reconstruction, reconstruct-business-view, infer-intent, phase0-business-framing]
shared_refs:
  - ../../shared/constitution.md
  - ../../shared/evidence-anchoring.md
  - ../../shared/glossary.md
  - ../../templates/reconstructed-business-view.md
---

# business-reconstruction (R3)

The third sequential producer of the `recon` meta-skill. R1 (`system-cartography`) and R2 (`behavior-reconstruction`) described the observable **WHAT** -- the entry points, services, data stores, and the flows the system actually runs -- each claim anchored to `file:line` or a commit (RE-01). R3 is different in kind. It reconstructs the **WHY** and the **WHO**: the business objective the system serves, the users it is built for, the pain points it exists to relieve, and the goals that define success. None of that is observable fact. Business intent is almost never written in the code, so R3 does not *read* it -- it **infers** it from the structure R1 and R2 surfaced plus git history, naming, commit messages, and test assertions.

Because every claim in this fragment is a deduction, not an observation, the load-bearing discipline is **confidence labelling** (RE-02): every intent claim is explicitly marked *inferred*, carries a confidence level (`high` / `medium` / `low`), and cites the evidence the inference rests on. Intent is **never** stated as fact. A `Subscription` aggregate, a `trialEndsAt` field, and a cron that emails lapsed users may together suggest "the business monetises via recurring subscriptions with a trial" -- a reasonable inference, but an inference, and the next reader must be able to see exactly how much weight it bears. The confidence ladder:

- **high** -- multiple independent anchors of different kinds converge on this reading and nothing in the code contradicts it. The SAD can reasonably proceed on it.
- **medium** -- the evidence is suggestive but thin, single-sourced, or partly ambiguous. Worth recording; a stakeholder should confirm.
- **low** -- a plausible hypothesis the architect would not bet on. Recorded so it is not lost, flagged so it is not trusted.

The one calibration rule that governs everything below: **confidence is set by the weakest link in the inference chain, not by how plausible the conclusion sounds.** "Enterprise SaaS" inferred from a single `Tenant` class is `low`, however confident the prose reads. This fragment becomes the SAD's **S1a Business View** input -- the SAD treats a `high`-confidence framing very differently from a pile of `low` guesses, so flattening the confidence builds the SAD on sand. Read `../../shared/evidence-anchoring.md` §2 (confidence calibration) before producing anything.

---

## When to invoke

- The operator asks to "reconstruct the business view", "infer why this system exists / who it is for", or "produce the Phase-0 business framing" -- and **R1 and R2 are both `[x] approved`** in the gate tracker.
- The system is brownfield with **no current PRD/SRD**: there is no authored business document, so the framing must be *generated from the code*. This is recon's distinctive contribution -- the SAD's S1 cannot frame a system it has never read.
- The orchestrator/router has routed here per the root `SKILL.md` §Orchestration Step 3 after confirming the prior gate against the tracker.

## When NOT to invoke

- **R1 or R2 is not `[x] approved`.** R3 consumes both; producing it on top of an unapproved inventory or flow map is the premature-advance error (see §Pre-conditions). Refuse and point to the open gate.
- **A real PRD/SRD already exists and is current.** Recon's job is to *generate* the business framing only when no document exists. If a genuine business document exists, take it straight to the SAD's S1a -- do not have R3 manufacture an inferred view that competes with an authored one. Route to the SAD (`sad-*` `business-discovery`).
- **The operator wants a redesign, a "better" business model, or product recommendations.** R3 reconstructs the intent the system *appears* to embody; it never prescribes what the business *should* do. Recommendations are out of scope (and would muddy the SAD's S1a).
- A line-level code review or bug hunt -- route to general engineering tooling.

## Pre-conditions

Requires **both R1 AND R2 marked `[x] approved`** in the `FLOW.md` gate tracker (`<target-root>/docs/reverse-engineer/FLOW.md` §Current session). Per the root `SKILL.md` §Gate approval protocol:

1. **Verify the tracker, not merely the files.** Confirm the R1 and R2 rows are `[x] approved`, and confirm `system-cartography.md` and `behavior-reconstruction.md` exist on disk (disk wins -- a gate marked `[x]` whose fragment is absent is degraded to `[ ]`).
2. If either prior gate is not `[x] approved`, **refuse** and surface the open gate ("R3 needs R1 + R2 approved; R2 is still `[?] awaiting review`"). No `--force`.
3. Also verify tracker coherence (RE-05): the `[x]` chain is contiguous and at most one gate is active. A coherence violation -> refuse to route until the operator resolves it.

R3 has two prior gates because it reasons over both the inventory (R1) and the behaviour (R2) to infer intent; it cannot run on R1 alone.

## Handoff contract

Runtime-agnostic interface (a single LLM reads these inputs; an agent receives them as the message payload):

- **Consumes:** the approved `system-cartography.md` (R1) and `behavior-reconstruction.md` (R2), plus their **carry-forward notes** -- which domain aggregates/entities R1 found, which auth roles and client types it identified, the directory structure and key endpoints, and the dominant flows R2 reconstructed. These are the raw inference signals.
- **Produces:** `reconstructed-business-view.md` (per `../../templates/reconstructed-business-view.md`), parked behind gate **R3** `[?] awaiting review`. One fragment, then STOP.
- **Carry-forward context:** the **confidence summary** (N high / M medium / K low) and the **open questions for a stakeholder**. These travel forward so the operator and the downstream SAD know whether the business framing is a solid foundation (`high` dominant) or a hypothesis that needs stakeholder confirmation (`low`/`medium` dominant). The open-questions list maps directly onto the SAD's S1a Open Questions.

---

## Workflow

### Step 1 -- Gather the inference signals

Do not start writing intent. First assemble the raw signals from R1 + R2 and the repo, capturing each as an anchor you can cite later:

- **Domain aggregates / entities** -- the nouns the system models (`grep -rn "class .*Aggregate\|public class" src/Domain/` or per stack). A `Subscription`, `Invoice`, `Plan` cluster says far more about intent than any comment.
- **Auth roles & client types** -- role enums, policy names, the kinds of client apps that call the API (from R1). These reveal *who* the system serves.
- **Directory structure** -- top-level domain folders (`billing/`, `fulfilment/`, `compliance/`) are intent signposts.
- **Key endpoints** (from R1) and **dominant flows** (from R2) -- what the system spends its surface area on.
- **Git-history weight** -- where the development effort actually went: `git log --oneline -- <path> | wc -l` per domain folder. A 3-year history dominated by `src/Domain/Billing/` is strong evidence the business *is* billing.
- **Commit messages** -- developers narrate intent in commits they never write in code (`git log --oneline --grep="<domain>"`). Capture the SHA.
- **Naming** -- class, method, and config names that name a business concept.
- **Test assertions** -- tests encode expected outcomes; a test asserting an SLA or a business rule is intent made executable.
- **Declared intent in documentation (RE-01 §6).** Sweep **every** doc artifact (READMEs, `CLAUDE.md` / `AGENTS.md`, `docs/**`, `*.puml`, ADRs) -- state the command + count so the sweep is complete; nothing is discarded. Documentation is a *strong intent signal* even where it is weak capability evidence: a README that declares a goal the code has not built is direct testimony of what the team **intended**. In particular, pull R2's **`⚑ declared (not observed)`** items forward -- a declared-but-unbuilt use case is high-value *intent* (it tells you what the system is *for*) and low-value *capability* (it is not running). Weight it under RE-02 accordingly: it can support an inferred objective/goal as `medium`/`low` "stated intent, not observed capability", never as a `high` resting on docs alone.

### Step 2 -- Infer the OBJECTIVE

State, in one business-terms paragraph, what the system is *for* -- explicitly **as inferred, not as fact**. Then set its confidence **by the converging anchors**: `high` only if several different *kinds* of anchor (domain types + a key flow + git-history weight, say) reinforce each other and nothing contradicts; `medium` if the picture is suggestive but single-sourced; `low` if it is a thin hypothesis. List every supporting anchor in the Evidence field (RE-01).

### Step 3 -- Infer the USERS / ACTORS

Deduce who the system is built to serve, from auth roles and policies, client app types, actor names in the domain model, and API consumers. One row per inferred actor: `Inferred actor | Evidence (file:line / role enum / client app) | Confidence`. A role enum with `Admin | Buyer | Supplier` is medium-to-high evidence for those actors; an actor invented with no anchor is dropped (RE-01).

### Step 4 -- Infer the PAIN POINTS

Deduce the problems the system appears built to relieve -- from what it *automates* (a cron that replaces a manual task), what it *replaces*, and what the commit history shows it *iterating on* (a feature touched repeatedly was a real pain). One row per pain point: `Inferred pain point | Evidence | Confidence`. e.g. "manual month-end reconciliation" backed by a `ReconciliationJob` (`file:line`) plus a commit "automate the reconciliation slog" (`<sha>`) -> medium, because no PRD confirms the business pain directly.

### Step 5 -- Infer the GOALS

Deduce the observable outcomes the system appears designed to achieve, from features, metrics, **SLAs in config**, and **test assertions** (which encode expected behaviour). One row per goal: `Inferred goal | Evidence | Confidence`. A configured timeout or a test asserting a throughput floor is stronger evidence of a goal than prose ever is.

### Step 6 -- Write the inference-method note

One short paragraph stating **which signals** you drew on (directory structure, domain model, git history, tests, naming) and the **dominant sources of uncertainty**. This is what lets a reviewer judge whether your confidences are calibrated -- it exposes the inference chain so a mis-calibrated `high` is catchable. Without it the confidence labels are unauditable.

### Step 7 -- List OPEN QUESTIONS for a stakeholder

The intent questions the code **cannot answer**: every `low` and `medium` item from Steps 2-5, plus genuine ambiguities (two readings the code can't disambiguate, an actor whose real-world identity is unknown). One row per question: `# | Question | Why the code can't answer it | Affects (which inferred objective/goal)`. This list **maps directly onto the SAD's S1a Open Questions** -- it is how the SAD knows what to ask a human before building on the framing. If the inferences are all genuinely `high`, the list may be short, but ambiguities the code cannot settle still belong here.

### Step 8 -- Confidence summary tally

One line: `N high, M medium, K low`. **Compute it by counting the actual Confidence cells you just wrote** -- the §Inferred objective (1) plus every row of the §Inferred users, §Inferred pain points, and §Inferred goals tables. Do NOT type a remembered number: the tally MUST equal the row counts, and the `recon-auditor` verifies this deterministically (RE-02). If `low`/`medium` dominate, **say so plainly**: the business framing is a hypothesis the SAD should confirm with a stakeholder, not a settled foundation. This honest tally is the signal the carry-forward depends on.

### Step 9 -- STOP at gate R3

Write `reconstructed-business-view.md`, park gate **R3** `[?] awaiting review`, present it, and stop. The orchestrator runs `recon-auditor` `by-gate` (the cadence calls this out specifically at the close of R3, the inference-heavy gate) before the operator approves. Do **not** advance to R4. One fragment, then STOP (RE-05).

> **The trap this gate exists to catch.** R3 is exactly where the model most wants to narrate a confident product story. A fluent paragraph -- "the system is designed for enterprise customers who need advanced reporting" -- reads like a finding but is unanchored intent dressed as fact. **A confident tone is not evidence.** An "enterprise customers" claim with no anchor is an RE-02 violation: either anchor it and weight it (`low`, with the one `Report` class it rests on), or drop it. Never let the prose's confidence outrun the anchors beneath it.

---

## Open-question resolution pass (operator-triggered, optional)

After R3 is parked (`[?]`) the operator may ask the Reverse-Engineer to take a pass at the §Open
questions before the SAD handoff -- using the code to answer what the code *can* answer, and cleanly
escalating the rest. This is **not** a new gate and does **not** change R3's state; it edits
`reconstructed-business-view.md` in place while the gate waits.

For **each** row in §Open questions for a stakeholder, run a targeted investigation and choose **exactly
one** of two outcomes -- never a third:

1. **Resolve (with an anchor).** If a real anchor in the target answers the question, rewrite the row to
   `Resolved: <answer> (`file:line` / commit)`. If the resolution changes a confidence judgement
   elsewhere in the fragment (e.g. an inferred goal can now move `low` -> `medium` because the question
   that capped it is answered), update that row's **Confidence** + **Evidence** and **recompute the
   §Confidence summary tally from the rows** (RE-02 deterministic, per 0.1.1).
2. **Escalate (stakeholder-required).** If the code genuinely cannot answer it -- the question turns on
   business intent, a human decision, or external context not present in the repo -- mark the row
   `Stakeholder required: <one line on why the code cannot answer it>`. Leave it open.

**The forbidden third outcome -- never do this:** invent or assert an answer that has no `file:line` /
commit anchor. An unanswerable question is *escalated*, not *guessed*. A confident-sounding paragraph is
not a resolution. This is RE-01 (anchor or degrade) and RE-02 (no un-anchored intent stated as fact)
applied to the open questions themselves: a `Resolved:` row is a claim row and therefore **must** carry
an anchor; a row with no anchor must read `Stakeholder required:`.

**Calibration (RE-02).** Resolving a question with a single thin anchor does not licence a `high`
confidence elsewhere -- the weakest-link rule still governs. Prefer escalation over a weak resolution.

This pass is idempotent: re-running it re-investigates only the rows still marked open/stakeholder-
required and leaves `Resolved:` rows untouched unless new evidence overturns them.

---

## Output contract

`reconstructed-business-view.md`, structured per `../../templates/reconstructed-business-view.md`:

- `# Reconstructed Business View -- <target name>`
- `## Inferred objective` -- the paragraph + **Confidence** + **Evidence**.
- `## Inferred users / actors` -- table, each row `Inferred actor | Evidence | Confidence`.
- `## Inferred pain points` -- table, each row `Inferred pain point | Evidence | Confidence`.
- `## Inferred goals` -- table, each row `Inferred goal | Evidence | Confidence`.
- `## Inference method note` -- the signals used + dominant uncertainties.
- `## Open questions for a stakeholder` -- the table mapping to SAD S1a Open Questions.
- `## Confidence summary` -- the one-line tally.

**Every intent claim carries a Confidence cell (`high|medium|low`) and a non-empty Evidence anchor.** No frontmatter -- the fragment is inlined as the SAD's Business View input. This fragment feeds the SAD's **business framing** plane -> **S1a** (`business-discovery`).

---

## Refusal conditions

The sub-skill refuses to write the fragment (or degrades the offending claim) and returns the specific violation when:

| # | Trigger | Rule | Returned message |
|---|---|---|---|
| 1 | R1 or R2 is not `[x] approved` in the tracker (or its fragment is absent on disk). | RE-05, Pre-conditions | Stop. "R3 requires R1 + R2 approved; `<gate>` is `<state>`." Point to the open gate; do not produce on an unapproved prior. No `--force`. |
| 2 | An intent claim is stated as fact with no confidence label, or with no evidence anchor. | RE-02 | Reject the bare claim. Every objective / actor / pain point / goal must be marked inferred, carry `high\|medium\|low`, and cite an anchor. Add them or drop the claim. |
| 3 | A `high` confidence is backed by a single weak anchor (e.g. one suggestive directory name). | RE-02 (mis-calibration) | Downgrade. Confidence is the weakest link in the inference, not the plausibility of the conclusion. One thin anchor is `low`/`medium`, not `high`. |
| 4 | An inferred intent has no supporting anchor at all (invented to complete a tidy story). | RE-01 | Drop it. An unanchored intent claim is confabulation; it does not survive into the fragment, even quarantined, unless a real (if weak) anchor exists -> then `low`. |
| 5 | A current, real PRD/SRD already exists and the operator is asking R3 to write the business view a stakeholder should author. | When NOT to invoke | Refuse and route to the SAD's S1a. Recon generates framing only when no document exists; it does not compete with an authored business view. |

---

## Why these rules

R3 is the **inference-heavy gate**, and inference is precisely where a language model is most fluent and least grounded. R1, R2, and R4 describe what is observably on disk; R3 reconstructs what was never written down. That is genuinely useful -- the SAD's S1 cannot frame a system it has never read, and recon's whole reason for being is the brownfield case where no business document exists. But it is also the gate where the model most wants to narrate a confident, coherent product story that *sounds* like understanding while resting on almost nothing.

The confidence labels are the defence. They are the **load-bearing signal** that lets the SAD proceed on a `high`-confidence framing and *seek a stakeholder* on a `low` one. Strip them -- flatten every inference into a flat declarative paragraph -- and you have handed the SAD a pile of guesses indistinguishable from findings, and it will build the naïve baseline (and everything downstream) on sand. The discipline that keeps this gate honest is the same one that runs through the whole skill: anchor every claim, weight every inference by its weakest link, and never let a confident tone substitute for evidence.

---

## References

- `../../shared/constitution.md` -- **RE-02** (inferred intent labelled with confidence + evidence -- R3's governing rule), **RE-01** (every supporting fact anchored), **RE-05** (tracker coherence; one fragment then STOP).
- `../../shared/evidence-anchoring.md` -- **§2 confidence calibration** (the ladder and the weakest-link rule -- central to R3), §1 anchor forms, §3 the `⚠ unverified` quarantine.
- `../../shared/glossary.md` -- inferred intent, confidence (high/medium/low), anchor, brownfield, the three planes.
- `../../templates/reconstructed-business-view.md` -- the fragment R3 fills; the output contract must match it.
- root `SKILL.md` -- §Gate approval protocol, §Orchestration (routing, the R3 auditor cadence), and the three-plane handoff.
- The SAD's `business-discovery` (S1a) -- the downstream consumer: this fragment becomes the SAD's Business View input, and its open questions become the SAD's S1a Open Questions.
