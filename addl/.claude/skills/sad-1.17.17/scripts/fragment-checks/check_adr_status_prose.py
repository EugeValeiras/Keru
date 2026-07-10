#!/usr/bin/env python3
"""check_adr_status_prose.py -- fragments must not transcribe a stale ADR Status.

An ADR's Status (DRAFT/PROPOSED/ACCEPTED/DECLINED/SUPERSEDED) lives in the ADR
file and is operator-owned; it changes AFTER a fragment is written (e.g. the
operator accepts the ADR). A fragment that hardcodes the status in prose
-- "ADR-0001 (..., PROPOSED) decided ..." -- goes stale and trips a FALSE audit
mismatch ("PROPOSED rather than ACCEPTED") even though the architecture is
correct. Reference an ADR by id and let the ADR file be the source of truth.

This check scans the gate fragments + the assembled SAD for a status keyword
transcribed in proximity to an ADR id and flags it when it disagrees with that
ADR's actual Status. Exit 1 (with a report) on any stale transcription.

Usage:  check_adr_status_prose.py <workspace-root>
        check_adr_status_prose.py --self-test
Stdlib only.
"""
import os
import re
import sys

STATUSES = ("DRAFT", "PROPOSED", "ACCEPTED", "DECLINED", "SUPERSEDED")
STATUS_RE = re.compile("|".join(STATUSES))
STATUS_ROW = re.compile(r"^\|\s*\*{0,2}Status\*{0,2}\s*\|\s*([^\n|]*?)\s*\|", re.M)
ADR_REF = re.compile(r"\bADR-\d+\b")

# The fragments whose prose can transcribe an ADR status (the assembled SAD too).
SCAN = [
    "docs/architect/business-view.md",
    "docs/architect/naive-architecture.md",
    "docs/architect/flow-analysis.md",
    "docs/architect/stressor-catalog.md",
    "docs/architect/contagion-analysis.md",
    "docs/architect/residual-design.md",
    "docs/architect/empirical-test.md",
    "docs/sad/sad.md",
]


def adr_statuses(root):
    """Map ADR id -> actual Status (upper) from docs/adr/."""
    out = {}
    adir = os.path.join(root, "docs", "adr")
    if not os.path.isdir(adir):
        return out
    for name in sorted(os.listdir(adir)):
        m = re.match(r"^(ADR-\d+)-.+\.md$", name)
        if not m:
            continue
        with open(os.path.join(adir, name), encoding="utf-8") as fh:
            s = STATUS_ROW.search(fh.read())
        if s:
            out[m.group(1)] = s.group(1).strip().upper()
    return out


def scan_text(text, statuses):
    """Return [(adr_id, found_status, actual)] for stale transcriptions.

    A status keyword within the same sentence and 80 chars after an ADR id is a
    transcription of that ADR's status; if it disagrees with the ADR file it is
    stale. Proximity + sentence boundary keep unrelated prose out.
    """
    viol = []
    flagged = set()  # one finding per ADR per file (the id also appears inside its own path)
    for m in ADR_REF.finditer(text):
        adr = m.group(0)
        if adr in flagged:
            continue
        actual = statuses.get(adr)
        if not actual:
            continue
        window = text[m.end(): m.end() + 80]
        window = re.split(r"(?<=[.;])\s", window, 1)[0]  # stop at sentence end
        sm = STATUS_RE.search(window)
        if sm and sm.group(0).upper() != actual:
            viol.append((adr, sm.group(0).upper(), actual))
            flagged.add(adr)
    return viol


def check(root):
    statuses = adr_statuses(root)
    out = []
    for rel in SCAN:
        p = os.path.join(root, rel)
        if not os.path.isfile(p):
            continue
        with open(p, encoding="utf-8") as fh:
            for adr, found, actual in scan_text(fh.read(), statuses):
                out.append((rel, adr, found, actual))
    return out


def main(argv):
    if "--self-test" in argv:
        return _self_test()
    if len(argv) != 2:
        print("usage: check_adr_status_prose.py <workspace-root> | --self-test", file=sys.stderr)
        return 2
    v = check(argv[1])
    if not v:
        print("ADR-STATUS-PROSE OK: no stale ADR status transcribed in any fragment.")
        return 0
    for rel, adr, found, actual in v:
        print(f"VIOLATION: {rel} narrates {adr} as {found} but its actual Status is {actual} -- reference by id, do not transcribe status")
    return 1


def _self_test():
    import tempfile, pathlib
    fails = 0
    with tempfile.TemporaryDirectory() as d:
        adr = pathlib.Path(d, "docs", "adr"); adr.mkdir(parents=True)
        arch = pathlib.Path(d, "docs", "architect"); arch.mkdir(parents=True)
        (adr / "ADR-0001-x.md").write_text("# ADR-0001 - x\n| **Status** | ACCEPTED |\n", encoding="utf-8")
        rd = arch / "residual-design.md"
        # stale: prose says PROPOSED, ADR is ACCEPTED -> 1 violation
        rd.write_text("ADR-0001 (`docs/adr/ADR-0001-x.md`, PROPOSED) decided not to implement X.\n", encoding="utf-8")
        if len(check(d)) != 1:
            print("self-test FAIL: stale PROPOSED prose should be 1 violation"); fails += 1
        # matching: prose says ACCEPTED -> 0
        rd.write_text("ADR-0001 (`docs/adr/ADR-0001-x.md`, ACCEPTED) decided not to implement X.\n", encoding="utf-8")
        if len(check(d)) != 0:
            print("self-test FAIL: matching status must not flag"); fails += 1
        # id-only (no status near id) -> 0  [the recommended form]
        rd.write_text("Removed by ADR-0001 (single operator). Elsewhere the gate is PROPOSED for unrelated reasons.\n", encoding="utf-8")
        if len(check(d)) != 0:
            print("self-test FAIL: id-only reference must not flag (status beyond the sentence window)"); fails += 1
        # unknown ADR id -> 0
        rd.write_text("ADR-0099 (PROPOSED) is not on disk.\n", encoding="utf-8")
        if len(check(d)) != 0:
            print("self-test FAIL: unknown ADR must not flag"); fails += 1
    print("self-test:", "OK" if fails == 0 else f"{fails} FAILURE(S)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
