#!/usr/bin/env python3
"""check_ids.py -- deterministic ID resolution for the Developer role (D-03).

Every global ID a Developer artifact (spec/plan/tasks/implemented code surfaced as
text) cites must resolve to the pinned landed release, and IDs are append-only:
never renumbered, never reused (see ../../shared/constitution.md, D-03). A dangling
reference -- an ID that names nothing in the release -- is a hard finding; the gate
cannot pass with one.

Two modes:

    check_ids.py <artifact> <arch-dir>    # resolve every ID/service the artifact
                                          # cites against the landed release
    check_ids.py <arch-dir>               # release self-consistency (D1 intake):
                                          # every crisp ID referenced inside the
                                          # release resolves to a definition in it

The RDAG id scheme (../../shared/glossary.md, the SAD `rdag-id-scheme.md`):

    UC-NNN   use case        defined by a use-cases/uc-NNN-*.md file
    ADR-NNN  binding decision defined by a decisions/ADR-NNN.md file
    NFR-NN   quality req      defined in system-design/nfr-register.md
    service  *Manager/*Engine/*Access, defined in system-design/service-catalog.md
    S-NN     structural stressor   lineage back to the SAD; "defined" = present in
    C-NN     coupling / topology   the release (the SAD evidence layer that minted
    U-NN     unstressed surface    them is NOT part of the handoff)

Crisp types (UC/ADR/NFR/service) resolve against their authoritative file; lineage
types (S/C/U) resolve against the whole release, since the handoff carries them as
references, not definitions.

Exit codes:  0 all cited IDs resolve / 1 one or more dangling (gate blocked)
             2 usage error / required input missing

Stdlib-only. Self-test:  check_ids.py --self-test
"""

import argparse
import os
import re
import sys

OK, FINDINGS, ERROR = 0, 1, 2

SERVICE_RE = re.compile(r"\b[A-Z][A-Za-z0-9]*(?:Manager|Engine|Access)\b")
ID_PATTERNS = {
    "UC": re.compile(r"\bUC-\d{2,}\b"),
    "ADR": re.compile(r"\bADR-\d{2,}\b"),
    "NFR": re.compile(r"\bNFR-\d{2,}\b"),
    "S": re.compile(r"\bS-\d{2,}\b"),
    "C": re.compile(r"\bC-\d{2,}\b"),
    "U": re.compile(r"\bU-\d{2,}\b"),
}
# How each type is labelled and resolved. Crisp types resolve against a defining
# file; lineage types resolve against the whole release.
CRISP = ["SVC", "UC", "ADR", "NFR"]
LINEAGE = ["S", "C", "U"]
LABELS = {
    "SVC": "service names", "UC": "use-case ids", "ADR": "ADR ids",
    "NFR": "NFR ids", "S": "structural-stressor ids", "C": "coupling ids",
    "U": "unstressed-surface ids",
}


class FormatError(Exception):
    """A required binding input is missing."""


class IdResult:
    def __init__(self, typ, ok, findings=None):
        self.typ = typ
        self.name = LABELS[typ]
        self.ok = ok
        self.findings = findings or []

    @property
    def status(self):
        return "PASS" if self.ok else "FAIL"


def collect(text):
    """All ID tokens + service names in a blob of text, keyed by type."""
    out = {k: set(p.findall(text)) for k, p in ID_PATTERNS.items()}
    out["SVC"] = set(SERVICE_RE.findall(text))
    return out


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def load_release(arch_dir):
    """Return (present, defined, warnings).

    present[type] = every token of that type appearing anywhere in the release.
    defined[type] = the authoritative definitions for the crisp types.
    """
    catalog_path = os.path.join(arch_dir, "system-design", "service-catalog.md")
    nfr_path = os.path.join(arch_dir, "system-design", "nfr-register.md")
    uc_dir = os.path.join(arch_dir, "use-cases")
    dec_dir = os.path.join(arch_dir, "decisions")

    for required in (catalog_path, nfr_path):
        if not os.path.isfile(required):
            raise FormatError("required binding input not found: %s" % required)

    warnings = []
    present = {k: set() for k in list(ID_PATTERNS) + ["SVC"]}
    for root, _dirs, files in os.walk(arch_dir):
        for fn in files:
            if fn.endswith(".md"):
                ids = collect(_read(os.path.join(root, fn)))
                for k in present:
                    present[k] |= ids[k]

    defined = {k: set() for k in CRISP}
    # services: any service name appearing in the catalog file
    defined["SVC"] = set(SERVICE_RE.findall(_read(catalog_path)))
    # NFRs: any NFR id appearing in the register file
    defined["NFR"] = set(ID_PATTERNS["NFR"].findall(_read(nfr_path)))
    # UCs: from use-cases/uc-*.md (filename + content)
    if os.path.isdir(uc_dir):
        for fn in sorted(os.listdir(uc_dir)):
            if not fn.endswith(".md"):
                continue
            m = re.search(r"\buc-(\d{2,})", fn, re.I)
            if m:
                defined["UC"].add("UC-" + m.group(1))
            defined["UC"] |= set(ID_PATTERNS["UC"].findall(_read(os.path.join(uc_dir, fn))))
    else:
        warnings.append("no use-cases/ dir in the release: every UC citation will dangle")
    # ADRs: from decisions/ADR-*.md (filename + content)
    if os.path.isdir(dec_dir):
        for fn in sorted(os.listdir(dec_dir)):
            if not fn.endswith(".md"):
                continue
            m = re.search(r"\badr-(\d{2,})", fn, re.I)
            if m:
                defined["ADR"].add("ADR-" + m.group(1))
            defined["ADR"] |= set(ID_PATTERNS["ADR"].findall(_read(os.path.join(dec_dir, fn))))
    else:
        warnings.append("no decisions/ dir in the release: every ADR citation will dangle")

    return present, defined, warnings


