<!--
TEMPLATE: reconstructed-business-view.md (R3 fragment)
Produced by the business-reconstruction sub-skill. INFER the business intent (objective, users,
pain points, goals) from R1+R2 + git history + naming + tests.
GOLDEN RULE (RE-01): every supporting fact is anchored.
INFERRED INTENT LABELLED (RE-02): every intent claim carries Confidence (high/medium/low) AND
the Evidence behind it. Intent is NEVER stated as fact -- it is reconstructed and weighted.
Pre-condition: R1 + R2 approved.
This fragment feeds the SAD's *business framing* plane -> S1a. Delete this comment block.
No frontmatter -- it is inlined as the SAD's Business View input.
-->

# Reconstructed Business View -- <target name>

> Recon R3. The system's *intent* reconstructed by inference from the implementation, git history, and naming. Unlike R1/R2, these are deductions: each carries a confidence level and the evidence it rests on (RE-02). A stakeholder should confirm anything below `high`.

## Inferred objective

What the system is *for*, in business terms (one paragraph). State it as inferred.

- **Confidence:** high | medium | low
- **Evidence:** the converging anchors -- domain aggregates, key endpoints, git-history weight, naming. List them (`file:line`, commit, command output).

## Inferred users / actors

Who the system is built to serve, deduced from auth roles, client types, actor names in the domain, API consumers.

| Inferred actor | Evidence | Confidence |
|---|---|---|
| | `file:line` / role enum / client app | high/med/low |

## Inferred pain points (what the system exists to relieve)

The problems the system appears built to solve, deduced from what it automates, what it replaces, what the commit history shows it iterating on.

| Inferred pain point | Evidence | Confidence |
|---|---|---|
| e.g. "manual month-end reconciliation" | `ReconciliationJob` (`file:line`) + commit msg `<sha>` | medium |

## Inferred goals (what success looks like)

Observable outcomes the system appears designed to achieve, deduced from features, metrics, SLAs in config, test assertions.

| Inferred goal | Evidence | Confidence |
|---|---|---|
| | | |

## Inference method note

One short paragraph: how the inferences were drawn (which signals -- directory structure, domain model, git history, tests, naming) and the dominant sources of uncertainty. This is what lets a reviewer judge whether the confidences are calibrated.

## Open questions for a stakeholder

The intent questions the code cannot answer -- the things a human would have to confirm. These are exactly the items that came out `low` or `medium` above, plus genuine ambiguities. (This maps onto the SAD's S1a Open Questions.)

| # | Question | Why the code can't answer it (initially) | Affects | Status |
|---|---|---|---|---|
| Q1 | | | which inferred objective/goal | Open |

> **Status** is one of `Open` (not yet investigated past R3's first pass), `Resolved: <answer> (anchor)`
> (the open-question resolution pass found a file:line/commit answer), or `Stakeholder required: <why>`
> (the code genuinely cannot answer -- carry to the SAD's S1a Open Questions). A `Resolved:` row MUST
> carry an anchor (RE-01); only `Open`/`Stakeholder required` rows may lack one.

## Confidence summary

A one-line tally: N high, M medium, K low. If `low`/`medium` dominate, say plainly that the business framing is a hypothesis the SAD should confirm with a stakeholder, not a settled foundation.
