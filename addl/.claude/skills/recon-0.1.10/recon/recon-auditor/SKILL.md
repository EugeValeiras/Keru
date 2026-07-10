---
name: recon-auditor
description: Cross-cutting sub-skill of the `recon` meta-skill. Validates a single recon fragment, all four fragments end-to-end, or the code-vs-prior-SAD/recon drift, against constitution rules RE-01 to RE-05. Runs deterministic checks first, heuristic checks second; produces `audit-iter-N.md` (or `audit-drift-<ref>.md` in drift mode) with violations citing RE-NN, false-anchor findings, and fix proposals in unified-diff format. Advisory -- the operator decides; no `--force`. Invoke at any gate before approval, end-to-end after R4, or periodically once a SAD/recon exists to detect drift.
task_types: [audit, validate-recon, check-fragment, audit-drift, detect-architecture-drift]
shared_refs:
  - ../../shared/constitution.md
  - ../../shared/evidence-anchoring.md
  - ../../shared/glossary.md
---

# recon-auditor (cross-cutting)

The auditor sub-skill. Validates the output of the recon chain against constitution rules **RE-01 to RE-05** (`shared/constitution.md`). It produces an audit report -- a separate artifact, not embedded in any fragment -- containing rule violations, false/missing-anchor findings, fix proposals in unified-diff format, and any accepted-exception entries the operator has documented.

The auditor's discipline is **conservative**: it does not silently fix anything. Every violation is reported with a proposed fix, but applying the fix is the responsibility of the producer sub-skill that emitted the offending fragment (R1..R4). The auditor closes an audit only when its deterministic violations are resolved or explicitly accepted-with-rationale, and its heuristic concerns have been reviewed. There is no `--force` flag.

The auditor is the **only** sub-skill that runs ACROSS the meta-skill rather than producing one fragment of the three-plane evidence. It can be invoked after any producer emits a fragment (by-gate), after R4 over all four fragments (end-to-end), or against a prior SAD/recon to detect drift (diff). Its findings are **advisory** -- they are facts about rule compliance, not an approval. Approval is a separate gate the operator owns (see the gate machine in the root `SKILL.md`).

---

## When to invoke

- Immediately after a producer sub-skill emits a fragment, **before** the operator approves it (`by-gate` mode). This is the cheap, routine check, run as a flow step per the root `SKILL.md` §Recommended auditor cadence -- it is where RE-01 (unanchored claims) and RE-02 (un-flagged intent) get caught before they propagate downstream.
- At the close of **R3** specifically: R3 is the inference-heavy gate (business intent reconstructed from code), so it is where mis-calibrated confidence (RE-02) and intent-stated-as-fact surface.
- After **R4** is emitted, before the handoff (`end-to-end` mode) -- the full RE-01..RE-05 pass over all four fragments plus tracker coherence.
- **Periodically once a SAD or recon already exists** (`diff` / drift mode) -- re-run recon over the evolved code and diff it against the prior SAD/recon to find where the documented architecture no longer matches the running one. This is the capability that keeps the architecture honest over time (root `SKILL.md` §The drift loop).

## When NOT to invoke

- **Before any fragment exists.** The auditor needs at least one fragment (by-gate / end-to-end) or a prior SAD/recon (diff) to audit. Refuse with a pre-condition message.
- **As a substitute for a producer.** The auditor checks; it does not produce evidence. If the operator wants an R3 business view, they run `business-reconstruction`, not the auditor. The auditor never writes fragment content.
- **To "approve" a fragment the operator is uneasy about.** The auditor reports rule-compliance facts (anchored / un-anchored, calibrated / mis-calibrated, coherent / incoherent tracker). Approval is a separate gate captured in `FLOW.md`. A clean audit is not consent; an operator's sign-off is.

## Modes of invocation

| Mode | Input | Scope of checks |
|---|---|---|
| **by-gate** | One fragment file (e.g., `system-cartography.md`) | The checks for that fragment's rule(s) -- RE-01 always; RE-02 if it is R3; RE-03 if R1/R2/R4; RE-04 if R4 -- **plus RE-05** (tracker coherence always runs). The fastest mode; runs during gate production before operator approval. |
| **end-to-end** | All four approved/produced fragments (R1..R4) | All of RE-01..RE-05 across every fragment, plus the RE-05 walk of the full tracker. The slowest mode; runs after R4. |
| **diff (drift)** | The current target code + the prior SAD/recon to diff against | Re-runs the recon observations over the evolved code and diffs them against the prior artifact. Output `audit-drift-<ref>.md`. See §Drift mode specifics. |

