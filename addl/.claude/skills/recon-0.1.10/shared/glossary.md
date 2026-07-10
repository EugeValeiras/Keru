---
title: Glossary -- Brownfield Recon meta-skill
version: 1.2
date: 2026-06-18
---

# Glossary

Vocabulary for the `recon` meta-skill. Terms are listed in dependency order (earlier terms are used in later definitions) rather than alphabetically.

### Brownfield

A project that **already exists and already runs**, as opposed to greenfield (designed from scratch). Recon's entire reason for being: the SAD chain starts from a PRD/SRD, but the most common real case is a brownfield system with little or no documentation. Recon is the brownfield front door.

### Recon fragment (or just "fragment")

One markdown deliverable produced by one gate (R1-R4), parked at its gate for human review, written into the target repo's `docs/reverse-engineer/`. A fragment is **a set of evidence-anchored observations, not a narrative** -- every claim points at a place in the code or its history. One gate = one fragment = one approval.

### Gate

A checkpoint in the sequential recon chain (R1, R2, R3, R4). A gate has a state (`[ ] [~] [?] [x] [!] [i]`) tracked in `FLOW.md`. A sub-skill may not produce its fragment until its prior gate is `[x] approved`. Gates make "we are still on R2" a checked precondition rather than something the operator must catch.

### Anchor (evidence anchor)

A concrete, re-checkable pointer attached to a claim: a `file:line` (or range), a commit SHA, or a command + its captured output. The unit of RE-01. An anchor lets a human falsify a claim in one click -- open the file, go to the line, see whether the claim holds. A `file:line` that does not actually support the claim is a **false anchor** -- worse than none. See `shared/evidence-anchoring.md`.

### `⚠ unverified` (quarantine)

The mark on a claim that is useful but could not be anchored (dynamic evidence with no running system, an ambiguous inference). It preserves the lead for the SAD to chase while making it impossible to mistake a hypothesis for a finding. A fragment dominated by `⚠ unverified` rows did not actually ground in the code.

### Documentation anchor vs code anchor

Two ranks of evidence (RE-01). A **code anchor** (`file:line` in source/tests, a commit) records what the system *does* -- it is proof. A **documentation anchor** (a README / `docs/**` / `*.puml` / `*.http` / an intent-bearing comment) records what the authors *say* -- it is a claim/lead, ranked below code because documentation goes stale. For the *audit* plane (R1/R2) a claim resting only on a documentation anchor is not an observed fact; it is `⚑ declared (not observed)` until a code anchor confirms it. See `shared/evidence-anchoring.md` §6.

### `⚑ declared (not observed)`

