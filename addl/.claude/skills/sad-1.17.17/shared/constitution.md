---
title: Constitution -- Software Architecture Document meta-skill
version: 1.0
date: 2026-05-09
---

# Constitution

Single source of truth for the rules enforced by the `sad` meta-skill. Every sub-skill cites by `R-NN`. The `sad-auditor` sub-skill enforces these rules at every gate.

When a rule appears to conflict with anything else in the repository, this file wins.

## How to read a rule

Each rule has:

- **Statement.** One-sentence claim.
- **Mechanism.** `deterministic` (mechanically verifiable), `heuristic` (requires LLM judgment), or `both`. Determines the auditor's approach.
- **Body.** Explanation of scope, motivation, edges.
- **Verification.** How to detect a violation.
- **Citations.** Source: book `L#-L#` (Lowy = `righting-software-md/righting-software-juval-lowy-only-need.md`; O'Reilly = `residuality/residuality-md/residuality.md`) or guardrail `#` from `sad/template.md` §Restrictions §Decomposition Discipline.
- **Valid example** + **Anti-example.** At least one of each, drawn from the EV charging worked example where possible.
- **Walkthrough** (optional). Worked illustration for complex rules.

The numbering R-01 to R-27 is intentionally non-contiguous: R-08 is reserved/dropped from the prior federation (the smallest-set numeric heuristic) and replaced empirically by R-18. With R-08 absent, there are 26 active rules.

---

## Section 1 -- Decomposition principles

### R-01. The Golden Rule -- decompose by residue, not by function

**Statement.** Decompose the system into components organized around residues (units of architectural change under stress), not around functions, processes, use cases, or business domains.

**Mechanism.** `heuristic`.

**Body.** A residue is what is left of an architecture after exposure to a stressor (O'Reilly L406-413). The architecture is the integration of all residues identified through stressor analysis. Volatility-based decomposition (Lowy L477-479) is the historical predecessor; it is preserved as one signal among several but the unit of decomposition is now the residue. Every component must justify its existence by tracing to one or more Structural residues in the Stressor Catalog (see R-18). Functional decomposition couples components to requirements (Lowy L165, L505) and produces architectures that fail when business behavior shifts; residue-based decomposition contains change inside the affected residue.

**Verification.** For each component, ask: which residue justifies it? If the answer is "use case X" or "feature Y", the rule is violated.

**Citations.** Lowy L477-505 (volatility-based decomposition), L161-205 (functional decomposition trap). O'Reilly L406-413 (residue as unit), L514-540 (architecture as collection of residues).

**Valid example.** EV charging: `ChargerAccess` exists because residue #1 (new car models) and the hot-column reading on the Contagion Matrix justify a polymorphic hardware abstraction.

**Anti-example.** EV charging: a `StartChargingFeature` component would couple the architecture to one specific use case; if the use case changes, the component name and responsibilities decay.

---

### R-22. The architect's mindset is lateral; correctness is the developer's mindset

**Statement.** The architect's primary cognitive mode is lateral thinking -- comfort with being wrong, exploration of differences, imagination over definition. Linear thinking (precision, exact correctness, fixation on definitions) is necessary but secondary; without lateral dominance it cannot produce architecture in complex contexts.

**Mechanism.** `heuristic`.

**Body.** Per O'Reilly L1378-1470 (the Linear and Lateral Thinking chapter): the senior architect gap is not technical skill but cognitive mode. "For the mythical 10X developer, 9X is lateral thinking" (L1427-1428). The same chapter rules (L1431-1432): "Anyone who has mastered lateral thinking without linear thinking will not be able to produce good architecture." Linear thinking is necessary scaffolding; lateral thinking is the dominant mode. The meta-skill's sub-skills assume lateral dominance -- an architect operating in linear-only mode will execute the workflows mechanically and produce output that technically passes the auditor but fails to reach criticality. This rule makes the mode requirement explicit so junior architects recognize when they are reading the docs through the wrong lens. `shared/architectural-walking.md` is the canonical reference for the cognitive mode; this rule names it as non-negotiable.

**Verification.** Heuristic. Look for: definitions defended past stressor evidence ("but the PRD says Customer means X"); fixation on "the correct decomposition" instead of "what could break this decomposition"; treatment of refusal conditions as checklist items; one-liner stressors and one-liner residue justifications (lateral mode produces narratives); resistance to iteration ("we already analyzed this").

**Citations.** O'Reilly L1378-1470 (Linear and Lateral Thinking), L1427-1428 (10X = 9X lateral), L1431-1432 (lateral without linear fails), L1450-1452 (consistently wrong until less wrong), L1129-1278 (Architectural Walking).

**Valid example.** Stressor analysis session: an architect generates 20 stressors via PESTLE, then pauses and says "I do not yet feel I understand how this business works under stress" and runs a second pass with abstraction-stressing on the Customer entity. The second pass produces 8 more stressors that the first pass would have missed. The architect is operating in lateral mode -- the framework is the structure; the unease is the walk. Compliant.

**Anti-example.** Same session, different architect: generates 20 stressors via PESTLE, marks the catalog complete, refuses to do the abstraction-stressing pass because "PESTLE is a recognized framework and we have used it". The architect is in linear mode -- treating the framework as a checklist. R-22 violation. The downstream Contagion Matrix will be thin and the Ri test will likely produce a value close to zero.

---

### R-21. The architect's goal is criticality, not correctness

**Statement.** Architectural decisions optimize for survival under unknown stress (criticality), not for perfect handling of known requirements (correctness).

**Mechanism.** `heuristic`.

**Body.** Criticality is the Kauffman-network state where N (component count), K (link count), and P (component bias toward predictable behavior) are balanced such that the system survives unknown stress without collapsing under management of its own resources (O'Reilly L807-846). Correctness is the goal of the developer and the mathematician (O'Reilly L859-861). Conflating the two leads architects to over-specify edge cases for known stressors and miss the structural moves that protect against unknown ones. The empirical Ri test (R-15 source for "Empirical Test" rows; see also `template.md` §Empirical Test) is the only mechanism that lets this rule be falsified per project.

**Verification.** Heuristic. Look for: design conversations dominated by edge-case enumeration (correctness symptom) without corresponding stressor analysis (criticality symptom). Look for: an Empirical Test section omitted from the SAD.

**Citations.** O'Reilly L807-867 (criticality), L859-861 (literal: "The goal of the architect is criticality, not correctness").

**Valid example.** EV charging residue #3 (broken key fob) added an entire ALPR subsystem -- arguably "over-engineered" for the specific stressor. But the Combined residues (#14 ICE-ing, #15 AFIR) survive for free because of it. Criticality paid off.

**Anti-example.** A SAD that lists 30 edge cases per use case but has no Stressor Catalog and no Empirical Test section.

---

## Section 2 -- IDesign service hierarchy

### R-02. Service hierarchy

**Statement.** Every component in the Static Architecture is typed as exactly one of: Manager, Engine, ResourceAccess, Resource, Utility, Client.

**Mechanism.** `deterministic` (schema check on Static Architecture component table).

**Body.** Lowy L981-1077 defines the four-layer architecture plus the Utilities Bar. Manager components encapsulate sequence (workflow) volatility and are stateful per workflow instance (Lowy L1027). Engine components encapsulate activity volatility and are stateless (Lowy L1027). ResourceAccess components encapsulate access to a Resource and are stateless; the contract exposes atomic business verbs (Lowy L1049-1063, see R-07). Resources are the actual physical state holders -- databases, queues, file systems, external systems (Lowy L1069-1071). Utilities are cross-cutting infrastructure callable from any layer (Lowy L1073-1075). Clients are entry points: end-user apps or other systems (Lowy L985-1003).

**Verification.** Schema: every row in the Static Architecture component taxonomy table has `type in {Manager, Engine, ResourceAccess, Resource, Utility, Client}`.

**Citations.** Lowy L981-1077 (the four layers), L1027 (Manager / Engine definitions), L1049-1063 (ResourceAccess), L1069-1071 (Resource), L1073-1075 (Utility), L985-1003 (Client). Synthesis: `template.md` §Static Architecture (IDesign) Component Taxonomy table.

**Valid example.** EV charging: `ChargeSessionManager` (Manager), `AuthEngine` (Engine), `ChargerAccess` (ResourceAccess), `Charger hardware` (Resource), Pub/Sub Dapr (Utility), customer's mobile app (Client).

**Anti-example.** EV charging: a `CustomerService` component without a layer assignment -- ambiguous between Manager (workflow over customers) and Engine (customer matching logic).

---

### R-03. Closed architecture

**Statement.** Calls go top-down to the layer immediately below; no calling up; no sideways calls within a layer.

**Mechanism.** `deterministic` (graph check on Call Rules table + sequence diagrams).

**Body.** The closed architecture (Lowy L1293-1295) trades flexibility for encapsulation. Synchronous Manager-to-Manager is forbidden (Lowy L1283-1289). Engine-to-Engine is forbidden (Lowy L1391). ResourceAccess-to-ResourceAccess is forbidden (Lowy L1393). Upward calls (Engine to Manager, ResourceAccess to Engine, Resource to anything) are forbidden. The four legitimate exceptions are codified in R-04. Within Business Logic both Managers and Engines may call ResourceAccess (Lowy L1329-1331); this is standard, not an exception.

**Verification.** Graph traversal: build the directed call graph from the Call Rules table and any sequence diagrams; flag any edge that violates top-down-only or appears within a layer (subject to R-04).

**Citations.** Lowy L1281-1295 (closed architecture), L1283-1289 (no sync M2M), L1329-1331 (BL to RA standard), L1361-1393 (Design Don'ts).

**Valid example.** EV charging: `ChargeSessionManager -> AuthEngine -> CustomerAccess -> CustomerDB`. Top-down only.

**Anti-example.** `AuthEngine -> ChargeSessionManager` (calling up); `BillingEngine -> AuthEngine` (sideways within Engines); `OverstayManager -> BillingManager` synchronously (sideways within Managers; must use Pub/Sub per R-04).

---

### R-04. Relaxing the rules -- four legitimate exceptions

**Statement.** The closed architecture admits exactly four exceptions: (a) Utilities are callable by Manager / Engine / ResourceAccess (Clients and Resources do not call Utilities), (b) Managers and Engines both call ResourceAccess (standard within BL, see R-03), (c) Manager-to-Engine is not a sideways call (Engines are Strategy pattern in an orthogonal plane), (d) Queued Manager-to-Manager via a queue Resource.

**Mechanism.** `both` -- deterministic for (a) and (d); heuristic for (b) and (c) when ambiguity exists.

**Body.** (a) Utilities pass the cappuccino-machine litmus test (Lowy L1325-1327): if the component could plausibly be used in any other system (security, logging, pub/sub), it is a Utility. Synthesis stricter rule: Utilities are internal infrastructure called by Manager / Engine / ResourceAccess only. Clients (entry points) do not call Utilities -- a Client that did so would leak system concerns and conflict with Lowy L1381 (Clients do not publish events). Resources do not call Utilities -- they are passive. (b) Standard within Business Logic per R-03. (c) Manager-to-Engine is not sideways because Engines are an orthogonal plane (Lowy L1333-1335). (d) Queued Manager-to-Manager (Lowy L1337-1351): the proxy is a ResourceAccess to the queue Resource (call DOWN), and the queue listener is another Client (call DOWN to receiving Manager); semantically justified for use cases that trigger latent execution of other use cases. Any other apparent violation must be reframed using one of these four; pure violations are R-03 violations, not R-04 exceptions.

**Verification.** For each call that crosses or stays within a layer in a way that would otherwise violate R-03: confirm it matches one of the four exceptions and the matching context (Utility / BL-to-RA / M-to-E / queued M-to-M). Heuristic check on (b) and (c): is the receiver actually a Utility / Engine?

**Citations.** Lowy L1311-1351 (relaxing the rules), L1325-1327 (cappuccino test), L1329-1331 (BL to RA), L1333-1335 (M to E), L1337-1351 (queued M to M).

**Walkthrough (EV charging).** `ChargeSessionManager` posts `ChargeCompleted` event to the Dapr Pub/Sub Utility (R-04a). `BillingManager` consumes `ChargeCompleted` from the same Utility (R-04d -- listener is a Client, the Pub/Sub Utility is the queue Resource family). Result: no synchronous Manager-to-Manager call ever happens; the closed architecture is preserved.

**Anti-example.** `OverstayManager` synchronously calling `BillingManager.WaiveFee()` -- this is sideways and synchronous, not queued. Even if intentional, it violates R-03 and is not covered by R-04d.

---

## Section 3 -- Naming and decomposition hygiene

### R-05. Decomposition hygiene -- no technology vocabulary in component names

**Statement.** Component names must not contain technology, framework, or infrastructure vocabulary (Lambda, SQS, Kubernetes, Postgres, gRPC, Lambda, REST, Kafka, etc.).

**Mechanism.** `deterministic` (regex on component table + diagram labels).

**Body.** Component names express axes of architectural change, not the implementation technology used at this point in time. A component named `LambdaInvoker` or `SQSQueueProcessor` is coupled to its current technology; when the technology shifts, either the name lies or the component must be renamed. Components named for residues (e.g., `BillingManager` for the billing residue) survive technology change.

**Verification.** Regex check against a forbidden-vocabulary list (case-insensitive): aws, azure, gcp, lambda, sqs, sns, kafka, kubernetes, k8s, docker, postgres, mysql, mongodb, redis, dapr (in Manager/Engine/RA names; allowed in Utility names like `DaprPubSub`), grpc, rest, http, websocket, etc.

**Citations.** Lowy L1085-1089 (naming as compound noun + suffix), guardrail-adjacent.

**Valid example.** `ChargerAccess` (encapsulates volatility of accessing the charger as a resource).

**Anti-example.** `ChargerRESTAPIAccess`, `ChargerHTTPAccess`, `ChargerKafkaConsumer`. Each ties the name to current transport.

---

### R-06. Naming convention -- two-part Pascal case with valid suffix

**Statement.** Service names are two-part compound words in Pascal case. The suffix is exactly one of: `Manager`, `Engine`, `Access`. Resource and Utility names follow domain conventions (no required suffix beyond what is conventional for the underlying technology).

**Mechanism.** `deterministic` (regex).

**Body.** Lowy L1085-1105 codifies the naming rules. Manager prefix is a noun for the volatility encapsulated in use cases (e.g., `ChargeSession` in `ChargeSessionManager`). Engine prefix is a noun describing the encapsulated activity, often a gerund (e.g., `Auth` in `AuthEngine`, `Calculating` in `CalculatingEngine`). ResourceAccess prefix is a noun for the Resource or its data (`Customer` in `CustomerAccess`).

**Verification.** Regex per type: `^[A-Z][a-z]+([A-Z][a-z]+)*Manager$` for Managers; same with `Engine` or `Access`. Component table validation.

**Citations.** Lowy L1085-1105.

**Valid example.** `ChargeSessionManager`, `AuthEngine`, `CustomerAccess`.

**Anti-example.** `ChargeSession_Manager` (snake_case), `chargeSessionManager` (camelCase), `ChargeSessionMgr` (abbreviated suffix), `BillingService` (wrong suffix).

---

### R-07. Atomic business verbs only in ResourceAccess contracts

**Statement.** Atomic business verbs (e.g., `Credit`, `Debit`, `StartCharge`, `StopCharge`) appear only as operations on ResourceAccess contract interfaces. They never appear as service name prefixes; never as Manager workflow names.

**Mechanism.** `both` -- deterministic for service name regex; heuristic for whether a verb is "atomic business" or already too granular.

**Body.** Atomic business verbs are immutable because they relate to the nature of the business (Lowy L1055-1059). They belong in the contract that the ResourceAccess exposes to Business Logic, where they are translated into CRUD/IO against the Resource. Putting an atomic verb in a service name (e.g., `ChargeBillingManager`) reveals functional decomposition: the service is named for what it does, not for the volatility it encapsulates.

**Verification.** Regex: no service name starts with a known business verb. Heuristic: review ResourceAccess contracts and confirm each operation name is an atomic business verb.

**Citations.** Lowy L1055-1059 (atomic verbs immutable), L1101-1105 (gerunds outside Engines indicate functional decomposition).

**Valid example.** `ChargerAccess.StartCharge()`, `ChargerAccess.StopCharge()`, `ChargerAccess.Unlock()`.

**Anti-example.** `StartChargeManager` (verb as Manager prefix); `ChargingEngine` may be borderline -- if it contains the activity of charging it is fine; if it contains the workflow of charging it should be a Manager.

---

## Section 4 -- Anti-design rules

### R-09. No speculative design

**Statement.** Do not encapsulate volatilities or stressors that have no narrative basis in the analysis -- do not "design for the future" by adding components that no residue justifies.

**Mechanism.** `heuristic`.

**Body.** Lowy L815-823 calls this Speculative Design and warns against encapsulating phantom changes (the SCUBA shoes example). O'Reilly L1014-1052 reframes the same trap as instinctive over-engineering -- adding microservices, dependency injection, or generic abstractions as a default response to unknown futures, instead of running the stressor analysis that would tell you which abstractions are actually justified. Speculative design is correctly framed as the absence of stressor analysis, not the presence of too much analysis.

**Verification.** Heuristic. For each component lacking a Structural residue (R-18 violation), confirm whether the component was added speculatively. For each NFR that traces only to "future-proofing" with no residue source, raise R-09.

**Citations.** Lowy L815-823 (Speculative Design). O'Reilly L1014-1052 (over-engineering as anti-pattern).

**Valid example.** EV charging: residue #2 (electricity failure) justifies `BatteryAccess`. The component exists because a stressor was identified, not because batteries are "the future".

**Anti-example.** Adding a `MachineLearningEngine` to the EV charging architecture because "ML is the future" -- no residue justifies it.

---

### R-10. No solutions masquerading as requirements

**Statement.** When a stakeholder presents a requirement, identify whether it is a real requirement or a solution disguised as one. Encapsulate the underlying volatility, not the proposed solution.

**Mechanism.** `heuristic`.

**Body.** Lowy L687-701 illustrates with the cooking example: "we need a kitchen" is a solution; the requirement is "feeding the people in the house"; the deeper requirement is "well-being of the occupants". Encapsulating the solution couples the architecture to a specific implementation; encapsulating the volatility leaves the architecture composable. The technique is to point out the masquerade and ask: are there other possible solutions?

**Verification.** Heuristic. For each Manager / Engine: does the component name describe a volatility or a specific solution? Cross-check stakeholder requirements against the Stressor Catalog -- if a requirement was added to the catalog without a stressor reframing, flag for review.

**Citations.** Lowy L687-701.

**Valid example.** EV charging stressor #3 is "key fob breaks". The architectural response was not "make the key fob more durable"; it was an alternative auth path (ALPR) which decouples authentication from billing.

**Anti-example.** Stakeholder says "we need a 24/7 customer support call center"; the architecture adds a `CallCenterManager`. The real requirement is "customer can resolve issues when they arise"; the call center is one solution.

---

### R-11. Almost-expendable Manager

**Statement.** Each Manager is almost expendable: it orchestrates Engines and ResourceAccess and encapsulates sequence volatility, with no business logic of its own beyond the workflow.

**Mechanism.** `heuristic`.

**Body.** Lowy L1163-1171 describes three Manager qualities: expensive (you fight changes -- functional decomposition smell), expendable (pass-through with no value -- design distortion), almost-expendable (workflow holder, easy to adapt). The rule says: aim for almost-expendable. A Manager that contains pricing rules, calculation logic, or external API parsing is doing the job of an Engine or a ResourceAccess.

**Verification.** Heuristic. For each Manager: list the activities inside it. Are they workflow steps (load, call, persist, post) or business activities (calculate, validate, transform)? The latter belong in Engines.

**Citations.** Lowy L1163-1171.

**Valid example.** EV charging: `ChargeSessionManager` orchestrates `AuthEngine.Authenticate -> ChargerAccess.StartCharge -> ... -> ChargerAccess.Unlock`. It does no charging itself.

**Anti-example.** `ChargeSessionManager` contains a method `CalculatePrice(kwh)` that applies tariffs. Pricing is a business activity; it belongs in `BillingEngine`.

---

### R-12. Interface stability

**Statement.** Interfaces (especially ResourceAccess contracts and Manager public operations) are stable; implementations behind them are volatile.

**Mechanism.** `heuristic`.

**Body.** Lowy L1055-1059 anchors this on atomic business verbs being practically immutable. The reason interfaces stay stable is that they are tied to the nature of the business (credit, debit, charge, unlock); the implementation can change with technology, regulation, or scale without breaking the contract. This is also the canonical Kauffman P (predictability bias): stable contracts raise P and reduce the system's effective K, contributing to criticality (R-21).

**Verification.** Heuristic. Compare contract operations across iterations -- if they churn frequently, either the contract was wrong (atomic verbs missed) or the implementation is leaking through.

**Citations.** Lowy L1055-1059. O'Reilly L832-836 (interfaces raise P).

**Valid example.** `ChargerAccess.StartCharge(sessionId)` survives a switch from REST to gRPC, from on-premises to cloud, from a single charger model to polymorphic charger models. The contract reflects business intent; the implementation is replaceable.

**Anti-example.** `ChargerAccess.SendPostRequestToChargerAPI(payload)` -- implementation leaks into the contract. Switching transports breaks consumers.

---

## Section 5 -- Stressor analysis discipline

### R-13. Stressors are typed

**Statement.** Every entry in the Stressor Catalog has a Type column with exactly one of: `Structural`, `Topological`, `Business`, `Combined`. The type determines which downstream subsection the stressor feeds.

**Mechanism.** `deterministic` (schema check on Stressor Catalog table).

**Body.** Synthesis decision 2. The four types correspond to four kinds of architectural response: Structural drives a change in IDesign components or call topology and feeds the Contagion Matrix; Topological drives a change in deployment topology and feeds the Topological Residue Map; Business produces a business decision but no software change and feeds the Business Residues Log; Combined is a stressor already survived by an existing combination of residues and feeds the Looping Signals table. Without typing, business and topological residues either get dropped from the catalog or get forced awkwardly into the Contagion Matrix.

**Verification.** Schema: every row in the Stressor Catalog has `Type in {Structural, Topological, Business, Combined}`. Untyped or mistyped rows are violations.

**Citations.** `synthesis-explanation.md` §6 Decision 2. `template.md` §Stressor Catalog. Guardrail # (typing is implicit in guardrails 1, 2, 3, 8).

**Valid example.** EV charging: stressor #3 (failed login) is Structural; #13 (privacy regulation) is Topological; #4 (EV market crash) is Business; #14 (ICE-ing) is Combined.

**Anti-example.** A stressor catalog where "EV market crash" appears in the Contagion Matrix as a row with all zeros -- it should have been typed Business and routed to the Business Residues Log.

---

### R-17. Combined residues are recorded as Looping Signals

**Statement.** When a new stressor is already survived by a combination of existing residues, it is recorded as a Combined-typed entry in the Stressor Catalog AND in the Looping Signals table with explicit "survived by combination of #X, #Y, #Z" trace.

**Mechanism.** `deterministic` (schema check on Looping Signals table) + `heuristic` (whether the combination genuinely survives the stressor).

**Body.** Synthesis decision 6. Looping is the empirical signature of approaching criticality (O'Reilly L1812-1816). The book treats it as narrative observation; the synthesis treats it as a structured artifact. Combined residues are the strongest persuasive material in the SAD -- they are the moments where the architecture absorbs an unforeseen stressor for free. Hiding them in prose loses the evidence.

**Verification.** Schema: every Combined-typed stressor has a corresponding row in Looping Signals with non-empty `Survived by Combination of` column referencing valid residue numbers.

**Citations.** `synthesis-explanation.md` §6 Decision 6. `template.md` §Looping Signals. Guardrail #8. O'Reilly L1812-1816, L1819-1840 (mathematical leverage).

**Valid example.** EV charging: stressor #15 (AFIR 2023 mandates credit-card payment) is recorded as Combined, survived by combination of #3 (auth/billing decoupling). The auth/billing decoupling was added for a broken plastic key fob ten years earlier; AFIR was absorbed without architectural rewrite.

**Anti-example.** A SAD where stressor #15 is mentioned only in a closing paragraph as "we got lucky on AFIR"; no Looping Signals row, no trace, no reusable evidence.

---

### R-18. No structural component without a Structural residue

**Statement.** Every component that appears in the Static Architecture must trace to one or more Structural residues in the Stressor Catalog. Components without traceable residue are rejected.

**Mechanism.** `deterministic` (cross-reference check between Static Architecture component table and Contagion Matrix columns).

**Body.** Guardrail #1 of the Decomposition Discipline. This rule replaces the prior R-08 (Lowy's smallest-set numeric heuristic of "8+ Managers = fail"). The replacement is empirical: instead of arbitrating component count by a number, we require each component to be empirically motivated by a residue. The result is a smaller, justified component set without an arbitrary cap.

**Verification.** For each row in the Static Architecture component taxonomy table, find the column in the Contagion Matrix with the same component name. The column must have at least one `1` entry pointing to a Structural-typed residue.

**Citations.** `synthesis-explanation.md` §6 Decision 7, guardrail #1. `template.md` §Restrictions §Decomposition Discipline rule 1.

**Valid example.** EV charging: `OverstayManager` exists because residue #12 (customer abandons car in slot) is Structural and motivates it. Cell `(stressor 12, OverstayManager)` is `1`.

**Anti-example.** Adding `LoyaltyManager` to the Static Architecture without any stressor in the catalog mentioning loyalty programs. R-18 violation; either add the residue or remove the component.

---

### R-19. No deployment unit without a Topological residue

**Statement.** Every deployment unit boundary in the Deployment Diagram must trace to one or more Topological residues in the Topological Residue Map.

**Mechanism.** `deterministic` (cross-reference check).

**Body.** Guardrail #2. Deployment topology is not a free architectural variable; each boundary carries cost, complexity, and cross-boundary constraints. Without a Topological residue justifying the boundary, the deployment decision is speculative. Topological residues come in two families, both valid drivers of a deployment boundary:

- **Geographic / jurisdictional** -- geography, tenancy, replication, latency zone, sovereignty. These answer *where* a unit runs.
- **Operational** -- `independent-scaling`, `failure-isolation` (blast-radius), `change-cadence`, `resource-profile`, `security-zone`. These answer *which shared components must run as a separate process*. Note the interaction with R-25: under the repo's actor-style default, each Manager is already its own service (no operational residue needed for that). Operational residues do their work on **shared Engines/ResourceAccess** (used by 2+ Managers) -- they justify promoting a shared component to its own service rather than duplicating it -- and on the rare case of co-locating Managers.

**Verification.** For each deployment unit boundary in the Deployment Diagram, the corresponding row in the Deployment Unit Boundaries table must reference a valid Topological Residue # (geographic or operational) from the Topological Residue Map. Per-Manager service boundaries trace to the Manager's own Structural residue (R-18 / R-25), not to a separate Topological residue.

**Citations.** `template.md` §Restrictions §Decomposition Discipline rule 2. `template.md` §Topological Residue Map and §Deployment Diagram §Deployment Unit Boundaries. O'Reilly L1940-1943 (same stress profile -> combine, applied within a Manager cluster per R-25), L2556-2558 (over-granular separations that don't help -> less granularity).

**Valid example.** EV charging: per-country deployment boundary traces to Topological Residue #13 (privacy regulation requires customer data within home country) -- a geographic driver. Operational example: a shared `RatingEngine` used by two Managers is promoted to its own service by an `independent-scaling` operational residue (it absorbs spikes independently), rather than being duplicated.

**Anti-example.** Splitting deployment by AWS region "for performance" without a Topological residue justifying the split. R-19 violation. (Note: giving each Manager its own service is NOT an R-19 violation -- under R-25 that is the actor-style default, justified by each Manager's own Structural residue, not by a Topological one.)

---

### R-20. No probability or cost discussion before matrix closure

**Statement.** No column or annotation for `Probability`, `Likelihood`, `Risk Score`, `Cost`, or equivalent appears in the Stressor Catalog or the Contagion Matrix at any point before the matrix is complete and the Empirical Test is run.

**Mechanism.** `deterministic` (schema check on column headers).

**Body.** Guardrail #6. O'Reilly L1763-1768 is explicit: "No use of probability. All stressors must go in the list, no matter how ridiculous." Probability and cost filter the catalog and bias the matrix toward consensus and "likely" scenarios -- exactly the failure mode the random simulation is designed to avoid (O'Reilly L660-669, the curse of high dimensionality and patchy human samples). Probability and cost re-enter later, in FMEA and ATAM (O'Reilly L1958-2000), once the structural analysis is complete.

**Verification.** Schema: regex on Stressor Catalog and Contagion Matrix column headers for forbidden terms.

**Citations.** `synthesis-explanation.md` §6 Decision 7. `template.md` §Restrictions §Decomposition Discipline rule 6. O'Reilly L1763-1768, L1786-1792.

**Valid example.** EV charging Stressor Catalog has columns: Type, Stressor, Detection, Attractor, Business Reaction, Technical Change. No probability column.

**Anti-example.** A Stressor Catalog with a Likelihood column ranked 1-5; entries with Likelihood ≤ 2 silently dropped. Three of the most valuable EV charging residues (#3 broken key fob, #13 privacy regulation, the future #15 AFIR-equivalent) would have been filtered out.

---

## Section 6 -- Integration discipline

### R-14. IDesign override on cross-layer merge signals

**Statement.** Two components proposed for merge based on identical or similar Contagion Matrix column signatures may be merged only if both belong to the same IDesign layer. Cross-layer merges (Manager + Engine, Engine + ResourceAccess, Manager + ResourceAccess, ResourceAccess + Resource) are forbidden regardless of matrix similarity.

**Mechanism.** `deterministic` (rejection of cross-layer merge proposals in Contagion Matrix readings).

**Body.** Synthesis decision 3. The Contagion Matrix's "identical column signatures" pattern is a useful merge signal within a layer (two Engines doing related activities, two ResourceAccess for the same Resource family). Across layers it is a false positive: a Manager and its dedicated Engine often have similar matrix signatures because they participate in the same use cases, but they are structurally distinct by IDesign discipline -- stateful workflow vs stateless logic, different roles in the closed architecture (R-02, R-03). Merging them would collapse two layers into one and eliminate the criticality gain that layering provides.

**Verification.** Deterministic on merge proposals: if a matrix-reading section proposes merging components, validate both belong to the same IDesign layer.

**Citations.** `synthesis-explanation.md` §6 Decision 3. `template.md` §Contagion Matrix §IDesign Override on Merge Signals. Guardrail #7.

**Walkthrough (EV charging).** `BillingMgr` and `BillingEngine` have similar column signatures (both Σ=4) in the EV charging Contagion Matrix. The matrix-reading section proposes them as merge candidates. R-14 fires: cross-layer pair (Manager + Engine), merge rejected, override documented inline. The two stay separate; the false positive is caught.

**Anti-example.** A SAD that merges `BillingMgr` and `BillingEngine` into `BillingService` because their matrix signatures matched. R-14 violation; the resulting `BillingService` is a stateful + stateless hybrid that breaks R-02 typing and R-11 almost-expendable Manager.

---

### R-15. NFR traceability

**Statement.** Every non-functional requirement in the SAD has a `Source` column populated with a reference to one of: a specific cell of the Contagion Matrix, a specific row of the Topological Residue Map, or a specific Business Residue. NFRs without traceability are rejected.

**Mechanism.** `deterministic` (schema + cross-reference check).

**Body.** Synthesis decision 4 + guardrail #4. A standard problem in SAD templates is that NFRs are filled in with generic boilerplate ("the system must be efficient") that is unfalsifiable, untestable, and useless. This rule forces every NFR to be empirically grounded in the stressor analysis. The three valid sources correspond to the three places stress reveals NFR needs: matrix cells (component-level NFRs like resumability, idempotency under failover), topology rows (residency, latency-zone, sovereignty), business residues (operational constraints that do not produce code but constrain behavior, e.g., diversification readiness).

**Verification.** Schema: every NFR row has a non-empty `Source` column. Cross-reference: the Source resolves to an existing matrix cell `(stressor #, component)`, topology row, or business residue #.

**Citations.** `synthesis-explanation.md` §6 Decision 4. `template.md` §Derived NFRs and per-use-case NFR tables. Guardrail #4.

**Walkthrough (EV charging).** "Resumable charge session" NFR traces to matrix row 9b cells across `ChargeSessionMgr / CA.Stop / CA.Unlock`. "Per-country data residency" NFR traces to topology row 13. "Operational diversification readiness" NFR traces to Business Residue #6. All three have Source populated; all three are empirically derived; all three are testable.

**Anti-example.** "The system must be highly available" with no Source. R-15 violation; either find the matrix cell / topology row / business residue that motivates it, or drop the NFR.

---

### R-16. Use cases document the resolved architecture, not drive its decomposition

**Statement.** Use cases describe the behavior of the residual architecture after it has been decomposed via stressor analysis. Use cases are not the source of any decomposition decision.

**Mechanism.** `heuristic`.

**Body.** Synthesis decision 5 + guardrail #5. O'Reilly heuristic L2745: "Flows are better than process or use case mapping." Lowy / IDesign explicitly walked use cases through the layers as the validation step; the synthesis preserves use cases for documentation but moves them downstream of decomposition. A SAD that derives components from use cases ends up coupled to the current set of use cases; when the business behavior shifts, the components fragment. Use cases enter the SAD at §Behavioral Diagrams, after the residual architecture is closed, with a Residue Mapping subsection that traces which residues each use case exercises.

**Verification.** Heuristic. Look for: components named for use cases (`AddCustomerManager`, `ProcessOrderManager`); use cases predating the Stressor Catalog in document chronology; Residue Mapping subsections empty or missing per use case.

**Citations.** `synthesis-explanation.md` §6 Decision 5. `template.md` §Behavioral Diagrams (use case section structure). Guardrail #5. O'Reilly L2745.

**Valid example.** EV charging Use Case "Customer charges car" exists in the Behavioral Diagrams section. Its Residue Mapping subsection traces the use case to residues #3 (auth path), #9 (resumable session), #12 (overstay billing), #13 (per-country data). Use case documents how the resolved architecture behaves; it did not drive the decomposition.

**Anti-example.** A SAD where `ChargeCarManager`, `RegisterCustomerManager`, `BillCustomerManager`, `HandleDamageManager` are listed -- one Manager per use case. R-16 violation; this is functional decomposition disguised, and the next use case that arrives forces a new Manager (R-01 violation cascade).

---

## Section 7 -- Representation discipline

### R-23. C4 architecture is expressed as one Structurizr DSL workspace, with correct scope per derived view

**Statement.** All C4 architecture in SAD fragments, worked examples, and doctrinal references is expressed as a **single Structurizr DSL `workspace.dsl` per project** -- one `model` (people, software systems, containers, components, deployment) from which the required views are **derived**: System Context (`systemContext`), Container (`container`), one Component view (`component`) per Container with 2+ IDesign components, Deployment (`deployment`), and an optional Dynamic view (`dynamic`). The `workspace.dsl` is the canonical, machine-validatable source; rendered images (SVG/PNG via the Structurizr -> C4-PlantUML pipeline) accompany it for human reading. Ad-hoc diagrams (Mermaid `flowchart`, hand-drawn boxes) are not used for C4 representation. The §Static Architecture (IDesign) diagram and the §Behavioral Diagrams are NOT C4 -- they are authored in PlantUML (`style-conventions` §6.2); the naive-architecture baselines stay Mermaid `flowchart` (`style-conventions` §6). R-23 does not touch those.

**Mechanism.** `both` -- deterministic for structural well-formedness (the workspace validates; a view is declared at each required level; no Container element is named after an IDesign component; relationship edges respect the call rules) + heuristic for whether the grouping/naming semantics are right (overlaps R-25).

**Body.** The C4 model (Simon Brown) defines four levels with strict scope per level. Mermaid forced each level to be a separately-drawn block, which drifts and invites *level-mixing* (drawing an IDesign component as a Container). Structurizr DSL eliminates the failure mode at the representation layer: the model is defined **once** and a `component` is **lexically nested** inside its `container`, which is nested inside its `softwareSystem`. A view simply scopes to a level (`systemContext` / `container` / `component`) and `include *`s the elements visible at that scope. **You cannot place a component at container scope** -- the model does not permit it -- so the most common C4 error becomes impossible by construction. The IDesign service hierarchy (R-02) maps directly: each IDesign component is a DSL `component` tagged with its layer (`Manager` / `Engine` / `ResourceAccess` / `Resource` / `Utility` / `Client`), styled so the rendered diagram still reads as IDesign.

**Per-level scope (canonical, in DSL terms):**

- **Level 1 -- System Context (`systemContext <system>` view).** Shows the target `softwareSystem` as one box, the `person` actors who interact with it, and the external `softwareSystem`s (tagged `"External"`) it integrates with. Nothing internal to the target system (the view scope excludes containers/components automatically). Audience: everybody.
- **Level 2 -- Container (`container <system>` view).** Zooms into the target system. Shows the `container` elements (separately deployable / runnable units) within the system, plus data stores (tag `"Database"`, `shape Cylinder`), queues / message buses (tag `"Queue"`), and `softwareSystem`s tagged `"External"` as supporting elements. **One `container` per row of the §Service Grouping Map (S4, R-25).**
  - **A container is** a separately deployable / runnable thing: an application, a database, a queue, a file store, a serverless function, a mobile / web / desktop app, a microservice.
  - **A container is NOT** an IDesign component (Manager / Engine / ResourceAccess / Utility) unless that component is independently deployed. In most deployments, multiple IDesign components live inside one `container` as nested `component`s.
- **Level 3 -- Component (`component <container>` view).** Zooms into one `container`. Shows the `component`s (IDesign Managers / Engines / ResourceAccess / Utilities) nested inside that container. **One Component view is produced per container that has 2+ IDesign components.** Containers with a single IDesign component (e.g., a Client app) or none (e.g., a database container) do NOT need a Component view; the §Container <-> Component mapping table is sufficient.
  - **A component is** an IDesign Manager / Engine / ResourceAccess / Utility implemented as a code module nested (`component`) inside the container's `softwareSystem`/`container` scope.
- **Level 4 -- Deployment (`deployment <system> <environment>` view).** Maps the Level-2 containers to infrastructure via `deploymentEnvironment { deploymentNode { ... containerInstance <id> } }`. Nodes nest (cloud > region > cluster > pod). Per-jurisdiction Topological residues (R-19) appear as separate top-level `deploymentNode`s per jurisdiction.
- **Level 5 -- Code (rare).** Not required in SADs produced by this meta-skill.

**Verification.**

- Deterministic (a) -- well-formedness: the `workspace.dsl` validates (`structurizr validate`, or the renderer's parse step); a view is declared for each required level (System Context, Container, one Component view per multi-component Container, Deployment).
- Deterministic (b) -- no Container named after an IDesign component: no `container` element's name/identifier matches a Manager / Engine / ResourceAccess / Utility name from the §Static Architecture taxonomy. (Level-mixing *within* a level is already impossible by the model's nesting; this check catches the remaining failure mode -- declaring a component **as** a container.)
- Deterministic (c) -- Component-view coverage: for each container with 2+ IDesign components in the §Container <-> Component mapping, a `component <container>` view exists.
- Deterministic (d) -- call-rule edges (R-03): parse the model's `<source> -> <destination>` relationships and flag illegal IDesign-layer calls (`Engine -> Engine`, `ResourceAccess -> ResourceAccess`, `Client -> ResourceAccess`, `Client -> Engine`, `Client -> Utility`, synchronous `Manager -> Manager`) by the layer tags of the endpoints.

**Citations.** Structurizr DSL language reference (docs.structurizr.com/dsl/language). C4 model official documentation (c4model.com/diagrams/system-context, /container, /component, /deployment). Internal: `shared/style-conventions.md` §6.1.

**Valid example.** One `workspace.dsl`: a `softwareSystem` "Shop" containing ~20 `container`s (deployable services / DBs / queues), each service container nesting its IDesign `component`s tagged by layer; external systems as `softwareSystem ... "External"`; a `deploymentEnvironment` nesting cloud > region > cluster with `containerInstance`s. Views: one `systemContext`, one `container`, one `component` per container with 2+ components, one `deployment`, optionally one `dynamic` per key flow.

**Anti-example 1.** The DSL declares `marketplaceManager = container "Marketplace Manager" ...` at the `softwareSystem` level. R-23 violation: a Manager is an IDesign **component**, not a container; it must be a `component` nested inside its **service** container (the one named for the §Service Grouping Map row), shown in that container's `component` view.

**Anti-example 2.** A `container "Marketplace Service"` nests 4 `component`s but no `component marketplaceService` view is declared. R-23 violation (coverage): every container with 2+ IDesign components needs its own Component view.

**Anti-example 3.** C4 architecture is drawn as a Mermaid `flowchart` (or `C4Container`) block instead of being expressed in the `workspace.dsl`. R-23 violation: C4 representation is the DSL workspace, not ad-hoc Mermaid. (The §Static Architecture IDesign diagram is PlantUML, not C4 -- `style-conventions` §6.2; the only Mermaid in a SAD is the naive baseline, `style-conventions` §6.)

---

### R-24. Residue smallest-set discipline -- extend before introducing

**Statement.** When a Structural residue admits multiple architectural responses of varying complexity, the residue commits to the **simplest response that absorbs the stressor**. Specifically: introducing a new Resource (especially a third-party engine or external infrastructure tool) requires explicit justification that extending existing ResourceAccess components with new atomic verbs is insufficient. The default is to extend; new Resources are an elaboration that needs to clear a higher bar.

**Mechanism.** `heuristic`.

**Body.** Per Lowy L2179-2181 ("Make sure the level of workflow volatility justifies the additional complexity, learning curves, and changes to the development process") and per the broader "in theory, it is just another Manager" framing (Lowy L2167), residues should not add components that can be avoided by extending existing ones. The trap is most acute when a stressor presents as "needs durable state across long-running operations": linear thinkers (R-22 violation) reach for a third-party engine (workflow engine, rules engine, state store SaaS) when extending existing domain ResourceAccess components with new atomic verbs (`RecordState`, `LoadState`, `ListInflight`, `Resume`) would absorb the stressor equivalently.

A new Resource (especially third-party) is justified when it provides capability that domain ResourceAccess GENUINELY cannot, for example:

- Visual workflow editing by non-developers (the engine's value proposition is the editor, not just the storage).
- Multi-process coordination beyond what database transactions provide (e.g., distributed sagas with cross-region coordination).
- Complex temporal semantics built-in (timers, delays, retries with backoff measured in days) that re-implementing over a DB would require non-trivial custom code.
- Operational tooling (workflow inspection, debugging, replay) that the team cannot afford to build.

Just "long-running" + "durable" + "replayable" alone do NOT clear the bar. Those are standard ResourceAccess territory: persist state via the existing RA, load on Manager restart, replay via deterministic state transitions.

**Verification.** Heuristic. For each Structural residue whose `Technical Change to Residue (IDesign)` column introduces a new Resource (especially named "engine", "store", "service", or a third-party product), ask:

1. Could this stressor be absorbed by extending an existing ResourceAccess atomic-verb set?
2. If yes, what does the new Resource provide that the extension does not?
3. Does the answer to (2) match one of the legitimate justifications above (visual editing / multi-process / complex temporal / operational tooling)?

If yes-yes-no, the residue is over-engineered. Refactor to use extended ResourceAccess; defer the third-party Resource to an ADR if and when justification (2) becomes concrete.

**Citations.** Lowy L2163-2186 (workflow Manager pattern), L2167 (literal: "In theory, it is just another Manager"), L2179-2181 (literal: complexity must be justified). Internal: this rule introduced 2026-05-17 in response to a P5 review that exposed misapplied workflow Manager pattern in the TradeMe SAD; `shared/idesign-vocabulary.md` §10 expands the workflow-specific case.

**Valid example.** TradeMe stressor #4 (long-running matching workflow F11->F12->F13 with hours-long gaps) absorbed by extending ProjectsAccess with `RecordPendingMatchState`, `QueryPendingMatches`, `ResumeMatch` atomic verbs. MarketplaceManager workflow state persists via these verbs into the project record. On Manager restart, ProjectsAccess.QueryPendingMatches lists in-flight workflows; the Manager re-instantiates them. No new Resource introduced; no third-party engine dependency.

**Anti-example.** TradeMe stressor #4 absorbed by introducing `Workflows` (Resource backed by Temporal / Camunda third-party engine) + `WorkflowsAccess` (ResourceAccess wrapper with `LoadWorkflow` / `SaveWorkflow` / `ReplayWorkflow` atomic verbs). The stressor said "long-running" + "durable" + "replayable" -- all standard RA territory. The engine adds no capability the extended ProjectsAccess does not already provide. R-24 violation: over-engineered residue, two avoidable components (Resource + RA), operational complexity for no marginal stressor coverage. Engine choice deferred to ADR if visual editing or multi-process saga semantics become concrete future needs.

---

### R-25. Service grouping: the Manager is the unit of deployment

**Statement.** Each Manager defines a separately deployable unit (service / container) by default -- one Manager, one service. The Engines and ResourceAccess that a Manager uses co-locate with it. The existence of each Manager is already justified by a Structural residue (R-18, surfaced by any of the six frameworks); that justification is also the justification for its service. Departures from one-Manager-one-service -- a shared Engine/RA promoted to its own unit, or two Managers collapsed into one unit -- require stress evidence, not preference.

**Mechanism.** `heuristic`.

**Body.** This repo's deployment style is **actor-based**: a Manager encapsulates a workflow's volatility (R-11), and its workflow boundary is its deployment boundary (each Manager is a deployable actor type, e.g. Dapr). The grouping is read from stress, not chosen freely:

- **Manager -> its own service (default).** Distinct Managers encapsulate distinct workflow volatilities, so distinct stressors hit them; their stress profiles differ; distinct services emerge naturally. The Structural residue that justifies the Manager (R-18, any framework) justifies its service.
- **Engine / ResourceAccess -> co-locate with the Manager they serve.** A private Engine/RA shares its Manager's stress profile and dependency path. This is O'Reilly L1940-1943 ("same stress profile -> combine -> reduce N") applied *within* the Manager's cluster: do not give a single-Manager Engine its own service.
- **Shared Engine/RA (used by 2+ Managers) -> stress decides.** The column signature plus boundary stressing decide whether it is duplicated per Manager, co-located with its dominant Manager, or promoted to its own service (driven by `resource-profile` / `independent-scaling`, etc., R-19).
- **Collapsing two Managers into one service -> needs evidence.** Only when they share a near-identical stress profile -- which is also an R-11 signal to check whether they are really one Manager.

This deliberately departs from Lowy's monolith-by-default and from O'Reilly's literal "reduce N" (which, taken globally, would collapse services). The repo applies "reduce N" only *inside* a Manager's cluster; *between* Managers the actor-style isolation wins. The departure is intentional and documented. The grouping is recorded in the §Service Grouping Map (S4 `contagion-analysis`) and consumed by the §C4 Model container view (S5 `residual-design`).

**Verification.** Heuristic. In the §Service Grouping Map: every Manager is its own deployable unit; its private Engines/RAs are co-located (not split out); every shared Engine/RA in its own unit cites the operational driver (R-19); every two-Manager co-location cites the shared stress profile. A single-Manager Engine given its own service with no driver, or all Managers collapsed into one service despite divergent profiles, are R-25 violations.

**Citations.** O'Reilly L1886-1901 (integration requires distributed-systems judgment; "residuality cannot teach you this"), L1940-1943 (literal: same stress profile -> combine -> reduce N -- applied within the Manager cluster here), L2556-2558 (over-granular separations that don't help -> less granularity). Lowy L1163-1171 (Manager encapsulates workflow volatility), L1027 (Manager stateful per workflow). Internal: introduced 2026-05-21; default set to actor-style one-Manager-one-service after the A-vs-B decision in the design discussion. Related: R-11 (almost-expendable Manager), R-18 (Manager <- Structural residue), R-19 (operational Topological drivers for shared components), R-23 (C4 diagram scope).

**Valid example.** TradeMe: each Manager (MembershipManager, MarketplaceManager, EducationManager) is its own service with its private ResourceAccess co-located inside it. MatchingEngine -- reused by Membership + Marketplace -- is its own service (a shared component, `resource-profile` / `independent-scaling` driver). The §Service Grouping Map has one row per service, each citing either the Manager's residue (for Manager services) or the operational driver (for the shared MatchingEngine service).

**Anti-example 1.** Collapsing all Managers into one monolithic `Core` service "to reduce N" when their stress profiles differ. R-25 violation: it discards the actor-style workflow isolation the residues call for. **Anti-example 2.** Giving a private, single-Manager Engine (e.g. an Engine used only by BillingManager) its own service with no operational driver. R-25 violation: needless N inflation; it should co-locate with its Manager.

---

### R-26. Gate-tracker coherence (NON-NEGOTIABLE)

**Statement.** The gate tracker MUST satisfy three invariants at every read:

1. **Contiguous approval chain.** Every gate marked `[x] approved` MUST have every prior gate also `[x] approved`.
2. **Active gates require approved priors.** Every gate marked `[~]` in progress / `[?]` awaiting review / `[i]` iterating MUST have every prior gate `[x] approved` (the same chain rule -- active work cannot float above an unapproved prior).
3. **Single active gate.** AT MOST ONE gate may be in `[~]` / `[?]` / `[i]` at any time. If such a gate exists, it MUST be the first gate after the contiguous `[x]` block; every gate further downstream MUST be `[ ]` pending (or `[!]` blocked).

Any state that violates any of the three is a **tracker inconsistency** and MUST be refused -- the router cannot advance, no sub-skill may emit a downstream fragment, and the auditor reports the inconsistency until the operator resolves it (revert the offending `[x]` / `[?]` / `[~]` / `[i]` to `[ ]`, or approve every missing prior).

**Mechanism.** `deterministic`.

**Body.** The Gate Approval Protocol (root `SKILL.md` §Gate approval protocol) enforces approval **at producer time** -- the executor checks the prior gate before emitting. That is necessary but not sufficient: the **tracker itself** can be edited out-of-band by a UI, a manual edit, a buggy orchestrator, or a fixture into a state where downstream `[x]` (or `[?]`, `[~]`, `[i]`) sits on top of an unapproved prior. R-26 closes that gap with three **whole-tracker invariants** that must hold at every read, not only at every write.

The single-active-gate rule (invariant 3) is the operator-facing consequence of invariants 1 and 2 combined: because every active state demands an `[x]`-only chain above it, only the gate **immediately after the last `[x]`** can be active; any second active gate would require the first one to be approved already. This makes the workflow single-threaded by construction: at any moment there is at most one decision waiting for the human (`[?]`), one fragment being produced (`[~]`), or one iteration in flight (`[i]`).

All three invariants are mechanical -- walk the gate tracker top-down (per the chain S1a -> S1b -> S2 -> ... -> S7, and the downstream S8a -> S8b extension when present):

- For invariants 1 and 2: for every gate in `[x]` / `[~]` / `[?]` / `[i]`, every prior must be `[x]`.
- For invariant 3: count gates in `[~]` / `[?]` / `[i]`; the count must be 0 or 1.

A violation of any invariant is a tracker inconsistency. The router refuses to advance until resolved; sub-skills refuse to emit; the auditor flags it as a deterministic violation in `by-fragment` and `end-to-end` modes.

R-26 complements three existing rules without restating them:

- **Disk is the source of truth** (root `SKILL.md` §Orchestration Step 1, added 2026-05-27) verifies *artifact existence* -- did the file claimed by the tracker actually land? R-26 verifies *approval order* -- is the chain of `[x]` itself coherent? Both are tracker-read invariants; both refuse to advance on violation.
- **Reopen rule** (`SKILL.md` §Orchestration Step 6) says reopening `Sn` cascades downstream `[x]` -> `[ ]`. R-26 is the symmetrical invariant: that cascade must be reflected in the tracker before any further forward motion -- if it was not, the tracker is incoherent and the router refuses.
- **Gate state machine (canonical)** (`SKILL.md` §Orchestration) names the transitions and their owners. R-26 names the *invariant the tracker must satisfy* across those transitions: no `[x]` downstream of a non-`[x]`.

**Verification.** Deterministic. The auditor in `by-fragment` mode walks the gate tracker for the fragment under audit and checks all three invariants; in `end-to-end` mode it walks the whole chain S1a..S7 (+ S8a/S8b when present). The router in `SKILL.md` §Orchestration Step 1 reports any inconsistency next to position ("Gates approved: ...; inconsistency: S2 `[x]` while prior S1b is `[?]`" / "two active gates: S1b `[?]` and S3 `[?]`") and refuses to route until the operator resolves it. There is no `--force`.

**Citations.** Internal: introduced 2026-06-08 after a UI dev fixture (`ui-sad`) exhibited the failure mode (S2 `[x]` while S1b `[?]`) and exposed that the existing producer-time check did not cover the tracker-read case. Extended the same day with the active-prior and single-active-gate invariants -- the operator-facing consequence: only one decision pending at a time. Related: `SKILL.md` §Gate approval protocol (producer-time check), §Orchestration Step 1 (disk-is-source-of-truth + R-26 enforcement), §Orchestration Step 6 (Reopen rule and cascade), §Orchestration Gate state machine (canonical) (transition ownership table).

**Valid example.** `S1a [x] -- 2026-06-05 | S1b [x] -- 2026-06-07 | S2 [x] -- 2026-06-08 | S3 [?] | S4..S7 [ ]`. Chain of `[x]` contiguous (invariant 1); S3 active has only `[x]` priors (invariant 2); S3 is the single active gate (invariant 3). Coherent.

**Anti-example 1 (invariant 1).** `S1a [x] | S1b [?] | S2 [x] | S3 [?]`. S2 `[x]` sits above S1b `[?]` -- chain not contiguous. Router refuses; operator reverts S2 to `[ ]` or approves S1b.

**Anti-example 2 (invariant 2).** `S1a [x] | S1b [ ] | S2 [?]`. S2 is active but its prior S1b is `[ ]` -- active gate floating above an unapproved prior. Router refuses; revert S2 or move S1b through `[~]` -> `[?]` -> `[x]` first.

**Anti-example 3 (invariant 3).** `S1a [x] | S1b [?] | S2 [?]`. Two gates active simultaneously -- forbidden. Single-active-gate rule says only the first gate after the last `[x]` can be active; S2 cannot be `[?]` while S1b is still `[?]`.

---

### R-27. Open Questions surfaced (NON-NEGOTIABLE)

**Statement.** The Business View MUST surface every unresolved business input -- PRD TBCs, unconfirmed assumptions, and open stakeholder questions whose answer would change the framing -- as a first-class **Open Questions** section, each entry grounded to its source and tagged with what it affects. The questions MUST be found by a **systematic multi-lens scan** of the PRD/SRD (the Open Questions discovery pass), not noticed ad hoc, and the scan MUST be attested by a **Lens Coverage Ledger** in which every lens L1-L12 emits an explicit verdict -- a finding (with the OQ IDs it produced) or "none". A missing or blank lens row is an incomplete sweep, not a clean one. Gate **S1a** MUST NOT be approved silently while any Open Question is unresolved: the executor MUST warn the operator, enumerate the unresolved questions, and proceed only on **explicit acknowledgment, recorded at the gate**. Open Questions are distinct from deferred volatilities (sensed stressors intentionally routed to S3): the former gate S1a; the latter are carry-forward context and do NOT.

**Mechanism.** `both`.

**Body.** The PRD's gaps are first-order architectural information. Everything downstream -- the naive baseline (S1b), the stressor catalog, the residual design -- is built on the Business View; if the framing silently rests on unanswered questions, advancing buries the risk where no later gate will catch it. Good architecture demands the fewest possible open doubts before S1b: every detail of the PRD must be understood, and the ones that cannot be understood from the document alone must be named, not skipped.

R-27 is the inverse of R-09: R-09 forbids *inventing* answers the PRD does not give (no speculative design); R-27 forbids *hiding* the fact that the PRD did not give them. Together: do not fabricate the missing answers, and do not paper over them -- surface them and make the operator decide, consciously and on the record, whether to proceed.

The discovery must be **systematic, not incidental**. Ambiguity hides in more than the explicit `TBC` markers; the discovery pass runs a catalogue of lenses -- lexical (uncertainty markers, hedge words, unquantified targets) and semantic/lateral (undefined terms, silent actors/ownership, lifecycle gaps, edge/failure silence, scope boundaries, external dependencies, conflicts, measurability, stale/unexamined premises, regulatory/compliance silence) -- so that nothing is missed by reading only for the obvious. Each candidate is then triaged into exactly one of: (a) **Open Question** -- needs a stakeholder answer the architect cannot supply (gates S1a); (b) **deferred volatility** -- a stressor the architect has sensed and will address in S3 (non-gating carry-forward); (c) **resolvable now** -- answerable from a careful reading of the PRD itself (resolved, not an OQ). This is lateral mode (R-22): an ambiguity is evidence of incomplete understanding to engage with, not a defect to patch away.

The acknowledgment is **not a hard block** -- the operator may have legitimate reasons to proceed (parallel stakeholder threads, time-boxing) -- but it must be a conscious, recorded decision, never a silent default (same spirit as an auditor accepted-exception). Open Questions must stay distinct from deferred volatilities: conflating them either inflates the gate with non-blocking stressors or buries a genuine blocker among deferrals.

**Verification.** Deterministic: `business-view.md` has an `### Open Questions` section (or explicit "None"); each entry is a card -- a `#### OQ-N - <Status> -- <title>` heading carrying the Status (`Open` / `Open (partial)` / `Resolved`), a `**Question:**`, and a `<sub>**Affects:** ... -- **PRD:** ...</sub>` footer (the Affects + Source) -- or, for pre-1.17.14 fragments, a legacy `| ID | Open question | Affects | Status | Source |` table row with all five cells filled; and a **Lens Coverage Ledger** lists all twelve lenses L1-L12, each with a non-empty verdict (a finding or "none") -- a missing lens or a blank verdict is a deterministic violation (the forcing function: no lens may be silently skipped). When gate S1a is `[x]` with >=1 `Open` / `Open (partial)` entry, the S1a row's `Approved on` cell in the FLOW.md Gate tracker carries an acknowledgment appended after the date (`<date> (acknowledged: ...)`); the Gate tracker has no Notes column, so this cell is the single normative location the deterministic check reads. A bare date while `Open` / `Open (partial)` entries remain is a violation. Heuristic: whether extraction is complete -- the verdicts must be genuine, not "none" rubber-stamped over a real gap; a PRD `TBC` / "unconfirmed" left uncaptured, or a semantic ambiguity (silent actor, lifecycle gap, internal conflict, stale/unexamined premise, regulatory/privacy silence) that the lens claimed "none" for, is a violation. The inverse is also a violation: an OQ attributed to a lens that did not *literally* fire (a decorative attribution -- e.g. an underspecified term mapped to L1 when no `TBC` marker is present and the real catch is L4) understates the true coverage gap; each OQ's listed lens(es) must match what that lens actually scans for. Spot-checkable when the PRD is in scope.

**Citations.** Internal -- introduced 2026-06-13 after the RAF Business View surfaced 10 PRD TBCs (OQ-1..OQ-10) judged first-order business risk, and the project asked for a systematic ambiguity-detection method so no detail is skipped. Related: R-09 (no speculative design -- do not invent answers), R-21 (criticality over correctness), R-22 (lateral mindset -- ambiguity as evidence), `business-discovery` Step 1.2 (Open Questions discovery pass) + Step 1.5 (gate S1a), template §Business View Open Questions.

**Valid example.** RAF Business View lists OQ-1 (GGR latency unconfirmed, affects G-05) .. OQ-10, found across lenses L1 (explicit `TBC`), L5 (who clears a freeze), L6 (`NoBonus?` flag semantics), L9 (in-flight frontend migration). At S1a the operator is warned "10 open questions unresolved", acknowledges proceeding, and the gate note records it. Deferred volatilities (abuse arms race, negative-NGR swings) are listed separately as S3 carry-forward and do NOT trigger the warning.

**Anti-example 1.** A Business View that silently drops the PRD's `TBC` markers and presents a clean framing; S1a approved with no acknowledgment. R-27 violation -- downstream rests on invented certainty.

**Anti-example 2.** Listing deferred volatilities (abuse arms race) under Open Questions -> spurious gate warning; or burying a genuine blocker (GGR latency) in the S3 carry-forward list so it never gates S1a. R-27 violation -- the two categories must stay distinct.

---

## Section 8 -- Verifiability cross-reference

| R-NN | Mechanism | Source | Enforced by sub-skill |
|---|---|---|---|
| R-01 | heuristic | Lowy L477-505, O'Reilly L406-413 | `business-discovery`, `residual-design`, `sad-auditor` |
| R-02 | deterministic | Lowy L981-1077 | `residual-design`, `sad-auditor` |
| R-03 | deterministic | Lowy L1281-1295 | `residual-design`, `sad-auditor` |
| R-04 | both | Lowy L1311-1351 | `residual-design`, `sad-auditor` |
| R-05 | deterministic | Lowy L1085-1089 | `business-discovery`, `residual-design`, `sad-auditor` |
| R-06 | deterministic | Lowy L1085-1105 | `business-discovery`, `residual-design`, `sad-auditor` |
| R-07 | both | Lowy L1055-1059, L1101-1105 | `residual-design`, `sad-auditor` |
| R-09 | heuristic | Lowy L815-823, O'Reilly L1014-1052 | `stressor-analysis`, `residual-design`, `sad-auditor` |
| R-10 | heuristic | Lowy L687-701 | `business-discovery`, `stressor-analysis`, `sad-auditor` |
| R-11 | heuristic | Lowy L1163-1171 | `residual-design`, `sad-auditor` |
| R-12 | heuristic | Lowy L1055-1059, O'Reilly L832-836 | `residual-design`, `sad-auditor` |
| R-13 | deterministic | Synthesis Decision 2, template §Stressor Catalog | `stressor-analysis`, `sad-auditor` |
| R-14 | deterministic | Synthesis Decision 3, template §IDesign Override, guardrail #7 | `contagion-analysis`, `sad-auditor` |
| R-15 | deterministic | Synthesis Decision 4, template §Derived NFRs, guardrail #4 | `residual-design`, `sad-auditor` |
| R-16 | heuristic | Synthesis Decision 5, guardrail #5, O'Reilly L2745 | `residual-design`, `sad-auditor` |
| R-17 | both | Synthesis Decision 6, template §Looping Signals, guardrail #8 | `contagion-analysis`, `sad-auditor` |
| R-18 | deterministic | Guardrail #1 | `residual-design`, `sad-auditor` |
| R-19 | deterministic | Guardrail #2 | `contagion-analysis`, `residual-design`, `sad-auditor` |
| R-20 | deterministic | Guardrail #6, O'Reilly L1763-1768 | `stressor-analysis`, `contagion-analysis`, `sad-auditor` |
| R-21 | heuristic | O'Reilly L807-867, L859-861 (literal) | `empirical-test`, `sad-auditor` |
| R-22 | heuristic | O'Reilly L1378-1470, L1427-1428 (literal), L1431-1432 (literal), L1450-1452 (literal), L1129-1278 | all sub-skills (cross-cutting mindset), `sad-auditor` |
| R-23 | deterministic | Structurizr DSL language reference; `shared/style-conventions.md` §6.1 | `residual-design`, `sad-assembler`, `sad-auditor` |
| R-24 | heuristic | Lowy L2167 (literal: "in theory just another Manager"), L2179-2181; `shared/idesign-vocabulary.md` §10 | `stressor-analysis`, `residual-design`, `sad-auditor` |
| R-25 | heuristic | O'Reilly L1886-1901, L1940-1943 (literal), L2556-2558 | `contagion-analysis`, `residual-design`, `sad-auditor` |
| R-26 | deterministic | Internal -- introduced 2026-06-08; `SKILL.md` §Gate approval protocol + §Orchestration Step 1 / Step 6 / Gate state machine (canonical) | router (`SKILL.md` §Orchestration Step 1), all sub-skills (refuse to emit), `sad-auditor` |
| R-27 | both | Internal -- introduced 2026-06-13; `business-discovery` Step 1.2 (discovery pass) + Step 1.5 (gate S1a); template §Business View Open Questions | `business-discovery`, `sad-auditor` |

## Notes

- The auditor (`sad-auditor`) runs deterministic checks first (R-02, R-03, R-05, R-06, R-13, R-14, R-15, R-17 schema, R-18, R-19, R-20, R-23, R-27 section/gate/ledger shape) and heuristic checks second (R-01, R-04 ambiguous cases, R-07 ambiguous cases, R-09, R-10, R-11, R-12, R-16, R-21, R-22, R-24, R-25, R-27 verdict genuineness). R-27 is `both`: the section/gate/lens-ledger shape is deterministic (incl. all 12 lenses carrying a verdict), the genuineness of each lens verdict is heuristic.
- R-22 (lateral mindset) is the only rule that applies to the architect's cognitive mode across all sub-skills. The auditor cannot mechanically check mode; what it can check is the OUTPUT shape (one-liner stressors, checklist-like coverage, mechanical refusal-condition satisfaction). Failed mode shows up as thin output that passes hygiene but produces low Ri.
- The auditor has no `--force` flag. Closure requires resolving findings or documenting an explicit accepted exception with rationale.
- R-08 is intentionally absent. The historical Lowy heuristic (smallest set ~10 components, 8+ Managers = failure) is replaced by R-18 (each component must trace to a Structural residue), which is empirically grounded rather than count-based.
