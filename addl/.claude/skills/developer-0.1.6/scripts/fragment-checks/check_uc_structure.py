#!/usr/bin/env python3
"""check_uc_structure.py -- D1 handoff-form validation for use cases (CHK-10).

The Architect <-> Developer integration depends on every landed use case being
well-formed: its "Architectural Context" block (preserved verbatim into spec.md,
then carried into /speckit-plan) must have the three subsections the contract
mandates, and every service it names must exist in the catalog. If a future
release ships a malformed UC, the downstream verbatim-copy + scope checks have
nothing sound to anchor on and the gap is silent. This check makes D1 reject a
malformed handoff up front.

Per use-case-contract.md, the `## 4. Architectural Context` block has EXACTLY:
  - Call Chain     -- a graph (mermaid or arrow notation)
  - Services touched -- a table; every service MUST exist in service-catalog.md
  - Residue        -- per touched service, the S-NN it absorbs

    check_uc_structure.py architecture/arch-X.Y.Z/

Layer-rule conformance of the Call Chain (CHK-09) is the deterministic job of Q3
in check_constitution.py at D3 (on the verbatim copy); this check verifies FORM.

Exit codes:  0 every UC well-formed / 1 a UC is malformed (gate blocked)
             2 usage error / no use-cases dir / no catalog
Stdlib-only. Self-test:  check_uc_structure.py --self-test
"""

import argparse
import os
import re
import sys

OK, FINDINGS, ERROR = 0, 1, 2

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
SECTION_NUM_RE = re.compile(r"^\d+(?:\.\d+)*\.?\s+")
SERVICE_RE = re.compile(r"\b[A-Z][A-Za-z0-9]*(?:Manager|Engine|Access)\b")
S_RE = re.compile(r"\bS-\d{2,}\b")
ARROW_RE = re.compile(r"-+\.?-*>")
REQUIRED_SUBSECTIONS = ["call chain", "services touched", "residue"]


class FormatError(Exception):
    """A required binding input is missing."""


def _htitle(h):
    return SECTION_NUM_RE.sub("", h.strip()).lower()


def section_body(text, title):
    """Body under the first heading whose number-stripped title == title (lower),
    up to the next heading of same-or-higher level. None if absent."""
    lines = text.splitlines()
    start = level = None
    for i, ln in enumerate(lines):
        m = HEADING_RE.match(ln)
        if m and _htitle(m.group(2)) == title:
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
    return "\n".join(body)


def load_catalog_services(arch_dir):
    p = os.path.join(arch_dir, "system-design", "service-catalog.md")
    if not os.path.isfile(p):
        raise FormatError("required binding input not found: %s" % p)
    with open(p, encoding="utf-8") as fh:
        return set(SERVICE_RE.findall(fh.read()))


def _table_services(text):
    """[(service, full_row)] from the FIRST column of each markdown table data row.
    Reading only the first column avoids matching the category word 'ResourceAccess'
    that sits in the second column of a Services-touched / Residue table."""
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells:
            continue
        first = cells[0].replace("`", "").replace("*", "").strip()
        if first.lower() == "service" or set(first) <= set("-: "):
            continue
        m = SERVICE_RE.search(first)
        if m:
            out.append((m.group(0), s))
    return out


def check_uc(text, fname, catalog):
    """Findings for one use-case file (empty list = well-formed)."""
    findings = []
    ac = section_body(text, "architectural context")
    if ac is None:
        return ["%s: no 'Architectural Context' section (use-case-contract S2)" % fname]

    subs = {s: section_body(ac, s) for s in REQUIRED_SUBSECTIONS}
    for s in REQUIRED_SUBSECTIONS:
        if subs[s] is None:
            findings.append("%s: Architectural Context missing the '%s' subsection" % (fname, s.title()))
        elif not subs[s].strip():
            findings.append("%s: the '%s' subsection is empty" % (fname, s.title()))

    cc = subs.get("call chain") or ""
    if cc.strip() and not ARROW_RE.search(cc):
        findings.append("%s: Call Chain has no edges (need at least one 'A -> B' / mermaid '-->'); "
                        "a node-only graph cannot be layer-checked" % fname)

    st = subs.get("services touched") or ""
    touched = {svc for svc, _ in _table_services(st)}
    if st.strip():
        if not touched:
            findings.append("%s: Services touched lists no *Manager/*Engine/*Access service" % fname)
        for svc in sorted(touched - catalog):
            findings.append("%s: service '%s' in Services touched is NOT in the service catalog (CHK-10)" % (fname, svc))

    rs = subs.get("residue") or ""
    if rs.strip():
        if not S_RE.search(rs):
            findings.append("%s: Residue cites no structural stressor S-NN" % fname)
        # per-service lineage: every touched service needs a Residue row carrying an S-NN,
        # and no Residue service may be absent from Services touched (use-case-contract S2/S3).
        residue_all, residue_with_snn = set(), set()
        for svc, row in _table_services(rs):
            residue_all.add(svc)
            if S_RE.search(row):
                residue_with_snn.add(svc)
        for svc in sorted(touched - residue_with_snn):
            findings.append("%s: service '%s' (Services touched) has no Residue S-NN lineage "
                            "(use-case-contract S2: Residue per touched service)" % (fname, svc))
        for svc in sorted(residue_all - touched):
            findings.append("%s: service '%s' appears in Residue but not in Services touched" % (fname, svc))

    return findings


