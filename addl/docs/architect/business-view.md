## Business View

> **Source corpus:** `Keru-Casos-de-Uso-MVP.md` (single document, Spanish). It merges two initiative layers: the **original scope** (`Keru-Scope-MVP.docx.pdf`, cited throughout as `§3.x`) and a batch of **product decisions dated 2026-07-09** that modify or supersede parts of that scope (admin pre-approval of caregivers, family members also record clinical data, caregiver history with rehire, bidirectional reviews, mandatory alerts with an always-available in-app record, invitation-based family linking, caregiver acceptance of requests, payments module suspended pending decision, multi-patient-profile accounts). Where the two layers speak to the same point, the 2026-07-09 decision governs (`Keru-Casos-de-Uso-MVP.md` header note). This Business View is ONE synthesized framing across both layers; genuine unresolved conflicts are logged in §Open Questions, not silently merged.
>
> **Changelog — Open Questions resolution pass (R-27), 2026-07-10.** Operator (stakeholder) answers were recorded against the open-question cards: OQ-1, OQ-2, OQ-3, OQ-4, and OQ-8 are resolved; OQ-6 and OQ-7 are partially answered and stay open; OQ-5 was explicitly deferred by the operator and stays open. The answers were rippled into the Objective, goals G1, G2, G3, G5, G6, G7, G9, G10, G11, invariant I5, deferred volatilities DV-3, DV-7, and new DV-11, and the carry-forward notes.
>
> **Changelog — Open Questions resolution pass 2 (R-27), 2026-07-10.** Second pass on operator (stakeholder) directives: OQ-6 is resolved — the 3-to-5-second configurable expectation also governs alert delivery (UC-18). OQ-5 and OQ-7 were explicitly closed by operator decision: OQ-5 with its substance (governing regulation, jurisdiction, consent basis) still undecided, carried forward as an unresolved compliance/consent input in DV-2; OQ-7 with the per-province zone definition accepted as not yet defined, carried forward as new DV-12. Ripple: G1, G6, and the carry-forward notes. No open question gates S1a after this pass.

### Objective

Keru is a caregiver marketplace ("the Uber of caregivers") that connects patients and their families with professional caregivers. Families and patients find caregivers by zone, type of care, and reputation, and hire them online; during the service, caregivers — and linked family members — record the patient's health metrics; the family follows the patient's state and evolution from anywhere. The platform curates the caregiver side: a caregiver becomes visible only after an internal review approves the account, and verification badges make credential, identity, and background checks visible to the demand side. The MVP's objective is to validate the complete end-to-end circuit — find and hire a caregiver, record the patient's metrics, and have the family see the patient's state; payment is outside the MVP: the patient pays the caregiver off-platform and marks the operation as paid on the platform, which closes it (OQ-1, resolved by the stakeholder 2026-07-10). (`Keru-Casos-de-Uso-MVP.md §1`, `§2`, `§UC-19`, `§Módulo C`)

### Pain Points

Pain points are synthesized from the product vision and the problems the documented capabilities exist to remove (`Keru-Casos-de-Uso-MVP.md §1`, `§2`, `§4`):

- Families cannot reliably find a trustworthy professional caregiver matched to their situation — by zone, care modality (home or hospital), type of care, availability, and rate — and today have no way to verify a candidate's credentials, identity, or background before letting them care for a vulnerable person. (`§1`, `§UC-06`, `§UC-07`, `§UC-19`)
- A family whose relative is cared for at home or in hospital has no remote visibility into the patient's condition; they depend on being physically present or on ad-hoc word of mouth from whoever is with the patient. (`§1`, `§UC-14`)
- Clinical observations made during care — vital signs, medication given, day-to-day events — are not captured in one shared, dated, attributable record, so there is no trustworthy history, no view of evolution over time, and no answer to "who recorded what, when". (`§UC-12`, `§UC-13`, `§UC-20`, `§6`)
- When a vital sign goes out of range or something notable happens to the patient, the family learns about it late or not at all. (`§UC-18`)
- Caregivers lack a channel to publish their professional profile (specialties, certifications, availability, rates, work zone) and to be found and hired on the strength of a verifiable reputation; they also take on clients blind, with no view of the patient/family's track record and no say before a hiring is imposed on them. (`§UC-02`, `§UC-10`, `§UC-21`)
- When a family wants to bring back a caregiver who served them well, there is no record of who cared for the patient and when, so rehiring a known, trusted person is needlessly hard. (`§UC-16`)
- One person often cares for more than one relative (e.g. both parents), and juggling searches, hirings, and clinical records for several patients without per-patient separation invites dangerous mix-ups. (`§UC-22`)

