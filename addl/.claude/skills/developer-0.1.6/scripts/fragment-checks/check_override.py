#!/usr/bin/env python3
"""check_override.py -- build and verify the Q1-Q6 plan-template override (P4 / S3).

The SAD hands off `plan-template-constitution-check.md`: a PARTIAL two-tier block
(Tier 1 = Q1-Q6 NON-WAIVABLE, Tier 2 = Complexity Tracking) meant to REPLACE the
Constitution Check + Complexity Tracking sections of spec-kit's plan template --
"keep the rest of the template (Summary, Technical Context, Project Structure, ...)
untouched".

But spec-kit's `resolve_template` REPLACES the core template with the override
wholesale (confirmed by execution): installing the partial block AS the override
strips Technical Context / Project Structure and can leave the gate with no Q-rows,
so the whole Constitution Check passes vacuously -- the governance hub silently
nullifies itself. So D1 must SPLICE, not copy:

    # produce the merged override by splicing the landed block into a COPY of the
    # consumer's CURRENT core plan-template (version-robust: read the real core):
    check_override.py --build .specify/templates/plan-template.md \\
        architecture/arch-X.Y.Z/integration/plan-template-constitution-check.md \\
        > .specify/templates/overrides/plan-template.md

    # verify the merged override is well-formed before D1 approves and before D3:
    check_override.py --verify .specify/templates/overrides/plan-template.md \\
        .specify/templates/plan-template.md .specify/memory/constitution.md

Verify checks: (a) every stock section of the core template (except the two it
replaces) survives in the override; (b) the Constitution Check section carries all
of Q1-Q6; (c) Tier 1 is marked NON-WAIVABLE and excluded from Complexity Tracking;
(d) the constitution declares the same six Constitution Check questions (agreement).

Exit codes:  0 ok / 1 findings (gate blocked) / 2 usage error
Stdlib-only. Self-test:  check_override.py --self-test
"""

import argparse
import os
import re
import sys

OK, FINDINGS, ERROR = 0, 1, 2

H2_RE = re.compile(r"^##\s+(.*?)\s*$")
ANY_H_RE = re.compile(r"^(#{1,6})\s+\S")
DROP_IN = "Drop-in instructions"


def split_h2(text):
    """Return (preamble_lines, [(heading, body_lines)]) split at H2 (## ) headings.
    H1 and any text before the first H2 go to the preamble; H3+ stay in the body."""
    pre, secs, cur = [], [], None
    for ln in text.splitlines():
        m = H2_RE.match(ln)
        if m:
            if cur is not None:
                secs.append(cur)
            cur = [m.group(1), []]
        elif cur is None:
            pre.append(ln)
        else:
            cur[1].append(ln)
    if cur is not None:
        secs.append(cur)
    return pre, secs


def _norm(h):
    return h.strip().lower()


def _demote(text):
    """Add one '#' to every ATX heading (## -> ###), so the landed block nests as a
    subsection of the merged '## Constitution Check'."""
    out = []
    for ln in text.splitlines():
        out.append("#" + ln if ANY_H_RE.match(ln) else ln)
    return "\n".join(out)


def normalize_landed(landed):
    """Strip the landed block's HTML-comment header and its Drop-in-instructions
    footer, demote its headings by one level, and drop its own top heading -- leaving
    the body (intro + Tier 1 + Tier 2) to sit under the merged '## Constitution Check'."""
    t = re.sub(r"^\s*<!--.*?-->\s*", "", landed, count=1, flags=re.DOTALL)
    idx = t.find(DROP_IN)
    if idx != -1:
        head = t[:idx]
        cut = head.rfind("\n---")
        t = t[:cut] if cut != -1 else head[:head.rfind("\n")] if "\n" in head else ""
    t = _demote(t)
    lines = t.splitlines()
    for i, ln in enumerate(lines):
        if ANY_H_RE.match(ln):
            del lines[i]
            break
    return "\n".join(lines).strip("\n")


def build_override(core, landed):
    """Splice the landed two-tier block into a copy of the core plan-template:
    replace the 'Constitution Check' section with the block, drop the standalone
    'Complexity Tracking' section (Tier 2 now covers it), keep the rest in order."""
    pre, secs = split_h2(core)
    landed_body = normalize_landed(landed)
    out = []
    for h, body in secs:
        hn = _norm(h)
        if hn == "constitution check":
            out.append(("Constitution Check", landed_body.splitlines()))
        elif hn == "complexity tracking":
            continue
        else:
            out.append((h, body))
    parts = []
    pre_txt = "\n".join(pre).strip("\n")
    if pre_txt:
        parts.append(pre_txt)
    for h, body in out:
        parts.append(("## " + h + "\n" + "\n".join(body)).rstrip("\n"))
    return "\n\n".join(parts) + "\n"


