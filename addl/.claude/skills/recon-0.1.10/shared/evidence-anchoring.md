---
title: Evidence anchoring -- how to cite, mark confidence, and quarantine the unverified
version: 1.3
date: 2026-06-18
---

# Evidence anchoring

The operational how-to behind the recon constitution's RE-01 (every claim anchored), RE-02 (inferred intent labelled with confidence), and RE-04 (observed stressors only). Read this before producing any fragment. The rules say *what* must hold; this file says *how* to make it hold in practice.

The single failure mode this whole skill defends against: **a language model reconstructing an architecture confabulates structure that is not there.** It reads a few files and narrates a coherent system -- event buses, gateways, sagas -- that the code does not contain. Anchoring is the antidote. An anchored fragment is not a story about the system; it is a set of pointers into the system, each of which a human can check in one click.

## 1. Anchor forms (RE-01)

Every claim cites at least one of these. Prefer the most specific available.

| Form | Looks like | Use for |
|---|---|---|
| **File + line** | `src/Api/Controllers/OrdersController.cs:42` | Any claim about code structure that lives at a place: an entry point, a class, a dependency, a config value. The default and strongest anchor. |
| **File + line range** | `src/OrderManager.cs:30-48` | A claim about a span: a method body, a constructor's injected dependencies, a block. |
| **Commit SHA** | `a1b2c3d` (7-40 hex) | A claim about history or change: when a feature appeared, a revert, a bug-fix cluster. Pair with `git show <sha>` output when the claim is about *what* changed. |
| **Command + output** | a fenced ```` ```verify ```` block: the command on line 1, its verbatim output below | A dynamic / aggregate observation that no single line carries: a churn count, a dependency tally, a test result, a route list. The ```` ```verify ```` fence lets `tools/check-counts.py` **re-run** the command and confirm the count -- see the rule below. |

**Rules for anchors:**

