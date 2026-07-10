---
name: handoff-assembler
description: Optional sub-skill of the `recon` meta-skill; after R1-R4 are approved, packages the four fragments into a single phase0-evidence.md with the three planes labelled for the SAD's "When a prior implementation exists" mode -- business framing -> S1a, as-built audit -> S6 evidence, observed stressors -> S3 -- preserving every anchor, confidence label, and observed/anticipated split. Invoke when assembling the Phase-0 handoff for a SAD.
task_types: [handoff-assembler, assemble-phase0-evidence, package-handoff]
shared_refs:
  - ../../shared/constitution.md
  - ../../shared/glossary.md
  - ../../templates/phase0-evidence.md
---

# handoff-assembler (optional)

Optional, terminal sub-skill of the recon chain. It runs **only after R1-R4 are all `[x] approved`** and integrates the four approved fragments into the single three-plane document the SAD consumes: `phase0-evidence.md`. Its job is to take what the four producers already established and lay it out in the shape the SAD's reception socket accepts -- nothing more.

The assembler's contract is **conservative**: it is **assembly / transcription, not analysis**. It does not re-read the target repo, re-derive a flow, re-type a component, or sharpen a confidence. It inlines approved fragment content under the three labelled planes and writes a small amount of boilerplate (the provenance table, the confidence summary, the "how to use this in a SAD" note). If it cannot lay out the planes without inventing a claim, it refuses -- the missing analysis belongs in the producer that owns it, not here.

The reason this discipline matters is epistemic, not cosmetic. The four fragments carry three markers that make them trustworthy: **anchors** (RE-01 -- every claim falsifiable on disk), **confidence labels** (RE-02 -- inferred intent carries its weight), and the **observed/anticipated split** (RE-04 -- stress this system showed vs. stress an architect anticipates). Those markers are exactly what lets the SAD route each plane correctly and decide how much to trust it. The assembler **preserves every one of them verbatim**. Stripping a confidence label, merging the two stressor lists, or "improving" a claim would smuggle un-audited content past the four gates that approved the originals.

---

## When to invoke

- R1, R2, R3, and R4 are **all `[x] approved`** in the gate tracker (`FLOW.md` §Current session), and the end-to-end auditor pass (recommended after R4) is done.
- The operator wants a **single copy-paste bundle** to carry into a new SAD project, rather than handing the SAD four separate fragment files.

## When NOT to invoke

- **Any gate is not yet `[x]`.** The assembler is not a way to "finish" recon early by skipping a gate or papering over an unapproved fragment. Run / approve the open gate first.
- **To add or sharpen analysis.** New flows, finer typing, recalibrated confidence, extra stressors -- all of that belongs in the producer that owns it (R1/R2 for the audit, R3 for the framing, R4 for the stressors), behind its gate. The assembler does not produce new findings.
- **As a substitute for the SAD.** The bundle is Phase-0 evidence the SAD consumes; it is not a SAD and does not decide a target architecture (RE-03 -- that is downstream).

## Pre-conditions

**ALL of R1, R2, R3, R4 are `[x] approved`** in the gate tracker -- verified, not assumed (root `SKILL.md` §Gate approval protocol). Before assembling:

1. Read the tracker (`FLOW.md` §Current session) and confirm every gate R1-R4 reads `[x] approved`.
2. Confirm each gate's named fragment exists on disk (`system-cartography.md`, `behavior-reconstruction.md`, `reconstructed-business-view.md`, `asbuilt-stressors.md`). A gate marked `[x]` whose fragment is absent is degraded to `[ ]` -- treat that as not approved.
3. Confirm the tracker is coherent -- the contiguous `[x]` chain R1 -> R2 -> R3 -> R4 required by **RE-05** (NON-NEGOTIABLE). A non-contiguous chain (e.g., R3 `[x]` while R2 is `[?]`) is a tracker inconsistency; refuse and point to it.

If any gate is not `[x] approved`, **refuse** (see §Refusal conditions). The assembler is not a gate and grants no approvals -- it only packages what the four gates already approved.

