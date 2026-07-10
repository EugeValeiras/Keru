---
name: sad-auditor
description: Cross-cutting sub-skill of the `sad` meta-skill. Validates a fragment, the assembled SAD, a diff, or an S8 handoff + its consumer integration against constitution rules R-01 to R-27, the eight guardrails, and the RDAG conformance checks (CHK-01 to CHK-17). Runs deterministic checks first, heuristic checks second; produces `audit.md` with violations (citing R-NN / guardrail # / CHK-NN), traceability gaps, fix proposals in unified-diff format, and optional open accepted exceptions. No `--force` flag; closure requires resolving findings or documenting accepted exceptions with rationale. Invoke at any sub-skill gate, after S7 assembly, after any fragment edit, or after an S8 handoff to check integration state.
task_types: [audit, validate-sad, check-fragment, audit-diff, audit-handoff]
shared_refs:
  - shared/constitution.md
  - shared/decomposition-discipline.md
  - shared/idesign-vocabulary.md
  - shared/architectural-walking.md
  - shared/glossary.md
  - sad/template.md
  - sad/synthesis-explanation.md
  - sdd-interface/standard/rdag-standard.md
  - sdd-interface/standard/rdag-conformance.md
---

# sad-auditor (cross-cutting)

The auditor sub-skill. Validates the output of any other sub-skill against constitution rules R-01 to R-27 and the eight guardrails from `shared/decomposition-discipline.md`. Produces `audit.md` -- a separate artifact, not embedded in the SAD -- containing violations, traceability gaps, fix proposals in unified-diff format, and any accepted-exception entries the architect has documented.

The auditor's discipline is **conservative**: it does not silently fix anything. Every violation is reported with a proposed fix, but applying the fix is the responsibility of the sub-skill that produced the offending artifact. The auditor closes only when violations are resolved or explicitly accepted with rationale (R-22-style accepted exceptions). There is no `--force` flag.

The auditor is the only sub-skill that runs ACROSS the meta-skill rather than producing one specific SAD section. It can be invoked after any fragment is produced, after S7 assembles the SAD, or after any fragment is edited.

---

## When to invoke

- Immediately after a sequential sub-skill produces a fragment (auditor in `by-fragment` mode, before user approval).
- After S7 assembles the SAD (auditor in `end-to-end` mode).
- After any fragment is edited in an iteration loop (auditor in `diff` mode, scoped to the changed fragment plus downstream impacts).
- Before shipping the SAD to stakeholders (final `end-to-end` audit; user has reviewed and resolved all violations).
- After an S8 handoff is emitted, or to check a consumer's integration state (auditor in `handoff` mode). This catches a botched integration: the wrong *kind* of constitution in place (a SAD-workflow constitution used as the consumer's), artifacts not landed at the release directory, a missing `PENDING` status, or a non-verbatim principle.

## When NOT to invoke

- Before any fragment exists (the auditor needs at least one fragment to audit; refuse with a pre-condition message).
- As a substitute for sub-skill execution. The auditor checks; it does not produce architectural content. If the user wants to add a residue, they run S3 / S4 / S5, not the auditor.
- To "approve" something the user is uncomfortable with. The auditor reports facts about rule compliance; user approval is a separate gate captured in FLOW.md per the project's tracking convention.

## Modes of invocation

| Mode | Input | Scope of checks |
|---|---|---|
| **by-fragment** | One fragment file (e.g., `stressor-catalog.md`) | Only the checks that apply to that fragment's section(s). The fastest mode; runs during sub-skill execution before user approval. |
| **end-to-end** | The assembled `sad.md` | All checks across all sections. The slowest mode; runs after S7. |
| **diff** | A list of changed fragments since the last audit | Only the checks affected by the changes plus downstream traceability checks (e.g., changing the Stressor Catalog re-runs Coupling Map / NFR / Use Case Residue Mapping checks). |
| **handoff** | An emitted release directory (`architecture/arch-X.Y.Z/`) + the consumer's `.specify/memory/constitution.md` | The RDAG handoff & integration checks (§2.8): CHK-01..17 + the integration-state checks. Audits the S8 output and how it landed in the consumer, NOT the SAD fragments. |

The mode is declared by the user when invoking. If the mode is ambiguous, the auditor refuses with "specify mode: by-fragment | end-to-end | diff | handoff".

## Pre-conditions per mode

| Mode | Pre-condition |
|---|---|
| by-fragment | The named fragment file exists. |
| end-to-end | `sad.md` exists. (Implies the upstream chain S1-S7 ran.) |
| diff | The list of changed fragments is provided. The auditor reads each, plus any artifacts downstream of them. |
| handoff | The release directory `architecture/arch-X.Y.Z/` exists; the consumer's `.specify/memory/constitution.md` is readable (or its absence noted). |

---

## Workflow

### Step 1 -- Determine the check set

Given the mode and scope, build the set of checks to run. The full check inventory is in §Check Inventory below; each check is tagged with the fragments it applies to. The auditor runs only the checks relevant to the scope.

### Step 2 -- Run deterministic checks (always first)

Deterministic checks are mechanically verifiable. They are cheap and produce binary results (pass / fail). Run all deterministic checks before any heuristic check. If a deterministic check fails, the heuristic checks for the same rule may still run, but the violation is logged regardless.

**Script-backed deterministic checks (run these FIRST, report their output verbatim -- do NOT re-do them by eye).** A subset of the deterministic checks is mechanical enough to be a tested script in the bundle (`scripts/fragment-checks/`); running the script makes the result reproducible across audit runs instead of depending on the LLM applying the catalogue consistently (the failure the smoke-test S1a / audit-iter-5/6 exposed). Invoke whichever apply to the fragment in scope:

- `scripts/fragment-checks/check_counts.py <fragment>` -- prose-vs-table aggregate reconciliation: R-13 count-consistency (S3 per-Type distribution), S4 operation-columns / `N = rows + columns` / `Σ-Col == K`, S6 X/Y/S/Ri, **S6 unstressed-surfaces count (`S - Y` from the survives table)**, **S5 component-taxonomy per-Layer counts (Managers/Engines/ResourceAccess/Resources/Utilities) + the `IDesign components` total**, and **(on the assembled `sad.md`) the S7 exec-summary total stressor count (== catalog Type-column tally) and Looping Signals count (== the S4 Looping Signals table row count)** (§2.2 / empirical §2.4 / static §2.6).
- `scripts/fragment-checks/check_fragment.py <fragment>` -- structural checks: R-27 Lens Coverage Ledger completeness (L1-L12, non-empty verdicts) + OQ entry shape (§2.5), R-13 stressor typing presence (§2.1), R-02 taxonomy typing + R-05 tech-vocab + R-06 naming (§2.1), R-15 NFR Source non-empty (§2.3).
- `scripts/fragment-checks/reconcile_flow.py <FLOW.md> --check` -- Mermaid-table coherence (R-26, §2.7b).
- `scripts/fragment-checks/check_adr_applied.py <workspace-root>` -- ADR lifecycle: every `ACCEPTED`
  ADR whose Impact assessment Outcome is `iterating Sn` / `reopen Sn` (not `no-op`) MUST be cited by id
  in its impact gate's fragment (and, post-S7, in `sad.md`). A non-zero exit is a binding-ADR violation:
  name the ADR + gate, and propose either applying the impact (re-emit the gate) or changing the ADR's
  status. Run in `end-to-end` and `by-fragment` (S5 / S7) modes; not part of `handoff` mode.
- `scripts/fragment-checks/check_adr_status_prose.py <workspace-root>` -- ADR status consistency: a
  fragment / the assembled SAD must NOT transcribe an ADR's `Status` into prose where it disagrees
  with the ADR file (the status is operator-owned and goes stale on accept/decline). A non-zero exit
  names the file + the stale `ADR-NNNN narrated as X but actual is Y`; the fix is to reference the ADR
  by id and drop the inline status. Run in `end-to-end` and `by-fragment` (S5 / S7) modes; not handoff.
  Complements `check_adr_applied.py`: that one enforces an ACCEPTED ADR **is** reflected (binding);
  this one enforces the fragment does not **mis-state** the ADR's status.
- **ADR self-claim consistency (heuristic, not script-backed).** Beyond the two ADR scripts, read each
  ADR's prose and verify the **actions it claims to have performed in other fragments actually exist on
  disk**. An ADR that states it *annotated* / *re-typed* / *swept* / *applied* something to a named fragment,
  where that fragment does not contain the claimed change, is an **overclaim finding** -- the decision-of-record
  describes a state that does not exist. The fix is to either apply the action or relabel it *deferred* (cite
  the finding id and why, e.g. the target gate is `[x]` approved). This is the producer-overclaim class
  (intended-as-done); it is heuristic because the claim takes many prose shapes no single script catches.
  **Re-audit scope:** when an ADR is itself the resolution vehicle for an audit finding, re-run the audit
  over the **ADR** (not only the fragment it amends) before the operator accepts it -- the ADR is authored
  after the original audit and is otherwise never checked.
- `scripts/fragment-checks/check_handoff.py <handoff-dir>` -- RDAG handoff-conformance reconciliation
  (the deterministic subset of CHK-11 / CHK-12 / CHK-14): the manifest Artifact-inventory matches the
  files actually emitted (both directions), every recited `N services` / `N binding ADRs` count equals
  its enumerated tally, and every enumerated binding ADR resolves to a `decisions/ADR-*.md`. Self-contained
  over the emitted handoff dir (it never opens the SAD). Run in `handoff` mode only; a non-zero exit is a
  conformance violation -- name the artifact and propose aligning the manifest or emitting the missing file.

A non-zero exit is a deterministic violation: cite the rule, quote the script's line, and propose the fix. The rows in the categories below are the SPEC each script enforces; where a row is marked `script-backed`, the script is the source of truth and the prose row is its description.

The deterministic check categories:

#### 2.1 Doctrine (constitution rules with deterministic mechanism)

