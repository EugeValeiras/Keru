---
name: flow-analysis
description: Second sub-skill of the `sad` meta-skill. Produces the Flow Analysis fragment of a SAD -- a table of information flows between actors (people, companies, software components external to the system). Invoke after the Naïve Architecture fragment exists. Distinct from use-case mapping; this is per O'Reilly L2745 heuristic that flows replace process or use case mapping.
task_types: [map-flows, actor-flows, information-flows]
shared_refs:
  - shared/constitution.md
  - shared/glossary.md
  - shared/stressor-frameworks.md
  - sad/template.md
  - sad/synthesis-explanation.md
---

# flow-analysis (S2)

Produces the Flow Analysis fragment of a SAD: a table of information flows between actors (a person, a group, a company, a software component external to the system). Each flow has a source, a destination, a payload, and a trigger.

Flow analysis is a deliberate departure from use-case-driven architectural thinking. O'Reilly L2745 lists as a canonical heuristic: "Flows are better than process or use case mapping." The reason: use cases describe scenarios as ordered sequences with branches and outcomes; flows are the underlying information paths regardless of which scenario triggers them. Stressors (S3) attack flows -- prevention, delay, duplication, reorder, reroute, corruption, replay, loss -- and the flow-stressing framework (`shared/stressor-frameworks.md` §5) is the bridge from S2 to S3.

---

## When to invoke

- The Naïve Architecture fragment (S1 output) exists and has been approved.
- The system has identifiable external actors (users, partners, schedulers, regulators, hardware) and a reasonable count of paths between them.
- The downstream `stressor-analysis` (S3) is about to begin -- flows feed flow-stressing.

## When NOT to invoke

- Naïve architecture does not exist yet (run S1 first).
- The request is to document use cases. Use cases enter the SAD in `residual-design` (S5), not here, and they DOCUMENT the resolved architecture rather than DRIVE it (R-16).
- The request is for a sequence diagram of internal component calls. That belongs to the §Static Architecture or §Behavioral Diagrams sections of the SAD, not the Flow Analysis section.
- The system has no meaningful external interaction (pure internal batch job with no actors). Even then, scheduler triggers count as flows; if there is genuinely nothing flowing, the system probably does not need a SAD.

## Pre-conditions

- The **S1b gate (Naïve Architecture) is marked `[x] approved`** in the project gate tracker (`FLOW.md`), not merely produced -- verify before producing (root `SKILL.md` §Gate approval protocol). S1b approval implies S1a (Business View) was approved first.
- `business-view.md` exists and is approved (gate S1a).
- `naive-architecture.md` exists and is approved (gate S1b).

Without S1's outputs, S2 has no Clients or Resources to draw flows between.

## Handoff contract

- **Consumes:** `naive-architecture.md` (the Clients and Resources between which flows are drawn) -- prior gate S1b must be `[x] approved`.
- **Produces:** `flow-analysis.md` (table: From / To / Information / Trigger; bidirectional channels split into two rows).
- **Lateral context to carry forward:** which flows feel fragile or under-specified (seeds for S3 flow-stressing); any actor/flow the naive cannot satisfy (coverage gaps S3 will stress).

---

## Workflow

### Step 1 -- Enumerate actors

An actor is anything external to the system that can be a source or destination of an information flow. From the Naïve Architecture, identify:

- All **Clients** -- end-user applications, partner systems, schedulers, mobile apps.
- All **external Resources** -- third-party APIs, payment processors, regulatory reporting endpoints, partner databases.
- The **organization** itself, when humans (operators, support, finance) act as senders or receivers.

The internal components (Managers, Engines, ResourceAccess) are NOT actors for flow analysis purposes. They are the system; flows are between actors AND the system.

A flow can be:

- Actor -> System (request, event ingestion, trigger).
- System -> Actor (response, notification, report, command to hardware).
- Actor -> Actor mediated by the System (a customer payment routed by the system to a partner).

### Step 2 -- For each pair of actors, identify the flows

For each meaningful actor pair, ask: what information moves between them, in what direction, on what trigger?

Each flow has:

| Column | Description |
|---|---|
| `#` | Sequential identifier (F1, F2, ...). |
| `From (Actor)` | Source actor. |
| `To (Actor)` | Destination actor (may be "System" if the system as a whole is the recipient before being demultiplexed internally). |
| `Information / Payload` | What moves. One line. Concrete. Not "data"; specify the data. |
| `Trigger` | The event or condition that causes the flow to occur. Mandatory. |

Bidirectional channels (a request expecting a response) are TWO flows, not one: F_n for the request, F_n+1 for the response.

### Step 3 -- Verify the table

Run these checks before declaring the fragment ready:

| Check | Verification |
|---|---|
| Every flow has a trigger | The Trigger column is non-empty for every row. |
| Triggers are concrete | Triggers are events or conditions, not "needed" or "when applicable". |
| No internal-only flows | No row has an internal component (Manager, Engine, ResourceAccess) as both From and To. |
| Direction is meaningful | The From / To pair is not symmetric in a single row (collapse into two rows if needed). |
| Payload is non-trivial | The Information / Payload column describes what flows, not "request" or "response" alone. |

If checks fail, refuse to write (see §Refusal conditions).

### Step 4 -- Note flows the naïve architecture cannot satisfy

After the table, add a short subsection (`Coverage notes`) listing any flow whose current naïve architecture has no obvious component to handle. This is informative for S3 (stressor-analysis) but does NOT change the naïve baseline -- the baseline is the control. If a flow has no component to handle it, it becomes a clear stressor candidate in S3.

