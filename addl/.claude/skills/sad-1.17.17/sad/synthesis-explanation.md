# From Two Methods to One Practice -- Synthesizing IDesign and Residuality

> **Purpose**: This document explains how and why we combined two software architecture methods -- Juval Lowy's **IDesign** (the volatility-based decomposition method from *Righting Software*) and Barry O'Reilly's **Residuality Theory** (from *Residues: Time, Change, and Uncertainty in Software Architecture*) -- into a single working practice for designing and documenting software architectures.
>
> **Audience**: Senior architects who do not yet know either method. By the end of this document you should understand what each method offers, why neither is sufficient on its own, what theoretical bridge connects them, what specific synthesis decisions we made, how we validated the synthesis empirically by running it against the book's own canonical example, and how to actually use the resulting template and worked examples on your own projects.
>
> **What this is not**: a sales pitch. We will be explicit about what each method does poorly, what we discarded, and where the synthesis is still incomplete.

---

## 1. The architect's dilemma

A software architecture has to last while the world around it changes. Customers, markets, regulations, technologies, competitors, geographies, and the internal politics of a business are in constant motion. The software, by contrast, is rigid -- code does what it does, and changing it is expensive. The job of the architect is to design a structure that absorbs change without collapsing, before knowing which specific changes will arrive.

The traditional response to this problem has been imported wholesale from physical-world engineering: gather requirements, list risks, apply patterns from previous projects, decompose by use cases or business processes. This works in stable, predictable domains -- bridges, cars, factories. It works less well when the *context* of the system is itself volatile. And almost every interesting software system today executes in a volatile context.

Two methods we will discuss respond to this problem in different ways, from different intellectual lineages, and end up -- perhaps surprisingly -- covering each other's blind spots almost exactly.

---

## 2. What IDesign brings

IDesign was developed by Juval Lowy and codified in *Righting Software* (2019). It is a **decomposition method**: given a system, it tells you how to break it into components such that the components are organized around volatility rather than around features, processes, or use cases.

Its central claim is that the natural decomposition lines of a system are the lines along which the system is most likely to change. If you decompose by what changes together, your components stay coherent under stress; if you decompose by what behaves together (use cases, processes), your components fragment as soon as the business behavior shifts.

IDesign provides three things:

**A taxonomy**. Components belong to one of five layers, with strict naming conventions:

- **Clients** are entry points (UI, external callers).
- **Managers** (named `<Verb>Manager`) orchestrate workflows. They are the only stateful workflow holders.
- **Engines** (`<Noun>Engine`) encapsulate volatile business logic. They are stateless.
- **ResourceAccess** (`<Noun>Access`) translates business operations into resource operations. Stateless.
- **Resources** are databases, queues, external APIs.
- **Utilities** are cross-cutting concerns (logging, security, configuration).

**Strict call rules**. Calls between layers are tightly constrained. Clients call Managers. Managers call other Managers asynchronously only, never synchronously. Managers call Engines and ResourceAccess. Engines call ResourceAccess. ResourceAccess is the only layer that touches Resources. Upward calls are forbidden. Engines do not call Engines (they share via the Manager that orchestrates them).

**A method**. IDesign also prescribes a procedure for validating a decomposition: walk every use case as a sequence diagram through the layers, ensure every call respects the rules, ensure every component has a justified reason to exist.

What IDesign gives you, in practice, is **a clear, opinionated, teachable vocabulary for expressing static architecture** plus a discipline that makes communication patterns predictable. A team that adopts IDesign produces architectures that look similar across projects, communicate with each other through known patterns, and resist the most common form of architectural decay (Manager logic leaking into Engines, Engines knowing about Resources, ad-hoc upward calls).

What IDesign does not give you is a way to know if your **volatility list is correct**. The method assumes you can identify what changes. If your prediction of volatility is wrong, your decomposition is wrong, and IDesign provides no mechanism to discover that until production tells you.

---

## 3. What Residuality brings

Residuality Theory was developed by Barry O'Reilly over roughly a decade, formalized through a series of academic papers, and published as the short book *Residues* in 2024. It is the result of investigating why some senior architects consistently produce architectures that survive in unpredictable environments while their formally-trained colleagues do not.

