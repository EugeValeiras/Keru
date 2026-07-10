---
title: Decomposition discipline -- the eight guardrail rules
version: 1.0
date: 2026-05-10
---

# Decomposition Discipline

Working reference for the eight guardrail rules that enforce the IDesign + Residuality synthesis. The rules originate in `sad/template.md` §Restrictions §Decomposition Discipline; they are mapped to constitution rules R-13 through R-20 in `shared/constitution.md`. This document expands each rule with EV charging worked examples so that the auditor (`sad-auditor`) and any sub-skill that produces a fragment can recognize compliance and violations on sight.

The eight rules translate the seven synthesis decisions of `sad/synthesis-explanation.md` §6 into hard constraints on the SAD output.

---

## How the rules relate

| Guardrail | Constitution rule | Synthesis decision | Mechanism |
|---|---|---|---|
| #1 No new structural component without a Structural residue | R-18 | 7 (discipline as guardrails) | deterministic |
| #2 No new deployment unit without a Topological residue | R-19 | 7 | deterministic |
| #3 No undocumented business decision affecting architectural reasoning | R-13 (typing routes business decisions to the Business Residues Log) | 2 (typed residues) + 7 | deterministic + heuristic |
| #4 No NFR without traceability to matrix cell, topology row, or business residue | R-15 | 4 (NFR traceability) | deterministic |
| #5 No use case is the source of a decomposition decision | R-16 | 5 (use cases document, not drive) | heuristic |
| #6 No probability or cost discussion until the matrix is complete | R-20 | 7 | deterministic |
| #7 Manager-Engine pairs are not merged based on matrix similarity alone | R-14 | 3 (IDesign override) | deterministic |
| #8 Combined residues are recorded, not discarded | R-17 | 6 (looping signals formalized) | deterministic + heuristic |

The auditor enforces each guardrail at the gate where its inputs are all available:

- #1, #4, #7 -- enforced at gate G5 (after `residual-design` produces the Static Architecture and NFRs).
- #2 -- enforced at gate G4 (after `contagion-analysis` produces the Topological Residue Map).
- #3, #6, #8 -- enforced at gate G4.
- #5 -- enforced at gate G5 (when use cases enter the SAD as documentation).
- All -- re-checked at gate G7 (end-to-end audit of the assembled SAD).

---

## Guardrail #1 -- No new structural component without a Structural residue

**Rule.** Every component appearing in the Static Architecture must trace to one or more `Structural` residues in the Stressor Catalog.

**Constitution mapping.** R-18.

**Why it matters.** Components added "just in case" are speculative design (R-09). Components added because the team finds them familiar from past projects are pattern-driven, not residue-driven. The rule forces every component to be empirically motivated by a stressor that the team has explicitly written down.

**Detection.** For each row of the Static Architecture component taxonomy table, look up the column with the same name in the Contagion Matrix. If the column does not exist, or all cells in the column are `0`, the rule is violated.

**Valid example -- EV charging.**

`OverstayManager` exists. Looking at the Contagion Matrix, the `OverstayMgr` column has value `1` for stressor #12 (customer abandons car in slot). Stressor #12 is `Structural`. Therefore the component is justified. Compliant.

**Anti-example -- EV charging.**

Suppose someone adds `LoyaltyManager` to the Static Architecture because "we'll probably want a loyalty program someday". The Stressor Catalog has no entry mentioning loyalty. The Contagion Matrix has no `LoyaltyMgr` column. Guardrail #1 fires. The architect must either: (a) add the corresponding Structural residue to the Stressor Catalog with attractor and business reaction, or (b) remove the component.

**Auditor action.** Cross-reference Static Architecture component table against Contagion Matrix columns. Report each unmatched component as a violation with proposed fix: "Add Structural residue X to the catalog OR remove component Y from the Static Architecture."

---

## Guardrail #2 -- No new deployment unit without a Topological residue

**Rule.** Every deployment unit boundary in the Deployment Diagram must trace to one or more `Topological` residues in the Topological Residue Map.

**Constitution mapping.** R-19.

