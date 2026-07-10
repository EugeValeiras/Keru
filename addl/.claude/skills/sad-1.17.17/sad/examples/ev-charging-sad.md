# Worked Example v2 -- EV Charging Network (from O'Reilly, *Residues*, ch. "A Worked Example")

> **Purpose**: Apply the **v2 template** (residual + IDesign + typed residues + topological map + business log + looping signals) to the book's worked example. This is a re-run of the v1 example after the template was improved.
>
> **Note on fidelity**: Sections drawn directly from the book are unmarked. Sections where the book is silent and the template demands content remain marked **[extrapolated]** -- these are confined to genuinely novel areas (Ri test, residual architecture summary, and the R-27 Open Questions pass added to demonstrate the card format on a book example that predates R-27), not to the core book-derived structure.
>
> **What changed since v1 of this example**: stressors are now typed; topological and business residues live in their own subsections; looping signals (ICE-ing, AFIR) are formally recorded; IDesign override is documented inline.

---

## Product

A cloud-based system to manage fast chargers for electric cars and customer subscriptions on a global scale. The platform manages customer subscriptions and billing, and allows customers to identify themselves at the charger.

---

## Open Questions **[extrapolated]**

> Unresolved business inputs surfaced by the multi-lens discovery pass (S1 Step 1.2, R-27): inputs whose answer would change the framing and that the architect cannot supply from the Product brief alone. Gate S1a cannot be approved silently while any entry is `Open` or `Open (partial)`.
>
> **[extrapolated]** -- the book is silent here (its Product brief is two sentences, not a PRD). These cards are derived from genuine gaps in that brief (R-09 -- not invented); each card's Source anchor points at the Product brief or a numbered section in lieu of a `PRD:L<n>`. The section exists to demonstrate the R-27 card format on a book example that predates R-27.

#### OQ-1 - Open -- Subscription entitlement and pricing model

**Question:** What does a customer subscription entitle (unlimited / metered / tiered access), and how is a charge priced -- a flat per-session fee, a per-kWh rate, or time-of-use? The Product brief frames "customer subscriptions and billing" but specifies neither the entitlement nor the pricing basis.

<sub>**Affects:** the billing basis -- `BillingEngine`, the "Operational diversification readiness" NFR; pre-empts the static-pricing assumption the Ri test later flags -- **PRD:** Product brief (silent); cf. Sec 9 T5</sub>

#### OQ-2 - Open -- Jurisdictions in scope at launch

**Question:** "Global scale" spans many regulatory regimes (data residency, payment, consumer protection) that differ by country. Which jurisdictions are in scope at launch, and in what rollout order? The per-country data-residency residue and the AFIR payment mandate make the launch jurisdiction list load-bearing for the deployment topology.

<sub>**Affects:** deployment topology (per-country federation), `JurisdictionEngine`, `CustomerAccess` residency -- **PRD:** Product brief ("global scale", silent on which); cf. Stressor 13, Stressor 15</sub>

#### OQ-3 - Open (partial) -- Customer identification methods at launch

**Question:** By what means do customers identify themselves at a charger, and is more than one method required at launch (key fob, smartphone app, contactless bank card)? "Customers identify themselves at the charger" is stated, but the supported set -- and whether non-fob methods are in scope for the first release -- is not.

**Answer:** The baseline method is an RFID key fob with a unique identifier, held against a panel on the charger (Sec 1, naive architecture). Whether an app- or card-based path is also required at launch stays open -- the AFIR card-payment mandate (Stressor 15) implies card auth will eventually be needed, but its launch scope is unconfirmed.

<sub>**Affects:** `AuthEngine` (single- vs multi-modal), authentication scope at launch -- **PRD:** Sec 1 (key fob); cf. Stressor 15 (AFIR card mandate)</sub>

#### OQ-4 - Open -- Billing-dispute and fee-waiver ownership

**Question:** When a customer disputes a charge or is billed in error, who is authorized to waive or refund a fee, under what policy, and within what limits? "Billing" is in scope but the dispute path and its owner are unstated.