def run(arch_dir):
    catalog = load_catalog_services(arch_dir)
    uc_dir = os.path.join(arch_dir, "use-cases")
    if not os.path.isdir(uc_dir):
        raise FormatError("no use-cases/ directory in %s" % arch_dir)
    ucs = sorted(f for f in os.listdir(uc_dir) if re.match(r"(?i)uc-\d", f) and f.endswith(".md"))
    if not ucs:
        raise FormatError("no uc-NNN-*.md files in %s" % uc_dir)
    findings = []
    for f in ucs:
        with open(os.path.join(uc_dir, f), encoding="utf-8") as fh:
            findings.extend(check_uc(fh.read(), f, catalog))
    return findings, len(ucs)


def report(findings, n_ucs, arch_dir):
    print("Use-case handoff-form validation (CHK-10) -- D1")
    print("  release:   %s" % arch_dir)
    print("  use cases: %d" % n_ucs)
    print()
    if not findings:
        print("VERDICT: every use case is well-formed (Architectural Context with Call Chain / "
              "Services touched / Residue; all touched services in the catalog).")
        return
    print("Findings (%d):" % len(findings))
    for f in findings:
        print("  - %s" % f)
    print()
    print("VERDICT: BLOCKED -- a landed use case is malformed. The handoff is not ready to "
          "implement against; re-land a conformant release (a UC defect is the Architect's, "
          "raised back to the SAD).")


# --- self-test -----------------------------------------------------------------
_CATALOG = (
    "# catalog\n| Service | Category | Stressors-absorbed |\n|---|---|---|\n"
    "| ChargeSessionManager | Manager | S-03 |\n"
    "| AuthEngine | Engine | S-15 |\n"
    "| ChargerAccess | Access | S-01 |\n"
)
_UC_OK = """# UC-001 -- Charge session

## 4. Architectural Context

### Call Chain

```mermaid
graph LR
    Charger --> CSM
    CSM --> AuthE
```

### Services touched

| Service | Category | Role |
|---|---|---|
| `ChargeSessionManager` | Manager | orchestrates |
| `AuthEngine` | Engine | identity |
| `ChargerAccess` | Access | hardware |

### Residue

| Service | Absorbs |
|---|---|
| `ChargeSessionManager` | S-03 |
| `AuthEngine` | S-15 |
| `ChargerAccess` | S-01 |

## 5. Main Flows
...
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

    catalog = set(SERVICE_RE.findall(_CATALOG))

    expect("well-formed UC passes (every touched service has Residue lineage)", not check_uc(_UC_OK, "uc-001.md", catalog))

    # SEEDED: missing the whole Residue subsection
    no_res = _UC_OK[:_UC_OK.index("### Residue")] + "## 5. Main Flows\n...\n"
    f = check_uc(no_res, "uc-001.md", catalog)
    expect("missing Residue subsection is caught", any("Residue" in x and "missing" in x for x in f))

    # SEEDED: a Services-touched service not in the catalog
    bad_svc = _UC_OK.replace("| `AuthEngine` | Engine | identity |", "| `BillingManager` | Manager | bills |")
    f = check_uc(bad_svc, "uc-001.md", catalog)
    expect("service not in catalog is caught (CHK-10)", any("BillingManager" in x and "NOT in the service catalog" in x for x in f))

    # SEEDED: Call Chain present but trivial (a single node, no edges) -- the FN the
    # workflow confirmed escaped before this fix.
    trivial_cc = _UC_OK.replace("    Charger --> CSM\n    CSM --> AuthE\n", "    CSM[ChargeSessionManager]\n")
    f = check_uc(trivial_cc, "uc-001.md", catalog)
    expect("trivial node-only Call Chain (no edges) is caught", any("Call Chain has no edges" in x for x in f))

    # SEEDED: no Architectural Context at all
    f = check_uc("# UC-009 -- stub\n## 1. Business Context\n...\n", "uc-009.md", catalog)
    expect("missing Architectural Context is caught", any("no 'Architectural Context'" in x for x in f))

    # SEEDED: a touched service has no Residue lineage (Residue covers only 2 of 3)
    no_lineage = _UC_OK.replace("| `AuthEngine` | S-15 |\n", "")
    f = check_uc(no_lineage, "uc-001.md", catalog)
    expect("touched service without Residue lineage is caught",
           any("AuthEngine" in x and "no Residue S-NN lineage" in x for x in f))

    # SEEDED: a Residue row names a service absent from Services touched (orphan)
    orphan = _UC_OK.replace("| `ChargerAccess` | S-01 |", "| `ChargerAccess` | S-01 |\n| `CustomerAccess` | S-13 |")
    f = check_uc(orphan, "uc-001.md", catalog)
    expect("orphan service in Residue (not in Services touched) is caught",
           any("CustomerAccess" in x and "not in Services touched" in x for x in f))

    print("\nself-test: %d passed, %d failed" % (passed, failed))
    return OK if failed == 0 else FINDINGS


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_uc_structure.py",
        description="D1: validate every landed use case is well-formed (CHK-10).")
    parser.add_argument("arch_dir", nargs="?", help="the landed release dir architecture/arch-X.Y.Z/")
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixtures and exit")
    ns = parser.parse_args(argv)

    if ns.self_test:
        return self_test()
    if not ns.arch_dir:
        parser.error("expected <arch-dir> (or --self-test)")
    if not os.path.isdir(ns.arch_dir):
        print("error: release dir not found: %s" % ns.arch_dir, file=sys.stderr)
        return ERROR
    try:
        findings, n = run(ns.arch_dir)
    except FormatError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return ERROR
    report(findings, n, ns.arch_dir)
    return FINDINGS if findings else OK


if __name__ == "__main__":
    sys.exit(main())
