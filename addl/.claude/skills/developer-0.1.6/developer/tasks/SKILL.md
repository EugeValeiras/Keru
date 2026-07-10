---
name: tasks
description: D4 of the developer meta-skill. Invokes spec-kit's /speckit-tasks to generate the ordered, TDD-first task list from the approved plan, then reviews that tests precede implementation and every task traces to a spec/plan item that still conforms to the landed architecture.
task_types:
  - generate-tasks
  - drive-speckit-tasks
shared_refs:
  - shared/constitution.md
  - shared/glossary.md
---

# tasks -- D4 (task list)

Drives **spec-kit `/speckit-tasks`** to turn the approved plan into an ordered task list. spec-kit generates the tasks; this gate enforces D-02 (test-driven) and confirms no task reintroduces an architecture violation the Constitution Check cleared at D3.

## When to invoke

- D3 approved (Q1-Q6 all yes) for a feature.
- To regenerate tasks after a D4 reopen.

## When NOT to invoke

- D3 not approved, or its Constitution Check has an open No.
- To write tasks by hand -- `/speckit-tasks` owns the content.

## Pre-conditions

- D3 `[x]` approved; `plan.md` Constitution Check is all `yes`.

## Handoff contract

- **Consumes:** `specs/NNN-<slug>/plan.md` (+ research/data-model/contracts) and the carry-forward constraints (binding ADRs, NFR scopes).
- **Produces:** `specs/NNN-<slug>/tasks.md` (gate **D4**) -- ordered, TDD-first.
- **Carry-forward:** the test-first ordering and the per-task service/ID references, so D5's implementation stays conformant and verifiable.

## Workflow

1. **Invoke spec-kit -- and demand TDD (D-02).** Run `/speckit-tasks`. spec-kit's tasks are **test-optional by default** (it generates tests only when the spec asks or the user requests TDD), so the invocation MUST explicitly direct it to produce a **TDD-first** list: test tasks precede their implementation tasks. Without this, `tasks.md` ships without tests and D5 cannot pass honestly.
2. **Verify TDD-first (deterministic, D-02).** Run `scripts/fragment-checks/check_tdd.py specs/NNN-<slug>/tasks.md`. spec-kit organizes tasks by user story; the check requires, **per user story**, that there is at least one test task and that no implementation task precedes the first test task (Setup/Foundational/Polish phases are infrastructure and exempt). A `tasks.md` that omits a story's tests -- spec-kit's test-optional default -- or lists code before its tests is sent back (re-run `/speckit-tasks` directing it to TDD-first), not patched here.
3. **Verify traceability + conformance (deterministic).** Run `scripts/fragment-checks/check_ids.py specs/NNN-<slug>/tasks.md architecture/arch-X.Y.Z/`: every service/NFR/ADR a task references resolves to the pin and matches the plan (no task silently adds a service the Constitution Check did not clear).
4. **STOP at the gate.** Park D4 at `[?]`. Do not begin D5.

## Output contract

- `specs/NNN-<slug>/tasks.md` (spec-kit's structure), TDD-first.
- The TDD-ordering verdict + ID/conformance verdict + a 2-4 line summary.

## Refusal conditions

| Trigger | Rule | Response |
|---|---|---|
| Tasks place implementation before its tests | D-02 | request changes; TDD-first is required |
| A task references a service/ID not cleared at D3 | D-01 / D-03 | refuse; the Constitution Check governs |

## References

- `shared/constitution.md`, `shared/glossary.md`
- `scripts/fragment-checks/check_tdd.py`, `scripts/fragment-checks/check_ids.py`