**Coverage-notes discipline (feedback F-03 -- keeps S2 at altitude and avoids anchoring S3).** Three rules, or the auditor raises altitude/anchoring concerns (the audit-iter-4 HC-1/HC-2/HC-3 class):

- **(a) Stay at flow / system-actor altitude. Do NOT name internal components.** A Coverage note observes "this flow has no home in the naive set", not "`LedgerAccess` should handle it" -- naming a Manager/Engine/RA/Resource is S3+ work where the component is the subject. Dropping below flow altitude pre-commits decomposition the matrix has not yet justified.
- **(b) An out-of-naive-set driver gets a row-level pointer.** When a Trigger depends on an actor/driver absent from the naive component set (a temporal/clock/tick cadence, an external scheduler, a periodic job), add a **one-word pointer in the Trigger cell** (e.g. `Periodic (cadence: see Coverage notes)`) so the gap is visible from the table itself, not only buried in the prose below it.
- **(c) Frame pre-sensed stressors/volatilities as a SEED, not a closed set.** Any reference here to carried-forward DV-n / pre-sensed volatilities is explicitly "a starting menu for S3, not an exhaustive list" -- instruct S3 to run its own exhaustive lateral pass regardless (R-22). Pre-framing S3 too densely risks anchoring its walk to this list and suppressing genuinely lateral findings.

---

## Output contract

One fragment file in the project workspace:

### `flow-analysis.md`

Markdown fragment that fills SAD §Flow Analysis:

- One paragraph orienting the reader (actors enumerated, total flow count).
- The Flow Analysis table with columns: `#`, `From (Actor)`, `To (Actor)`, `Information / Payload`, `Trigger`.
- The Coverage notes subsection (optional, only if there are flows without obvious component support).

No frontmatter.

---

## Refusal conditions

| # | Trigger | Returned message |
|---|---|---|
| 1 | Any row has empty Trigger column. | List the offending rows. Trigger is mandatory because flow stressing (S3) starts from "what could prevent / delay / duplicate / reroute / corrupt this trigger event". A flow without a trigger cannot be stressed. |
| 2 | Trigger value is non-specific ("needed", "as required", "when applicable"). | List the offending rows. Demand a concrete event or condition. |
| 3 | Any row has an internal component (Manager, Engine, ResourceAccess) as From AND To. | Reject. Internal component-to-component communication is governed by the call rules table in §Static Architecture, not by flow analysis. Move that "flow" out of this table. |
| 4 | Use case scenarios (with branches and outcomes) submitted as flows. | Reject. A flow is an information path, not a scenario. Use cases enter the SAD at §Behavioral Diagrams in S5, not here. R-16. |
| 5 | The table has fewer than 3 flows in a system with multiple Clients. | Heuristic warning. A non-trivial system typically has many flows; very few suggests S1 missed actors or S2 missed bidirectional pairs. Ask the user to verify before proceeding to S3. |
| 6 | Naïve architecture fragment does not exist (pre-condition violation). | Refuse. Direct the user to run `business-discovery` (S1) first. |

---

## Worked example

See `sad/examples/ev-charging-sad.md` §2 (Flow Analysis) for a complete worked example. EV charging produces six flows:

| F# | From | To | Payload | Trigger |
|---|---|---|---|---|
| F1 | Customer | Charger | RFID tap (fob ID) | Customer presents fob |
| F2 | Charger | Cloud | Authenticate request | F1 |
| F3 | Cloud | Charger | Authenticate result + start command | F2 success |
| F4 | Charger | Cloud | Charge complete event | Energy delivered |
| F5 | Cloud | Charger | Stop + unlock command | F4 |
| F6 | Cloud | Customer | Subscription invoice | Periodic |

Six flows, each with a concrete trigger. Note F1 -> F2 -> F3 is a chain (F2 triggered by F1, F3 triggered by F2 success); the chain is captured by the Trigger column referencing prior flows. F6 has a non-flow trigger ("Periodic") -- a temporal trigger from a scheduler actor that the SAD will need to model (this is the kind of insight Coverage Notes captures).

---

## Why this sub-skill is separate from use-case mapping

Use cases mix three concerns: the actors (who), the flows (what moves), and the procedural steps (how the system responds). When use cases drive decomposition (R-16 violation), the procedural steps become Manager workflows and each new use case spawns a new Manager.

Flow analysis isolates the second concern only. The procedural response to a flow is the resolved-architecture concern of `residual-design` (S5), which assigns flow handling to Managers + Engines + ResourceAccess via call chains. Splitting flows from procedures keeps the architecture residue-driven (R-01) rather than scenario-driven.

Cited O'Reilly L2745 (Heuristic: "Flows are better than process or use case mapping.").

---

## References

- `shared/constitution.md` -- R-01 (residue-driven), R-16 (use cases document, not drive).
- `shared/glossary.md` -- "Stressor", "Random simulation" (flows are the substrate of flow-stressing).
- `shared/stressor-frameworks.md` §5 -- Flow stressing, the downstream framework that consumes this fragment.
- `sad/template.md` §Flow Analysis -- the SAD section this sub-skill fills.
- `sad/synthesis-explanation.md` §5 (use cases as documentation, not driver) -- the procedural justification for separating flows from use cases.
- `sad/examples/ev-charging-sad.md` §2 -- worked example.
- `residuality/residuality-md/residuality.md` L2745 -- O'Reilly's heuristic that motivates this sub-skill.
