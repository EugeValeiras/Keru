# Sync Impact Report (draft) -- adopting "Service Decomposition by Residue"

> **Emitted by:** speckit-handoff (S8) at RDAG 0.1.0, as a **draft** to guide the
> gated integration step. It is illustrative for this worked example (EV Charging
> has no real consumer repo); it is written as it would read for a consumer that
> currently governs decomposition "by Volatility" -- e.g. a spec-kit project whose
> `.specify/memory/constitution.md` has a Principle "Service Decomposition by
> Volatility". A human applies this during integration; S8 does not edit the
> consumer's constitution.

## Apply mode

**insert/replace** -- the consumer already has a constitution. Swap the
architecture-half principle; leave every implementation-half principle (language,
testing, observability, etc.) untouched.

*(For a greenfield consumer the mode would be `scaffold`: create the full
constitution with this principle complete and implementation-half principles as
labeled stubs.)*

## Version bump

A principle replacement is a **major** constitution amendment. Bump per the
consumer's Governance section and record this report in the same change.

## Reconciliations table (insert/replace mode -- competing principles)

Used when the host has a real implementation constitution AND a **competing
decomposition principle** (canonical case: "Service Decomposition by
**Volatility**"). It is a CHK-04 conflict -- the Residue principle **supersedes**
it (Architecture Supremacy); the two are NOT merged. The implementation-half
principles (Tech Stack, language, testing, ...) import verbatim. Confirm each
row before applying:

| Axis | Host says (legacy) | RDAG says (this release) | Resolution |
|---|---|---|---|
| Decomposition driver | by Volatility (predicted change) | by Residue (what survives stressor contagion) | Supersede (host principle replaced) |
| Service naming | `Mgr*` / `Eng*` / `RA*` prefix | `*Manager` / `*Engine` / `*Access` suffix (Lowy) | Rename plan; old names deprecated, not silently repointed |
| Catalog shape | flat / unversioned | **versioned release directory** `architecture/arch-X.Y.Z/` (Current / Target / Superseded) | Migrate to the versioned layout; existing catalog becomes `arch-1.0.0` |
| Cross-service messaging | ad-hoc or stack-default | binding ADR (e.g. Dapr pub/sub) -- runtime claimed by architecture | Per Architecture Supremacy; plan conforms, doesn't re-decide |
| Authz / auth | ad-hoc or IdP-coupled | a residue (if Structural) traced to an `S-NN` | Audit; if Structural, lift into a catalog service; otherwise note as `U-NN` |

*(For this example -- ev-charging, scaffold mode -- the table is illustrative.
In a real insert/replace run S8 pre-skeletons it with the host's actual values
to confirm.)*

## What changes

| # | Change | Why |
|---|---|---|
| 1 | Replace the principle "Service Decomposition by **Volatility**" with "Service Decomposition by **Residue**" (drop-in block, `principle-decomposition-by-residue.md`). | The decomposition driver is the residue (what survives stressor contagion), not predicted volatility. Volatility was the IDesign lens, never the driver. |
| 2 | Naming convention: category **suffix** (`*Manager`/`*Engine`/`*Access`), Lowy. | Replaces any `Mgr*`/`Eng*`/`RA*` prefix convention. Existing services must be renamed (search-and-replace plan across catalog/use-case/spec docs; old names deprecated, not silently repointed). |
| 3 | Strengthen Constitution Check question 4: from "is the encapsulated volatility credible?" (judgment) to "does each service list a Structural `S-NN` in its Stressors-absorbed field?" (mechanical, self-contained). | The residue lineage makes the gate checkable instead of a review opinion. |
| 4 | Add Constitution Check question 5 (NFR records a `C-NN` Source) and question 6 (plan conforms to binding ADRs). | NFRs become grounded in a real coupling; runtime/protocol decisions become enforceable (Architecture Supremacy). |
| 5 | The gate resolves against the **Tier-1** artifacts (`service-catalog` with inline `S-NN`, `nfr-register` with `C-NN` Source, use-cases, binding ADRs). The full SAD evidence layer (stressor catalog, coupling map, criticality certificate) is published via **Backstage**, not shipped into the repo. | Keeps the consumer surface lean; the lineage resolves inline, the full analysis stays auditable on Backstage. |

## Ripple (consumer-side, to fix in the same change)

- Every doc citing "Principle ... (Service Decomposition by Volatility)" or
  "volatility encapsulated" -- the service catalog, use cases, already-generated
  specs -- updates to the residue framing.
- The `architecture/governance/constitution.md` publication mirror re-copies from
  the canonical in the same change (out-of-sync mirror is a review blocker).
- Service renames (change #2) propagate to any code/contract names the consumer
  derived from the old prefixed names.

## Conformance to verify after applying (CHK-01..05)

1. The principle block is present **verbatim** in `.specify/memory/constitution.md`
   (the file `/speckit-plan` reads).
2. The adopted RDAG version (0.1.0) is recorded.
3. Questions 4-6 are wired into the `/speckit-plan` gate and block on "no".
4. No implementation-half principle contradicts the architecture half.
5. The principle text contains zero concrete-technology terms.
