---
title: Constitution -- Developer meta-skill
version: 0.1.0
date: 2026-06-23
---

# Developer constitution -- the rules

The active rules for the Developer role. Each has a scope, a mechanism (how it is
enforced -- deterministic script, LLM heuristic, or both), and what it defends
against. These are **this skill's own authority**; they do not extend the SAD's
R-01..R-27 or recon's RE-01..RE-05. The Constitution Check Q1-Q6 is the runtime
expression of D-01.

| Rule | Scope | Mechanism | Defends against |
|---|---|---|---|
| **D-01 Architecture Supremacy** | all gates; enforced at D3 | both | implementation silently overriding the binding architecture |
| **D-02 Tested code** | D4, D5 | heuristic + spec-kit | shipping untested or non-TDD implementation |
| **D-03 ID resolution** | D2..D5 | deterministic (`check_ids.py`) | dangling references; invented/renumbered IDs |

## D-01 -- Architecture Supremacy

The landed `architecture/arch-X.Y.Z/` release is **binding**. The Developer
conforms to it and never silently overrides it.

- Services, NFRs, and binding decisions come **only** from the landed release
  (`service-catalog.md`, `nfr-register.md`, `decisions/ADR-*.md`). The Developer
  never invents a service, an NFR, or a binding decision inline.
- When the plan needs something the architecture does not provide, the Developer
  raises a **back-channel request** -- a *catalog amendment request* (new service),
  an *ADR request* (new binding decision), or a *residue-analysis request*
  (missing stressor lineage). It does not decide unilaterally.
- Runtime / protocol / middleware choices conform to every **binding ADR**
  (`Binding: Yes`). A plan that contradicts one is blocked (Constitution Check Q6).

**Runtime expression -- the Constitution Check (Q1-Q6).** Wired into spec-kit's
plan template by the landed `plan-template-constitution-check.md`, it runs at D3.
Q1-Q4 (catalog membership, naming, call-chain layering, structural-stressor
lineage) are **NON-WAIVABLE** and excluded from any Complexity-Tracking waiver;
Q5-Q6 (NFR coupling lineage, binding-ADR conformance) are NON-WAIVABLE per RDAG.
A "No" resolves by amending the architecture (a new release) or raising an ADR --
never by an inline exception.

**Impact-on-add corollary (Phase A only).** A new ADR/UC may be added **only in
the FLOW phase, before a spec-kit workflow starts** -- never during a running
workflow. Each add is evaluated for **absorption** against the landed release:
`absorbed` -> proceed (a target UC / a conforming Tier-2 ADR), no architecture
reopen; `needs-architecture` -> a back-channel request to the SAD. The Developer
never lets an un-absorbed decision pass as if it conformed, and never adds a UC/ADR
mid-workflow (a gap found there stops the workflow and is handled back in Phase A).

**Constitution-drift corollary (the one in-workflow reopen).** If the constitution
changes while a workflow is executing, run an impact assessment against the already
generated `spec.md` / `plan.md` / `tasks.md` / code and **reopen + regenerate** the
impacted step(s) so the artifacts conform to the changed constitution. This is the
only reopen trigger inside a workflow.

## D-02 -- Tested code

Implementation is test-driven and tested. spec-kit's `/speckit-tasks` orders
tests before implementation, and `/speckit-implement` writes both. The Developer
gate (D5) does not approve unless:

- the task list (D4) is TDD-first (test tasks precede their implementation tasks);
- `/speckit-implement` produced tests alongside code; and
- the tests run green and the Constitution conformance still holds after the code
  exists (no service/NFR/ADR drift introduced while implementing).

The Developer does not write the tests itself -- spec-kit does -- but it **refuses
to approve** an implementation gate whose tests are absent or red.

## D-03 -- ID resolution

Every global ID a spec/plan/tasks artifact cites must **resolve** to the pinned
landed release, and IDs are **append-only**:

- `UC-NNN`, `S-NN`, `C-NN`, `NFR-NN`, `ADR-NNN`, `U-NN`, and service names
  (`*Manager`/`*Engine`/`*Access`) referenced in a Developer artifact must exist
  in the landed `architecture/arch-X.Y.Z/` at the pinned version.
- The Developer never renumbers or reuses an ID. A new UC discovered during
  implementation gets the **next** `UC-NNN` (by directory scan), never a recycled
  one.
- A dangling reference (an ID that does not resolve) is a hard finding --
  `scripts/fragment-checks/check_ids.py` fails on it; the gate cannot pass with an unresolved ID.

## Why these rules

The architecture earned its shape through a stress-driven walk (Residuality
Theory) and a volatility-based decomposition (IDesign). That reasoning -- the
"why" (R-22) -- is encoded as residue lineage (`service -> S-NN`), coupling lineage
(`NFR -> C-NN`), and binding ADRs. If the implementation can quietly add a service,
relax an NFR, or pick a runtime the architecture forbade, the governance is
theatre and the SAD's guarantees (the Ri attestation, the criticality goal)
evaporate. D-01 keeps the architecture supreme; D-03 keeps the lineage honest;
D-02 keeps the implementation real. Everything spec-kit produces is welcome -- it
just has to pass through these three gates.
