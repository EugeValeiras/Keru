#!/usr/bin/env python3
"""check_scope.py -- architecture-scope drift between a feature and its UC (P5 / A2).

The UC's "Services touched" table is the architectural scope of the feature: the
constitution says "/speckit-plan MUST NOT introduce a service absent from Services
touched". But the verbatim Architectural Context block + the catalog membership check
do NOT stop the spec (or plan) from citing OTHER catalog services in its requirements
-- a silent scope widening that only an operator might notice at the heuristic Q3.
This check makes it deterministic.

    check_scope.py <spec.md> <uc.md>            # D2: spec scope vs the UC
    check_scope.py <spec.md> <uc.md> --plan <plan.md>   # + D3 backward completeness
    check_scope.py <spec.md> <uc.md> --code <path...>   # + D5 post-implement code drift

D2 checks:
  - every service the spec names is in the UC's "Services touched" (no scope widening);
  - every NFR the spec references is in the UC's "Applicable NFRs" (no out-of-scope NFR).
D3 (with --plan): the plan covers every service the UC touches (backward completeness).
D5 (with --code): the implemented code introduces no service outside the UC's Services
  touched. spec-kit's post-implement drift must be read off the CODE that was written,
  not off plan.md -- the plan is the intent; the code is what actually shipped.

Exit codes:  0 in scope / 1 scope drift or incompleteness (gate blocked)
             2 usage error / file not found
Stdlib-only. Self-test:  check_scope.py --self-test
"""

import argparse
import os
import re
import sys

OK, FINDINGS, ERROR = 0, 1, 2

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
SECTION_NUM_RE = re.compile(r"^\d+(?:\.\d+)*\.?\s+")
SERVICE_RE = re.compile(r"\b[A-Z][A-Za-z0-9]*(?:Manager|Engine|Access)\b")
NFR_RE = re.compile(r"\bNFR-\d{2,}\b")
# 'ResourceAccess' matches SERVICE_RE but is the category word (column 2 of a Services
# touched table), never a service name -- exclude it so it is not read as a service.
CATEGORY_WORDS = {"ResourceAccess"}


def _htitle(h):
    return SECTION_NUM_RE.sub("", h.strip()).lower()


def section_body(text, substr):
    """Body under the first heading whose number-stripped title CONTAINS substr (lower),
    up to the next heading of same-or-higher level. '' if absent."""
    lines = text.splitlines()
    start = level = None
    for i, ln in enumerate(lines):
        m = HEADING_RE.match(ln)
        if m and substr in _htitle(m.group(2)):
            start, level = i + 1, len(m.group(1))
            break
    if start is None:
        return ""
    body = []
    for ln in lines[start:]:
        m = HEADING_RE.match(ln)
        if m and len(m.group(1)) <= level:
            break
        body.append(ln)
    return "\n".join(body)


def _table_services(text):
    """Service names from the FIRST column of a markdown table (skips header/separator;
    reading column 1 avoids the category word in column 2)."""
    out = set()
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
            out.add(m.group(0))
    return out


def _services(text):
    return set(SERVICE_RE.findall(text)) - CATEGORY_WORDS


def check(spec_text, uc_text, plan_text=None, code_text=None):
    findings = []
    touched = _table_services(section_body(uc_text, "services touched"))
    if not touched:
        return ["the UC has no parseable 'Services touched' table -- run check_uc_structure first"]

    for svc in sorted(_services(spec_text) - touched):
        findings.append("scope drift: the spec cites service '%s' that is NOT in the UC's "
                        "'Services touched' (the architecture did not approve it for this feature)" % svc)

    uc_nfrs = set(NFR_RE.findall(section_body(uc_text, "applicable nfr")))
    if uc_nfrs:
        for nfr in sorted(set(NFR_RE.findall(spec_text)) - uc_nfrs):
            findings.append("scope drift: the spec references %s outside the UC's Applicable NFRs" % nfr)

    if plan_text is not None:
        for svc in sorted(touched - _services(plan_text)):
            findings.append("backward completeness: the plan does not reference UC service '%s' "
                            "(Services touched) -- the feature's call chain is incompletely planned" % svc)

    if code_text is not None:
        for svc in sorted(_services(code_text) - touched):
            findings.append("post-implement drift: the implemented code introduces service '%s' "
                            "that is NOT in the UC's 'Services touched' (D-01 -- the architecture "
                            "did not sanction it; this is what actually shipped, not the plan)" % svc)
    return findings


SRC_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".java", ".cs", ".rb", ".kt",
            ".swift", ".rs", ".cpp", ".cc", ".c", ".h", ".hpp", ".php", ".scala", ".m", ".mm"}


def _read_code(paths):
    """Concatenate the text of the given code paths. A directory is walked for source
    files (by extension) so binaries/assets are skipped; a file is read as-is."""
    chunks = []
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                for fn in files:
                    if os.path.splitext(fn)[1].lower() in SRC_EXTS:
                        chunks.append(_read(os.path.join(root, fn)))
        elif os.path.isfile(p):
            chunks.append(_read(p))
        else:
            raise FileNotFoundError(p)
    return "\n".join(chunks)


