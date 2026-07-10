---
title: Constitution -- Brownfield Recon meta-skill
version: 1.4
date: 2026-06-18
---

# Constitution

Single source of truth for the rules enforced by the `recon` meta-skill. Every sub-skill cites by `RE-NN`. The `recon-auditor` sub-skill enforces these rules at every gate.

When a rule appears to conflict with anything else in the repository, this file wins.

The recon skill exists to **read an existing, running system and reconstruct the three planes a SAD needs as Phase-0 evidence** -- a business framing, an as-built audit, and observed stressors -- *without inventing structure*. Reverse engineering is exactly the place an LLM confabulates with confidence: it sees three files and narrates a microservice topology that does not exist. The whole skill is built around one defence against that failure: **every claim is anchored to evidence on disk, or it is degraded.** The five rules below are that defence made operational.

## How to read a rule

Each rule has:

- **Statement.** One-sentence claim.
- **Mechanism.** `deterministic` (mechanically verifiable), `heuristic` (requires LLM judgment), or `both`. Determines the auditor's approach.
- **Body.** Explanation of scope, motivation, edges.
- **Verification.** How to detect a violation.
- **Valid example** + **Anti-example.** Drawn from a recon run over a real repo.

The numbering RE-01 to RE-05 is contiguous; there are 5 active rules. They are deliberately few -- the recon skill is a producer with a narrow remit, not a full design method. The SAD's own 26 rules (`sad-*/shared/constitution.md`) take over once the handoff lands.

---

## RE-01. Evidence anchoring -- every claim cites `file:line` or a commit, or it is degraded

**Statement.** Every assertion in every recon fragment cites a concrete evidence anchor: a `path:line` (or `path:line-range`), a commit SHA, or a command + its observed output. An assertion with no anchor is either deleted or kept and marked `⚠ unverified`; it is never presented as established fact.

**Mechanism.** `both` -- deterministic for the *presence* of an anchor on each claim row, AND, when an anchor carries an expected snippet (`path:line ~ token`), deterministic for whether that token is *on the cited line*; heuristic for whether an unsnippeted anchor actually *supports* the claim.

**Body.** This is the recon skill's "disk wins". Reverse engineering inverts the normal direction of a SAD: instead of designing forward from a PRD, the skill reads backward from code that already runs. The danger is not omission -- it is **confident fabrication**: the model reads `OrderService.cs`, sees a `PaymentClient` field, and writes "the system integrates with Stripe via a dedicated payment gateway service" when the field is an unused stub. The anchor requirement makes every claim falsifiable by a human in one click: open the file, go to the line, see whether the claim holds. A fragment is a set of anchored observations, not a narrative. Where the evidence is a dynamic observation rather than a static line (a log line, a `git log` count, a test that passes), the anchor is the command and its output, captured verbatim. The `⚠ unverified` mark is not a loophole -- it is a quarantine: it lets a genuinely useful hypothesis survive into review while making it impossible to mistake for fact. A fragment that is mostly `⚠ unverified` is a fragment that was not actually grounded in the code, and the auditor says so.

**Documentation is evidence too -- but a weaker class: a claim, not a proof.** A brownfield repo often *does* carry documentation -- READMEs, `CLAUDE.md` / `AGENTS.md`, `docs/**`, `*.puml` sequence diagrams, `*.http` request specs, ADRs, migration notes, intent-bearing comments. It is **never ignored** -- *no information in the target repo is discarded; all of it is valuable, which is the whole point of sweeping it* -- but it is **ranked below code**. Code is the source of truth (documentation goes stale); a **documentation anchor** records what the authors *say* the system does or intends, a **code anchor** records what it *does*. Every documentation-sourced claim therefore resolves into exactly one of three states: **(1) confirmed** -- the docs declared it and code/tests prove it, so it enters as an observed fact (the doc was the lead, the code is the proof); **(2) `⚑ declared (not observed)`** -- the docs declare a capability the code does not implement, captured as a first-class, segregated finding (an intended-but-unbuilt **milestone**), anchored to the doc that declares it, never mixed into observed facts and never silently dropped -- an intention the team wrote down but did not build is exactly the signal a downstream reader must keep the option to act on (and may cleanly discard later if it does not apply); **(3) drift** -- the docs assert something the code contradicts, recorded as a discrepancy. For the *audit* plane (R1 / R2 = what the system **is** / **does**), a claim resting only on a documentation anchor is not an observed fact -- it is `⚑ declared (not observed)` until a code anchor confirms it. (For R3 *intent*, documentation legitimately carries more weight -- intent is rarely written in code -- but still under RE-02 confidence.) The corollary is a **completeness duty**: the producer enumerates the repo's information-bearing artifacts with a command + count (so coverage is auditable, exactly as entry points are) and accounts for **every** one -- nothing escapes the sweep.

