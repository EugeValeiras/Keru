---
title: Glossary -- Software Architecture Document meta-skill
version: 1.1
date: 2026-05-21
---

# Glossary

Vocabulary used throughout the meta-skill. Organized by lineage: IDesign (Lowy), Residuality (O'Reilly), Synthesis (this repo). Each term includes a citation to the source book or to the synthesis document.

When a term has different but compatible meanings in IDesign and Residuality, both definitions are listed under the term's primary lineage with a cross-reference.

---

## A. IDesign vocabulary (Lowy, *Righting Software*, 2019)

**Atomic business verb.** A lowest-level activity in the business that cannot be expressed by any other business activity (e.g., `Credit`, `Debit`, `StartCharge`, `Unlock`). Practically immutable because it relates to the nature of the business; appears only in ResourceAccess contract operations, never as a service name prefix. Cited Lowy L1055-1059. See R-07.

**Client.** Entry point to the system. May be a user-facing application or another system. Triggers Manager workflows. Cited Lowy L985-1003. See R-02.

**Closed architecture.** A layered architecture in which calls go top-down to the layer immediately below; no upward calls; no sideways calls within a layer. Trades flexibility for encapsulation. Cited Lowy L1281-1295. See R-03.

**Engine.** Stateless component that encapsulates the volatility of a business activity (rules, calculations, transformations, strategies). Prefix is a noun describing the activity, often a gerund (e.g., `AuthEngine`, `CalculatingEngine`). Engines do not call other Engines (R-03). Cited Lowy L1027, L1097, L1101. See R-02.

**ResourceAccess.** Stateless component that translates business operations (atomic business verbs) into operations against a Resource. Suffix is `Access`; prefix is a noun for the Resource or the data it provides (e.g., `CustomerAccess`, `ChargerAccess`). The only layer that touches Resources. Cited Lowy L1049-1063. See R-02.

**Resource.** Physical state holder or external system the architecture relies on (database, queue, file system, external API). Cited Lowy L1069-1071. See R-02.

**Manager.** Stateful (per workflow instance) component that orchestrates a use case workflow. Encapsulates the volatility of the sequence (the workflow), not the activity. Suffix is `Manager`; prefix is a noun for the volatility (e.g., `ChargeSessionManager`, `BillingManager`). Almost-expendable: orchestrates Engines and ResourceAccess, holds no business logic of its own (R-11). Cited Lowy L1027, L1093, L1163-1171. See R-02, R-11.

**Solutions masquerading as requirements.** A stakeholder-stated need that is actually one possible solution to an underlying volatility, framed as if it were the volatility itself (e.g., "we need a kitchen" instead of "we need to feed the occupants"). Encapsulating the masquerade couples the architecture to a specific solution. Cited Lowy L687-701. See R-10.

**Speculative design.** Adding components or abstractions to encapsulate volatilities that have no narrative basis in the analysis -- "designing for the future" without evidence. The SCUBA shoes example. Cited Lowy L815-823. See R-09.

**Utility.** Cross-cutting infrastructure component (security, logging, pub/sub, message bus, hosting, diagnostics) callable from any layer. Passes the cappuccino-machine litmus test: could plausibly be used in any other system. Cited Lowy L1073-1075, L1325-1327. See R-02, R-04.

**Workflow Manager.** A Manager that loads, executes, and persists workflows from an external workflow store, often using a third-party workflow execution tool. Mentioned in the TradeMe case study; the synthesis treats it as one of several Manager implementation patterns. Cited Lowy L2163-2186.

---

## B. Residuality vocabulary (O'Reilly, *Residues*, 2024)

**Architectural walking.** The cognitive practice by which an architect learns a complex domain: not by listing entities and defining their relations, but by walking around the problem repetitively and observing the differences each walk reveals. Drawn from Deleuze, *Difference and Repetition* (1968), via O'Reilly L1129-1278. Walks ARE stressors -- the walk is the perspective ("I am exploring the domain"); the stressor is the artifact ("here is the fact I generated"). The canonical reference is `shared/architectural-walking.md`. Mandatory reading before invoking any sub-skill of the meta-skill (R-22).

**Consistently wrong.** The mindset O'Reilly L1450-1452 names (literal): "Software architecture is the practice of being consistently wrong until you reach a point of being a little bit less wrong." A required mindset shift for developers trained in precision and exactness. The architect never claims complete understanding; updates structures as walks reveal differences; treats today's decomposition as a snapshot, not a truth. See `shared/architectural-walking.md` §5. Foundation for R-22.

**Difference and Repetition.** Gilles Deleuze, 1968. The philosophical anchor for architectural walking: knowledge of a complex thing emerges from repeated walks observing differences, not from definitions seeking identity. O'Reilly cites this work at L1183-1184 and L1209 as the foundation for the architectural walking concept. The meta-skill imports the Deleuzian framing without requiring the architect to read the source text -- the operational consequences are captured in `shared/architectural-walking.md`.

**Attractor.** A recurring state that a complex business system returns to despite countless individual variables. In residuality, each stressor pushes the system toward a (possibly new) attractor; the architecture's job is to survive in those attractors. Cited O'Reilly L778-805.

**Contagion matrix.** A matrix with stressors as rows and components as columns; cell `(i, j) = 1` if stressor `i` affects component `j`, `0` otherwise. The diagnostic instrument of residuality: surfaces hyperliminal coupling, hot rows (high-impact stressors), hot columns (over-loaded components), identical signatures (merge candidates), and overall topology of stress propagation. See `template.md` §Contagion Matrix; cited O'Reilly L1886-1957.

**Criticality.** The Kauffman-network state where N (component count), K (link count), and P (component bias toward predictable behavior) are balanced such that the system survives unknown stress without being so connected that managing dependencies overwhelms it. The architectural goal in residuality. Distinct from correctness. Cited O'Reilly L807-867. See R-21.

**Ergodicity.** The property of a system whose future is already expressed in its past behavior. Software systems are mostly ergodic; the human / business systems they execute inside are not. Assuming ergodicity in a non-ergodic context is a common architectural mistake. Cited O'Reilly L414-432.

**Lateral thinker.** An architect whose primary cognitive mode is exploration, imagination, and comfort with being wrong. The lateral thinker asks "what could break this structure?" rather than "what is the correct structure?". Treats anomalies as evidence the abstraction is wrong rather than as edge cases to patch. Per O'Reilly L1378-1470, the senior architect gap is the gap between linear and lateral thinking. Per L1427-1428 (literal): "for the mythical 10X developer, 9X is lateral thinking." Per L1431-1432: lateral thinking without linear thinking cannot produce good architecture (the rule). Required mindset codified as R-22. See `shared/architectural-walking.md` §4.

**Linear thinker.** An architect (typically a senior developer transitioning to architecture) whose primary cognitive mode is precision, definition-fixation, and demand for correctness at every step. Excellent for programming; insufficient for architecture in complex contexts. The linear thinker treats refusal conditions as checklists, defends abstractions against stressor evidence, and asks for "the correct decomposition" instead of "what could break this decomposition". Cited O'Reilly L1378-1470. See `shared/architectural-walking.md` §4. Linear thinking remains necessary as scaffolding under lateral dominance (R-22).

**Hyperliminality.** The condition of a complicated, ergodic, ordered system (the software) executing inside a complex, non-ergodic, disordered context (the business). Software architecture is the engineering of hyperliminal systems. Cited O'Reilly L443-455, L499-503.

**Hyperliminal coupling.** Implicit coupling between components, revealed only when both react to the same stressor. Two components affected by stressor `S` are coupled even if no functional dependency in code connects them. Surfaced by the contagion matrix as two `1`s in the same row. Cited O'Reilly L1082-1111, L1934-1937. See R-14 (override does NOT apply to hyperliminal coupling readings, only to merge proposals).

**Looping.** When new stressors added during analysis are increasingly survived by combinations of existing residues -- the empirical signature of approaching criticality. Cited O'Reilly L1812-1816. See R-17.

**Mathematical leverage.** The reason residuality works: the number of potential stressors is orders of magnitude greater than the number of attractors. A residue designed for one stressor protects against all stressors that push the system toward the same attractor, including unknown future ones. Cited O'Reilly L1068-1078, L1819-1840.

**Naïve architecture.** The minimal architecture that solves the problem as stated, with no consideration of stress or change. The control against which the residual architecture is measured in the empirical Ri test. Cited O'Reilly L893-915.

**N, K, P.** The three Kauffman parameters governing attractor count in a Random Boolean Network. N = number of nodes (components). K = number of links between them. P = bias: each node's tendency to behave predictably in response to inputs. SOLID, DRY, OOP, IDesign call rules all set N and K topology and raise P. Cited O'Reilly L737-846. See `kauffman-nkp.md`.

**Random simulation.** The act of generating diverse, unfiltered stressors to expose the structure of the business context that traditional analysis misses. Probability and cost are explicitly excluded during simulation; they enter later in FMEA / ATAM. Cited O'Reilly L634-734, L1763-1768. See R-20.

**Residual architecture.** The integration of the naïve architecture with all residues identified through stressor analysis. The output of the meta-skill, expressed as a SAD per `template.md`.

**Residue.** What is left of an architecture after exposure to a stressor; the unit of architectural change in residuality. Each residue describes the changes necessary to the naïve architecture so that it would survive in the attractor the stressor induces. Cited O'Reilly L406-413, L915-1061.

**Residual Index (Ri).** Empirical metric `Ri = (Y - X) / S`, where X is the count of test stressors survived by the naïve architecture, Y by the residual architecture, S the test set size, `-1 <= Ri <= 1`. Ri > 0 indicates positive movement toward criticality. Cited O'Reilly L2014-2018, L2036-2040 (train/test analogy with ML). See `template.md` §Empirical Test.

**Stressor.** Any fact about the context that is currently unknown to or unaccounted for in the naïve architecture. May be technical, organizational, market, regulatory, environmental. Probability is not part of the definition. Cited O'Reilly L1472-1502, L1763-1768.

**Train / test split.** The empirical Ri test uses two disjoint stressor sets: the training set (used during design to drive residue identification) and the test set (used after design to compute Ri). Borrowed from machine learning. Cited O'Reilly L2036-2040. See R-15 (Empirical Test source row).

---

## C. Synthesis vocabulary (this repo, 2026-05-09)

**Boundary stressing.** The sixth stressor-generation lens (S3): stresses co-location decisions -- what would force components to run as separate deployable units? Discovers operational Topological residues (R-19). Under R-25's actor-style default (one Manager = one service), it focuses on the cases the default leaves open: whether a shared Engine/RA (used by 2+ Managers) should be promoted to its own service, and the rare co-location of two Managers. See `shared/stressor-frameworks.md` §6.

**Business residue.** A residue that produces a business decision but no software change. Recorded in the `Business Residues Log` of the SAD as a decision-of-record. Examples in EV charging: market crash (#4), competitor pricing (#6, #7, #11), capacity / queueing (#5). Synthesis decision 2; see R-13.

**Combined residue.** A stressor already survived by a combination of existing residues. No new component or deployment unit. Recorded in the `Looping Signals` table with explicit "survived by combination of #X, #Y, #Z" trace. Examples in EV charging: ICE-ing (#14), AFIR (#15). Synthesis decision 6; see R-13, R-17.

**Decomposition discipline.** The eight guardrail rules in `template.md` §Restrictions §Decomposition Discipline. Mapped to constitution rules R-13 through R-20. Synthesis decision 7.

**Doubly-justified component (deprecated).** Term used in the prior federation for a component that appeared in both volatility analysis and residuality analysis. Replaced by the cleaner approach of typed residues (R-13) plus residue-component traceability (R-18). Term not used in the current synthesis.

**Fragment.** The output of one of the seven sequential sub-skills (S1-S7). A markdown file that fills one or more sections of the SAD template. Fragments are reviewed and approved individually before being integrated by `sad-assembler` (S7) into the final SAD. See `FLOW.md`.

**IDesign override.** The principle by which IDesign layer discipline (stateless / stateful, call rules, R-02 typing) overrides residuality merge signals based on contagion matrix similarity. Cross-layer pairs (Manager + Engine, ResourceAccess + Resource, etc.) are never merged on signature similarity alone, even if their column signatures are identical. Synthesis decision 3; see R-14.

**NFR traceability sources.** The three valid sources for any non-functional requirement in the SAD: (a) a specific cell of the Contagion Matrix, (b) a specific row of the Topological Residue Map, (c) a specific Business Residue. NFRs without a Source column populated to one of these are rejected. Synthesis decision 4; see R-15.

**Operational Topological residue.** A Topological residue whose driver is operational rather than geographic: `independent-scaling`, `failure-isolation` (blast-radius), `change-cadence`, `resource-profile`, or `security-zone`. Under R-25, it promotes a shared Engine/RA (used by 2+ Managers) to its own service, or justifies a rare Manager co-location -- it does NOT drive per-Manager splits (those are the actor-style default). Generated by boundary stressing (S3); consumed by the Service Grouping Map (S4). See R-19, R-25.

**SAD (Software Architecture Document).** The single integrated markdown output of the meta-skill, conforming to `sad/template.md`. Produced by `sad-assembler` (S7) by integrating six approved fragments. The auditor (`sad-auditor`) validates the SAD end-to-end against constitution rules and the eight guardrails.

**Service Grouping Map.** The S4 sub-table mapping IDesign components to separately deployable units (services / containers). Actor-style default (R-25): one Manager per service, with its private Engines/RAs co-located inside it (O'Reilly L1940-1943 "same profile -> combine", applied within the Manager cluster). Shared Engines/RAs become their own service only when promoted by an operational Topological residue. Consumed by the §C4 Model container view (S5), one `container` per row. Synthesis (2026-05-21); see R-25.

**Structural residue.** A residue that drives a change in IDesign components or call topology. Enters the Contagion Matrix. Examples in EV charging: new car models (#1), failed login (#3), server failure (#9). Synthesis decision 2; see R-13, R-18.

**Topological residue.** A residue that drives a change in deployment topology. Two families (R-19): **geographic / jurisdictional** (geography, tenancy, replication, latency zones, sovereignty -- *where* a unit runs) and **operational** (independent-scaling, failure-isolation, change-cadence, resource-profile, security-zone -- *which components run as a separate process*; see Operational Topological residue). Enters the Topological Residue Map. May also have component impact and additionally appear in the Contagion Matrix marked `(T)`. Examples in EV charging: privacy regulation (#13, geographic). Synthesis decision 2; see R-13, R-19, R-25.

**Typed residue.** A stressor catalog entry with a `Type` column populated as one of: `Structural`, `Topological`, `Business`, `Combined`. Typing is mandatory and drives downstream routing into the four catalog sub-sections. Synthesis decision 2; see R-13.

**Unstressed surface.** A test stressor that the residual architecture failed to survive during the empirical Ri test. Marks the next round of stress analysis -- where the architecture is still vulnerable. Recorded in the Empirical Test section. See `template.md` §Empirical Test.

---

## Cross-reference index

| Term | Lineage | Constitution rule |
|---|---|---|
| Architectural walking | Residuality | R-22 |
| Atomic business verb | IDesign | R-07 |
| Attractor | Residuality | R-01 (residue framing), R-21 |
| Boundary stressing | Synthesis | R-19, R-25 |
| Consistently wrong | Residuality | R-22 |
| Difference and Repetition | Residuality | R-22 (philosophical anchor) |
| Lateral thinker | Residuality | R-22 |
| Linear thinker | Residuality | R-22 |
| Closed architecture | IDesign | R-03 |
| Combined residue | Synthesis | R-13, R-17 |
| Contagion matrix | Residuality | R-13, R-14, R-15 |
| Criticality | Residuality | R-21 |
| Engine | IDesign | R-02 |
| Fragment | Synthesis | (workflow concept; see FLOW.md) |
| Hyperliminal coupling | Residuality | R-14 (override does NOT eliminate) |
| IDesign override | Synthesis | R-14 |
| Looping | Residuality | R-17 |
| Manager | IDesign | R-02, R-11 |
| Mathematical leverage | Residuality | R-01, R-21 |
| Naïve architecture | Residuality | (input to R-18 chain) |
| N, K, P | Residuality | R-12, R-21 |
| NFR traceability sources | Synthesis | R-15 |
| Operational Topological residue | Synthesis | R-19, R-25 |
| Random simulation | Residuality | R-20 |
| Residue | Residuality | R-01 |
| Residual Index (Ri) | Residuality | R-21 (Empirical Test) |
| ResourceAccess | IDesign | R-02 |
| Resource | IDesign | R-02 |
| SAD | Synthesis | (output of meta-skill) |
| Service Grouping Map | Synthesis | R-25 |
| Solutions masquerading | IDesign | R-10 |
| Speculative design | IDesign | R-09 |
| Stressor | Residuality | R-13, R-20 |
| Structural residue | Synthesis | R-13, R-18 |
| Topological residue | Synthesis | R-13, R-19, R-25 |
| Train / test split | Residuality | R-15 (Empirical Test) |
| Typed residue | Synthesis | R-13 |
| Unstressed surface | Synthesis | (Empirical Test output) |
| Utility | IDesign | R-02, R-04 |
| Workflow Manager | IDesign | (pattern under R-02) |