- **Point at the line that proves the claim, not near it.** An anchor that lands on an unrelated line is a *false anchor* -- worse than none, because it manufactures false confidence. When you cite `file:line`, you have read that line.
- **Pin the proof with a snippet -- `path:line ~ token` -- so the line-number is machine-checkable.** Append a `~` and a short literal token copied from the cited line, inside the same code span: `` `dapr.yaml:17 ~ DATABASE_URL` ``, `` `gateway/package.json:4 ~ "type": "module"` ``, `` `tickstream-consumer.yaml:9-10 ~ 192.168.10.3:30102` ``. The token is the few characters that *prove* the claim; matching is whitespace-insensitive (do not reproduce source indentation) and case-sensitive (copy the literal). For a range, the token must sit on some line within it. The snippet cannot contain a backtick (it runs to the closing backtick / end of line). This is **strongly recommended on every claim-bearing `file:line` and MANDATORY in multi-fact inventory cells and across sibling-file families** -- exactly where off-by-one anchors hide. Why it matters: the line-number alone is only checkable by a human re-reading the file (fallible -- it is how a wrong `:18`-for-`:17` survives an audit); the snippet lets `tools/check-anchors.py` confirm mechanically that the token is on the line, turning every off-by-one into a hard failure instead of a manual catch.
- **Every count / enumeration claim is a re-runnable `verify` block, not a prose number.** Do not paraphrase `git log` into "lots of churn", and do not write "grep → 21 hits" as bare prose -- the *number* drifts from the truth and nothing catches it (a count is the one anchor a snippet cannot pin; it bit R1 twice -- "11 actor types" when there were 10, "22" when the grep returned 21). Instead emit the command and its verbatim output in a fenced ```` ```verify ```` block:

  ````
  ```verify
  grep -rn "func (.*) Type() string" pkg/actors | wc -l
  21
  ```
  ````

  `tools/check-counts.py <fragment> <repo-root>` re-runs every `verify` command (read-only whitelist: `grep`/`rg`/`find`/`wc`/`git ls-files`/`git log`/`sort`/`uniq`/`head`/`tail`/`cut`/`tr`/`comm`, pipes only -- no shell, no writes, no network) and **hard-fails on any output that does not match the pasted one**. So the number is mechanically true, not trusted. This is MANDATORY for any "N of X" / "→ N hits" / registration-count / enumeration claim. Matching is per-line whitespace-trimmed (paste the clean number; the tool absorbs `wc`'s left-pad). A non-whitelisted command is warned, never run -- rephrase it into the whitelist or drop the numeric claim. **Write the command to be environment-stable**, or the count is not reproducible: a recursive `grep -r` over a repo with binaries / build caches emits `Binary file ... matches` lines (to stdout when piped, on BSD grep) and recurses into caches the census excludes -- so use **`grep -rIn`** (`-I` skips binary files) and/or **`--include=*.ext`** to scope to source. The number must be identical whether you, a teammate, or `check-counts.py` runs it (this exact trap inflated a real `→ 6` to `14` in the 0.1.7 dogfood).
- **One claim can carry several anchors.** "B2B billing platform (high confidence)" earns its confidence by *converging* anchors -- list them all.
- **One *anchor* proves one *fact* -- pair each fact with its own line, never pack several behind a bare comma-list.** The converse of the rule above: a claim may carry several anchors, but in a multi-fact cell each fact must be pinned to its *own* line *inline*, so the mapping is 1:1 and auditable -- `node:20-alpine (:2), npm ci (:14), CMD (:33), EXPOSE 6002/6003 (:25)`, **not** a bare `:2,14,33,25`. A bare comma-list is a false-anchor trap: each number drifts independently and a wrong or past-EOF one (`:42` when the file ends at 33) hides in the list. The fixed-row inventory tables (`§Runtimes & stack`, `§Build & deploy`) aggregate by design, so the inline pairing is what carries this -- the cell still lists several facts, but each names its line. (`tools/check-anchors.py <fragment> <repo-root>` mechanically flags every cited line past its file's end, and -- for any anchor carrying a `~ token` snippet -- every line whose content does not contain the token.)
- **Never reuse a sibling file's line numbers -- re-walk each file.** Two files that play the same role (`web/package.json` vs `gateway/package.json`, `web/Dockerfile` vs `gateway/Dockerfile`) almost never share a layout. A line that is correct in one is wrong in the other -- the `test` script may sit at `:11` in one and `:10` in its sibling. When you cite the same construct across sibling files, open *each* file and read *its* line; copying a sibling's number is exactly how a "fixed" anchor stays broken.
- **Relative paths from the repo root.** So a reader can `cd` to the root and open the path directly.
- **A documentation anchor is a claim, not a proof -- rank it below code (§6).** Citing a README / `docs/**` / `*.puml` / `*.http` / a comment records what the authors *say*, not what the system *does*. For an *audit*-plane claim (R1/R2), a doc-only anchor is `⚑ declared (not observed)` until a code anchor confirms it. Mine every doc (nothing is discarded), but prove against code.

### Useful commands for anchoring (read-only, no network)

These are the recurring evidence sources. Run them; cite them.

```bash
# Entry points (HTTP routes, CLI verbs, handlers) -- adapt the pattern per stack
grep -rn "MapGet\|MapPost\|\[Route\|\[HttpGet\|@app.route\|@RestController\|router\." src/

# Dependency fan-out of a suspected hot class
grep -c "using \|import " <file>           # crude import count
# constructor injection count -> read the constructor span

# Churn (which files change most -- the raw hotspot signal for RE-04)
git log --format= --name-only | sort | uniq -c | sort -rn | head -30

# Co-change / contagion (which files change *together* -- coupling evidence for R4)
# (per-commit file sets; pairs that recur are coupled)
git log --format='%H' --name-only

# Bug-fix clustering on a module (RE-04 observed stress)
git log --oneline --grep="fix\|bug\|hotfix" -- <path>

# In-code stress markers (RE-04)
grep -rn "HACK\|FIXME\|TODO\|XXX\|workaround\|race\|deadlock" src/

# Age / authorship of a suspicious line
git blame -L <start>,<end> <file>
```

Adapt the patterns to the stack you find (the cartography R1 establishes what stack it is). The point is not the exact grep -- it is that the number you write down came from a command a reader can re-run.

## 2. Confidence calibration (RE-02)

R3 reconstructs business *intent*, which is almost never written in the code, so every R3 intent claim carries a confidence level. Calibrate it honestly:

| Confidence | Means | Evidence shape |
|---|---|---|
| **high** | Multiple independent anchors converge on this reading and nothing in the code contradicts it. The SAD can reasonably proceed on it. | 3+ anchors of different kinds (domain types + a webhook + git-history weight), mutually reinforcing. |
| **medium** | The evidence is suggestive but thin, single-sourced, or partly ambiguous. Worth recording; a stakeholder should confirm. | 1-2 anchors, or anchors that admit more than one reading. |
| **low** | A plausible hypothesis the architect would not bet on. Recorded so it is not lost, flagged so it is not trusted. | A single weak signal (one suggestive name, one inference chain with gaps). |

**Calibration discipline:** confidence is set by the *weakest link in the inference*, not by how plausible the conclusion feels. "Enterprise SaaS" inferred from one `Tenant` class is `low`, however confident the prose sounds. The auditor (RE-02 heuristic check) flags a `high` backed by a single weak anchor.

State confidence and evidence together, e.g.:

> **Inferred goal:** reduce manual invoice reconciliation. **Confidence: medium.** Evidence: a `ReconciliationJob` cron (`src/Jobs/ReconciliationJob.cs:18`) and a commit message "automate the month-end reconciliation slog" (`9f3a1c2`). No PRD or issue tracker confirms the business pain directly -- hence medium.

## 3. The `⚠ unverified` quarantine (RE-01)

Sometimes a claim is genuinely useful but you could not anchor it -- the evidence is dynamic and you cannot run the system, or the inference is real but the supporting line is ambiguous. Do not delete it silently and do not present it as fact. **Quarantine it:** keep it, prefix it with `⚠ unverified`, and say what anchor is missing.

> ⚠ unverified -- The system appears to call an external fraud-scoring API, but the endpoint is read from config (`appsettings.json` key `FraudApi:Url`) and the value is not in the repo; the integration target is unknown without a running environment or ops access.

The quarantine mark does two jobs: it preserves a lead for the human/SAD to chase, and it makes the gap *visible* so a reader never mistakes a hypothesis for a finding. A fragment dominated by `⚠ unverified` rows is a fragment that did not actually ground in the code -- the auditor reports that ratio, and it is a signal to go read more before parking the gate.

Do **not** confuse `⚠ unverified` with `⚑ declared (not observed)` (§6). `⚠ unverified` = "I could not anchor this at all." `⚑ declared (not observed)` = "the documentation explicitly declares it **and** the code demonstrably lacks it" -- a *positively anchored* milestone finding, not a quarantined guess.

## 4. Observed vs anticipated (RE-04)

R4 stressors split into two epistemic classes that must not mix:

- **Observed** -- the system itself testifies: an incident doc, a churn count, a co-change pair, a `// HACK: race under load` comment, a revert, a bug-fix cluster. Each carries an anchor. These are the stressors the SAD's S3 *cannot generate on its own*, because they require having watched this specific system live -- recon's unique contribution.
- **Anticipated (not observed)** -- a stressor the architect suspects but cannot anchor to evidence in this system. Permitted, but only in a separate `## Anticipated (not observed)` section, explicitly labelled. The SAD's S3 generates these by method; recon's job is to flag the ones it sensed, not to pad the observed list with them.

The test for "observed": *can I point at the place in the repo or its history where this stress already showed itself?* If yes, anchor it and it is observed. If the answer is "no, but it probably happens" -- it is anticipated.

## 5. Worked contrast (the whole skill in one example)

**Unanchored (what the skill exists to prevent):**

> The system is a scalable, event-driven order-processing platform built around a message bus, designed for high-volume e-commerce with a microservices architecture. It likely struggles under peak load and would benefit from better service boundaries.

Every sentence is confabulation or prescription: no anchors, intent stated as fact, a guessed stressor, a redesign. This passes a human's "sounds right" filter and is almost entirely unfalsifiable.

**Anchored (what a recon fragment looks like):**

> Single ASP.NET process (`src/Api/Program.cs:1`), one entry surface: 11 HTTP routes under `OrdersController` / `CustomersController` (`grep -rn "\[Http" src/Api/Controllers` -> 11). Persistence is one SQL Server via EF Core (`src/Data/AppDbContext.cs:14`, connection string key `Default`). No message bus: the only `IBus`-like reference is an unused stub (`src/Infra/Events.cs:8`, zero call sites -- `grep -rn "Events\." src/` -> 0).
>
> **Inferred objective (R3):** B2B order management for wholesale customers. **Confidence: medium.** Evidence: `WholesaleCustomer` aggregate (`src/Domain/Customers/WholesaleCustomer.cs:1`), bulk-order endpoint (`OrdersController.CreateBulk`, `src/Api/Controllers/OrdersController.cs:120`). No PRD in repo -- medium, not high.
>
> **Observed stressor (R4):** concurrent-checkout double-charge. **Evidence:** `// HACK: double-charge under concurrent checkout` (`src/Checkout/PaymentProcessor.cs:204`); 6 fix commits 2025 (`git log --oneline --since=2025-01-01 --grep=charge -- src/Checkout/PaymentProcessor.cs`).

Same system, opposite epistemics: every claim is a pointer, intent is flagged and weighted, stress is anchored to the code's own testimony. That is the deliverable.

## 6. Documentation as evidence: lead, not proof (RE-01)

A brownfield repo usually is not as undocumented as the "no docs" premise assumes -- it carries READMEs, `CLAUDE.md` / `AGENTS.md`, `docs/**`, `*.puml` sequence diagrams, `*.http` request specs, ADRs, migration notes, and intent-bearing comments. **None of it is thrown away: no information in the target repo is discarded -- all of it is valuable, and that is the whole point of sweeping it.** But documentation is a **weaker class of evidence than code**, because docs go stale: a **documentation anchor** records what the authors *say*; a **code anchor** records what the system *does*. Code is the source of truth.

### The completeness sweep (do this, with a count)

Before classifying anything, **enumerate every information-bearing artifact in the repo** and write the command + count, exactly as entry points are enumerated -- so coverage is auditable and nothing escapes:

```bash
# Documentation / intent artifacts (adapt extensions to the repo)
find . -type f \( -name '*.md' -o -name '*.puml' -o -name '*.http' -o -name 'AGENTS*' \) \
  -not -path '*/node_modules/*' -not -path '*/.git/*' | sort
# count, so the sweep's completeness is re-checkable
find . -type f \( -name '*.md' -o -name '*.puml' -o -name '*.http' \) -not -path '*/node_modules/*' | wc -l
```

Every artifact the sweep finds is **accounted for** -- mined as a lead or explicitly noted as carrying nothing new. An artifact on disk but absent from the fragment is a coverage gap the auditor flags.

### The three states of a documentation-sourced claim

When a doc declares the system does / is / intends X, resolve it against the code into exactly one state -- never silently drop it:

| State | Test | Where it goes |
|---|---|---|
| **Confirmed** | the doc declared X **and** a code/test anchor proves X | an **observed** fact (the doc was the lead, the code is the proof) -- cite the code anchor (optionally the doc too) |
| **`⚑ declared (not observed)`** | the doc declares X, the code **demonstrably does not** implement X | a **first-class, segregated** finding -- an intended-but-unbuilt **milestone**. Anchor it to the doc that declares it **and** state the confirmed absence in code. Never mix it into observed facts. |
| **drift** | the doc asserts X, the code **contradicts** X (does Y) | record what the code does (anchored) + note the doc discrepancy |

`⚑ declared (not observed)` is **not** the same as `⚠ unverified`. `⚠ unverified` means "I could not anchor this at all." `⚑ declared (not observed)` is a *positive, anchored* finding: the doc explicitly declares it (doc anchor) and the code explicitly lacks it (confirmed absence). It is the milestone the team wrote down but did not build -- captured so a downstream reader can choose to keep or cut it, never lost by default.

> ⚑ declared (not observed) -- The README declares an automated `feature -> strategy -> risk -> order` pipeline as the system's spine (`README.md:9-15`), but the `feature` service ships as a source-less binary, the strategy/risk handler bodies are absent, and **nothing consumes `orders.cmd.v1`** (`grep -rn "orders.cmd.v1" services pkg` -> only the publisher). Declared intent, not observed capability -- a candidate milestone for a stakeholder to confirm or drop.

**Audit plane vs intent plane.** For R1 / R2 (what the system **is** / **does**) a claim anchored *only* to a doc is **not** an observed fact -- it is `⚑ declared (not observed)` until a code anchor confirms it. For R3 (*intent*) documentation legitimately carries more weight, since intent is rarely written in code -- but it still travels under an RE-02 confidence level, and a declared-but-unbuilt capability is strong evidence of *intent* even as it is zero evidence of *capability*.

## References

- `shared/constitution.md` -- RE-01, RE-02, RE-04 (the rules this file operationalizes), RE-03 (why no redesign creeps into the worked example above).
- `shared/glossary.md` -- residual candidate, observed/anticipated stressor, anchor, confidence.
- Each producer sub-skill's `## Output contract` -- the per-fragment table shapes that carry these anchors.
