---
name: system-cartography
description: Entry sub-skill of the `recon` meta-skill. Produces the `system-cartography.md` fragment -- the inventory of entry points, modules/services, data stores, external integrations, build/deploy topology, and runtimes, reconstructed from a running, undocumented repo with every claim anchored to `file:line` or a command. Invoke as gate R1, the brownfield entry; refuse when there is no existing implementation to read.
task_types: [system-cartography, inventory, reverse-engineer, onboard-brownfield]
shared_refs:
  - ../../shared/constitution.md
  - ../../shared/evidence-anchoring.md
  - ../../shared/glossary.md
  - ../../templates/system-cartography.md
---

# system-cartography (R1)

Entry sub-skill of the meta-skill, and the first of the four sequential gates. It produces exactly one fragment -- `system-cartography.md` -- the structural inventory of what **exists** in the target repo: its runtimes and stack, every way the outside world gets in, the modules/services/components on disk, the data stores, the external integrations, and the build/deploy topology. It reconstructs all of this primarily by *reading the running code* -- the source of truth. The repo may also carry documentation (a README, `docs/**`, diagrams); R1 sweeps **all** of it (nothing in the repo is discarded -- RE-01 §6) and uses it as a **lead** to corroborate the module map, but documentation is ranked below code: a structural claim resting only on a doc is `⚑ declared (not observed)`, not an observed fact, until a code anchor confirms it. This fragment is the foundation R2 (behavior), R3 (business intent), and R4 (as-built + stressors) all build on; if the map of what is there is wrong or unanchored, everything downstream inherits the error.

The golden rule governs every line of output. **Every inventory claim is anchored to evidence on disk** -- a `file:line`, a commit SHA, or a command and its verbatim output (RE-01); a claim you cannot anchor is dropped or kept and marked `⚠ unverified`. R1 is the densest-anchor fragment in the chain, so it carries the strictest form of the rule: in the multi-fact inventory cells and across sibling-file families (`web/` vs `gateway/` package.json + Dockerfile) **pin each `file:line` with a `~ token` snippet** (`shared/evidence-anchoring.md` §1) -- the literal text that proves the claim -- so `tools/check-anchors.py` can mechanically catch the off-by-one line numbers that are this fragment's characteristic failure. And the inventory is **descriptive only** (RE-03): record what the code is, with the names the code itself uses, and stop. No "should", no proposed refactor, no renaming a component to a "better" or "more correct" name. R1 holds up an honest mirror; reading messy code naturally provokes fixes, but the fix is the SAD's call downstream, derived from stressors -- never recon's to assert. An unanchored or redesigned cartography is worse than no cartography: it manufactures false confidence and poisons the SAD's naïve baseline before the SAD has even started.

---

## When to invoke

- The operator points you at a project that **already exists and already runs** but is under-documented (no PRD/SRD, no `docs/architecture`), and asks "what is this", "onboard / reverse-engineer / document this repo", or "produce the Phase-0 evidence for a SAD from this code".
- A recon run is starting fresh: no `FLOW.md` gate tracker exists yet, or the tracker exists with R1 still `[ ]` pending (or `[i] iterating` after a rejection / reopen).
- You need the system map -- the inventory of entry points, modules, stores, integrations, and topology -- as the substrate R2/R3/R4 read from.

## When NOT to invoke