The mode is **declared by the operator** when invoking. If the mode is ambiguous, the auditor refuses with: **"specify mode: by-gate | end-to-end | diff"**.

## Pre-conditions per mode

| Mode | Pre-condition |
|---|---|
| by-gate | The named fragment file exists on disk. The `FLOW.md` gate tracker is readable (for the RE-05 walk). |
| end-to-end | R1..R4 fragments exist on disk (implies the chain ran). The `FLOW.md` tracker is readable. |
| diff (drift) | A prior SAD or recon artifact exists to diff against (the `<ref>` it diffs from). The current target repo is readable. |

---

## Workflow

### Step 1 -- Determine the check set

Given the mode and scope, build the set of checks to run. The full inventory is in §Check inventory below; each check is tagged with the rule and the fragment(s) it applies to. The auditor runs only the checks relevant to the scope -- but the two RE-05 checks (tracker coherence + workspace placement) **always** run whenever a `FLOW.md` / target repo is in scope, in every mode.

### Step 2 -- Run deterministic checks (always first)

Deterministic checks are mechanically verifiable: they produce binary pass/fail results and are cheap. Run **all** deterministic checks before any heuristic check. A fragment that fails RE-01 (an unanchored claim) has a more basic problem than any calibration nuance; there is no point spending heuristic judgment on it until the mechanical baseline is clean. If a deterministic check fails, the heuristic checks for the same rule may still run, but the violation is logged regardless.

### Step 3 -- Run heuristic checks (after the deterministic pass)

Heuristic checks require LLM judgment and produce graded results (`pass` / `concern` / `fail` with a confidence of `low` / `medium` / `high`). These are the checks that open a cited `file:line` and judge whether it actually supports the claim, whether a `high` confidence is calibrated, whether prose has crept into prescription, and whether a cited stressor genuinely indicates stress. A heuristic `concern` is not a violation -- it is an invitation to the operator to look again.

### Step 4 -- Generate fix proposals

For each violation, generate a fix proposal in **unified-diff format**, with:

- The affected fragment file path.
- The affected section / row / cell.
- The proposed change (added / removed / modified content).
- The rationale linking the fix to the rule (`RE-NN`).

Example:

```
File: reconstructed-business-view.md
Section: §Inferred objectives row #2
Rule: RE-02
Violation: intent claim has no Confidence cell.

Proposed change:
- | 2 | Targets enterprise customers needing advanced reporting | | `src/Reporting/Report.cs:1` |
+ | 2 | Targets enterprise customers needing advanced reporting | low | `src/Reporting/Report.cs:1` (single suggestive class; no PRD) |

Rationale: RE-02 requires every R3 intent claim to carry a calibrated Confidence and an Evidence anchor. One suggestive class is a weak single source -> low.
```

The auditor does **NOT** apply the fix. The producer that emitted the fragment applies it on re-invocation. The auditor only proposes.

### Step 5 -- Document accepted exceptions

The operator may explicitly accept a violation where the rule applies but the cost of compliance exceeds the value (e.g. an anchor that genuinely requires a running environment the operator cannot stand up -- kept as `⚠ unverified`). Accepted exceptions are recorded in the report's §Accepted Exceptions with: the rule (`RE-NN`); the fragment + section affected; the rationale for acceptance; the expiration condition (e.g. "until ops access is granted"); and the sign-off (operator identifier). Accepted exceptions are NOT a default -- they are a deliberate decision-of-record so future iterations and drift passes can re-evaluate them.

### Step 6 -- Produce the report

Write the audit output to the project workspace (`<target-root>/docs/reverse-engineer/`) with the structure in §Output contract: `audit-iter-N.md` for by-gate / end-to-end, `audit-drift-<ref>.md` for drift.

---

## Check inventory

Organized by rule. **DETERMINISTIC first, then HEURISTIC.** Both RE-05 checks (tracker + workspace) always run.

### Deterministic checks