## Handoff contract

- **Consumes:** the four **approved** fragments -- `system-cartography.md` (R1), `behavior-reconstruction.md` (R2), `reconstructed-business-view.md` (R3), `asbuilt-stressors.md` (R4) -- plus `templates/phase0-evidence.md` (the structure to fill). All four prior gates must be `[x] approved`.
- **Produces:** a single `phase0-evidence.md` in the target's `docs/reverse-engineer/`. This is **NOT a gate** and parks at no `[?]` -- it is an assembly artifact. There is no STOP-at-gate; the bundle is presented for the operator to carry to a SAD.
- **Carry-forward (into a SAD project, not into another recon gate):** the operator opens a new SAD project and chooses entry mode **β** (a fresh SAD, this implementation as S6 evidence) or **γ** (a SAD for the next phase, this implementation as a residual candidate S6 measures). In every mode the **naïve baseline stays the SAD's independently-built control** -- this evidence is a residual candidate S6 *measures*, it **never becomes the baseline** (RE-03; treating it as the baseline would destroy the empirical Ri test). Then S1a..S7 runs unchanged; the SAD is never patched.

## Workflow

### Step 1 -- Verify all four gates `[x]` (refuse otherwise)

Run the Pre-conditions check: R1-R4 all `[x] approved`, fragments present on disk, tracker coherent per RE-05. If any gate is not approved, the chain is non-contiguous, or a fragment is missing, **refuse** and name the open gate. Do not assemble a partial bundle.

### Step 2 -- Build `## Business framing -> S1a` (from R3)

Inline R3's `reconstructed-business-view.md` -- the inferred **objective / users / pain points / goals**, each **with its confidence (`high|medium|low`) and the evidence anchor that supports it** -- plus the **Open Questions** for a stakeholder. Do **not** strip or soften the confidence labels (RE-02): the confidence is the load-bearing signal that tells S1a how much weight each inferred item bears and which Open Questions need a stakeholder.

### Step 3 -- Build `## As-built audit -> S6 evidence` (from R1 + R2 + R4 typing)

Inline, descriptively (RE-03 -- no `should` / refactor / renaming):

- the **system map** from R1 (entry points, services/modules, data stores, external integrations, build/deploy topology, runtimes);
- the **observed flows** from R2 (use cases / flows reconstructed from routes, handlers, jobs, schedulers, tests);
- the **IDesign typing of the as-built** from R4 (Manager / Engine / ResourceAccess / Resource / Utility / Client) plus the observed coupling/contagion.

Keep every anchor intact (RE-01). Label this plane clearly as a **residual candidate the SAD's S6 measures** -- evidence, never the baseline.

### Step 4 -- Build `## Observed stressors -> S3` (from R4)

Inline R4's two sections **exactly as approved**, preserving the split (RE-04):

- `### Observed (anchored)` -- R4's Observed stressors table, every row keeping its anchor (incident link, churn count + command, coupling metric, `file:line` of a HACK/TODO, commit SHA).
- `### Anticipated (not observed)` -- R4's Anticipated section, clearly labelled as not-observed hypotheses.

Do **not** merge the two lists. The observed stressors are the signal only recon can supply (they required watching this system live); S3 generates anticipated stressors by its own method, so it must be able to tell the two apart.

### Step 5 -- Provenance table + confidence summary

