---
title: Back-channel request template -- catalog-amendment / ADR / residue-analysis
version: 0.1.1
date: 2026-06-30
---

# Back-channel request template

> The Developer's ONLY legal response to a gap in the architecture: when the plan needs
> something the landed release does not provide, raise a back-channel request to the SAD --
> never an inline invention (D-01 Architecture Supremacy). A Constitution Check "No" routes
> here, the gate STOPS, and the plan is NOT edited to mask the gap. Pick the ONE form whose
> trigger matches the failed question; fill it; surface it for the operator. Same workspace,
> so the SAD picks it up and re-lands a new `arch-X.Y.Z` if warranted.
> See `shared/glossary.md` (Back-channel request) and `developer/plan/SKILL.md` (step 3).

| Failed question | Form to use |
|---|---|
| Q1 (a plan service is absent from the catalog) | Catalog amendment request |
| Q6 (the plan contradicts a binding ADR, or a new binding decision is needed) | ADR request |
| Q4 / Q5 (a service lacks a structural `S-NN`, or an NFR lacks a coupling `C-NN`) | Residue-analysis request |

## The written instance -- required YAML frontmatter

The file you WRITE is `docs/developer/back-channel-NNN-<slug>.md` (NOT this template
verbatim). It MUST lead with a YAML frontmatter block carrying the fields the orchestrator's
back-channel tracker reads -- `status`, `gate`, `pin` -- so the request surfaces with its
status pill, its "blocks Dn" chip, and the architecture pin it was raised against. A literal
copy of this template (whose own frontmatter is just doc metadata) leaves those null and the
tracker degrades to a bare "open" entry. Lead the instance with EXACTLY this shape, then the
matching Form body below:

```yaml
---
title: <short title of the gap>
status: open          # the orchestrator owns this open -> routed -> resolved; never edit after writing
gate: D3 plan         # the gate this blocks (D2 for a specify-time UC gap; D3 for a plan-time ADR / residue gap)
pin: arch-X.Y.Z       # the landed release pinned at D1 that this request was raised against
date: <YYYY-MM-DD>
---
```

The body keeps a human `- **Status:**` line for readability, but the frontmatter `status:`
is the authoritative value the tracker reads -- set them consistently at write time; after
that the orchestrator owns the frontmatter `status:` and you never touch it.

---

## Form A -- Catalog amendment request (Q1)

- **Gate / question:** D3 plan -- Q1 (catalog membership)
- **Finding:** <the service the plan needs, and where it is referenced>
- **Why it cannot be absorbed:** <the catalog has no such service; naming it inline would invent architecture>
- **Requested change:** add (or correct the name of) the service `<Name>Manager|Engine|Access` in `service-catalog.md`, with its category and residue lineage.
- **Blocked plan section(s):** <spec/plan references waiting on this>
- **Status:** `open` (awaiting SAD re-land) | `resolved by arch-X.Y.Z`

## Form B -- ADR request (Q6 / new binding decision)

- **Gate / question:** D3 plan -- Q6 (binding-ADR conformance), or a D2/D3 impact-on-add `needs-architecture`
- **Issue:** <the binding ADR the plan contradicts, or the runtime/protocol/middleware decision that needs a binding ruling>
- **Proposed decision (for the SAD to rule on, not the Developer to set):** <the candidate decision + the conformance condition it would impose>
- **Rationale:** <why the implementation cannot decide this unilaterally -- it is architecture territory>
- **Blocked plan section(s):** <references waiting on the ruling>
- **Status:** `open` (awaiting SAD re-land) | `resolved by ADR-NNN in arch-X.Y.Z`

## Form C -- Residue-analysis request (Q4 / Q5)

- **Gate / question:** D3 plan -- Q4 (structural `S-NN` lineage) or Q5 (NFR coupling `C-NN`)
- **Finding:** <the service with no structural `S-NN`, or the NFR with no coupling `C-NN`>
- **Why it is an architecture gap:** the lineage is incomplete -- the residue/coupling that justifies the service or NFR is not recorded; the Developer cannot synthesize it.
- **Requested analysis:** record the missing `S-NN` / `C-NN` for `<service or NFR>` in the relevant register.
- **Blocked plan section(s):** <references waiting on the lineage>
- **Status:** `open` (awaiting SAD re-land) | `resolved by arch-X.Y.Z`
