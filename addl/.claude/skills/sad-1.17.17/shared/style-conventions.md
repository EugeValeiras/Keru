---
title: Style conventions -- Software Architecture Document meta-skill
version: 1.1
date: 2026-05-21
---

# Style Conventions

Repository-wide writing and formatting conventions. Applies to all markdown produced by the meta-skill (templates, sub-skill outputs, doctrinal references, examples). Does not apply to source books in `righting-software-md/` or `residuality/residuality-md/` which are external content.

When in doubt, match the conventions used in `sad/template.md` and `sad/examples/ev-charging-sad.md` -- they are the de-facto reference for SAD output style.

---

## 1. Character set and punctuation

- **US-ASCII only** in skill content, doctrine files, templates, and worked examples. No smart quotes, no em-dashes, no en-dashes, no curly apostrophes.
- Use `--` (two ASCII hyphens) where you would use an em-dash.
- Use `'` (straight apostrophe) and `"` (straight quote).
- Exception: source book contents in `righting-software-md/` and `residuality/residuality-md/` are preserved as-is (they may contain Unicode punctuation from PDF conversion).

**Why.** Skill content is consumed by tools that may not handle Unicode consistently; ASCII guarantees clean rendering everywhere.

---

## 2. Language

- **English** mandatory in skill content: every `SKILL.md`, every file under `sad/`, every file in `shared/`.
- **Spanish allowed** in process documents: `PLAN.md`, `FLOW.md`, `TASK.md`, `CHECKLIST.md`, `CLAUDE.md`. These are internal to the team; the user works in Spanish; English would add friction without benefit.
- **Mixed allowed** only in process documents when citing English source material.

---

## 3. File naming

- Markdown files: `lowercase-hyphenated.md`. Examples: `business-discovery.md`, `idesign-vocabulary.md`, `ev-charging-sad.md`.
- Directories: `lowercase-hyphenated/`. Examples: `sad/`, `business-discovery/`, `examples/`.
- Avoid: snake_case, camelCase, PascalCase for file/directory names. Underscore `_` is reserved for cases where hyphen would be ambiguous (rare).
- Foundation documents at repo root use UPPERCASE: `PLAN.md`, `FLOW.md`, `TASK.md`, `CHECKLIST.md`, `CLAUDE.md`, `README.md`. Convention preserved from prior practice.

---

## 4. Frontmatter

Doctrinal and normative files start with YAML frontmatter:

```
---
title: <document title>
version: <semver, e.g., 1.0>
date: <YYYY-MM-DD of last substantive change>
---
```

Sub-skill `SKILL.md` files use the skill-creator harness frontmatter (`name`, `description`, `task_types`, optional `shared_refs`) -- not the doctrinal frontmatter above.

Process files (`PLAN.md`, `FLOW.md`, `TASK.md`, `CHECKLIST.md`) do NOT use frontmatter -- they are working documents updated frequently.

---

## 5. Headings

- ATX style only: `# H1`, `## H2`, `### H3`, etc.
- One `# H1` per file (the document title or section equivalent).
- Avoid setext underlining (`===`, `---` after a line of text).
- Skip levels only when the structure justifies it -- prefer continuous nesting.

### 5.1 Fragment headings start at `###` (the SAD reserves `#`/`##`)

The assembled SAD (S7) uses `#` for the title and `##` for top-level sections (§Business View, §Architectural Stress Analysis, §Analysis and Design, ...). So **sub-skill fragments must start their internal headings at `###`** -- a fragment that uses `##` for its internal sections collides with the SAD's `##` sections and forces the assembler to demote headings by hand. Fragment authors (S1-S6): the fragment's own title may be `##` (it becomes a SAD subsection), but everything internal to it is `###` and deeper.

### 5.2 Iterations within a fragment: the Delta convention

When a project iterates (S6 -> S3 feed-forward), a fragment gains new content for iteration N+1. Do NOT stack raw addenda that leave iter-N and iter-N+1 counts coexisting in the same prose (that is what forces the assembler to reconcile counts by hand). Instead, append a **`### Delta -- iteration N+1`** subsection that states what changed, and follow one rule: **the canonical counts/values are those of the latest Delta.** Earlier iterations stay as history below the latest Delta, clearly dated, never silently overwritten. The assembler and the R-13 count-consistency check both read the latest Delta as authoritative; prose summaries must reflect the latest Delta, not an earlier one.