The mark on a capability/use-case the **documentation declares but the code demonstrably does not implement** -- an intended-but-unbuilt **milestone**. Unlike `⚠ unverified` (couldn't anchor at all), this is a *positively anchored* finding: anchored to the doc that declares it **and** to the confirmed absence in code. It is captured in a segregated section (never mixed with observed facts), so a downstream reader keeps the option to act on it -- or cleanly discard it -- rather than losing it by default. The documentation analogue of the RE-04 `anticipated (not observed)` split.

### Completeness sweep

The duty (RE-01) to enumerate **every** information-bearing artifact in the target repo -- code, tests, and all documentation (`*.md`, `*.puml`, `*.http`, READMEs, `CLAUDE.md`/`AGENTS.md`, ADRs, comments) -- with a command + count so coverage is auditable, and to account for each one. *No information in the repo is discarded.* The same "state the command + count" discipline R1 uses for entry points, applied to the whole information surface. In R1 the enumeration is mechanical, so it is a script -- the **repo census**.

### Repo census / typed inventory

The deterministic, exhaustive file census R1 runs at Step 0 via `tools/repo-census.py`: it enumerates every file (`git ls-files` + untracked-not-ignored, deps/caches excluded by a fixed list) and tags each by type (`source:<lang>`, `test`, `config`, `docs`, `build-ci`, `iac-deploy`, `schema-migration`, `asset-binary`, `generated-lock`, `unclassified`). The output `r1-inventory.json` is the **trackable typed worklist** the producer walks file-by-file and the **coverage ledger** the auditor checks. The census *enumerates and types* (mechanical, script); the producer *interprets* (judgment, LLM) -- never the reverse, since a script inferring architecture from contents would be the confabulation recon prevents. Its `coverage` mode hard-fails on any censused file R1 left unaccounted-for -- the "nothing is lost" guarantee made mechanical. `unclassified` is the safety net: anything the typer did not recognise is surfaced for review, never dropped.

### `verify` block (count claim)

A fenced ```` ```verify ```` block carrying an enumeration/count claim as a re-runnable command + its verbatim output (command on line 1, output below). `tools/check-counts.py` re-runs the command (read-only whitelist, no shell) and hard-fails if the count does not match -- so the number is mechanically true, not trusted prose. Mandatory for every "N of X" / "→ N hits" / registration-count claim (RE-01). Closes the count blind spot that the `~ token` snippet (which pins a *line's* content, not a *tally*) cannot reach -- the class that twice wrote a wrong actor count in R1.

### Confidence (high / medium / low)

The calibrated weight attached to an **inferred intent** claim in R3 (RE-02). `high` = multiple independent anchors converge, nothing contradicts; `medium` = suggestive but thin or ambiguous; `low` = a plausible hypothesis not to bet on. Set by the weakest link in the inference, not by how plausible the conclusion feels. The SAD treats a `high` business framing very differently from a pile of `low` guesses.

### Inferred intent

A statement about *why* the system exists or *who* it serves -- objective, users, pain points, goals. Almost never written in the code, so R3 reconstructs it by deduction from structure, naming, git history, and tests. Always labelled as inferred, with confidence + evidence (RE-02). Distinct from the observable *what* (R1/R2/R4), which is described as fact when anchored.

### Descriptive, not prescriptive

The stance of R1/R2/R4 (RE-03): describe the system **as it is**, including bad structure, with anchors -- never say what it *should* be, rename components to "better" names, or propose refactors. Redesign is the SAD's job; doing it in recon contaminates the SAD's naïve baseline and pre-empts its stressor analysis.

### Observed stressor

A point of architectural stress the **system itself testifies to**: a production incident, a churn/hotspot measurement, a co-change (contagion) pair, a `// HACK: race under load` comment, a revert, a bug-fix cluster -- each carrying an anchor (RE-04). These are the stressors the SAD's S3 **cannot generate on its own**, because they require having watched this specific system live. Recon's unique contribution.

### Anticipated stressor (not observed)

A stressor the architect suspects but cannot anchor to evidence in this system. Permitted in R4, but only in a separate `## Anticipated (not observed)` section, never mixed with observed ones. The SAD's S3 generates these by method; recon's job is to flag the ones it sensed and keep them visibly distinct.

### Coupling / contagion (observed)

When two modules change together across history (co-change), or one module's change forces another's. R4 measures this from `git log` and reports it descriptively ("changing X forced changing Y across commits A, B, C") -- it does **not** prescribe decoupling them (RE-03). Mirrors the SAD's contagion concept but read from the as-built rather than derived from stressors.

### As-built / residual candidate

The existing implementation, typed in IDesign terms (Manager / Engine / ResourceAccess / Resource / Utility / Client) by R4 to describe what is there. When handed to the SAD it is a **residual candidate** that S6 (the empirical Ri test) measures against the naïve baseline -- it is **evidence, never the baseline**. Treating it as the baseline would destroy the SAD's empirical test, because the residual would be measured against an already-strong starting point.

### The three planes (Phase-0 evidence)

The document shape the SAD's "When a prior implementation exists" mode accepts, and recon's output: **business framing** (R3 -> SAD S1a), **as-built audit** (R1+R2+R4 typing -> a residual candidate S6 measures), and **observed stressors** (R4 -> held for SAD S3). The optional `handoff-assembler` packages all three, labelled, into `phase0-evidence.md`.

### Entry mode (β / γ)

How the operator brings recon's Phase-0 evidence into a SAD project. **β** = a fresh SAD, the existing implementation as S6 evidence (not the baseline). **γ** = a SAD for the next phase, the existing implementation as a residual candidate S6 measures. (Mode **α** -- audit the existing Phase-0 -- routes to the SAD's auditor, not recon.) In all modes the naïve baseline stays the SAD's independently-built control.

### Drift

The growing gap between a documented architecture (a SAD or a prior recon) and the running code as it evolves. `recon-auditor` in **diff mode** re-runs recon and diffs against the prior, producing an anchored, dated `audit-drift-<ref>.md` of exactly what changed and where the SAD is now stale. The capability that keeps the architecture honest over time.

### Router / orchestrator

The component (the main LLM, or a UI parent) that reads the gate tracker, reports position, routes the request to the right sub-skill, delegates with the handoff contract, and closes gates. Runtime-agnostic: the same contract whether a single LLM navigates the docs or a multi-agent runtime spawns `Reverse-Engineer` / `Reverse-Engineer-Auditor` subagents.

## References

- `shared/constitution.md` -- RE-01..RE-05, the rules these terms operationalize.
- `shared/evidence-anchoring.md` -- anchors, confidence, the quarantine, observed-vs-anticipated, in practice.
- Root `SKILL.md` -- gates, router, the three planes, the drift loop.
- `sad-*/shared/glossary.md` -- the downstream SAD's vocabulary (naïve baseline, residual, Ri test, stressor types) that recon's output feeds into.