**Verification.** Deterministic: (a) every claim-bearing row / bullet in a fragment carries an anchor token matching `([\w./-]+:\d+(-\d+)?)` (file:line), a 7-40 hex commit SHA, or a fenced command-output block; rows without one and without an explicit `⚠ unverified` mark are violations. (b) line-resolvability -- a cited line past its file's end is a mechanical false anchor. (c) content -- when an anchor carries an expected snippet (`path:line ~ token`), the token must appear on the cited line; an off-by-one (the line exists but proves the wrong fact) is a mechanical false anchor too. Checks (b) and (c) are settled exhaustively by `tools/check-anchors.py`. Heuristic: spot-check the *unsnippeted* anchors -- open the cited line and confirm it supports the claim (a `file:line` that points at an unrelated line, or a commit that does not contain the cited change, is a false anchor and worse than no anchor). The snippet turns the highest-frequency false anchor -- the off-by-one whose line still exists -- from a fallible manual read into a hard, reproducible failure. (d) Documentation ranking -- an *audit*-plane (R1 / R2) claim whose only anchor is a documentation file (`.md` / README / `.puml` / `.http` / an intent-bearing comment) and which is **not** marked `⚑ declared (not observed)` is treated as an unconfirmed claim, not an observed fact. (e) Completeness -- the producer's documentation sweep enumerates the repo's information-bearing artifacts with a command + count; an artifact present on disk but unaccounted-for in the fragment is a coverage gap. (f) Count verification -- every enumeration / count claim is a fenced ```` ```verify ```` block (command + verbatim output); `tools/check-counts.py` re-runs the command (read-only whitelist, no shell) and a count that does not match the re-run is a mechanical false claim. (b), (c), (e), (f) are settled by tested scripts. Heuristic: judge whether a `⚑ declared (not observed)` is genuinely unbuilt (the code really lacks it) versus merely built somewhere the sweep did not look.

**Valid example.** R1 system-cartography: "HTTP entry point: `POST /api/orders` handled by `OrdersController.Create` -- `src/Api/Controllers/OrdersController.cs:42`. Persists via `OrderRepository.Save` -- `src/Data/OrderRepository.cs:88`."

**Anti-example.** R1: "The system uses an event-driven architecture with a message bus for inter-service communication." -- no anchor, no file, no line. If there is a `IBus` reference at `src/Infra/Bus.cs:12` that is unused dead code, this claim is fabrication; if there is a real RabbitMQ publisher, cite it. Either way the unanchored sentence is a violation.

---

## RE-02. Inferred intent is labelled, with confidence and the evidence that supports it

**Statement.** In R3 (business reconstruction), any statement of business *intent* -- objective, users, pain points, goals -- is explicitly marked as **inferred**, carries a confidence level (`high` / `medium` / `low`), and cites the evidence (code, naming, git history, tests) that the inference rests on. Intent is never presented as fact when it is a deduction from the implementation.

**Mechanism.** `both` -- deterministic for the presence of a confidence level + evidence on each intent claim; heuristic for whether the confidence is calibrated to the evidence.