---

## 6. Diagrams

Representation is split three ways by diagram kind. The kind, not the authoring convenience, decides the tool:

- **Mermaid `flowchart`** -- reserved for **naive-architecture baselines only** (S1b: the naive static / call-topology diagram). These are the genuine "flow" baselines and the **only** Mermaid in a SAD. Embedded as `\`\`\`mermaid ... \`\`\``; renders natively in GitHub and most markdown previewers (no external dependency), which is why the cheap, throwaway naive baseline keeps it.
- **PlantUML** -- for the residual **§Static Architecture (IDesign)** diagram, the **§Behavioral Diagrams** (activity / sequence diagrams), and any class / state diagram. Authored as `\`\`\`plantuml` fenced blocks (the canonical source); rendered downstream (see §6.2). Not Mermaid.
- **Structurizr DSL** -- for all **C4 architecture** (one `workspace.dsl`; see §6.1). Rendered downstream via the Structurizr -> C4-PlantUML pipeline.
- No committed image files (`.png`, `.jpg`, `.svg`) for hand-drawn diagrams; the `\`\`\`plantuml` / `\`\`\`dsl` / `\`\`\`mermaid` source is authoritative and renders downstream. Source-book images are exempt (they live with their source documents).
- **Net:** a SAD has at most one Mermaid block (the naive baseline); the residual Static Architecture + every behavioral diagram are PlantUML; C4 is the `workspace.dsl`.

### 6.1 C4 architecture: one Structurizr DSL workspace, correct scope per derived view

All C4 architecture in any SAD fragment, worked example, or doctrinal reference is expressed as a **single Structurizr DSL `workspace.dsl`** (R-23). One `model` defines people, software systems, containers, and components **once**; the views derive each C4 level from that model. This makes level-mixing structurally impossible (a `component` is nested inside its `container`) and yields a single validatable source plus crisp rendered images.

| C4 level | DSL view | What it shows |
|---|---|---|
| Level 1 -- System Context | `systemContext <system>` | Target `softwareSystem` + `person`s + external `softwareSystem`s (tag `"External"`). No internal detail. |
| Level 2 -- Container | `container <system>` | The target system's `container`s (deployable / runnable units: apps, services, `"Database"`/`"Queue"` stores). One container per §Service Grouping Map row. |
| Level 3 -- Component | `component <container>` | One container's nested `component`s (IDesign Managers / Engines / ResourceAccess / Utilities). One view per container with 2+ IDesign components. |
| Level 4 -- Deployment | `deployment <system> <env>` | `deploymentNode`s (cloud / region / cluster / pod) with `containerInstance`s mapping Level-2 containers to infrastructure. |
| Dynamic (optional) | `dynamic <scope>` | Sequence-style runtime interaction for a specific flow. |

#### The model (authored once)

```
workspace "<System Name>" "<Brief description>" {
    model {
        // people
        <id> = person "<Name>" "<description>"
        // target system, with containers nesting components
        <sys> = softwareSystem "<System>" "<description>" {
            <svc> = container "<Service / Deployable Unit>" "<description>" "<technology>" {
                <mgr> = component "<XxxManager>" "<description>" "<tech>" "Manager"
                <eng> = component "<XxxEngine>" "<description>" "<tech>" "Engine"
                <ra>  = component "<XxxAccess>" "<description>" "<tech>" "ResourceAccess"
            }
            <db>  = container "<Store>" "<description>" "<tech>" "Database"
            <bus> = container "Message Bus (<broker>)" "<description>" "<tech>" "Queue"
        }
        // external systems
        <ext> = softwareSystem "<Third Party>" "<description>" "External"
        // relationships (source initiates) -- see call rules below
        <id> -> <svc> "<verb phrase>" "<technology>"
        <mgr> -> <eng> "<verb phrase>"
        // deployment
        deploymentEnvironment "<Env>" {
            deploymentNode "<cloud>" {
                deploymentNode "<region>" {
                    deploymentNode "<service node>" {
                        containerInstance <svc>
                    }
                }
            }
        }
    }
    views {
        /* see below */
        styles {
            /* IDesign tags */
        }
    }
}
```

