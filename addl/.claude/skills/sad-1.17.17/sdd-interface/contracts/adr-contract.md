---
title: "RDAG Contract -- ADR-NNN.md"
version: 0.1.0
date: 2026-05-26
status: Draft (Phase 0b)
---

# RDAG Contract -- `ADR-NNN.md`

An ADR is the **mechanism of the seam**. A runtime, protocol, or middleware
decision captured in an ADR is **promoted from implementation territory to a
binding architecture constraint** (Architecture Supremacy,
`../standard/rdag-standard.md` §4): the implementation half must conform and may
not substitute an alternative. This is the lever that moves the line between the
two halves. This contract defines the ADR schema, the binding mechanism, and the
mapping from the SAD. Ids in `../standard/rdag-id-scheme.md`.

**Emitted from:** the SAD's ADRs (decisions deferred from residue analysis, and
runtime/protocol decisions). **Landing zone:** the path the consumer's
constitution names, inside the release directory: `architecture/arch-X.Y.Z/decisions/ADR-NNN.md`.

## 1. The agnosticism boundary -- ADRs may name technology

The RDAG **standard** never names a concrete technology (Agnosticism Rule,
`../standard/rdag-standard.md` §5). A per-project **ADR is the exception**: it
*may and often must* name a runtime/protocol (e.g. Dapr, a messaging protocol,
a saga engine). Agnosticism governs the reusable doctrine; ADRs are concrete
per-project instances. There is no contradiction.

## 2. File schema

```text
# ADR-NNN -- <Title>
<metadata table: Id, Status (Proposed/Accepted/Superseded), Date, Deciders>
## Context        -- the residue/stressor/coupling that forced the decision
## Decision
## Binding scope   -- see §3
## Consequences
## Alternatives considered
```

## 3. Binding scope (the RDAG-specific section)

| Field | Required | Meaning |
|---|---|---|
| **Binding** | yes | `Yes` (claims implementation territory; prevails per Supremacy) or `No` (informational / contextual decision, not enforced against the implementation half). |
| **Claims** | if Binding | The implementation concern reclaimed for architecture, e.g. "service-to-service invocation and pub/sub runtime", "outbound transport protocol". |
| **Constrains** | if Binding | The services / operations bound, by catalog name / `UC-NNN` / `Op-X`. |
| **Conformance check** | if Binding | The condition `/speckit-plan` question 6 evaluates, e.g. "plan's inter-service calls go through the chosen runtime". |

## 4. Field-by-field mapping (SAD -> ADR)

| Section | SAD source | Rule |
|---|---|---|
| Context | the residue/stressor/coupling that forced the decision | Trace to `S-NN` / `C-NN` / service names so the decision is grounded, not arbitrary. |
| Decision | the SAD's recorded decision | State the chosen option plainly. |
| Binding / Claims / Constrains | whether the decision claims a runtime/protocol/middleware | A runtime/protocol/middleware decision is `Binding: Yes`. A purely structural decision already lives in the catalog and is usually `Binding: No` here. |
| Conformance check | the testable condition the decision implies | Phrase it so question 6 can be answered yes/no. |
| Consequences, Alternatives | the SAD's analysis | Carry the rejected options and why. |

## 5. Worked shape -- the Dapr case

> **ADR-007 -- Adopt Dapr for inter-service invocation and pub/sub.**
> Context: the topology coupling `C-04` (Managers must communicate without
> synchronous coupling, R-03) and `S-12` (the system will scale to N nodes).
> Decision: use Dapr building blocks. **Binding: Yes.** Claims: inter-service
> invocation + pub/sub runtime + state building block. Constrains: all Managers
> (cross-Manager communication via Dapr pub/sub, never synchronous). Conformance
> check: plan's Manager->Manager paths use Dapr pub/sub; no synchronous Manager call.

Dapr's building blocks map onto the call rules and actor-style grouping (R-25),
which is exactly why the choice is architectural and, once recorded, binds.

## 6. How the gate finds a binding ADR

A binding ADR's decision MUST be locatable by `/speckit-plan` question 6
(`../standard/rdag-standard.md` §6). It is referenced from the **service
catalog** (the "Binding ADRs" field of each constrained service) and listed in
the **handoff manifest**, so the gate enumerates binding ADRs without scanning.
A binding ADR not referenced anywhere is a contract violation (CHK-12).

## 7. The back-channel

When `/speckit-plan` needs a runtime/protocol decision that no ADR has made, it
does not decide locally -- it raises an **ADR request** to the architecture
team, the runtime/protocol analogue of the catalog amendment request
(`../standard/rdag-standard.md` §6). Inline runtime invention in `plan.md` is a
review blocker, same as inline service invention.

## 8. Conformance

Checked by: **CHK-12** (binding ADR decision locatable from catalog/manifest),
**CHK-11** (cited `S-NN`/`C-NN`/services resolve), **CHK-13** (append-only
`ADR-NNN`). See `../standard/rdag-conformance.md`.

## 9. Related files

- `../standard/rdag-standard.md` -- Architecture Supremacy (§4), Agnosticism
  (§5), gate question 6 (§6).
- `catalog-contract.md` -- the "Binding ADRs" field that points back here.
- `handoff-manifest-contract.md` -- enumerates binding ADRs for the gate.
