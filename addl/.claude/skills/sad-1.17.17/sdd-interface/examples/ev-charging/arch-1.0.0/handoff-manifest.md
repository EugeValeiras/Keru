# Handoff Manifest -- EV Charging Network

> Worked example exercising `../../../contracts/handoff-manifest-contract.md`. The
> first file a consumer reads: what was handed off, at what version, where each
> piece lands, and that the set is valid.

## Architecture Release

`arch 1.0.0` -- **Status: Current**. This handoff is the **immutable directory**
`architecture/arch-1.0.0/`. First release; **no migration in progress** (no
Target, no migration delta). When a future use case impacts the architecture,
the SAD is re-run and a new directory `architecture/arch-2.0.0/` is emitted as
`Target` with a `1.0.0 -> 2.0.0` delta; `arch-1.0.0/` stays Current and untouched
until a migration plan completes (rdag-standard sect.11).

## Release stamp

`arch 1.0.0` -- the single Architecture Release shared by every artifact below
(CHK-14). A citation always resolves "at the manifest-pinned version"; within
this stamp the set is frozen and coherent.

## Adopted RDAG version

`RDAG 0.1.0` (`../../../standard/`). Decomposition by Residue; Lowy suffix naming.

## Emission precondition

Criticality certificate verdict: **Ri = 0.67, Passing**; SAD assembled. The
handoff is authorized to emit (CHK-15). Were the verdict Failing or absent, this
set MUST NOT be consumed.

## Artifact inventory

| Artifact | Landing zone (consumer path) | Version |
|---|---|---|
| service-catalog | `architecture/arch-1.0.0/system-design/service-catalog.md` | arch 1.0.0 |
| nfr-register | `architecture/arch-1.0.0/system-design/nfr-register.md` | arch 1.0.0 |
| use-case UC-001 | `architecture/arch-1.0.0/use-cases/uc-001-charge-session.md` | arch 1.0.0 |
| use-case UC-002 | `architecture/arch-1.0.0/use-cases/uc-002-overstay-billing.md` | arch 1.0.0 |
| ADR-001 | `architecture/arch-1.0.0/decisions/ADR-001.md` | arch 1.0.0 |
| constitution principle | `.specify/memory/constitution.md` (insert/replace or scaffold) | RDAG 0.1.0 (doctrine version) |

The inventory is also the landing-zone map: a re-emission overwrites exactly
these files and nothing else.

> **Constitution principle -- special entry.** The architecture-half principle
> does not land under `architecture/`; it lands in the **canonical** constitution
> `.specify/memory/constitution.md` (what `/speckit-plan` reads). It is never
> overwritten -- it is applied at the gated integration step in `insert/replace`
> mode (existing constitution) or `scaffold` mode (greenfield). The emitted
> inputs for that step live in `integration/` (the drop-in block + the Sync
> Impact Report draft).

## SAD provenance (Tier 2 -- via Backstage, NOT in the handoff)

The SAD's evidence layer -- the full stressor catalog (`S-01..S-15`), coupling
map (`C-01..C-08`), and criticality certificate (Ri = 0.67, `U-01`) -- is **not**
emitted here. It is published with the full SAD via Backstage / TechDocs. Tier 1
carries the resolvable conclusions inline (catalog Stressors-absorbed `S-NN`;
nfr-register Source `C-NN`); this manifest's Ri attestation and the provenance
link point reviewers at the published SAD for the full analysis.

## Binding ADRs

| ADR | Claims | Constrains |
|---|---|---|
| ADR-001 | Inter-service invocation + pub/sub runtime (Dapr) | All Managers |

`/speckit-plan` question 6 enumerates binding ADRs from this list.

## Back-channels

| Trigger | Request | Goes to |
|---|---|---|
| Plan needs an absent service | Catalog amendment request | Architecture Team |
| Plan needs an unmade runtime/protocol decision | ADR request | Architecture Team |
| A new use case surfaces an unaccounted stressor (or relies on `U-01`) | Residue-analysis request (may open a new `S-NN`) | Architecture Team (next SAD iteration) |