#### What goes at each level

**System Context** (`systemContext <sys>`): the target `softwareSystem`, the `person` actors, the external `softwareSystem`s (tag `"External"`). The view scope **excludes** containers and components automatically -- non-technical audience.

**Container** (`container <sys>`): the `container`s inside the system boundary. A container is a **separately deployable / runnable thing** (service, DB, queue, app), never an IDesign component / class / library / module. Data stores carry tag `"Database"` (`shape Cylinder`); queues / buses carry tag `"Queue"`. **One container per row of the §Service Grouping Map (S4, R-25)**; the `container` name equals the `Service / Deployable Unit` name from that map verbatim.

**Component** (`component <svc>`): the IDesign `component`s nested inside one service container, tagged by layer. A component is **NOT separately deployable** -- it lives in its container's deployment unit. **One Component view per container with 2+ IDesign components.** Containers with 0-1 components are exempt (the §Container <-> Component mapping table covers them).

**Deployment** (`deployment <sys> <env>`): `deploymentNode`s nesting cloud > region > cluster > pod, with `containerInstance`s placing Level-2 containers on infrastructure. Per-jurisdiction Topological residues (R-19) -> separate top-level `deploymentNode`s.

#### Vocabulary (Structurizr DSL)

- **People:** `<id> = person "<label>" "<description>"`.
- **Systems:** `<id> = softwareSystem "<label>" "<description>" ["<tags>"]`; external -> tag `"External"`.
- **Containers:** `<id> = container "<label>" "<description>" "<technology>" ["<tags>"]`; stores -> `"Database"`, queues -> `"Queue"`, third-party -> `"External"`.
- **Components:** `<id> = component "<label>" "<description>" "<technology>" "<IDesign layer tag>"` where the layer tag is one of `Manager` / `Engine` / `ResourceAccess` / `Resource` / `Utility` / `Client`.
- **Deployment:** `deploymentEnvironment "<env>" { deploymentNode "<label>" "<description>" "<technology>" ["<instances>"] { deploymentNode {...} | infrastructureNode <...> | containerInstance <id> } }`.
- **Relationships:** `<source> -> <destination> "<label>" ["<technology>"]`; source is who **initiates**.
- **Views:** `systemContext` / `container` / `component` / `deployment` / `dynamic`, each with `include *` and `autoLayout` (default unless explicit layout is requested).
- **Styles:** one `element` block per tag, **one property per line** (see the one-statement-per-line rule below):

  ```
  styles {
      element "<tag>" {
          background <#rrggbb>
          color <#rrggbb>
          shape <Shape>
      }
  }
  ```

  Map IDesign layers to colours so the render reads as IDesign (suggested: Manager / Engine / ResourceAccess / Utility distinct backgrounds; `"Database"` -> `shape Cylinder`; `"Queue"` -> `shape Pipe`; `"External"` -> grey).

> **One statement per line (Structurizr DSL requirement, validated 2026-06-21).** Every `{` MUST be the **last token on its line** and every statement MUST be on its **own line**. The compact single-line forms `deploymentNode "pool" { containerInstance svc }` and `element "Manager" { background #1168bd color #ffffff }` are **rejected** by the Structurizr parser ("Number of instances must be a positive integer or a range" and "Too many tokens, expected: element <tag> {" respectively). Always emit the expanded multiline form -- including nested `deploymentNode`s (one `deploymentNode "..." {` per line) and `element` styles (one `background`/`color`/`shape` per line).

