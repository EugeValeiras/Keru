---
name: residual-design
description: Fifth sub-skill of the `sad` meta-skill. Produces the Derived NFRs and Analysis-and-Design fragment of a SAD -- the residual architecture expressed in IDesign vocabulary, the use cases (as documentation only), and the structural diagrams (C4, deployment). Invoke after the contagion-analysis fragment is approved. Every NFR traces to a Coupling Map row, Topology row, or Business residue. Every new component traces to a Structural residue. Every deployment unit traces to a Topological residue.
task_types: [design, integrate-residues, idesign-static, derive-nfrs]
shared_refs:
  - shared/constitution.md
  - shared/idesign-vocabulary.md
  - shared/decomposition-discipline.md
  - shared/glossary.md
  - sad/template.md
  - sad/synthesis-explanation.md
---

# residual-design (S5)

Produces the Derived NFRs section and the full Analysis-and-Design section of a SAD. This is where the residual architecture is **expressed** -- it has already been **decided** by the upstream chain (Stressor Catalog -> Contagion Matrix -> Hyperliminal Coupling Map -> Topological Residue Map -> Business Residues Log -> Looping Signals). S5 puts the decision into IDesign vocabulary, derives the non-functional requirements from the contagion analysis, and produces the diagrams that document the result.

S5 does NOT take new architectural decisions. Every component, every NFR, every deployment unit boundary traces back to a specific row of the upstream fragments. If S5 needs to introduce something without traceability, the upstream is incomplete -- backtrack to S3 / S4 instead of inventing in S5.

---

## When to invoke

- `contagion-analysis.md` exists, is approved, and has all seven sub-tables populated (Contagion Matrix, NKP Totals, Hyperliminal Coupling Map, Topological Residue Map, Business Residues Log, Looping Signals, Service Grouping Map).
- The architect is ready to commit to a residual decomposition expressed in IDesign vocabulary.
- The IDesign override decisions from S4 are settled (no pending cross-layer merge questions).

## When NOT to invoke

- Contagion analysis fragment does not exist or has incomplete sub-tables (run / finish S4 first).
- The Hyperliminal Coupling Map has rows with non-decisive Architectural Response ("investigate" / "TBD"). Those decisions belong in S4; close them there before S5.
- The user wants to redesign the architecture from scratch ignoring the contagion analysis. That is not S5; that is a re-run of the meta-skill from S1.

## Pre-conditions

- The **S4 gate is marked `[x] approved`** in the project gate tracker (`FLOW.md`), not merely produced -- verify before producing (root `SKILL.md` §Gate approval protocol).
- `business-view.md`, `naive-architecture.md`, `flow-analysis.md`, `stressor-catalog.md`, `contagion-analysis.md` all exist and are approved.
- Hyperliminal Coupling Map rows with `Document NFR contract` response have NFR Source references that S5 will consume.
- Topological Residue Map rows have Cross-Boundary Constraints declared.
- The §Service Grouping Map (S4 Step 9) exists; the §C4 Model container view has one `container` per row of it (R-25).

## Handoff contract

- **Consumes:** `contagion-analysis.md` (Coupling Map rows -> NFRs per R-15; Topology rows -> deployment per R-19; Service Grouping Map -> Containers per R-25) + `business-view.md` invariants (the regression target S6 will check) -- prior gate S4 must be `[x] approved`.
- **Produces:** `residual-design.md` (NFRs + Static Architecture + Use Cases + 5 C4 diagrams + Deployment + Architectural Fitness Functions).
- **Lateral context to carry forward:** why each residue exists (its originating Structural stressor per R-18, so S6 can re-stress it), the gate-vs-config split decisions, and the service-grouping rationale -- carried so S6's fresh stressors probe the same seams rather than re-deriving them.

## Workflow

### Step 1 -- Derive NFRs

Walk the contagion-analysis fragment and produce one or more NFR rows for each of three sources. Every NFR has a non-empty Source column (R-15).

#### 1.1 NFRs sourced from Hyperliminal Coupling Map

Per O'Reilly L1114-1120 (canonical): hidden couplings revealed by the matrix ARE the non-functional requirements. For each Coupling Map row with `Architectural Response = Document NFR contract`:

- Read the row's `NFR Source` reference (e.g., `Hyperliminal Coupling #2`).
- Read the row's `Affected Components` (e.g., `Billing + Storage + Audit`).
- Write one or more NFRs that specify how the coupled components coordinate under the stressor:
  - Atomic operation contract (e.g., "Billing, Storage, Audit commit or rollback as one unit when stressor #2 hits").
  - Eventual consistency window (e.g., "Audit reaches consistency with Billing within 5 seconds").
  - Idempotency contract (e.g., "Billing retries are safe; duplicate stress events produce no double-charge").
  - Retry / replay semantics (e.g., "Storage replays from durable log on Billing partial-commit").

