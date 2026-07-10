---
name: contagion-analysis
description: Fourth sub-skill of the `sad` meta-skill. Builds the Contagion Matrix, Topological Residue Map, Business Residues Log, and Looping Signals from a typed Stressor Catalog. Surfaces hyperliminal coupling and refactor candidates. Applies the IDesign override (R-14) before any merge proposal. Invoke after the Stressor Catalog is closed; refuse to invoke while the catalog is still growing.
task_types: [contagion, build-matrix, hyperliminal, looping-signals]
shared_refs:
  - shared/constitution.md
  - shared/idesign-vocabulary.md
  - shared/decomposition-discipline.md
  - shared/kauffman-nkp.md
  - shared/glossary.md
  - sad/template.md
  - sad/synthesis-explanation.md
---

# contagion-analysis (S4)

Consumes the Stressor Catalog (S3 output) and produces interrelated sub-tables: the Contagion Matrix (Structural residues against components), the Topological Residue Map (geographic boundaries -- geography / tenancy / replication -- AND operational boundaries -- independent-scaling / failure-isolation / change-cadence / resource-profile / security-zone), the Business Residues Log (decisions-of-record with no software change), the Looping Signals table (Combined residues with explicit "survived by combination of" trace), and the Service Grouping Map (which components co-locate into which deployable units, R-25).

These sub-tables are the **diagnostic instruments** of the meta-skill. The Contagion Matrix surfaces hyperliminal coupling (two components affected by the same stressor are coupled even if no functional dependency connects them in code). The Topological Residue Map drives deployment topology decisions in S5. The Business Residues Log preserves decisions that would otherwise vanish from institutional memory. The Looping Signals are the strongest persuasive material in the SAD -- they are the moments where the architecture absorbs an unforeseen stressor for free. The Service Grouping Map turns the matrix's column signatures into the service / container decomposition S5 will draw (O'Reilly L1940-1943).

S4 does NOT make the refactor decisions. It surfaces refactor candidates. Decisions are made downstream in `residual-design` (S5) by an architect with distributed-systems judgment.

---

## When to invoke

- The Stressor Catalog (S3 output) is closed and approved.
- The catalog has at least one Structural residue (otherwise the Contagion Matrix is empty).
- The architect is ready to read the matrix carefully -- this sub-skill produces diagnostic output, not prescriptive output.

## When NOT to invoke

- Stressor Catalog is still growing. Premature matrix construction creates emotional attachment to columns; let the catalog stabilize first.
- The user is asking for refactor proposals as decisions. S4 surfaces candidates; S5 decides. Redirect if the user wants commitment to a specific refactor.
- The catalog has only Business and Combined residues (no Structural, no Topological). The four sub-tables would be vacuous; the analysis is incomplete or the typing is wrong. Send back to S3.

## Pre-conditions

- The **S3 gate is marked `[x] approved`** in the project gate tracker (`FLOW.md`), not merely produced -- verify before producing (root `SKILL.md` §Gate approval protocol).
- `stressor-catalog.md` exists and is approved.
- The catalog contains at least one `Structural`-typed stressor (matrix needs at least one row).
- The Naïve Architecture (S1) lists the components that will populate the matrix columns.

## Handoff contract

- **Consumes:** `stressor-catalog.md` (the typed stressors -- Structural ones become matrix columns; all feed random simulation) + `naive-architecture.md` (the components stressed) -- prior gate S3 must be `[x] approved` with >=1 Structural stressor.
- **Produces:** `contagion-analysis.md` (Contagion Matrix + NKP reading + Hyperliminal Coupling Map + Topological Residue Map + Business Residue table + Looping note + Service Grouping Map).
- **Lateral context to carry forward:** the matrix hot-spots (high-K columns S5 turns into residues), the surprising hyperliminal couplings (invisible in the call graph -- canonical NFR sources S5 must document), and any IDesign override (R-14) decisions where layer discipline beat a matrix-driven merge signal.

## Workflow

### Step 1 -- Build the Contagion Matrix

The matrix has stressors as rows (Structural residues plus Topological residues with component impact, marked `(T)`) and components as columns (from the Naïve Architecture). Each cell is `1` or `0`:

- `1` if the stressor affects the component's operation.
- `0` if it does not.

Operations on the same ResourceAccess that have distinct stress profiles should be split into separate columns (e.g., `ChargerAccess.StartCharge`, `ChargerAccess.StopCharge`, `ChargerAccess.Unlock` are three columns in the EV charging example). The granularity exposes bugs like the workflow-coupling failure between Stop and Unlock that the book's worked example surfaces.

Compute `Σ Row` (per stressor, count of components affected) and `Σ Column` (per component, count of stressors that affect it). These totals are the diagnostic signal for the readings in Step 2.