**Why it matters.** Deployment topology has cost. Each boundary (region, tenancy partition, replication zone, latency zone) means infrastructure, network configuration, deployment orchestration, monitoring, and cross-boundary contract enforcement. Without a Topological residue justifying the boundary, the cost is incurred without a reason traceable to stress.

**Detection.** For each deployment unit boundary in the Deployment Diagram, check the Deployment Unit Boundaries table for a `Topological Residue #` reference. The reference must resolve to an existing row in the Topological Residue Map.

**Valid example -- EV charging.**

The Deployment Diagram shows a per-country deployment boundary (each country runs its own data plane). The Deployment Unit Boundaries table shows: `Boundary: Per-country | Topological Residue #: 13`. The Topological Residue Map row 13 is the privacy regulation residue (customer PII must remain in-country). Compliant.

**Anti-example -- EV charging.**

Suppose someone splits the deployment into "US-East" and "US-West" "for performance". The Topological Residue Map has no row for latency-driven partitioning. Guardrail #2 fires. The architect must either: (a) add a Topological residue justifying the latency-driven split (e.g., a stressor about charge-event ingestion latency with a clear attractor), or (b) collapse the deployment back into one US region.

**Auditor action.** Cross-reference Deployment Unit Boundaries table against Topological Residue Map. Report each unmatched boundary as a violation.

---

## Guardrail #3 -- No undocumented business decision affecting architectural reasoning

**Rule.** Any business decision that influences the architectural reasoning of the SAD must be recorded as a `Business` residue in the Business Residues Log, with its rationale.

**Constitution mapping.** R-13 (typing forces business decisions into the log).

**Why it matters.** Architectures fail when decisions are made silently and then forgotten. "We don't need multi-tenancy because we agreed not to expand to enterprise customers" is a decision that, once forgotten, looks like an architecture flaw rather than a business choice. The Business Residues Log captures these decisions-of-record so a future architect understands *why the system does not solve a problem it could have solved*.

**Detection.** Heuristic. For each topic discussed in stakeholder workshops or design reviews that did NOT produce a Structural or Topological residue, ask: was a business decision made? If yes, is it recorded in the Business Residues Log?

**Valid example -- EV charging.**

Stressor #4 (EV market crashes) was discussed. The business decision was: "if the market dies, we pivot the real-estate to petrol stations". The Business Residues Log has row 4 with stressor, attractor (business no longer viable as EV charging), business decision (pivot real-estate to petrol stations), and rationale (no platform change can save a dead market). Compliant.

**Anti-example -- EV charging.**

Suppose stressor #4 is discussed, the team agrees "no change needed", and the discussion ends. Six months later, an executive asks "did we consider what happens if EV demand collapses?" -- there is no record. Guardrail #3 fires retroactively (and would have fired during audit). The architect must add the Business Residues Log entry.

**Auditor action.** Heuristic. Compare the Stressor Catalog `Business` count to the Business Residues Log row count -- they must match. Report mismatch as a violation requiring sync.

---

## Guardrail #4 -- No NFR without traceability to matrix cell, topology row, or business residue

**Rule.** Every non-functional requirement in the SAD has a `Source` column populated with a reference to one of: a specific cell of the Contagion Matrix, a specific row of the Topological Residue Map, or a specific Business Residue. NFRs without a Source are rejected.

**Constitution mapping.** R-15.

**Why it matters.** Generic NFRs ("the system must be highly available", "performance must be acceptable") are unfalsifiable, untestable boilerplate. The rule forces every NFR to be empirically derived from the stressor analysis. The three valid sources correspond to the three places stress reveals NFR needs.

**Detection.** For each row in the Derived NFRs section and in each per-use-case NFR table, the `Source` column must be non-empty AND the Source reference must resolve to a real artifact (existing cell, existing topology row, existing business residue number).

**Valid example -- EV charging.**

NFR "Resumable charge session" has `Source: Matrix row 9b (CSM / CA.Stop / CA.Unlock)`. The reference resolves: row 9b exists in the matrix; the cells at the named columns are populated. Compliant.

NFR "Per-country data residency" has `Source: Topology row 13`. Row 13 exists in the Topological Residue Map. Compliant.

