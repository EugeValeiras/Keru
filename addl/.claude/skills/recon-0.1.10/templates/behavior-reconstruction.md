<!--
TEMPLATE: behavior-reconstruction.md (R2 fragment)
Produced by the behavior-reconstruction sub-skill. Reconstruct what the system ACTUALLY DOES
from its routes, handlers, jobs, schedulers, and tests. Sweep ALL documentation (README, docs/**,
*.puml, *.http) for declared flows too -- but documentation is a LEAD, code is the PROOF (RE-01 §6):
a declared flow confirmed against code is observed; one with no code is `⚑ declared (not observed)`.
GOLDEN RULE (RE-01): every flow/use case traces to anchors (`file:line` along the call path,
or a test that exercises it). Unanchored behavior is dropped or `⚠ unverified`. No information in
the repo is discarded -- declared-but-unbuilt use cases are captured, not lost.
DESCRIPTIVE ONLY (RE-03): describe observed behavior, not desired behavior. No redesign.
Pre-condition: R1 (system-cartography.md) approved -- the entry points are the seeds for flows.
Delete this comment block. No frontmatter -- inlined as the SAD's *audit* plane.
-->

# Behavior Reconstruction -- <target name>

> Recon R2. What the system observably does, traced from R1's entry points through to data stores and side effects. Every flow is anchored along its path; tests cited where they pin behavior.

## Observed use cases / flows

One subsection per significant flow. A flow starts at an R1 entry point and follows the call chain to its effects (writes, external calls, emitted events). Reconstruct from the code; cite the chain.

### Flow: <name as the code suggests it>

- **Trigger / entry:** the R1 entry point that starts it. Anchor.
- **Path:** the observed call chain, step by step, each step anchored.
  - `EntryHandler` (`file:line`) -> `Service.Method` (`file:line`) -> `Repository.Save` (`file:line`) -> data store.
- **Effects:** what changes -- rows written, events emitted, external calls made. Anchored.
- **Confirmed by:** a test that exercises this flow, if one exists (`tests/...:NN`). If none, say so -- absence of a test is itself a finding.
- **Notes / `⚠ unverified`:** branches not fully traced, dynamic dispatch you could not resolve statically.

(Repeat per flow. Order them by entry-point importance from R1.)

## Background / scheduled / event-driven behavior

Flows not triggered by a synchronous request: cron jobs, queue consumers, timers, startup hooks.

| Behavior | Trigger | What it does | Anchor |
|---|---|---|---|
| | e.g. cron `0 2 * * *` | | `file:line` (schedule + handler) |

## Behavior evidenced only by tests

Behavior you could infer mainly from the test suite (the tests assert it, the production path is indirect). Useful because tests encode intended behavior explicitly.

| Behavior | Test | Anchor |
|---|---|---|
| | | `tests/...:NN` |

## Declared use cases (not observed)

Use cases / flows the **documentation declares** (README, `docs/**`, `*.puml`, `*.http`) but for which **no implementing code exists** -- intended-but-unbuilt milestones (RE-01 §6). Captured, never dropped; segregated from observed flows. Each row anchors BOTH the declaring doc AND the confirmed absence in code. May be empty.

| Declared use case | Declared in (doc anchor) | Confirmed absent in code (anchor) | Note |
|---|---|---|---|
| | e.g. `README.md:9-15` | e.g. `grep -rn "orders.cmd.v1" services` -> only publisher; handler bodies absent | `⚑ declared (not observed)` -- candidate milestone |

## Cross-flow observations

Shared handlers, common middleware, behavior that spans flows (auth, logging, transactions). Descriptive. Note where flows converge on the same module (a pointer for R4 coupling analysis).

## Gaps & unverified

Flows that depend on runtime config, external state, or dynamic dispatch you could not resolve from the repo -- each `⚠ unverified` with the missing anchor named. Entry points from R1 for which no handler logic could be located (a sign R1 may need reopening). State the **documentation-sweep command + count** here so coverage is auditable (RE-01 §6 completeness) -- nothing in the repo went unread.