**Body.** R1, R2, and R4 describe what is observably *there* (RE-03). R3 is different in kind: business intent is almost never written in the code, so R3 reconstructs it by inference -- a directory called `billing/`, a `Subscription` entity with a `trialEndsAt` field, and a cron job that emails lapsed users together suggest "the business monetises via recurring subscriptions with a trial". That is a reasonable inference, but it is an inference, and the next reader (the SAD's S1a) must be able to see exactly how much weight it bears. Confidence is the load-bearing signal: `high` means multiple independent anchors converge and there is no contradicting evidence; `medium` means the evidence is suggestive but thin or partly ambiguous; `low` means it is a hypothesis worth recording but easily wrong. The SAD treats a `high`-confidence business framing very differently from a pile of `low` guesses -- it may proceed on the former and must seek a stakeholder on the latter. Stripping the confidence flattens that signal and invites the SAD to build on sand.

**Verification.** Deterministic: every R3 intent claim row has a `Confidence` cell with one of `high|medium|low` and a non-empty `Evidence` anchor (per RE-01). A bare intent statement with no confidence is a violation. Heuristic: a `high` confidence backed by a single weak anchor (one suggestive directory name) is mis-calibrated -- the auditor flags it as a concern.

**Valid example.** R3: "Inferred objective: the system is a B2B subscription billing platform. **Confidence: high.** Evidence: `Subscription`, `Invoice`, `Plan` aggregates (`src/Domain/Billing/*.cs`); Stripe webhook handler at `src/Api/Webhooks/StripeController.cs:30`; 3-year commit history dominated by billing features (`git log --oneline -- src/Domain/Billing/ | wc -l` -> 412)."

**Anti-example.** R3: "The system is designed for enterprise customers who need advanced reporting." -- stated as fact, no confidence, no evidence. There may be a `Report` class, but "enterprise customers" and "advanced" are unanchored intent dressed as finding. Either mark it `low` with the `Report`-class anchor, or drop it.

---

## RE-03. Descriptive, not prescriptive -- describe what exists, never redesign

**Statement.** R1, R2, and R4 describe the system **as it is**. They do not say what the system *should* be, propose refactors, rename components to "better" names, or impose a target architecture. Zero redesign -- that is the SAD's job, downstream.

**Mechanism.** `heuristic`.

**Body.** This rule protects the empirical test at the heart of the SAD. The SAD measures a residual (stress-driven) architecture against a *naïve* baseline via the Ri test (sad S6). The existing implementation enters the SAD as a **residual candidate** that S6 measures -- it is evidence, not the baseline. If recon smuggles redesign into its description ("this God-class `OrderManager` should be split into three services"), it does two damaging things: it contaminates the naïve baseline the SAD must build independently, and it pre-empts the stressor analysis that is supposed to *derive* whether that split is justified. Recon's job is to hold up a clean, honest mirror. The temptation is strong because a competent engineer reading messy code naturally thinks in fixes; RE-03 says: record the mess with anchors, name the coupling you observe (that is RE-04 territory), but do not prescribe the cure. Describe the God-class, cite its 2,000 lines and 40 dependencies, observe the contagion -- and stop. The use of existing names (even bad ones) is mandatory: recon reports `OrderManager` because that is what the file is called (`src/OrderManager.cs:1`), not `OrderProcessingService` because that would be "more IDesign-correct". Renaming is a design act.

**Verification.** Heuristic. Look for: modal verbs of recommendation (`should`, `ought to`, `we recommend`, `the ideal`, `a better design`); proposed component names that do not exist in the code; target-state diagrams; refactor plans; any sentence that describes a system other than the one on disk. R4 specifically describes *observed* coupling/contagion -- it may say "changing X forces changing Y, observed across commits A, B, C" but not "X and Y should be decoupled".

**Valid example.** R1: "`OrderManager` (`src/OrderManager.cs:1`) is a 2,140-line class with direct references to 14 other classes (`grep -c 'using ' src/OrderManager.cs` and the constructor's 9 injected dependencies, lines 30-48). It handles HTTP request parsing, pricing, persistence, and email." -- pure description, anchored, no judgment about whether this is good.

**Anti-example.** R1: "`OrderManager` is a God class that violates single-responsibility and should be decomposed into `OrderManager`, `PricingEngine`, and `OrderAccess` following IDesign." -- prescriptive. The decomposition is the SAD's call to make, derived from stressors, not recon's to assert.

---

## RE-04. Observed stressors only -- speculation is labelled and segregated

**Statement.** Every stressor in R4 cites real evidence of stress already in the system: a production incident, a churn/hotspot measurement, a coupling metric, a TODO/FIXME/workaround in the code, a revert, a bug-fix cluster. Stressors the architect *anticipates* but cannot anchor to observed evidence are permitted, but only in a clearly separated `Anticipated (not observed)` section, never mixed into the observed list.

**Mechanism.** `both` -- deterministic for the observed/anticipated separation + presence of an anchor on each observed stressor; heuristic for whether the cited evidence genuinely indicates stress.

**Body.** R4 produces two things the SAD consumes: the **residual candidate** (the as-built typed in IDesign terms, fed to S6) and the **observed stressors** (fed to S3). The stressors are the high-value output, and they are precisely where confident invention is most tempting -- "this system probably struggles under high load" reads like analysis but is a guess. The discipline that makes R4 trustworthy is the same as RE-01 applied to stress: a stressor counts as *observed* only if the system itself testifies to it. The forms of testimony are concrete: a file that changes far more often than its neighbours (churn -- `git log --format= --name-only | sort | uniq -c | sort -rn`), a cluster of bug-fix commits touching the same module, a `// HACK: race condition under concurrent checkout` comment, an incident postmortem in the repo, two modules that always change together (contagion -- co-change analysis). Anticipated stressors are not worthless -- the SAD's S3 may well want them -- but they are a different epistemic class, and the SAD must be able to tell the difference, because S3's whole method is to generate anticipated stressors *itself*. Recon's observed stressors are the ones S3 cannot generate because they require having watched this specific system live. Mixing the two robs the SAD of exactly the signal recon is uniquely able to provide.

**Verification.** Deterministic: the R4 fragment has a `## Observed stressors` section and a separate `## Anticipated (not observed)` section (the latter may be empty); every row under Observed carries an evidence anchor (incident link, churn count + command, coupling metric, `file:line` of a HACK/TODO, commit SHA). An observed-section row with no anchor, or an anticipated stressor sitting in the observed section, is a violation. Heuristic: does the anchor actually indicate stress? (A file with high churn because it is a config registry that legitimately grows is not necessarily under architectural stress -- the auditor flags weak inferences.)

**Valid example.** R4 Observed: "Checkout race condition. **Evidence:** `// HACK: lock here, double-charge under concurrent checkout` at `src/Checkout/PaymentProcessor.cs:204`; 6 bug-fix commits touching this file in 2025 (`git log --oneline --since=2025-01-01 --grep=charge -- src/Checkout/PaymentProcessor.cs`); incident `docs/incidents/2025-03-double-charge.md`."

**Anti-example.** R4 Observed: "The system will likely have scalability problems at high traffic." -- no incident, no metric, no anchor; this is an anticipated stressor stated as observed. It belongs (if kept at all) under `## Anticipated (not observed)`, labelled as a hypothesis.

---

## RE-05. Tracker & workspace coherence (NON-NEGOTIABLE)

**Statement.** The recon flow is structurally coherent on disk. **(Tracker)** the R-gate tracker in `FLOW.md` is coherent at every read: (1) the chain of `[x] approved` gates is contiguous from R1; (2) every active gate (`[~]` / `[?]` / `[i]`) has all prior gates `[x]`; (3) at most one gate is active at any time -- only the first gate after the last `[x]` may be active. **(Workspace)** recon writes its whole flow -- the `FLOW.md` tracker, the four R1-R4 fragments, the `r1-inventory.json` manifest, the `audit-iter-N.md` / `audit-drift-<ref>.md` reports, and the `phase0-evidence.md` bundle -- only under `<target-root>/docs/reverse-engineer/` (the recon role's own folder); it never writes into `docs/architecture/`, which is reserved for the downstream SAD deliverable.

**Mechanism.** `deterministic`.

**Body.** This is the direct mirror of the SAD's R-26, and it exists for the same reason: an out-of-band actor (a UI bug, a manual edit, a buggy orchestrator, a test fixture) can mutate the tracker into an incoherent state -- R3 marked `[x]` while R2 is still `[?]`, or two gates active at once -- without the executor ever getting a chance to refuse. The recon chain is strictly sequential (R1 -> R2 -> R3 -> R4; see each sub-skill's Pre-conditions), so the same three invariants that keep the SAD single-threaded keep recon single-threaded: at any moment there is exactly one decision pending for the operator. The single-active-gate rule (invariant 3) is what enforces "one fragment, then STOP for human review" as a state-shape property rather than a hope. Combined with the disk-wins rule (a gate marked `[?]`/`[x]`/`[i]` whose fragment is absent on disk is degraded to `[ ]`), this makes the tracker a faithful, falsifiable record of where the recon actually is. The **workspace** half guards the other on-disk structural fact: ADDL runs one lifecycle role per phase under `docs/`, and recon shares the tree with the SAD; if a recon artifact lands in `docs/architecture/` it collides by name with the SAD deliverable (`FLOW.md`, `audit-iter-N.md`). Which folder owns each artifact is a simple, binary rule -- exactly the kind of mechanical fact that must not live as prose the producing subagent can silently "correct" back to `docs/architecture/`. It is a single canonical mapping (recon-owned artifact -> `docs/reverse-engineer/`) made a hard check.

**Verification.** Deterministic. **(Tracker)** walk the tracker R1 -> R2 -> R3 -> R4 and verify the three invariants. Any `[x]` on a non-`[x]` prior, any active gate above an unapproved prior, or two active gates is a tracker inconsistency. The fix is binary: revert the offending gate to `[ ]`, or approve every missing prior. No `--force`. The router refuses to route on a violation (`SKILL.md` §Orchestration Step 1) and the auditor flags it (`recon-auditor` always-on check). **(Workspace)** `tools/check-workspace.py <target-root>` walks `docs/` and flags every recon-owned artifact (matched by canonical basename) that is not under `docs/reverse-engineer/`; a recon artifact under `docs/architecture/` -- or sitting loose elsewhere in `docs/` -- is a mechanical **`MISPLACED`** violation (exit 1). The SAD's own files in `docs/architecture/` are not recon-owned and are ignored. The fix is to move the artifact into `docs/reverse-engineer/`.

**Valid example.** Tracker shows R1 `[x]`, R2 `[x]`, R3 `[~]`, R4 `[ ]`; the workspace holds `docs/reverse-engineer/{FLOW.md, system-cartography.md, ...}` and nothing recon-owned under `docs/architecture/`. Contiguous approved chain (R1, R2); the single active gate (R3) has all priors approved; everything downstream is pending; every artifact in its own folder. Coherent.

**Anti-example.** Tracker shows R1 `[x]`, R2 `[?]`, R3 `[x]`, R4 `[ ]`. R3 is `[x]` while its prior R2 is only `[?]` -- the approval chain is not contiguous (invariant 1 broken). Or: `FLOW.md` was written to `docs/architecture/FLOW.md`, colliding with the SAD tracker -- a `MISPLACED` workspace violation. Either is a structural inconsistency the auditor flags and the router refuses to advance past.

---

## Cross-reference table

| Rule | Scope (gates) | Mechanism | What it defends |
|---|---|---|---|
| RE-01 Evidence anchoring | R1, R2, R3, R4 | both | Against confident fabrication -- every claim falsifiable on disk |
| RE-02 Inferred intent labelled | R3 | both | Against deduction dressed as fact -- the SAD sees how much weight intent bears |
| RE-03 Descriptive not prescriptive | R1, R2, R4 | heuristic | The SAD's naïve baseline and empirical Ri test (recon is a mirror, not a redesign) |
| RE-04 Observed stressors only | R4 | both | The signal only recon can supply -- stress this specific system has actually shown |
| RE-05 Tracker & workspace coherence | Router, all gates | deterministic | One-fragment-then-STOP as a state-shape invariant (mirror of SAD R-26) + recon writes only under `docs/reverse-engineer/`, never the SAD's `docs/architecture/` |

## References

- `shared/evidence-anchoring.md` -- the concrete how-to for RE-01 / RE-02 / RE-04 anchoring (anchor forms, confidence calibration, the `⚠ unverified` quarantine).
- `shared/glossary.md` -- vocabulary (residual candidate, observed stressor, the three planes, gate, fragment).
- The root `SKILL.md` -- the gate machine and router that enforce RE-05.
- `sad-*/shared/constitution.md` -- the SAD's 26 rules (R-01..R-27) that take over once the handoff lands; RE-03 exists to protect that constitution's empirical test (S6) and naïve baseline (S1b).
