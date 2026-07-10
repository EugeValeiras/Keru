#!/usr/bin/env python3
"""check_arch_context.py -- verbatim Architectural Context preservation (D-01 / D2).

When D2 seeds a feature spec from a use case, the spec MUST carry the use case's
three-section Architectural Context -- Call Chain / Services touched / Residue --
**verbatim** under an "Architectural Context" heading. That block is the lateral
"why" (R-22) the SAD earned through the stress-driven walk; if D2 paraphrases,
trims, or silently edits it, the architecture's reasoning stops surviving into
implementation. This check diffs the spec's block against the source UC's block
and hard-fails on any drift (see ../../shared/glossary.md, "Architectural Context").

    check_arch_context.py specs/NNN-<slug>/spec.md \\
        architecture/arch-X.Y.Z/use-cases/uc-NNN-<slug>.md

It (1) locates the "Architectural Context" section in each file (a heading whose
text is exactly "Architectural Context", at any level, up to the next heading of
the same or higher level), (2) confirms the source UC block carries the three
required subsections, and (3) compares the two blocks. Comparison trims only the
block's outer blank lines and each line's trailing whitespace -- everything else
must match, so a reflow, a dropped sentence, or a re-ordered subsection is caught.

Exit codes:  0 preserved verbatim / 1 missing block, missing subsection, or drift
             2 usage error / file not found

Stdlib-only. Self-test:  check_arch_context.py --self-test
"""

import argparse
import difflib
import os
import re
import sys

OK, FINDINGS, ERROR = 0, 1, 2

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
# Strip a leading section-number prefix ("4. ", "4.2 ", "4.2.1. ") so a numbered
# UC heading like "## 4. Architectural Context" matches an unnumbered spec heading
# like "## Architectural Context". The RDAG use-case contract numbers its sections;
# spec-kit's spec has no such section, so the injected spec-side heading is unnumbered.
SECTION_NUM_RE = re.compile(r"^\d+(?:\.\d+)*\.?\s+")
CONTEXT_TITLE = "architectural context"
REQUIRED_SUBSECTIONS = ["Call Chain", "Services touched", "Residue"]


def extract_block(text):
    """Return the body under the 'Architectural Context' heading (up to the next
    heading of same-or-higher level), or None if the heading is absent."""
    lines = text.splitlines()
    start = None
    level = None
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if not m:
            continue
        title = SECTION_NUM_RE.sub("", m.group(2).strip()).lower()
        if title == CONTEXT_TITLE:
            start = i + 1
            level = len(m.group(1))
            break
    if start is None:
        return None
    body = []
    for line in lines[start:]:
        m = HEADING_RE.match(line)
        if m and len(m.group(1)) <= level:
            break
        body.append(line)
    return body


def normalize(body):
    """Trim each line's trailing whitespace and the block's outer blank lines.
    Internal structure and content are preserved so real drift still shows."""
    trimmed = [ln.rstrip() for ln in body]
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    return trimmed


def missing_subsections(body):
    blob = "\n".join(body).lower()
    return [s for s in REQUIRED_SUBSECTIONS if s.lower() not in blob]


def check(spec_text, uc_text):
    """Return (ok, findings, diff_lines)."""
    findings = []
    uc_block = extract_block(uc_text)
    spec_block = extract_block(spec_text)

    if uc_block is None:
        findings.append("the source use case has no 'Architectural Context' heading")
    if spec_block is None:
        findings.append("the spec has no 'Architectural Context' heading (D2 must carry it verbatim)")
    if uc_block is None or spec_block is None:
        return False, findings, []

    miss = missing_subsections(uc_block)
    if miss:
        findings.append("the source UC block is missing required subsection(s): %s" % ", ".join(miss))

    uc_norm = normalize(uc_block)
    spec_norm = normalize(spec_block)
    diff = []
    if uc_norm != spec_norm:
        findings.append("the spec's Architectural Context does not match the source UC verbatim")
        diff = list(difflib.unified_diff(uc_norm, spec_norm,
                                         fromfile="uc (source of truth)", tofile="spec",
                                         lineterm=""))
    return not findings, findings, diff


def report(ok, findings, diff, spec_path, uc_path, as_json=False):
    if as_json:
        import json
        print(json.dumps({"spec": spec_path, "uc": uc_path, "passed": ok,
                          "findings": findings, "diff": diff}, indent=2))
        return
    print("Architectural Context preservation (D-01 / D2)")
    print("  spec: %s" % spec_path)
    print("  uc:   %s" % uc_path)
    print()
    if ok:
        print("VERDICT: the spec preserves the use case's Architectural Context verbatim.")
        return
    print("Findings:")
    for f in findings:
        print("  - %s" % f)
    if diff:
        print()
        print("Diff (uc = source of truth -> spec):")
        for line in diff:
            print("  %s" % line)
    print()
    print("VERDICT: BLOCKED -- D2 must carry the UC's Architectural Context byte-for-byte. "
          "Restore the verbatim block; do not paraphrase or trim it (R-22).")


