<!--
TEMPLATE: system-cartography.md (R1 fragment)
Produced by the system-cartography sub-skill. Fill every section by READING the target repo.
GOLDEN RULE (RE-01): every claim below carries an anchor -- `file:line`, a commit SHA, or a
fenced command+output block. A claim you cannot anchor is dropped or marked `⚠ unverified`.
ONE ANCHOR PER FACT: in the table sections (Runtimes & stack, Build & deploy) do NOT pack several
facts behind one bare comma-separated line list -- pair each fact with its own line inline
(`npm ci (:14), CMD (:33)`). And when citing the same construct across sibling files (web/ vs
gateway/ package.json or Dockerfile) RE-WALK each file -- a line right in one is wrong in the other.
DESCRIPTIVE ONLY (RE-03): inventory what exists. No "should", no refactors, no renaming.
DOCS ARE A LEAD, CODE IS PROOF (RE-01 §6): sweep all docs (state the command + count in Gaps),
corroborate the inventory with them, but a structural item docs declare and code lacks is
`⚑ declared (not observed)`, not an observed item. No information in the repo is discarded.
Delete this comment block when producing the real fragment. No frontmatter -- this fragment is
meant to be inlined as the SAD's *audit* plane.
-->

# System Cartography -- <target name>

> Recon R1. Reconstructed primarily from the running code (the source of truth), with documentation swept as a corroborating lead. Every claim is anchored; see `⚠ unverified` for gaps and `⚑ declared (not observed)` for documented-but-unbuilt items.

## Overview

One paragraph: what kind of system this is in structural terms (a single web service / a set of services / a CLI / a library / a monolith with N modules), the primary language(s)/runtime(s), and the single entry surface(s). Anchored. No intent yet (that is R3).

## Runtimes & stack

| Aspect | Finding | Anchor |
|---|---|---|
| Language(s) / version | | e.g. `global.json:3`, `go.mod:1`, `package.json:14` |
| Framework(s) | | |
| Build system | | e.g. `Makefile`, `*.csproj`, `pom.xml` |
| Package/dependency manifest | | |

## Entry points

Every way the outside world gets in: HTTP routes, gRPC services, CLI verbs, message consumers, scheduled jobs, public library APIs.

| # | Kind (HTTP/CLI/queue/cron/lib) | Entry | Handler | Anchor |
|---|---|---|---|---|
| 1 | | e.g. `POST /api/orders` | e.g. `OrdersController.Create` | `src/...:NN` |

State how the list was enumerated as a ```` ```verify ```` block (command + verbatim count), so `check-counts.py` re-runs it and the completeness is *mechanically* re-checkable -- not a trusted prose number (RE-01). Every count claim in this fragment (entry points, actor tally, registration counts) is a `verify` block, e.g.:

```verify
grep -rn "MapGet\|MapPost\|\[Http" src | wc -l
11
```

## Modules / services / components

The internal structural units as they exist on disk (directories, projects, packages, namespaces). Use the **names the code uses** (RE-03) -- not improved ones.

| Module / unit | Responsibility (as observed) | Anchor |
|---|---|---|
| | | path / `file:line` |

If the system is split into deployable services, note the boundary and how it is deployed.

## Data stores

Every place state lives: databases, queues, caches, file stores, external state-holding systems.

| Store | Kind (SQL/NoSQL/queue/cache/file) | Accessed via | Anchor |
|---|---|---|---|
| | | e.g. EF Core context / repository / driver | `file:line` (connection config + access code) |

## External integrations

Third-party / cross-system calls leaving this system: APIs, SaaS, webhooks, other internal systems.

| Integration | Direction (out/in) | Via | Anchor | Notes |
|---|---|---|---|---|
| | | | `file:line` | mark `⚠ unverified` if the target is config-only and not resolvable from the repo |

## Build & deploy topology

How the system is built, packaged, and deployed, as evidenced by CI config, Dockerfiles, IaC, deploy scripts.

| Aspect | Finding | Anchor |
|---|---|---|
| Build / CI | | `.github/workflows/...`, `Jenkinsfile`, etc. |
| Packaging | | `Dockerfile`, etc. |
| Deploy target / topology | | IaC / manifests; `⚠ unverified` if not in repo |

## Carry-forward to later gates

Short notes for R2/R3/R4 -- not findings, pointers: which modules look hot or large (for R4 churn/contagion), which entry points have the densest logic (for R2 flows), which directories hint at the domain (for R3 intent). Anchored where possible.

## Census coverage

From `repo-census.py` (Step 0; manifest in `r1-inventory.json`). The per-category count table, then an **exclusions** list: every censused file not individually inventoried above, with a one-line reason. The auditor runs `repo-census.py coverage` -- every file is referenced above or listed here (RE-01 §6, nothing lost).

| Category | Count |
|---|---|
| source:<lang> / test / config / docs / build-ci / iac-deploy / schema-migration / asset-binary / generated-lock / unclassified | |

**Excluded (out of scope), with reason:**

| Path (or dir) | Reason |
|---|---|
| | e.g. `.claude/` -- installed tooling, not the system; generated binary; runtime log |

(Every `unclassified` file is dispositioned here -- inventoried above, or excluded with a reason.)

## Gaps & unverified

Anything that could not be anchored from the repo alone (runtime-only behavior, config-resolved targets, absent infra definitions), each marked `⚠ unverified` with the missing anchor named. Documented-but-unbuilt structural items marked `⚑ declared (not observed)`.
