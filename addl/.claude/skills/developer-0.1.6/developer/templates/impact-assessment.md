---
title: Impact assessment template -- UC/ADR add during Phase A
version: 0.1.0
date: 2026-06-24
---

# Impact assessment template

> Reusable block emitted whenever Phase A surfaces a NEW use case (at D2 specify) or a new
> implementation ADR (at D3 plan). Paste the `## Impact assessment` block below into the
> artifact. Adds are a **Phase A activity only** -- never during the spec-kit workflow
> (Phase B). The block has exactly three fields plus the routed outcome.
> See `developer/SKILL.md` (Impact assessment) and `developer/specify/SKILL.md` /
> `developer/plan/SKILL.md` (impact-on-add).

## Impact assessment

- **Affected:** <the catalog services / NFRs / binding ADRs this add touches; cite ids>
- **Absorption:** `absorbed` | `needs-architecture`
- **Rationale:** <1-3 sentences: why it is absorbed by the landed architecture, or why it needs an upstream change>

### Outcome (determined by Absorption)

- `absorbed` -- a Tier-2 decision that conforms to the binding ADRs (and, for a new UC, fits
  the landed catalog/NFRs). It gets the next append-only `UC-NNN` / `ADR-NNN` and proceeds.
- `needs-architecture` -- it cannot be absorbed under Architecture Supremacy. **STOP** and
  raise a back-channel request (see `developer/templates/back-channel-request.md`); the
  resolution is an upstream SAD re-land (a new `arch-X.Y.Z`), surfaced for the operator.
  Never invent the service / NFR / binding decision inline (D-01).