Topological residues with component impact go in the matrix marked `(T)` AND in the Topological Residue Map (Step 3). Pure Topological residues without component impact stay only in the Topological Residue Map. Business and Combined residues never enter the matrix.

### Step 2 -- Compute NKP totals

Per O'Reilly L2520-2522 (literal): "The number of 1's in the network gives an approximation of K in this network. The number of stressors and components/functions represents N." After the matrix is built, compute the three Kauffman parameters as approximations -- not as exact numbers but as markers for refactor decisions.

#### 2.1 N (size of the bipartite friction network)

N = **number of stressors + number of components/functions** in the matrix. This is a deliberate framing: the matrix is a bipartite graph with stressors on one axis and components on the other, and N counts both kinds of nodes.

A common mistake is to count only components (N = 4 if there are 4 components). **The book is explicit that stressors count too** -- adding stressors to the catalog increases N and, per L836-837 ("as N and K rise, the number of attractors rises"), increases attractor count in the system. This matters because thin stressor catalogs underestimate N and produce a falsely-low estimate of architectural complexity.

#### 2.2 K (count of coupling edges revealed under stress)

K = **count of all `1` cells in the matrix**. Per L2520-2521 (literal). This is the number of stressor-to-component links the random simulation has exposed.

K is NOT the same as the count of HTTP calls in the call graph. K counts coupling under stress -- including hyperliminal coupling that is invisible in the static call graph. A system with K much higher than its call-graph link count is a system with significant hidden coupling.

#### 2.3 P (predictability bias)

P is qualitative, not numeric. Per L831-836 (literal): "P is the node's bias - its tendency toward similar behavior in response to repeated stimuli... interfaces, uniform error handling, service-oriented ideas, all contribute to biasing the components toward a particular behavior."

Assess P as `low` / `medium` / `high` using this checklist (each tick raises P):

| Consistency axis | Present? |
|---|---|
| Components share a uniform error model | |
| Components share a uniform authentication / authorization mechanism | |
| Components expose stable contracts via interfaces | |
| Components use a uniform serialization format | |
| Components share a uniform tracing / observability convention | |
| Components share a uniform retry / timeout / circuit-breaker policy | |
| Components honor a uniform event envelope (if event-driven) | |

- 0-2 ticks -> P = `low` (high architectural chaos; each component reinvents discipline)
- 3-5 ticks -> P = `medium` (some shared discipline; uneven)
- 6-7 ticks -> P = `high` (strong shared discipline; criticality friendly)

#### 2.4 NKP totals output

The NKP block goes immediately after the Contagion Matrix in the SAD fragment:

| Parameter | Value | Approximation source |
|---|---|---|
| N | `<#stressors>` + `<#components>` = `<total>` | This matrix (O'Reilly L2522) |
| K | `<sum of 1s>` | This matrix (O'Reilly L2520) |
| P | `low` / `medium` / `high` -- `<one-paragraph qualitative assessment per checklist>` | Cross-cutting consistency assessment (O'Reilly L831-836) |

#### 2.5 Reading direction

Per O'Reilly L2526-2528 (literal): "An analysis of this matrix will allow us to try and **reduce K, optimize N, and decide which measures we need to take to optimize P**."

This gives the three architectural action verbs:

- **Reduce K** -- always toward lower K. High K means high coupling exposure under stress; refactor candidates target K reduction (decouple, partition, introduce abstraction).
- **Optimize N** -- find the critical point, not minimize. Too low N means components are doing too much; too high N means microservice-explosion overhead. Target the regime where N supports the stressor catalog without over-fragmentation.
- **Optimize P** -- typically upward. Each tick on the P checklist that becomes true (uniform interfaces, uniform error model, etc.) raises P and lets the system carry higher K without losing criticality.

NKP is NOT an exact formula. Per L2658-2664 (literal): "It would be possible to teach this as a simple algorithm--fill in the matrix and look for the seven triggers and refactor from there. However, this exercise leads to a multitude of conversations that uncovers more details about how the system might be best designed. These are too many and too varied to be captured in a single step and there is value to using this as a tool to aid discussion and debate."

The NKP totals are markers, not targets. Their value is in catalyzing the conversation that produces the residual decomposition. Two architectures with identical NKP triples can be very different; the totals point at where to look, not what to do.

### Step 3 -- Read the matrix

Apply the seven canonical reading patterns from the template §Refactor Triggers. Each reading produces refactor candidates:

| # | Pattern | Detect by | Refactor candidate |
|---|---|---|---|
| 1 | **Hot row** | Stressor with high Σ Row (touches many components) | The stressor is high-impact and reveals hyperliminal coupling. Document the implicit non-functional contracts between the touched components. May indicate a missing abstraction or a fundamental architectural shift. |
| 2 | **Hot column** | Component with high Σ Column (touched by many stressors) | The component is doing too much. Consider splitting (lowering N at this point in the system) or hardening with redundancy (if the load is real and structural). **Mark the hottest columns as `PoC recommended`**: a hot-spot carries the most technical uncertainty, so a proof-of-concept that validates its chosen residue is worth scheduling in implementation. This complements the Ri (which measures survival) with a viability check (can this hot-spot's solution actually be built as designed?). |
| 3 | **Multiple 1s in same row** | Two or more components react to the same stressor | Hyperliminal coupling. Document the implicit contract between them: what does one need to know about the other when this stressor hits? |
| 4 | **Identical column signatures** | Two columns have the same pattern of 1s across all rows | Merge candidate -- **but apply the IDesign override (Step 4) before merging.** |
| 5 | **Globally high K** | Many 1s overall, dense matrix | The pattern or decomposition choice is likely wrong. Refactor before commit. Consider whether the Naïve Architecture was too monolithic (too few components carrying too much stress) or too fragmented. |
| 6 | **Zero-total columns** | Component with Σ Column = 0 (never touched by any stressor) | Either the component is invulnerable (rare and suspicious) or the stressor catalog is incomplete (likely). Investigate. May indicate speculative design (R-09). |
| 7 | **Stressor combinations** | Multiple stressors hit overlapping components | Build an attack/failure tree for the combination. Surfaces chains where a primary stressor cascades into secondary failures across components that are individually OK. |

For each finding, write a short refactor candidate description (1-3 sentences) into the matrix-reading section. Do NOT yet commit to the refactor.

### Step 4 -- Build the Hyperliminal Coupling Map

The most important insight the matrix produces. O'Reilly L1082-1111: "Sometimes when an architecture is hit by a particular stressor two or more components will be affected. When this happens, it is possible to say that these components are coupled. This is a particularly nasty form of coupling because it is invisible right up to the moment at which the stressor hits the system." L1934-1937 (literal): "anywhere there are two 1's in the same row indicates this hidden coupling."

For every row in the Contagion Matrix where Σ Row >= 2, record the coupling in the Hyperliminal Coupling Map. This is a deliberate, focused extraction of the matrix readings, separate from the prose findings of Step 2.

#### 4.1 Why this map exists

Hyperliminal coupling is the canonical source of non-functional requirements (O'Reilly L1114-1120, literal): "Since these invisible couplings are not functional, they fall under the realm of non-functional and can help architects to navigate the traditional problem of non-functional requirements. Non-functional requirements have always been a difficult issue for software engineering. The assumption has always been that they are difficult to uncover. Here we will state that they simply don't exist in a way that is discoverable by any other means than random simulation."

This means: a SAD that has no Hyperliminal Coupling Map has no empirical basis for its non-functional requirements. The NFRs in S5 derive directly from rows of this map (along with topology rows from §Topological Residue Map and rows of §Business Residues Log -- R-15 traceability).

#### 4.2 Classify each coupling

For each multi-1 row, classify the coupling's nature:

| Nature | Definition | Typical signal |
|---|---|---|
| **Intrinsic** | The coupling is inherent to the business domain. Removing it would mean removing the responsibility one of the components has. | Regulation always couples auditing components; a financial transaction always couples balance, ledger, and notification. |
| **Extrinsic** | The coupling is an artifact of the current decomposition. A different decomposition could break it. | A Manager and an Engine accidentally share a stressor because the Manager pulled activity logic that should have been in the Engine. |

The classification matters because it determines the architectural response in Step 4.3.

#### 4.3 Choose the architectural response per coupling

| Response | When to choose | Output |
|---|---|---|
| **Document NFR contract** | Most common. The coupling is acceptable (intrinsic) or the cost of decoupling exceeds the cost of explicit coordination (extrinsic but small). | One or more NFRs in §Derived NFRs (S5) specifying how the coupled components coordinate under stress -- atomic operation, eventual consistency window, idempotency contract, retry semantics, replay protocol. |
| **Decouple** | When the coupling is extrinsic AND the cost of carrying it forward is high (the matrix shows the residue should not have been entangled). | A Structural refactor candidate added to the §Reading the matrix prose findings. May propose a new component, a split, or a re-typed responsibility. |
| **Accept and harden** | When the coupling is intrinsic and no NFR contract beyond standard reliability is meaningful. | Operational uplift: redundancy, observability, monitoring on the coupled components. No new NFR entry (or a minimal one); the response is operational, not architectural. |

For every row, the response must be explicit. "It depends" or "investigate" is not a response -- close it down before writing the fragment.

#### 4.4 Output -- the Hyperliminal Coupling Map table

Columns:

| Column | Required | Format |
|---|---|---|
| `Stressor #` | Yes | Reference to the catalog row. |
| `Affected Components` | Yes | List of components with `1` in that row. Format: `Component A + Component B + Component C`. |
| `Coupling Nature` | Yes | `intrinsic` or `extrinsic`. |
| `Architectural Response` | Yes | `Document NFR contract` / `Decouple` / `Accept and harden`. |
| `NFR Source (for §Derived NFRs)` | Yes for `Document NFR contract` and `Accept and harden`; `(refactor)` for `Decouple` | The reference S5 will use when writing the NFR. Format: `Hyperliminal Coupling #N` matches the row number in this map. |

Example shape (from the user's working example):

| Stressor # | Affected Components | Coupling Nature | Architectural Response | NFR Source |
|---|---|---|---|---|
| 1 | Tick + Candle + Replay | extrinsic | Decouple | (refactor) |
| 2 | Billing + Storage + Audit | intrinsic | Document NFR contract | Hyperliminal Coupling #2 |
| 3 | Session + Cache + Routing | intrinsic | Document NFR contract | Hyperliminal Coupling #3 |
| 4 | Window + Indicators | extrinsic | Decouple | (refactor) |

The map is a focused extraction. It does not duplicate the matrix; it surfaces only what matters most.

### Step 5 -- Build the Topological Residue Map

For every `Topological`-typed stressor in the catalog, add a row to the Topological Residue Map. Columns:

| Column | Required | Format |
|---|---|---|
| `Residue #` | Yes | Reference to the catalog row. |
| `Topology Driver` | Yes | The dimension. Two families (R-19): **geographic / jurisdictional** -- geography, tenancy, replication, latency zone, sovereignty (answer *where* a unit runs); **operational** -- `independent-scaling`, `failure-isolation` (blast-radius), `change-cadence`, `resource-profile`, `security-zone` (answer *which components must run as a separate process*). Operational drivers are what justify splitting one logical service into multiple deployable units; without one, co-location is the default (R-25). |
| `Deployment Decision` | Yes | What the deployment topology becomes under this residue. |
| `Affected Components` | Yes | Components that are bounded by the topology decision (typically a subset of the Naïve Architecture). |
| `Cross-Boundary Constraints` | Yes | What is `Allowed` and what is `Forbidden` across the topology boundary. Without this, the residue is incomplete and S5 cannot derive the deployment unit boundary. |

### Step 6 -- Build the Business Residues Log

For every `Business`-typed stressor, add a row to the Business Residues Log. Columns:

| Column | Required | Format |
|---|---|---|
| `Residue #` | Yes | Reference to the catalog row. |
| `Stressor` | Yes | Restated from the catalog. |
| `Attractor` | Yes | The business state under this stressor. |
| `Business Decision` | Yes | What the business decided to do (e.g., pivot, lobby, partner, raise margins, plan capacity). |
| `Rationale for No Software Change` | Yes | Why the architecture does NOT respond. This is the decision-of-record that prevents the question from being relitigated later (guardrail #3). |

### Step 7 -- Build the Looping Signals table

For every `Combined`-typed stressor, add a row to the Looping Signals table. Columns:

| Column | Required | Format |
|---|---|---|
| `Residue #` | Yes | Reference to the catalog row. |
| `Stressor` | Yes | Restated. |
| `Survived by Combination of` | Yes | The explicit list of residue numbers whose combination handles this stressor. Without the trace, the Combined typing is unfounded (R-17). |
| `Notes` | Recommended | Why the combination works. This is the persuasive material -- the moment where a residue added for one specific stressor turns out to absorb a different unforeseen one. |

### Step 8 -- Apply the IDesign override (R-14) before any merge proposal

When Step 3 surfaces an "identical column signatures" finding (Pattern #4), do NOT propose the merge in the output without first checking whether the two columns belong to the same IDesign layer:

| Pair | Override fires? | Action |
|---|---|---|
| Engine + Engine in the same volatility bounded context | No | Merge candidate is valid (same layer). |
| ResourceAccess + ResourceAccess for the same Resource family | No | Merge candidate is valid (same layer). |
| Manager + Manager that own the same logical workflow | No | Merge candidate is valid (same layer, rare). |
| Manager + Engine | **Yes** | Reject. Manager-Engine pairs that co-evolve have similar signatures because they participate in the same use cases; they are structurally separate by IDesign (stateful workflow vs stateless logic). Document the override inline. |
| Manager + ResourceAccess | **Yes** | Reject. Cross-layer collapse. |
| Engine + ResourceAccess | **Yes** | Reject. R-07 atomic-verb discipline violated by merge. |
| ResourceAccess + Resource | **Yes** | Reject. R-03 collapses. |
| Anything + Utility | **Yes** | Reject. Cappuccino test fails for the merged result. |

For every override that fires, add an explicit note in the matrix-reading section: "**IDesign Override applied.** The matrix suggests [Component A] and [Component B] are merge candidates. They are not. [Reason]." This note serves both as documentation and as auditor-friendly evidence that R-14 was enforced.

### Step 9 -- Build the Service Grouping Map (R-25)

The matrix plus the Manager decomposition tell you how components group into separately deployable units (services / containers). The repo's deployment style is **actor-based**: **one Manager, one service** by default (R-25). This step records that grouping so S5 does not improvise the C4 Container decomposition.

This is NOT the same reading as Step 3 Pattern #4 / Step 8 (merge of *logical* components, same-layer, R-14). Step 9 is about **physical co-location**: which logical components run in the same process / deployable unit.

#### 9.1 One service per Manager

Each Manager is its own deployable unit. The Manager's existence is already justified by a Structural residue (R-18, from any of the six frameworks); that residue justifies its service -- no separate Topological residue is needed for the per-Manager boundary. Distinct Managers encapsulate distinct workflow volatilities, so their column signatures (stress profiles) differ, and distinct services emerge naturally.

#### 9.2 Co-locate private Engines/RAs with their Manager

For each Manager, the Engines and ResourceAccess used **only** by that Manager co-locate inside its service. They share the Manager's stress profile and dependency path -- this is O'Reilly L1940-1943 ("same stress profile -> combine -> reduce N") applied *within* the Manager's cluster. Do not give a single-Manager Engine/RA its own service.

#### 9.3 Resolve shared Engines/RAs by stress

An Engine/RA used by 2+ Managers is the case the matrix and boundary stressing resolve:

- If a boundary stressor produced an operational Topological residue on it (`resource-profile`, `independent-scaling`, etc.), promote it to its own service.
- Otherwise, either duplicate it per Manager (if cheap and stateless) or co-locate it with its dominant Manager. Record the choice and its rationale.

Collapsing two Managers into one service is allowed only when they share a near-identical stress profile -- and that is also an R-11 signal to check whether they are really one Manager.

#### 9.3.1 A Client-reachable promoted unit needs an entry Manager -- decide it here

A promoted unit (9.3) is normally an internal shared service: the Managers call it, no Client does (the `MatchingService` / `RegulationService` Engines in the TradeMe example are Manager-called, Manager-less by design). But if the promotion produces a unit a **Client** invokes directly -- the canonical case is a CQRS / read-model / query or API surface split out for `independent-scaling` -- that unit cannot be a bare Engine/RA: a Client may only call a Manager (R-03 / R-04 (a)). It needs an **entry Manager** owning the entry workflow, with the promoted Engine/RA as its private component.

**Decide that Manager here, in S4, not in S5.** Judge Client-reachability from the naïve call topology (S1b) the matrix was built on: if a Client edge would land on this unit, add the entry Manager to its `IDesign components` now. Deferring it to the S5 §2.8 entry-Manager check forces a full S4 reopen -- the S5 gate would otherwise discover a Client-facing service with no Manager and bounce the grouping map back. The read/query split must carry its Manager from the start.

#### 9.4 Output -- the Service Grouping Map table

Columns:

| Column | Required | Format |
|---|---|---|
| `Service / Deployable Unit` | Yes | The name of the service / container (typically named for its Manager, e.g., `MembershipService`; or for a shared component, e.g., `MatchingService`). |
| `IDesign components` | Yes | The IDesign components running inside this unit (the Manager + its private Engines/RAs; or the shared component). |
| `Grouping basis` | Yes | For a Manager service: the Manager's Structural residue # (R-18). For a shared-component service: the operational Topological residue # that promoted it (R-19). For a rare two-Manager co-location: the shared stress profile. |

Every Manager appears as its own service (or, exceptionally, co-located with a documented shared profile). Every shared component in its own service cites an operational Topological residue. A single-Manager Engine/RA given its own service with no driver, or all Managers collapsed into one service despite divergent profiles, is an R-25 violation surfaced here, not downstream.

**The `Service / Deployable Unit` column is the canonical authority for service / deployable-unit names.** S5 (§C4 Model container view) and every downstream fragment reuse these names verbatim; service names are not re-coined elsewhere. If a reopen renames a service, rename it here first, then propagate.

S5 consumes this map directly: the §C4 Model container view has one `container` per row of this map.

### Step 10 -- Hygiene checks before writing the fragment

| Check | Verification | Rule |
|---|---|---|
| Matrix has Σ Row and Σ Column | Last row is column totals; last column is row totals. | -- |
| **NKP totals computed** | N, K, P totals reported immediately after the matrix. N counts both stressors AND components (not components only). | This sub-skill, Step 2, O'Reilly L2520-2522 |
| **N counts stressors + components** | N is explicitly the sum, not just one side. | O'Reilly L2522 literal |
| **Counts reconcile (script-backed)** | After drafting and **before** parking the fragment, run the bundled `scripts/fragment-checks/check_counts.py <fragment>`. Every operation-column count cited in prose, `N = rows + columns`, and `Σ-Col total == K` MUST reconcile with the matrix as printed; the script hard-fails on drift (this is the audit-iter-6 "17 operation-columns vs 14" + "N = 56 vs 53" class). Re-derive every aggregate from the table -- never hand-carry "17" / "56" across an edit. | R-13 count-consistency (feedback F-02) |
| **P assessment uses the 7-axis checklist** | P value (low / medium / high) is justified by which consistency axes are present. | This sub-skill, Step 2.3 |
| Topological residues with `(T)` annotation | Topological-typed rows in the matrix are marked. | R-13 |
| **Every multi-1 row in Hyperliminal Coupling Map** | Every matrix row with Σ Row >= 2 has a corresponding entry in §Hyperliminal Coupling Map with Coupling Nature + Architectural Response populated. | This sub-skill, Step 4 |
| **Every Coupling Map row has an explicit response** | No row says "investigate" / "it depends" / "TBD". Each is `Document NFR contract` / `Decouple` / `Accept and harden`. | This sub-skill, Step 4.3 |
| **Document-NFR-contract rows produce NFR sources** | Every Coupling Map row with response `Document NFR contract` has a `NFR Source` reference that S5 will consume. | R-15 (downstream) |
| All Topological residues in the map | Every Topological-typed catalog row is in §Topological Residue Map. | R-19 (downstream) |
| All Business residues in the log | Every Business-typed catalog row is in §Business Residues Log. | Guardrail #3 |
| All Combined residues in Looping Signals | Every Combined-typed catalog row is in §Looping Signals. | R-17 + guardrail #8 |
| Business residues have rationale | Every row of the Business Residues Log has the `Rationale for No Software Change` column populated. | Guardrail #3 |
| Topological residues have cross-boundary constraints | Every row of the Topological Residue Map has `Allowed` and `Forbidden` cross-boundary flows declared. | R-19 |
| Looping Signals have explicit combination trace | Every row of the Looping Signals table has `Survived by Combination of #X, #Y` with valid residue numbers. | R-17 |
| No cross-layer merges proposed | Every merge candidate in the matrix-reading section is within the same IDesign layer, or the IDesign override note is present. | R-14 + guardrail #7 |
| Service Grouping Map present and grounded | Every Manager is its own deployable unit (or a documented two-Manager co-location); its private Engines/RAs co-locate with it (not split out); every shared Engine/RA in its own unit cites an operational Topological residue #; every component appears in exactly one row. | R-25 |

If any deterministic check fails, refuse to write (see §Refusal conditions).

---

## Output contract

One fragment file in the project workspace:

### `contagion-analysis.md`

Markdown fragment that fills SAD §Contagion Matrix, §NKP Totals, §Hyperliminal Coupling Map, §Topological Residue Map, §Business Residues Log, §Looping Signals, §Service Grouping Map. Structure:

1. One paragraph orienting the reader: total residue count by type, dimensions of the matrix (rows × columns), count of hyperliminal couplings detected, summary NKP triple.
2. **§Contagion Matrix (Structural Residues)** -- the matrix with Σ Row and Σ Column.
3. **§NKP Totals** -- N, K, P table from Step 2 with one-paragraph reading direction (which lever to push: reduce K, optimize N, optimize P).
4. **§Reading the matrix** -- one numbered finding per pattern hit (hot rows, hot columns, etc.). Each finding has 1-3 sentences describing the refactor candidate. Each merge candidate has an IDesign override note where applicable.
5. **§Hyperliminal Coupling Map** -- table with the five columns from Step 4.4 (`Stressor #` / `Affected Components` / `Coupling Nature` / `Architectural Response` / `NFR Source`). Every matrix row with Σ Row >= 2 produces a row here. This is the canonical source of non-functional requirements (cited O'Reilly L1114-1120) that S5 will consume when writing §Derived NFRs.
6. **§Topological Residue Map** -- table with the five columns from Step 5.
7. **§Business Residues Log** -- table with the five columns from Step 6. Optionally followed by short notes on residues that bridge to Structural decisions elsewhere.
8. **§Looping Signals (Combined Residues)** -- table with the four columns from Step 7. Optionally followed by a short closing paragraph on what the mathematical leverage of these Combined residues represents (cite `shared/glossary.md` "Mathematical leverage").
9. **§Service Grouping Map** -- table with the three columns from Step 9.4 (`Service / Deployable Unit` / `IDesign components` / `Grouping basis`). One service per Manager (with its private Engines/RAs co-located) plus one service per promoted shared component; S5 maps one C4 Container per row (R-25).

No frontmatter.

---

## Refusal conditions

| # | Trigger | Rule | Returned message |
|---|---|---|---|
| 1 | Stressor Catalog (S3 output) does not exist or is unapproved. | Pre-condition | Refuse. Direct the user to run `stressor-analysis` (S3) first. |
| 2 | Catalog has no Structural residues. | Pre-condition | Refuse. The Contagion Matrix would be empty. Either the typing in S3 is wrong (re-type) or the analysis is incomplete (re-run S3 with more frameworks). |
| 3 | Matrix lacks Σ Row or Σ Column. | Hygiene | Reject. Recompute. The totals are the diagnostic signal. |
| 4 | A merge proposal in the matrix-reading section is cross-layer (Manager-Engine, Engine-RA, etc.) WITHOUT the IDesign Override note. | R-14 + guardrail #7 | List the cross-layer pair. Either add the IDesign Override note rejecting the merge, or do not propose the merge. |
| 5 | A Topological-typed catalog row is missing from the Topological Residue Map. | R-13 routing | List the missing row. Add it to the map. |
| 6 | A Topological Residue Map row lacks `Cross-Boundary Constraints`. | R-19 | List the offending row. The deployment unit boundary cannot be derived without the constraints; S5 will refuse downstream. |
| 7 | A Business-typed catalog row is missing from the Business Residues Log. | Guardrail #3 | List the missing row. |
| 8 | A Business Residues Log row lacks `Rationale for No Software Change`. | Guardrail #3 | List the offending row. The decision-of-record requires the rationale; without it, the business decision is undocumented and the architecture appears to have a gap that future architects cannot interpret. |
| 9 | A Combined-typed catalog row is missing from the Looping Signals table. | R-17 + guardrail #8 | List the missing row. Add it. |
| 10 | A Looping Signals row lacks `Survived by Combination of` or references invalid residue numbers. | R-17 | List the offending row. Without an explicit valid trace, the Combined typing is unfounded; either correct the trace or re-type as Structural / Business. |
| 11 | A Business or Combined residue appears in the Contagion Matrix as a row. | R-13 routing | List the offending row. Remove it from the matrix; place it in the correct sub-table per its type. |
| 12 | A matrix row with Σ Row >= 2 is missing from the Hyperliminal Coupling Map. | This sub-skill Step 3 | List the offending matrix row. Every multi-1 row must enter the Coupling Map because every multi-1 row is hidden coupling that produces an NFR (O'Reilly L1114-1120). |
| 13 | A Hyperliminal Coupling Map row has an empty or non-decisive Architectural Response (e.g., "investigate", "TBD", "it depends"). | This sub-skill Step 3.3 | List the offending row. Close the decision: `Document NFR contract` / `Decouple` / `Accept and harden`. |
| 14 | A Hyperliminal Coupling Map row with Architectural Response = `Document NFR contract` has no `NFR Source` reference. | R-15 (downstream) | List the offending row. The NFR Source is what S5 will consume to write the §Derived NFRs row; without it, the NFR cannot be traced back per R-15. |
| 15 | NKP totals missing or N counts components only (not stressors + components). | O'Reilly L2520-2522 | Recompute. N = #stressors + #components per the book; K = sum of 1s; P = qualitative low/medium/high with the 7-axis consistency checklist. |
| 16 | §Service Grouping Map is missing, OR a single-Manager Engine/RA is given its own service with no operational driver, OR all Managers are collapsed into one service despite divergent stress profiles, OR a shared Engine/RA is split out without citing an operational Topological residue. | R-25 | Apply the actor-style default: one Manager per service with its private Engines/RAs co-located. Co-locate single-Manager Engines with their Manager. Promote a shared Engine/RA only with an operational Topological residue (backtrack to S3 boundary stressing). |
| 17 | A component in the matrix appears in zero rows, or in more than one row, of the §Service Grouping Map. | R-25 | Every component runs in exactly one deployable unit. List the offending component; assign it to exactly one row. |
| 18 | A §Service Grouping Map row is reachable by a Client (a query / read-model / API surface, typically a promoted unit per 9.3.1) but lists no Manager among its `IDesign components`. | R-03 / R-04 (a) + R-25 | A Client may only call a Manager. Add an entry Manager to that unit here, with the promoted Engine/RA as its private component. Do not defer the decision to S5 -- that forces a full S4 reopen. |

---

## Worked example

See `sad/examples/ev-charging-sad.md` §4 (Contagion Matrix), §5 (Topological Residue Map), §6 (Business Residues Log), §7 (Looping Signals) for a complete worked example. Key features of the worked example:

- **9 rows in the matrix** (8 Structural + 1 Topological with component impact `(T)` for #13). Plus row 9b which decomposes "server failure" into the distinct sub-case of "server fails *during* charge" to expose the Stop / Unlock workflow bug.
- **15 columns in the matrix** at fine granularity (ChargerAccess split into Start / Stop / Unlock).
- **Hot row #3** (failed login, Σ=8) reshapes 8 components and introduces the ALPR subsystem. This is the *pivotal* residue.
- **Identical column signatures BillingMgr + BillingEngine** -- IDesign Override applied, merge rejected, override note documented inline.
- **One Topological residue** (#13 privacy regulation) producing a per-country deployment unit.
- **Five Business residues** in the log (#4, #5, #6, #7, #11), each with explicit rationale for no software change.
- **Two Looping Signals** (#14 ICE-ing, #15 AFIR 2023). The AFIR signal is the canonical example of mathematical leverage: a residue added for a broken plastic key fob ten years earlier absorbs an EU regulation without architectural rewrite.

---

## Why these rules

- **R-13.** Typing in S3 is the routing key for the five sub-tables in S4 (matrix + coupling map + topology + business + looping). Untyped stressors are unroutable.
- **R-14.** The IDesign override is the most important place where IDesign discipline actively saves residuality from a false positive. Manager-Engine pairs with similar matrix signatures are NOT merge candidates.
- **R-15 / Hyperliminal Coupling Map.** Per O'Reilly L1114-1120, hidden couplings revealed by the matrix ARE the non-functional requirements of the system. The Coupling Map is the canonical source of NFRs that S5 will consume; a SAD without a populated Coupling Map has no empirical basis for its NFRs.
- **R-17.** Looping Signals make the strongest persuasive material in the SAD findable and traceable. Burying them in prose loses the evidence of approaching criticality.
- **R-19.** Topology residues without cross-boundary constraints cannot inform a deployment diagram. The constraints are the contract between regions / tenancies / replicas.
- **Guardrails #3 and #8.** Business decisions and Combined residues are easy to lose -- they don't show up in code. Recording them is the only way they survive to the next iteration of the SAD or to a future architect.

---

## References

- `shared/constitution.md` -- R-13, R-14, R-17, R-19.
- `shared/idesign-vocabulary.md` §6 -- the IDesign Override walkthrough with the BillingMgr / BillingEngine example.
- `shared/decomposition-discipline.md` -- guardrails #3, #7, #8 expanded with EV examples.
- `shared/kauffman-nkp.md` -- the NKP framing of what the matrix surfaces (hyperliminal coupling, K signals).
- `shared/glossary.md` -- "Contagion matrix", "Hyperliminal coupling", "Looping", "Mathematical leverage".
- `sad/template.md` §Contagion Matrix, §Refactor Triggers, §IDesign Override, §Topological Residue Map, §Business Residues Log, §Looping Signals.
- `sad/synthesis-explanation.md` §6 Decisions 2, 3, 6 -- the doctrinal anchors.
- `sad/examples/ev-charging-sad.md` §4-§7 -- worked example.
- `residuality/residuality-md/residuality.md` -- book citations used in this SKILL.md:
  - L831-837 -- P definition + "as N and K rise, the number of attractors rises, and as P rises, the number of attractors fall".
  - L1082-1111 -- Hyperliminal Coupling chapter (invisible coupling, contagion).
  - L1114-1120 (literal) -- "Since these invisible couplings are not functional, they fall under the realm of non-functional and can help architects to navigate the traditional problem of non-functional requirements."
  - L1819-1840 -- mathematical leverage justifying Looping Signals.
  - L1886-1957 -- NKP analysis with matrices.
  - L1934-1937 (literal) -- "anywhere there are two 1's in the same row indicates this hidden coupling".
  - L1940-1942 -- hidden cohesion / merge signal.
  - L2520-2522 (literal) -- "The number of 1's in the network gives an approximation of K in this network. The number of stressors and components/functions represents N."
  - L2526-2528 (literal) -- "An analysis of this matrix will allow us to try and reduce K, optimize N, and decide which measures we need to take to optimize P."
  - L2544-2647 -- the seven matrix triggers (row totals highest / column totals highest / multiple 1s in row / similar responses / many high numbers / combinations / untouched components).
  - L2658-2664 (literal) -- "It would be possible to teach this as a simple algorithm... However, this exercise leads to a multitude of conversations... there is value to using this as a tool to aid discussion and debate."