<sub>**Affects:** `BillingEngine` waive policy, `BillingManager` reconciliation; a customer-support ownership boundary -- **PRD:** Product brief (silent); cf. Stressor 10 (billing errors)</sub>

#### OQ-5 - Open -- Customer-data consent, retention, and cross-use

**Question:** A global subscription-and-billing service holds personal and payment data, and identifying a customer at the charger captures location/time data. What are the consent, retention, and permissible-use constraints per jurisdiction -- and do they govern any data captured about non-subscribers at a charger site? The Product brief is silent on the governing privacy regime.

<sub>**Affects:** data residency / privacy (`CustomerAccess`, `JurisdictionEngine`); retention and consent policy -- **PRD:** Product brief (silent); cf. Stressor 13 (privacy regulation)</sub>

#### OQ-6 - Resolved -- Where subscription and authorization state lives

**Question:** Is subscription/authorization state held centrally or at the charger -- does the charger decide locally, or defer to a central service?

**Answer:** Centrally. The charger sends a message to a cloud service, which looks up subscription status and allows or denies the charge (Sec 1, naive architecture); the charger is a thin client and the system of record is in the cloud. (The later "Offline unlock authority" NFR adds a cached, time-bounded credential for degraded operation, but the authority of record stays central.)

<sub>**Affects:** authority boundary -- `ChargeSessionManager`, `CustomerAccess`; the "Offline unlock authority" NFR -- **PRD:** Sec 1 (naive)</sub>

> **Deferred volatilities (sensed now, routed to later stress analysis -- non-gating).** Stressors the architect already senses but defers; carry-forward context only, they do NOT gate S1a.
>
> - **Dynamic electricity pricing.** Smart-grid prices that change intra-day (Sec 9 T5) -- a future stressor against the static-pricing assumption in `BillingEngine`, distinct from the launch pricing-model question OQ-1.
> - **Vehicle-to-grid (V2G) reverse power flow.** Chargers feeding energy back to the grid (Sec 9 T6) -- `ChargerAccess` is unidirectional today; sensed as the next round's structural stressor.

#### Lens Coverage Ledger

> Forcing function (R-27): the multi-lens scan (S1 Step 1.2) is complete only when every lens L1-L12 carries an explicit verdict -- the OQ IDs it produced, or the literal word `none`. A blank or missing lens is an incomplete sweep, not a clean result.

| Lens | Verdict (OQ IDs, or `none`) |
|---|---|
| L1 Marker (TBC / TBD / unconfirmed / ?) | none (the book example carries no explicit TBC / `?` markers -- it is a finished narrative, not a PRD) |
| L2 Hedge (maybe / assume / likely / should) | none |
| L3 Unquantified target (~ / indicative / no number) | OQ-1 (no pricing basis or rate is stated) |
| L4 Undefined term (used but not defined; >1 reading) | OQ-1 ("subscription / billing" entitlement undefined), OQ-3 ("identify" -- which methods) |
| L5 Silent actor / ownership (who triggers / approves / owns) | OQ-4 (who authorizes a fee waiver / refund) |
| L6 Lifecycle / state gap (state with no entry/exit; flag semantics) | OQ-6 (where subscription / authorization state lives) |
| L7 Edge / failure silence (empty / negative / concurrent / failure) | OQ-4 (the billing-error / dispute path) |
| L8 Scope boundary (in/out, phase 2, per-tenant, rollout order) | OQ-2 (launch jurisdictions + rollout order), OQ-3 (which auth methods at launch) |
| L9 External / in-flight dependency (status unconfirmed) | OQ-2 (per-country regulatory regimes are external and unconfirmed) |
| L10 Conflict / measurability (contradiction; data to measure exists?) | none |
| L11 Stale / unexamined premise (settled decision on a stale/unverified premise) | none |
| L12 Regulatory / compliance / privacy silence (data/money/consent/AML/jurisdiction unaddressed) | OQ-5 (consent / retention / privacy regime), OQ-2 (per-country regulatory scope) |

---

## 1. Naïve Architecture

