---
title: Stressor source frameworks
version: 1.4
date: 2026-05-21
---

# Stressor Source Frameworks

Working reference for the six frameworks the meta-skill uses to generate stressors during the `stressor-analysis` (S3) sub-skill. Each framework is a different angle on the business context. Used together, they mitigate the curse of high dimensionality (O'Reilly L660-669) -- the human tendency to generate "patchy", consensus-driven samples instead of genuinely diverse ones.

This document expands what `sad/template.md` §Stressor Catalog and `sad/synthesis-explanation.md` §9 reference. Constitution rules R-13 (typed residues), R-20 (no probability filter), and the discipline rules in `shared/decomposition-discipline.md` apply throughout.

The six frameworks are deliberately heterogeneous: PESTLE for macro context, Porter for competitive context, Business Model Canvas for internal business mechanics, abstraction stressing for ontological assumptions, flow stressing for inter-actor information paths, and boundary stressing for runtime deployment fronts. No single framework is sufficient on its own; the goal is breadth, not completeness within any one lens.

---

## 1. PESTLE (Political, Economic, Social, Technological, Legal, Environmental)

### Definition

PESTLE is a macro-environment scan covering six categories of external factors that affect any business. The architect uses each letter as a prompt to generate stressors that the technology team would not surface on its own.

### Key questions

| Letter | Questions to ask |
|---|---|
| **P**olitical | What government policies, trade restrictions, sanctions, lobbying outcomes, or political instability could affect this system? Who in our context could be sanctioned or excluded? |
| **E**conomic | What inflation, currency, interest-rate, recession, supply-chain, or commodity-price shifts could affect customer behavior, costs, or revenue? |
| **S**ocial | What demographic, cultural, generational, accessibility, or value-shift trends could change who uses the system or how? |
| **T**echnological | What new platforms, devices, AI / ML capabilities, protocols, or vendor shifts could obsolete current technical assumptions? (NOT the same as our internal tech stack -- think industry-wide.) |
| **L**egal | What laws, regulations, compliance regimes, or court rulings could be enacted that change what we may store, share, or do? |
| **E**nvironmental | What climate, weather, energy availability, pandemic, or physical-environment events could affect operations? |

### Example stressors generated (EV charging)

- **P:** A government bans imports of electric vehicles from a specific country. (Removes a vehicle population from our charger compatibility list.)
- **E:** Electricity prices triple due to gas crisis. (Charging cost model is no longer competitive.)
- **S:** New generation prefers shared mobility over ownership. (Subscription model loses its target customer.)
- **T:** Wireless charging at parking spots becomes commercially viable. (Plug-based hardware obsolescence.)
- **L:** EU AFIR mandates ad-hoc credit-card payment at all chargers (this is the actual book example #15).
- **E:** Heatwave brownouts limit charging hours in summer. (Capacity unpredictable.)

### When to use PESTLE

First-pass scan. Always run early in `stressor-analysis`. Cheap, broad, surfaces stressors no engineer would think of alone. Best with stakeholders from outside engineering (legal, marketing, operations).

### When PESTLE alone is insufficient

PESTLE produces external stressors. It does not surface internal-business-mechanics stressors (use Business Model Canvas) or competitor-driven stressors (use Porter). For inward-facing systems with no competitive pressure (internal tooling), PESTLE may produce thin output -- compensate with abstraction stressing.

---

## 2. Porter's 5 Forces

### Definition

Porter's framework analyzes the competitive structure of an industry. Each force is a different way the architecture's value can be eroded by competitive pressure.

### The five forces

| Force | Stressor question |
|---|---|
| **Threat of new entrants** | What new competitors could enter our market? What does their architecture make easy that ours does not? |
| **Bargaining power of buyers** | What can customers demand that they cannot today? What makes them choose us vs alternatives? |
| **Bargaining power of suppliers** | Who do we depend on (cloud providers, hardware vendors, payment processors, regulators) -- and what happens when their terms change? |
| **Threat of substitutes** | What alternative solutions could replace ours entirely? (Not "different vendor", but "different solution category".) |
| **Competitive rivalry** | What can existing competitors do that would force us to react? Pricing? Coverage? Features? Lock-in? |

### Example stressors generated (EV charging)

- **New entrants:** A car manufacturer launches its own proprietary charging network. (Reduces our addressable customer base.)
- **Buyer power:** Fleet operators demand B2B billing; individual customers do not. (Pricing structure assumes B2C; B2B is structurally different.)
- **Supplier power:** Our hardware partner doubles its license fee. (Unit economics break.)
- **Substitutes:** Solid-state batteries with 1000-mile range make public charging unnecessary for most trips. (Demand collapses.)
- **Rivalry:** Competitor offers free charging for Tesla owners. (Direct competitive pressure -- this is book example #6.)

### When to use Porter

When the system operates in a competitive market. Generates Business-typed residues most often (R-13). Many Porter-derived stressors land in the Business Residues Log (R-13 + R-15 traceability), not the Contagion Matrix.

### When Porter alone is insufficient

Porter produces market stressors but says little about regulation, technology shifts, or operational events. Pair with PESTLE for breadth. Internal tools or non-commercial systems get little value from Porter -- use Business Model Canvas instead.

---

## 3. Business Model Canvas (BMC)

### Definition

The Business Model Canvas (Osterwalder & Pigneur, 2010) decomposes a business model into nine blocks. Each block is a vector of stressors -- "what could change in this block?" -- that the architecture might need to absorb.

### The nine blocks

| Block | Stressor question |
|---|---|
| **Customer Segments** | Who do we serve today? Who could we be forced to serve tomorrow? Who could we lose? |
| **Value Propositions** | What value do we promise? What if a competitor or substitute redefines what "value" means here? |
| **Channels** | How do customers reach us? What if a channel disappears (app store removal, third-party shutdown)? |
| **Customer Relationships** | How do we engage customers? What if the engagement model shifts (self-service to assisted, or vice versa)? |
| **Revenue Streams** | How do we make money? What new revenue streams could emerge? Which existing ones could collapse? |
| **Key Resources** | What do we own that makes us viable (data, hardware, IP)? What if one becomes unavailable? |
| **Key Activities** | What do we do internally? What if one activity becomes uneconomical or impossible? |
| **Key Partnerships** | Who do we depend on? What if a partner exits, raises prices, or changes terms? |
| **Cost Structure** | Where does cost come from? What if a cost component blows up (electricity, compute, labor)? |

### Example stressors generated (EV charging)

- **Customer Segments:** Fleet operators become the primary segment, not individual drivers.
- **Value Propositions:** Reliability becomes more important than price.
- **Channels:** App stores ban our app due to a policy change. We cannot reach mobile customers without a new channel.
- **Customer Relationships:** Subscription model is replaced by pay-per-use due to customer preference.
- **Revenue Streams:** Retail (coffee, food) at charging sites becomes a primary revenue line (book example #6 reframe).
- **Key Resources:** Our charger hardware vendor's IP is enjoined; we cannot manufacture more.
- **Key Activities:** Field maintenance becomes regulated; only certified technicians may service chargers.
- **Key Partnerships:** Payment processor exits the market; we need to integrate a new one (related to book example #15).
- **Cost Structure:** Real-estate costs at charging sites triple due to urban land scarcity.

### When to use BMC

When the system has a clear business model. Surfaces internal-mechanics stressors PESTLE and Porter miss. Especially good for revenue, partnership, and cost stressors. Frequently produces Topological residues (when geographies / segments shift) and Business residues (when revenue / cost decisions land outside software).

### When BMC alone is insufficient

BMC focuses on the business; it does not stress the technology assumptions or the data model. Pair with abstraction stressing for ontological coverage.

---

## 4. Abstraction stressing

### Definition

Abstraction stressing is an internal-architecture lens: challenge every noun in the domain model. For each domain entity, ask: "What if this is not what we think it is?" The technique surfaces stressors that hide inside the architect's own assumptions about the business.

### Key questions

For each domain entity (e.g., `Customer`, `Order`, `Account`, `Charger`, `Tradesman`, `Project`):

- **Identity.** What if the entity has multiple identities? Multiple instances representing the same thing? No stable identity at all?
- **Boundary.** What if the boundary between this entity and another shifts? What if two entities merge or one splits?
- **Cardinality.** What if the cardinality changes (1:1 becomes 1:N, N:M, or 0:N)?
- **Lifetime.** What if the entity is much shorter-lived or much longer-lived than we assumed?
- **State.** What if the entity has more states than the current model captures?
- **Ownership.** What if the entity changes hands? What if it is owned by multiple parties simultaneously?
- **Equality.** What does it mean for two of these entities to be "the same"? Could that definition change?

### Example stressors generated (EV charging)

- **Customer identity:** A customer is now a fleet (a corporate identity that aggregates many individual drivers). Auth model assumed 1 person = 1 fob; now 1 fleet = many drivers + many fobs + shared billing.
- **Customer cardinality:** A driver works for two fleets. Whose subscription pays?
- **Charger boundary:** A "charger" was a single unit. Now a charger is a stall with multiple plugs sharing one network connection.
- **ChargeSession lifetime:** Sessions assumed to last minutes to hours. A truck on a slow charger overnight has a session lasting 14 hours. A multi-day trickle charge breaks all timeouts.
- **Account ownership:** An account changes hands when a fleet is acquired. Existing sessions, balances, history -- who owns them?

### When to use abstraction stressing

Always, late in `stressor-analysis`. After PESTLE / Porter / BMC have produced external stressors, abstraction stressing surfaces internal model fragility. Especially valuable for systems where the architect feels confident about the domain -- the certainty itself is suspect.

### Every-noun pass (O'Reilly Rule 3 -- canonical)

Abstraction stressing challenges the nouns of the **domain model**. O'Reilly's third brainstorming rule is the systematic complement: **go through every noun in each component's name and stress that noun.** It is cheap, exhaustive, and mechanical -- run it once the naive architecture (S1) gives named components.

**Run it exhaustively, not as a sample.** This is the rule's whole value: take EVERY noun in EVERY component's name and apply each prompt below. Do not stop at a representative handful -- a sample defeats the random-simulation purpose (O'Reilly L660-669). For a system with ~12 components averaging ~1.5 nouns each, expect on the order of 5-7 stressors per component (~60-80 raw) before deduplication. That volume is the point, not an accident.

For each component, take each noun in its name and ask what happens when that noun:

- **fails / becomes unavailable** (e.g. `RegulatoryReportingEngine` -> what if *reporting* fails? what if the *regulatory* rule set is gone?),
- **multiplies** (more than one of this noun -- two *configurations* claiming to be current),
- **changes shape / schema** (the *audit* event schema changes and every caller breaks),
- **is deleted while in use** (a *config* entry removed while live operations depend on it),
- **arrives out of order / duplicated / replayed** (a *payment* recorded twice).

This is the rule that, in practice, surfaces the highest-blast-radius stressors -- shared Resources and Utilities (the nouns everyone reads) light up as hot columns. Type each stressor as it lands (R-13). Expect volume; the Contagion Matrix (S4) and looping will filter. Near-duplicate every-noun stressors across components (the "race-condition on every Manager" family) are a normal output -- keep them typed and let the matrix collapse them. **Do not pre-curate** the every-noun output ("this one seems unlikely") -- that is exactly the bias the rule defeats; generate all, type all, let the matrix decide.

It is a generation *technique* under abstraction stressing, not a seventh framework: it produces the same residue profile (predominantly Structural), so it shares abstraction stressing's row in the calibration matrix.

### When abstraction stressing alone is insufficient

It surfaces only stressors that the architect can imagine through introspection (whether of the domain model or the component names). Pair with PESTLE / Porter / BMC for the external context the architect does not have authority over.

---

## 5. Flow stressing

### Definition

Flow stressing is the per-flow lens: for each row of the §Flow Analysis section, stress the flow itself. The flows are the connective tissue between actors; flow stressing surfaces stressors at the seams.

### Key questions per flow

For each flow `From (Actor) -> To (Actor): Information / Payload`:

- **Prevention.** What could prevent this flow from happening at all?
- **Delay.** What could delay it past acceptable bounds?
- **Duplication.** What could cause this flow to happen twice (or many times) when it should have happened once?
- **Reordering.** What could cause flows to arrive out of order?
- **Reroute.** What could cause this flow to go to a different recipient than intended?
- **Corruption.** What could cause the payload to arrive distorted, partial, or with wrong values?
- **Replay.** What could cause this flow to be replayed maliciously or accidentally at a later time?
- **Loss.** What could cause this flow to be silently dropped (no failure signal)?

### Example stressors generated (EV charging)

For flow F2 (Charger -> Cloud: authenticate request):

- **Prevention:** Cellular network outage at the charger location. No flow possible.
- **Delay:** Request takes 30s to clear the cellular link; customer has walked away.
- **Duplication:** Charger retries on timeout, sending two auth requests; cloud counts two charging sessions.
- **Reroute:** DNS poisoning routes the charger to an attacker's mock cloud.
- **Corruption:** Bit-flip on the cellular link changes the fob ID by one digit; auth attaches to the wrong customer's account.
- **Replay:** Captured auth packet replayed by an attacker with a cloned fob.
- **Loss:** Flow is dropped silently; charger interprets non-response as auth failure; customer confused.

For flow F4 (Charger -> Cloud: charge complete event):

- **Prevention:** Cloud is down for maintenance. The charger has finished charging but cannot tell anyone.
- **Delay:** Event queued for hours due to cloud backlog. Billing reconciliation lags.
- **Duplication:** Charger thinks the event was lost and retries; cloud bills twice.
- **Loss:** Event dropped; customer is billed for an open session that never closes.

### When to use flow stressing

Always, after `flow-analysis` (S2) is approved and the Flow Analysis table is stable. Generates a high density of Structural residues (R-13) because flow corruption usually maps to a component-level fix (idempotency, retry, replay protection).

### When flow stressing alone is insufficient

It only addresses what is in the Flow Analysis table -- if a flow is missing from S2, it cannot be flow-stressed. Pair with abstraction stressing to discover missing flows (when an entity's boundary or cardinality shifts, new flows often appear).

---

## 6. Boundary stressing

### Definition

Boundary stressing stresses **co-location** decisions. Where flow stressing asks "what could go wrong with the information flowing *between actors*", boundary stressing asks "what would force these components to run as separate deployable units?" It discovers **operational Topological residues** (R-19) -- the drivers that, under R-25, resolve the cases that the actor-style default does not settle on its own.

Under R-25 the default is already fixed: **one Manager, one service**, with each Manager's private Engines/ResourceAccess co-located inside it. So boundary stressing does NOT hunt for reasons to split Managers (that split is the default, justified by each Manager's own residue). It focuses on the two cases the default leaves open:

- **Shared Engines/ResourceAccess** (used by 2+ Managers): does a boundary stressor force this shared component into its own service (rather than duplicating it or co-locating it with one Manager)?
- **Manager co-location** (the rare inverse): do two Managers share a profile strongly enough to run in one service?

The bias matches Lowy + R-25: the lens looks for the specific stressor where the default grouping genuinely fails. If no boundary stressor applies to a shared component, duplicate it or co-locate it with its dominant Manager -- do not promote it to its own service.

### Key questions (per component or component pair A / B)

| Driver | Stressor question | Produces (R-19 operational driver) |
|---|---|---|
| **Independent scaling** | What load would make A scale at a wildly different rate or factor than B? (A spikes 100x at peak; B is constant.) | `independent-scaling` |
| **Failure isolation** | What failure in A must NOT be allowed to take down B? (A processes untrusted third-party input; B is mission-critical.) | `failure-isolation` (blast-radius) |
| **Change cadence** | What makes A change / deploy far more often than B? (A iterates daily on promo rules; B is stable for quarters.) | `change-cadence` |
| **Resource profile** | Do A and B have incompatible resource profiles? (A is GPU / CPU-bound batch; B is memory-bound latency-sensitive.) | `resource-profile` |
| **Security zone** | Does A handle a different trust level / compliance scope than B? (A is internet-facing or PCI-scoped; B must stay out of that scope.) | `security-zone` |

### Example stressors generated (EV charging)

- **Independent scaling:** During a festival, charge-authentication requests spike 50x while billing volume stays flat. AuthEngine and BillingEngine have divergent scaling profiles -> `independent-scaling` boundary candidate.
- **Failure isolation:** The ALPR (plate-recognition) subsystem ingests images from untrusted third-party cameras; a crash on a malformed image must not take down charge authorization -> ALPRManager isolated from ChargeSessionManager (`failure-isolation`).
- **Change cadence:** Pricing rules change weekly for promotions; charge-control logic is stable for quarters. Coupling their deploy slows pricing or risks charging -> `change-cadence` boundary.
- **Resource profile:** ALPR image processing is GPU-intensive; the charge session is I/O-bound. Co-locating wastes or starves resources -> `resource-profile` boundary.
- **Security zone:** The payment gateway is PCI-scoped; the rest of the system must stay out of PCI scope -> `security-zone` boundary.

### When to use boundary stressing

Late in `stressor-analysis`, after the naive architecture (S1) gives concrete components to stress and the other frameworks have produced the business / context / flow stressors. Boundary stressing reads against the candidate components. Its residues are typed **Topological** (operational sub-family, R-13 stays closed at four types) and feed the Topological Residue Map (S4), which the Service Grouping reading and §C4 Model container view (S5) consume.

### When boundary stressing alone is insufficient

It only addresses runtime deployment boundaries. It says nothing about business volatility, regulation, or domain-model fragility. It also presupposes a component set to stress -- run it after at least a naive decomposition exists. Pair with abstraction stressing (which can reveal that a component should not exist at all, making its boundary moot).

---

## How to use the six together

A reasonable session sequence:

1. **PESTLE first** (15-30 min). Cheap macro scan. Stakeholders outside engineering contribute most.
2. **Porter** (15-30 min). Competitive context. If the system is non-competitive, skip and replace with deeper BMC.
3. **BMC** (30-60 min). Business mechanics. Often produces the largest count of stressors.
4. **Abstraction stressing** (30-60 min). Ontological challenge. Engineers contribute most. Often produces the highest-impact stressors (deep structural changes).
5. **Flow stressing** (15 min per flow). Seam-level. Run after Flow Analysis is stable.
6. **Boundary stressing** (15-30 min). Run after a candidate component set exists; discovers operational Topological residues. Under R-25 the default is one Manager = one service (private Engines/RAs co-located); this lens resolves the open cases -- whether a shared Engine/RA gets its own service, or two Managers co-locate.

Do not stop after one or two frameworks. The diversity of frameworks is the random simulation -- skipping any of them rebuilds the bias the random simulation is meant to defeat.

A first session typically produces 50-80 stressors of mixed quality across all frameworks once the every-noun pass is run exhaustively (it alone yields ~5-7 per component). Type each as you go (R-13). Do not filter. The Contagion Matrix (`contagion-analysis` S4) will surface what matters.

**Volume is measured by looping, not by a count.** Do NOT target a stressor number. The catalog is complete when **looping** appears -- new stressors are increasingly survived by existing residues (O'Reilly L1812-1816; S3 Step 8). That is the empirical signal the attractor space has been sampled enough. If looping has NOT appeared, the catalog is under-sampled: keep generating (run the every-noun pass exhaustively, push the random/decision-tree harder, do not curate). If looping HAS appeared, stop -- more stressors past looping is redundancy, not criticality. A peer pipeline generating 182 stressors (deduplicated from 241, with whole near-duplicate families) is over-generating past the looping point; a curated 55 that loops samples the same attractor space with less redundancy. Neither the high count nor the low count is the goal -- the looping is.

---

## Framework x Residue type coverage

The six frameworks are not interchangeable for residue typing. Each tends to produce a different mix of typed residues (R-13), and the matrix below is a **calibration tool**: if a session's stressor catalog has a residue distribution wildly different from the column expectations, it usually signals a framework was skipped or under-exercised.

| Framework | Business | Topological | Structural |
|---|---|---|---|
| PESTLE | **Primary** (regulatory, economic, political shifts) | Secondary (geographic / segment redistribution) | Rare (occasional via the Technological letter) |
| Porter | **Primary** (revenue erosion, partner pricing, substitute disruption) | Secondary (market-entry geography) | Rare |
| BMC | **Primary** (revenue, cost, channel, partnership) | **Primary** (segment / channel / geographic shifts) | Rare (occasional via Key Resources / Key Activities) |
| Abstraction stressing | Secondary (ownership transfers) | Secondary (boundary shifts) | **Primary** (identity, cardinality, lifetime, state) |
| Flow stressing | Rare | Rare | **Primary** (idempotency, retry, replay, ordering, loss) |
| Boundary stressing | Rare | **Primary** (operational drivers: scaling, failure-isolation, change-cadence, resource-profile, security-zone) | Rare |

### How to read it

- **Primary** = the framework reliably produces this residue type and is one of the best sources for it.
- **Secondary** = the framework produces this residue type often enough to matter, but is not the main source. Do not rely on it as the only source.
- **Rare** = the framework occasionally produces this type, usually as a side effect. Do not rely on it for coverage.

### Calibration heuristic

After a `stressor-analysis` session, count residues by type. A healthy catalog typically has Business and Structural dominating, with Topological visible. If Structural is missing, abstraction or flow stressing was likely under-exercised. If Business is missing, PESTLE / Porter / BMC was likely under-exercised. If Topological is present but contains only geographic drivers (no operational ones: scaling / failure-isolation / change-cadence / resource-profile / security-zone), boundary stressing was likely skipped -- and the service-grouping decision in S5 will have no stress-derived basis (R-25). The matrix is the diagnostic.

> **Why Combined is not in the matrix.** R-13 defines four residue types -- Structural, Topological, Business, and **Combined**. Combined is intentionally absent from this matrix because Combined residues are not *generated* by any framework: they **emerge** in `contagion-analysis` (S4) when a new stressor turns out to be already survived by the combination of existing residues (R-17), and are recorded as Looping Signals. R-13's taxonomy is closed at four types -- the three columns here cover every type a framework can directly produce; do not add columns for invented types.

---

## Anti-patterns when using the frameworks

### "Likely scenarios only"

Filtering frameworks by what stakeholders consider likely defeats the purpose. PESTLE generates "ridiculous" stressors (war, pandemic, regulation reversal) that are not likely individually but collectively define the attractor space. Same for Porter (a substitute that does not exist yet still defines a future attractor).

### "Stressors that have a known fix"

Some teams stop generating stressors once they have a "candidate solution" in mind. This skips the random simulation step. Generate first, then map to residues; mapping early biases the catalog.

### "We already use a framework"

A team running PESTLE in their strategy meeting does NOT have a stressor catalog. The stressor catalog is a different artifact: typed, traceable, fed into a Contagion Matrix. The framework is the input; the catalog is the output. Do not skip the catalog because "we have done PESTLE before."

### "One framework is enough"

Each framework is biased. Their combination is the random simulation. Using only one rebuilds the bias.

---

## References

- O'Reilly, B. M. (2024). *Residues*, especially L1763-1768 (no probability), L1850-1855 (frameworks listed), L1819-1840 (mathematical leverage justifies breadth).
- Osterwalder, A., & Pigneur, Y. (2010). *Business Model Generation: A Handbook for Visionaries, Game Changers, and Challengers.* John Wiley & Sons.
- Porter, M. E. (2008). *The Five Competitive Forces That Shape Strategy.* Harvard Business Review, 86(1), 78.
- Perera, R. (2017). *The PESTLE Analysis.* Nerdynaut.
- `shared/constitution.md` -- R-13 (typed residues), R-20 (no probability).
- `shared/decomposition-discipline.md` -- guardrails #3 (business decisions documented), #6 (no probability/cost), #8 (combined residues recorded).
- `sad/template.md` §Stressor Catalog -- where the output of these frameworks lands.
- `sad/examples/ev-charging-sad.md` §3 -- worked example of a typed Stressor Catalog.