| Rule | Fragment(s) | Check |
|---|---|---|
| **RE-01** Evidence anchoring (presence) | R1, R2, R3, R4 | Every claim-bearing row / bullet carries an anchor token -- a `file:line` (or `file:line-range`, matching `([\w./-]+:\d+(-\d+)?)`), a 7-40-hex commit SHA, or a fenced command-output block -- OR an explicit `⚠ unverified` mark. A row with **neither** an anchor nor an `⚠ unverified` mark is a violation. |
| **RE-01** Anchor line-resolvability (past-EOF) | R1, R2, R3, R4 | Run `tools/check-anchors.py <fragment> <repo-root>`: for **every** cited `file:line` / `file:line-range` / `file:N,M,K` (comma-lists expanded), the file must exist and **every** cited line must be within it (`line <= file length`). A line **past EOF** -- `gateway/Dockerfile:42` when the file ends at 33 -- is a mechanical false anchor and a **violation**. This is the deterministic subset of the false-anchor check: the script settles line-existence with no judgment, so the heuristic walk (below) spends judgment only on whether an *existing* line *supports* its claim. (Unresolved paths are reported as warnings, not violations -- they may be prose tokens like `node:20`.) |
| **RE-01** Anchor content (snippet-on-line) | R1, R2, R3, R4 | The **same** `tools/check-anchors.py` run also settles content for every anchor that carries a `~ token` snippet (`` `dapr.yaml:17 ~ DATABASE_URL` ``): the token must appear on the cited line (or, for a range, on some line within it), whitespace-normalized. A snippet that is **not** on its line -- the off-by-one whose line still exists (`dapr.yaml:18` cited for a credential that lives on line 17; `gateway/package.json:5` cited for `"type":"module"` that lives on line 4) -- is a mechanical false anchor and a **`CONTENT` violation**, with the script finger-pointing the true line when it is within ±5. This is the part of the false-anchor check the producer makes deterministic by pinning the proof; it removes the highest-frequency false anchor from the fallible heuristic walk. (Anchors with no snippet get line-existence only -- the heuristic walk still covers their semantic support.) |
| **RE-01** Documentation as evidence (audit-plane) | R1, R2 | Three sub-checks on the §6 doctrine: **(a)** the fragment states a **documentation-sweep command + count** (completeness is auditable); its absence is a violation. **(b)** No *audit-plane* claim (an R1 inventory item / R2 observed flow) rests **only** on a documentation anchor (a path under `docs/`, a `*.md` / `*.puml` / `*.http`, a README) without a code anchor, unless it is explicitly marked `⚑ declared (not observed)`. A doc-only observed claim is a violation -- documentation is a lead, not proof. **(c)** `⚑ declared (not observed)` items are **segregated** (R2: in `## Declared use cases (not observed)`; R1: in §Gaps), never mixed into observed facts -- a `⚑` row among observed items, or an observed item that is really doc-only, is a violation. Mirrors the RE-04 observed/anticipated separation check, applied to documentation. |
| **RE-01** Census coverage (nothing lost) | R1 | Run `tools/repo-census.py coverage <system-cartography.md> <repo-root>`: it re-enumerates + types every file in the target and checks each is **accounted for** -- referenced in the fragment, or listed in its `## Census coverage` exclusions block (a path token / ancestor-directory match). A file present in the repo but **`UNCOVERED`** (exit 1) is a completeness violation: R1 silently omitted it. The census is deterministic (same repo state → same file set), so this is mechanical, not judgment -- the "no information in the repo is discarded" mandate made a hard check. (`unclassified` files are additionally surfaced for explicit disposition.) |
| **RE-01** Count verification | R1, R2, R3, R4 | Run `tools/check-counts.py <fragment> <repo-root>`: it re-runs every fenced ```` ```verify ```` block's command (read-only whitelist, no shell — `grep`/`find`/`wc`/`git ls-files`/`git log`/… piped) and compares output to the pasted count. A **`MISMATCH`** (exit 1) is a mechanical false claim — the prose number drifted from what the command returns. This closes the count blind spot the snippet check cannot reach (a `file:line ~ token` pins a line's content, not a grep tally); it is the class that wrote "11 actor types" for 10 and "22" for 21. A non-whitelisted command is warned (unverifiable), never run. |
| **RE-02** Inferred intent labelled | R3 | Every intent claim row (objective / users / pain points / goals) has a `Confidence` cell holding one of `high` / `medium` / `low`, AND a non-empty `Evidence` anchor (per RE-01). A bare intent statement with no confidence or no evidence is a violation. |
| **RE-02** Confidence-summary tally consistency | R3 | The §Confidence summary one-liner (`N high, M medium, K low`) MUST equal the actual count of `high`/`medium`/`low` Confidence cells across §Inferred objective + the §Inferred users / pain points / goals tables. Count the rows; compare to the stated tally. A mismatch is a **violation** (the tally is load-bearing carry-forward to the SAD's S1a -- a wrong count misrepresents how solid the framing is). Fix: correct the tally to the true counts. |
| **RE-04** Observed stressors only | R4 | The fragment has a `## Observed stressors` section AND a separate `## Anticipated (not observed)` section (the latter may be empty). Every row under Observed carries an evidence anchor (incident link / churn count + command / coupling metric / `file:line` of a HACK/TODO / commit SHA). An Observed row with no anchor, or an anticipated stressor sitting in the Observed section, is a violation. |
| **RE-05** Tracker coherence (ALWAYS RUNS) | Router, all gates | Walk the `FLOW.md` gate tracker R1 -> R2 -> R3 -> R4 and verify the three invariants: **(1)** the chain of `[x] approved` is contiguous from R1; **(2)** every active gate (`[~]` / `[?]` / `[i]`) has all prior gates `[x]`; **(3)** at most ONE gate is active at any time. Report **PASS**, or list every offending row as a violation. Fix is binary: revert the offending gate to `[ ]`, or approve every missing prior. No `--force`. |
| **RE-05** Workspace placement (ALWAYS RUNS) | Router, all gates | Run `tools/check-workspace.py <target-root>`: it walks `docs/` and flags every recon-owned artifact (`FLOW.md`, the four R1-R4 fragments, `r1-inventory.json`, `audit-iter-N.md` / `audit-drift-<ref>.md`, `phase0-evidence.md` -- matched by canonical basename) that is **not** under `docs/reverse-engineer/`. A recon artifact under `docs/architecture/` -- or sitting loose elsewhere in `docs/` -- is a **`MISPLACED`** violation (exit 1): it collides by name with the SAD deliverable that owns `docs/architecture/`. The SAD's own files there are not recon-owned and are ignored. The folder rule is binary (recon-owned -> `docs/reverse-engineer/`), so this is mechanical, not judgment. Fix: move the artifact into `docs/reverse-engineer/`. |