def report(findings, spec_path, extra):
    print("Architecture-scope drift (P5 / A2)%s" % (" + %s" % extra if extra else ""))
    print("  spec: %s" % spec_path)
    print()
    if not findings:
        print("VERDICT: in scope -- the spec stays within the UC's Services touched / Applicable NFRs"
              + (" (%s)." % extra if extra else "."))
        return
    print("Findings (%d):" % len(findings))
    for f in findings:
        print("  - %s" % f)
    print()
    print("VERDICT: BLOCKED -- a service/NFR outside the UC's approved scope, or an unplanned "
          "UC service. Stay within the UC; if the feature genuinely needs more, add/extend the "
          "UC in Phase A (it does not get widened silently in the spec/plan).")


# --- self-test -----------------------------------------------------------------
_UC = """# UC-001 -- Charge session

## 4. Architectural Context

### Call Chain
```mermaid
graph LR
    Charger --> CSM
```

### Services touched

| Service | Category | Role |
|---|---|---|
| `ChargeSessionManager` | Manager | orchestrates |
| `AuthEngine` | Engine | identity |
| `ChargerAccess` | ResourceAccess | hardware |

### Residue
| Service | Absorbs |
|---|---|
| `ChargeSessionManager` | S-03 |

## 10. Applicable NFRs
NFR-01, NFR-02
"""
# spec carries the verbatim AC (so it names the three services in column 1, plus the
# category word ResourceAccess in column 2) and adds in-scope requirements.
_SPEC_OK = _UC.replace("# UC-001 -- Charge session", "# Feature spec: 001-charge").replace(
    "## 10. Applicable NFRs\nNFR-01, NFR-02\n",
    "## Requirements\nFR-1: ChargeSessionManager opens a session honoring NFR-01.\n")


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

    expect("in-scope spec passes (and ResourceAccess category word is not a service)",
           not check(_SPEC_OK, _UC))

    # SEEDED: spec cites a service not in the UC's Services touched
    drift = _SPEC_OK.replace("FR-1: ChargeSessionManager opens a session honoring NFR-01.",
                             "FR-1: ChargeSessionManager opens a session.\nFR-2: BillingManager bills it.")
    f = check(drift, _UC)
    expect("service scope drift is caught", any("BillingManager" in x and "scope drift" in x for x in f))

    # SEEDED: spec references an NFR outside the UC's Applicable NFRs
    nfr_drift = _SPEC_OK.replace("honoring NFR-01.", "honoring NFR-01 and NFR-99.")
    f = check(nfr_drift, _UC)
    expect("NFR scope drift is caught", any("NFR-99" in x for x in f))

    # SEEDED: plan omits a UC service (backward completeness)
    plan_missing = "# plan\nImplement via ChargeSessionManager and ChargerAccess.\n"  # AuthEngine omitted
    f = check(_SPEC_OK, _UC, plan_missing)
    expect("plan omitting a UC service is caught (backward completeness)",
           any("AuthEngine" in x and "backward completeness" in x for x in f))

    # a complete plan passes the backward-completeness check
    plan_ok = "# plan\nChargeSessionManager calls AuthEngine then ChargerAccess.\n"
    expect("complete plan passes backward completeness", not check(_SPEC_OK, _UC, plan_ok))

    # SEEDED: the implemented code introduces a service the UC never sanctioned (D5 drift)
    code_drift = ("class ChargeSessionManager {}\nclass AuthEngine {}\nclass ChargerAccess {}\n"
                  "class FraudEngine {}  // never in the UC\n")
    f = check(_SPEC_OK, _UC, None, code_drift)
    expect("code-introduced service is caught (D5 post-implement drift)",
           any("FraudEngine" in x and "post-implement drift" in x for x in f))

    # in-scope code passes
    code_ok = "class ChargeSessionManager {}\nclass AuthEngine {}\nclass ChargerAccess {}\n"
    expect("in-scope implemented code passes", not check(_SPEC_OK, _UC, None, code_ok))

    print("\nself-test: %d passed, %d failed" % (passed, failed))
    return OK if failed == 0 else FINDINGS


def _read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_scope.py",
        description="Architecture-scope drift: the spec/plan stays within the UC's Services touched.")
    parser.add_argument("spec", nargs="?", help="the feature spec.md")
    parser.add_argument("uc", nargs="?", help="the source use-cases/uc-NNN-*.md")
    parser.add_argument("--plan", help="the plan.md (adds the D3 backward-completeness check)")
    parser.add_argument("--code", nargs="+", metavar="PATH",
                        help="implemented source file(s)/dir(s) (adds the D5 post-implement code-drift check)")
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixtures and exit")
    ns = parser.parse_args(argv)

    if ns.self_test:
        return self_test()
    if not ns.spec or not ns.uc:
        parser.error("expected <spec.md> <uc.md> (or --self-test)")
    for p in [ns.spec, ns.uc] + ([ns.plan] if ns.plan else []):
        if not os.path.isfile(p):
            print("error: file not found: %s" % p, file=sys.stderr)
            return ERROR
    code_text = None
    if ns.code:
        try:
            code_text = _read_code(ns.code)
        except FileNotFoundError as exc:
            print("error: code path not found: %s" % exc, file=sys.stderr)
            return ERROR

    findings = check(_read(ns.spec), _read(ns.uc), _read(ns.plan) if ns.plan else None, code_text)
    extra = " + ".join([s for s, on in [("backward completeness", ns.plan),
                                         ("post-implement code drift", ns.code)] if on])
    report(findings, ns.spec, extra)
    return FINDINGS if findings else OK


if __name__ == "__main__":
    sys.exit(main())
