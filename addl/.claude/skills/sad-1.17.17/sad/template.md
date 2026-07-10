# [MKT] Architecture Engineering Template -- Residual + IDesign Fusion (v2)

> **Working in progress -- v2**
> Author: Arturo (DEV-Team). Content may change without notice.
> Based on: Analysis & Design Engineering Template + Residuality Theory (O'Reilly, 2024) + IDesign Method (Lowy, 2019)

> **Changes from v1** (driven by the EV charging worked example):
> 1. Stressors are now **typed** -- Structural / Topological / Business / Combined.
> 2. New subsection **Topological Residue Map** for deployment-level residues that don't fit IDesign component decomposition.
> 3. New subsection **Business Residues Log** for stressors that produce a business decision but no software change.
> 4. New subsection **Looping Signals (Combined Residues)** to formally record the criticality-emergence pattern.
> 5. New methodological note in *Contagion Matrix*: **IDesign discipline overrides matrix-driven merge signals** when the candidate components belong to different IDesign layers (Manager--Engine pairs are not merged on signature similarity alone).
> 6. *Decomposition Discipline* and *Glossary* updated accordingly.

---

## Methodological Note

This template fuses three architectural lineages:

- **Structural backbone** -- from the original Analysis & Design Engineering Template: UML behavioral diagrams, C4, deployment.
- **Decomposition method** -- from Residuality Theory: stressor analysis, contagion matrix, residual integration, empirical Ri test.
- **Component taxonomy and communication rules** -- from IDesign: Managers, Engines, ResourceAccess, Resources, Utilities, with strict call rules.

The intent is that residuality drives **discovery** (which residues exist, where the architecture is brittle), IDesign provides the **vocabulary and communication discipline** that expresses the result (raising P, restricting K in Kauffman terms), and UML/C4 **documents** the final residual architecture for stakeholders.

Use cases and activity diagrams are deliberately repositioned: they are *documentation of the resolved architecture*, never drivers of decomposition. Decomposition is driven by the contagion matrix, the topological residue map, and IDesign discipline.

---

## Business View

*If this document is associated with an SRD, please link to it in this section and remove the following sections if the content could be duplicated.*

### Objective

### Pain Points

### Goals

### Invariants (non-negotiables)

> Business properties that must hold under every stressor: regulatory / legal / contractual non-negotiables (e.g. "personal data never leaves its home jurisdiction"; "funds always flow contractor -> system -> worker"). These are **acceptance criteria the Empirical Test (S6) verifies**, NOT units of decomposition -- the decomposition stays residue-driven (R-01 / R-25). Each invariant is one observable property, grounded to its PRD requirement where a PRD exists (`PRD:L<n>`). Omit this section if the system has no hard non-negotiables (do not invent them -- R-09).

| Invariant | Source (PRD ref, if any) |
|---|---|
| | |

### Open Questions

> Unresolved business inputs surfaced from the PRD/SRD or from stakeholder gaps: PRD TBCs, unconfirmed assumptions, and questions whose answer would change the framing (R-27). Found by the multi-lens Open Questions discovery pass (S1 Step 1.2), NOT noticed ad hoc. These are NOT deferred volatilities (sensed stressors routed to S3): an Open Question needs a stakeholder answer the architect cannot supply; a deferred volatility is a stressor the architect will address in S3. Gate S1a cannot be approved silently while any entry is `Open` (or `Open (partial)`) -- the executor warns and the operator must explicitly acknowledge proceeding. State "None" if there are genuinely no unresolved inputs (do not invent them -- R-09).

> **Card format.** Each Open Question is a card -- a `#### OQ-N - <Status> -- <short title>` heading, then the question, an optional answer (present once a stakeholder gives one), and an Affects/Source footer. This carries a partial stakeholder answer alongside the still-open question, which a bare table row cannot.
>
> - **Status** is one of `Open` (no answer yet), `Open (partial)` (a partial stakeholder answer is recorded but the question still needs more), or `Resolved` (answered -- cite the source). **`Open` and `Open (partial)` both gate S1a; `Resolved` does not.**
> - **Affects** names the goal / invariant / downstream decision the question touches; **Source** (the `**PRD:**` / stakeholder anchor) is where any answer must come from -- the architect never invents one (R-09).
> - The title delimiter before the short title is ` -- ` (an em dash in a rendered doc); the separator after the id is a single ` - ` (a middle dot in a rendered doc). Render with status emoji if you like; the status word is what gates.
> - Pre-1.17.14 fragments used a single `| ID | Open question | Affects | Status | Source |` table; the deterministic check (`check_fragment.py`) still accepts that legacy form.

#### OQ-1 - Open -- <short title>

**Question:** <the unresolved business input, stated in full>

**Answer:** <present only once a stakeholder answers; a partial answer keeps Status `Open (partial)` so the question still gates>

<sub>**Affects:** <goal / invariant / downstream decision> -- **PRD:** <L<n>, or `stakeholder`></sub>

> **Deferred volatilities (sensed now, routed to S3 -- non-gating).** Stressors the architect already senses but deliberately defers to stressor-analysis (S3). Listed here as carry-forward context only; they do NOT gate S1a. Omit if none.
>
> -

#### Lens Coverage Ledger

> Forcing function (R-27): the multi-lens scan (S1 Step 1.2) is complete only when **every** lens L1-L12 has emitted an explicit verdict. A verdict is either the OQ IDs that lens produced or the literal word `none`. A missing lens row or a blank verdict is an incomplete sweep, not a clean one -- the auditor flags it deterministically. `none` is a legitimate verdict, but it asserts the lens was genuinely applied and found nothing.

| Lens | Verdict (OQ IDs, or `none`) |
|---|---|
| L1 Marker (TBC / TBD / unconfirmed / ?) | |
| L2 Hedge (maybe / assume / likely / should) | |
| L3 Unquantified target (~ / indicative / no number) | |
| L4 Undefined term (used but not defined; >1 reading) | |
| L5 Silent actor / ownership (who triggers / approves / owns) | |
| L6 Lifecycle / state gap (state with no entry/exit; flag semantics) | |
| L7 Edge / failure silence (empty / negative / concurrent / failure) | |
| L8 Scope boundary (in/out unclear; deferrals; per-tenant divergence) | |
| L9 External / in-flight dependency (status unconfirmed) | |
| L10 Conflict / measurability (contradictions; non-measurable goals) | |
| L11 Stale / unexamined premise (settled decision on a stale/unverified premise) | |
| L12 Regulatory / compliance / privacy silence (data/money/consent/AML/jurisdiction unaddressed) | |

---

## Architectural Stress Analysis

> **Purpose**
> This section captures the design-time residuality work that drives the rest of the SAD. Outputs are: (a) a residual decomposition expressed in IDesign terms, (b) a deployment topology derived from topological residues, (c) a log of business-only decisions, and (d) a set of empirically-grounded non-functional requirements traceable to specific residues.

### Naïve Architecture

> The minimal IDesign-compliant architecture that solves the problem as described in the SRD/PRD, with no consideration of stress or change. This is the **control** against which the residual architecture will be measured in the empirical test.

*Diagram here -- naive baseline IDesign static view (Managers / Engines / ResourceAccess / Resources). This is the one Mermaid `flowchart` in a SAD (`style-conventions` §6); the residual Static Architecture in §Analysis and Design is PlantUML.*

### Flow Analysis

> A flow is the movement of information between two actors (person, group, company, software component). This replaces process or use-case decomposition as the **analysis-time tool**, since process-based decomposition locks the architecture into a specific business process which is itself volatile.

| Flow # | From (Actor) | To (Actor) | Information / Payload | Trigger |
|---|---|---|---|---|
| | | | | |

### Stressor Catalog

> A stressor is **any fact about the context currently unknown to the architect or unaccounted for in the naïve architecture**. Probability and cost are explicitly excluded at this stage -- they will be considered later, in ATAM and FMEA.
>
> Each residue is **typed**, and the type determines which downstream subsection it feeds:

| Type | Drives a change in... | Feeds | No software change? |
|---|---|---|---|
| **Structural** | IDesign components or call topology | Contagion Matrix | No -- produces components |
| **Topological** | Deployment topology (geography, tenancy, replication) | Topological Residue Map | Sometimes -- may also have component impact |
| **Business** | Business decision only | Business Residues Log | Yes |
| **Combined** | Nothing -- already survived by existing residues | Looping Signals | Yes |

> Sources to feed the catalog: PESTLE, Porter's 5 Forces, Business Model Canvas, abstraction-stressing (challenge every noun in the domain model -- *Customer*, *Order*, *Account*), stakeholder workshops, lateral-thinking exercises.

| Residue # | Type | Stressor | Detection | Attractor (new business state) | Business Reaction | Technical Change to Residue (IDesign) |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |

> **Stop condition**: when new stressors are increasingly hard to find, or when new stressors arrive as *Combined* (already survived), the architecture is approaching **criticality**. Combined residues are not failures of imagination -- they are the empirical signature that the residual analysis is paying off.

### Contagion Matrix (Structural Residues)

> Maps Structural residues (rows) to IDesign components (columns). A `1` means the stressor affects that component's operation; `0` means it does not. Topological residues with component-level impact may also appear here; pure Topological, Business, and Combined residues do **not** enter this matrix.

|  | Manager A | Manager B | Engine X | RA Y | Resource Z | Utility U | Σ Row |
|---|---|---|---|---|---|---|---|
| Stressor 1 | | | | | | | |
| Stressor 2 | | | | | | | |
| **Σ Column** | | | | | | | |

#### NKP Totals

> Per O'Reilly L2520-2522: the matrix gives an approximation of the three Kauffman parameters. Use these as markers for refactor direction, not as targets. NKP is a visual approximation, not exact math (L2658-2664).

| Parameter | Value | How |
|---|---|---|
| **N** | `<#stressors>` + `<#components>` = `<total>` | Count of nodes on both sides of the bipartite matrix (O'Reilly L2522: "the number of stressors and components/functions represents N"). |
| **K** | `<sum of 1s>` | Total `1` cells across the matrix (O'Reilly L2520: "the number of 1's in the network gives an approximation of K"). K captures coupling under stress, NOT the count of HTTP calls in the call graph. |
| **P** | `low` / `medium` / `high` | Qualitative. Tick each consistency axis: uniform error model / uniform auth / interface contracts / uniform serialization / uniform tracing / uniform retry policy / uniform event envelope. 0-2 = low; 3-5 = medium; 6-7 = high. |

> **Reading direction** (O'Reilly L2526-2528): "An analysis of this matrix will allow us to try and **reduce K**, **optimize N**, and decide which measures we need to take to **optimize P**." K goes down; N seeks the critical point; P typically goes up.

#### Refactor Triggers

| Trigger | Pattern | Action |
|---|---|---|
| **Hot row** | Stressor with high row total | High-impact stress; reveals hyperliminal coupling and missed NFRs |
| **Hot column** | Component with high column total | Component is doing too much; consider splitting, or harden with redundancy if importance is real |
| **Multiple 1s in same row** | Two+ components react to same stressor | Hyperliminal coupling -- document the implicit non-functional contract between them |
| **Identical column signatures** | Two components with same response pattern | Merge candidate -- **but apply the IDesign override below before merging** |
| **Globally high K** | Many 1s overall | Pattern or decomposition choice likely wrong -- refactor before commit |
| **Zero-total columns** | Component never touched by stress | Either invulnerable (rare) or stressor catalog is incomplete (likely) |
| **Stressor combinations** | Multiple stressors hit overlapping components | Build an attack/failure tree per combination |

#### IDesign Override on Merge Signals

> **The matrix suggests, IDesign discriminates.**
>
> Two columns with identical signatures are merge candidates *only if they belong to the same IDesign layer*. A Manager--Engine pair that co-evolves is structurally separate by IDesign discipline -- stateful workflow vs. stateless logic -- and must not be merged regardless of matrix signature. Likewise, a ResourceAccess and a Resource cannot be collapsed even if their stress profiles match.
>
> Valid merges from matrix similarity:
>
> - Engine + Engine in the same volatility bounded context
> - ResourceAccess + ResourceAccess for the same resource family
> - Manager + Manager *only* if they own the same logical workflow and were split prematurely
>
> When in doubt, IDesign call rules and the stateless/stateful axis prevail over residuality merge signals.

#### Hyperliminal Coupling Map

> **What this is.** A focused extraction from the matrix. For every row where two or more components have a `1` (Σ Row >= 2), those components are coupled by that stressor *even though no functional dependency in code connects them*. This is the most important insight the matrix produces.
>
> **Why it matters.** Hyperliminal coupling is invisible in the static call graph; it is revealed only when stress hits the system. A fix to one of the coupled components without considering the others will leak. Per O'Reilly L1114-1120, hyperliminal couplings are the canonical source of non-functional requirements: "Since these invisible couplings are not functional, they fall under the realm of non-functional and can help architects to navigate the traditional problem of non-functional requirements."
>
> Every row in this map should drive at least one entry in §Derived NFRs.

| Stressor # | Affected Components | Coupling Nature | Architectural Response | NFR Source (for §Derived NFRs) |
|---|---|---|---|---|
| | | | | |

> **Coupling Nature** -- one of: `intrinsic` (the coupling is inherent to the business domain; e.g., regulation will always couple all audit-relevant components) or `extrinsic` (the coupling is an artifact of the current decomposition and could be removed by refactor).
>
> **Architectural Response** -- one of:
>
> - `Document NFR contract` -- most common. The coupling is accepted; the response is an NFR that specifies how the coupled components must coordinate under stress (atomic operation, eventual consistency window, idempotency, retry contract).
> - `Decouple` -- when the coupling is extrinsic and the matrix shows the residues should not have been entangled. Produces a Structural refactor candidate.
> - `Accept and harden` -- when the coupling is intrinsic and acceptance is the right call (no NFR contract beyond standard reliability), but the affected components warrant redundancy / observability uplift.

### Topological Residue Map

> Topological residues drive deployment topology, not component decomposition. They feed the *Deployment Diagram* section directly. Examples: data residency by jurisdiction, multi-region replication, tenant isolation, latency-zone partitioning.

| Residue # | Topology Driver | Deployment Decision | Affected Components | Cross-Boundary Constraints (Allowed / Forbidden) |
|---|---|---|---|---|
| | | | | |

> **Reading**: each row defines a deployment unit boundary and the data/control flows permitted across it. This is also the canonical source of any residency, latency-zone, or sovereignty NFRs -- those NFRs trace to rows here, not to the contagion matrix.

### Business Residues Log

> Stressors that produced a business decision but no software change. These exist to record that the conversation took place, what was decided, and why no architectural action was needed. They are **decisions-of-record**, equivalent to ADRs.
>
> A residue that is *business only* today may become *structural* tomorrow if the decision changes. The log preserves the chain of reasoning so a future architect understands *why the system does not solve a problem it could have solved*.

| Residue # | Stressor | Attractor | Business Decision | Rationale for No Software Change |
|---|---|---|---|---|
| | | | | |

### Looping Signals (Combined Residues)

> When a new stressor is already survived by a combination of existing residues, no new residue is created. These *combined residues* are the empirical signature of approaching criticality and **should be recorded** -- they are the strongest evidence of the value of the residual analysis, and the most persuasive material when communicating with stakeholders or leadership.

| Residue # | Stressor | Survived by Combination of | Notes |
|---|---|---|---|
| | | | |

### Service Grouping Map

> Which IDesign components run in which separately deployable units (services / containers). Actor-style default (R-25): **one Manager, one service**, with the Engines/ResourceAccess used only by that Manager co-located inside it (O'Reilly L1940-1943 "same stress profile -> combine", applied within the Manager's cluster). A shared Engine/RA (used by 2+ Managers) becomes its own service only when promoted by an operational Topological residue (`independent-scaling` / `failure-isolation` / `change-cadence` / `resource-profile` / `security-zone`). Do not collapse all Managers into one monolith, and do not give a single-Manager Engine its own service. The §C4 Model container view draws one `container` per row of this table.

| Service / Deployable Unit | IDesign components (Manager + its private Engines/RAs, or a shared component) | Grouping basis (Manager's Structural residue #, or operational Topological residue # for a promoted shared component) |
|---|---|---|
| | | |

### Derived Non-Functional Requirements

> NFRs are not generic boilerplate. Each NFR below traces back to:
>
> - one or more cells of the **contagion matrix** (component-level NFRs), or
> - one or more rows of the **topological residue map** (residency, latency, sovereignty NFRs), or
> - a **business residue** that imposes an operational constraint without changing components.
>
> If you cannot trace an NFR to one of these three sources, it is not a real NFR for this system -- it is a copy-paste from a previous template.

| NFR | Source (Matrix Cell / Topology Row / Business Residue #) | Specification |
|---|---|---|
| | | |

### Empirical Test (Residual Index)

> After the residual architecture is integrated, generate a **new** list of stressors not used during design. Apply both the naïve and the residual architecture against this list. Count survivors:
>
> - X = stressors survived by the naïve architecture
> - Y = stressors survived by the residual architecture
> - S = total stressors in the test list
>
> Ri = (Y - X) / S,   where  -1 ≤ Ri ≤ 1
>
> Ri > 0 indicates positive movement toward criticality. As Ri approaches 0 across iterations, further architectural work yields diminishing returns. Test stressors that the residual architecture *fails* to survive mark the next round of stress analysis -- the unstressed surfaces of the system.

| Iteration | Date | S | X | Y | Ri | Unstressed Surfaces Identified |
|---|---|---|---|---|---|---|
| 1 | | | | | | |

#### Invariant Preservation

> For each invariant declared in §Business View, verify the residual architecture preserves it under the test stressors. A violation is a **critical regression** (worse than a per-stressor regression): the system may survive a stressor yet break a non-negotiable while doing so. Omit if no invariants were declared.

| Invariant | Preserved under all test stressors? | Violating stressor + residue (if any) |
|---|---|---|
| | | |

---

## Analysis and Design

> **Purpose**
> The diagrams in this section **document** the residual architecture produced above. They are not the source of decomposition decisions; the contagion matrix and the topological residue map are. Use cases describe how the resolved architecture behaves, not how it was decomposed.

### Behavioral Diagrams

> All behavioral diagrams in this section (use-case / activity / sequence / statechart) are authored in **PlantUML** (`\`\`\`plantuml` fenced blocks, `@startuml ... @enduml`), not Mermaid -- `style-conventions` §6.2. Prefer activity diagrams for use-case process flows; sequence diagrams when the cross-service interaction is the point.

| Diagram | Description |
|---|---|
| **Use Case Diagram** | Organizes observable behaviors of the resolved system |
| **Sequence Diagram** | Time ordering of messages across IDesign layers |
| **Collaboration Diagram** | Structural organization of message-passing objects |
| **Statechart Diagram** | State transitions driven by events |
| **Activity Diagram** | Flow of control across activities |

---

#### Use Case #1

*Diagram here*

##### Scenarios

- **Main:** Scenario that allows you to create a new event.
- **Alternative:** Scenario where the received event already exists.
- **Exceptional:** Scenario where the event cannot be created because there are problems with the database.

##### Activity Diagram

*Diagram here*

##### Residue Mapping

> Which residues from the Stressor Catalog does this use case exercise? Include all types -- Structural residues that shaped the components, Topological residues that constrain where it can run, and any Business residues that affect its operation.

| Residue # | Type | Relevance to this Use Case |
|---|---|---|
| | | |

##### Non-functional Requirements (per Use Case)

> These NFRs must trace to specific cells of the contagion matrix, rows of the topological map, or business residues involving the components participating in this use case.

| Attribute | Specification | Source (Matrix Cell / Topology Row / Business Residue #) |
|---|---|---|
| **Scalability** | | |
| **Availability** | | |
| **Performance** | | |
| **Reliability** | | |
| **Interoperability** | | |

---

#### Use Case #2

*Diagram here*

##### Scenarios

- **Main:**
- **Alternative:**
- **Exceptional:**

##### Activity Diagram

*Diagram here*

##### Residue Mapping

| Residue # | Type | Relevance to this Use Case |
|---|---|---|
| | | |

##### Non-functional Requirements (per Use Case)

| Attribute | Specification | Source |
|---|---|---|
| **Scalability** | | |
| **Availability** | | |
| **Performance** | | |
| **Reliability** | | |
| **Interoperability** | | |

---

### General Non-functional Requirements

> System-wide NFRs that emerge from the contagion matrix, topological map, or business residues at the *system* scope rather than per-use-case.

| Attribute | Requirements |
|---|---|
| **Scalability** | The system must handle traffic by scaling vertically and/or horizontally. The team is responsible for capacity planning. |
| **Availability** | Core functionality must be available 24/7. The service must have a Disaster Recovery Plan. The system must provide readiness and liveness endpoints. The system must provide circuit breaker and retry mechanisms. |
| **Performance** | The system must be as efficient as required by the specifications of each use case. |
| **Reliability** | No loss or corruption of data during processing. |
| **Interoperability** | Dapr will be used to ensure interoperability with other applications and services. |
| **Monitoring** | Event monitoring and logging must be supported for issue identification and resolution. Components must share a distributed trace with a unique identifier, based on OpenTelemetry. |

---

### Structural Diagrams

| Diagram | Scope | Representation |
|---|---|---|
| **Static Architecture (IDesign)** | IDesign components + call rules (per layer) | PlantUML `\`\`\`plantuml` component diagram (not C4; `style-conventions` §6.2) |
| **C4 Model** | System Context + Container + per-Container Component + Deployment + optional Dynamic, all derived from one model | one Structurizr DSL `workspace.dsl` (R-23) |
| **Virtual Actor Diagram** (optional) | Virtual actors (Dapr) when applicable | per-tool |

---

#### Static Architecture (IDesign)

> The static architecture follows the **IDesign taxonomy**, which provides the vocabulary and communication discipline of the residual architecture. The taxonomy and call rules raise **P** (component bias toward predictable behavior) in the Kauffman sense, while the contagion matrix has already optimized **N** and **K**.

##### Component Taxonomy

| Layer | Stereotype / Naming | Responsibility | State |
|---|---|---|---|
| **Clients** | UI, external callers | Trigger Manager workflows | -- |
| **Managers** | `<Verb>Manager` | Orchestrate workflows of a use case; the only stateful workflow holders | Stateful per workflow |
| **Engines** | `<Noun>Engine` | Encapsulate volatile business activity / rules | Stateless |
| **Resource Access** | `<Noun>Access` | Translate business operations into resource operations | Stateless |
| **Resources** | DB, queue, external API | Persisted state and external systems | -- |
| **Utilities** | Cross-cutting | Logging, security, configuration | Stateless |

##### Call Rules

| From -> To | Allowed | Notes |
|---|---|---|
| Client -> Manager | yes | Entry point. Prefer queued/async via Dapr Pub/Sub for long-running workflows |
| Manager -> Manager | Async only | Never synchronous. Queue via Dapr Pub/Sub. Avoids hidden coupling that would inflate K |
| Manager -> Engine | yes | Synchronous business logic |
| Manager -> ResourceAccess | yes | Direct, when no business logic is needed |
| Engine -> ResourceAccess | yes | |
| Engine -> Engine | no | Reuse via Manager composition or extract into shared Engine called by Manager |
| ResourceAccess -> Resource | yes | Only ResourceAccess touches the underlying Resource |
| Manager / Engine / ResourceAccess -> Utility | yes | Utilities are internal infrastructure of the system |
| Client -> Utility | no | Clients trigger Manager workflows; they do not call internal infrastructure directly. Synthesis stricter than Lowy L1317; consistent with Lowy L1381 |
| Resource -> Utility | no | Resources are passive |
| Upward calls (Engine -> Manager, RA -> Engine, RA -> Manager, Resource -> anything) | no | Hard rule. Violations break P and inflate K |

*Static architecture diagram here (PlantUML `\`\`\`plantuml` component diagram -- `style-conventions` §6.2; NOT Mermaid, NOT C4)*

---

#### C4 Model (Structurizr DSL)

Per R-23, all C4 architecture is one `workspace.dsl` (one model -> derived views). Author it in a single fenced ```dsl block. See `shared/style-conventions.md` §6.1 for vocabulary, per-level scope, and the IDesign-layer tag/style mapping.

- **Model:** `person`s; the target `softwareSystem` containing one `container` per §Service Grouping Map row (names verbatim), each service container nesting its IDesign `component`s tagged `Manager`/`Engine`/`ResourceAccess`/`Resource`/`Utility`/`Client`; data stores tagged `"Database"`, queues `"Queue"`; external systems as `softwareSystem ... "External"`; relationships (`->`, source = initiator, obeying the Call Rules); a `deploymentEnvironment` nesting `deploymentNode`s with `containerInstance`s.
- **Views:** one `systemContext`; one `container`; one `component <container>` for **every** container with 2+ IDesign components (mandatory coverage); one `deployment`; optionally one `dynamic` per key flow. Each `include *` + `autoLayout`.
- **Styles:** an IDesign-layer `styles` block.

*`workspace.dsl` here (single ```dsl block). Renderers derive the per-level images from it.*

##### Container <-> Component mapping

| Container | Technology | IDesign components inside (Level 3) | Documentation |
|---|---|---|---|
| | | | |

---

#### Virtual Actor Diagram

| Actor | IDesign Layer | Description | Responsibility | Use Cases / Residues |
|---|---|---|---|---|
| | | | | |

*Diagram here*

---

#### Deployment Unit Boundaries

The `deployment` view of the §C4 Model `workspace.dsl` (above) visualizes the runtime topology: `deploymentNode`s nesting cloud > region > cluster > pod with `containerInstance`s. Per R-19, every deployment-unit boundary traces to a Topological Residue #; per-jurisdiction residues become separate top-level `deploymentNode`s.

##### Deployment Unit Boundaries (from Topological Residue Map)

| Boundary | Topological Residue # | Allowed Cross-Boundary Flows | Forbidden Cross-Boundary Flows |
|---|---|---|---|
| | | | |

---

## Technical Considerations

| Consideration | Details |
|---|---|
| **Service-oriented approach** | Each service represents a limited business context. The residual analysis informs which contexts deserve their own service (high column total + distinct attractor profile). |
| **Event-driven architecture** | EDA via Dapr for asynchronous communication, especially Manager -> Manager. Integration events based on the area's business processes. CloudEvents standard. Backstage as event catalog. |
| **Development technology** | C#, .NET Core. Libraries not versioned unless vulnerability or major framework change. No SDKs for pub/sub -- Dapr only. |
| **Design Patterns** | Circuit Breaker (Dapr), Pub/Sub (Dapr), Virtual Actors (Dapr) |
| **Deployment** | Use DevOps abstractions where possible. |
| **Documentation and testing** | All services documented; unit and integration tests required. |
| **Criticality discipline** | Architecture decisions prioritize **criticality** (survival under unknown stress) over **correctness** (perfect handling of known requirements). Correctness is the goal of the developer; criticality is the goal of the architect. |

### Architectural Fitness Functions

> The SAD does not stop at stating the rules -- it prescribes how the **implementation** enforces them, so the code cannot drift from the architecture. Each fitness function is an automated check the implementation team wires into CI; the SAD names the check and the rule it enforces. These are recommendations to implementation, not code the SAD ships.

| Fitness function (CI assertion) | Enforces | Fails the build when |
|---|---|---|
| No module in a layer imports a layer above it | R-03 closed architecture | An upward dependency exists (Engine -> Manager, RA -> Engine, Resource -> anything) |
| No Engine references another Engine; no RA references another RA | R-03 (no sideways within layer) | A same-layer call exists outside the R-04 exceptions |
| Client modules reference only Manager entry points | R-04 (a) tightened | A Client imports an Engine / RA / Utility |
| Manager-to-Manager calls go through the Pub/Sub Utility only | R-04 (d) | A synchronous Manager -> Manager call exists |
| Each deployable unit contains exactly one Manager (+ its private Engines/RAs) | R-25 actor-style | A service hosts 2+ Managers without a documented co-location, or a single-Manager Engine has its own service |
| Component names match the residue taxonomy | R-05 / R-06 | A name carries technology vocabulary or breaks Pascal+suffix |
| A shared Resource is read-only for non-owner services | R-25 / Step 2.7 | A non-owner service writes a shared Resource |

The set is project-specific: derive one fitness function per Call Rule and per Service Grouping Map row. This is the design -> implementation bridge -- the auditor guarantees the SAD is internally correct; these functions guarantee the code stays faithful to it.

---

## Restrictions

### Pub/Sub

- Use of external SDKs (e.g. **Pulsar.Client**) is not allowed. Only the Dapr Pub/Sub component.

**Justification:**

- **Infrastructure abstraction** -- Dapr hides the underlying broker (Pulsar, Kafka, etc.), reducing vendor lock-in.
- **Unified observability** -- standardized metrics, traces, and logs across all Pub/Sub operations.
- **Simplified maintenance** -- avoids broker-specific SDK upgrades and lets teams focus on business logic.

### Event Schema

- All events must be validated against the **CloudEvents** schema registered in **Backstage**.

### Decomposition Discipline

- **No new structural component** is introduced without a *Structural* residue in the Stressor Catalog.
- **No new deployment unit** is introduced without a *Topological* residue in the Topological Residue Map.
- **No business decision** that affects architectural reasoning is undocumented -- it lives in the *Business Residues Log*.
- **No NFR** is documented without traceability to a contagion matrix cell, a topological boundary, or a business residue.
- **No use case** is the source of a decomposition decision; use cases document the behavior of the resolved architecture.
- **No probability or cost discussion** until after the stressor catalog is closed and the matrix is complete.
- **Manager--Engine pairs (and any cross-layer pairs) are not merged** based on matrix similarity alone; IDesign layer discipline overrides pure-residuality merge signals.
- **Combined residues are recorded, not discarded** -- they are evidence of criticality and the strongest argument for the value of the analysis.

---

## Appendices

### References

- PRD:
- SRD:
- O'Reilly, B. M. (2024). *Residues: Time, Change, and Uncertainty in Software Architecture.* Leanpub.
- Lowy, J. (2019). *Righting Software.* Addison-Wesley.
- Parnas, D. L. (1972). *On the criteria to be used in decomposing systems into modules.* CACM 15(12).
- Kauffman, S. A. (1995). *At Home in the Universe.* Oxford University Press.

### Architecture Decision Records (ADRs)

Significant decisions that are too large or contested to fit in a single SAD cell are recorded as ADRs in `<project-root>/docs/adr/ADR-XXXX-<short-name>.md`. Use the template at `sad/adr-template.md`. List the ADRs that apply to this SAD here:

| ADR | Title | Status | Referenced from |
|---|---|---|---|
| | | | |

Reference an ADR from the SAD body using its ID (e.g., `ADR-0003`). Common reference points: §Restrictions, §Technical Considerations, Business Residues Log Rationale column, Topological Residue Map Cross-Boundary Constraints column. See `adr-template.md` §How to reference an ADR from the SAD for details.

### Audit Status

Audit reports are produced by the `sad-auditor` sub-skill, one per iteration, as separate files (`audit-iter-N.md` in the project workspace). They are NOT embedded in this SAD; this section is the index.

| Iteration | Audit date | Mode | Status | Open Violations | Accepted Exceptions | Report |
|---|---|---|---|---|---|---|
| | | | | | | |

The audit is considered closed only when all deterministic violations are resolved or explicitly accepted with rationale (no `--force`). See `sad/sad-auditor/SKILL.md` for the auditor's check inventory and refusal conditions.

### Stressor Source Frameworks

- **PESTLE** (Political, Economic, Social, Technological, Legal, Environmental)
- **Porter's 5 Forces**
- **Business Model Canvas**
- **Abstraction stressing** -- challenge every noun in the domain model
- **Flow stressing** -- for each flow, ask what could prevent, delay, duplicate, reroute, or corrupt the information
- **Boundary stressing** -- for each component pair, what would force them into separate deployable units (operational Topological residues)
- **Every-noun pass** (O'Reilly Rule 3) -- run exhaustively: every noun of every component name, stressed (fails / multiplies / schema-changes / deleted-in-use / replayed)

### Traceability Matrix

> A consolidated view of the traceability that is otherwise distributed across the SAD (R-15 NFR sources, R-16 use-case residue mappings, R-18 component-to-residue, R-19 deployment-to-topology, optional PRD grounding). One row per residue; columns chain residue -> component -> NFR -> use case -> deployment -> (optional) PRD source. This is a derived view -- it does not introduce new traceability, it makes the existing chains auditable at a glance.

| Residue # | Type | Component(s) | NFR(s) | Use case(s) | Deployment unit | PRD source (if any) |
|---|---|---|---|---|---|---|
| | | | | | | |

### Glossary

| Term | Definition |
|---|---|
| **Residue** | What remains of an architecture after exposure to a specific stressor; the unit of architectural change |
| **Stressor** | Any fact about the context unknown to or unaccounted for in the naïve architecture |
| **Attractor** | A recurring state of the business system to which a stressor pushes it |
| **Hyperliminal coupling** | Implicit coupling between components, revealed only when both react to the same stressor |
| **Criticality** | The Kauffman-network state where N, K, P are balanced such that the system survives unknown stress |
| **N / K / P** | Number of components / links / behavioral bias -- the three Kauffman parameters governing attractor count |
| **Ri (Residual Index)** | Empirical metric (Y - X) / S of a residual architecture's improvement over the naïve baseline |
| **Looping** | When new stressors are already survived by existing residues -- recorded as Combined residues, signal of approaching criticality |
| **Structural residue** | A residue that drives a change in IDesign components or call topology. Enters the contagion matrix |
| **Topological residue** | A residue that drives a change in deployment topology (geography, tenancy, replication). Enters the topological residue map |
| **Business residue** | A residue that produces a business decision but no software change. Logged as decision-of-record |
| **Combined residue** | A stressor already survived by a combination of existing residues. No new component or deployment change; recorded as criticality evidence |
| **IDesign override** | Principle by which IDesign layer discipline (stateless/stateful, call rules) overrides matrix-driven merge signals across layers |
