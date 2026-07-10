---
title: "RDAG Contract -- handoff-manifest.md"
version: 0.1.0
date: 2026-05-26
status: Draft (Phase 0b)
---

# RDAG Contract -- `handoff-manifest.md`

The handoff manifest is the **coherence anchor** of a handoff. The emitted
artifacts are not independent -- the catalog cites `S-NN` from the stressor
catalog, use cases cite `NFR-NN` from the register, the certificate attests a
catalog version. The manifest pins them all to **one release stamp** so every
cross-reference resolves within a mutually consistent set (CHK-14). It is the
first file a consumer reads: it says what was handed off, at what version, where
each piece lands, and that the set is valid. Ids in
`../standard/rdag-id-scheme.md`.

**Emitted from:** SAD assembly (S7) plus the S6 verdict, aggregating every
artifact. **Landing zone:** the root of the release directory it versions
(`architecture/arch-X.Y.Z/handoff-manifest.md`) -- the entry point for that
release.

## 1. File schema

```text
# Handoff Manifest
## Architecture Release  -- semver `arch vX.Y.Z`; this release's status (Current / Target)
## Release stamp         -- the one version shared by all artifacts in this handoff
## Adopted RDAG version  -- the standard version this handoff conforms to
## Emission precondition -- the Ri verdict attestation (CHK-15)
## Artifact inventory    -- each artifact: landing zone, version/checksum
## Migration delta       -- changes vs the prior release (added/deprecated/superseded)
## Binding ADRs          -- the list the gate enumerates (CHK-12)
## Back-channels         -- where amendment / ADR / migration requests go
```

## 1a. Architecture Release and migration (rdag-standard sect.11)

The manifest is where a handoff declares **which Architecture Release** it is and
how it relates to the consumer's current one:

- **Architecture Release** -- the semver `arch vX.Y.Z` this handoff publishes. A
  release is immutable; a re-run that changes the architecture is a **new**
  release, not an overwrite.
- **Status** -- what the consumer's governed amendment should set this release
  to: `Current` (first release, or the post-migration promotion) or `Target`
  (introduced alongside an existing `Current`, opening a migration).
- **Migration delta** -- when this release supersedes a prior one, the manifest
  lists what changed (`Added` / `Deprecated` / `Superseded` services, new NFRs,
  new / superseded ADRs). This delta is the input a spec-kit **migration plan**
  consumes to move from `Current` to `Target`. The current and target releases
  **coexist** until the migration plan completes (append-only ids make this
  safe); then the amendment promotes `Target -> Current` and marks the prior
  `Superseded` (retained, not deleted).

## 2. Release stamp -- why one version, not seven

If each artifact versioned independently, a spec could cite `service-catalog
v3` whose `NFR-03` points at an `nfr-register v2` where `NFR-03` means something
else -- a silent broken trace. The release stamp is a **single version applied
to the whole set**: all artifacts in one handoff carry it, and a citation always
resolves "at the manifest-pinned version" (`../standard/rdag-id-scheme.md` §4).
A new handoff is a new stamp; within a stamp, the set is frozen and coherent.

## 3. Artifact inventory

One row per emitted artifact:

| Field | Meaning |
|---|---|
| **Artifact** | The **Tier-1** set only: `service-catalog`, `nfr-register`, `use-case (UC-NNN)`, `ADR-NNN`, and the **constitution principle** (the architecture half). The SAD's evidence layer (stressor catalog, coupling map, criticality certificate) is NOT in the handoff -- it is published via Backstage (see below). |
| **Landing zone** | The exact path in the consumer repo this artifact lands at. |
| **Apply mode** | `overwrite` for the artifacts under `architecture/`; `insert/replace` or `scaffold` for the constitution principle (see below). |
| **Version / checksum** | The release stamp (and optionally a content checksum) so drift is detectable. |

The inventory is also the **landing-zone map**: it is where the producer
declares, per artifact, the consumer path -- the seam's "where does this go"
made explicit so a re-emission overwrites the right files and nothing else.

### The constitution principle is a special inventory entry

The architecture-half principle does **not** land under `architecture/`. Its
landing zone is the consumer's **canonical** constitution,
`.specify/memory/constitution.md` -- the file `/speckit-plan` actually reads
(CHK-01), not the `architecture/governance/` publication mirror. It is never
overwritten; it is applied at the gated integration step in one of two modes:

- **insert/replace** -- the consumer already has a constitution: the
  architecture-half principle is swapped in (replacing any prior "by Volatility"
  principle), the implementation-half principles are left untouched.
- **scaffold** -- the consumer is greenfield: a full constitution is created with
  the architecture half complete and the implementation-half principles as
  labeled stubs.

The manifest records which mode applies, so the integration step knows whether
it is editing an existing constitution or scaffolding a new one.

## 4. Emission precondition attestation

The manifest restates the SAD's Ri verdict (from S6): a handoff is emitted only
from a SAD whose Ri is `Passing` and whose S7 assembly is complete (CHK-15). A
manifest with a `Failing` or absent verdict is not a valid handoff; the set MUST
NOT be consumed. The manifest also carries a **provenance pointer** to the full
SAD (e.g. its Backstage / TechDocs location), where the evidence layer (stressor
catalog, coupling map, criticality certificate) lives -- referenced for audit,
not shipped in the handoff.

## 5. Binding ADRs

The manifest lists every `ADR-NNN` with `Binding: Yes`, so `/speckit-plan`
question 6 enumerates binding ADRs from one place instead of scanning the ADR
folder (`adr-contract.md` §6). A binding ADR missing from this list is a
contract violation (CHK-12).

## 6. Back-channels

The manifest names where the two upstream requests go (`../standard/rdag-standard.md`
§6): the **catalog amendment request** (a plan needs an absent service) and the
**ADR request** (a plan needs an unmade runtime/protocol decision). This makes
the architecture/feature boundary actionable, not just stated.

## 7. Field-by-field mapping (SAD -> manifest)

| Section | SAD source | Rule |
|---|---|---|
| Release stamp | assigned at emission (S7/S8) | One stamp per handoff; monotonic. |
| Adopted RDAG version | the `../standard/` version emitted against | Recorded for CHK-02. |
| Emission precondition | the S6 Ri verdict | Must be `Passing`. |
| Artifact inventory | the set of emitted artifacts | One row each; landing zones from the consumer's constitution. |
| Binding ADRs | the ADRs with `Binding: Yes` | Enumerate all. |
| Back-channels | the consumer's amendment / ADR request paths | From the integration setup. |

## 8. Conformance

Checked by: **CHK-14** (one coherent stamp across all artifacts), **CHK-15**
(emission precondition), **CHK-12** (binding ADRs enumerated), **CHK-11**
(landing-zone paths and cited ids resolve). See `../standard/rdag-conformance.md`.

## 9. Related files

- `../standard/rdag-standard.md` -- the back-channels (§6) and the gate.
- `../standard/rdag-id-scheme.md` -- "the pinned version" the stamp defines (§4).
- every `contracts/*` artifact -- the inventory references them all.