def _questions(text):
    """The set of Constitution-Check question numbers declared in text, accepting both
    the override's `Q1`.. table form and the constitution's `1.`.. numbered-list form."""
    qs = set(re.findall(r"\bQ([1-6])\b", text))
    if len(qs) < 6:
        qs |= set(re.findall(r"(?m)^\s*\|?\s*([1-6])\.\s", text))
    return qs


def verify_override(override, core, constitution):
    findings = []
    _, core_secs = split_h2(core)
    _, ov_secs = split_h2(override)
    ov_headings = {_norm(h) for h, _ in ov_secs}

    # (a) stock sections preserved (the C2 hole: a partial override strips these)
    for h, _ in core_secs:
        if _norm(h) in ("constitution check", "complexity tracking"):
            continue
        if _norm(h) not in ov_headings:
            findings.append("stock section missing from the override: '%s' "
                            "(a partial override was installed wholesale -- splice, don't copy)" % h)

    cc = None
    for h, body in ov_secs:
        if _norm(h) == "constitution check":
            cc = "\n".join(body)
            break
    if cc is None:
        findings.append("the override has no '## Constitution Check' section")
        cc = ""

    # (b) all six questions present (a partial drop leaves the gate vacuous)
    missing = [q for q in "123456" if q not in _questions(cc)]
    if missing:
        findings.append("Constitution Check is missing question(s): " + ", ".join("Q" + q for q in missing))

    # (c) Tier 1 NON-WAIVABLE + EXCLUDED from Complexity Tracking (the whole point of
    # the override vs spec-kit's stock waivable Complexity Tracking). Match the
    # operative exclusion phrase, not the bare words "complexity tracking" (which also
    # appear in Tier 2's "Complexity Tracking applies").
    cc_l = cc.lower()
    if "non-waivable" not in cc_l:
        findings.append("Constitution Check does not mark Tier 1 NON-WAIVABLE")
    if "excluded from complexity tracking" not in cc_l and "not eligible for complexity tracking" not in cc_l:
        findings.append("Constitution Check does not exclude Tier 1 from Complexity Tracking "
                        "(Q1-Q6 must be non-waivable -- the whole reason for the override)")

    # (d) the constitution declares the same six questions (agreement)
    if len(_questions(constitution)) < 6:
        findings.append("the constitution does not declare all six Constitution Check "
                        "questions -- override and constitution disagree (the gate spec-kit "
                        "reasons from must match the override section)")
    return findings


def report(findings, override_path):
    print("Override well-formedness (P4 / S3)")
    print("  override: %s" % override_path)
    print()
    if not findings:
        print("VERDICT: the spliced override is well-formed (stock sections preserved, "
              "Q1-Q6 present, Tier 1 non-waivable, agrees with the constitution).")
        return
    print("Findings:")
    for f in findings:
        print("  - %s" % f)
    print()
    print("VERDICT: BLOCKED -- do NOT install this override; the Constitution Check gate "
          "would be malformed or vacuous. Build it with --build (splice into a copy of the "
          "current core plan-template).")


# --- self-test -----------------------------------------------------------------
_CORE = """# Implementation Plan: [FEATURE]

## Summary
[summary]

## Technical Context
**Language/Version**: [e.g. Python 3.11]

## Constitution Check
*GATE: Must pass before Phase 0.*
[Gates determined based on constitution file]

## Project Structure
src/

## Complexity Tracking
| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
"""

_LANDED = """<!--
Emitted by speckit-handoff. Apply to .specify/templates/plan-template.md, replacing
the stock Constitution Check section.
-->

# Constitution Check (two tiers)

Run at the start of every /speckit-plan. Tier 1 is non-waivable.

## Tier 1 -- Architecture half (NON-WAIVABLE)

A single No is a hard stop. These questions are EXCLUDED from Complexity Tracking.

| # | Question | Resolves against |
|---|---|---|
| Q1 | Is every service in plan.md present in the service catalog? | service-catalog.md |
| Q2 | Does each service name follow the category suffix? | naming |
| Q3 | Does the call chain respect the layer rules? | use-case Architectural Context |
| Q4 | Does each service list a Structural S-NN? | service-catalog.md |
| Q5 | Does each NFR record a coupling C-NN? | nfr-register.md |
| Q6 | Does the runtime/protocol/middleware conform to all binding ADRs? | decisions/ADR-*.md |

## Tier 2 -- Implementation half (waivable, Complexity Tracking applies)

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|

---

**Drop-in instructions.** Replace the existing Constitution Check + Complexity
Tracking sections with this two-tier block. Keep the rest untouched.
"""