### Heuristic checks

| Rule | Fragment(s) | Check |
|---|---|---|
| **RE-01** false-anchor spot-check | R1, R2, R3, R4 | Open the cited `file:line` (or `git show <sha>`) and confirm it actually supports the claim it is attached to. A pointer that lands on an unrelated line -- or a commit that does not contain the cited change -- is a **false anchor** and is **worse than no anchor**, because it manufactures false confidence. The deterministic checks above (`check-anchors.py`) have already settled that every cited line *exists* AND -- for every anchor carrying a `~ token` snippet -- that its proof-token is on the cited line; here you judge whether an *existing, snippet-less* line *supports* its claim -- the part that still needs judgment. **Spot-check prose anchors; but in any cell that pairs several facts with several lines (the R1 inventory tables especially), open and verify EVERY line in the cell -- not a sample -- because a line that exists but supports the wrong fact (a `test` script cited at `:11` when `:11` is the closing `}`) passes the line-existence check, and unless it is pinned with a snippet only a content read catches it. And when one anchor into a sibling-file family (`web/` vs `gateway/` package.json or Dockerfile) is wrong, RE-VERIFY the whole family rather than clearing the siblings by analogy -- the same construct sits on different lines in differently-laid-out files.** Where an anchor IS snippet-pinned, the deterministic content check has already done this read -- do not re-clear it by analogy, but do not waste judgment re-reading it either. Report each as an Anchor Finding. |
| **RE-02** calibration | R3 | A `high` confidence backed by a single weak anchor (one suggestive directory name, one inference chain with gaps) is mis-calibrated -- confidence is set by the weakest link in the inference, not by how plausible the prose sounds. Report as a `concern`. |
| **RE-03** descriptive-not-prescriptive | R1, R2, R4 | Scan for prescription: modal verbs (`should`, `ought to`, `we recommend`, `the ideal`, `a better design`); refactor proposals; target-state diagrams; proposed component names that do **not** exist in the code; any sentence describing a system other than the one on disk. Recon is a mirror, never a redesign -- the redesign is the SAD's job. Report each as a violation-grade prescriptive finding (RE-03 is heuristic, so it is graded with confidence). |
| **RE-04** stress-genuineness | R4 | Does the cited anchor genuinely indicate architectural stress? A high-churn file that is a config registry legitimately growing is not necessarily under stress; a co-change pair that is two halves of one feature is not necessarily coupling pain. Report weak stress inferences as a `concern`. |
| **RE-01** ⚠-unverified-ratio signal | any fragment | Compute the share of claim rows marked `⚠ unverified`. A fragment dominated by `⚠ unverified` did not actually ground in the code -- it is a set of hypotheses, not findings. Report the ratio as a `concern` and recommend reading more before the gate is parked. |
| **RE-01** declared-not-observed genuineness + sweep completeness | R1, R2 | Two judgments the count cannot settle: **(1)** is each `⚑ declared (not observed)` item *genuinely* unbuilt -- the code really lacks it -- or was it built somewhere the producer's sweep did not look (a mis-classified milestone is a false negative; report as `concern`)? **(2)** did the documentation sweep actually account for **every** artifact its own `find`/count surfaced -- `find` the docs independently and check none was read past in silence (an artifact present but unmined is a coverage gap; recon's mandate is that *no information in the repo is lost*). Report gaps as a `concern`. |