From the book: customers receive a key fob with a unique identifier; they hold it against a panel on the charger; a message is sent to a cloud service; the cloud looks up subscription status and allows or denies the charge. The cloud-based solution is "a simple API connected to a database."

Re-expressed in IDesign:

| Layer | Component | Responsibility |
|---|---|---|
| Manager | `ChargeSessionManager` | Orchestrate authenticate -> start charge -> stop charge -> unlock |
| Engine | `AuthEngine` | Match RFID id to active subscription |
| ResourceAccess | `CustomerAccess` | Read subscription state |
| ResourceAccess | `ChargerAccess` | Hardware abstraction: `StartCharge`, `StopCharge`, `Unlock` |
| Resource | CustomerDB, Charger hardware | -- |

**What the naïve architecture explicitly ignores**: hardware faults, key fob loss, queues, damage, server failure, billing disputes, abandoned cars, privacy regulation, geographic variation, electricity supply failures, market shifts, competition.

---

## 2. Flow Analysis

| # | From | To | Information | Trigger |
|---|---|---|---|---|
| F1 | Customer | Charger | RFID tap (fob ID) | Customer presents fob |
| F2 | Charger | Cloud | Authenticate request (fob ID) | F1 |
| F3 | Cloud | Charger | Authenticate result + start command | F2 success |
| F4 | Charger | Cloud | Charge complete event | Energy delivered |
| F5 | Cloud | Charger | Stop + unlock command | F4 |
| F6 | Cloud | Customer | Subscription invoice | Periodic |

---

## 3. Stressor Catalog

> All stressors from the book's table (page 52) classified by **Type**. Each type feeds a different downstream subsection.