| Rule | Check |
|---|---|
| R-02 | Every component in §Static Architecture has a valid `type in {Manager, Engine, ResourceAccess, Resource, Utility, Client}`. |
| R-03 | The Call Rules table allows no upward calls, no sideways within layer (except R-04 exceptions). **AND** the PlantUML edges (`-->` / `..>`) of the §Static Architecture diagram AND the `<source> -> <destination>` relationships of the §C4 Model `workspace.dsl` agree with it: parse the edges and flag `Engine -> Engine`, `ResourceAccess -> ResourceAccess`, `Client -> ResourceAccess`, `Client -> Engine`, `Client -> Utility`, and synchronous `Manager -> Manager` (resolved via the endpoints' IDesign-layer tags). These slip into diagrams even when the Call Rules table is correct (they ride in on residues phrased "X coordinates with Y"); parsing the diagram edges makes the check deterministic, not heuristic. |
| R-05 | No component name in the taxonomy matches the forbidden vocabulary regex (case-insensitive: aws, azure, gcp, lambda, sqs, kafka, kubernetes, k8s, docker, postgres, mysql, mongodb, redis (in non-Utility roles), dapr (in non-Utility roles), grpc, rest, http, websocket, etc.). |
| R-06 | Every Manager / Engine / ResourceAccess name matches `^[A-Z][a-z]+([A-Z][a-z]+)*(Manager|Engine|Access)$`. |
| R-07 | No service name (Manager / Engine / ResourceAccess) starts with a known atomic business verb (Credit, Debit, StartCharge, etc.). Verbs appear only in ResourceAccess contract operations. |

#### 2.1b Business View Open Questions (R-27 -- S1 outputs)

R-27 is `both`: the section / gate / lens-ledger shape is deterministic (incl. all 12 lenses carrying a verdict -- the forcing function); the genuineness of each lens verdict is heuristic. Applies to `business-view.md` (and §Business View in the assembled SAD).

| Check | Mechanism | What to verify |
|---|---|---|
| Open Questions section present | deterministic | §Business View has an `### Open Questions` section -- a table or the explicit token "None". Absent section is a violation. |
| Entry shape | deterministic | Every Open Questions row has an ID (`OQ-NN`), a question, an `Affects` field, a `Status` of `Open` / `Answered`, and a `Source`. |
| Lens Coverage Ledger complete | deterministic | A `#### Lens Coverage Ledger` is present and lists all twelve lenses L1-L12, each with a non-empty verdict (OQ IDs or the literal `none`). A missing lens row (including a ledger that stops at L10 -- the pre-1.16.3 catalogue) or a blank verdict is a violation -- the forcing function: no lens may be silently skipped. |
| Gate acknowledgment | deterministic | When gate S1a is `[x]` and >=1 entry is `Status: Open`, the S1a row's `Approved on` cell in the FLOW.md Gate tracker carries an acknowledgment appended after the date -- `<date> (acknowledged: ...)`. A bare date (no parenthetical) while `Open` entries remain = violation. The cell is the contract location (the tracker has no Notes column). |
| Category separation | deterministic | Deferred volatilities are kept in the non-gating "Deferred volatilities" note, NOT among the Open Questions (the `#### OQ-N` cards, or the legacy OQ table) and vice versa. A stressor sitting in the Open Questions, or a stakeholder question buried in the deferred-volatilities note, is a violation. |
| Verdict genuineness (false `none`) | heuristic | When the PRD is in scope: spot-check the ledger verdicts. A lens that claims `none` while the PRD plainly carries something it should catch -- an uncaptured `TBC` (L1), a silent actor (L5), a lifecycle gap (L6), an edge silence (L7), an internal conflict (L10), a stale/unexamined premise (L11), a regulatory/privacy silence (L12) -- is a rubber-stamped `none` and a concern. |
| Attribution genuineness (literal firing) | heuristic | The inverse direction (R-27 1c / business-discovery Step 1.2): a lens that claims an OQ it did not *literally* fire on -- a decorative attribution, e.g. an underspecified term mapped to L1 (`TBC` marker) when no marker is present and the real catch is L4; a domain-reasoned premise mapped to a lexical lens -- is a violation. It understates the true coverage gap by making a quiet lens look productive. Cross-check each OQ's listed lens(es) against the lens definition: the marker/term/condition that lens scans for must actually be present in the cited `PRD:L#`. An OQ may list multiple lenses only if each genuinely caught it. |

#### 2.2 Synthesis (decomposition discipline guardrails)

| Rule | Check |
|---|---|
| R-13 / Guardrail #3 | Every row in §Stressor Catalog has a `Type` column with one of `Structural` / `Topological` / `Business` / `Combined`. |
| R-13 (count consistency) -- **script-backed** | Run the bundled `scripts/fragment-checks/check_counts.py <fragment>` and report its output verbatim; do NOT eyeball the table. The script re-derives every aggregate cited in prose from its table and hard-fails on drift: (S3) per-Type counts == Type-column tally; (S4) operation-column count, `N = rows + columns`, `Σ-Col total == K`; (S6) X/Y/S and the `Ri = (Y - X)/S` triple, plus the unstressed-surfaces count (`S - Y` from the survives table); **(S5) the Component Taxonomy per-Layer counts == the Layer-column tally and the `IDesign components` total == the service-layer sum (Clients counted separately)**; **(S7, on the assembled `sad.md`) the exec-summary total stressor count == the catalog Type-column tally and the Looping Signals count == the S4 Looping Signals table row count.** This is the audit-iter-5 ("9 Topological vs 8") / audit-iter-6 ("17 operation-columns vs 14") / the iteration-4 S5 ("8 ResourceAccess vs 7", "30 components vs 29") class -- now mechanical, not prose, so the result is reproducible across runs. |
| R-NN (ADR binding) -- **script-backed** | Run `scripts/fragment-checks/check_adr_applied.py <workspace-root>` and report its output verbatim. An `ACCEPTED` ADR with a non-`no-op` Impact assessment whose id is absent from its impact gate's fragment is a violation -- the assembled SAD would contradict an accepted decision. Deterministic: presence of the ADR id in the fragment. |
| R-14 / Guardrail #7 | No merge proposal in matrix readings is cross-layer (Manager+Engine, Manager+ResourceAccess, etc.) without the IDesign Override note. |
| R-15 / Guardrail #4 | Every row in §Derived NFRs and every per-use-case NFR has a non-empty `Source` column. |
| R-17 / Guardrail #8 | Every `Combined`-typed stressor has a corresponding row in §Looping Signals with a non-empty `Survived by Combination of` reference. |
| R-18 / Guardrail #1 | Every component in §Static Architecture appears in the `Technical Change to Residue (IDesign)` column of at least one Structural residue in §Stressor Catalog. Do NOT verify via §Contagion Matrix columns -- those are the Naïve Architecture, so residual components added in S5 cannot appear there (a known false-positive source). |
| R-19 / Guardrail #2 | Every deployment unit boundary in §Deployment Diagram references a row in §Topological Residue Map. |
| R-20 / Guardrail #6 | No column header in §Stressor Catalog or §Contagion Matrix matches `probability|likelihood|risk|cost|complexity|effort|priority` (case-insensitive). |

#### 2.3 Hyperliminal Coupling Map checks (S4 outputs)

| Check | Description |
|---|---|
| Multi-1 row coverage | Every matrix row with Σ Row >= 2 has an entry in §Hyperliminal Coupling Map. |
| Decisive architectural response | No row has `Architectural Response` containing `investigate` / `TBD` / `it depends`. |
| NFR Source for Document-NFR-contract rows | Every row with `Architectural Response = Document NFR contract` has a non-empty `NFR Source` reference. |
| NKP Totals present | §NKP Totals reports N (stressors + components), K (sum of 1s), P (low/medium/high with checklist). |
| N formula correct | N = #stressors + #components, NOT components only. Auditor checks the value matches the matrix dimensions. |

#### 2.4 Traceability (cross-reference resolution)

For end-to-end and diff modes:

| Reference | Target | Check |
|---|---|---|
| Stressor # in any sub-table | §Stressor Catalog | The referenced number exists. |
| `Hyperliminal Coupling #N` NFR Source | §Hyperliminal Coupling Map | Row N exists. |
| `Topology row N` NFR Source | §Topological Residue Map | Row N exists. |
| `Business Residue #N` NFR Source | §Business Residues Log | Row N exists. |
| Use Case Residue Mapping references | §Stressor Catalog | All referenced residue #s exist. |
| Deployment Unit Boundary `Topological Residue #` | §Topological Residue Map | Row exists. |
| Component name in Use Case scenario / sequence diagram | §Static Architecture Component Taxonomy | Component exists. |
| `Survived by Combination of` in §Looping Signals | §Stressor Catalog | All referenced residue #s exist AND are not Combined-typed (loops cannot reference loops). |
| `PRD:L<n>` / `PRD §<x>` grounding refs (conditional -- only if present) | PRD/SRD source | Every PRD grounding ref resolves to a real line/section of the supplied PRD. Also flag the inverse error: a **stressor** carrying a `PRD:L` ref (genuine stressors are not in the PRD -- style-conventions §7.1). Skipped entirely if the SAD uses no PRD refs. |

#### 2.5 Empirical check (S6 outputs)

| Check | Description |
|---|---|
| Train/test disjuncia (verbatim) | No test stressor in §Empirical Test appears verbatim in §Stressor Catalog **of the same iteration at the moment of the test**. Disjuncia is per-iteration: a test stressor from iteration N legitimately becomes a catalog entry in iteration N+1 (the S6 -> S3 feed-forward of unstressed surfaces). Do NOT flag an iter-N test stressor for appearing in the iter-(N+1) catalog -- that is correct feed-forward, not a violation. Check disjuncia against the catalog as it stood when that iteration's test ran. |
| Train/test disjuncia (semantic) | Flagged for human review when wording differs but triggering event + propagation + attractor match a catalog entry of the same iteration. Heuristic; auditor reports candidates, user resolves. |
| Ri formula present | `Ri = (Y - X) / S = <value>` written explicitly. |
| **Ri arithmetic correct** | Recompute `(Y - X) / S` from the reported X, Y, S and confirm it equals the reported Ri value. Deterministic. Catches the class of bug where the Ri stated in a summary / front-matter does not match the per-stressor table (e.g. a header says `Ri=0.78` while the table yields `0.68`). |
| **Counts reconcile across the fragment** -- script-backed | Run `scripts/fragment-checks/check_counts.py <fragment>` and report its output: X equals the count of `Naive survives = 1` rows; Y equals the count of `Residual survives = 1` rows; S equals the table row count; the `Ri = (Y - X)/S` triple matches; and any per-type tally stated in prose sums to S and matches the table. Do not re-count by hand -- the script is the deterministic source. | 
| Binary survival | X and Y are integers. No partial-credit scoring. |
| Unstressed surfaces enumerated | Every test stressor with `Residual survives = 0` is documented with failure mode. |
| Regressions flagged (count) | Every row with `Naive = 1` and `Residual = 0` is counted and tagged as a regression (Step 6.1), not silently averaged into a positive Ri. |
| Invariant coverage | Every invariant declared in the §Business View (S1 Step 1.3) has a row in the §Invariant Preservation table (S6 Step 6.2); a declared invariant with no verification row is a gap. Empty/absent only if the Business View declares no invariants. |
| Ri sign reported | The interpretation (positive / zero / negative) is named in the fragment. |

#### 2.6 Representation discipline (R-23 -- C4 as Structurizr DSL)

For fragments / SADs that contain C4 architecture (S5 residual-design, S7 assembled SAD). R-23 is `deterministic`; these checks are mechanical. Reference: `shared/style-conventions.md` §6.1. The C4 architecture is a single `workspace.dsl`; level-mixing *within* a level is impossible by the model's nesting, so the checks target the failure modes the model does NOT prevent.

| Check | How | Rule |
|---|---|---|
| C4 is one Structurizr DSL workspace | The §Structural Diagrams section contains a single fenced ```dsl `workspace.dsl` (not Mermaid C4 / `flowchart` for C4). The workspace parses; `model` and `views` blocks present. | R-23 (a) |
| Required views declared | Views include one `systemContext`, one `container`, one `deployment`; a `component <c>` view for each container with 2+ IDesign components. | R-23 (a) |
| No `container` named after an IDesign component | No `container` element name/identifier matches a Manager / Engine / ResourceAccess / Utility name from the §Static Architecture taxonomy. Those must be nested `component`s. **Highest-value check** -- it catches the error R-23 exists to prevent. | R-23 (b) scope |
| Component-view coverage complete | Every container with 2+ IDesign components (per the Container <-> Component mapping) has a `component <container>` view. Containers with 0-1 components are exempt. | R-23 (c) coverage |
| Deployment present | A `deploymentEnvironment` with `deploymentNode`s and `containerInstance`s exists; per-jurisdiction Topological residues appear as separate top-level nodes. | R-23 (a) |

These are reported as deterministic violations. The no-`container`-named-after-a-component check is the highest-value one.

**Representation tiers (`style-conventions` §6 / §6.2 -- non-C4).** Deterministic, distinct from R-23 (which governs only C4). Checks the Mermaid / PlantUML split by diagram kind:

| Check | How | Reference |
|---|---|---|
| Static Architecture is PlantUML | The §Static Architecture (IDesign) diagram is a `\`\`\`plantuml` block (`@startuml ... @enduml`), NOT a `\`\`\`mermaid` block. | `style-conventions` §6.2 |
| Behavioral diagrams are PlantUML | Every diagram under §Behavioral Diagrams (use-case / activity / sequence) is a `\`\`\`plantuml` block, NOT Mermaid. | `style-conventions` §6.2 |
| Mermaid is naive-only | The only `\`\`\`mermaid` block in the SAD is the S1b naive-architecture baseline. Any `\`\`\`mermaid` in the residual §Analysis and Design is a violation. | `style-conventions` §6 |

#### 2.7 Structural consistency (post-change)

After any structural change (component split / rename / merge / re-type), the new component names must resolve consistently across every artifact. This is the deterministic counterpart to the S5 §2.6 "Structural Change Impact Checklist": it catches incomplete propagation -- a label updated in the taxonomy but stale elsewhere. The reference set is the §Static Architecture Component Taxonomy; every component name used anywhere else must appear there.

| Check | Description |
|---|---|
| Diagram names resolve to taxonomy | Every component named in the Static Architecture diagram and the `component` elements and `container` elements of the §C4 Model `workspace.dsl` resolves to a row in the §Static Architecture Component Taxonomy. |
| NFR Affected Components resolve | Every component named in the `Affected Components` column of §Derived NFRs and §General NFRs resolves to the taxonomy. |
| Use Case component names resolve | Every component named in a use case scenario / activity diagram / Residue Mapping resolves to the taxonomy. |
| Service Grouping Map names resolve | Every component in the §Service Grouping Map resolves to the taxonomy, and every taxonomy component appears in exactly one Service Grouping Map row. |
| Service names match S4 -> S5 verbatim | Every `container` element name in the §C4 Model `workspace.dsl` equals a `Service / Deployable Unit` name in the §Service Grouping Map (S4) character-for-character; no service renamed or coined in S5. The §Service Grouping Map is the naming authority (`contagion-analysis` §9.4). |
| No orphaned old names | A component name that exists in one artifact but not in the taxonomy is a stale reference from an incomplete structural change -- flag it with the artifacts where it still appears. An upstream S3 / S4 candidate-residue name annotated `(folded into X)` / `(re-typed as X)` is NOT an orphan: candidate residue names are non-binding (R-22 / R-24) and the annotation records the resolution. |

Reported as deterministic violations. This is the check that would have caught the incomplete ripple after a Manager split (stale labels in 2 diagrams + 7 NFRs) in one pass instead of across audit iterations.

#### 2.7b Gate-tracker coherence (R-26, NON-NEGOTIABLE)

Runs in `by-fragment` and `end-to-end` modes. Walks the gate tracker
(`FLOW.md §Current session`) top-down and flags any `[x] approved` whose prior
gate is not `[x] approved`. This is a state-shape check on the tracker itself
-- distinct from the producer-time Gate Approval Protocol check, which fires
only when an executor is about to emit. R-26 fires on every audit read.

| Check | Description | Rule |
|---|---|---|
| Tracker coherence (all three invariants) | Walk the chain S1a -> S1b -> S2 -> ... -> S7 (+ S8a -> S8b when present) and verify: **(1)** every `[x]` has all priors `[x]` (contiguous approval chain); **(2)** every `[~]` / `[?]` / `[i]` has all priors `[x]` (active gates require approved priors); **(3)** at most one gate is in `[~]` / `[?]` / `[i]` (single-active-gate rule -- only the first gate after the last `[x]` can be active). Any violation is a **tracker inconsistency** -- deterministic. Fix is binary: revert the offending gate to `[ ]`, or approve every missing prior. No `--force`. | R-26 |
| Mermaid-table coherence (diagram == table) | Run the bundled `scripts/fragment-checks/reconcile_flow.py <FLOW.md> --check`: every Mermaid `Sn`/`Gn` node's label mark + `:::class` must match what the authoritative Gate tracker table requires. Drift (table updated, diagram stale -- feedback F-01) is a deterministic finding; the fix is `--fix` (rewrites the diagram from the table, never the table). This is a representation check on the diagram, orthogonal to the table-coherence invariants above. | R-26 / `style-conventions` |

Reported as a deterministic violation, not a concern. Catches an out-of-band
mutation (UI bug, manual edit, buggy orchestrator, fixture) that the executor
never had a chance to refuse. The single-active-gate rule (invariant 3) is what
keeps the workflow single-threaded: only one decision pending at a time.

#### 2.8 Handoff & Integration conformance (S8 / RDAG -- `handoff` mode only)

Runs against an emitted release directory (`architecture/arch-X.Y.Z/`) and the
consumer's `.specify/memory/constitution.md`. Maps to the CHK assertions in
`sdd-interface/standard/rdag-conformance.md`. Deterministic; each failure carries
a fix proposal. This category is what catches a botched integration -- the most
common being the wrong *kind* of constitution in place.

| Check | Description | CHK |
|---|---|---|
| **Consumer constitution is the right kind** | `.specify/memory/constitution.md` carries the **Service Decomposition by Residue** principle. A **SAD-workflow constitution** (markers: "SAD Workspace", Gate Approval, Lateral Analysis, Naïve Baseline, Reopen Propagation) sitting there *as the consumer's* is a violation -- it governs how the SAD is *produced*, not how the system is *implemented*. Fix: scaffold the consumer constitution; preserve the SAD-workflow one aside (`docs/architect/sad-workspace-constitution.md`). | CHK-01 |
| **Principle verbatim** | The principle's normative clauses match the emitted `integration/principle-decomposition-by-residue.md` verbatim (host may renumber / adjust surrounding prose, never the clauses). | CHK-01 |
| **Current Architecture pointer resolves** | The constitution names `Current = arch-X.Y.Z` and that release directory exists with its Tier-1 set (catalog + nfr-register + use-cases + ADRs + manifest). | CHK-16 |
| **Integration status explicit** | If the implementation half still has unfilled `[TODO]` stubs, a `PENDING` status banner is present -- the project must not be silently presented as ratified/complete. | integration-state |
| **Service naming (Lowy suffix)** | Every service name matches `(Manager|Engine|Access)$` or is a Resource entry. | CHK-06 |
| **Residue lineage** | Every catalog service lists >=1 Structural `S-NN` in its Stressors-absorbed field. | CHK-07 |
| **NFR lineage** | Every `NFR-NN` records a `C-NN` Source and an `Applies-to`. | CHK-08 |
| **Layer rules (use-case call chains)** | No `Manager->Manager` sync, no `Client->ResourceAccess`, no `Engine->Manager` in any use-case call chain. | CHK-09 |
| **Architectural Context complete** | Each use case declares Call Chain + Services touched + Residue; every touched service exists in the catalog. | CHK-10 |
| **Traces resolve** | Every cited `S-NN` / `C-NN` / `NFR-NN` / service name resolves within the release. | CHK-11 |
| **Binding ADRs locatable** | Every binding ADR is referenced from the catalog or the manifest (so `/speckit-plan` Q6 can enumerate it). | CHK-12 |
| **Binding-ADR set consistent** | The enumerated binding-ADR set agrees across every artifact that recites it -- the manifest's "Binding ADRs" section, the constrained services' "Binding ADRs" fields in `service-catalog.md`, and the "Binding ADRs (this release)" line in `integration/constitution.scaffold.md` -- none still showing a set / an `N binding ADRs` count that excludes a post-S8a-appended binding ADR the manifest lists. The agnostic principle text (`principle-decomposition-by-residue.md`) is exempt (CHK-05). | CHK-14 |
| **Tier-1 only** | The handoff carries no Tier-2 evidence files (stressor-catalog / coupling-map / criticality-certificate) -- those are Backstage-published, not shipped. | Tier boundary |
| **Release directory immutable** | A published `arch-X.Y.Z/` is not edited in place; a changed architecture is a NEW `arch-X.Y.Z+1/` + migration delta. | CHK-16/17 |

The first four are the integration checks the user-facing botch surfaces; the
rest mirror the artifact-set conformance S8 self-checks at emission. Fix proposals
follow the same conservative discipline (Step 4): the auditor proposes (e.g.
"scaffold the consumer constitution from `integration/constitution.scaffold.md`;
move the SAD-workflow constitution aside"), it does not silently apply.

### Step 3 -- Run heuristic checks (only if Step 2 passes)

Heuristic checks require LLM judgment. They are slower and produce graded results (`pass` / `concern` / `fail` with confidence). Heuristic checks include the constitution rules whose mechanism is `heuristic` or `both`:

| Rule | Heuristic check |
|---|---|
| R-01 | Every component's residue justification reads as residue-based, not function-based or use-case-based. (E.g., `BillingManager` is justified by "billing workflow volatility under stressors X, Y", not by "we need a billing service".) |
| R-04 | Each exception applied (Utility callable from BL/RA, Manager-to-Engine, queued M-to-M) is legitimately applied (not used to launder an R-03 violation). |
| R-07 (heuristic part) | Is the verb actually atomic-business? Or is it a system-level verb (Save, Update) that betrays CRUD-thinking? |
| R-09 | No component lacks a residue justification (would indicate speculative design). |
| R-10 | No stressor in the catalog is a solution masquerading as a requirement. |
| R-11 | Every Manager is almost-expendable -- its responsibilities are workflow only, no business logic. |
| R-12 | ResourceAccess contracts expose atomic business verbs, not implementation-leaking operations (e.g., no `SendPostRequest`). |
| R-16 | No component name matches a use case name (would indicate use-case-driven decomposition). |
| R-21 | The SAD includes the Empirical Test section (a SAD without one is correctness-oriented, not criticality-oriented). |
| **R-22** | **Output shape signals**: one-liner stressors (Pitfall 2 in S3), technical-not-contextual framing (Pitfall 1 in S3), checklist-like uniform refusal-condition coverage, edge-case-as-residue (Pitfall 3 in S3), defended abstractions across multiple stressors, low Ri value relative to depth of analysis. Auditor cannot check cognitive mode mechanically but reports these signals as R-22 indicators with confidence. |
| **R-13 + R-22 (framework calibration)** | **Residue-type distribution signal**: count residues by type in the Stressor Catalog and compare against the calibration matrix in `shared/stressor-frameworks.md` §Framework x Residue type coverage. A healthy catalog has Business and Structural dominating with Topological visible. If a type is **entirely absent**, flag it as a `concern` (not a violation -- absence may be legitimate for the system's nature): no Structural suggests abstraction stressing or flow stressing was under-exercised; no Business suggests PESTLE / Porter / BMC was under-exercised; no Topological suggests no geography / tenancy / replication stressing was attempted. Combined is excluded from this signal -- it emerges in S4, not from frameworks (R-17). Report which framework was likely skipped, with confidence proportional to how lopsided the distribution is. **Under-sampling signal:** if the catalog has zero Combined residues / no Looping Signals, the simulation may have stopped before looping (S3 Step 8) -- the volume measure is looping, not a count, so a no-looping catalog is a `concern` for under-sampling (likely the every-noun pass was not run exhaustively). Conversely, hundreds of near-duplicate stressors past a clear looping point is over-generation, not rigor. |
| **R-24** | **Smallest-set residue discipline**: for each new Resource in the Static Architecture (especially a third-party engine), verify smallest-set was applied -- was extending an existing ResourceAccess attempted first? Is one of the 4 legitimate justifications (visual editing / multi-process saga / complex temporal / operational tooling, per `shared/idesign-vocabulary.md` §9) cited? A new Resource justified only by "long-running + durable + replayable" is an R-24 concern: that is standard ResourceAccess territory and needs no third-party engine. Report with confidence; the architect confirms or documents an accepted exception. |
| **R-25** | **Service grouping: Manager is the unit of deployment** (actor-style default): check the §Service Grouping Map and §C4 Model container view. Each Manager should be its own deployable unit with its **private** Engines/ResourceAccess co-located inside it. Flag as concerns: (a) a single-Manager Engine/RA given its own service with no operational driver (needless N inflation -- should co-locate with its Manager); (b) all Managers collapsed into one monolithic service despite divergent stress profiles (loses actor-style isolation); (c) a shared Engine/RA (used by 2+ Managers) in its own service without citing the operational Topological residue (`independent-scaling` / `resource-profile` / etc.); (d) two Managers co-located without citing a shared stress profile; (e) a Client-reachable promoted unit (query / read-model / API surface) with no entry Manager among its co-located components -- a Client may only call a Manager (R-03 / R-04 (a)), and the entry Manager should have been decided at S4 §9.3.1, not deferred to S5. Report with confidence. The default (one Manager, one service) is correct and needs no driver -- it traces to the Manager's own Structural residue. |

### Step 4 -- Generate fix proposals

For each violation, generate a fix proposal in unified-diff format. The fix proposal includes:

- The affected fragment file path.
- The affected section / row / cell.
- The proposed change (added / removed / modified content).
- The rationale linking the fix to the rule.

Example fix proposal format:

```
File: stressor-catalog.md
Section: §Stressor Catalog row #7
Rule: R-13
Violation: Type column empty.

Proposed change:
- | 7 | | Manufacturer lock-in | ... |
+ | 7 | Business | Manufacturer lock-in | ... |

Rationale: R-13 requires every stressor to be typed. The stressor is a competitive force producing a business decision; type = Business.
```

The auditor does NOT apply the fix. The user (or the sub-skill that produced the fragment, on re-invocation) applies it. The auditor only proposes.

### Step 5 -- Document accepted exceptions

An architect may explicitly accept a violation in cases where the rule applies but the cost of compliance exceeds the value. Accepted exceptions are documented in `audit.md` §Accepted Exceptions with:

- The rule (R-NN or guardrail #).
- The fragment + section affected.
- The rationale for acceptance.
- The expected expiration condition (e.g., "until we have the budget to implement per-country deployment").
- Sign-off (architect name or identifier).

Accepted exceptions are NOT a default. They are a deliberate decision-of-record. The auditor lists them so future iterations can re-evaluate.

### Step 6 -- Produce `audit.md`

Write the audit output to `audit.md` in the project workspace, with the structure described in §Output Contract below.

---

## Check inventory (consolidated)

Total checks across modes:

| Category | Count | Mechanism |
|---|---|---|
| Doctrine (R-02 / R-03 / R-05 / R-06 / R-07 deterministic part) | 5 | deterministic |
| Business View Open Questions (R-27 deterministic part: section present / entry shape / lens-ledger complete / gate acknowledgment / category separation) | 5 | deterministic |
| Synthesis guardrails (R-13 typing + R-13 count-consistency / ADR binding / R-14 / R-15 / R-17 / R-18 / R-19 / R-20) | 9 | deterministic |
| Hyperliminal Coupling Map | 5 | deterministic |
| Traceability (incl. conditional PRD grounding-ref resolution) | 9 | deterministic |
| Empirical (incl. Ri arithmetic + counts reconcile + regression count + invariant coverage) | 10 | deterministic |
| Representation (R-23 C4 as Structurizr DSL: one workspace / required views / no container-named-as-component / Component-view coverage / deployment present) | 5 | deterministic |
| Structural consistency post-change (diagram / NFR / use case / Service Grouping name resolution + S4->S5 service-name parity + orphan detection) | 6 | deterministic |
| Gate-tracker coherence (R-26; `by-fragment` + `end-to-end`): table coherence + Mermaid-table reconciliation (`reconcile_flow.py`) | 2 | deterministic |
| Heuristic constitution (R-01 / R-04 / R-07 heuristic / R-09 / R-10 / R-11 / R-12 / R-16 / R-21 / R-22 / R-13+R-22 framework calibration / R-24 smallest-set / R-25 service grouping / R-27 verdict genuineness / R-27 attribution genuineness) | 15 | heuristic |
| Handoff & Integration (CHK-01..17 + integration-state; `handoff` mode) | 13 | deterministic |
| **Total** | **84 checks** | mixed |

In `by-fragment` mode, typically 5-15 checks run plus the R-26 tracker-coherence check (§2.7b). In `end-to-end` mode, all 69 SAD checks run plus R-26. In `diff` mode, the count depends on the scope of changes (typically 10-25) plus R-26. In `handoff` mode, the 13 §2.8 checks run (the SAD-fragment checks do not -- a handoff audit is about the S8 output and its integration, not the SAD body); R-26 also runs whenever a `FLOW.md` is present in scope. The structural-consistency checks (§2.7) are the core of `diff` mode -- they re-run whenever a component is renamed / split / merged.

The Representation checks (R-23) apply whenever C4 architecture is in scope (S5 residual-design fragment, S7 assembled SAD, or a diff touching either). The no-`container`-named-after-a-component check is the one that catches the most common C4 error.

The framework-calibration check (R-13 + R-22) applies whenever the Stressor Catalog is in scope (S3 fragment, end-to-end, or a diff that touches the catalog). It is a `concern`-only check: it never produces a deterministic violation, because an absent residue type can be legitimate for the system's nature.

---

## Output contract

One file in the project workspace. **Report-name convention:**
`audit-iter-N.md` for by-fragment / end-to-end / diff (one per SAD iteration);
**`audit-handoff-arch-X.Y.Z.md`** for `handoff` mode (one per audited release).

### `audit.md` (logical name; see the convention above)

Markdown file with frontmatter and the audit report structure. Frontmatter:

```
---
title: SAD audit -- <project name>
audit-date: <YYYY-MM-DD>
mode: by-fragment | end-to-end | diff | handoff
scope: <fragment names | "sad.md" | release dir "architecture/arch-X.Y.Z/">
iteration: <N from the parent SAD's frontmatter>
status: open | closed
violations: <count>
heuristic-concerns: <count>
accepted-exceptions: <count>
---
```

Body structure:

1. **§Executive summary** -- one paragraph: mode, scope, count of violations, count of accepted exceptions, overall status.
2. **§Deterministic Violations** -- table with columns: `#` / `Rule` / `Severity` (always `violation` for deterministic) / `Fragment` / `Section` / `Description` / `Fix Proposal`.
3. **§Heuristic Concerns** -- table with columns: `#` / `Rule` / `Severity` (`concern` / `fail`) / `Confidence` (`low` / `medium` / `high`) / `Fragment` / `Section` / `Description` / `Suggested Resolution`.
4. **§Traceability Gaps** -- table for missing or broken cross-references.
5. **§Empirical Test Findings** -- if applicable: Ri value, unstressed surfaces, train/test disjuncia check result.
6. **§Accepted Exceptions** -- table with columns: `#` / `Rule` / `Fragment` / `Section` / `Rationale` / `Expiration` / `Sign-off`.
7. **§Closure** -- one paragraph: what needs to happen for the audit to close (resolve violations, document exceptions, re-run after fixes).

The audit is `status: closed` only when:

- All deterministic violations are resolved or explicitly accepted (R-22-style with rationale).
- All heuristic concerns are reviewed (acknowledged by the architect, not necessarily resolved).
- All traceability gaps are resolved.
- The Ri test passes the disjuncia check (or the violation is explicitly accepted, which is rare and warrants a strong rationale).

---

## Refusal conditions

The auditor refuses to run, or refuses to close the audit, when:

| # | Trigger | Returned message |
|---|---|---|
| 1 | Pre-condition violated (mode missing, scope missing, fragment file does not exist). | Identify the missing input. The auditor cannot infer mode or scope. |
| 2 | The user asks the auditor to fix an issue silently. | Refuse. The auditor proposes fixes; it does not apply them. Re-run the sub-skill that produced the fragment to apply the fix. |
| 3 | The user asks to close the audit with deterministic violations unresolved AND without accepted exceptions. | Refuse. Closure requires resolution or explicit acceptance with rationale. There is no `--force`. |
| 4 | The user asks to skip a check ("just don't check R-X for now"). | Refuse. The check set is determined by mode and scope, not by user preference. Document an accepted exception if the rule applies but the user accepts the violation. |
| 5 | The user asks to lower confidence on a heuristic concern without re-running the check. | Refuse. Confidence is the auditor's output, not the user's input. The user may dispute via accepted exception with rationale. |
| 6 | The user asks for a "summary score" / "audit grade" / "% compliance". | Refuse with explanation. The auditor reports violations and concerns; it does not produce summary scores. A score would invite gaming the audit; the meta-skill's empirical test is the Ri value (S6), not an auditor grade. |

---

## Worked example

For the EV charging SAD (the canonical worked example), an end-to-end audit would produce something like:

| Section | Findings |
|---|---|
| Deterministic violations | None (the EV charging SAD as published in §3-§7 passes typing, naming, hygiene, and Coupling Map checks). |
| Heuristic concerns | R-22 indicator: §3 stressor #4 (EV market crashes) has a fairly thin narrative; could be expanded. Low-confidence concern. |
| Traceability gaps | None. |
| Empirical Test Findings | §9 reports Ri = 4/6 ~ 0.67 with T5 / T6 marked as unstressed surfaces. Train/test disjuncia verified verbatim against §3 catalog (the test stressors T1-T6 do not appear). |
| Accepted Exceptions | The EV charging example is dated pre-2026-05-11 enrichments, so it lacks §Hyperliminal Coupling Map and §NKP Totals subsections. Documented as accepted exceptions until the next iteration of the worked example. |
| Closure | Audit closed pending the documented exceptions; recommend updating the worked example in P5 (TradeMe migration) or as a separate task. |

This is the kind of output an architect receives from the auditor. It is descriptive, actionable, and bounded -- no scores, no grades, no silent edits.

---

## Why these rules

- **Conservative discipline.** The auditor's no-silent-fix and no-`--force` rules prevent the audit from becoming a rubber stamp. Violations must be addressed, not bypassed.
- **Deterministic first.** Cheap checks first means heuristic LLM judgment runs only after the mechanical baseline is verified. A fragment that fails R-02 (typing) is not worth running R-01 (heuristic Golden Rule) against -- it has a more basic problem.
- **No summary scores.** Per O'Reilly's framing of the Ri test as the empirical signature, the auditor refuses to compete with Ri by producing a different "quality score". Compliance with rules is necessary; criticality (Ri > 0 on test set) is the actual goal.
- **R-22 as output-shape signal.** The auditor cannot check the architect's cognitive mode directly; it reports the SHAPE of the output (one-liner stressors, defended abstractions, mechanical refusal coverage) as indicators. Low-confidence R-22 concerns are not violations -- they are invitations to reflect.
- **Accepted exceptions over force.** Real projects have moments when compliance costs exceed value. The accepted exceptions mechanism preserves this flexibility without polluting the rule system. The exception is a decision-of-record; the rule still holds.

---

## How `audit.md` integrates with the SAD

The SAD `template.md` §Appendices includes a reference to the latest audit. Specifically, after the §Architecture Decision Records subsection, add a §Audit Status subsection:

```markdown
### Audit Status

| Iteration | Audit date | Mode | Status | Open Violations | Accepted Exceptions | Report |
|---|---|---|---|---|---|---|
| 1 | YYYY-MM-DD | end-to-end | closed | 0 | 2 | `audit-iter-1.md` |
```

This makes the audit history visible from the SAD without embedding the full audit content. Per Q1 resolution (2026-05-16): audit reports are separate files (`audit-iter-N.md`), one per iteration, with the SAD §Appendices §Audit Status table providing the index.

---

## References

- `shared/constitution.md` -- all 26 active rules (R-01 to R-27, R-08 intentionally absent) + cross-reference table. The auditor enforces every rule listed there.
- `shared/decomposition-discipline.md` -- the 8 guardrails (R-13 to R-20 mapping).
- `shared/idesign-vocabulary.md` -- the IDesign taxonomy, call rules, and override that the auditor mechanically checks.
- `shared/architectural-walking.md` §4 -- the cognitive-mode signals that R-22 heuristic check looks for.
- `shared/stressor-frameworks.md` §Framework x Residue type coverage -- the calibration matrix the framework-calibration check (R-13 + R-22) compares the catalog's residue-type distribution against.
- `shared/glossary.md` -- vocabulary the auditor uses in violation descriptions.
- `sdd-interface/standard/rdag-conformance.md` -- the CHK-01..17 assertions the `handoff`-mode checks (§2.8) enforce.
- `sdd-interface/standard/rdag-standard.md` -- the RDAG doctrine (drop-in principle, Architecture Release versioning) the handoff audit checks against.
- `sad/template.md` -- the structural template the auditor uses to know what sections to check.
- `sad/synthesis-explanation.md` §6 -- the seven synthesis decisions that motivate the synthesis-category checks.
- Each sequential sub-skill's `SKILL.md` -- the source of the refusal conditions the auditor mirrors when it checks output produced by that sub-skill.
- `sad/sad-assembler/SKILL.md` -- the assembler's cross-reference table is the auditor's reference for end-to-end traceability checks.