### Consolidated count

| Category | Count | Mechanism |
|---|---|---|
| RE-01 anchor-presence (per claim row) | 1 | deterministic |
| RE-01 anchor line-resolvability / past-EOF (script `tools/check-anchors.py`) | 1 | deterministic |
| RE-01 anchor content / snippet-on-line (script `tools/check-anchors.py`) | 1 | deterministic |
| RE-01 documentation as evidence (sweep present + audit-plane doc-only + declared segregation) | 1 | deterministic |
| RE-01 census coverage / nothing-lost (script `tools/repo-census.py coverage`) | 1 | deterministic |
| RE-01 count verification (script `tools/check-counts.py`) | 1 | deterministic |
| RE-02 confidence + evidence presence | 1 | deterministic |
| RE-02 confidence-summary tally consistency | 1 | deterministic |
| RE-04 observed/anticipated separation + observed-anchor presence | 1 | deterministic |
| RE-05 tracker coherence (three invariants; ALWAYS) | 1 | deterministic |
| RE-05 workspace placement (script `tools/check-workspace.py`; ALWAYS) | 1 | deterministic |
| RE-01 false-anchor spot-check | 1 | heuristic |
| RE-02 calibration | 1 | heuristic |
| RE-03 descriptive-not-prescriptive | 1 | heuristic |
| RE-04 stress-genuineness | 1 | heuristic |
| RE-01 ⚠-unverified-ratio signal | 1 | heuristic |
| RE-01 declared-not-observed genuineness + sweep completeness | 1 | heuristic |
| **Total** | **17 checks** | mixed |

In `by-gate` mode, the checks that apply to that one fragment's rule(s) run, plus the two RE-05 checks (tracker + workspace) -- typically 3-11 checks (R1 carries the most: anchoring, snippet content, documentation, census coverage, and count verification). In `end-to-end` mode, all 17 run across the four fragments. In `diff` mode, the §Drift mode specifics checks run plus RE-05 (tracker + workspace) whenever a `FLOW.md` / target repo is in scope.

---

## Drift mode specifics

In `diff` (drift) mode the auditor re-runs the recon observations over the **current** target code and diffs them against the **prior** SAD/recon (`<ref>`). It is the cross-time complement to the static checks: where the static checks ask "is this fragment honest about the code as it is now?", drift asks "does the documented architecture still match the running one?". Concretely, it reports:

- **Entry points** that are **new**, **moved**, or **gone** vs the prior R1 / SAD.
- **Data stores** that appeared, moved, or were removed.
- **Flows** (R2 use cases) that changed, were added, or no longer exist.
- **Stressors** that materialized (an anticipated stressor that now has observed evidence; a new HACK/incident/churn hotspot) or were resolved.
- Each finding anchored to the **current** code (`file:line` / commit / command output, per RE-01) and dated.

