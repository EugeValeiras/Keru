<!--
TEMPLATE: phase0-evidence.md (handoff bundle)
Produced by the handoff-assembler sub-skill AFTER R1-R4 are all [x] approved. It packages the
four fragments into the three planes the SAD's "When a prior implementation exists (Phase-0 as
evidence)" mode accepts, each plane labelled with its SAD destination for direct copy-paste.
This is ASSEMBLY, not new analysis: do not add claims that are not already in R1-R4. Preserve
the anchors (RE-01), the confidence labels (RE-02), and the observed/anticipated split (RE-04)
exactly as approved. Delete this comment block.
-->

# Phase-0 Evidence -- <target name>

> Reverse-engineered from the running system by the `recon` skill (v0.1.2), gates R1-R4 approved on <dates>. This is the three-plane Phase-0 evidence the SAD's "When a prior implementation exists" mode consumes. Every claim is anchored to the target repo; inferred business intent carries confidence; observed stressors are separated from anticipated ones.
>
> **How to use this in a SAD project:** open a new SAD project, choose entry mode **β** (fresh SAD, this implementation as S6 evidence) or **γ** (SAD for the next phase). The naïve baseline stays the SAD's independently-built control -- this evidence never becomes the baseline. Then S1a..S7 runs unchanged.

---

## Business framing -> S1a

> Source: R3 `reconstructed-business-view.md`. Feeds the SAD's `business-discovery` (S1a). Intent is inferred; confidences below tell S1a how much to trust each item and which Open Questions need a stakeholder.

<!-- Inline R3's inferred objective / users / pain points / goals WITH their confidence + evidence, and the Open Questions for a stakeholder. Do not strip the confidence labels. -->

---

## As-built audit -> S6 evidence

> Source: R1 `system-cartography.md` + R2 `behavior-reconstruction.md` + R4's IDesign typing. This is a **residual candidate** the SAD's S6 (empirical Ri test) measures against the naïve baseline. It is evidence, never the baseline -- treating it as the baseline would destroy the empirical test.

<!-- Inline: the system map (entry points, modules, data stores, integrations, build/deploy) from R1; the observed flows from R2; the IDesign typing of the as-built from R4. Keep anchors. Descriptive only (RE-03). -->

---

## Observed stressors -> S3

> Source: R4 `asbuilt-stressors.md`. Held for the SAD's `stressor-analysis` (S3). These are the stressors S3 cannot generate on its own -- they required watching this specific system live. The Anticipated list overlaps with what S3 produces by method and is kept separate.

### Observed (anchored)

<!-- Inline R4's Observed stressors table with anchors intact (RE-04). -->

### Anticipated (not observed)

<!-- Inline R4's Anticipated section, clearly labelled as not-observed hypotheses. -->

---

## Provenance

| Plane | Source fragment(s) | Gate approved on |
|---|---|---|
| Business framing | reconstructed-business-view.md (R3) | <date> |
| As-built audit | system-cartography.md (R1), behavior-reconstruction.md (R2), asbuilt-stressors.md (R4) | <dates> |
| Observed stressors | asbuilt-stressors.md (R4) | <date> |

Recon version: 0.1.2. Confidence summary (from R3): <N high / M medium / K low>. If the business framing is mostly medium/low, the SAD should treat it as a hypothesis to confirm with a stakeholder, not a settled foundation.