O'Reilly's diagnosis is that the successful architects have abandoned requirements-driven and pattern-driven design in favor of something that looks, on the surface, like skeptical pessimism: they *stress the architecture from many random angles* until it stops breaking. He gives this practice a theoretical foundation drawn from complexity science (Stuart Kauffman's work on Random Boolean Networks) and from continental philosophy (Deleuze on difference, Bergson on time, Whitehead on process).

The core ideas:

**A residue is what's left of an architecture after exposure to a stressor.** This is the unit of architecture. An architecture is not a static diagram; it is a collection of residues over time, each one expressing how the architecture changes in response to a particular pressure.

**A stressor is any fact about the context that is not accounted for in the current architecture**. Crucially, probability is excluded. The architect does not need to predict what will happen. The architect needs to enumerate things that could happen and reason about how the architecture would respond.

**Stressor analysis is a random simulation of the environment**. By generating diverse stressors -- drawn from PESTLE, Porter's 5 Forces, Business Model Canvas, abstraction-stressing, lateral thinking -- the architect builds a sample of the possible attractors (recurring states) of the business system. Each attractor demands a residue. The architecture is the integration of all residues.

**The contagion matrix is a diagnostic tool**. Stressors as rows, components as columns. A `1` means the stressor affects the component. The matrix surfaces hidden coupling (two components that react to the same stressor are coupled, even if no functional dependency connects them), components that are doing too much (high column totals), components that should be merged (identical column signatures), and the overall topology of stress propagation.

**Criticality emerges through looping**. As more stressors are analyzed, eventually new stressors arrive that are *already survived* by combinations of existing residues. This is the empirical signature that the architecture has reached criticality -- it can survive things it was not designed for. O'Reilly calls this the mathematical leverage of the method: each residue covers an unbounded set of unknown future stressors that share its attractor shape.

**The empirical Ri test**. A residual architecture can be tested by generating a fresh list of stressors not used in design, applying them to both the naïve baseline and the residual architecture, and computing Ri = (Y - X) / S, where X and Y are stressors survived by each, and S is the test set size. Ri > 0 indicates positive movement toward criticality.

What Residuality gives you, in practice, is **a way to discover unknown unknowns** -- and a method that produces empirically falsifiable claims about architecture quality.

What Residuality does not give you is a **vocabulary or discipline for expressing the result**. The book is explicit about this: "How to integrate residues into a single coherent architecture is not something residuality can teach you. A good grounding in distributed systems and service orientation is necessary." Residuality identifies the residues; it leaves the integration to the architect's existing toolkit.

---

## 4. The bridge -- why these two methods compose

This is where the synthesis becomes more than convenience. The two methods are not arbitrary partners; they are **theoretically complementary** at a level deeper than the surface methodologies.

O'Reilly's framework rests on Kauffman's analysis of complex systems. Three parameters govern how attractors (recurring states) emerge in a network:

- **N** -- the number of nodes (components).
- **K** -- the number of links between them.
- **P** -- the *bias* of each node: its tendency to behave predictably in response to inputs.

Kauffman showed that when N, K, and P are balanced, a system reaches criticality: it has enough structure to be stable, enough flexibility to absorb stress, and few enough attractors to remain comprehensible.

O'Reilly notes -- and this is the critical line in the book -- that "SOLID, DRY, OOP and most pattern approaches are directed toward finding the right balance of N, K, and P." He observes that **P is raised by restricting how components interact**: through interfaces, service orientation, uniform error handling, predictable communication patterns.

This is, almost word-for-word, what IDesign does. IDesign's call rules -- Manager-to-Manager only async, Engines do not call Engines, only ResourceAccess touches Resources -- are a method for fixing P high. Its layered taxonomy is a method for restricting K to predictable topologies. Its naming conventions and stateless/stateful discipline make components behave predictably enough that other components can rely on them without coordination.

In other words: **IDesign is an opinionated, teachable, transferable method for setting two of the three Kauffman parameters**. It provides the bias and the topology. What it cannot do is tell you whether the values it sets are correct for your specific context. That diagnosis requires running the system against random samples of the environment -- which is exactly what Residuality's stressor analysis does.

The bridge, then, is this:

> **IDesign provides the language. Residuality provides the evidence. Each method has the gap the other fills.**

This is not a vague analogy. The contagion matrix in Residuality literally measures the K of the architecture (number of stressor-component links), reveals where K is too high (hot rows, hot columns), and provides the diagnostic feedback needed to know whether IDesign's chosen taxonomy is paying off in this context. The looping behavior -- when new stressors are absorbed by existing residue combinations -- is the empirical signature that P, K, and N have reached criticality.

Once seen, this complementarity is hard to unsee. The two methods stop looking like alternatives and start looking like two halves of one practice that neither author had quite finished.

---

## 5. What we kept from each method

The synthesis was conservative: we kept almost everything from both methods that did not directly conflict.

From **IDesign** we kept:

- The five-layer taxonomy and naming conventions, exactly as Lowy specifies them.
- The strict call rules, treated as hard constraints.
- The stateless/stateful axis as a structural property that overrides certain residuality signals (more on this below).
- The principle that the static architecture is expressed in this taxonomy and these rules.
- The deployment topology as a derived output, not an input.

From **Residuality** we kept:

- Stressor analysis as the primary discovery tool, replacing requirements gathering as the driver of decomposition.
- The contagion matrix as the diagnostic instrument and the source of non-functional requirements.
- The empirical Ri test as the validation mechanism.
- The philosophical stance against probability and cost as filters during analysis (they enter later, in ATAM and FMEA).
- The unit of architecture being the residue, not the component or the pattern.
- The distinction between criticality (the architectural goal) and correctness (the developer's goal).

What we **discarded**:

From IDesign, we set aside Lowy's "method" as the primary decomposition driver. The method walks use cases through the layers as sequence diagrams to validate decomposition. We could not use this as the lead artifact because Residuality is explicit that use-case-driven decomposition produces architectures that fail when the business process changes, and Parnas (1972) said the same thing fifty years ago. We kept use cases -- they are still valuable for documenting behavior -- but moved them downstream of the decomposition decision.

From Residuality, we discarded nothing fundamental. What we *added* was the structural language IDesign provides, because Residuality alone leaves the architect with a list of residues and no canonical way to express their integration.

---

## 6. The seven synthesis decisions

Beyond the conservative "keep what works" stance, the synthesis required seven specific decisions, each of which warrants explanation.

### Decision 1 -- Stress analysis precedes design diagrams

The single most important reordering. In a traditional template, you start with use cases or requirements and produce diagrams from them. In ours, you produce the naïve architecture, then run stressor analysis and contagion matrix, *then* document the resulting residual architecture with diagrams.

The reason is straightforward: if diagrams come first, the team builds emotional attachment to them and treats stressor analysis as confirmation of an already-decided design. If stress analysis comes first, the diagrams are an honest output, not a defended position.

### Decision 2 -- Stressors are typed

Not all residues produce the same kind of architectural change. A residue can change components, deployment topology, or only business decisions; some residues are not new at all but combinations of existing ones absorbing a new stressor.

We classify each residue as:

- **Structural** -- drives a change in IDesign components or call topology. Enters the contagion matrix.
- **Topological** -- drives a change in deployment topology (geography, tenancy, replication). Enters a separate topological residue map.
- **Business** -- produces a business decision but no software change. Recorded in a business residues log.
- **Combined** -- survived by an existing combination of residues. No new component or deployment change. Recorded as a looping signal.

This is a non-trivial improvement over either source method. Pure Residuality treats all residues as a flat list; pure IDesign has no concept of business-only or combined residues at all. Without this typing, business residues either get dropped from the catalog (and the conversation that produced them is lost) or get forced awkwardly into the matrix.

### Decision 3 -- The IDesign override on merge signals

Residuality's contagion matrix sometimes suggests merging two components with identical stress signatures. This is correct *within a layer*: two Engines with the same column signature can often merge.

But the matrix will also suggest merging across layers -- for example, a Manager and its dedicated Engine often co-evolve and have similar signatures. This is a residuality false positive. IDesign discipline -- stateless versus stateful, the call rules, the layer separation -- must override this signal. Manager--Engine pairs are structurally distinct by IDesign rule and must not be merged regardless of matrix similarity.

This override is documented inline in the matrix-reading section. It is the most important place where IDesign actively *disciplines* a residuality conclusion rather than merely complementing it.

### Decision 4 -- NFRs are traceable, with three possible sources

A standard problem in SAD templates is that non-functional requirements are filled in with generic boilerplate ("the system must be efficient", "the system must be available"). These are unfalsifiable, untestable, and useless.

In our synthesis, every NFR must trace to one of three sources: a specific cell in the contagion matrix (component-level NFRs like atomic distributed freeze, idempotency under failover), a specific row in the topological residue map (residency, latency-zone, sovereignty NFRs), or a specific business residue (operational NFRs that do not produce code but constrain behavior -- such as "billing must support non-charging revenue streams by configuration").

If an NFR cannot trace to one of these three, it is not a real NFR for this system. It is a copy-paste from a previous template.

### Decision 5 -- Use cases as documentation, not driver

Use cases survive in the SAD, but their role changes. They no longer drive decomposition. They document the behavior of the *already-resolved* residual architecture. Each use case includes a *Residue Mapping* subsection that explicitly traces which residues (Structural, Topological, Business) the use case exercises.

This compromise preserves the communicative value of use cases -- they are still useful for stakeholder conversations, regulatory documentation, and onboarding -- without letting them dictate structure.

### Decision 6 -- Looping signals are formalized

When a new stressor arrives and is already survived by a combination of existing residues, this is the empirical signature of approaching criticality. The book treats this as narrative observation; we treat it as a structured artifact.

Each combined residue is recorded with explicit "survived by combination of #X, #Y, #Z" trace and notes on why the combination works. These are the strongest persuasive material in the entire SAD -- they are the moments where the architecture absorbs an unforeseen stressor without code changes -- and they need to be findable and trace-able, not buried in prose.

### Decision 7 -- Decomposition discipline as guardrail rules

The synthesis is enforced by eight explicit rules in the *Restrictions* section of the template:

1. No new structural component without a Structural residue justifying it.
2. No new deployment unit without a Topological residue.
3. No business decision affecting architectural reasoning is undocumented.
4. No NFR without traceability to matrix cell, topology row, or business residue.
5. No use case is the source of a decomposition decision.
6. No probability or cost discussion until the matrix is complete.
7. No cross-layer merge based on matrix similarity alone (IDesign override).
8. Combined residues are recorded, not discarded.

These rules are the difference between adopting the method and performing its rituals. They are also the rules that get enforced in design review.

---

## 7. How we validated the synthesis

A method that has not been tested against its source material is just an opinion. We did two things to test ours.

**First**, we ran the **wallet example** -- a multi-currency wallet with thousands-of-TPS scale targets. This was a familiar-domain case. The method produced a residual architecture, surfaced a hyperliminal coupling that matters in wallets (atomic distributed freeze across Compliance, Balance, Account when sanctions hit), and identified specific NFRs -- for example, idempotency under DB failover -- that traced cleanly to matrix cells. The wallet example confirmed the method *works on a domain we know*.

**Second**, and more importantly, we ran the **EV charging example from O'Reilly's own book**. This is the canonical worked example in Chapter 6 of *Residues*. By running it through our template, we tested whether our synthesis distorts the source material or fits it.

The result was that the **first version (v1) of the template fit the book's example reasonably well, but with two visible gaps**:

- Stressor #13 in the book (privacy regulation forcing per-country data residency) is fundamentally a deployment topology decision, not a component decomposition. It did not fit cleanly in the *Static Architecture* section.
- Stressors #4, #6, #7, #11 in the book (EV market crash, competitor pricing, manufacturer lock-in, competitor coverage) produce business decisions but no software change. They had no place in the template at all and risked being dropped.

These two gaps generated a **second version (v2)** of the template, which adds:

- The *Topological Residue Map* as a separate subsection feeding the *Deployment Diagram*.
- The *Business Residues Log* as a decisions-of-record annex.
- The *Looping Signals* subsection as a formal place to record combined residues (specifically, the book's two most persuasive moments: ICE-ing absorbed for free by combinations of residues, and the AFIR EU regulation absorbed ten years after design without rewrites).
- The *IDesign Override Note* in the matrix-reading guidance.

Re-running the book's example against v2 closed the gaps without distortion. **And it produced a small surprise**: the *Business Residues Log*, which we added expecting it to be a documentation annex, turned out to *generate two new NFRs* (operational diversification readiness, capacity-aware site provisioning) that v1 had no way to surface. The log is not ceremony; it is a real source of operational requirements that get lost when business conversations end without code.

This is the right pattern for maturing an architectural method: build the synthesis, test it against a canonical case, identify gaps as concrete failures rather than abstract worries, fix the gaps with traceable changes, re-test. We have done this once. The method should be expected to evolve again as it meets cases that v2 also fails to fit.

---

## 8. The artifacts you are receiving

The bundle consists of several markdown files. They are designed to be read in this order:

**The synthesis explanation** (this document). Read first, once. It explains the reasoning behind everything else.

**The template (v2)**. The normative artifact. This is what you fill in when you produce a Software Architecture Document (SAD). It is structured to enforce the seven synthesis decisions through its sections, headers, and discipline rules.

**Two worked examples**. The first works through the EV charging system from O'Reilly's book -- the canonical case -- and includes a section explicitly explaining what changed between v1 and v2 of the template. The second works through a multi-currency wallet at scale. Read at least one before attempting to fill in the template yourself.

**The v1 versions** (template and EV example) are also kept in the bundle as historical artifacts. They are useful for understanding what was wrong with the first cut and why the gaps mattered. Do not use them as references; use v2.

The bundle is internally consistent: vocabulary in the explanation matches the template, the worked examples use the template's section structure, and every concept in the glossary is used in the worked examples. If you find an inconsistency, it is a bug -- please flag it.

---

## 9. How to actually run this on your next project

Theoretical understanding is not enough; the method only sticks through use. Here is the practical path.

**Start with the naïve architecture.** Draw the simplest IDesign-compliant decomposition that solves the problem as the SRD or PRD describes it. Resist the urge to be clever. The naïve architecture is supposed to be naïve -- its job is to be the control against which the residual architecture will be measured. If you start clever, you have nothing to measure against.

**Generate stressors broadly before generating them deeply.** The first session should produce thirty to fifty stressors of mixed quality. Use PESTLE, Porter's 5 Forces, the Business Model Canvas, and abstraction-stressing (challenge every noun in the domain model: *Customer*, *Order*, *Account* -- what if they are not what you think?). Do not filter for probability. Do not filter for cost. The point is breadth.

**Type each stressor as you go.** Structural, Topological, Business, or Combined. The discipline of typing forces you to think about what kind of change the stressor implies, and prevents the catalog from becoming a dumping ground.

**Build the contagion matrix only after the catalog stabilizes.** Premature matrix construction creates emotional attachment to columns. Wait until the stressor catalog has stopped growing meaningfully (or until new stressors arrive as Combined more often than as new entries -- that is the looping signal).

**Read the matrix, do not just fill it in.** The matrix has seven distinct readings (hot rows, hot columns, multi-1 rows, identical signatures, globally high K, zero-total columns, stressor combinations). Each reading produces a refactor candidate. Apply the IDesign override before merging anything across layers.

**Express residues in IDesign vocabulary, not in service names.** "Add a microservice for X" is not a residue change; it tells you nothing about responsibility, statefulness, or call rules. "Add `XManager` orchestrating `XEngine` over `XAccess` to a new `XResource`" is a residue change. The IDesign vocabulary forces specificity.

**Do not skip the empirical Ri test.** The test is the only mechanism the method provides for falsifying the work. Generate a fresh list of stressors not used during design, apply both architectures, compute Ri. Test stressors that the residual architecture *fails* to survive are the next round of stress analysis -- they are the unstressed surfaces of the system. The test does not say "you are done"; it says "here is where to stress next."

**Common mistakes to avoid**. Do not treat the contagion matrix as a checklist. Do not let cost or probability filter stressors during analysis (they enter later via ATAM and FMEA, not earlier). Do not add components without residue justification. Do not accept NFRs that cannot trace to a specific source. Do not let use cases creep back into the role of decomposition driver -- they are documentation, full stop.

**When not to use this method**. Some projects do not need it. Genuinely simple, genuinely short-lived, or genuinely well-understood domains can be designed by less rigorous methods at lower cost. The method earns its keep when the domain is hyperliminal -- a complicated software system executing inside a complex, non-ergodic context. If your context is genuinely stable and your requirements are genuinely complete, the overhead of stressor analysis is not justified. (You should be skeptical, however, of your confidence that this is the case. Most architects who think their context is stable are wrong.)

---

## 10. What this is and is not

**This is** a working synthesis of two existing methods, validated empirically against the canonical case of one of them, expressed in a template and worked examples that can be used in a real project tomorrow.

**This is not** a silver bullet, and the document would lose credibility if it claimed to be one. It is not a replacement for systems engineering, distributed systems knowledge, domain expertise, or the experience that lets a senior architect look at a contagion matrix and immediately know which patterns matter. It does not solve the problem of bad stakeholder communication, of organizations that punish admission of uncertainty, or of teams that lack the basic skills to refactor a distributed system once the matrix tells them where to refactor.

What it does is surface the inputs of those existing skills earlier and more rigorously, so that the skills get applied to the right problems at the right time. The method does not make average architects into good ones. It makes good architects more consistent, more defensible, and more empirically honest about what they have produced.

---

## 11. Closing -- the empirical stance

If you read O'Reilly's book carefully, the most striking thing is not the philosophy or the complexity-science framing. It is the claim that this method produces architectures that **survive empirical tests of survival** and that this effect is **statistically significant** across projects. That is a remarkable claim for a software architecture method. Most methods are sold on plausibility, intuition, or the prestige of their authors. Residuality is sold on falsifiability.

The synthesis you are receiving inherits that stance. The Ri test is the most important section of the template that does not get skipped. It is the only part of the method that can tell you whether the work was worth doing. Treat it as the deliverable that closes the loop.

If your residual architecture, tested against fresh stressors, does not score better than the naïve baseline, you have learned something valuable: the analysis was not yet deep enough, or the stressors were not yet diverse enough, or the matrix readings were not aggressive enough. That is an honest result. It is also the result that the traditional engineering paradigm makes impossible to obtain, because it provides no test at all.

Welcome to the practice. Be prepared to be wrong before you are right.