NFR "Operational diversification readiness" has `Source: Business residue #6`. Business residue #6 exists in the Business Residues Log. Compliant.

**Anti-example -- EV charging.**

NFR "The system must be highly available 24/7". Source column empty. Guardrail #4 fires. The architect must either: (a) trace the NFR to a specific source (e.g., matrix row 9 across CSM / CA.Unlock cells, which establishes the offline-unlock authority NFR), or (b) drop the NFR as boilerplate.

**Auditor action.** Schema check on Source column. Cross-reference resolution check. Report each empty or unresolvable Source as a violation.

---

## Guardrail #5 -- No use case is the source of a decomposition decision

**Rule.** Use cases describe the behavior of the residual architecture after it has been decomposed via stressor analysis. Use cases never appear as the justification for adding, splitting, or merging components.

**Constitution mapping.** R-16.

**Why it matters.** Use-case-driven decomposition is functional decomposition disguised. Each use case becomes a Manager (or worse, a service); the architecture fragments as new use cases arrive. Residue-driven decomposition produces components that survive use-case change.

**Detection.** Heuristic. Look for: components named for use cases (`AddCustomerManager`, `ProcessOrderManager`, `ChargeCarManager`); use cases predating the Stressor Catalog in document chronology; Residue Mapping subsections empty or missing per use case; component additions justified in design notes by reference to a use case rather than a residue.

**Valid example -- EV charging.**

Use Case "Customer charges car" appears in §Behavioral Diagrams of the SAD. Its Residue Mapping subsection traces the use case to residues #3 (auth path), #9 (resumable session), #12 (overstay billing), #13 (per-country data). The components participating in this use case (`ChargeSessionManager`, `AuthEngine`, `ChargerAccess`, etc.) all have prior justification through Structural residues. Compliant.

**Anti-example.**

Suppose the Static Architecture lists `ChargeCarManager`, `RegisterCustomerManager`, `BillCustomerManager`, `HandleDamageManager` -- one Manager per major use case. Guardrail #5 fires. This is functional decomposition; each component is named for what it does, not for the volatility it encapsulates. The residual architecture would have `ChargeSessionManager`, `MembershipManager`, `BillingManager`, `LegalCaseManager` (or similar), each justified by Structural residues.

**Auditor action.** Heuristic. Sample component names against use case names and flag overlaps. Sample Residue Mapping subsections per use case and flag missing or empty sections. Report each overlap as a violation requiring rename + traceability check.

---

## Guardrail #6 -- No probability or cost discussion until the matrix is complete

**Rule.** No column or annotation for `Probability`, `Likelihood`, `Risk Score`, `Cost`, `Complexity`, `Effort`, or equivalent appears in the Stressor Catalog or the Contagion Matrix at any point before the matrix is complete and the Empirical Test is run.

**Constitution mapping.** R-20.