For each Coupling Map row with `Architectural Response = Accept and harden`, write operational NFRs (redundancy level, observability requirements, monitoring SLAs).

For each Coupling Map row with `Architectural Response = Decouple`, do NOT write an NFR -- the response is a Structural refactor (handled in Step 2). The Coupling Map row's `NFR Source` will be `(refactor)`.

#### 1.2 NFRs sourced from Topological Residue Map

For each row of the Topological Residue Map, write one or more NFRs covering:

- Data residency (e.g., "Customer PII does not cross country boundaries").
- Latency zone (e.g., "Charge authorization completes within 200ms in the customer's home region").
- Sovereignty / jurisdiction (e.g., "All EU operations comply with AFIR ad-hoc payment requirement").
- Replication / failover (e.g., "Per-region instances survive a single-region outage without data loss").

The Source column references the topology row by number.

#### 1.3 NFRs sourced from Business Residues Log

For each Business Residues Log row that constrains operations without producing code (e.g., diversification readiness, capacity provisioning), write an NFR that names the operational constraint. The Source column references the Business Residue # by number.

#### 1.4 Validate NFR traceability

| Check | Verification |
|---|---|
| Every NFR has a Source | R-15 / guardrail #4 |
| Source resolves to a real upstream artifact | The reference points to an existing Coupling Map row / Topology row / Business residue |
| No boilerplate NFRs | No row reads "the system must be highly available", "performance must be acceptable", "the system must be efficient" without a traceable source |

### Step 2 -- Produce the Static Architecture

Walk the upstream fragments and produce the residual decomposition in IDesign vocabulary.

#### 2.1 Component Taxonomy table

Start from the Naïve Architecture (S1 output) and apply every Structural residue from the Stressor Catalog. For each residue's `Technical Change to Residue (IDesign)` column entry, integrate the component additions / changes / splits / merges into the taxonomy. Every component in the taxonomy traces to one or more Structural residues per R-18.

Taxonomy columns:

| Layer | Component | Stereotype / Type | Responsibility | State |
|---|---|---|---|---|

Apply naming conventions per R-06 (two-part Pascal case, valid suffix). Apply hygiene per R-05 (no technology vocab).

#### 2.2 Call Rules table

For each pair of components, declare whether a call is allowed, with notes. Use the Call Rules pattern from `shared/idesign-vocabulary.md` §3. Apply the recent tightening: `Client -> Utility` forbidden (Lowy L1381 + synthesis); `Resource -> Utility` forbidden.

**Derive the Architectural Fitness Functions from the Call Rules + Service Grouping Map.** The SAD does not stop at stating the rules -- it prescribes how the implementation enforces them in CI so the code cannot drift from the architecture (template §Technical Considerations §Architectural Fitness Functions). Produce one CI assertion per call rule (no upward calls -> R-03; no Client->Engine/RA/Utility -> R-04(a); no sync M-to-M -> R-04(d)) and per Service Grouping Map row (one Manager per deployable unit -> R-25; shared Resource read-only for non-owners). These are recommendations to the implementation team, not code the SAD ships -- the design->implementation bridge.

#### 2.3 Static Architecture diagram (PlantUML)

Produce a PlantUML `\`\`\`plantuml` component diagram (`@startuml ... @enduml`) showing the four IDesign layers (Client / Business Logic with Manager + Engine / ResourceAccess / Resource) plus the Utilities Bar. Each component is a `component`; group by layer with `package`. Edges respect the closed architecture (R-03) and the four legitimate exceptions (R-04): solid `-->` for sync calls, dashed `..>` for queued / async (R-04 (d)). PlantUML, not Mermaid -- `style-conventions` §6.2.

#### 2.4 Watch for if-cascade residues during component design

Per R-22 and `shared/architectural-walking.md` §4.2: when a residue's Technical Change column reads as a branch addition (`if isLateTick`, `if isCorrection`, `if isFleetCustomer`, etc.), the residue is probably wrong. A correct residue is usually a decoupling, an interface abstraction, or a partitioning that makes the special case structural rather than conditional.

When designing the Static Architecture, if a component would have to handle a multi-branch conditional for residues from S3, that is a signal one of two things has happened:

1. The residues in the catalog are too low-level -- they describe symptoms (the branches needed) rather than attractors (the structural shifts). Backtrack to S3 and re-run Step 6 (edge case as broken abstraction).
2. The component's responsibility is too broad -- it is absorbing multiple distinct residues that should live in separate components. Split the component during S5.

Either way, do not produce a Static Architecture where a single component carries an `if`-cascade across many residues. The Contagion Matrix will reveal this as a hot column (column total >= 5 with the residues being qualitatively unrelated to each other), and S5 must split before the matrix gets that bad.