def check_artifact(artifact_text, present, defined):
    cited = collect(artifact_text)
    results = []
    for typ in CRISP:
        dangling = sorted(cited[typ] - defined[typ])
        results.append(IdResult(typ, not dangling,
                                ["%s does not resolve to the pinned release" % x for x in dangling]))
    for typ in LINEAGE:
        dangling = sorted(cited[typ] - present[typ])
        results.append(IdResult(typ, not dangling,
                                ["%s appears nowhere in the pinned release" % x for x in dangling]))
    return results


def check_release(present, defined):
    """Self-consistency: a crisp ID referenced inside the release but never
    defined (e.g. a UC mentioned in an ADR with no matching uc-NNN file)."""
    results = []
    for typ in CRISP:
        dangling = sorted(present[typ] - defined[typ])
        results.append(IdResult(typ, not dangling,
                                ["%s is referenced in the release but never defined" % x for x in dangling]))
    return results


def report(results, subject, arch_dir, mode, warnings, as_json=False):
    if as_json:
        import json
        print(json.dumps({
            "subject": subject, "arch": arch_dir, "mode": mode,
            "passed": not any(r.ok is False for r in results),
            "warnings": warnings,
            "results": [{"type": r.typ, "name": r.name, "status": r.status,
                         "findings": r.findings} for r in results],
        }, indent=2))
        return
    print("ID resolution (D-03) -- %s mode" % mode)
    if subject:
        print("  artifact: %s" % subject)
    print("  release:  %s" % arch_dir)
    for w in warnings:
        print("  warning: %s" % w)
    print()
    for r in results:
        n = len(r.findings)
        suffix = "  (%d finding%s)" % (n, "" if n == 1 else "s") if not r.ok else ""
        print("  %-4s %-26s %s%s" % (r.typ, r.name, r.status, suffix))
    findings = [(r, f) for r in results if not r.ok for f in r.findings]
    if findings:
        print()
        print("Findings (dangling / unresolved -- a hard D-03 failure):")
        for r, f in findings:
            print("  - [%s] %s" % (r.typ, f))
    print()
    if any(not r.ok for r in results):
        print("VERDICT: BLOCKED -- a cited ID does not resolve. IDs are append-only and "
              "must exist in the pinned release; fix the citation or, if the release is "
              "genuinely missing it, raise a back-channel request.")
    else:
        print("VERDICT: all cited IDs resolve to the pinned release.")


def run(subject, arch_dir):
    present, defined, warnings = load_release(arch_dir)
    if subject is None:
        return check_release(present, defined), "release", warnings
    return check_artifact(_read(subject), present, defined), "artifact", warnings


# --- self-test -----------------------------------------------------------------
_BASE = {
    "system-design/service-catalog.md": (
        "# Service catalog\n\n"
        "| Service | Category | Stressors-absorbed |\n|---|---|---|\n"
        "| OrderManager | Manager | S-01, S-03 |\n"
        "| PricingEngine | Engine | S-02 |\n"
        "| LedgerAccess | Access | S-04 |\n"
    ),
    "system-design/nfr-register.md": (
        "# NFR register\n\n| NFR | Statement | Source |\n|---|---|---|\n"
        "| NFR-01 | latency | C-01 |\n| NFR-02 | availability | C-02 |\n"
    ),
    "decisions/ADR-001.md": "# ADR-001 gRPC\nBinding: Yes\n",
    "decisions/ADR-002.md": "# ADR-002 PostgreSQL\nBinding: Yes\n",
    "use-cases/uc-001-capture.md": (
        "# UC-001 Order capture\n\nCall Chain: Client -> OrderManager -> PricingEngine "
        "-> LedgerAccess\nResidue: S-01, S-03; coupling C-01; surface U-01\n"
    ),
}
_PLAN_OK = (
    "# plan UC-001\nOrderManager calls PricingEngine, persists via LedgerAccess.\n"
    "Honors NFR-01 (C-01) and ADR-001; absorbs S-01; surface U-01.\n"
)
_PLAN_BAD = (
    "# plan UC-999\nOrderManager calls BillingManager.\n"
    "Honors NFR-77 and ADR-099; absorbs S-99; coupling C-88.\n"
)