**Why it matters.** Probability and cost filter the catalog and bias the matrix toward consensus and "likely" scenarios. Three of the most valuable EV charging residues (#3 broken key fob, #13 privacy regulation, #15 AFIR ten years later) would have been filtered out by a probability column. O'Reilly L1763-1768 is explicit: "No use of probability. All stressors must go in the list, no matter how ridiculous."

Probability and cost re-enter later, in FMEA / ATAM (O'Reilly L1958-2000), once the structural analysis is complete.

**Detection.** Schema check on Stressor Catalog and Contagion Matrix column headers. Regex on forbidden terms (case-insensitive): probability, likelihood, risk, cost, complexity, effort, priority.

**Valid example -- EV charging.**

The Stressor Catalog has columns: `#`, `Type`, `Stressor`, `Detection`, `Attractor`, `Business Reaction`, `Technical Change to Residue (IDesign)`. No probability, no cost. Compliant.

**Anti-example.**

A Stressor Catalog with columns including `Likelihood (1-5)` and entries marked `Likelihood ≤ 2` filtered out before the matrix is built. Guardrail #6 fires. The architect must remove the column and re-include any filtered entries.

**Auditor action.** Schema check on column headers. Report any forbidden column as a violation.

---

## Guardrail #7 -- Manager-Engine pairs (and other cross-layer pairs) are not merged based on matrix similarity alone

**Rule.** Two components proposed for merge based on identical or similar Contagion Matrix column signatures may be merged only if both belong to the same IDesign layer. Cross-layer merges are forbidden regardless of matrix signature.

**Constitution mapping.** R-14.

**Why it matters.** The matrix's "identical signatures" pattern is a useful merge signal within a layer. Across layers it is a false positive: a Manager and its dedicated Engine often have similar signatures because they participate in the same use cases, but they are structurally distinct by IDesign discipline (stateful workflow vs stateless logic). Merging would collapse R-02 typing.

**Detection.** Inspect each merge proposal in the Contagion Matrix reading sections. For each proposed merge, check the layers of the proposed components.

**Valid example -- EV charging.**

In the EV charging Contagion Matrix, `BillingMgr` and `BillingEngine` both have Σ = 4 with similar response patterns. The matrix-reading section flags them as merge candidates. Guardrail #7 fires: cross-layer pair (Manager + Engine). The matrix reading explicitly applies the IDesign Override: "These are not merged. Manager-Engine pairs that co-evolve are structurally separate by IDesign discipline." Compliant.

**Anti-example.**

A SAD that merges `BillingMgr` and `BillingEngine` into `BillingService`. The merged component is a stateful + stateless hybrid that breaks R-02 (no longer cleanly typed) and R-11 (almost-expendable Manager). Guardrail #7 fires.

**Auditor action.** For every merge proposal in matrix reading text or change list, check IDesign layers of the proposed pair. Report any cross-layer merge as a violation.

---

## Guardrail #8 -- Combined residues are recorded, not discarded

**Rule.** When a new stressor is discovered to be already survived by a combination of existing residues, it is typed `Combined` in the Stressor Catalog AND recorded in the Looping Signals table with explicit `Survived by Combination of #X, #Y, #Z` trace.

**Constitution mapping.** R-17.

**Why it matters.** Looping is the empirical signature of approaching criticality (O'Reilly L1812-1816). Combined residues are the strongest persuasive material in the SAD -- they are the moments the architecture absorbs an unforeseen stressor for free. The book treats them as narrative observation; the synthesis treats them as structured artifacts so the persuasive value is captured and reusable.

**Detection.** Schema: every `Combined`-typed stressor in the catalog has a corresponding row in the Looping Signals table. The row's `Survived by Combination of` column is non-empty and references valid residue numbers.

**Valid example -- EV charging.**

Stressor #14 (ICE-ing -- fossil-fuel cars deliberately blocking chargers) is added to the Stressor Catalog as `Combined`. The Looping Signals table row 14 records: `Survived by Combination of: #3 (ALPR captures plate), #8 (cameras provide evidence), #12 (per-minute billing applies regardless of vehicle type)`. Notes column explains: "Anti-social behavior becomes a revenue line." Compliant.

Stressor #15 (AFIR 2023 EU regulation) is also `Combined`, survived by combination of #3 alone (the auth/billing decoupling already in place from the broken key-fob residue ten years earlier). Compliant.

**Anti-example.**

A SAD where stressor #15 is mentioned only in a closing prose paragraph: "Conveniently, our architecture survived AFIR." No Looping Signals row, no trace, no reusable evidence. Guardrail #8 fires. The architect must add the Looping Signals row with the explicit combination trace.

**Auditor action.** Schema check: `Combined`-typed stressors in catalog vs Looping Signals table rows. Report mismatches and missing trace columns as violations.

---

## Cross-references

- `shared/constitution.md` -- canonical rule statements R-13, R-14, R-15, R-16, R-17, R-18, R-19, R-20.
- `shared/idesign-vocabulary.md` -- IDesign taxonomy and call rules; the IDesign override (R-14 / Guardrail #7) is expanded there with cross-layer merge anti-patterns.
- `shared/glossary.md` -- single-line definitions of each term used here.
- `sad/synthesis-explanation.md` §6 -- the seven synthesis decisions that motivate these guardrails.
- `sad/template.md` §Restrictions §Decomposition Discipline -- the canonical statement of all eight rules.
- `sad/examples/ev-charging-sad.md` -- worked example illustrating each guardrail in practice.
