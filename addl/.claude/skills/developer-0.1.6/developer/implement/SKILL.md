---
name: implement
description: D5 of the developer meta-skill. Invokes spec-kit's /speckit-implement to execute the approved tasks into code and tests in the consumer repo, then verifies the tests run green and the Constitution conformance still holds after the code exists (no service/NFR/ADR drift introduced while implementing).
task_types:
  - implement-feature
  - drive-speckit-implement
shared_refs:
  - shared/constitution.md
  - shared/glossary.md
---

# implement -- D5 (implementation)

The final gate. Drives **spec-kit `/speckit-implement`** to execute the task list into code + tests. spec-kit writes the implementation; this gate refuses to approve unless the tests are green and the code still conforms to the landed architecture.

## When to invoke

- D4 approved (TDD-first task list) -- to implement the **next task range** the orchestrator names (a phase, or several phases). D5 is **incremental**: it is invoked once per increment, parking for review between increments, until every task is `[X]`.
- To re-implement after a D5 reopen or a failed verification.

## When NOT to invoke

- D4 not approved.
- To hand-write the implementation -- `/speckit-implement` owns the content; this gate verifies it.

## Pre-conditions

- D4 `[x]` approved; `tasks.md` is TDD-first.

## Handoff contract

- **Consumes:** `specs/NNN-<slug>/tasks.md`, `plan.md`, and the binding constraints (ADRs, NFRs).
- **Produces:** code + tests in the consumer source tree (gate **D5**) -- spec-kit's implementation.
- **Carry-forward:** the green test run + the post-implementation conformance verdict, which the Developer-Auditor's `diff` mode uses as the drift baseline.

## Workflow

1. **Cross-artifact consistency first (read-only), once per feature.** On the FIRST implement increment, run `/speckit-analyze` -- it runs at this D4->D5 boundary (after `tasks.md`, before implementing) and reports spec<->plan<->tasks<->constitution inconsistencies without writing anything. Resolve CRITICAL findings before implementing. (Later increments of the same feature skip re-analyze unless the artifacts changed.)
2. **Invoke spec-kit for the NAMED RANGE only.** The orchestrator names an exact set of `tasks.md` task ids in the inject -- the incomplete tasks through the operator's chosen target phase. Run `/speckit-implement` to execute **exactly those tasks** (tests, then code, TDD order); it marks each `[X]` in `tasks.md` as it completes. **Do NOT implement tasks beyond the named range** -- the remaining phases are separate, operator-gated increments. (With no range named, fall back to the next incomplete phase.)
3. **Verify tests green (D-02).** Run the consumer's test suite. A red or absent suite blocks the gate -- do not approve around it.
4. **Verify post-implementation conformance against the CODE (drift, deterministic).** The drift re-check reads what actually shipped, not the plan. Collect the source paths the completed tasks touched (listed in `tasks.md`) and run `scripts/fragment-checks/check_scope.py specs/NNN-<slug>/spec.md architecture/arch-X.Y.Z/use-cases/uc-NNN-*.md --code <those source paths>`: no service outside the UC's "Services touched" may appear in the code. Re-run `scripts/fragment-checks/check_ids.py` over `tasks.md` for ID drift. If the code introduced a service, NFR, or runtime decision the architecture did not sanction (D-01), that is a finding -- request changes or, if the code genuinely needs something new, the impact-on-add `needs-architecture` path (back-channel to the SAD).
5. **STOP for review after the increment.** Park D5 at `[?]` with this increment's test result + conformance verdict. The operator reviews the increment and either triggers the **next** task range (back to step 2) or, once **every** task in `tasks.md` is `[X]`, **fully approves D5**. The orchestrator commits each reviewed increment to the feature branch; D5 cannot be fully approved while any task is still `[ ]`. **Approving D5 is NOT integration:** the feature lives on its `NNN-<slug>` branch until the operator **explicitly authorizes** Integrate-to-base (a PR via the remote, or a local `--no-ff` merge). Do **not** merge, push, or open a PR on your own -- integration is an authorized outward act the orchestrator performs on the operator's trigger (mirror of the SAD `S8a -> S8b` land rule). After it lands, the flow returns to Phase A for the next UC. (See `SKILL.md` -- the Consumer-repo git lifecycle section.)

## Phased implementation

D5 is **incremental**, not all-at-once. `tasks.md` is grouped by `## Phase N`, and
each user-story phase is an independently testable increment. The operator chooses
how far to implement each time (a single next phase, or several phases at once);
the orchestrator computes the incomplete-task range through that target phase and
names it in the inject. You implement exactly that range (TDD), mark those tasks
`[X]`, and park for review. Repeat until every task is `[X]`, at which point D5 is
fully approvable. This keeps large implementations reviewable in slices and lets
the operator stop, inspect, and resume -- never a single unreviewable big-bang.

The completion signal is the `tasks.md` checkboxes: the orchestrator reads them to
show progress, to compute the next range, and to gate the final approve (no open
`[ ]` task may remain). Mark `[X]` honestly and only for tasks you actually
implemented and whose tests pass.

## Output contract

- Code + tests in the consumer repo (spec-kit's output), tests green.
- The test-run result + post-implementation conformance verdict + a 2-4 line summary.

## Refusal conditions

| Trigger | Rule | Response |
|---|---|---|
| Tests red or absent | D-02 | refuse; the implementation is not done |
| Code uses a service/NFR/runtime the architecture did not sanction | D-01 | request changes, or back-channel if genuinely needed |
| Operator asks to approve with failing tests "for now" | D-02 | refuse; tested means tested |

## References

- `shared/constitution.md`, `shared/glossary.md`
- `scripts/fragment-checks/check_scope.py` (`--code`), `scripts/fragment-checks/check_ids.py`, `scripts/fragment-checks/check_constitution.py`