# --- self-test -----------------------------------------------------------------
_UC = """# UC-001 Order capture

## Architectural Context

### Call Chain
Client -> OrderManager -> PricingEngine -> LedgerAccess

### Services touched
OrderManager, PricingEngine, LedgerAccess

### Residue
S-01 (burst), S-03 (partial failure); coupling C-01; surface U-01

## Acceptance
Out of scope for the context block.
"""

_SPEC_OK = """# Feature spec: 001-order-capture

## Overview
Some spec-kit preamble.

## Architectural Context

### Call Chain
Client -> OrderManager -> PricingEngine -> LedgerAccess

### Services touched
OrderManager, PricingEngine, LedgerAccess

### Residue
S-01 (burst), S-03 (partial failure); coupling C-01; surface U-01

## Requirements
FR-1 ...
"""

# paraphrased Residue line (drift)
_SPEC_DRIFT = _SPEC_OK.replace(
    "S-01 (burst), S-03 (partial failure); coupling C-01; surface U-01",
    "S-01 and S-03; coupling C-01")
# missing the whole block
_SPEC_NOBLOCK = "# Feature spec\n\n## Overview\nNo context block here.\n"


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

    ok, findings, diff = check(_SPEC_OK, _UC)
    expect("verbatim spec passes", ok and not findings)

    ok, findings, diff = check(_SPEC_DRIFT, _UC)
    expect("paraphrased block is caught", not ok and any("verbatim" in f for f in findings))
    expect("drift produces a diff", bool(diff))

    ok, findings, diff = check(_SPEC_NOBLOCK, _UC)
    expect("missing spec block is caught", not ok and any("spec has no" in f for f in findings))

    # trailing-whitespace-only difference (each line rstripped) still passes
    spec_ws = _SPEC_OK.replace("surface U-01", "surface U-01   ")
    ok, findings, diff = check(spec_ws, _UC)
    expect("trailing-whitespace-only difference still passes", ok)

    # numbered UC heading ("## 4. Architectural Context", per the RDAG use-case
    # contract) matches an unnumbered spec heading -- the real-artifact bug.
    uc_numbered = _UC.replace("## Architectural Context", "## 4. Architectural Context")
    ok, findings, diff = check(_SPEC_OK, uc_numbered)
    expect("numbered UC heading still matches the spec block", ok and not findings)

    # a UC missing a required subsection is flagged
    uc_missing = _UC.replace("### Residue\nS-01 (burst), S-03 (partial failure); coupling C-01; surface U-01\n", "")
    ok, findings, diff = check(_SPEC_OK, uc_missing)
    expect("UC missing a required subsection is flagged",
           not ok and any("subsection" in f for f in findings))

    # exit-code contract
    expect("exit-code contract (0 verbatim / 1 drift)",
           (OK if check(_SPEC_OK, _UC)[0] else FINDINGS) == OK
           and (FINDINGS if not check(_SPEC_DRIFT, _UC)[0] else OK) == FINDINGS)

    print("\nself-test: %d passed, %d failed" % (passed, failed))
    return OK if failed == 0 else FINDINGS


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_arch_context.py",
        description="Verify the spec preserves the use case's Architectural Context verbatim (D-01/D2).")
    parser.add_argument("spec", nargs="?", help="the feature spec.md")
    parser.add_argument("uc", nargs="?", help="the source use-cases/uc-NNN-*.md")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixtures and exit")
    ns = parser.parse_args(argv)

    if ns.self_test:
        return self_test()

    if not ns.spec or not ns.uc:
        parser.error("expected <spec.md> <uc-file.md> (or --self-test)")
    for p in (ns.spec, ns.uc):
        if not os.path.isfile(p):
            print("error: file not found: %s" % p, file=sys.stderr)
            return ERROR

    with open(ns.spec, encoding="utf-8") as fh:
        spec_text = fh.read()
    with open(ns.uc, encoding="utf-8") as fh:
        uc_text = fh.read()

    ok, findings, diff = check(spec_text, uc_text)
    report(ok, findings, diff, ns.spec, ns.uc, as_json=ns.json)
    return OK if ok else FINDINGS


if __name__ == "__main__":
    sys.exit(main())