> **Render-format requirement (validated 2026-06-20).** The IDesign-layer **tag** colours only survive an exporter that applies per-tag element styles. Structurizr's **`plantuml`** exporter (`-format plantuml`) does -- it emits a PlantUML stereotype per tag with the tag's `BackgroundColor`, so Manager/Engine/ResourceAccess/Utility render in distinct colours. The **`plantuml/c4plantuml`** exporter (the `c4-skill`'s default) does **not** -- it colours strictly by C4 macro type (Person/System/Container/Component), so every component renders the same blue and the IDesign layer is lost. Renderers MUST use a tag-style-preserving export (`plantuml`, or any path that honours element-tag styles). This is a renderer concern, not a skill rule, but the §6.1 "reads as IDesign" claim depends on it.

#### Utilities in C4: the Utility is a Component, the broker is a Container

An IDesign Utility (`PubSubUtility`, `SecurityUtility`, `LoggingUtility`) is a `component` tagged `Utility`, nested inside the service containers that use it. It is **never a `container`.** The infrastructure it fronts (Kafka / NATS broker, secret store, log sink) **is** a `container` -- but **named for the infrastructure, not the Utility**: `container "Message Bus (Kafka)" ... "Queue"`, not `container "PubSubUtility"`. Each service's `PubSubUtility` component relates to that broker container.

References: Structurizr DSL language reference (docs.structurizr.com/dsl/language); C4 model official site (c4model.com). Updated 2026-06-20 with the Mermaid -> Structurizr DSL migration (R-23).

### 6.2 PlantUML: residual Static Architecture + behavioral diagrams

The residual §Static Architecture (IDesign) diagram and every §Behavioral Diagram (activity / sequence) are authored in **PlantUML**, embedded as a `\`\`\`plantuml` fenced block holding a single `@startuml ... @enduml` document. The PlantUML source is the canonical, reviewable artifact; it renders downstream to SVG/PNG (PlantUML server / CLI / the c4-skill pipeline) -- it does NOT render natively in GitHub, the same trade-off the C4 `workspace.dsl` accepts (§6.1). A SAD `.md` read without a renderer still carries the readable PlantUML source.

| Diagram | PlantUML form | What it shows |
|---|---|---|
| §Static Architecture (IDesign) | component diagram (`@startuml` + `component` / `package` + `-->` edges) | The IDesign layers (Client / Manager / Engine / ResourceAccess / Resource / Utility) and the closed-architecture call edges (R-03 / R-04). One diagram per SAD. |
| §Behavioral Diagrams (per use case) | activity diagram (`@startuml` + `start` / `:action;` / `if/else` / `stop`) or sequence diagram (`participant` + `->`) | The runtime flow of one use case across the residual components, with the Residue Mapping. |

#### Conventions

- One `@startuml ... @enduml` per fenced `\`\`\`plantuml` block. Give it a `title`.
- **Static Architecture:** group components by IDesign layer (e.g., `package "Managers" { ... }`); draw only call edges that obey the Call Rules (R-03/R-04). The auditor parses these edges for R-03 the same way it parses the §C4 Model `workspace.dsl` relationships.
- **Behavioral:** prefer activity diagrams for process flows (the use-case happy path + branches); use a sequence diagram only when the cross-service interaction is the point. Name lanes / participants after the residual IDesign components so the §Residue Mapping resolves.
- **US-ASCII only** (house style); PlantUML syntax is ASCII anyway.
- No `!include` of remote URLs in skill content (keeps the source self-contained); a standalone `@startuml` is enough.

The naive-architecture baseline (S1b) is the **one exception** that stays Mermaid `flowchart` (§6) -- it is the cheap throwaway baseline, not residual doctrine.

References: PlantUML language reference (plantuml.com/guide). Added 2026-06-20 with the non-C4 Mermaid -> PlantUML split (style-conventions §6); see §6.1 for C4.

---

## 7. Citations

Cite sources with these patterns (chosen for grep-ability and to match the constitution):

| Source | Citation pattern | Example |
|---|---|---|
| Lowy book | `Lowy L<start>-<end>` | `Lowy L1085-1105` |
| O'Reilly book | `O'Reilly L<start>-<end>` | `O'Reilly L807-867` |
| Synthesis explanation | `synthesis-explanation §<n>` | `synthesis-explanation §6 Decision 2` |
| Template | `template §<SectionName>` | `template §Stressor Catalog` |
| Constitution rule | `R-NN` | `R-13` |
| Guardrail | `guardrail #N` | `guardrail #4` |
| Sub-skill | `<sub-skill-name>` (lowercase-hyphenated) | `stressor-analysis` |
| PRD / SRD source line | `PRD:L<n>` or `PRD §<x>` (or `SRD:...`) | `PRD:L158`, `PRD §5.3` |

Always cite the source rather than restating it. The constitution and templates are the canonical source for rules and structure; reference docs build on them by cross-citation.

For a single-line citation: `Cited Lowy L1027.` For a range or section: `Cited Lowy L981-1077 (the four layers).`

- **ADR references.** Cite an ADR by its id (`ADR-NNNN`). Do not transcribe its `Status` into prose --
  the ADR file's `Status` cell is the source of truth (it is operator-owned and mutates). Only the
  assembler's §Appendices ADR table shows a Status, read live from the ADR file at assembly time.
  (Enforced by `scripts/fragment-checks/check_adr_status_prose.py`.)

### 7.1 Source grounding to the PRD/SRD (optional, but bounded)

When the SAD is produced from a PRD/SRD with stable line numbers, ground artifacts back to the requirement that motivates them, using the `PRD:L<n>` pattern. This makes the SAD auditable against its source. It is **optional** (many SADs are produced without a stable-line PRD) but recommended in regulated / certification contexts.

What CAN be grounded to the PRD (it comes from the PRD):

- **Business View** items -- objective, pain points, goals, invariants (S1 Step 1.2).
- **Naive Architecture** components -- the requirement each component answers.
- **Structural residues** whose technical change responds to an *explicit* requirement.

What must NOT be force-grounded:

- **Genuine stressors.** By definition a stressor is "a fact about the context not accounted for in the naive architecture" -- it is *not* in the PRD. Anchoring a real stressor to a PRD line is a contradiction (if it were in the PRD it would not be a stressor). Stressors trace to their generating framework (PESTLE / boundary / every-noun / ...), not to the PRD.

If a project has no line-stable PRD, omit grounding refs entirely -- do not invent line numbers.

---

## 8. Tables

- Use pipe-delimited markdown tables.
- Always include the separator row (`|---|---|...`).
- Right-align numeric columns when alignment improves scannability; otherwise default left-align.
- Escape literal pipes inside cells with `\|`.
- Tables with more than ~10 columns or ~30 rows are usually a sign the data wants a different format -- consider splitting.

---

## 9. Lists

- Unordered lists use `-` (single hyphen + space).
- Ordered lists use `1.` `2.` `3.` (let markdown handle numbering; do not manually number `1.` `1.` `1.`).
- Indentation: 2 spaces or 4 spaces, consistent within a file.
- Nested lists: blank line before the nested level only when the nested content is multi-line.

---

## 10. Code spans and blocks

- Inline code: backticks. Use for: file paths (`shared/constitution.md`), command names (`mv`), code identifiers (`ChargeSessionManager`), constitution references (`R-13`), guardrail references (`guardrail #4`).
- Fenced code blocks for multi-line code, with a language hint where applicable: `\`\`\`bash`, `\`\`\`yaml`, `\`\`\`mermaid`, `\`\`\`python`. Plain `\`\`\`` only when no language fits.

---

## 11. Cross-document references

- Link to a file with `\`relative/path/to/file.md\`` (backticked path). Example: `` `shared/constitution.md` ``.
- Link to a section with `\`file.md§SectionName\``. Example: `` `template.md §Stressor Catalog` ``.
- Use markdown links `[text](path)` only when the path is verbose or when the link is a primary navigation aid (e.g., in cross-reference tables at the end of a document).

---

## 12. Versioning

- Doctrinal and normative files (constitution, glossary, template, synthesis-explanation, etc.) carry a `version` and `date` in frontmatter. Increment `version` on substantive change to rules / structure, not on typo fixes.
- Process files (PLAN, FLOW, TASK, CHECKLIST) do not carry version metadata; their state is the present tense of the project.
- Sub-skill `SKILL.md` files inherit versioning conventions from the skill-creator harness, separate from this scheme.

---

## 13. What not to do

- Do not use emojis in skill content, doctrine, templates, or worked examples. (User has not requested them; they reduce machine-parseability and look out of place in technical documentation.)
- Do not write multi-paragraph docstrings or comment blocks in markdown files -- if a section needs explanation, put it in a section, not a side-note block.
- Do not commit `.DS_Store`, `__pycache__/`, editor swap files, or other OS / tool noise. The repo `.gitignore` covers the common cases; if a tool generates new noise, extend `.gitignore`.
- Do not introduce new normative documents without a frontmatter `version` and `date`. If a file isn't worth versioning, it probably isn't normative.
- Do not embed PDFs, Word docs, or other binaries in the doctrine. Source books are in dedicated directories with their own conversion scripts; user-facing doctrine is markdown only.