_CONST = """# Project Constitution

## Principle: Service Decomposition by Residue
...clauses...

**Constitution Check questions (gate at /speckit-plan).** The gate MUST answer:

1. Is every service in plan.md present in the service catalog?
2. Does each service name follow the category suffix?
3. Does the call chain respect the layer rules?
4. Does each service list a Structural S-NN?
5. Does each NFR record a coupling C-NN?
6. Does the plan's runtime/protocol/middleware conform to all binding ADRs?
"""


def self_test():
    passed = failed = 0

    def expect(label, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print("  ok    %s" % label)
        else:
            failed += 1
            print("  FAIL  %s" % label)

    merged = build_override(_CORE, _LANDED)

    # the splice keeps the stock sections and drops the standalone Complexity Tracking
    expect("splice keeps Summary", "## Summary" in merged)
    expect("splice keeps Technical Context", "## Technical Context" in merged)
    expect("splice keeps Project Structure", "## Project Structure" in merged)
    expect("splice has a single Constitution Check section", merged.count("## Constitution Check") == 1)
    expect("splice dropped the standalone Complexity Tracking section",
           "## Complexity Tracking" not in merged)
    expect("splice carries Q1-Q6", all(("Q%d" % i) in merged for i in range(1, 7)))

    # a well-formed merged override passes verify
    expect("merged override verifies clean", not verify_override(merged, _CORE, _CONST))

    # SEEDED VIOLATION (the C2 root cause): install the partial block WHOLE as the override
    f_partial = verify_override(_LANDED, _CORE, _CONST)
    expect("installing the partial block whole is caught (stock sections stripped)",
           any("stock section missing" in f for f in f_partial))

    # seeded: a merged override with Q6 dropped -> vacuous gate caught
    merged_no_q6 = merged.replace("| Q6 | Does the runtime/protocol/middleware conform to all binding ADRs? | decisions/ADR-*.md |", "")
    expect("dropped Q6 is caught", any("Q6" in f for f in verify_override(merged_no_q6, _CORE, _CONST)))

    # seeded: Tier 1 is no longer EXCLUDED from Complexity Tracking (the override would
    # then be no better than spec-kit's stock waivable gate)
    merged_waivable = merged.replace("EXCLUDED from Complexity Tracking", "subject to Complexity Tracking")
    expect("loss of the Complexity-Tracking exclusion is caught",
           any("exclude" in f.lower() for f in verify_override(merged_waivable, _CORE, _CONST)))

    # seeded: constitution disagrees (only 5 questions)
    const_5 = _CONST.replace("6. Does the plan's runtime/protocol/middleware conform to all binding ADRs?", "")
    expect("constitution/override disagreement is caught", any("disagree" in f or "six" in f for f in verify_override(merged, _CORE, const_5)))

    # exit-code contract
    expect("exit-code: clean -> 0", (FINDINGS if verify_override(merged, _CORE, _CONST) else OK) == OK)
    expect("exit-code: partial -> 1", (FINDINGS if verify_override(_LANDED, _CORE, _CONST) else OK) == FINDINGS)

    print("\nself-test: %d passed, %d failed" % (passed, failed))
    return OK if failed == 0 else FINDINGS


def _read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_override.py",
        description="Build (splice) and verify the Q1-Q6 plan-template override.")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--build", nargs=2, metavar=("CORE", "LANDED"),
                   help="splice LANDED into a copy of CORE; print the merged override to stdout")
    g.add_argument("--verify", nargs=3, metavar=("OVERRIDE", "CORE", "CONSTITUTION"),
                   help="verify a merged OVERRIDE is well-formed")
    g.add_argument("--self-test", action="store_true", help="run the built-in fixtures and exit")
    ns = parser.parse_args(argv)

    if ns.self_test:
        return self_test()

    if ns.build:
        core, landed = ns.build
        for p in (core, landed):
            if not os.path.isfile(p):
                print("error: file not found: %s" % p, file=sys.stderr)
                return ERROR
        sys.stdout.write(build_override(_read(core), _read(landed)))
        return OK

    override, core, constitution = ns.verify
    for p in (override, core, constitution):
        if not os.path.isfile(p):
            print("error: file not found: %s" % p, file=sys.stderr)
            return ERROR
    findings = verify_override(_read(override), _read(core), _read(constitution))
    report(findings, override)
    return FINDINGS if findings else OK


if __name__ == "__main__":
    sys.exit(main())
