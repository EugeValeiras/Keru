<!--
Emitted by speckit-handoff (S8) at RDAG 0.1.0.

This artifact is the GATE WIRING that makes CHK-03 true by construction. Apply
it to the consumer's `.specify/templates/plan-template.md` at landing (Phase 2),
replacing the stock single-tier Constitution Check section.

WHY: spec-kit's stock plan-template carries a generic "Complexity Tracking"
table that lets ANY violation be "justified" -- including an architecture one
("ERROR if violations unjustified" is the escape valve). RDAG requires Q1-Q6 to
be NON-WAIVABLE. The two-tier block below excludes Q1-Q6 from Complexity
Tracking and makes a failure a hard stop -> catalog/ADR amendment request.
-->

# Constitution Check (two tiers)

Run at the start of every `/speckit-plan`. Tier 1 is **non-waivable** -- no
Complexity Tracking entry can carry a Tier-1 failure forward. Tier 2 is the
usual implementation gate and may be waived per the project's Complexity
Tracking discipline.

## Tier 1 -- Architecture half (NON-WAIVABLE)

For each question, answer Yes/No against the plan being proposed. A single **No**
is a **hard stop**: the plan cannot proceed; raise a catalog amendment or an ADR
request to the architecture team. **These questions are EXCLUDED from Complexity
Tracking.**

| # | Question | Resolves against |
|---|---|---|
| Q1 | Is every service in `plan.md` present in the service catalog (at the declared release)? | `architecture/arch-X.Y.Z/system-design/service-catalog.md` |
| Q2 | Does each service name follow the category suffix (`*Manager` / `*Engine` / `*Access`)? | naming convention (Lowy) |
| Q3 | Does the call chain respect the layer rules (no `Manager`->`Manager` sync, no `Client`->`ResourceAccess`, no `Engine`->`Manager`)? | the use case's "Architectural Context" (verbatim from `architecture/arch-X.Y.Z/use-cases/`) |
| Q4 | Does each service list at least one Structural stressor identifier (`S-NN`) in its Stressors-absorbed field? | `service-catalog.md` Stressors-absorbed (Structural by R-18) |
| Q5 | Does each NFR record a coupling (or topology) identifier (`C-NN`) in its Source field? | `architecture/arch-X.Y.Z/system-design/nfr-register.md` |
| Q6 | Does the plan's runtime / protocol / middleware conform to all binding ADRs? | `architecture/arch-X.Y.Z/decisions/ADR-*.md` (binding) + the manifest's binding-ADRs list |

A **No** triggers an architecture-team review request:

- **Q1 No** -> catalog amendment request (the architecture team decides whether to add the service, in a new release).
- **Q4 / Q5 No** -> the architecture is wrong here, not the plan -- raise back to the SAD.
- **Q6 No** -> the plan must conform, or a new ADR must be raised; the implementation cannot decide unilaterally (Architecture Supremacy).

> A Tier-1 violation is NOT eligible for Complexity Tracking. There is no "we
> will revisit later" path through Tier 1.

## Tier 2 -- Implementation half (waivable, Complexity Tracking applies)

The implementation-half principles (language, testing, observability, security,
...) are checked here as usual. A violation may be carried as a documented
Complexity Tracking entry per the project's amendment policy.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| (example) 4th project | (current need) | (why 3 projects insufficient) |
| ... | ... | ... |

(This table behaves like the stock `plan-template.md` Complexity Tracking.)

---

**Drop-in instructions.** In the consumer's `.specify/templates/plan-template.md`,
replace the existing "Constitution Check" + "Complexity Tracking" sections with
this two-tier block. Keep the rest of the template (Summary, Technical Context,
Project Structure, ...) untouched.
