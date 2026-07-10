#!/usr/bin/env python3
"""check_principle.py -- clause-level CHK-01 (P1 / S2).

The landed constitution's **architecture half** must carry the SAD principle
"Service Decomposition by Residue" with its normative CLAUSES intact. The SAD's own
rule (principle-decomposition-by-residue.md): "copy the normative clauses verbatim
(you may renumber the principle and adjust surrounding prose, never the clauses)."

So whole-file byte-identity is the wrong contract (the scaffold renumbers the
principle, wraps it in project framing, appends project-specific examples, and
`/speckit-constitution` prepends a sync-impact report). CHK-01 is a CLAUSE-level
check: every normative clause line of the source principle must survive, verbatim,
in the constitution's principle block -- ignoring numbering, surrounding prose
(blockquote notes), formatting, and trailing project instantiations like
"(here: U-01 ...)". An altered or dropped clause is a hard finding.

    check_principle.py .specify/memory/constitution.md \\
        architecture/arch-X.Y.Z/integration/principle-decomposition-by-residue.md

This is the guard that the Developer touched ONLY the implementation half: the
architecture half's clauses are the handoff's, immutable from the Developer side.

Exit codes:  0 clauses intact / 1 a clause is altered or missing (gate blocked)
             2 usage error / file not found / principle not found
Stdlib-only. Self-test:  check_principle.py --self-test
"""

import argparse
import os
import re
import sys

OK, FINDINGS, ERROR = 0, 1, 2

PRINCIPLE_RE = re.compile(r"service decomposition by residue", re.I)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


def principle_block(text):
    """Lines of the 'Service Decomposition by Residue' principle section (heading text
    matched leniently so a renumbered 'I. ...' heading still resolves), up to the next
    heading of same-or-higher level. None if the principle heading is absent."""
    lines = text.splitlines()
    start = level = None
    for i, ln in enumerate(lines):
        m = HEADING_RE.match(ln)
        if m and PRINCIPLE_RE.search(m.group(2)):
            start, level = i + 1, len(m.group(1))
            break
    if start is None:
        return None
    body = []
    for ln in lines[start:]:
        m = HEADING_RE.match(ln)
        if m and len(m.group(1)) <= level:
            break
        body.append(ln)
    return body


_SEP_RE = re.compile(r"^[-=]{3,}$")
_TABLE_SEP_RE = re.compile(r"^\|?[\s:|-]+\|?$")
_LEAD_RE = re.compile(r"^(?:#{1,6}\s+|[-*+]\s+|\d+\.\s+|[IVXLC]+\.\s+)")
_TRAIL_PAREN_RE = re.compile(r"\s*\([^()]*\)\s*[.;:,]?\s*$")
# What starts a NEW logical unit (blank line also flushes): blockquote, heading,
# bullet, number, roman numeral, table row, or a bold-led directive.
_NEW_UNIT_RE = re.compile(r"^(?:>|#{1,6}\s|[-*+]\s|\d+\.\s|[IVXLC]+\.\s|\||\*\*)")


def reflow(block):
    """Join hard-wrapped continuation lines into logical units (paragraph / bullet /
    table row). Real principle files wrap at ~76 cols, and a project-specific append
    like '(here: U-01 ...)' can re-wrap a bullet -- so comparison must be per-clause,
    not per-physical-line."""
    units, cur = [], ""

    def flush():
        nonlocal cur
        if cur.strip():
            units.append(cur.strip())
        cur = ""

    for ln in block:
        s = ln.strip()
        if not s:
            flush()
            continue
        if _NEW_UNIT_RE.match(s):
            flush()
            cur = s
        else:
            cur = (cur + " " + s) if cur else s
    flush()
    return units


def is_clause(unit):
    """A normative unit -- drop blockquote prose, separators, table-separator rows,
    and headings; keep directives, bullets, and table rows."""
    if unit.startswith(">") or _SEP_RE.match(unit) or _TABLE_SEP_RE.match(unit) or HEADING_RE.match(unit):
        return False
    return True


def normalize(line):
    """Reduce a clause line to its comparable normative core: strip a leading
    list/number/roman marker, table pipes, markdown emphasis/backticks, a trailing
    project instantiation '(...)', and collapse whitespace. Numbering and surrounding
    prose are allowed to differ; the clause words are not."""
    s = _LEAD_RE.sub("", line.strip())
    s = s.replace("|", " ").replace("**", "").replace("*", "").replace("`", "")
    s = _TRAIL_PAREN_RE.sub("", s)
    s = re.sub(r"\s+", " ", s).strip().rstrip(".:;,")
    return s


def check(constitution_text, principle_text):
    """Return (ok, findings). The source principle's clauses must all appear in the
    constitution's principle block (constitution may add prose / renumber)."""
    findings = []
    src_block = principle_block(principle_text)
    con_block = principle_block(constitution_text)
    if src_block is None:
        return False, ["the source principle file has no 'Service Decomposition by Residue' principle"]
    if con_block is None:
        return False, ["the constitution has no 'Service Decomposition by Residue' principle "
                       "(architecture half missing or principle not landed -- CHK-01)"]

    # map normalized -> original source clause (for reporting), skip empties
    src = {}
    for u in reflow(src_block):
        if not is_clause(u):
            continue
        n = normalize(u)
        if n:
            src.setdefault(n, u)
    con = {normalize(u) for u in reflow(con_block) if is_clause(u)}
    con.discard("")

    missing = [orig for n, orig in src.items() if n not in con]
    for orig in missing:
        findings.append("clause altered or missing from the constitution: %r" % orig)
    return not findings, findings


