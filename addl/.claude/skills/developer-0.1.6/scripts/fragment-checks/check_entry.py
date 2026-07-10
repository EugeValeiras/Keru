#!/usr/bin/env python3
"""check_entry.py -- sole-entry / D1-precondition guard (A5).

The governance only holds if EVERY plan is generated through D1's spliced Q1-Q6 override.
A direct `/speckit-plan` that skips D1 uses spec-kit's STOCK plan-template -- which has no
Constitution Check -- so the gate is silently absent and check_constitution evaluates a
plan that was never built under the architecture. This guard refuses that path:

  - the Q1-Q6 override template must be installed (else spec-kit falls back to stock);
  - the D1 architecture pin must exist (proof D1 actually ran -- see check_drift.py / A3);
  - any plan.md that exists must CARRY the Constitution Check Q1-Q6 section (proof it was
    generated through the override, not a bypassing direct /speckit-plan).

    check_entry.py <workspace-root>                 # before planning: D1 wiring present?
    check_entry.py <workspace-root> --plan <plan.md>   # + the plan carries the gate

Exit codes:  0 entry is governed / 1 D1 bypassed or wiring missing (gate blocked)
             2 usage error / path not found
Stdlib-only. Self-test:  check_entry.py --self-test
"""

import argparse
import os
import re
import sys

OK, FINDINGS, ERROR = 0, 1, 2

OVERRIDE_REL = os.path.join(".specify", "templates", "overrides", "plan-template.md")
PIN_REL = os.path.join(".specify", "memory", ".arch-pin.json")
CONSTITUTION_CHECK_RE = re.compile(r"constitution\s+check", re.IGNORECASE)
Q_RE = re.compile(r"\bQ([1-6])\b")


def has_constitution_check(plan_text):
    """True if the plan carries the spliced Constitution Check gate: a 'Constitution Check'
    heading/line AND at least 4 distinct Q1-Q6 markers (the override's hallmark; a stock
    spec-kit plan has neither)."""
    if not CONSTITUTION_CHECK_RE.search(plan_text):
        return False
    return len(set(Q_RE.findall(plan_text))) >= 4


def check(override_present, pin_present, plan_text):
    findings = []
    if not override_present:
        findings.append("the Q1-Q6 override plan-template is NOT installed (%s) -- /speckit-plan "
                        "would use spec-kit's STOCK template and the Constitution Check gate would "
                        "be absent. Complete D1 (intake) first." % OVERRIDE_REL)
    if not pin_present:
        findings.append("no D1 architecture pin (%s) -- D1 was never completed, so a plan/tasks "
                        "run would be ungoverned. Run D1 (intake) and pin the constitution first." % PIN_REL)
    if plan_text is not None and not has_constitution_check(plan_text):
        findings.append("plan.md carries NO 'Constitution Check' Q1-Q6 section -- it was generated "
                        "BYPASSING the governed override (a direct /speckit-plan). Regenerate the "
                        "plan through D1's override template; do not hand-add the section.")
    return findings


def report(findings, root, with_plan):
    print("Sole-entry / D1-precondition guard (A5)")
    print("  workspace: %s" % root)
    print()
    if not findings:
        print("VERDICT: governed entry -- the Q1-Q6 override + D1 pin are present"
              + (" and the plan carries the Constitution Check gate." if with_plan else "."))
        return
    print("Findings (%d):" % len(findings))
    for f in findings:
        print("  - %s" % f)
    print()
    print("VERDICT: BLOCKED -- this would run spec-kit OUTSIDE the governed entry. The Developer "
          "meta-skill is the sole entry: D1 lands + approves + pins + installs the override, and "
          "only then does Phase B (/speckit-specify .. /speckit-plan ..) run.")


# --- self-test -----------------------------------------------------------------
_PLAN_GATED = """# Implementation plan -- 001 (UC-001)

## Technical Context
...

## Constitution Check (two tiers)
### Tier 1 -- Architecture half (NON-WAIVABLE)
- Q1 catalog membership: yes
- Q2 naming suffix: yes
- Q3 call-chain layering: yes
- Q4 structural lineage: yes
### Tier 2 -- Implementation half
- Q5 NFR coupling: yes
- Q6 binding-ADR conformance: yes
"""
# a STOCK spec-kit plan: Technical Context + Project Structure, but NO Constitution Check
_PLAN_STOCK = """# Implementation plan -- 001

## Technical Context
Language: Python.

## Project Structure
src/, tests/.
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

    expect("override+pin present, gated plan -> governed (no findings)",
           not check(True, True, _PLAN_GATED))
    expect("override+pin present, no plan -> governed (precondition only)",
           not check(True, True, None))
    expect("missing override is caught",
           any("override plan-template is NOT installed" in f for f in check(False, True, None)))
    expect("missing pin is caught",
           any("no D1 architecture pin" in f for f in check(True, False, None)))
    expect("a STOCK plan (no Constitution Check) is caught -- the A5 bypass signal",
           any("BYPASSING the governed override" in f for f in check(True, True, _PLAN_STOCK)))
    expect("a gated plan passes the content check", not check(True, True, _PLAN_GATED))
    # a plan that mentions 'Constitution Check' but carries too few Q-markers is still a bypass
    weak = "## Constitution Check\nWe considered Q1 only.\n"
    expect("a Constitution-Check heading with <4 Q-markers is still caught",
           any("BYPASSING" in f for f in check(True, True, weak)))

    print("\nself-test: %d passed, %d failed" % (passed, failed))
    return OK if failed == 0 else FINDINGS


def _read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_entry.py",
        description="Sole-entry / D1-precondition guard (A5): no /speckit-plan that skips D1.")
    parser.add_argument("root", nargs="?", help="the workspace root (holds .specify/)")
    parser.add_argument("--plan", help="a plan.md to verify it carries the Constitution Check gate")
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixtures and exit")
    ns = parser.parse_args(argv)

    if ns.self_test:
        return self_test()
    if not ns.root:
        parser.error("expected <workspace-root> (or --self-test)")
    if not os.path.isdir(ns.root):
        print("error: workspace root not found: %s" % ns.root, file=sys.stderr)
        return ERROR
    plan_text = None
    if ns.plan:
        if not os.path.isfile(ns.plan):
            print("error: file not found: %s" % ns.plan, file=sys.stderr)
            return ERROR
        plan_text = _read(ns.plan)

    findings = check(os.path.isfile(os.path.join(ns.root, OVERRIDE_REL)),
                     os.path.isfile(os.path.join(ns.root, PIN_REL)),
                     plan_text)
    report(findings, ns.root, bool(ns.plan))
    return FINDINGS if findings else OK


if __name__ == "__main__":
    sys.exit(main())
