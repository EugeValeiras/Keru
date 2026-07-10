---
name: sad-assembler
description: Seventh and final sequential sub-skill of the `sad` meta-skill. Integrates the six approved upstream fragments (business-view + naive-architecture + flow-analysis + stressor-catalog + contagion-analysis + residual-design + empirical-test) into a single Software Architecture Document (SAD). The assembler does NOT edit fragment content; it stitches sections, fills boilerplate (methodological note, technical considerations, restrictions, appendices), writes a one-paragraph executive summary, and verifies cross-references. Invoke after all upstream fragments are approved; refuse otherwise.
task_types: [assemble, integrate-sad, stitch-fragments, executive-summary]
shared_refs:
  - shared/constitution.md
  - shared/decomposition-discipline.md
  - shared/style-conventions.md
  - shared/glossary.md
  - sad/template.md
  - sad/synthesis-explanation.md
  - sad/adr-template.md
---

# sad-assembler (S7)

Final sequential sub-skill. Integrates the six approved fragments into a single `sad.md` following `sad/template.md`. The output is the canonical Software Architecture Document that stakeholders, engineering teams, regulators, and downstream auditors consume.

The assembler's contract is **conservative**: it does NOT edit fragment content. Every section of the SAD is filled either by inlining an approved fragment or by writing boilerplate (Methodological Note, Technical Considerations, Restrictions, Appendices, executive summary). If the assembler discovers an inconsistency between fragments, it refuses -- the resolution belongs in the relevant upstream sub-skill, not in S7.

The assembler is the integration point of the meta-skill. Its discipline (no silent edits, refusal on inconsistency, explicit cross-reference resolution) is the structural reason the upstream sub-skills can be invoked independently and iterated separately: each fragment is a self-contained, approved artifact that S7 composes without re-interpretation.

---

## When to invoke

- All six prior fragments exist and are approved: `business-view.md`, `naive-architecture.md`, `flow-analysis.md`, `stressor-catalog.md`, `contagion-analysis.md`, `residual-design.md`, `empirical-test.md`.
- The architect is ready to produce a single integrated artifact for stakeholders.
- The Ri test in S6 produced a positive or near-zero value (negative Ri is a backtrack signal, not a ship signal).

## When NOT to invoke