| # | Type | Stressor | Detection | Attractor | Business Reaction | Technical Change to Residue (IDesign) |
|---|---|---|---|---|---|---|
| 1 | **Structural** | New car models | Industry contacts | Cannot charge new models -- revenue loss | Flexible charging connectors, adaptors, extra space | `ChargerAccess` polymorphic over connector type |
| 2 | **Structural** | Electricity failure | Alarm | Cannot charge cars -- revenue loss | Batteries | New `BatteryAccess`; `PowerEngine` (rules: prefer grid, fallback to battery) |
| 3 | **Structural** | Failed login (key fob breaks) | Software alert | Customer stranded, queues, lost revenue | Allow charge, invoice later on registration | **Major residue.** New `ALPRManager`; `ALPREngine`; `CameraAccess`; `AuthEngine` extended for plate auth; **billing decoupled from authentication** |
| 4 | **Business** | EV market crashes | Stock prices, consumer attitudes | Business no longer viable | Convert to petrol stations | (n/a) |
| 5 | **Business** | Queues | Cameras, sensors | Customer churn, lost revenue | Capacity planning, extra space for expansion | (n/a -- real-estate / planning) |
| 6 | **Business** | Competitors cheaper | Market scanning | Customer churn | Increase margins with physical stores | (n/a) |
| 7 | **Business** | Competitor lock-in / manufacturer | Market scanning | Fewer available customers | Lobbying, partnership | (n/a) |
| 8 | **Structural** | Damage (accident/criminal) | Sensors | Fewer chargers, lost revenue, customer satisfaction | Redundancy, security cameras | `SensorAccess` (impact/tilt); `CameraAccess` (security feed); `DamageDetectionEngine` |
| 9 | **Structural** | Server failure | Software alert | Customer cannot unlock cars | Change unlock mechanism | `ChargerAccess.Unlock` operates in degraded mode (cached credentials at charger); `ChargeSessionManager` becomes resumable |
| 10 | **Structural** | Billing errors | Complaints | Customer satisfaction affected | Waive fees | `BillingEngine` exposes waive policy; `BillingManager` reconciliation flow |
| 11 | **Business** | Competitor better coverage | Market scanning | Fewer available customers | Increase investment | (n/a) |
| 12 | **Structural** | Customer abandons car in slot | ALPR | Fewer chargers, less revenue, customer satisfaction | Invoice per minute | `OverstayManager` (async, time-based); `OverstayEngine` (per-minute fee rules); `BillingEngine` extended |
| 13 | **Topological** | Privacy regulation | Legal investigation | Cannot store customer data outside home country | Different solutions per geography | Per-country deployment of `CustomerAccess`; `JurisdictionEngine`; data residency at Resource layer |
| 14 | **Combined** | ICE-ing (fossil-fuel cars blocking chargers) | -- | -- | -- | (Survived by combination of #3, #8, #12) |
| 15 | **Combined** | AFIR 2023 -- mandatory credit-card payment | EU regulation | New auth path required | Add card-based auth | (Survived by #3 decoupling -- only `AuthEngine` extension + new `PaymentProcessorAccess`) |

---

## 4. Contagion Matrix (Structural Residues)

> Only **Structural** residues enter the matrix. Stressor #13 (Topological) is included additionally because it has component-level impact on `CustomerAccess`; it is also in the Topological Residue Map (§5). Business and Combined residues do not appear here.
>
> Operations on the same `ChargerAccess` are kept as distinct columns to expose the workflow-coupling bug the book reveals.

|  | ChargeSessionMgr | ALPRMgr | BillingMgr | OverstayMgr | AuthEng | ALPREng | BillingEng | OverstayEng | CA.StartCharge | CA.StopCharge | CA.Unlock | CustomerAccess | CameraAccess | BatteryAccess | SensorAccess | **Σ** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 -- New car models | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | **1** |
| 2 -- Electricity failure | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | **2** |
| 3 -- Failed login | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | **8** |
| 8 -- Damage | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 1 | **3** |
| 9 -- Server failure | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | **5** |
| 9b -- Server fails *during* charge | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | **3** |
| 10 -- Billing errors | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **2** |
| 12 -- Abandoned car | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | **7** |
| 13 -- Privacy regulation *(T)* | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | **2** |
| **Σ Column** | **3** | **2** | **4** | **1** | **2** | **2** | **4** | **1** | **3** | **1** | **2** | **3** | **3** | **1** | **1** | |

*(T) = Topological residue with component impact; also appears in §5.*

### Reading the matrix

**Hot row -- Stressor #3 (Failed login, Σ=8)**
A single stressor (a broken plastic key fob) reshapes 8 components. The book reads this as the *pivotal* residue: introducing ALPR as an alternative auth path forces the *decoupling of authentication from billing*. Every component touched by row 3 was either created or refactored in response. This is the residue that later makes the architecture survive #14 (ICE-ing) and #15 (AFIR) -- both Combined residues in §7.

**Hot row -- Stressor #12 (Abandoned car, Σ=7)**
Forces the time-based billing model and depends on residue #3 (ALPR). Demonstrates *residue chaining* -- #12 is not implementable without the mechanisms #3 already added.

**Multiple 1s in row 9b (Server fails during charge)**
`CA.StopCharge` and `CA.Unlock` both react. This is the bug the book highlights: if the cloud server fails between issuing stop and issuing unlock, the customer is physically locked to the charger.

> **IDesign reading of this bug**: in good IDesign, "end charge session" is a single logical operation owned by `ChargeSessionManager`. The fact that it decomposes into two separate `ChargerAccess` calls means the workflow needs either:
>
> 1. An atomic `ChargerAccess.EndSession()` operation at the hardware abstraction (preferred -- pushes responsibility to where state lives), or
> 2. A persistent, resumable workflow in `ChargeSessionManager` with idempotent retry on Unlock.
>
> The contagion matrix surfaces this in seconds. A traditional review of the static architecture would not, because both calls live inside the same component and look like a normal sequence.

**Identical column signatures -- `BillingMgr` and `BillingEngine` (both Σ=4, similar pattern)**

> **IDesign Override applied.** The matrix suggests these are merge candidates. **They are not.** Manager--Engine pairs that co-evolve are structurally separate by IDesign discipline (stateful workflow vs. stateless logic) and must not be merged regardless of matrix signature. Their similar signature is *expected* (a Manager and its dedicated Engine see the same stressors); the IDesign override prevents a residuality false positive.

**Cold cells -- `OverstayMgr` and `OverstayEng` (Σ=1 each)**
Touched only by stressor #12. Their isolation is the property that makes them safely evolvable. Do not load other concerns into them.

**Hot column -- `ChargerAccess` (combined: Start + Stop + Unlock = Σ=6)**
If we collapse the three operations into a single component column, `ChargerAccess` is the hottest. This is correct: it is the boundary to the physical world, the most volatile surface in the system. Implications: hardware abstraction must be deeply versioned, polymorphic over connector/protocol type, and capable of degraded operation when the cloud is unreachable.

---

## 5. Topological Residue Map

> Topological residues drive deployment topology, not component decomposition. They feed the *Deployment Diagram* directly.

| Residue # | Topology Driver | Deployment Decision | Affected Components | Cross-Boundary Constraints |
|---|---|---|---|---|
| 13 | Privacy regulation: customer data must remain in home country; cannot be used outside home country | Per-country deployment unit. Each country runs its own data plane (`CustomerAccess` + CustomerDB). Stateless layers (Engines, ResourceAccess for non-personal resources) may share regional deployment. | `CustomerAccess`, `JurisdictionEngine`, CustomerDB | **Allowed**: charger inventory metadata, FX rates, partner integrations, software releases. **Forbidden**: any flow carrying customer PII across country boundaries. `CustomerAccess` reads/writes are bounded to the customer's home country instance. |

> **Reading**: this single topological residue produces a profound deployment architecture decision -- the system goes from "global cloud" to "federation of country units". This decision did not appear from any functional requirement; it appeared because we asked "what if the regulatory ground shifts under us?".

---

## 6. Business Residues Log

> Stressors that produced a business decision but no software change. Recorded as decisions-of-record so future architects understand *why the system does not solve a problem it could have solved*.

| Residue # | Stressor | Attractor | Business Decision | Rationale for No Software Change |
|---|---|---|---|---|
| 4 | EV market crashes | Business no longer viable as EV charging | Pivot existing real-estate to petrol stations | Software is salvageable but the business model is the issue; no platform change can save a dead market. Decision documented to prevent over-engineering for survivability that physical assets already provide |
| 5 | Queues forming at chargers | Customer churn | Capacity planning, real-estate expansion | The bottleneck is physical (number of chargers per site), not software. Software can detect via existing `SensorAccess`/`CameraAccess` (added by #8) but cannot resolve the underlying limit |
| 6 | Competitors offer cheaper rates | Customer churn from price pressure | Increase margins via physical-store revenue (retail at charging sites) | Pricing flexibility already exists in `BillingEngine`; no new software needed. Business decided diversification of revenue is the correct response, not deeper price war |
| 7 | Competitor manufacturer lock-in | Fewer available customers (proprietary chargers per car brand) | Lobbying, partnership programs, information campaigns | Software cannot solve a market-access problem. `ChargerAccess` polymorphism (residue #1) handles the technical compatibility side; the business side is regulatory/political |
| 11 | Competitor with better geographic coverage | Fewer available customers | Increased investment in physical buildout | Capital allocation problem; no architectural lever applies |

> **Why we kept #5 here despite SensorAccess/CameraAccess existing**: the *residue* is the business decision to plan capacity and acquire real estate. The detection mechanism (sensors, cameras) is provided by a separate Structural residue (#8 Damage). This separation is important -- it prevents the false impression that "we solved queues with software".

---

## 7. Looping Signals (Combined Residues)

> Stressors already survived by a combination of existing residues. Recorded because they are the empirical signature of approaching criticality and the strongest argument for the value of the residual analysis.

| Residue # | Stressor | Survived by Combination of | Notes |
|---|---|---|---|
| 14 | ICE-ing (fossil-fuel cars deliberately blocking chargers) | #3 (ALPR captures plate of any vehicle), #8 (cameras provide evidence), #12 (per-minute billing applies regardless of vehicle type) | **Anti-social behavior becomes a revenue line.** ICE-ing was unforeseeable when the original design was made; the combined residues turn it from a customer-experience disaster into a billing event with legal evidence trail |
| 15 | AFIR 2023 -- EU mandates ad-hoc credit-card payment at all public chargers | #3 (auth/billing decoupling already in place from key-fob residue) | **Ten years after design, an EU regulation is absorbed without architectural rewrite.** Adding credit-card auth is now a localized change in `AuthEngine` plus a new `PaymentProcessorAccess`. `BillingEngine` and `ChargeSessionManager` are unchanged because the residue from a broken plastic key fob already split authentication from billing |

> **The mathematical leverage**: each of these Combined residues represents *an unbounded set of unknown future stressors* that share the same attractor shape. Residue #3 was added because of one specific stressor (key fob breaks). It now covers ICE-ing, AFIR, and any future "new way to identify the customer" -- including stressors that have not happened yet.

---

## 8. Derived Non-Functional Requirements **[extrapolated]**

> The book stops at the matrix. The v2 template asks for traceable NFRs sourced from matrix cells, topological rows, or business residues.

| NFR | Source | Specification |
|---|---|---|
| Resumable charge session | Matrix row 9b (CSM / CA.Stop / CA.Unlock) | Charge session must complete (stop + unlock) atomically from the customer's perspective, even if the cloud fails mid-session. Implemented via either atomic `EndSession` at the charger or persistent workflow with idempotent unlock |
| Offline unlock authority | Matrix row 9 (CA.Unlock when CSM fails) | Charger must hold a cached, time-bounded credential allowing local unlock when cloud is unreachable for ≥ 60 s |
| Auth/billing independence | Matrix row 3 across AuthEng / BillingEng / BillingMgr | Authentication mechanism is a runtime parameter, not a structural decision. Adding a new auth method must not require changes in `BillingEngine` |
| Per-country data residency | **Topology row 13** | Customer data partitioned by jurisdiction. No cross-border flows carry PII. `CustomerAccess` is bounded to home-country instance |
| Polymorphic charger interface | Matrix row 1, plus hot-column reading on ChargerAccess | `ChargerAccess` interface abstracts connector type, voltage, protocol -- variations resolved internally |
| Hardware-degraded operation | Matrix rows 2, 8, 9 across BatteryAccess / SensorAccess / CA | Each hardware-facing `ResourceAccess` defines a degraded-mode contract |
| Operational diversification readiness | **Business residue #6** | `BillingEngine` pricing rules support non-charging revenue streams (retail at site) without code changes. Configuration-driven |
| Capacity-aware site provisioning | **Business residue #5** | Operational SLA: customer-visible queue length informs site expansion decisions. Software exposes the metric; business owns the response |

---

## 9. Empirical Test (Residual Index) **[extrapolated]**

> The book does not run a formal Ri test for this example. A plausible test set, generated *after* the residual architecture is closed:

| # | Test Stressor | Naïve survives? | Residual survives? | Rationale |
|---|---|---|---|---|
| T1 | Charger firmware vulnerability requires emergency offline patch | no | yes | `ChargerAccess` polymorphic over firmware version (residue #1); offline degraded mode (residue #9) lets unaffected chargers operate during rollout |
| T2 | New regulation: real-time energy reporting to grid operator | no | yes | `ChargeSessionManager` already emits charge events; add a `GridReportingAccess` consumer |
| T3 | Customer wants to pay via fleet operator (B2B billing) | no | yes | Auth/billing decoupling (residue #3) makes payer-id swappable from driver-id |
| T4 | Vandalism wave in a specific city | no | yes | Residue #8 (sensors + cameras) detects; redundancy already planned |
| T5 | Solar/wind smart-grid pricing changes electricity cost every 15 min | no | no | Not addressed; `BillingEngine` assumes static pricing. New residue analysis required around dynamic pricing |
| T6 | Charger needs to reverse-feed power to grid (V2G) | no | no | Not addressed; `ChargerAccess` is unidirectional. New residue needed |

**X = 0, Y = 4, S = 6  ->  Ri = 4/6 ~ 0.67**

Positive movement toward criticality. T5 and T6 mark the next round of stress analysis: **dynamic energy economics** is an unstressed surface.

---

## 10. Residual Architecture Summary **[extrapolated]**

| Layer | Components |
|---|---|
| **Managers** | `ChargeSessionManager` (resumable workflow), `ALPRManager`, `BillingManager`, `OverstayManager`, `LegalCaseManager` (damage/abuse) |
| **Engines** | `AuthEngine` (multi-modal: RFID / plate / card), `ALPREngine`, `BillingEngine` (stateless, waive-aware), `OverstayEngine`, `JurisdictionEngine`, `PowerEngine`, `DamageDetectionEngine` |
| **ResourceAccess** | `CustomerAccess` (per-country instance), `ChargerAccess` (polymorphic + degraded mode), `CameraAccess`, `SensorAccess`, `BatteryAccess`, `PaymentProcessorAccess` (added by AFIR), `GridReportingAccess` (added by T2 in next iteration) |
| **Resources** | Per-country CustomerDB, charger hardware, cameras, sensors, batteries, external payment processors, grid operator APIs |

**Manager-to-Manager**: async via Dapr Pub/Sub. `ChargeSessionManager` emits `ChargeCompleted` consumed by `BillingManager` and (later, by AFIR) `PaymentProcessorAccess`-fronted billing flow. This indirection is what enabled AFIR to be additive rather than invasive.

**Geographic topology** (from §5): per-country deployment unit. Each unit runs its own `CustomerAccess` + CustomerDB. Stateless layers (Engines, non-personal ResourceAccess) deployed regionally. Cross-country flows bounded to non-PII metadata.

---

## 11. v2 Template Validation -- What Changed Since v1 of This Example

| v1 Issue | v2 Resolution |
|---|---|
| Topological residue (#13) awkwardly forced into Static Architecture section | Now lives cleanly in §5 *Topological Residue Map*. Component impact still appears in matrix with `(T)` annotation |
| Pure-business stressors (#4, #6, #7, #11) had no place; risk of being dropped from catalog | All five business stressors (now including #5) recorded in §6 *Business Residues Log* with rationale. Decisions-of-record preserved |
| ICE-ing and AFIR documented as anecdotes inside the matrix-reading prose | Both formalized as Combined residues in §7 *Looping Signals* with explicit "survived by combination of" trace. Strongest material for stakeholder communication is now structured, not buried |
| BillingMgr/BillingEngine merge ambiguity addressed only in passing | IDesign override note in matrix-reading section makes the rule explicit and reusable |
| NFRs traceable only to matrix cells | NFRs now traceable to matrix cells, topology rows, *or* business residues. Two new NFRs (operational diversification, capacity-aware provisioning) emerged from Business Residues that v1 had no slot for |

**Sections where extrapolation marker was removed in v2 of the example**:
- Topological residues (was extrapolated into Static Architecture; now native)
- Business residues (was missing entirely; now native)
- Looping signals (was prose-only; now native)

**Sections where extrapolation marker remains** (genuinely beyond what the book provides for this example):
- §8 Derived NFRs -- the book stops at the matrix
- §9 Empirical Test Ri -- the book describes the formula but does not run it on the EV example
- §10 Residual Architecture Summary -- the book leaves this implicit

These remaining extrapolations are **template-driven rigor that the book itself recommends but does not execute on its own example**, not template gaps.

---

## 12. Closing Observation

The v2 template fits the book's example without forcing it. The two structural gaps identified in v1 (topology and business residues) closed cleanly. The IDesign override resolved a real merge-signal false positive. And formalizing Combined residues turned the book's two most persuasive moments (ICE-ing absorbed for free, AFIR absorbed ten years later) into structured, traceable evidence rather than narrative anecdote.

If a future version of the book ran its own example through this template, the only sections it would need to *add* are the Ri test and the residual architecture summary -- both of which the book recommends in principle but omits in practice.
