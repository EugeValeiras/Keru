---
title: ADR template -- Architecture Decision Record
version: 1.1
date: 2026-06-11
---

# ADR Template

Template for Architecture Decision Records (ADRs) used alongside a Software Architecture Document (SAD) produced by the `sad` meta-skill.

The SAD is the integrated artefact for a project: it carries the residual analysis, contagion matrix, residue logs, NFRs, and the resolved architecture. Most decisions live there. ADRs are a complementary artefact for decisions that are too large, too contested, or too long-lived to fit in a single SAD cell.

---

## When to use an ADR

Use an ADR when:

- A decision has **multiple plausible options**, each with non-trivial consequences (database engine, message bus implementation, multi-region replication strategy, public API style).
- A decision **supersedes** an earlier decision and needs an explicit `supersedes ADR-XXXX` link.
- A decision **ages independently** of the SAD (e.g., a contract with an external partner that the SAD references but does not embed).
- A decision affects **governance, compliance, or risk** and needs status tracking (PROPOSED -> ACCEPTED) for stakeholder sign-off.

Do NOT use an ADR when:

- The decision can be captured in a Business Residues Log row with a one-paragraph rationale -- use the log.
- The decision is just a refactor candidate from a Contagion Matrix reading -- use the §Refactor Triggers section of the SAD.
- The decision is an NFR derivation -- use the Derived NFRs table with a Source.
- The decision is a simple guardrail compliance choice -- it is already captured by the constitution rule that motivated it.

---

## Where to file an ADR

ADRs live alongside the SAD they support, in the project workspace, not in this meta-skill repository. The conventional path:

```
<project-root>/docs/adr/ADR-XXXX-<short-name>.md
```

- `XXXX` is a zero-padded sequence (`0001`, `0002`, ...) per project.
- `<short-name>` is `lowercase-hyphenated`.
- Each ADR is a separate file. ADRs are individually versioned by status, not by version number.

A project commonly maintains an `ADR-INDEX.md` next to the ADR files, listing all ADRs with their current status. The index is optional but recommended once the project has more than ~5 ADRs.

---

## How to reference an ADR from the SAD

The SAD references ADRs from sections where the decision applies. Common reference points:

| SAD section | When to reference an ADR |
|---|---|
| §Restrictions | When an ADR establishes a hard constraint (e.g., "all message-bus traffic uses Pulsar via Dapr -- see ADR-0003"). |
| §Technical Considerations | When an ADR documents a technology choice that does not rise to a hard restriction. |
| §Business Residues Log -- Rationale column | When a business residue's reasoning is fully detailed in an ADR (the log keeps a one-line summary; the ADR holds the depth). |
| §Topological Residue Map -- Cross-Boundary Constraints column | When the boundary is governed by a regulatory or partner ADR. |
| §Derived NFRs -- Source column | Rare. NFRs normally trace to matrix cell / topology row / business residue. An ADR-sourced NFR is acceptable only when the ADR ITSELF was driven by a Structural / Topological / Business residue (not the other way around). |

A reference is a backticked ADR ID: `` `ADR-0003` `` or a markdown link if the project hosts the ADRs at a known URL.

---

## Status lifecycle

| Status | Meaning |
|---|---|
| `DRAFT` | Author is still iterating on the content. Not yet shared for review. |
| `PROPOSED` | Open for stakeholder review. The decision is not yet binding. |
| `ACCEPTED` | Reviewed and approved. The decision is binding for the project. |
| `DECLINED` | Reviewed and rejected. The ADR is preserved as record of what was considered. |
| `SUPERSEDED` | Replaced by a later ADR. The replacing ADR's Linked ADRs field references this one. |

Linked ADR actions:

- `SUPERSEDED` -- this ADR replaces an earlier one. The earlier one's status moves to SUPERSEDED.
- `IMPROVEMENT` -- this ADR refines or extends an earlier one without superseding it. Both stay ACCEPTED.

---

## Template

Copy everything below into a new file at `<project-root>/docs/adr/ADR-XXXX-<short-name>.md`. Replace placeholders. Remove this preamble (everything above the line of dashes).

---

# ADR-XXXX - [Name of ADR]

> **Available statuses:** `DRAFT` `PROPOSED` `ACCEPTED` `DECLINED` `SUPERSEDED`
> **Linked ADR actions:** `SUPERSEDED` `IMPROVEMENT`
>
> **Status is operator-owned and binding.** The orchestrator (ADDL) or a human sets `Status`; the
> executor never changes it unprompted. An `ACCEPTED` ADR is binding -- its decision must be reflected
> in the architecture (the impact gate's fragment cites this ADR by id) before S7 can assemble. See
> `SKILL.md` §Post-S5 actions §ADR lifecycle and `scripts/fragment-checks/check_adr_applied.py`.
>
> **Describe only state you have actually written.** An ADR records *decisions* and the *state of disk*,
> never an intended-but-unperformed action as if completed. If the decision implies an edit to another
> fragment (annotating an upstream candidate as `(re-typed as X)`, sweeping a renamed component, updating
> an S4 map) that you have **not** made -- because the target gate is `[x]` approved, or the edit is
> deferred -- say so explicitly: write "the re-type is **recorded by this ADR**; the inline annotation in
> `<fragment>` is **deferred** (`<audit-finding-id>`)", not "the occurrences **are annotated**." Asserting
> an unperformed action as done is an overclaim the auditor treats as a finding (see `sad-auditor` §ADR
> self-claim consistency).

| Field | Value |
|---|---|
| **Title** | |
| **Status** | PROPOSED |
| **Linked ADRs** | |
| **Date** | DD Mon YYYY |
| **Context** | Describe the architectural design issue you are addressing, leaving no questions about why you are addressing this issue now. Following a minimalist approach, address and document only the issues that need addressing at various points in the life cycle. |
| **Options Considered** | Option 1 / Option 2 |
| **Decision** | |
| **Consequences** | |
| **Risks** | |
| **Impact assessment** | REQUIRED when created via the Create-ADR action (`SKILL.md` Post-S5 actions). See the `## Impact assessment` section below. |

---

## Options Considered

### Option 1 - { Name of Option }

{ Overview of Option }

**Consequences**

- Positive:
- Negative:

**Useful links:**

-

---

### Option 2 - { Name of Option }

{ Overview of Option }

**Consequences**

- Positive:
- Negative:

**Useful links:**

-

---

## Decision

{ Describe the decision made and the rationale behind it. }

---

## Impact assessment

When this ADR is emitted via the **Create-ADR** action defined in
`SKILL.md` Post-S5 actions, this section is REQUIRED (remove it only for
standalone ADRs with no SAD lifecycle in flight). Three fields, verbatim:

- **Affected gates:** { comma-separated Sn ids, may be empty }
- **Outcome:** { exactly one of: `no-op` | `iterating Sn` | `reopen Sn` }
- **Rationale:** { 1-3 sentences citing the diagram / residue / stressor / NFR
  that this decision changes, and enumerating the artifacts that must
  regenerate (which C4 diagram, which NFR rows, which sad.md sections) }

The orchestrator reads the `Outcome:` line and applies the corresponding
FLOW.md transition per `SKILL.md` Gate state machine (canonical). The ADR
itself never mutates the gate tracker. See `SKILL.md` Post-S5 actions for the
outcome -> transition table, including the frontier restriction on
`iterating Sn`.

---

## Cross-references

- `sad/template.md` §Appendices §Architecture Decision Records -- the SAD-side reference to the ADR convention.
- `shared/style-conventions.md` -- US-ASCII, naming conventions, citation patterns also apply to ADR content.