Add the **provenance table** (which plane came from which fragment, and each contributing gate's approval date from the tracker) and the **confidence summary** carried from R3 (`N high / M medium / K low`). Note that if the business framing is mostly medium/low, the SAD should treat it as a hypothesis to confirm with a stakeholder, not a settled foundation. These are the only items the assembler authors, and they introduce no new claims -- they surface the provenance and the existing confidence distribution.

### Step 6 -- "How to use this in a SAD" note + present

Write the one-paragraph note: open a new SAD project, choose entry mode **β** or **γ**, and remember the naïve baseline stays the SAD's independently-built control -- this evidence is **never** the baseline. Then **present the assembled bundle** to the operator to carry to the SAD. There is **no STOP-at-gate** (the assembler is not a gate); the bundle is the deliverable.

---

## Output contract

One file in the target's `docs/reverse-engineer/`:

### `phase0-evidence.md`

Structured per `templates/phase0-evidence.md`:

- the three planes, each **labelled with its SAD destination** -- `## Business framing -> S1a` (R3), `## As-built audit -> S6 evidence` (R1+R2+R4 typing), `## Observed stressors -> S3` (R4 Observed + Anticipated);
- the provenance table and confidence summary;
- the "how to use this in a SAD" note (modes β/γ; never the baseline).

**Every anchor (RE-01), every confidence label (RE-02), and the observed/anticipated split (RE-04) appear verbatim from the approved fragments.** The bundle contains no claim that is not already in R1-R4.

---

## Refusal conditions

| # | Trigger | Returned message |
|---|---|---|
| 1 | Any of R1-R4 is not `[x] approved` (or its fragment is absent on disk, or the tracker chain is non-contiguous per RE-05). | Premature assembly. Name the open / missing / inconsistent gate; direct the operator to approve it (or resolve the tracker) first. The assembler is not a gate and grants no approvals. |
| 2 | Asked to add, sharpen, or "improve" a claim during assembly (a new flow, finer typing, recalibrated confidence, extra stressor). | Refuse. Assembly is not analysis. Route the request back to the producer that owns it (R1/R2 audit, R3 framing, R4 stressors), behind its gate. |
| 3 | Asked to strip / soften confidence labels, or to merge the observed and anticipated stressor lists. | Refuse. RE-02 (confidence is the load-bearing signal for S1a) and RE-04 (S3 needs the observed/anticipated split) -- both must survive verbatim. |
| 4 | Asked to present the as-built as the SAD's baseline. | Refuse. The as-built is a **residual candidate / S6 evidence**, never the baseline (RE-03). The SAD builds its naïve baseline independently; treating the as-built as the baseline destroys the empirical Ri test. |

---

## Why these rules

- **The three-plane shape is the SAD's reception socket.** The SAD's "When a prior implementation exists (Phase-0 as evidence)" mode accepts exactly business framing (-> S1a), an as-built audit (-> a residual candidate S6 measures), and observed stressors (-> held for S3). Labelling each plane with its destination is what lets the operator drop the bundle into a SAD project and have S1a..S7 run unchanged, with no patch to the SAD.
- **Preserving anchors / confidence / the split is what makes the handoff trustworthy.** Those three markers are how the SAD routes each plane and calibrates how much to trust it: anchors make every claim checkable in one click; confidence tells S1a whether to proceed or seek a stakeholder; the observed/anticipated split gives S3 the live-system signal it cannot generate itself. Strip any of them and the SAD is building on un-audited material.
- **Adding analysis here would smuggle claims past the gates.** The four gates exist so a human approves each fragment before it propagates. A claim invented in the assembler never faced a gate. Keeping the assembler to assembly-only is the structural reason the gated chain holds end to end.

---

## References

- `../../shared/constitution.md` -- **RE-01** (evidence anchoring -- preserve every anchor), **RE-02** (inferred intent labelled -- preserve every confidence), **RE-04** (observed stressors only -- preserve the observed/anticipated split), **RE-05** (tracker coherence -- the contiguous `[x]` chain R1-R4 the Pre-conditions require).
- `../../shared/glossary.md` -- the three planes (Phase-0 evidence), residual candidate, entry mode β / γ.
- `../../templates/phase0-evidence.md` -- the bundle structure this sub-skill fills.
- Root `SKILL.md` -- §"The output -- the three planes (Phase-0 evidence for the SAD)" and §Gate approval protocol.
- `sad-*/SKILL.md` -- the downstream consumer; its "When a prior implementation exists (Phase-0 as evidence)" reception socket is what this bundle is shaped to fit.
