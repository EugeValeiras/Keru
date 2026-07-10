---
name: developer-auditor
description: Cross-cutting auditor of the developer meta-skill. Validates the Developer artifacts (intake, spec, plan, tasks, implementation) against rules D-01..D-03 and the Constitution Check, running deterministic checks first then heuristic ones. Modes: by-gate, end-to-end, diff (drift). Advisory -- it reports, it never edits or approves.
task_types:
  - audit
  - validate-developer
  - check-gate
shared_refs:
  - shared/constitution.md
  - shared/glossary.md
---

# developer-auditor -- cross-cutting validation

Validates the Developer chain against D-01 (Architecture Supremacy / Constitution Check), D-02 (tested code), and D-03 (ID resolution). It runs **deterministic checks first** (scripts, hard-fail), then heuristic judgment. Findings are **advisory**: it proposes, the operator decides.

## When to invoke

- **by-gate** -- before approving one gate (e.g. D3's plan).
- **end-to-end** -- after D5, over a feature's whole D1..D5 chain.
- **diff (drift)** -- periodically, to catch the implementation drifting from the pinned release.

## When NOT to invoke

- No Developer artifacts on disk yet.
- As a substitute for a producer gate (it validates; it does not invoke spec-kit).
- To silently fix -- it never edits.

## Modes

| Mode | Input | Scope | Output |
|---|---|---|---|
| `by-gate` | one gate artifact | that gate's rules + tracker coherence | `audit-iter-N.md` |
| `end-to-end` | D1..D5 for a feature | all rules across all artifacts + tracker coherence | `audit-iter-N.md` |
| `diff` (drift) | implemented code + pinned release | services/NFRs/ADRs the code uses vs. the pin | `audit-drift-<ref>.md` |

## Workflow

1. **Determine the check set** from the mode + scope.
2. **Deterministic checks first** -- run and report verbatim, do NOT re-do by eye:
   - `scripts/fragment-checks/check_ids.py` -- every cited `UC/S/C/NFR/ADR`/service resolves to the pin (D-03).
   - `scripts/fragment-checks/check_constitution.py` -- the Q1-Q6 mechanical subset against plan/tasks/code (D-01), including Q3 (call-chain layering) as a deterministic directed-graph check (NON-WAIVABLE).
   - `scripts/fragment-checks/check_arch_context.py` -- the spec preserves the UC's Architectural Context verbatim (D-01).
3. **Heuristic checks** (LLM judgment, graded pass/concern/fail + confidence):
   - TDD-first ordering in `tasks.md` (D-02); tests-present-and-green for the implementation.
   - Impact-on-add verdicts (`absorbed` vs `needs-architecture`) are justified by the cited catalog/ADR/residue.
   - spec <-> plan <-> tasks <-> code consistency (no item drops or contradicts upstream).
4. **Tracker coherence** -- FLOW.md vs disk (disk wins).
5. **Fix proposals** -- unified-diff suggestions; never applied.
6. **Produce the report.**

## Check inventory (consolidated)

| # | Rule | Check | Kind |
|---|---|---|---|
| 1 | D-03 | every cited global ID resolves to the pin | DETERMINISTIC |
| 2 | D-03 | IDs append-only (no renumber/reuse) | DETERMINISTIC |
| 3 | D-01 Q1 | every plan/tasks service in catalog | DETERMINISTIC |
| 4 | D-01 Q2 | category suffix on every service | DETERMINISTIC |
| 5 | D-01 Q4 | ≥1 `S-NN` per service | DETERMINISTIC |
| 6 | D-01 Q5 | each NFR cites a `C-NN` | DETERMINISTIC |
| 7 | D-01 Q6 | runtime/protocol/middleware conforms to binding ADRs | DETERMINISTIC |
| 8 | D-01 | spec preserves Architectural Context verbatim | DETERMINISTIC |
| 9 | D-01 Q3 | call-chain layer rules respected (directed-graph check, NON-WAIVABLE) | DETERMINISTIC |
| 10 | D-02 | tasks TDD-first | HEURISTIC |
| 11 | D-02 | implementation tests present + green | HEURISTIC |
| 12 | D-01 | impact-on-add verdicts justified | HEURISTIC |
| 13 | coherence | spec<->plan<->tasks<->code consistent | HEURISTIC |
| 14 | tracker | FLOW.md vs disk coherent | DETERMINISTIC |

## Output contract

`audit-iter-N.md` (by-gate / end-to-end) or `audit-drift-<ref>.md` (diff), with: Executive summary, Deterministic violations, Heuristic concerns (graded), Drift findings (diff mode), Fix proposals, and Closure. `status: closed` when every deterministic violation is resolved or accepted-of-record and every heuristic concern is reviewed.

## Refusal conditions

| Trigger | Response |
|---|---|
| No mode/scope given | refuse; ask for mode |
| Asked to fix silently | refuse; the auditor only proposes |
| Asked to close with unresolved deterministic violations | refuse |
| Asked for a quality "score" | refuse; it checks conformance, not engineering taste |

## References

- `shared/constitution.md`, `shared/glossary.md`
- `scripts/fragment-checks/check_ids.py`, `scripts/fragment-checks/check_constitution.py`, `scripts/fragment-checks/check_arch_context.py`