Output: `audit-drift-<ref>.md`. Findings are **advisory** -- the auditor reports where the SAD is now lying; the **operator** decides whether the drift warrants reopening a recon gate (`Rn` -> `[ ]`, cascade downstream) or a SAD gate. This converts "the docs are out of date" from a vague worry into an anchored, dated report of exactly what changed and where. This is the capability that makes recon valuable past day one.

---

## Output contract

One file in the project workspace (`<target-root>/docs/reverse-engineer/`). **Report-name convention:** `audit-iter-N.md` for `by-gate` / `end-to-end` (one per recon iteration); **`audit-drift-<ref>.md`** for `diff` mode (one per drift pass, `<ref>` naming the prior artifact diffed against).

Frontmatter:

```
---
title: Recon audit -- <target name>
audit-date: <YYYY-MM-DD>
mode: by-gate | end-to-end | diff
scope: <fragment name(s) | "R1..R4" | "drift vs <ref>">
status: open | closed
violations: <count>
heuristic-concerns: <count>
accepted-exceptions: <count>
---
```

Body structure:

1. **§Executive summary** -- one paragraph: mode, scope, count of violations, count of heuristic concerns, count of accepted exceptions, overall status.
2. **§Deterministic Violations** -- table: `#` / `Rule` (RE-NN) / `Severity` (always `violation`) / `Fragment` / `Section` / `Description` / `Fix Proposal`.
3. **§Heuristic Concerns** -- table: `#` / `Rule` (RE-NN) / `Severity` (`concern` / `fail`) / `Confidence` (`low` / `medium` / `high`) / `Fragment` / `Section` / `Description` / `Suggested Resolution`.
4. **§Anchor Findings** -- false anchors (a `file:line` that does not support its claim) and missing anchors, listed with the cited location and what was actually found there.
5. **§Drift Findings** -- *drift mode only*: new / moved / gone entry points, data stores, flows, stressors, each anchored to current code and dated.
6. **§Accepted Exceptions** -- table: `#` / `Rule` / `Fragment` / `Section` / `Rationale` / `Expiration` / `Sign-off`.
7. **§Closure** -- one paragraph: what must happen for the audit to close.

**Closure rules.** The audit is `status: closed` only when:

- All deterministic violations are resolved OR explicitly accepted-with-rationale in §Accepted Exceptions.
- All heuristic concerns have been reviewed (acknowledged by the operator, not necessarily resolved).
- All false-anchor findings are resolved (a false anchor is never an acceptable exception -- it is a corrected fact, not a tolerated cost).

The auditor does not close an audit on its own and never on a `--force`. Closure is the operator's decision, recorded.

---

## Refusal conditions

| # | Trigger | Returned message |
|---|---|---|
| 1 | Mode or scope missing, or the named fragment does not exist on disk (by-gate / end-to-end), or no prior SAD/recon exists to diff (drift). | Identify the missing input. The auditor cannot infer mode or scope: "specify mode: by-gate \| end-to-end \| diff". |
| 2 | The operator asks the auditor to fix an issue silently. | Refuse. The auditor proposes fixes as unified diffs; it does not apply them. Re-run the producer that emitted the fragment to apply the fix. |
| 3 | The operator asks to close the audit with deterministic violations unresolved AND no accepted exception. | Refuse. Closure requires resolution or explicit acceptance-with-rationale. There is no `--force`. |
| 4 | The operator asks to skip a check ("don't check RE-03 this pass"). | Refuse. The check set is determined by mode and scope, not by preference. If the rule applies but the operator accepts the violation, document an accepted exception. |
| 5 | The operator asks for a "compliance score" / "audit grade" / "% RE-conformance". | Refuse with explanation. A score invites gaming the audit. Recon's signal is the set of anchored fragments -- claims a human can check in one click -- not an auditor grade. The auditor reports violations and concerns; it does not rank. |
| 6 | The operator asks the auditor to judge the target system's engineering quality ("is this good architecture / should they refactor?"). | Refuse -- out of scope. Recon **describes** what is (RE-03); the SAD **judges** what should be, downstream. The auditor checks that the description is honest, not that the system is good. |

---

## Why these rules