def report(ok, findings, constitution_path):
    print("CHK-01 clause-level principle preservation (P1 / S2)")
    print("  constitution: %s" % constitution_path)
    print()
    if ok:
        print("VERDICT: the architecture-half principle clauses are intact "
              "(numbering / prose may differ; the clauses do not).")
        return
    print("Findings (%d):" % len(findings))
    for f in findings:
        print("  - %s" % f)
    print()
    print("VERDICT: BLOCKED -- the architecture half was altered. Its clauses are the "
          "handoff's and immutable from the Developer side; re-land the release (a new "
          "arch-X.Y.Z), do not edit the clauses locally. (The Developer edits ONLY the "
          "implementation half.)")


# --- self-test -----------------------------------------------------------------
# Hard-wrapped like the real principle file (~76 cols).
_SRC = """> **Emitted by:** speckit-handoff. Land in the canonical constitution.

## Principle: Service Decomposition by Residue

**Decomposition driver.** Services MUST encapsulate residues -- the components
that survive coherent under stressor contagion -- not units of functionality.

- Service names MUST NOT describe a function or a domain verb.
- Service names MUST denote what is encapsulated, suffixed by their IDesign
  category.

**Layer discipline (closed architecture).**

- Managers MUST NOT call other Managers synchronously; cross-Manager
  communication goes through a queue or pub-sub topic.
- Engines MUST NOT call Managers and MUST be stateless.

**Residue lineage (traceability).**

- A plan that knowingly builds on an unstressed surface from the SAD's empirical
  test MUST flag it.

**Binding ADRs.** A runtime, protocol, or middleware decision captured in an ADR
is a binding architecture constraint.
"""

# scaffold form: renumbered heading, hard-wrapped, an appended "(here: U-01 ...)"
# project instantiation that RE-WRAPS the bullet, an added agnostic blockquote note,
# and project framing -- the clauses themselves are unchanged.
_CONST_OK = """# EV Charging Network -- Project Constitution

# Architecture half

## I. Service Decomposition by Residue

**Decomposition driver.** Services MUST encapsulate residues -- the components
that survive coherent under stressor contagion -- not units of functionality.

- Service names MUST NOT describe a function or a domain verb.
- Service names MUST denote what is encapsulated, suffixed by their IDesign
  category.

**Layer discipline (closed architecture).**

- Managers MUST NOT call other Managers synchronously; cross-Manager
  communication goes through a queue or pub-sub topic.
- Engines MUST NOT call Managers and MUST be stateless.

**Residue lineage (traceability).**

- A plan that knowingly builds on an unstressed surface from the SAD's empirical
  test MUST flag it (here: U-01 dynamic energy economics, a documented
  unstressed surface).

> (The principle stays agnostic -- no concrete technology in its clauses, CHK-05.)

**Binding ADRs.** A runtime, protocol, or middleware decision captured in an ADR
is a binding architecture constraint.

# Implementation half

## [TODO] Testing strategy
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

    ok, f = check(_CONST_OK, _SRC)
    expect("verbatim-clauses constitution passes (renumber + prose + (here:...) tolerated)", ok and not f)

    # SEEDED VIOLATION: a clause is weakened (MUST NOT -> MAY)
    altered = _CONST_OK.replace(
        "- Engines MUST NOT call Managers and MUST be stateless.",
        "- Engines MAY call Managers.")
    ok, f = check(altered, _SRC)
    expect("altered clause (MUST NOT -> MAY) is caught",
           not ok and any("Engines MUST NOT call Managers" in x for x in f))

    # SEEDED VIOLATION: a clause is dropped
    dropped = _CONST_OK.replace(
        "- Engines MUST NOT call Managers and MUST be stateless.\n", "")
    ok, f = check(dropped, _SRC)
    expect("dropped clause is caught", not ok and any("Engines MUST NOT call Managers" in x for x in f))

    # SEEDED VIOLATION: the principle is not landed at all
    ok, f = check("# Constitution\n## [TODO] Testing\n", _SRC)
    expect("missing principle is caught", not ok and any("no 'Service Decomposition" in x for x in f))

    # a reordered + reformatted constitution still passes (renumber/format tolerated)
    reordered = _CONST_OK.replace("## I. Service Decomposition by Residue",
                                  "### 1. Service Decomposition by Residue")
    ok, f = check(reordered, _SRC)
    expect("reformatted heading still passes", ok and not f)

    # exit-code contract
    expect("exit-code: intact -> 0", (FINDINGS if check(_CONST_OK, _SRC)[1] else OK) == OK)
    expect("exit-code: altered -> 1", (FINDINGS if check(altered, _SRC)[1] else OK) == FINDINGS)

    print("\nself-test: %d passed, %d failed" % (passed, failed))
    return OK if failed == 0 else FINDINGS


def _read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_principle.py",
        description="Clause-level CHK-01: the constitution's architecture-half principle clauses match the landed principle.")
    parser.add_argument("constitution", nargs="?", help=".specify/memory/constitution.md")
    parser.add_argument("principle", nargs="?",
                        help="architecture/arch-X.Y.Z/integration/principle-decomposition-by-residue.md")
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixtures and exit")
    ns = parser.parse_args(argv)

    if ns.self_test:
        return self_test()
    if not ns.constitution or not ns.principle:
        parser.error("expected <constitution.md> <principle-source.md> (or --self-test)")
    for p in (ns.constitution, ns.principle):
        if not os.path.isfile(p):
            print("error: file not found: %s" % p, file=sys.stderr)
            return ERROR

    ok, findings = check(_read(ns.constitution), _read(ns.principle))
    report(ok, findings, ns.constitution)
    return OK if ok else FINDINGS


if __name__ == "__main__":
    sys.exit(main())
