# NFR Register -- EV Charging Network

| | |
|---|---|
| **Architecture Release** | arch 1.0.0 (Status: Current; worked example) |
| **Owner** | Architecture Team |
| **Status** | Worked example -- emitted from `sad/examples/ev-charging-sad.md` §8 |

> Worked example exercising `../../../../contracts/nfr-register-contract.md`. Single
> home for all NFRs. Each carries its `C-NN` Source inline (the full coupling
> analysis is SAD-side, on Backstage) and an `Applies-to` scope. Use cases
> reference these by id.

## Purpose

The one definition site for every non-functional requirement. There is no inline
NFR anywhere else; normalization is structural.

## NFRs

| Id | Statement (technology-agnostic, measurable) | Applies-to | Source `C-NN` | Status |
|---|---|---|---|---|
| NFR-01 | A charge session completes (stop + unlock) atomically from the customer's perspective, even if the cloud fails mid-session. | UC-001 | C-01 | Active |
| NFR-02 | A charger can perform a local unlock using a cached, time-bounded credential when the cloud is unreachable for >= 60 s. | UC-001 | C-02 | Active |
| NFR-03 | The authentication mechanism is a runtime parameter: adding a new auth method requires no change in `BillingEngine`. | System | C-03 | Active |
| NFR-04 | Customer PII is partitioned by jurisdiction; no cross-border flow carries PII; `CustomerAccess` is bounded to the home-country instance. | System | C-04 | Active |
| NFR-05 | `ChargerAccess` abstracts connector type, voltage, and protocol; variations resolve internally without changing callers. | UC-001 | C-05 | Active |
| NFR-06 | Each hardware-facing ResourceAccess (`ChargerAccess`, `BatteryAccess`, `SensorAccess`) defines a degraded-mode contract usable when its Resource is impaired. | System | C-06 | Active |
| NFR-07 | `BillingEngine` pricing rules support non-charging revenue streams via configuration, with no code change. | System | C-07 | Active |
| NFR-08 | Customer-visible queue length is exposed as a metric to inform site-expansion decisions; the operational response is owned by the business. | System | C-08 | Active |

## Notes

- `Applies-to` mixes `System` (architectural invariants: NFR-03/04/06/07/08) and
  `UC-001`-scoped (session-specific: NFR-01/02/05). Only system-wide items are
  `System`; a UC-bounded item names its use case.
- Scope follows the reach of the inducing coupling: `C-03`'s auth/billing
  independence is structural across the system, so NFR-03 is `System`; `C-01`'s
  stop/unlock atomicity lives inside the charge session, so NFR-01 is `UC-001`.
- The seam: each statement says *what* and *how much*, never *how* (no "use a
  cache"). Where honoring a target demands an architectural decision (e.g. the
  Dapr Pub/Sub indirection behind several flows), that decision is `ADR-001` and
  binds per Architecture Supremacy.
