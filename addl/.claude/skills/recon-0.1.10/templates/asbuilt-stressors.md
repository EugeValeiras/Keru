<!--
TEMPLATE: asbuilt-stressors.md (R4 fragment)
Produced by the asbuilt-stressors sub-skill. Two jobs: (1) type the AS-BUILT in IDesign terms
(descriptive residual candidate for the SAD's S6); (2) surface OBSERVED stressors the system
itself testifies to (for the SAD's S3).
GOLDEN RULE (RE-01): every claim anchored.
DESCRIPTIVE ONLY (RE-03): type and describe what exists + observed coupling. NO redesign,
NO "should decouple", NO target architecture.
OBSERVED ONLY (RE-04): each observed stressor cites real evidence (incident, churn, co-change,
HACK/FIXME, revert, bug-fix cluster). Speculation goes ONLY under "Anticipated (not observed)".
Pre-condition: R3 approved. Delete this comment block. No frontmatter.
This fragment feeds TWO SAD planes: the IDesign typing -> S6 residual candidate; the observed
stressors -> S3.
-->

# As-Built & Observed Stressors -- <target name>

> Recon R4. The existing implementation typed in IDesign terms (a *residual candidate* the SAD's S6 will measure -- evidence, never the baseline) plus the stressors this specific system has actually shown. Observed stressors are anchored; anticipated ones are segregated and labelled.

## As-built IDesign typing (residual candidate)

Type each significant component from R1's inventory as the closest IDesign role **as it actually behaves** -- Manager (workflow/orchestration), Engine (stateless activity/logic), ResourceAccess (state access), Resource (the store itself), Utility (cross-cutting infra), Client (entry point). This is descriptive: if a class does three roles at once, say so -- do not split it (that is the SAD's call).

| Component (code name) | Observed role | Closest IDesign type | Anchor | Notes (e.g. "mixes Manager+Engine+RA") |
|---|---|---|---|---|
| `OrderManager` | parses HTTP, prices, persists, emails | Manager (impure) | `src/OrderManager.cs:1` | does Engine + RA work inline |

State the typing is **descriptive** -- it records how the as-built maps onto IDesign vocabulary so S6 can measure it, not how it ought to be decomposed.

## Observed coupling / contagion

Modules that change together (co-change) or where one change forces another, measured from history. Descriptive only.

| Coupled units | Evidence | Strength |
|---|---|---|
| A <-> B | co-change in commits `<sha1>`, `<sha2>`, `<sha3>`; `git log --format= --name-only` co-occurrence | N of M commits |

## Observed stressors

The high-value output for the SAD's S3: stress this system has **already shown**. Each row MUST carry an anchor proving the system testified to it (RE-04).

| # | Stressor (as observed) | Evidence anchor | Where it bites |
|---|---|---|---|
| 1 | concurrent-checkout double-charge | `// HACK: ...` (`src/...:NN`); 6 fix commits 2025 (`git log ...` output); incident `docs/incidents/...` | `PaymentProcessor` |

Sources of testimony (use whichever apply, always anchored): production incident docs, churn hotspots (`git log --format= --name-only | sort | uniq -c | sort -rn`), bug-fix clusters on a module, `HACK`/`FIXME`/`XXX`/`workaround` comments, reverts, performance TODOs, retry/circuit-breaker code that marks a known failure mode.

## Anticipated (not observed)

Stressors the architect suspects but **cannot anchor** to this system's evidence. Permitted here, clearly separated, never mixed above. The SAD's S3 generates these by method; this section just flags what recon sensed.

| # | Anticipated stressor | Why suspected (reasoning, not evidence) |
|---|---|---|
| A1 | | |

## Handoff notes

- **To S6 (residual candidate):** the IDesign typing above is what S6 measures against the SAD's independently-built naïve baseline. It is evidence, not the baseline.
- **To S3 (stressors):** the Observed list is the part S3 cannot generate itself; the Anticipated list overlaps with what S3 produces by method.

## Gaps & unverified

Stress that runtime/operational data (not in the repo) would reveal -- load behavior, prod error rates -- marked `⚠ unverified`. Note that these are knowable only with ops/observability access.