def _build(tmp, overrides):
    files = dict(_BASE)
    files.update(overrides)
    for rel, content in files.items():
        p = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(content)
    return tmp


def self_test():
    import tempfile
    passed = failed = 0

    def check(label, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print("  ok    %s" % label)
        else:
            failed += 1
            print("  FAIL  %s" % label)

    with tempfile.TemporaryDirectory() as tmp:
        # the release lives in its own subdir so the artifacts written below are
        # NOT walked into the release universe
        arch = _build(os.path.join(tmp, "release"), {})

        # artifact: all ids resolve
        plan_ok = os.path.join(tmp, "plan_ok.md")
        open(plan_ok, "w").write(_PLAN_OK)
        res, mode, _ = run(plan_ok, arch)
        check("clean plan: every type resolves", all(r.ok for r in res) and mode == "artifact")

        # artifact: dangling of every type
        plan_bad = os.path.join(tmp, "plan_bad.md")
        open(plan_bad, "w").write(_PLAN_BAD)
        res, _, _ = run(plan_bad, arch)
        by = {r.typ: r for r in res}
        check("dangling UC-999 caught", not by["UC"].ok and any("UC-999" in f for f in by["UC"].findings))
        check("dangling service BillingManager caught", not by["SVC"].ok and any("BillingManager" in f for f in by["SVC"].findings))
        check("dangling ADR-099 caught", not by["ADR"].ok)
        check("dangling NFR-77 caught", not by["NFR"].ok)
        check("dangling S-99 caught", not by["S"].ok)
        check("dangling C-88 caught", not by["C"].ok)

        # release self-consistency: clean release passes
        res, mode, _ = run(None, arch)
        check("clean release self-consistency passes", all(r.ok for r in res) and mode == "release")

        # release self-consistency: a UC referenced but undefined is caught
        arch2 = _build(tmp + "_2",
                       {"decisions/ADR-002.md": "# ADR-002 PostgreSQL\nBinding: Yes\nSee UC-777 for context.\n"})
        res, _, _ = run(None, arch2)
        check("release with undefined UC-777 reference is caught",
              any(not r.ok and any("UC-777" in f for f in r.findings) for r in res))

    # exit-code contract
    with tempfile.TemporaryDirectory() as tmp:
        arch = _build(os.path.join(tmp, "release"), {})
        open(os.path.join(tmp, "ok.md"), "w").write(_PLAN_OK)
        open(os.path.join(tmp, "bad.md"), "w").write(_PLAN_BAD)
        r_ok, _, _ = run(os.path.join(tmp, "ok.md"), arch)
        r_bad, _, _ = run(os.path.join(tmp, "bad.md"), arch)
        check("exit-code contract (0 clean / 1 dangling)",
              (OK if all(r.ok for r in r_ok) else FINDINGS) == OK
              and (FINDINGS if any(not r.ok for r in r_bad) else OK) == FINDINGS)

    print("\nself-test: %d passed, %d failed" % (passed, failed))
    return OK if failed == 0 else FINDINGS


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_ids.py",
        description="Resolve every cited global ID against the pinned landed release (D-03).")
    parser.add_argument("args", nargs="*",
                        help="<artifact> <arch-dir>  OR  <arch-dir> (release self-check)")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixtures and exit")
    ns = parser.parse_args(argv)

    if ns.self_test:
        return self_test()

    if len(ns.args) == 1:
        subject, arch_dir = None, ns.args[0]
    elif len(ns.args) == 2:
        subject, arch_dir = ns.args[0], ns.args[1]
    else:
        parser.error("expected <artifact> <arch-dir> or <arch-dir> (or --self-test)")

    if subject is not None and not os.path.isfile(subject):
        print("error: artifact not found: %s" % subject, file=sys.stderr)
        return ERROR
    if not os.path.isdir(arch_dir):
        print("error: release dir not found: %s" % arch_dir, file=sys.stderr)
        return ERROR

    try:
        results, mode, warnings = run(subject, arch_dir)
    except FormatError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return ERROR

    report(results, subject, arch_dir, mode, warnings, as_json=ns.json)
    return FINDINGS if any(not r.ok for r in results) else OK


if __name__ == "__main__":
    sys.exit(main())