### Goals

Each goal is an observable outcome; success is verifiable without reference to any particular implementation.

- **G1 — Find a matching caregiver.** A family member or patient can find caregivers by combining filters — service zone, modality (home or hospital), type of care, availability, and rate range — and sees, already in the result list, each caregiver's rating, review count, and verification badges, because those are the choice criteria. A zone is a recognized geographic area; in the city of Buenos Aires (CABA) zones are neighborhoods, while what a zone is in each other Argentine province is not yet defined — an unknown the stakeholder explicitly accepted when closing OQ-7 (2026-07-10), carried forward as DV-12. (`§UC-06`)
- **G2 — Only approved caregivers are findable.** A newly registered caregiver is not visible to the demand side until an administrator has reviewed and approved the account; approved profiles show which certifications are platform-verified and which verification levels (certifications / identity / background) were granted. An approved caregiver ceases to be findable when they deactivate their own account, or when an administrator deactivates the account or hides it from the marketplace (OQ-8 answer). (`§UC-02`, `§UC-19`, `§UC-07`)
- **G3 — Hire with the caregiver's consent.** A hiring request for a specific patient (capturing modality, dates, special requirements, contact data) reaches the caregiver, who sees its detail — including the patient's reputation — and accepts or declines it; acceptance activates the care assignment, and the requester sees the status change and is notified of it. Payment stays off-platform: the patient pays the caregiver directly, then marks the operation as paid on the platform, and that closes the operation (OQ-1 answer). (`§UC-09`, `§UC-10`, `§UC-05`)
- **G4 — A traceable clinical record.** Caregivers with a current assignment and linked family members can record the patient's vital signs (blood pressure systolic/diastolic, heart rate, temperature, oxygen saturation, blood glucose), medication administrations (medication, dose, time, observations), and free-text notes; every record carries date/time and its author with role, and corrections never erase who recorded what. (`§Módulo D`, `§UC-12`, `§UC-13`, `§UC-20`)
- **G5 — The family sees the patient from anywhere.** A linked family member can consult the patient's current state, the chronological history interleaving vitals, medication, and notes, and per-metric evolution charts over an adjustable period, from any location and device; a record made by the caregiver or by another family member becomes visible within a refresh interval of 3 to 5 seconds, and that interval remains configurable for future analysis (OQ-6 answer). (`§UC-14`, `§UC-15`, `§6`)
- **G6 — The family is alerted, and no alert is lost.** When a recorded vital sign falls outside its applicable range — the platform-wide per-metric default the administrator configures for everyone, unless the patient's record carries a per-patient range that overrides the general default (OQ-4 answer) — or a note is recorded, every family member linked to the patient is alerted within the same 3-to-5-second interval that bounds visibility freshness — the stakeholder's stated bound, kept configurable (OQ-6 answer); every alert identifies the patient, metric, value, and time (or the note's text), remains retrievable in the application with a read/unread state and an unread count, and an immediate device notification — when the user has allowed it — is additional, never the only record. (`§UC-18`, `§Módulo G`)
- **G7 — Reputation cuts both ways.** After a finished service, the family/patient can rate and review the caregiver, and the caregiver can rate and review the patient/family — each independently of the other; caregiver reputation is visible in search results and profiles, and patient reputation is visible to the caregiver when evaluating new requests. Only participants of a real, finished service can review each other, each side reviews exactly once, and a review cannot be edited afterwards (OQ-3 answer). (`§UC-17`, `§UC-21`, `§Módulo F`)
- **G8 — One account, several patients, no mix-ups.** One account can create and manage multiple patient profiles (e.g. mother and father) and operate — search, hire, record, follow, invite, review — in the context of a selected profile; every hiring, clinical record, invitation, and review is tied to exactly one patient profile, and hiring one caregiver for two patients produces one request per patient. (`§UC-22`, `§UC-01`, `§UC-06`, `§UC-09`)
- **G9 — Joining the family circle is one shared invitation away.** A patient or an already-linked family member can invite a new family member by sharing a unique, patient-specific invitation through any channel; the same invitation works whether or not the invitee already uses Keru — an unregistered invitee completes registration and the link is established without additional steps, and a linked family member gains access only to the patients they are linked to. An invitation is valid for 30 minutes and is single-use — not reusable (OQ-2 answer). (`§UC-03`)
- **G10 — Known caregivers can be brought back.** A family member or patient can see the patient's currently assigned caregivers and the full history of past caregivers with their service periods, reach each one's current profile, and start a rehire from it; a past caregiver no longer active on the platform — whether they deactivated their own account or an administrator deactivated or hid them through the back office (OQ-8 answer) — still appears in the history, without a rehire option. (`§UC-16`)
- **G11 — MVP success criterion.** The complete end-to-end circuit is validated in real use: a family finds and hires a caregiver, the patient's metrics get recorded during the service, and the family sees the patient's state — on both mobile and web; the circuit counts as validated without money moving through the platform, closing each hiring via off-platform payment marked as paid on the platform (OQ-1 answer). (`§1`)

### Invariants (non-negotiables)

Regression guards for the empirical test (S6) — observable properties that must hold under every stressor. They are acceptance criteria, not units of decomposition (R-01/R-21).

| # | Invariant | Source |
|---|---|---|
| I1 | No caregiver ever appears in marketplace search results or receives hiring requests without prior administrator approval of the account. | `Keru-Casos-de-Uso-MVP.md §UC-19` (acceptance criteria), `§UC-02`, `§UC-06` |
| I2 | Every clinical record (vital signs, medication, note) permanently carries its date/time and its author with role; a correction never silently replaces a record — traceability is preserved. | `§UC-12` (acceptance criteria), `§UC-13`, `§UC-20`, `§6` |
| I3 | Access follows role and link: a caregiver can record data only for patients with a current assignment to them; a family member can read and record only for patients they are linked to. | `§UC-04` (acceptance criteria), `§UC-12`, `§UC-03`, `§6` |
| I4 | Every hiring request, clinical record, invitation, and review is bound to exactly one specific patient profile, never to the account in general. | `§UC-22` (acceptance criteria), `§UC-09` |
| I5 | A review exists only for a real, finished service between its author and its subject; each side reviews the other independently, at most once, and a review is never edited after it is made. | `§UC-17` (A1), `§UC-21` (A1, acceptance criteria); OQ-3 answer (operator, 2026-07-10) |
| I6 | Every alert reaches all family members linked to the patient and remains retrievable with read/unread state; an immediate device notification is never the only record of an alert. | `§UC-18` (acceptance criteria) |
| I7 | Finished assignments are preserved as history — never deleted — so the patient's caregiver history stays complete. | `§UC-05` (acceptance criteria), `§UC-16` |

### Open Questions

Unresolved business inputs surfaced by the multi-lens discovery pass (R-27), run **cross-layer** over the original-scope layer and the 2026-07-09 product-decision layer. Premises the document itself already resolves (family read-only → family also records, `§UC-14`; alerts optional → mandatory, `§Módulo G`; assignment manual → automatic on acceptance, `§UC-05`; caregiver must accept, `§UC-10`) are NOT logged — only what remains genuinely open. `Open` and `Open (partial)` questions gate S1a until the operator explicitly acknowledges proceeding.

Two **Open Questions resolution passes** (R-27) ran on 2026-07-10 with operator (stakeholder) input. After the first pass, OQ-1, OQ-2, OQ-3, OQ-4, and OQ-8 were resolved. The second pass closed the remainder: OQ-6 is resolved (the 3-to-5-second configurable bound also governs alert delivery); OQ-5 and OQ-7 were explicitly closed by operator decision — OQ-5 with its substance undecided (carried forward in DV-2), OQ-7 with the per-province zone definition accepted as undefined (carried forward as DV-12). **No question is in `Open` or `Open (partial)` status; nothing gates S1a.**

#### OQ-1 - Resolved (Answered) -- Payments module: in or out of the MVP

**Question:** Is online payment part of the MVP or not? The original scope (`§3.5`, and `§1`'s "complete end-to-end circuit") premised the validated circuit on hiring through the platform including payment; the 2026-07-09 decision suspends the module ("pending decision", UC-11 reserved, Module C withdrawn from the use cases). Until decided: does the MVP's "complete circuit" count as validated without money moving? If payments later land, the hiring lifecycle gains a "paid" state between acceptance (UC-10) and assignment activation (UC-05), and an external payment gateway becomes a dependency — with the stated integrity demands (no double charges on retries, persistent receipt).

**Answer:** Payment is outside the MVP: the patient pays the caregiver off-platform, but marks the operation as paid on the platform, and that is how the operation is closed. The MVP's "complete circuit" is therefore validated without money moving through the platform.

<sub>**Affects:** G3, G11 (what "end-to-end validated" means); hiring-request lifecycle; external-dependency set — **PRD:** `Keru-Casos-de-Uso-MVP.md §Módulo C` + `§7` (product decision 2026-07-09) vs original scope `§3.5` / `§1` — **Source:** operator (stakeholder), 2026-07-10</sub>

#### OQ-2 - Resolved (Answered) -- Invitation lifetime and reuse

**Question:** What is the family-invitation code/link's validity period, and is it single-use or reusable? UC-03 marks this explicitly "to be defined", and the domain model (`§5`) already gives the invitation an "expired" state with no rule for how it is reached. Note the internal conflict: the document's header asserts "no open assumptions remain", yet this item is still marked open in UC-03.

**Answer:** The validity period is 30 minutes, and the invitation is single-use — not reusable.

<sub>**Affects:** G9; I3 (link-scoped access — an over-live or freely reusable invitation widens who can read and write a patient's clinical data) — **PRD:** `Keru-Casos-de-Uso-MVP.md §UC-03` ("A definir") vs header note ("no quedan supuestos abiertos"); `§5` (InvitaciónFamiliar) — **Source:** operator (stakeholder), 2026-07-10</sub>

#### OQ-3 - Resolved (Answered) -- Second review of the same service: edit or forbid

**Question:** When a reviewer attempts a second review of the same finished service, is it rejected outright (one immutable review per side per service) or does it edit the existing review? UC-17 A2 marks this "to be defined"; UC-21 inherits the same restrictions for the caregiver-to-patient direction.

**Answer:** The review is made exactly once and cannot be edited later — one immutable review per side per service; a second attempt is rejected, not treated as an edit.

<sub>**Affects:** G7; I5 (whether "one review per side per service" is immutable-once-published or editable) — **PRD:** `Keru-Casos-de-Uso-MVP.md §UC-17` (A2, "a definir"), `§UC-21` (A1) — **Source:** operator (stakeholder), 2026-07-10</sub>

#### OQ-4 - Resolved (Answered) -- Who configures alert metric ranges, and what are the defaults

**Question:** Who defines the per-metric reference ranges that trigger out-of-range alerts (platform-wide defaults? per-patient by a family member? by the caregiver? by a clinician?), and what are the default values? UC-18 lists this explicitly under "points to define", while its precondition already assumes "reference ranges defined per metric". In a care context this is not a settings detail: whoever sets the ranges decides when a family is or is not warned about a health event.

**Answer:** Ranges depend on the metric being recorded; some ranges are homogeneous anywhere in the world (for example, low-grade fever starts at 37 °C and fever at 38 °C globally). The administrator configures the ranges on the platform for everyone, and beyond that general default — which each patient record carries by default — there can be per-patient ranges that differ from the general one.

<sub>**Affects:** G6; I6 (alert correctness — an alert can only be guaranteed if the triggering ranges have a defined owner and value) — **PRD:** `Keru-Casos-de-Uso-MVP.md §UC-18` ("Puntos a definir") — **Source:** operator (stakeholder), 2026-07-10</sub>

#### OQ-5 - Closed, not answered (deferred by operator decision, 2026-07-10; substance undecided) -- Governing health-data regulation, jurisdiction, and patient consent

**Question:** Which data-protection / health-data regulation governs the platform, in which jurisdiction(s) does it operate, and on what consent basis is a patient's clinical data processed? The document derives a generic sensitivity requirement from "the nature of the domain" (`§6`) but is silent on the governing legal constraint — and the product's own structure sharpens the question: patient profiles are created and managed by *other people* (the account holder registers their mother and father, `§UC-22`), specialties include pediatric and palliative care (`§UC-02`), and administrators manually process caregivers' identity and background/criminal-record documentation (`§UC-19`). Who consents on the patient's behalf, and what may the platform lawfully hold about caregivers' backgrounds?

**Answer:** None — the substance remains undecided. On 2026-07-10 the operator explicitly closed this question as a stakeholder decision to defer it: no governing regulation, no jurisdiction(s), and no patient-consent basis have been decided. This closure is a decision to stop gating S1a on the question, not an answer to it. The undecided substance stays visible downstream as an unresolved compliance/consent input recorded in DV-2, which S5's NFR derivation will hit; no regulatory content is assumed in the meantime.

<sub>**Affects:** I2, I3 (what traceability and access control must legally guarantee); G4, G5; caregiver-verification obligations (G2); DV-2 (carries the unresolved compliance/consent input forward) — **PRD:** `Keru-Casos-de-Uso-MVP.md §6` (silent on governing constraint), `§UC-19`, `§UC-22` — **Source:** operator (stakeholder), 2026-07-10 — closed as deferred; substance undecided</sub>

#### OQ-6 - Resolved (Answered) -- Quantify "real-time" / "no perceptible delay"

**Question:** What concrete freshness does the family-visibility promise require? The scope says the family follows the patient "in real time" (`§1`) and UC-14 accepts "visible without perceptible delay", but no number is given anywhere — seconds? a minute? And is the expectation the same for alert delivery (UC-18), where lateness has health consequences?

**Answer:** The refresh may occur every 3 to 5 seconds, and the interval is to be left configurable for future analysis. The same 3-to-5-second expectation also governs alert delivery (UC-18): an alert reaches the linked family members within that same configurable interval.

<sub>**Affects:** G5, G6 (measurability of the visibility and alerting goals; the thresholds downstream NFRs must commit to) — **PRD:** `Keru-Casos-de-Uso-MVP.md §1`, `§UC-14` (acceptance criteria), `§UC-18` — **Source:** operator (stakeholder), 2026-07-10</sub>

#### OQ-7 - Closed, partially answered (by operator decision, 2026-07-10; per-province zone definition remains undefined) -- What is a "zone"

**Question:** How is the "zone" that drives matching defined — a named neighborhood/city from a fixed list, a radius around a point, a drawn area? The term anchors both the caregiver's declared work zone (`§UC-02`) and the search's zone/location filter (`§UC-06`) but is never defined, and it admits materially different readings that change what "a caregiver serves this patient's zone" means.

**Answer:** Zones will be defined using the Google Maps API (the stakeholder's stated decision); in the city of Buenos Aires (CABA), for example, zones are neighborhoods. The known remainder: what a zone is for each other Argentine province is not yet defined — the stakeholder states it may differ per province and is not yet known. On 2026-07-10 the operator closed the question by decision, explicitly accepting that unknown; the per-province zone-definition variability is routed forward to S3 as DV-12.

<sub>**Affects:** G1 (whether search-by-zone is verifiable); caregiver profile content (G2); DV-12 (carries the accepted per-province unknown forward) — **PRD:** `Keru-Casos-de-Uso-MVP.md §UC-02` (flow step 6), `§UC-06` (filters) — **Source:** operator (stakeholder), 2026-07-10 — closed by decision; per-province definition remains undefined</sub>

#### OQ-8 - Resolved (Answered) -- How does a caregiver stop being active

**Question:** By what path does an approved caregiver become "no longer active on the platform", and who drives it? UC-16 A1 presumes such a state (a historical caregiver shown without a rehire option), but the documented caregiver account lifecycle is only pending → approved / rejected (`§UC-02`, `§5`) — there is no use case for voluntary departure, suspension, or revocation of approval (e.g. after serious negative reviews), and no owner named for it.

**Answer:** All users can deactivate their own accounts — in the caregiver's case, deactivation means they stop being visible in the marketplace. In addition, the administrator has access through the back office to all data and operations, and can deactivate users or make them not visible in the marketplace for some reason.

<sub>**Affects:** G10 (rehire availability); G2 / I1 (whether approval is revocable and by whom) — **PRD:** `Keru-Casos-de-Uso-MVP.md §UC-16` (A1) vs `§UC-02` / `§5` (account states) — **Source:** operator (stakeholder), 2026-07-10</sub>

> **Deferred volatilities (sensed now, routed to S3 -- non-gating).** Stressors the architect already senses and will deliberately address in stressor-analysis (S3). Carry-forward context only; they do NOT gate S1a.
>
> - **DV-1 — Clinically critical values and alert urgency.** An out-of-range vital is a potential health emergency; the cost of a missed, delayed, or silently dropped alert is asymmetric to everything else in the system (`§UC-12` A2, `§UC-18`).
> - **DV-2 — Health-data concentration and breach.** The platform accumulates sensitive clinical histories for many patients; exposure, leakage, or cross-patient disclosure is a domain-defining stressor (`§6`). Additionally, per the OQ-5 closure (deferred by operator decision, 2026-07-10), the governing data-protection / health-data regulation, the operating jurisdiction(s), and the patient-consent basis remain undecided — an unresolved compliance/consent input that S5's NFR derivation will hit; no regulatory content is assumed here.
> - **DV-3 — Payments landing later.** Online payment is now confirmed outside the MVP (OQ-1 answer): the hiring closes via off-platform payment marked as paid on the platform. The design must still not block a future online-payment landing — a "paid" state in the hiring lifecycle, an external gateway, retry integrity (no double charges), and receipts (`§Módulo C`, `§7` "do not design yet, do not block").
> - **DV-4 — Booking contention.** Overlapping requests to one caregiver, availability going stale after an acceptance, and the one-search-for-several-patients flow fanning out into per-patient requests (`§UC-06`, `§UC-09`, `§UC-10`).
> - **DV-5 — Reputation gaming and retaliation.** Fake or coerced reviews, and tit-for-tat dynamics that bidirectional reviewing invites (`§UC-17`, `§UC-21`).
> - **DV-6 — The manual approval queue as a growth bottleneck.** Caregiver supply is throttled by internal manual verification; a spike in signups stresses the back-office (`§UC-19`, `§4` of the scope).
> - **DV-7 — Invitation leakage.** An invitation shared through arbitrary channels can be forwarded or intercepted; whoever confirms it gains clinical-data access — now bounded by the OQ-2 answer (30-minute validity, single-use), which narrows but does not eliminate the window (`§UC-03`).
> - **DV-8 — Concurrent authorship of the clinical record.** A caregiver and several family members can record for the same patient at once; ordering, duplication, and correction semantics under concurrency (`§Módulo D`, `§UC-14`).
> - **DV-9 — Caregiver profile drift across rehires.** The historical caregiver's *current* profile (rates, zone, availability, active status) may differ from the one the family remembers (`§UC-16` A1).
> - **DV-10 — Out-of-scope items returning.** Chat between family and caregiver, wearable/medical-device integration, automated background checks, e-invoicing — excluded from the MVP but plausible next initiatives (`§7`).
> - **DV-11 — Back-office moderation ripple.** The OQ-8 answer defines two deactivation paths — any user can self-deactivate, and the administrator can deactivate a user or hide them from the marketplace through the back office. Either action landing mid-lifecycle (an active assignment, a pending hiring request, an unexpired invitation, a rehire in progress) stresses visibility, history, and rehire semantics (`§UC-16` A1; OQ-8 answer, operator 2026-07-10).
> - **DV-12 — Per-province zone-definition variability.** OQ-7 was closed by operator decision (2026-07-10) with zones defined via the Google Maps API and, in CABA, zones being neighborhoods — while explicitly accepting that what a zone is in each other Argentine province is not yet defined and may differ per province. That variability stresses zone-based matching (G1) and caregiver work-zone declarations (G2): a "zone" whose granularity or shape shifts by province changes what "a caregiver serves this patient's zone" means (`§UC-02`, `§UC-06`; OQ-7 closure, operator 2026-07-10).

#### Lens Coverage Ledger

| Lens | Verdict (OQ IDs, or `none`) |
|---|---|
| L1 Marker (TBC / TBD / unconfirmed / ?) | OQ-1 ("pendiente de decisión"), OQ-2 ("A definir"), OQ-3 ("a definir"), OQ-4 ("Puntos a definir") |
| L2 Hedge (maybe / assume / likely / should) | none — the parenthetical hedges found (e.g. `§UC-01` preconditions "none, or authenticated if...") resolve from a careful reading of the surrounding flow |
| L3 Unquantified target (~ / indicative / no number) | OQ-6 ("real time", "no perceptible delay" — no number anywhere) |
| L4 Undefined term (used but not defined; >1 reading) | OQ-7 ("zone") |
| L5 Silent actor / ownership (who triggers / approves / owns) | OQ-4 (range owner unnamed), OQ-8 (deactivation owner unnamed) |
| L6 Lifecycle / state gap (state with no entry/exit; flag semantics) | OQ-2 ("expired" state with no expiry rule), OQ-8 ("no longer active" state with no entry transition) |
| L7 Edge / failure silence (empty / negative / concurrent / failure) | none — candidates found were triaged to deferred volatilities (DV-4 booking contention, DV-8 concurrent authorship), since caregiver acceptance (`§UC-10`) is itself the documented conflict-resolution step and the rest is S3 material, not a stakeholder blocker |
| L8 Scope boundary (in/out unclear; deferrals; per-tenant divergence) | OQ-1 (Module C neither in nor out; UC-11 reserved) |
| L9 External / in-flight dependency (status unconfirmed) | OQ-1 (payment gateway is the only external dependency whose inclusion is unconfirmed) |
| L10 Conflict / measurability (contradictions; non-measurable goals) | OQ-2 (header "no open assumptions remain" vs UC-03's explicit "to define"), OQ-6 (the "real-time" goal is not measurable as stated) |
| L11 Stale / unexamined premise (settled decision on a stale/unverified premise) | OQ-1 (the scope-era premise that the validated E2E circuit includes online payment, `§3.5`/`§1`, is superseded-in-suspense by the 2026-07-09 decision). All other scope-era premises the 2026-07-09 layer touched are resolved *inside the document* (family read-only → also records; alerts optional → mandatory; manual assignment → automatic on acceptance; caregiver acceptance confirmed) and are therefore not open |
| L12 Regulatory / compliance / privacy silence (data/money/consent/AML/jurisdiction unaddressed) | OQ-5 (governing regulation, jurisdiction, patient consent basis, background-check data lawfulness) |

### Carry-forward (lateral context for downstream gates)

- **Two initiative layers, one framing.** Original scope (`§3.x` references) vs product decisions of 2026-07-09; the decisions govern where the layers overlap. The one genuinely unresolved cross-layer conflict — payments (OQ-1) — was resolved by the stakeholder on 2026-07-10: payment is outside the MVP (off-platform payment, marked as paid on-platform to close the operation); everything else the document reconciles itself.
- **Use-case inventory (module → UCs → layer).** The 21 use cases stay in the source document at full fidelity; they are NOT compressed into this view.

  | Module | Use cases | Layer origin |
  |---|---|---|
  | A — Users and authentication | UC-01, UC-02, UC-03, UC-04, UC-05, UC-22 | Scope §3.1; UC-03 mechanics, UC-02 pre-approval, and UC-22 are 2026-07-09 decisions |
  | B — Marketplace | UC-06, UC-07, UC-08, UC-09, UC-10 | Scope §3.2; UC-10 caregiver acceptance confirmed by decision |
  | C — Payments | (UC-11 reserved) | Outside the MVP (OQ-1 resolved 2026-07-10): off-platform payment, marked as paid on-platform to close the operation; UC-11 stays reserved |
  | D — Patient data recording | UC-12, UC-13, UC-20 | Scope §3.3/§3.7; family-also-records and UC-20 are decisions |
  | E — Patient state visualization | UC-14, UC-15, UC-16 | Scope §3.4; UC-16 history+rehire is a decision |
  | F — Bidirectional reputation | UC-17, UC-21 | Scope §3.6; UC-21 is a decision |
  | G — Alerts and notifications | UC-18 | Scope §3.7, elevated to mandatory by decision |
  | H — Back-office | UC-19 | Scope §3.2/§4; account pre-approval is a decision |

- **S2 (flow-analysis):** the use cases' main/alternative flows are the flow evidence; the E2E dependency order the document itself suggests (A → H → B → D → E → F → G, `§8`) is a reading aid, not a design commitment.
- **S5 (residual-design):** the source document is the **verbatim seed** for Use Cases with Residue Mapping — preserve each UC's flows, business rules, and acceptance criteria verbatim (anchored `Keru-Casos-de-Uso-MVP.md §UC-NN`, gaps marked `NEEDS CLARIFICATION`), and add the Residue Mapping the source cannot supply. The derived-NFR table (`§6`) seeds S5's NFR derivation; the OQ-6 answer supplies one measurable freshness bound for both visibility refresh and alert delivery (3–5 s, interval configurable). S5's NFR work will also hit the unresolved compliance/consent input left by the OQ-5 closure (governing regulation, jurisdiction, consent basis undecided — see DV-2).
- **Phase-0 evidence, never the baseline (R-09):** the document's mermaid use-case map (`§3`) and domain-model table (`§5`) describe the product's own domain/design structuring. S1b's naïve architecture MUST stay deliberately naïve — derived from this synthesized framing while *ignoring* that structure; the map and domain model are held as evidence for later gates (S5 reference, S6 residual-candidate comparison), never adopted as the control.
- **Invariant-backed vs ordinary goals:** G2↔I1, G4↔I2/I3, G8↔I4, G7↔I5, G6↔I6, G10↔I7 are invariant-backed; G1, G3, G5, G9, G11 are ordinary goals (no non-negotiable behind them beyond the shared access rule I3).
- **Out-of-scope guardrails (`§7`):** chat, medical-device/wearable integration, e-invoicing/fiscal reporting, automated background verification — excluded from MVP design; online payment is now excluded from the MVP too (OQ-1 answer: off-platform payment + on-platform mark-as-paid closes the operation), while a future online-payment landing stays unblocked (DV-3).
- **Deferred volatilities DV-1..DV-12** (above) route to S3 per the handoff contract; they are sensed stressors, not gating questions.