- **Conservative discipline.** The no-silent-fix and no-`--force` rules keep the audit from becoming a rubber stamp. A violation must be resolved or accepted-with-rationale, never bypassed. The auditor proposes; the producer applies; the operator decides.
- **Deterministic first.** Cheap mechanical checks run before any LLM judgment. A fragment with an unanchored claim (RE-01) has a more basic problem than a mis-calibrated confidence; there is no point spending heuristic effort until the mechanical baseline is clean.
- **Advisory, not authoritative.** The auditor reports facts about rule compliance. It does not approve fragments and does not grade the system. Approval is a separate human gate (root `SKILL.md` gate machine); a clean audit is evidence for that decision, not the decision itself.
- **The false-anchor check is the deepest defense.** A missing anchor is a visible gap. A *false* anchor -- a `file:line` that points at something unrelated -- is worse: it manufactures confidence a reader trusts without re-checking. Catching false anchors is the single most valuable thing the auditor does, because it defends the one property that separates a recon fragment from a confabulation: that every claim is checkable on disk. The check splits along the deterministic/heuristic seam, and the seam moved with 0.1.4: line-existence (does `:42` exist when the file ends at 33?) is mechanical, and so is *content* whenever the producer pins the proof with a `~ token` snippet (is `DATABASE_URL` actually on the cited line, or did `:18` drift one line off `:17`?) -- `tools/check-anchors.py` now settles **both** for every anchor exhaustively in the deterministic pass. What remains heuristic is whether an *unsnippeted* line *supports* its claim, so the heuristic walk spends effort only there -- and on a dense inventory fragment (R1) it walks every line of a multi-fact cell, not a sample, because the highest-yield false anchor is a line that exists but proves the wrong fact. The 0.1.4 snippet check exists precisely to pull that highest-yield case across the seam into mechanical territory, so it can no longer survive an audit by being cleared by analogy.
- **Drift is what makes recon valuable past day one.** The first onboarding pass is useful once; drift detection is useful forever. Re-running recon over evolved code and diffing it against the prior SAD/recon turns "the docs are stale" into an anchored, dated list of exactly what moved -- the mechanism that keeps the documented architecture honest over time.

---

## References

- `shared/constitution.md` -- the 5 active rules (RE-01 to RE-05) + cross-reference table. The auditor enforces every rule listed there and **only** those; it does not import the SAD's R-01..R-27.
- `shared/evidence-anchoring.md` -- anchor forms, confidence calibration, the `⚠ unverified` quarantine, and **§6 documentation as evidence** (the completeness sweep, doc-vs-code anchor ranking, and `⚑ declared (not observed)`). This is how the auditor tells a real anchor from a false one (the RE-01 heuristic spot-check), judges RE-02 calibration, and runs the new RE-01 documentation checks.
- `shared/glossary.md` -- vocabulary the auditor uses in findings (residual candidate, observed / anticipated stressor, anchor, confidence, gate, fragment, drift).
- `tools/check-anchors.py` -- the deterministic anchor validator the two RE-01 mechanical checks run (`check-anchors.py <fragment> <repo-root>`); flags every cited line past its file's end AND, for any anchor carrying a `~ token` snippet, every line whose content does not contain the token. Read-only, no dependencies.
- `tools/repo-census.py` -- the deterministic file census the RE-01 census-coverage check runs (`repo-census.py coverage <fragment> <repo-root>`); re-enumerates + types every file in the target and flags any not accounted for in R1. Read-only, no dependencies.
- `tools/check-counts.py` -- the deterministic count verifier the RE-01 count-verification check runs (`check-counts.py <fragment> <repo-root>`); re-runs every ```` ```verify ```` block's whitelisted read-only command (no shell) and flags any count that does not match. Read-only, no dependencies.
- `tools/check-workspace.py` -- the deterministic workspace-placement validator the RE-05 workspace check runs (`check-workspace.py <target-root>`); walks `docs/` and flags any recon-owned artifact not under `docs/reverse-engineer/` (a recon file leaked into the SAD's `docs/architecture/`). Read-only, no dependencies.
- `FLOW.md` -- the gate tracker the RE-05 coherence check walks (the three invariants live in its §Gate tracker note).
- The root `SKILL.md` -- the router, gate machine, doctrine table, recommended auditor cadence, and the drift loop the auditor's diff mode implements.
- `recon/system-cartography/SKILL.md` (R1), `recon/behavior-reconstruction/SKILL.md` (R2), `recon/business-reconstruction/SKILL.md` (R3), `recon/asbuilt-stressors/SKILL.md` (R4) -- each producer's `## Refusal conditions`, which the auditor mirrors when it checks the fragment that producer emitted.
