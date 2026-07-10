#!/usr/bin/env python3
"""check_adr_applied.py -- an ACCEPTED ADR's decision must be reflected before S7.

For each docs/adr/ADR-*.md whose Status is ACCEPTED and whose `## Impact assessment`
Outcome is `iterating Sn` / `reopen Sn` (not `no-op`), the affected gate's fragment
MUST cite the ADR id. Exit 1 (with a report) if any accepted ADR is not reflected.

Usage:  check_adr_applied.py <workspace-root>
        check_adr_applied.py --self-test
Stdlib only.
"""
import os
import re
import sys

# Gate -> deliverable/workshop fragment, per the layout doctrine (CLAUDE.md / SKILL.md).
GATE_FRAGMENT = {
    "S1a": "docs/architect/business-view.md",
    "S1b": "docs/architect/naive-architecture.md",
    "S2":  "docs/architect/flow-analysis.md",
    "S3":  "docs/architect/stressor-catalog.md",
    "S4":  "docs/architect/contagion-analysis.md",
    "S5":  "docs/architect/residual-design.md",
    "S6":  "docs/architect/empirical-test.md",
    "S7":  "docs/sad/sad.md",
}

STATUS_RE  = re.compile(r"^\|\s*\*{0,2}Status\*{0,2}\s*\|\s*([^\n|]*?)\s*\|", re.M)
HEADING_RE = re.compile(r"^#\s*(ADR-\d+)\b", re.M)


def parse_status(md):
    m = STATUS_RE.search(md)
    return m.group(1).strip().upper() if m else None


def parse_adr_id(md):
    m = HEADING_RE.search(md)
    return m.group(1) if m else None


def parse_outcome(md):
    i = re.search(r"^##\s+(?:\d+\.\s+)?Impact assessment\b", md, re.M)
    if not i:
        return (None, None)
    block = md[i.start():]
    nxt = re.search(r"\n##\s+\S", block)
    if nxt:
        block = block[:nxt.start()]
    m = re.search(r"\*{0,2}Outcome:\*{0,2}\s*([^\n]+)", block, re.I)
    raw = (m.group(1) if m else "").replace("`", "").strip()
    if re.match(r"^no[-\s]?op\b", raw, re.I):
        return ("no-op", None)
    g = re.match(r"^(iterating|reopen)\s+(S\d[ab]?)", raw, re.I)
    return (g.group(1).lower(), g.group(2)) if g else (None, None)


def check(root):
    adr_dir = os.path.join(root, "docs", "adr")
    violations = []
    if not os.path.isdir(adr_dir):
        return violations
    for name in sorted(os.listdir(adr_dir)):
        if not re.match(r"^ADR-\d+-.+\.md$", name):
            continue
        with open(os.path.join(adr_dir, name), encoding="utf-8") as fh:
            adr = fh.read()
        if parse_status(adr) != "ACCEPTED":
            continue
        outcome, gate = parse_outcome(adr)
        if outcome in (None, "no-op") or not gate:
            continue
        adr_id = parse_adr_id(adr) or name
        frag_rel = GATE_FRAGMENT.get(gate)
        frag = ""
        if frag_rel and os.path.isfile(os.path.join(root, frag_rel)):
            with open(os.path.join(root, frag_rel), encoding="utf-8") as fh:
                frag = fh.read()
        if adr_id not in frag:
            violations.append((adr_id, outcome, gate, frag_rel or "(no fragment for gate)"))
    return violations


def main(argv):
    if "--self-test" in argv:
        return _self_test()
    if len(argv) != 2:
        print("usage: check_adr_applied.py <workspace-root> | --self-test", file=sys.stderr)
        return 2
    v = check(argv[1])
    if not v:
        print("ADR-APPLIED OK: every ACCEPTED ADR is reflected in its impact gate fragment.")
        return 0
    for adr_id, outcome, gate, frag in v:
        print(f"VIOLATION: {adr_id} is ACCEPTED ({outcome} {gate}) but its id is absent from {frag}")
    return 1


def _self_test():
    import tempfile, pathlib
    failures = 0
    with tempfile.TemporaryDirectory() as d:
        adr = pathlib.Path(d, "docs", "adr"); adr.mkdir(parents=True)
        arch = pathlib.Path(d, "docs", "architect"); arch.mkdir(parents=True)
        accepted = ("# ADR-0001 - x\n| **Status** | ACCEPTED |\n\n"
                    "## Impact assessment\n- **Outcome:** iterating S5\n")
        (adr / "ADR-0001-x.md").write_text(accepted, encoding="utf-8")
        # fragment WITHOUT the id -> 1 violation
        (arch / "residual-design.md").write_text("no mention\n", encoding="utf-8")
        if len(check(d)) != 1:
            print("self-test FAIL: expected 1 violation when fragment omits the id"); failures += 1
        # fragment WITH the id -> 0 violations
        (arch / "residual-design.md").write_text("removed by ADR-0001\n", encoding="utf-8")
        if len(check(d)) != 0:
            print("self-test FAIL: expected 0 violations when fragment cites the id"); failures += 1
        # PROPOSED -> never blocks
        (adr / "ADR-0001-x.md").write_text(accepted.replace("ACCEPTED", "PROPOSED"), encoding="utf-8")
        (arch / "residual-design.md").write_text("no mention\n", encoding="utf-8")
        if len(check(d)) != 0:
            print("self-test FAIL: PROPOSED ADR must not block"); failures += 1
        # no-op accepted -> never blocks
        (adr / "ADR-0001-x.md").write_text(
            "# ADR-0001 - x\n| **Status** | ACCEPTED |\n\n## Impact assessment\n- **Outcome:** no-op\n",
            encoding="utf-8")
        if len(check(d)) != 0:
            print("self-test FAIL: no-op ACCEPTED ADR must not block"); failures += 1
    print("self-test:", "OK" if failures == 0 else f"{failures} FAILURE(S)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
