# recon prompt-eval set (model-driven, run by hand)

The mutation harness (`run-evals.py`) proves the **deterministic** layer catches
false anchors. This file is the other half: the **routing & gate-discipline**
eval, which needs the model and so cannot be made deterministic in CI. Run each
prompt against the installed skill in a scratch project and score the observed
behavior against **Expected**. A prompt **passes** only if every Expected bullet
holds.

Scoring: `pass` (all Expected hold) / `partial` (routes right, violates one gate
or anchoring rule) / `fail` (wrong route, or invents structure / unanchored
claims). Target: 0 `fail` on the routing + gate rows; every produced claim
anchored `file:line`/commit or marked `⚠ unverified` (RE-01); no redesign (RE-03).

Legend for gates: R1 system-cartography · R2 behavior-reconstruction ·
R3 business-reconstruction · R4 asbuilt-stressors.

---

## A. Entry routing — does the right gate open first?

| # | Prompt | Expected |
|---|--------|----------|
| A1 | "I inherited this repo and have no idea what it does. Help me understand it." | Routes to recon; opens **R1** first; states the gate chain; one fragment then STOP. |
| A2 | "Map every entry point, module, data store and external integration in here." | **R1**; inventory fragment only; does not jump to behavior or intent. |
| A3 | "Trace what actually happens when a request hits this service." | Recognizes this is **R2**, but refuses until **R1** is `[x] approved`; offers to start at R1. |
| A4 | "Why does this system exist and who is it for?" | Recognizes **R3** intent work; refuses ahead of R1→R2; explains the order. |
| A5 | "Where does this codebase hurt — what's fragile or hacky?" | Recognizes **R4** as-built stressors; gated behind R1–R3. |
| A6 | "We have an architecture doc in docs/. Is it still true?" | Routes to the **auditor diff/drift** mode; produces `audit-drift-<ref>.md`, not a fresh R1. |

## B. Gate discipline — one fragment per turn, then STOP

| # | Prompt | Expected |
|---|--------|----------|
| B1 | After R1 emitted but **not** approved: "great, keep going to R2." | Refuses; R2 will not run until R1 is `[x] approved`; points at the tracker. |
| B2 | "Do R1, R2 and R3 all now so I can read them together." | Refuses to batch; emits **only R1**, parks it, STOPS. |
| B3 | "Skip R1, just give me the business view." | Refuses to skip; explains R3 depends on R1→R2 evidence. |
| B4 | (Two gates approved) "what's the current state?" | Reports tracker position: which gates `[x]`, single active gate, what's next. |

## C. Backtracking / reopen

| # | Prompt | Expected |
|---|--------|----------|
| C1 | (R1 approved) "actually R1 missed the cron worker in jobs/ — fix it." | Reopens R1, re-emits the corrected fragment, re-parks; does not silently edit a downstream gate. |
| C2 | (R3 approved) "the inferred objective is wrong, it's a billing system." | Reopens R3; updates intent **with new evidence + confidence**; cascades only as needed. |

## D. Anchoring & honesty (RE-01 / RE-02 / RE-04)

| # | Prompt | Expected |
|---|--------|----------|
| D1 | "List the external integrations." | Each integration cites `file:line`/commit; anything inferred is `⚠ unverified`. |
| D2 | "What's the primary user persona?" | R3 intent carries a **confidence flag + evidence**, never a bare assertion (RE-02). |
| D3 | "The README says it autoscales — note that." | Doc-sourced claim is ranked **below code**: kept as a lead / `⚑ declared (not observed)` if unbuilt, not stated as fact. |
| D4 | "What are the biggest stressors?" | Only **observed** stressors (incidents, churn, coupling), each anchored; speculation segregated (RE-04). |

## E. Out-of-scope — recon must decline (RE-03)

| # | Prompt | Expected |
|---|--------|----------|
| E1 | "Propose a better, refactored architecture for this." | Declines: that is downstream SAD design work; recon describes what exists, never redesigns. |
| E2 | "Do a line-level security review of auth.go." | Declines: not recon's job; points to a review/security skill. |
| E3 | "Design this greenfield from this PRD." | Declines: recon is the brownfield front door; greenfield-from-PRD is the SAD's S1a. |

## F. Workspace placement (RE-05)

| # | Prompt | Expected |
|---|--------|----------|
| F1 | "Where will you write the tracker and fragments?" | Under **`docs/reverse-engineer/`** only — never the SAD's `docs/architecture/`. |
| F2 | (A `docs/architecture/` exists) "put the inventory next to the arch doc." | Refuses; keeps recon artifacts in `docs/reverse-engineer/`; cites the folder rule. |

---

## How to run

1. Install the bundle (`dist/recon-<version>/`) into a scratch project's `.claude/skills/`.
2. Use a small but real brownfield repo as the target (see EAI-89, the smoke test).
3. Issue each prompt, observe, and record pass/partial/fail + a one-line note.
4. Any deterministic claim the model emits can be spot-checked with the real
   validators (`tools/check-anchors.py`, `check-counts.py`, `repo-census.py
   coverage`, `check-workspace.py`) — that link back to the mutation harness is
   the point: the model proposes, the deterministic layer disposes.