- **Greenfield, no code.** There is no implementation to read. Recon has nothing to reconstruct; take the PRD/SRD to the SAD's `business-discovery` (S1a) directly.
- **A current cartography / PRD already exists.** If a faithful, current system map or architecture document already describes this repo, do not regenerate it -- take it forward. (Recon's job is to *produce* the inventory from code when no document exists, not to re-derive one that is current.)
- **The operator wants a redesign, refactor plan, or "better" architecture.** RE-03 forbids R1 from doing it, and it is the SAD's job regardless. Describe what is; route forward to the SAD for what should be.
- **R1 is already past.** If the tracker shows R1 `[x] approved`, you are not at the entry. Defer to the router, which will route to the open gate (R2/R3/R4) rather than re-producing R1.

## Pre-conditions

**None.** This is the entry gate -- there is no prior gate to verify, which is what makes R1 the brownfield front door. The single requirement is **read access to the target repo**.

Although R1 has no upstream gate, it still parks at a gate when done: it produces its fragment, marks R1 `[?] awaiting review`, and STOPS for the human checkpoint described in the root `SKILL.md` §Gate approval protocol. The gate machine and the RE-05 tracker-coherence invariants apply to R1 as they do to every gate; R1 is simply the one gate whose "verify the prior gate is `[x]`" step is vacuous.

## Handoff contract

Runtime-agnostic interface (a single LLM reads these inputs; an agent receives them as a message payload):

- **Consumes:** the target repo, **read-only**. Recon reads the whole tree but writes only under `<target-root>/docs/reverse-engineer/`; it never mutates the target's source.
- **Produces:** one fragment -- `system-cartography.md` -- behind gate **R1**. One fragment = one gate; the sub-skill stops at R1 and does not begin R2 in the same turn.
- **Carry-forward context** (the `## Carry-forward to later gates` section of the fragment) -- pointers, not findings, that aim the later gates:
  - which modules look **hot or large** (size, dependency fan-out) -- so R4 knows where to point its churn / contagion analysis;
  - which **entry points carry the densest logic** -- so R2 knows which flows are worth reconstructing first;
  - which **directories or domain types hint at the business domain** (`billing/`, a `Subscription` aggregate) -- so R3 knows where to look for inferred intent.
  Each pointer is anchored where possible; these are leads for the next gate, not conclusions.

---

## Workflow

Every step is **read-only**: `Glob` / `Grep` / `Read`, and `Bash` limited to `git` and local inspection -- **no network**. As you go, anchor every claim per `shared/evidence-anchoring.md`. The discipline to repeat at each step: *a claim you cannot point at on disk is dropped or marked `⚠ unverified` -- it never enters the fragment as fact.*

**Completeness is mechanical, so it is a script, not prose (Step 0).** Enumerating *every* file and typing it is deterministic and judgement-free -- the kind of step the skill's own "mechanical determinism" doctrine says to encode as a tested tool, not eyeball. R1 therefore opens with a `tools/repo-census.py` run that produces the **typed inventory** every later step walks; nothing in the repo escapes it. But the census only *enumerates and types* -- it never interprets. Reading what each file means, and anchoring it, is the judgement work of Steps 1-8. Code is the source of truth: a structural claim resting **only** on documentation is `⚑ declared (not observed)` (RE-01 §6), not an observed inventory item, until a code anchor confirms it.

### Step 0 -- Mechanically census the repo (deterministic, exhaustive)

Before reading anything, run the census so the worklist is complete and reproducible -- *no file is lost because no human chose the file list*:

```bash
python3 tools/repo-census.py census <target-repo-root> --json > docs/reverse-engineer/r1-inventory.json
python3 tools/repo-census.py census <target-repo-root>          # the count table, for the fragment
```

It enumerates `git ls-files` + untracked-not-ignored (dependencies / build caches excluded by a fixed list) and tags each file by type (`source:<lang>`, `test`, `config`, `docs`, `build-ci`, `iac-deploy`, `schema-migration`, `asset-binary`, `generated-lock`, and **`unclassified`**). `r1-inventory.json` is the **trackable typed inventory** -- the worklist for Steps 1-8 and the ledger the auditor's coverage check reads. Two rules:

- **Walk it category by category.** The `docs` category is your RE-01 §6 documentation sweep (mine each as a lead; declared-but-unbuilt → `⚑`). The `source:*` / `iac-deploy` / `schema-migration` categories seed the inventory steps. Record the count table in the fragment so coverage is auditable.
- **`unclassified` MUST be reviewed, one by one.** It is the safety net: anything the typer did not recognise (a stray compiled binary, a runtime log, a bespoke file) is surfaced, never dropped. Account for each -- inventory it, or note it as out-of-scope with a reason.

Every censused file ends Step 8 either **referenced** in the cartography or listed in an explicit `## Census coverage` exclusions block with a reason; the auditor verifies this mechanically (`repo-census.py coverage`). That is the "nothing is lost" guarantee made deterministic.

### Step 1 -- Establish the stack and runtimes

Read the manifests to fix the language(s), version(s), framework(s), build system, and dependency manager: `package.json`, `go.mod`, `*.csproj` / `global.json`, `pom.xml` / `build.gradle`, `pyproject.toml` / `requirements.txt`, `Gemfile`, `Cargo.toml`, etc. Anchor each finding to the manifest line, pinned with a `~ token` snippet (e.g. `` `gateway/package.json:4 ~ "type": "module"` ``) -- manifests are where sibling files (`web/` vs `gateway/`) lay the same key out on different lines, so the snippet is what stops a copied line-number from going stale. This decides which patterns the later steps grep for.

### Step 2 -- Enumerate entry points

Every way the outside world gets in: HTTP routes, gRPC services, CLI verbs, message/queue consumers, scheduled jobs, public library APIs. Grep the stack's route/handler patterns (adapt to what Step 1 found) -- e.g. `MapGet|MapPost|\[Http|\[Route`, `@app.route|@RestController`, `router\.(get|post)`, cron / scheduler registrations. **State the enumerating command and its count as a ```` ```verify ```` block** (RE-01: command + verbatim output), so the list's completeness is *mechanically* re-checkable -- `tools/check-counts.py` re-runs the grep and confirms the number. A bare prose count ("→ 11 hits") is the blind spot that wrote "11 actor types" for 10; every count claim in this fragment (entry points, actor `Type()` tally, registration counts) is a `verify` block, never a trusted prose number. Anchor each entry to its handler `file:line`.

### Step 3 -- Map modules / services / components

Map the internal structural units **as they exist on disk** -- directories, projects, packages, namespaces. Use the code's own names (RE-03): report `OrderManager` because the file is `OrderManager.cs`, not an "improved" name. Record each unit's responsibility *as observed*, anchored. If the system is split into deployable services, note the boundary and how each is deployed.

### Step 4 -- Find the data stores

Every place state lives: databases, queues, caches, file stores, external state-holding systems. Anchor each to **both** the connection/config (the connection-string key, the DSN, the `appsettings`/`.env` reference) **and** the access code (the ORM context, repository, or driver call site). If the connection target is resolved only from config that is not in the repo, mark it `⚠ unverified` and name the missing anchor.

### Step 5 -- External integrations

Third-party / cross-system calls leaving (or entering) this system: APIs, SaaS, webhooks, other internal systems. Anchor each to the call site or client construction. **Mark config-only targets `⚠ unverified`** -- if the integration endpoint is read from config and the value is not resolvable from the repo, you cannot confirm the target without a running environment, so it is a quarantined lead, not a finding. (And beware the unused-stub trap from RE-01: an `IPaymentClient` field with zero call sites is not an integration.)

### Step 6 -- Build & deploy topology

How the system is built, packaged, and deployed, as evidenced in the repo: CI config (`.github/workflows/`, `Jenkinsfile`, `.gitlab-ci.yml`), `Dockerfile`(s), IaC (Terraform, Helm, k8s manifests), deploy scripts. Anchor each to the file. Deploy *targets* that live only in an external system (not in the repo) are `⚠ unverified`.

### Step 7 -- Write the carry-forward notes

Capture the `## Carry-forward to later gates` pointers (see Handoff contract): hot/large modules for R4, dense entry points for R2, domain-hinting directories for R3. These are leads for the next gate, anchored where possible -- not findings, and not intent (intent is R3's job, under RE-02).

### Step 8 -- STOP at gate R1

Write `system-cartography.md` per the template, then **stop**. Present it, expect `recon-auditor` `by-gate` to run against it (per the root §Recommended auditor cadence), and mark R1 `[?] awaiting review`. Do not begin R2 in the same turn -- one fragment, then the human checkpoint. On operator sign-off the router marks R1 `[x] approved`; only then does R2 open.

> Throughout: **anchor every claim.** What cannot be anchored is dropped or marked `⚠ unverified` with the missing anchor named. A fragment dominated by `⚠ unverified` rows is one that did not actually ground in the code -- go read more before parking the gate.

---

## Output contract

One fragment file: `<target-root>/docs/reverse-engineer/system-cartography.md`, filled per `templates/system-cartography.md`. The template's sections are the contract:

- `# System Cartography -- <target name>` + the "reconstructed from running code" note;
- `## Overview` (what kind of system, in structural terms -- no intent yet);
- `## Runtimes & stack`, `## Entry points` (with the enumerating command + count), `## Modules / services / components`, `## Data stores`, `## External integrations`, `## Build & deploy topology` -- each an anchored table; every `file:line` in a multi-fact cell or sibling-file family pinned with a `~ token` snippet (RE-01 deterministic content check);
- `## Carry-forward to later gates`;
- `## Census coverage` -- the `repo-census.py` count table (per-category file counts) and an **exclusions** list: every censused file not individually inventoried above, with a one-line reason (out-of-scope tooling, generated, runtime artifact). Every file in `r1-inventory.json` is either referenced in the inventory or listed here -- the auditor verifies this with `repo-census.py coverage` (RE-01 §6 completeness). The `unclassified` bucket is dispositioned here, file by file.
- `## Gaps & unverified` -- every claim that could not be anchored, marked `⚠ unverified` with the missing anchor named; and any structural item the docs **declare** but the code lacks, marked `⚑ declared (not observed)` (a candidate the inventory should not lose).
- Plus the side artifact `docs/reverse-engineer/r1-inventory.json` -- the typed census manifest (the trackable worklist + coverage ledger).

**No frontmatter** on the fragment -- it is meant to be inlined directly. This fragment is the SAD's **audit** plane input: together with R2 and R4's IDesign typing it becomes the **residual candidate** the SAD's S6 measures against its naïve baseline -- evidence, never the baseline itself (RE-03).

---

## Refusal conditions

The sub-skill refuses to write the fragment and returns the specific violation when:

| # | Trigger | Rule | Returned message |
|---|---|---|---|
| 1 | The target repo is not accessible, is empty, or contains no implementation to read. | -- | Refuse. There is nothing to reconstruct from. If the project is greenfield, take the PRD/SRD to the SAD's `business-discovery` (S1a) directly; recon has no source. |
| 2 | The operator asks R1 to redesign, propose refactors, or rename components to "better" / "more IDesign-correct" names. | RE-03 | Refuse the redesign. R1 describes what exists, using the code's own names. Name the coupling you observe with anchors; the cure is the SAD's call downstream, derived from stressors. |
| 3 | A claim cannot be anchored to `file:line`, a commit, or a command + output, yet is about to be presented as established fact. | RE-01 | Do not write it as fact. Either drop it, or keep it under `## Gaps & unverified` marked `⚠ unverified` with the missing anchor named. |
| 4 | R1 is invoked to produce while it is **not** the entry -- the tracker shows R1 already `[x] approved`. | RE-05, root §Orchestration | Stop. R1 is past; you are not at the entry gate. Defer to the router, which routes to the open gate (R2/R3/R4) instead of re-producing R1. (To redo R1, the operator reopens it -- the cascade rule applies.) |
| 5 | The tracker is incoherent (e.g. a downstream gate `[x]` while R1 is not `[x]`, or two active gates). | RE-05 | Refuse to route/produce. Report the inconsistency next to position; the operator reverts the offending gate to `[ ]` or approves the missing prior. No `--force`. |

---

## Why these rules

Anchoring (RE-01) matters most precisely *here*, because R1 is the foundation. Every later gate reads this inventory as ground truth: R2 reconstructs flows from the entry points R1 listed, R3 infers intent from the domain directories R1 surfaced, R4 points churn analysis at the modules R1 flagged as hot. An unanchored R1 claim -- "the system uses a message bus", written because there was an `IBus` reference that turned out to be a dead stub -- does not stay contained; it propagates into three downstream fragments and finally into the SAD, each layer treating it as confirmed because R1 stated it plainly. Anchoring makes every cartography claim falsifiable in one click, so the error is caught at the gate rather than inherited.

Descriptive-only (RE-03) matters here for a different reason: renaming is a design act. The SAD measures a residual architecture against a *naïve* baseline it must build independently; the existing implementation enters as a residual candidate for S6 to measure, not as the baseline. If R1 smuggles in "better" names or a target shape, it contaminates that naïve baseline before the SAD starts and pre-empts the stressor analysis that is supposed to *derive* whether any restructuring is justified. So R1 reports `OrderManager` because that is the filename, records the 2,000-line class and its fan-out with anchors, and stops -- a clean mirror, not a redesign. The remaining rules (RE-02 inferred-intent, RE-04 observed-stressors) belong to R3 and R4; R1's contribution to the chain is an inventory that is *only* what is there, every line checkable.

---

## References

- `../../shared/constitution.md` -- **RE-01** (evidence anchoring, R1's golden rule), **RE-03** (descriptive not prescriptive, scope includes R1), **RE-05** (tracker coherence, enforced at every gate).
- `../../shared/evidence-anchoring.md` -- the concrete how-to: anchor forms (`file:line` / commit / command+output), the useful read-only commands, and the `⚠ unverified` quarantine. Read before producing the fragment.
- `../../shared/glossary.md` -- vocabulary (residual candidate, the three planes, gate, fragment, anchor).
- `../../templates/system-cartography.md` -- the fragment this sub-skill fills; its sections are the output contract.
- `../../tools/repo-census.py` -- the deterministic file census + typed inventory (Step 0) and the `coverage` "nothing is lost" check; read-only, no dependencies (`census <root> [--json]` / `coverage <fragment> <root>`).
- `../../tools/check-counts.py` -- re-runs every ```` ```verify ```` block's count command and hard-fails on a mismatch; closes the count blind spot. Read-only, whitelist, no shell.
- Root `../../SKILL.md` -- the router, the four-gate chain, the gate approval protocol and gate state machine, and the auditor cadence that runs `recon-auditor` `by-gate` against this fragment.