- One or more upstream fragments missing or unapproved (run / approve the upstream sub-skills first).
- The user wants the assembler to "fix" issues in the upstream fragments. S7 does not edit fragment content; resolutions live in their original sub-skill (e.g., a wrong NFR is fixed in S5, not in S7).
- The user wants partial assembly (just §Architectural Stress Analysis without §Analysis and Design). The SAD is a single coherent document; partial outputs are read directly from the fragment files, not from S7.
- The Ri in S6 is negative AND the user has not addressed it (R-21 + S6 Refusal #10). Shipping a SAD with negative Ri silently accepts an architecture worse than the naïve baseline.

## Pre-conditions

The **S6 gate (and all prior gates S1-S6) are marked `[x] approved`** in the project gate tracker (`FLOW.md`), not merely produced -- verify before assembling (root `SKILL.md` §Gate approval protocol).

All six fragments exist and are approved:

1. `business-view.md` (S1)
2. `naive-architecture.md` (S1)
3. `flow-analysis.md` (S2)
4. `stressor-catalog.md` (S3)
5. `contagion-analysis.md` (S4)
6. `residual-design.md` (S5)
7. `empirical-test.md` (S6)

Plus cross-reference inputs (read-only):

- `sad/template.md` -- the structural template.
- `sad/adr-template.md` -- if the project has ADRs to list.

## Handoff contract

- **Consumes:** all six approved fragments (`business-view.md`, `naive-architecture.md`, `flow-analysis.md`, `stressor-catalog.md`, `contagion-analysis.md`, `residual-design.md`, `empirical-test.md`) + `template.md` (structure) + `adr-template.md` (if ADRs exist) -- all prior gates S1-S6 must be `[x] approved`.
- **Produces:** final `sad.md` + a consolidated traceability matrix (stressor -> residue -> component -> NFR -> test).
- **Lateral context to carry forward:** none -- assembly is integration only. The job here is consistency, not new reasoning: reconcile counts, cross-references, and IDs across fragments so the final document is internally coherent.

## Workflow

### Step 1 -- Verify fragment completeness

For each of the six fragment files, confirm:

- The file exists at the expected path in the project workspace.
- The file is marked `[x] approved` in the project's `FLOW.md` (or its equivalent tracking artifact).
- The file is non-empty and contains the expected section headers per its source sub-skill's Output Contract.
- **Fragment headings start at `###`** (the SAD reserves `#`/`##`, style-conventions §5.1). If a fragment uses `##` internally, do NOT silently demote -- flag it for the source sub-skill to fix (the assembler does not edit fragment content).
- **If a fragment has iteration Deltas** (`### Delta -- iteration N`, style-conventions §5.2), the **latest Delta is canonical**: inline the latest Delta's counts/values, keep earlier iterations as dated history. Do NOT reconcile coexisting iter-N / iter-N+1 counts by hand -- the latest Delta is authoritative by convention.

If any fragment is missing or unapproved, refuse (see §Refusal conditions).

### Step 2 -- Verify cross-references

Walk the fragments looking for cross-references that must resolve. The assembler enforces the following references:

| Reference | From | To | Verification |
|---|---|---|---|
| Stressor # in §Reading the matrix | `contagion-analysis.md` | `stressor-catalog.md` | Every Stressor # cited in matrix readings exists in the Stressor Catalog. |
| `(T)` annotations in matrix | `contagion-analysis.md` | `stressor-catalog.md` Topological type | Every `(T)`-marked row is typed Topological in the catalog. |
| `Survived by Combination of #X, #Y` in Looping Signals | `contagion-analysis.md` | `stressor-catalog.md` | Every referenced residue # exists in the catalog. |
| `Hyperliminal Coupling #N` NFR Source | `residual-design.md` §Derived NFRs | `contagion-analysis.md` §Hyperliminal Coupling Map | Every NFR Source like `Hyperliminal Coupling #N` resolves to a row in the Coupling Map. |
| `Topology row N` NFR Source | `residual-design.md` §Derived NFRs | `contagion-analysis.md` §Topological Residue Map | Every NFR Source like `Topology row N` resolves to a row in the Topology Map. |
| `Business Residue #N` NFR Source | `residual-design.md` §Derived NFRs | `contagion-analysis.md` §Business Residues Log | Every NFR Source like `Business Residue #N` resolves to a row in the Business Log. |
| Residue Mapping per use case | `residual-design.md` §Behavioral Diagrams | `stressor-catalog.md` | Every residue # in a use case's Residue Mapping exists in the catalog. |
| Deployment Unit Boundary references | `residual-design.md` §Deployment Diagram | `contagion-analysis.md` §Topological Residue Map | Every boundary's `Topological Residue #` resolves to a row in the Topology Map. |
| C4 containers -> Service Grouping | `residual-design.md` §C4 Model container view | `contagion-analysis.md` §Service Grouping Map | Every `container` is a row of the Service Grouping Map; every split's `Boundary driver` resolves to an operational Topological residue (R-25). |
| Component names in Use Cases | `residual-design.md` §Behavioral Diagrams | `residual-design.md` §Static Architecture | Every component named in a use case appears in the Component Taxonomy. |
| Test stressor disjuncia | `empirical-test.md` | `stressor-catalog.md` | No test stressor (verbatim or semantic equivalent) appears in the catalog. |

If any cross-reference fails to resolve, refuse and direct the user to the upstream sub-skill responsible for the fragment that introduced the broken reference.

### Step 3 -- Assemble the SAD body

Stitch the fragments into a single `sad.md` following the structure in `sad/template.md`. The mapping:

| SAD section | Source fragment |
|---|---|
| §Methodological Note | Boilerplate from `template.md` (assembler writes verbatim). |
| §Business View | `business-view.md` inlined. |
| §Architectural Stress Analysis | Section header + boilerplate (assembler), then: |
| §Architectural Stress Analysis §Naïve Architecture | `naive-architecture.md` inlined. |
| §Architectural Stress Analysis §Flow Analysis | `flow-analysis.md` inlined. |
| §Architectural Stress Analysis §Stressor Catalog | `stressor-catalog.md` inlined. |
| §Architectural Stress Analysis §Contagion Matrix + §NKP Totals + §Refactor Triggers + §IDesign Override + §Hyperliminal Coupling Map + §Topological Residue Map + §Business Residues Log + §Looping Signals + §Service Grouping Map | `contagion-analysis.md` inlined. |
| §Architectural Stress Analysis §Derived NFRs | `residual-design.md` §Derived NFRs inlined. |
| §Architectural Stress Analysis §Empirical Test | `empirical-test.md` inlined. |
| §Analysis and Design | `residual-design.md` §Behavioral Diagrams + §General NFRs + §Structural Diagrams inlined. |
| §Technical Considerations | Boilerplate from `template.md` (assembler writes; may be project-customized via separate input). |
| §Technical Considerations §Architectural Fitness Functions | From `residual-design.md` -- one CI assertion per Call Rule + per Service Grouping Map row (R-03 / R-04 / R-25). The implementation-enforcement bridge. |
| §Restrictions | Boilerplate from `template.md` including the 8 guardrail rules. |
| §Appendices §References | Project PRD/SRD links + the standard book references. |
| §Appendices §Traceability Matrix | **Assembler-generated** (derived view). Consolidate the distributed chains -- residue -> component (R-18), NFR source (R-15), use-case residue mapping (R-16), deployment -> topology (R-19), optional PRD grounding -- into one row per residue. Introduces no new traceability; surfaces the existing chains at a glance. |
| §Appendices §Architecture Decision Records | If the project has ADRs, the assembler lists them in the per-project ADR table with their `Status`. For every `ACCEPTED` ADR whose `## Impact assessment` Outcome is `iterating Sn` / `reopen Sn`, the assembler MUST verify the decision is already reflected in the assembled body (the upstream fragment that fed it cites the ADR by id) -- it does NOT "reconcile" an accepted decision away with a note that keeps the contradicted structure. If an `ACCEPTED` non-`no-op` ADR is not reflected, **refuse to assemble** and direct the operator to apply the ADR's impact (re-emit the affected gate) or change its status. The per-project ADR table's `Status` column MUST be read live from each ADR file at assembly time (not copied from any upstream fragment's prose, which may be stale). The assembled body MUST reference ADRs by id only and MUST NOT restate an ADR's Status inline -- `check_adr_status_prose.py` flags a body status that disagrees with the ADR file. Otherwise left empty with a pointer to `adr-template.md`. |
| §Appendices §Stressor Source Frameworks | Boilerplate from `template.md` (the 6 frameworks summary). |
| §Appendices §Glossary | Boilerplate from `template.md`. |

The assembler does not modify the inlined content. If a fragment has a section header that does not match the template (e.g., a typo, a renamed section), the assembler refuses and directs the user to fix the fragment.

### Step 4 -- Write the executive summary

A one-paragraph executive summary goes at the top of the SAD, immediately after the title and before §Methodological Note. The summary's contents:

- **Sentence 1.** The system's objective (one line, drawn from §Business View).
- **Sentence 2.** The number of stressors analyzed, the breakdown by type, and the count of Looping Signals.
- **Sentence 3.** The NKP triple, the Ri value, and the iteration number.
- **Sentence 4.** A one-line architectural characterization (e.g., "Per-country deployment with auth/billing decoupling; criticality positive on iteration 1.").

The summary is the only synthesis the assembler is allowed to author. It is a reading aid for stakeholders, not a re-interpretation of the upstream content. If the assembler cannot write the summary in 4 sentences without contradicting any fragment, the fragments are inconsistent -- refuse.

### Step 5 -- Resolve cross-references in the assembled body

After stitching, the assembler walks the assembled `sad.md` and normalizes references:

- Stressor numbers across fragments must form a single contiguous sequence. If the Stressor Catalog has #1-#15, no fragment should reference #16 (would indicate inconsistency).
- Component names: every component name used in §Analysis and Design appears in the §Static Architecture component taxonomy.
- NFR Source references resolve to existing artifacts in the assembled document (no broken `Hyperliminal Coupling #99` style references).

### Step 6 -- Final hygiene checks

| Check | Verification | Rule |
|---|---|---|
| All fragments inlined | Every fragment appears in the assembled SAD at the expected section. | This sub-skill, Step 3 |
| No fragment content edited | The assembled SAD contains every line of each fragment verbatim (allowing only header-level adjustments to match template numbering). | This sub-skill, contract |
| Cross-references resolve | Every reference in the assembled body points to an existing target in the same document. | This sub-skill, Step 5 |
| Executive summary present | 4-sentence summary at the top. | This sub-skill, Step 4 |
| Style conventions respected | US-ASCII, mermaid diagrams, naming conventions per `shared/style-conventions.md`. | Style |
| Template sections present | Every section of `template.md` is filled or explicitly noted as not applicable. | Completeness |
| 8 guardrail rules in §Restrictions | The §Restrictions section includes the 8 decomposition discipline rules. | Boilerplate per template |
| ADR references resolve (if any) | If the project has ADRs and the SAD references them, each ADR-XXXX reference points to an existing ADR file. | `adr-template.md` convention |

If any check fails, refuse to write the final SAD.

---

## Output contract

One fragment file (the final SAD) in the project workspace:

### `sad.md`

The complete Software Architecture Document. Structure follows `sad/template.md` exactly, populated as described in Step 3. Frontmatter (per `shared/style-conventions.md` §4):

```
---
title: <project name> -- Software Architecture Document
version: <semver, e.g., 1.0>
date: <YYYY-MM-DD>
iteration: <N>
ri: <Ri value from S6>
---
```

The `iteration` and `ri` frontmatter fields are added by S7 (not present in fragment frontmatter; they characterize the assembled SAD). The `version` increments when the SAD is re-assembled after a new iteration of the meta-skill.

---

## Refusal conditions

| # | Trigger | Returned message |
|---|---|---|
| 1 | Any of the six required fragments is missing. | List the missing fragment(s). Direct the user to run the corresponding sub-skill. |
| 2 | Any fragment is unapproved. | List the unapproved fragment(s). User must approve before assembly. |
| 3 | A cross-reference fails to resolve (e.g., `Hyperliminal Coupling #99` not in the Coupling Map). | List the broken reference and its source fragment. Direct the user to fix the source fragment. The assembler does NOT silently fix references. |
| 4 | Fragment section headers do not match the template. | List the offending fragment + header. Direct the user to fix the fragment to match the template structure. The assembler does NOT silently rename headers. |
| 5 | Stressor numbering is non-contiguous or duplicated across fragments. | List the offending numbers. Stressor numbers must form one sequence; #5 cannot appear twice with different stressors. |
| 6 | A component named in §Analysis and Design is absent from §Static Architecture component taxonomy. | List the missing component. Direct the user to add it to the taxonomy in `residual-design.md`. |
| 7 | The executive summary cannot be written without contradicting a fragment. | Refuse. Identify the contradiction (e.g., NKP value in summary disagrees with NKP Totals in contagion-analysis). Direct the user to reconcile the fragments. |
| 8 | The Ri value from S6 is negative AND the project has not documented an explicit accepted exception. | Heuristic warning escalating to refusal. Shipping a SAD with `Ri < 0` is silently accepting an architecture worse than the naïve baseline. Recommend backtracking to S4 / S5 unless the user explicitly documents acceptance with rationale. |
| 9 | The user asks the assembler to edit fragment content. | Refuse. The assembler does not edit fragments. Edits live in the source sub-skill. |
| 10 | Two fragments report inconsistent NKP triples (e.g., contagion-analysis says N=27, K=58 and residual-design's NFR notes assume N=20). | Refuse. The NKP triple is computed once in S4 and inherited by downstream fragments. Inconsistency means a fragment was edited out of sync. |
| 11 | The test stressor list in `empirical-test.md` contains a stressor that also appears in `stressor-catalog.md`. | Refuse. Train/test disjuncia violation surfaced at assembly. Direct the user to fix `empirical-test.md` (remove the duplicate test stressor). |
| 12 | An `ACCEPTED` ADR's decision is not reflected in the architecture (its impact gate's fragment does not cite the ADR id, and its Outcome is not `no-op`). | Refuse. Run `scripts/fragment-checks/check_adr_applied.py <workspace-root>`; name the ADR + its impact gate; direct the operator to apply the impact or change the ADR status. Do not paper over it with an appendix reconciliation note. |

---

## Worked example

The EV charging worked example (`sad/examples/ev-charging-sad.md`) is itself the output of an S7-style assembly: every section in it inlines content that would have been produced by S1-S6 fragments. Reading the example bottom-up:

- §1 Naïve Architecture <- would come from `naive-architecture.md` (S1).
- §2 Flow Analysis <- `flow-analysis.md` (S2).
- §3 Stressor Catalog <- `stressor-catalog.md` (S3).
- §4 Contagion Matrix + §5 Topological Residue Map + §6 Business Residues Log + §7 Looping Signals <- `contagion-analysis.md` (S4). (The current example predates the Hyperliminal Coupling Map and NKP Totals sub-sections added in 2026-05-11; the next iteration of the example will include them.)
- §8 Derived NFRs + §10 Residual Architecture Summary <- `residual-design.md` (S5).
- §9 Empirical Test <- `empirical-test.md` (S6).
- §11 v2 Template Validation + §12 Closing Observation <- assembler-authored synthesis (this is the kind of content S7 may write in iterations 2+ of a project).

The example demonstrates that the assembler's output is a single coherent document that reads as one architecture, even though it is composed of seven independently approved pieces.

---

## Why these rules

- **Conservative integration.** The assembler not editing fragment content is the structural reason iteration works. Each sub-skill produces a stable artifact; S7 composes; if a fragment needs to change, the change happens in the source sub-skill and S7 re-assembles. Silent edits in S7 would break the iteration model.
- **Refusal on inconsistency.** Inconsistencies between fragments are signals that the upstream chain is out of sync. Silently resolving them in S7 would hide the synchronization problem and let it grow.
- **Executive summary as reading aid only.** The summary is the only writing S7 does. Limiting it to 4 sentences and requiring it to be consistent with every fragment prevents it from becoming a separate narrative that drifts from the architecture.
- **Negative Ri escalation.** Per `sad/synthesis-explanation.md` §11: shipping a SAD with negative Ri is silently accepting an architecture worse than the baseline. The assembler refuses to be the silent path to that outcome.

---

## References

- `shared/constitution.md` -- R-13 to R-24 (the synthesis-era rules the assembler validates indirectly via cross-references).
- `shared/decomposition-discipline.md` -- the 8 guardrail rules that go in §Restrictions of the assembled SAD.
- `shared/style-conventions.md` -- frontmatter, file naming, citation patterns, US-ASCII.
- `shared/glossary.md` -- vocabulary the assembled SAD draws on.
- `sad/template.md` -- the structural template the assembler follows. Authoritative for section structure, ordering, and boilerplate.
- `sad/synthesis-explanation.md` §11 -- the empirical stance the assembler enforces (positive Ri or documented exception).
- `sad/adr-template.md` -- the ADR convention the assembler references in §Appendices.
- `sad/examples/ev-charging-sad.md` -- the canonical worked example of a fully-assembled SAD.