#### 2.5 Split a hot Manager proactively -- do not wait for the auditor

The smallest-set baseline (R-24, "in theory just another Manager") starts most systems with a single Manager. As goals accumulate, that one Manager can absorb many unrelated workflows and become a hot column in the Contagion Matrix. **S5 must evaluate the split here, not leave it for the auditor to catch.**

Trigger to split (heuristic, both conditions): the single Manager's `Σ Column` in the Contagion Matrix is high (roughly `>= 8`) **AND** its responsibilities are **heterogeneous workflows** (distinct sequences that respond to distinct stressors), not one workflow with many steps.

How to split:

- **Split by clusters of volatility, not by use case (R-16).** Group the Manager's responsibilities by which residues hit them (column-signature clusters in the matrix); each cluster that is qualitatively independent becomes its own Manager. Do NOT split by use case (that is functional decomposition disguised, R-01 / R-16).
- **Inter-Manager communication is queued Manager-to-Manager via the Pub/Sub Utility (R-04 (d)),** never synchronous (R-03). A Manager that finishes its part emits an event; the next Manager subscribes.
- **Each resulting Manager stays almost-expendable (R-11)** -- workflow orchestration only, no business logic.
- Under R-25, each resulting Manager is then its own deployable service (one Manager, one service); its private Engines/RAs co-locate with it.

This converts what was historically an auditor finding (the hot-column Manager split) into anticipatory S5 design. If the split is genuinely unclear, produce the mono-Manager but flag the hot column explicitly so the `by-fragment` audit at the S5 gate (R-22 output-shape signal) raises it.

**Caveat -- synchronous gates do NOT split out.** A hot Manager often has its Σ Column inflated by **synchronous gates** (in-line validations on the execution path -- a risk-envelope check before a trade, an eligibility check before a match). A gate cannot leave the execution path: splitting it into another service would force a synchronous Manager-to-Manager / cross-service call, which R-03 forbids. So when you split a hot Manager, **only the configuration volatility separates; the gate logic stays co-located** on the execution path. See §2.7 for the full pattern.

#### 2.6 Structural Change Impact Checklist -- propagate in lockstep

Any structural change to a component -- a **split** (one component becomes several, e.g. the hot-Manager split in 2.5), a **rename**, a **merge**, or a **re-typing** -- ripples across the SAD. Incomplete propagation is the most common error after a structural change (a label updated in the taxonomy but stale in two diagrams and seven NFRs). When you split / rename / merge / re-type a component, update ALL of the following in the same pass, before writing the fragment:

1. **Component Taxonomy** table (the component's row).
2. **Call Rules** table (every row that referenced the old component).
3. **Static Architecture diagram** (nodes and edges).
4. **All C4 diagrams** -- Context (if it surfaced there), Container (the deployable unit), every Component diagram, Deployment.
5. **Affected Components column of EVERY NFR** -- not just the obvious ones; grep the old name across the whole §Derived NFRs and §General NFRs tables.
6. **Every Use Case** -- activity diagrams, scenarios, and Residue Mapping tables that named the component.
7. **Deployment Unit Boundaries** table and the **§Service Grouping Map** (a split usually changes the service grouping, R-25).
8. **Upstream candidate residue names this design discarded or folded.** A residue's IDesign name in S3 / S4 prose is a *candidate*, not binding (R-22); S5 may fold it into another component (R-24 smallest-set) or re-type it. When it does, sweep where that name appears upstream (S3 catalog prose, S4 `Optimize N` / matrix-reading notes) and annotate it `(folded into X)` / `(re-typed as X)`. This stops a discarded candidate from reading as a live component the auditor flags as obsolete.

Treat the old component name as a search term: it must not survive anywhere except in a deliberate "renamed from X" note. The `sad-auditor` has a deterministic post-change consistency check (component names in every diagram / NFR resolve to the current taxonomy) -- but propagating here, in lockstep, is cheaper than fixing it across audit iterations.

#### 2.7 Synchronous gate with externalized config (resolves R-25 vs R-03)

The actor-style default (R-25, one Manager = one service) collides with closed architecture (R-03, no synchronous Manager-to-Manager) whenever a **gate** -- a synchronous in-line check on the execution path -- needs a policy that another Manager owns. Example: `TradingManager`'s execution path must pass a risk-envelope gate, but the envelope limits are volatile and owned by an envelope-administration workflow. You cannot make the gate call the envelope service synchronously (R-03), and you cannot fold both workflows into one Manager (they have genuinely different volatilities, R-11).

The resolving pattern -- **synchronous gate with externalized config**:

1. **The gate logic stays co-located** on the execution path, as an Engine invoked by the Manager that owns that path (`RiskEnvelopeGate` Engine inside `TradingService`). It is synchronous and in-process -- R-03 respected, no cross-service sync call.
2. **The gate's configuration** (the volatile policy: limits, thresholds, rules) lives in a **shared Resource**, read by a **read-only ResourceAccess co-located in each service that gates on it** (`EnvelopePolicyAccess` (read-only) inside `TradingService`).
3. **Writes to that config stay with the single owning Manager** (the envelope-administration workflow owns `EnvelopeStore` writes). Every other service only reads.
4. The shared Resource is a **hyperliminal coupling** -- record it explicitly in the §Hyperliminal Coupling Map (S4), do not let it be implicit.

Guard rails (so this does not erode actor-style isolation into "everyone shares everything"):

- **Read-only only.** A service that is not the owner reads the shared config; it never writes it. A cross-service write is an R-25/R-03 violation, not this pattern.
- **Policy / gate reads only.** This is for configuration a gate consults, not for general business state. Sharing business-state Resources across services is a different (and usually wrong) thing.
- **Ask R-11 first.** If two Managers need to share a Resource read-write, that is a signal they may be one Manager -- check before reaching for the shared Resource.
- A shared **read-only** config Resource is allowed across services; the auditor treats it as a documented hyperliminal coupling, not a violation. A shared **read-write** Resource across services IS a violation.

#### 2.8 Every Client-facing service needs an entry Manager

A residue sometimes names only an Engine + a ResourceAccess for a Client-facing capability (e.g. "AccessControlEngine + IdentityAccess" for sign-in). Wiring the Client straight to the Engine or the RA is an R-03 / R-04 (a) violation -- the Client may only call a Manager. **Any service the Client invokes needs an entry Manager** that owns the workflow and orchestrates the Engine + RA. Identity / security / access-control is NOT an exception (and a Security Utility is not an entry point either -- the Client -> Utility call was forbidden by the 2026-05-10 tightening). So "AccessControlEngine + IdentityAccess" becomes `IdentityManager` -> `AccessControlEngine` + `IdentityAccess`.

### Step 3 -- Apply the Hyperliminal Coupling Decoupling decisions

For each Coupling Map row with `Architectural Response = Decouple`, apply the decoupling in the Static Architecture:

- The original entangled components are split.
- New ResourceAccess / Engine / Manager components are introduced as the residue dictates.
- The Call Rules table is updated to reflect the new topology.

If a Decouple decision cannot be implemented in the Static Architecture (e.g., the proposed refactor violates R-03 closed architecture), the decision was wrong -- backtrack to S4 and re-evaluate the row.

### Step 4 -- Produce Use Cases as documentation

Use cases enter the SAD here for the first time. They document the resolved residual architecture per R-16; they do NOT drive decomposition.

**Seeding from a rich-docs entry.** When the project entered via `business-discovery` §Rich documentation
input (multi-initiative), the input use cases were carried forward as seed evidence. SEED each Use Case
here from its source -- preserve the input's Main/Alternative Flows, Business Rules, and Acceptance
Criteria **verbatim** (anchored to the source doc; gaps `NEEDS CLARIFICATION`) -- rather than authoring
from a blank page, then ADD the Residue Mapping (§4.3). Seeding does NOT relax R-16: a seeded use case
with zero residues in its mapping still does not belong in the SAD (added speculatively, R-09 risk) --
drop it or surface the gap. The verbatim flows/BR/AC are how the input's fine detail is preserved without
inflating the upstream business view.

For each Use Case the project requires (typically 2-5 core use cases; rarely more than 6):

#### 4.1 Use case diagram and scenarios

A UML-style Use Case Diagram (PlantUML `\`\`\`plantuml`; `style-conventions` §6.2) showing actors, the use case, and the components it touches. Scenarios documented as:

- **Main scenario** -- the happy path through the residual architecture.
- **Alternative scenario(s)** -- the variants that exist within the same component set (different inputs, optional features).
- **Exceptional scenario(s)** -- the failure paths through the residual architecture, including which residues handle which failures.

#### 4.2 Activity diagram per use case

PlantUML activity diagram (`\`\`\`plantuml`, `@startuml ... @enduml`; `style-conventions` §6.2) showing the control flow across IDesign layers. Solid arrows for sync calls; dashed for queued / async.

#### 4.3 Residue Mapping table per use case

Critical per R-16: every use case traces back to the residues that shaped its components. Columns:

| Residue # | Type | Relevance to this Use Case |
|---|---|---|

The Residue Mapping makes the dependency explicit: this use case behaves the way it behaves because of these residues. If a use case has zero residues in its mapping, either it does not belong in the SAD or it has been added speculatively (R-09 risk).

#### 4.4 Per-use-case NFRs

NFRs that apply to this use case specifically. Each must have a Source per R-15 (same three valid sources: Coupling Map / Topology / Business residue). Common per-use-case NFRs are subsets of the §Derived NFRs filtered to the components participating in this use case.

### Step 5 -- Produce structural diagrams

The C4 architecture is expressed as **one Structurizr DSL `workspace.dsl`** (R-23), authored in the §Structural Diagrams section as a single fenced ```dsl block. One `model` defines people, the target `softwareSystem`, its `container`s, and their nested `component`s **once**; the `views` block derives each C4 level. The canonical reference for the DSL vocabulary + per-level scope + IDesign tag mapping is `shared/style-conventions.md` §6.1 -- follow it exactly. Because a `component` is nested inside its `container`, level-mixing is structurally impossible; the discipline that remains is (a) never declaring an IDesign component as a `container`, and (b) one `component` view per multi-component container. The §Static Architecture (IDesign) diagram is NOT C4 -- it is a PlantUML component diagram (§5.0, `style-conventions` §6.2). NOTE: do not also emit Mermaid C4 blocks; the workspace is the sole C4 representation.

#### 5.0 Static Architecture (IDesign) -- PlantUML component diagram (not C4)

The Component Taxonomy table + Call Rules table + a PlantUML `\`\`\`plantuml` component diagram of the IDesign layers (the same diagram produced in §2.3). This is NOT a C4 diagram and NOT Mermaid; PlantUML is correct here (`style-conventions` §6.2). The only Mermaid `flowchart` in a SAD is the S1b naive baseline.

#### 5.1 The model and its views (one `workspace.dsl`)

In one `workspace.dsl`:

- **People** -> `person` elements (Clients / external actors).
- **Target system** -> one `softwareSystem` containing all `container`s.
- **Containers** -> one `container` per row of the §Service Grouping Map (S4). The `container` name MUST be the `Service / Deployable Unit` name from that map **verbatim** (S5 reads grouping AND naming from S4; the map is the naming authority, `contagion-analysis` §9.4). Data stores -> tag `"Database"`; queues / buses -> tag `"Queue"`; third-party engines -> `Container_Ext`-equivalent via tag `"External"`. **The Container decomposition is NOT chosen here -- it is read from the §Service Grouping Map (S4, R-25).** Each row's `IDesign components` become the container's nested `component`s; its `Grouping basis` is the Manager's Structural residue # or the promoting operational Topological residue #. If the grouping looks wrong, backtrack to S4 -- do not improvise here.
- **Components** -> one `component` per IDesign Manager / Engine / ResourceAccess / Utility, **nested inside** its container, tagged with its layer (`Manager` / `Engine` / `ResourceAccess` / `Resource` / `Utility` / `Client`). Under the actor-style default (R-25) a Manager service container nests one Manager + its private Engines/RAs; a shared component promoted by an operational Topological residue is its own container.
- **External systems** -> `softwareSystem ... "External"`.
- **Relationships** -> `<source> -> <destination> "<label>" "<technology>"`, source = initiator. These edges must obey the Call Rules (R-03/R-04); the auditor parses them.
- **Deployment** -> a `deploymentEnvironment` nesting `deploymentNode`s (cloud > region > cluster > pod) with `containerInstance`s. **Every deployment-unit boundary traces to a row in the Topological Residue Map (R-19)**; per-jurisdiction residues -> separate top-level nodes.
- **Views** -> declare exactly: one `systemContext <sys>`; one `container <sys>`; one `component <container>` **for every container with 2+ IDesign components** (R-23 coverage, mandatory); one `deployment <sys> <env>`; optionally one `dynamic` per key flow. Every view uses `include *` + `autoLayout`.
- **Styles** -> an IDesign-layer `styles` block (see §6.1) so the render reads as IDesign.

Also produce the **Container table** (feeds coverage + the Container <-> Component mapping): columns `Container` / `Type` (app / service / database / queue / external) / `Role` / `IDesign components inside` / `Grouping basis` (mirrors the §Service Grouping Map row). The `IDesign components inside` column is what determines which containers need a `component` view.

> **The grouping was decided in S4, not here.** One Manager = one service is the actor-style default (R-25). Do NOT collapse all Managers into one monolith, and do NOT give a single-Manager Engine its own container with no operational driver. Either error is an R-25 violation the auditor flags.

#### 5.2 Virtual Actor view (if applicable)

For actor-model systems (e.g., Dapr actors), a supplementary view/table of each actor type, its responsibilities, and the use cases / residues it participates in. Supplements -- does not replace -- the Component views.

### Step 6 -- Hygiene checks before writing the fragment

> **Script-backed (run before parking S5).** `scripts/fragment-checks/check_fragment.py residual-design.md` mechanically enforces the NFR-Source-non-empty (R-15), Taxonomy (R-02), tech-vocab (R-05), and naming (R-06) rows below, and `scripts/fragment-checks/check_counts.py residual-design.md` reconciles any aggregate counts. Run both and fix any hard-fail before the gate; the auditor runs the same scripts.

| Check | Verification | Rule |
|---|---|---|
| Every NFR has a Source | Source column non-empty; reference resolves to existing artifact | R-15 / guardrail #4 |
| Every component traces to a Structural residue | Component name appears in the `Technical Change to Residue (IDesign)` column of at least one Structural residue in the Stressor Catalog (S3). Do NOT verify via the Contagion Matrix: its columns are the Naïve Architecture, so residual components S5 adds never appear there. | R-18 / guardrail #1 |
| Every deployment unit traces to a Topological residue | Deployment Unit Boundaries table row references a valid Topological Residue # | R-19 / guardrail #2 |
| Every use case has a Residue Mapping | Per-use-case Residue Mapping table non-empty; references existing residue numbers | R-16 / guardrail #5 |
| Static Architecture respects R-02 | Every component typed as Manager / Engine / ResourceAccess / Resource / Utility / Client | R-02 |
| Static Architecture respects R-03 | No upward calls; no sideways within layer (except R-04 exceptions) | R-03 |
| R-04 exceptions correctly applied | Utility callers are Manager / Engine / ResourceAccess (not Client, not Resource); Manager-to-Engine is allowed; queued Manager-to-Manager via Pub/Sub Utility allowed | R-04 (with synthesis-tightened R-04 (a)) |
| Naming respects R-06 | Two-part Pascal case + valid suffix for Manager / Engine / Access | R-06 |
| Hygiene respects R-05 | No technology vocabulary in component names | R-05 |
| Manager almost-expendable | Every Manager orchestrates Engines / ResourceAccess; contains no business logic of its own | R-11 |
| Hot Manager evaluated for split | No single Manager has `Σ Column >= 8` with heterogeneous workflows left un-split or un-flagged; the split (if applied) is by volatility cluster (not use case) with queued M-to-M between Managers | This sub-skill, Step 2.5 / R-11 |
| No use case named for a component | No `<UseCaseName>Manager` pattern (functional decomposition disguised) | R-01 / R-16 |
| Hyperliminal Coupling Decouple decisions applied | Every Coupling Map row with response `Decouple` is reflected in the Static Architecture | This sub-skill, Step 3 |
| Representation per kind | The §Static Architecture (IDesign) diagram and every §Behavioral Diagram are `\`\`\`plantuml` blocks (not Mermaid); the only Mermaid `flowchart` allowed is the S1b naive baseline; C4 is the `workspace.dsl` | `style-conventions` §6 / §6.2 |
| C4 expressed as one Structurizr DSL workspace | The §Structural Diagrams section contains a single `workspace.dsl` that validates; no ad-hoc Mermaid C4 blocks. Views declared for System Context, Container, Deployment | R-23 (a) |
| No `container` named after an IDesign component | No `container` element's name/identifier matches a Manager / Engine / ResourceAccess / Utility from the taxonomy; those are nested `component`s | R-23 (b) scope |
| Component-view coverage complete | Every container with 2+ IDesign components has its own `component <container>` view | R-23 (c) coverage |
| C4 Containers trace to the Service Grouping Map | Every Container is one row of the §Service Grouping Map (S4); each Manager is its own service with its private Engines/RAs co-located; shared components in their own Container cite an operational Topological residue; no single-Manager Engine split out without a driver; no all-Managers-in-one monolith | R-25 |
| C4 Container names match the Service Grouping Map verbatim | Every `Container` name equals a `Service / Deployable Unit` name in the §Service Grouping Map (S4) character-for-character; no service renamed or newly coined in S5 | R-25 / naming authority |
| Every Client-facing service has an entry Manager | No Client edge targets an Engine / ResourceAccess / Utility; each service the Client invokes has a Manager owning the entry workflow (identity / security included) | R-03 / R-04 (a) + Step 2.8 |
| Synchronous gates stay on the execution path | A gate (in-line synchronous check) is an Engine co-located with its Manager, never split into another service; only its config is externalized | R-03 + Step 2.7 |
| Cross-service shared Resource is read-only + documented | Any Resource accessed by 2+ services is read-only for non-owners (writes only by the owning Manager) and recorded as a hyperliminal coupling | R-25 + Step 2.7 |

If any deterministic check fails, refuse to write the fragment (see §Refusal conditions).

---

## Output contract

One fragment file in the project workspace:

### `residual-design.md`

Markdown fragment that fills SAD §Derived Non-Functional Requirements (the bottom of §Architectural Stress Analysis) and the entirety of §Analysis and Design. Structure:

1. One paragraph orienting the reader: NFR count, component count by layer, use case count, deployment unit count.
2. **§Derived Non-Functional Requirements** -- the NFR table with three-source traceability.
3. **§Behavioral Diagrams** -- per use case: scenarios, activity diagram, Residue Mapping table, per-use-case NFRs.
4. **§General Non-functional Requirements** -- system-wide NFRs not specific to a use case (still with Source).
5. **§Structural Diagrams** (C4 is one Structurizr DSL workspace -- R-23):
   - **§Static Architecture (IDesign)** -- Component Taxonomy table + Call Rules table + PlantUML `\`\`\`plantuml` component diagram (NOT C4, NOT Mermaid; `style-conventions` §6.2).
   - **§C4 Model** -- a single fenced ```dsl block holding the `workspace.dsl`: the `model` (people, the target `softwareSystem` with its `container`s nesting `component`s tagged by IDesign layer, external systems, relationships, deployment) and the `views` (one `systemContext`; one `container`; one `component <container>` per Container with 2+ IDesign components -- R-23 coverage, mandatory; one `deployment`; optional `dynamic`) plus an IDesign-layer `styles` block.
   - **§Container <-> Component mapping** -- the Container table (with the `IDesign components inside` column) that determines coverage.
   - **§Virtual Actor view** -- if applicable.
   - **§Deployment Unit Boundaries** -- the table tracing each deployment node to a Topological Residue # (the `deployment` view above visualizes it).

No frontmatter.

---

## Refusal conditions

| # | Trigger | Rule | Returned message |
|---|---|---|---|
| 1 | `contagion-analysis.md` does not exist or is unapproved. | Pre-condition | Refuse. Direct the user to run / approve `contagion-analysis` (S4) first. |
| 2 | Hyperliminal Coupling Map has rows with non-decisive Architectural Response. | Pre-condition | Refuse. S4 must close every coupling row before S5 begins. Direct the user back to S4. |
| 3 | An NFR has empty Source. | R-15 / guardrail #4 | List the offending row. Either trace the NFR to a Coupling Map row / Topology row / Business residue, or drop it as boilerplate. |
| 4 | An NFR has a Source reference that does not resolve to an existing upstream row. | R-15 traceability | List the offending row. The Source must point to a real artifact in contagion-analysis. |
| 5 | A component in the Static Architecture has no Structural residue justifying it. | R-18 / guardrail #1 | List the offending component. Either add the Structural residue to the catalog (backtrack to S3 -> S4), or remove the component. |
| 6 | A deployment unit boundary has no Topological residue reference. | R-19 / guardrail #2 | List the offending boundary. Either add the Topological residue (backtrack to S3 -> S4), or remove the boundary. |
| 7 | A use case is missing a Residue Mapping subsection or it is empty. | R-16 / guardrail #5 | List the offending use case. Add the mapping or remove the use case. |
| 8 | A component has a name in non-Pascal-case or with invalid suffix. | R-06 | List the offending names; propose conforming alternatives. |
| 9 | A component name contains technology vocabulary. | R-05 | List the offending names; propose volatility-named alternatives. |
| 10 | The Call Rules table allows Client -> Utility, Client -> Engine, Client -> ResourceAccess, Resource -> Utility, or any upward call. | R-03 / R-04 (a) tightened | Reject. Update the Call Rules table to match `shared/idesign-vocabulary.md` §3. |
| 11 | A Manager contains business logic (calculation / rule / transformation). | R-11 | List the offending Manager. Move the logic into an Engine. |
| 12 | A use case is the source of a decomposition decision (a component exists "because the use case needs it"). | R-16 / R-01 | Refuse. Trace the component to a residue or remove it. Use cases document; they do not drive. |
| 13 | A Decouple decision from the Coupling Map is not applied in the Static Architecture. | This sub-skill, Step 3 | List the offending coupling row. Either apply the decoupling, or backtrack to S4 to re-evaluate the response. |
| 14 | An Engine calls another Engine, a ResourceAccess calls another ResourceAccess, or two Managers call synchronously. | R-03 | Refuse. Reframe via legitimate exception (R-04) or restructure. |
| 15 | C4 architecture is authored as Mermaid C4 / `flowchart` blocks instead of one Structurizr DSL `workspace.dsl`. | R-23 (a) | Reject. All C4 architecture is a single `workspace.dsl` (one model -> derived `systemContext` / `container` / `component` / `deployment` views). See `shared/style-conventions.md` §6.1. The §Static Architecture IDesign diagram is PlantUML (§6.2) and the §Behavioral Diagrams are PlantUML; the only Mermaid in a SAD is the S1b naive baseline (§6). |
| 16 | The §C4 Model `workspace.dsl` declares a `container` named after an IDesign component (Manager / Engine / ResourceAccess / Utility). | R-23 (b) level-mixing | Reject. Those are nested `component`s, not containers. Move them inside the relevant service `container` (shown in that container's `component` view). A container is a separately deployable unit; splitting one service into per-component containers also requires a Topological residue (R-19). |
| 17 | A `container` with 2+ IDesign components has no corresponding `component <container>` view. | R-23 (c) coverage | List the offending container. Produce its `component` view. |
| 18 | The container decomposition in the `workspace.dsl` does not match the §Service Grouping Map: a single-Manager Engine has its own container with no driver, or all Managers are collapsed into one monolith, or a shared component is split out without an operational Topological residue. | R-25 | The grouping is decided in S4, not S5. One service `container` per §Service Grouping Map row: one Manager service each (private Engines/RAs co-located), shared components promoted only with an operational driver. Backtrack to S4 to fix the map if needed. |
| 19 | A Client-facing capability is wired Client -> Engine / RA / Utility with no entry Manager. | R-03 / R-04 (a) + Step 2.8 | Add an entry Manager that owns the workflow and orchestrates the Engine + RA. Identity / security is not an exception; a Utility is not an entry point. |
| 20 | A gate (synchronous in-line check) is split into its own service, OR a shared Resource is written by more than one service. | R-03 + R-25 + Step 2.7 | Keep the gate co-located on the execution path (Engine inside its Manager); externalize only its config to a read-only shared Resource; writes stay with the owning Manager. |

---

## Worked example

See `sad/examples/ev-charging-sad.md` for a complete worked example. Key features:

- **§8 Derived NFRs** -- 8 NFRs, each with a Source: matrix rows (Resumable charge session traces to row 9b; Auth/billing independence traces to row 3 across AuthEng / BillingEng / BillingMgr), topology row 13 (per-country data residency), and business residues #5 / #6 (capacity provisioning, operational diversification readiness).
- **§Static Architecture** -- residual decomposition has `ChargeSessionManager`, `ALPRManager`, `BillingManager`, `OverstayManager`, `LegalCaseManager` as Managers; `AuthEngine`, `ALPREngine`, `BillingEngine`, `OverstayEngine`, `JurisdictionEngine`, `PowerEngine`, `DamageDetectionEngine` as Engines; multiple ResourceAccess components (`CustomerAccess` per-country, `ChargerAccess`, `CameraAccess`, `SensorAccess`, `BatteryAccess`, `PaymentProcessorAccess`).
- **§Deployment Diagram** -- per-country deployment unit boundary traces to Topological Residue #13.
- **Manager-to-Manager via Dapr Pub/Sub** (R-04 (d)) -- `ChargeSessionManager` emits `ChargeCompleted`; `BillingManager` subscribes; no sync M-to-M.

---

## Why these rules

- **R-15.** NFR traceability is the empirical link between the contagion analysis and the architecture. NFRs without source are boilerplate; they describe wishes, not contracts.
- **R-18 + R-19.** Component / deployment-unit traceability prevents speculative design (R-09) from sneaking in at the design stage. Every architectural element earns its existence from a stressor.
- **R-16.** Use cases as documentation rather than driver keeps the architecture residue-based. Use-case-driven design produces architectures that fragment as the business behavior shifts.
- **R-02 / R-03 / R-04.** The IDesign discipline at this stage IS the P-raising mechanism (per `shared/kauffman-nkp.md` §5). It is the structural reason the residual architecture is more critical than the naïve one.
- **R-11.** Manager almost-expendable is the second-order check on residue quality. A Manager that grows business logic is absorbing stress that should be elsewhere.

---

## References

- `shared/constitution.md` -- R-01, R-02, R-03, R-04 (with R-04 (a) tightening), R-05, R-06, R-07, R-09, R-11, R-12, R-15, R-16, R-18, R-19.
- `shared/idesign-vocabulary.md` -- the canonical four layers + Utilities Bar, taxonomy, call rules, IDesign override.
- `shared/decomposition-discipline.md` -- guardrails #1, #2, #4, #5.
- `shared/glossary.md` -- vocabulary used throughout the residual design.
- `sad/template.md` §Derived Non-Functional Requirements, §Analysis and Design (Behavioral Diagrams, General NFRs, Structural Diagrams) -- the SAD sections this sub-skill fills.
- `sad/synthesis-explanation.md` §6 Decisions 4 (NFR traceability) and 5 (use cases as documentation).
- `sad/examples/ev-charging-sad.md` §8 (Derived NFRs), §10 (Residual Architecture Summary) -- worked example.
- `residuality/residuality-md/residuality.md`:
  - L1082-1120 -- hyperliminal coupling as source of NFRs.
  - L1114-1120 (literal) -- hidden couplings ARE non-functional requirements.
- `righting-software-md/righting-software-juval-lowy-only-need.md`:
  - L981-1075 -- the four layers.
  - L1027 (Manager / Engine definition).
  - L1085-1105 (naming).
  - L1107-1129 (four questions for validation).
  - L1163-1171 (almost-expendable Manager).
  - L1281-1351 (closed architecture + relaxing the rules).
