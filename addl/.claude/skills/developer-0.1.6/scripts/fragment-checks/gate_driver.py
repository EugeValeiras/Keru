#!/usr/bin/env python3
"""gate_driver.py -- deterministic gate router for the Developer meta-skill.

The Developer governs spec-kit by deciding, at every step, WHICH spec-kit skill to
invoke, in what ORDER, with what FLAGS, and under what PRECONDITIONS. That decision
must NOT be left to LLM judgement turn-by-turn -- it is a deterministic function of
the workspace state. This script is that function.

Given a consumer workspace and a target feature, it resolves the state on disk and
emits the single next action: the current gate (D1..D5), the exact next
`/speckit-<x>` call (hyphen form -- the Claude-skill name), its
preconditions (met / unmet, blocking), any
governance directives the call must carry, and the exact deterministic checks to
run at this gate. The LLM's only non-deterministic job is to perform the one
generative skill invocation this script names -- a Python script cannot itself
invoke an in-session Claude skill.

Feature resolution mirrors spec-kit's own `common.sh: get_feature_paths`
(SPECIFY_FEATURE env -> .specify/feature.json "feature_directory" -> latest
specs/<NNN-slug>/), so the driver agrees with spec-kit about the active feature.

    gate_driver.py [WORKSPACE_ROOT] [--feature NAME] [--arch DIR] [--json]

Exit codes:  0 actionable next step (or feature complete) / 1 blocked (a
             precondition is unmet) / 2 usage error

Stdlib-only. Self-test:  gate_driver.py --self-test
"""

import argparse
import glob
import json as _json
import os
import re
import sys

OK, BLOCKED, ERROR = 0, 1, 2

# spec-kit Claude-skill invocation names (hyphen form). The dot form is only the
# workflow-engine id -- never used for invocation.
SPECIFY = "/speckit-specify"
CLARIFY = "/speckit-clarify"
PLAN = "/speckit-plan"
TASKS = "/speckit-tasks"
ANALYZE = "/speckit-analyze"
IMPLEMENT = "/speckit-implement"

CHECK_DIR = "scripts/fragment-checks"
ARCH_PIN = ".specify/memory/.arch-pin.json"   # A3 constitution-integrity pin, written at D1


class Action:
    """The single next step the orchestrator must take."""

    def __init__(self, gate, status, command=None, directives=None,
                 preconditions=None, checks=None, recommended_before=None, notes=None):
        self.gate = gate                      # D1..D5 or "complete"
        self.status = status                  # ready | blocked | complete
        self.command = command                # the /speckit-* call, or None
        self.directives = directives or []    # governance instructions the call must carry
        self.preconditions = preconditions or []  # [{name, met}]
        self.checks = checks or []            # deterministic check command-lines to run at this gate
        self.recommended_before = recommended_before  # optional /speckit-* to run first
        self.notes = notes or []

    @property
    def blocked(self):
        return self.status == "blocked"

    def to_dict(self, feature, feature_dir, arch):
        return {
            "feature": feature,
            "feature_dir": feature_dir,
            "arch": arch,
            "gate": self.gate,
            "status": self.status,
            "next_command": self.command,
            "directives": self.directives,
            "preconditions": self.preconditions,
            "recommended_before": self.recommended_before,
            "checks_to_run": self.checks,
            "notes": self.notes,
        }


def _latest_feature(specs_dir):
    """Mirror spec-kit: pick the highest sequential NNN- (or latest timestamp) dir."""
    if not os.path.isdir(specs_dir):
        return None
    seq, seq_name, ts, ts_name = -1, None, "", None
    for name in sorted(os.listdir(specs_dir)):
        if not os.path.isdir(os.path.join(specs_dir, name)):
            continue
        m = re.match(r"^(\d{8}-\d{6})-", name)
        if m:
            if m.group(1) > ts:
                ts, ts_name = m.group(1), name
            continue
        m = re.match(r"^(\d{3,})-", name)
        if m:
            n = int(m.group(1))
            if n > seq:
                seq, seq_name = n, name
    return ts_name or seq_name


def _read_feature_json(root):
    fj = os.path.join(root, ".specify", "feature.json")
    if not os.path.isfile(fj):
        return None
    try:
        with open(fj, encoding="utf-8") as fh:
            return _json.load(fh).get("feature_directory") or None
    except (ValueError, OSError):
        return None


def resolve_feature(root, feature_arg):
    """Return (feature_name, feature_dir_abs_or_None). Mirrors get_feature_paths."""
    specs_dir = os.path.join(root, "specs")
    name = feature_arg or os.environ.get("SPECIFY_FEATURE")
    if name:
        return name, os.path.join(specs_dir, name)
    fd = _read_feature_json(root)
    if fd:
        if not os.path.isabs(fd):
            fd = os.path.join(root, fd)
        return os.path.basename(fd.rstrip("/")), fd
    latest = _latest_feature(specs_dir)
    if latest:
        return latest, os.path.join(specs_dir, latest)
    return None, None


def detect_arch(root, arch_arg):
    """Return the landed release dir, or None. Newest architecture/arch-* by name."""
    if arch_arg:
        return arch_arg if os.path.isdir(arch_arg) else None
    cands = sorted(glob.glob(os.path.join(root, "architecture", "arch-*")))
    cands = [c for c in cands if os.path.isdir(c)]
    return cands[-1] if cands else None


def _tasks_all_done(tasks_path):
    """True if tasks.md exists and every task checkbox is marked done ([X]/[x])."""
    if not os.path.isfile(tasks_path):
        return False
    text = open(tasks_path, encoding="utf-8").read()
    boxes = re.findall(r"^\s*-\s*\[( |x|X)\]", text, re.M)
    return bool(boxes) and all(b in ("x", "X") for b in boxes)


def _rel(root, path):
    try:
        return os.path.relpath(path, root)
    except ValueError:
        return path


def decide(root, feature, feature_dir, arch):
    """The deterministic gate state machine. Returns an Action."""
    constitution = os.path.join(root, ".specify", "memory", "constitution.md")
    override = os.path.join(root, ".specify", "templates", "overrides", "plan-template.md")
    arch_present = arch is not None and os.path.isfile(constitution)
    override_present = os.path.isfile(override)

    # --- D1 intake: the landed RDAG handoff must be present and wired ----------
    if not arch_present:
        return Action(
            "D1", "blocked",
            preconditions=[
                {"name": "landed architecture/arch-X.Y.Z/ exists", "met": arch is not None},
                {"name": ".specify/memory/constitution.md exists", "met": os.path.isfile(constitution)},
            ],
            notes=["D1 intake: land the RDAG handoff (S8b) before any gate. "
                   "No spec-kit call until the binding architecture + constitution are present."])
    if not override_present:
        return Action(
            "D1", "blocked",
            preconditions=[{"name": ".specify/templates/overrides/plan-template.md installed (well-formed splice)", "met": False}],
            checks=[
                "%s/check_ids.py %s   # release ID self-consistency" % (CHECK_DIR, _rel(root, arch)),
                "%s/check_principle.py .specify/memory/constitution.md %s/integration/principle-decomposition-by-residue.md   # CHK-01 clause-level" % (CHECK_DIR, _rel(root, arch)),
                "%s/check_uc_structure.py %s   # CHK-10 every UC well-formed (handoff-form)" % (CHECK_DIR, _rel(root, arch)),
                "%s/check_adr_binding.py %s   # CHK-12 binding ADRs well-formed + enumerated (handoff-form)" % (CHECK_DIR, _rel(root, arch)),
                "%s/check_override.py --build .specify/templates/plan-template.md %s/integration/plan-template-constitution-check.md > .specify/templates/overrides/plan-template.md" % (CHECK_DIR, _rel(root, arch)),
                "%s/check_override.py --verify .specify/templates/overrides/plan-template.md .specify/templates/plan-template.md .specify/memory/constitution.md" % CHECK_DIR,
                "%s/check_drift.py .specify/memory/constitution.md %s --pin %s   # A3: pin the architecture half once approved" % (CHECK_DIR, _rel(root, arch), ARCH_PIN),
            ],
            notes=["D1 intake: SPLICE the RDAG Q1-Q6 block into a COPY of spec-kit's current "
                   "core plan-template -- do NOT install the partial block whole. resolve_template "
                   "REPLACES, so a whole-copy strips Technical Context / Project Structure and can "
                   "leave the gate vacuous. Use check_override.py --build to produce it and --verify "
                   "to confirm it is well-formed. /speckit-constitution does NOT install it."])

    spec = os.path.join(feature_dir, "spec.md") if feature_dir else None
    plan = os.path.join(feature_dir, "plan.md") if feature_dir else None
    tasks = os.path.join(feature_dir, "tasks.md") if feature_dir else None

    # --- D2 specify ------------------------------------------------------------
    if not feature_dir or not os.path.isfile(spec):
        return Action(
            "D2", "ready", command=SPECIFY,
            directives=["Seed from the target UC-NNN; the spec MUST carry the use "
                        "case's Architectural Context (Call Chain / Services touched / "
                        "Residue) verbatim (D-01/D2)."],
            preconditions=[{"name": "D1 intake approved (arch + constitution APPROVED + CHK-01 via check_principle.py + WELL-FORMED override via check_override.py --verify)", "met": True}],
            checks=[
                "%s/check_arch_context.py <FEATURE_DIR>/spec.md %s/use-cases/uc-NNN-*.md" % (CHECK_DIR, _rel(root, arch)),
                "%s/check_scope.py <FEATURE_DIR>/spec.md %s/use-cases/uc-NNN-*.md   # no scope drift beyond the UC" % (CHECK_DIR, _rel(root, arch)),
                "%s/check_ids.py <FEATURE_DIR>/spec.md %s" % (CHECK_DIR, _rel(root, arch)),
                "%s/check_drift.py .specify/memory/constitution.md %s --against %s   # A3 constitution integrity" % (CHECK_DIR, _rel(root, arch), ARCH_PIN),
            ],
            notes=["ENTRY POINT (Phase A -> Phase B): Phase A must be complete first -- "
                   "constitution APPROVED and the target UC selected. UC/ADR adds happen "
                   "in Phase A only, never during the workflow.",
                   "spec-kit runs create-new-feature.sh: creates the NNN-slug branch + "
                   "specs/NNN-slug/ and copies the spec template. Optional %s before D3 "
                   "if the spec carries [NEEDS CLARIFICATION] markers." % CLARIFY])

    fdir_rel = _rel(root, feature_dir)

    # --- D3 plan + Constitution Check -----------------------------------------
    if not os.path.isfile(plan):
        return Action(
            "D3", "ready", command=PLAN,
            recommended_before=CLARIFY,
            preconditions=[{"name": "spec.md exists (D2 approved)", "met": True}],
            checks=[
                "%s/check_entry.py .   # A5: D1 override + pin present before /speckit-plan (no bypass)" % CHECK_DIR,
                "%s/check_principle.py .specify/memory/constitution.md %s/integration/principle-decomposition-by-residue.md   # CHK-01 still holds (no architecture-half drift)" % (CHECK_DIR, _rel(root, arch)),
                "%s/check_drift.py .specify/memory/constitution.md %s --against %s   # A3 constitution integrity (pinned at D1)" % (CHECK_DIR, _rel(root, arch), ARCH_PIN),
                "%s/check_override.py --verify .specify/templates/overrides/plan-template.md .specify/templates/plan-template.md .specify/memory/constitution.md   # re-verify the gate wiring before planning" % CHECK_DIR,
                "%s/check_constitution.py %s/plan.md %s" % (CHECK_DIR, fdir_rel, _rel(root, arch)),
                "%s/check_scope.py %s/spec.md %s/use-cases/uc-NNN-*.md --plan %s/plan.md   # backward completeness" % (CHECK_DIR, fdir_rel, _rel(root, arch), fdir_rel),
                "%s/check_ids.py %s/plan.md %s" % (CHECK_DIR, fdir_rel, _rel(root, arch)),
            ],
            notes=["spec-kit runs setup-plan.sh and fills the Constitution Check from "
                   ".specify/memory/constitution.md. The override template wires Q1-Q6. "
                   "Park D3 only when check_constitution passes (Q1-Q6 all yes); a No is a "
                   "back-channel request, never an inline fix (D-01)."])

    # --- D4 tasks (TDD-mandatory per D-02) ------------------------------------
    if not os.path.isfile(tasks):
        return Action(
            "D4", "ready", command=TASKS,
            directives=["D-02 Tested code: spec-kit tasks are TEST-OPTIONAL by default. "
                        "Explicitly direct /speckit-tasks to produce a TDD-first task list "
                        "(test tasks precede their implementation tasks); otherwise D5 "
                        "cannot pass honestly."],
            preconditions=[
                {"name": "plan.md exists (D3 approved)", "met": True},
                {"name": "Constitution Check (Q1-Q6) passed at D3", "met": "verify: re-run check_constitution if unsure"},
            ],
            checks=[
                "%s/check_entry.py . --plan %s/plan.md   # A5: the plan carries the Q1-Q6 gate (not a bypassed /speckit-plan)" % (CHECK_DIR, fdir_rel),
                "%s/check_ids.py %s/tasks.md %s" % (CHECK_DIR, fdir_rel, _rel(root, arch)),
                "%s/check_tdd.py %s/tasks.md   # TDD-first per user story (D-02)" % (CHECK_DIR, fdir_rel),
                "%s/check_drift.py .specify/memory/constitution.md %s --against %s   # A3 constitution integrity" % (CHECK_DIR, _rel(root, arch), ARCH_PIN),
            ],
            notes=["spec-kit runs setup-tasks.sh (needs plan.md + spec.md)."])

    # --- feature complete? -----------------------------------------------------
    if _tasks_all_done(tasks):
        return Action(
            "complete", "complete",
            checks=[
                "%s/check_ids.py %s/tasks.md %s   # drift re-check" % (CHECK_DIR, fdir_rel, _rel(root, arch)),
                "%s/check_scope.py %s/spec.md %s/use-cases/uc-NNN-*.md --code <IMPLEMENTED_SRC>   # post-implement code drift (D-01)"
                % (CHECK_DIR, fdir_rel, _rel(root, arch)),
                "%s/check_drift.py .specify/memory/constitution.md %s --against %s   # A3 constitution integrity" % (CHECK_DIR, _rel(root, arch), ARCH_PIN),
            ],
            notes=["All tasks marked done. The post-implement drift re-check reads the CODE "
                   "that shipped, not plan.md: pass the source paths the completed tasks touched "
                   "(listed in tasks.md) as <IMPLEMENTED_SRC>. No service the architecture did not "
                   "sanction may appear in it (D-01)."])

    # --- D5 implement ----------------------------------------------------------
    return Action(
        "D5", "ready", command=IMPLEMENT,
        recommended_before=ANALYZE,
        preconditions=[{"name": "tasks.md exists (D4 approved)", "met": True}],
        directives=["D-02: do not approve D5 unless tasks were TDD-first and tests run green."],
        checks=[
            "%s/check_ids.py %s/tasks.md %s   # post-implement drift" % (CHECK_DIR, fdir_rel, _rel(root, arch)),
            "%s/check_scope.py %s/spec.md %s/use-cases/uc-NNN-*.md --code <IMPLEMENTED_SRC>   # post-implement code drift (D-01)"
            % (CHECK_DIR, fdir_rel, _rel(root, arch)),
            "%s/check_drift.py .specify/memory/constitution.md %s --against %s   # A3 constitution integrity" % (CHECK_DIR, _rel(root, arch), ARCH_PIN),
        ],
        notes=["%s (read-only cross-artifact consistency) runs AFTER tasks and BEFORE "
               "implement -- run it first. spec-kit implement marks tasks [X] in tasks.md. "
               "After implementing, the drift re-check reads the CODE (pass the touched source "
               "paths as <IMPLEMENTED_SRC>), not plan.md -- the code is what shipped." % ANALYZE])


def report(action, feature, feature_dir, arch, root, as_json):
    if as_json:
        print(_json.dumps(action.to_dict(feature, _rel(root, feature_dir) if feature_dir else None,
                                         _rel(root, arch) if arch else None), indent=2))
        return
    print("Developer gate driver (deterministic routing)")
    print("  workspace: %s" % root)
    print("  feature:   %s" % (feature or "(none yet)"))
    print("  release:   %s" % (_rel(root, arch) if arch else "(none)"))
    print()
    print("  GATE:   %s   [%s]" % (action.gate, action.status))
    if action.recommended_before:
        print("  run-first (recommended): %s" % action.recommended_before)
    if action.command:
        print("  NEXT CALL: %s" % action.command)
    elif action.status == "complete":
        print("  NEXT CALL: (none -- feature complete)")
    else:
        print("  NEXT CALL: (blocked -- resolve preconditions below)")
    if action.directives:
        print("  directives:")
        for d in action.directives:
            print("    - %s" % d)
    if action.preconditions:
        print("  preconditions:")
        for p in action.preconditions:
            print("    - [%s] %s" % (p["met"] if isinstance(p["met"], str) else ("x" if p["met"] else " "), p["name"]))
    if action.checks:
        print("  checks to run at this gate:")
        for c in action.checks:
            print("    $ %s" % c)
    if action.notes:
        print("  notes:")
        for n in action.notes:
            print("    - %s" % n)


def run(root, feature_arg, arch_arg):
    root = os.path.abspath(root)
    feature, feature_dir = resolve_feature(root, feature_arg)
    arch = detect_arch(root, arch_arg)
    action = decide(root, feature, feature_dir, arch)
    return action, feature, feature_dir, arch, root


# --- self-test -----------------------------------------------------------------
def _mkworkspace(tmp, *, arch=True, override=True, spec=False, plan=False,
                 tasks=False, tasks_done=False):
    root = tmp
    os.makedirs(os.path.join(root, ".specify", "memory"), exist_ok=True)
    os.makedirs(os.path.join(root, ".specify", "templates", "overrides"), exist_ok=True)
    if arch:
        d = os.path.join(root, "architecture", "arch-1.0.0", "use-cases")
        os.makedirs(d, exist_ok=True)
        open(os.path.join(root, ".specify", "memory", "constitution.md"), "w").write("# constitution\n")
    if override:
        open(os.path.join(root, ".specify", "templates", "overrides", "plan-template.md"), "w").write("# override\n")
    fdir = os.path.join(root, "specs", "001-cap")
    if spec or plan or tasks:
        os.makedirs(fdir, exist_ok=True)
    if spec:
        open(os.path.join(fdir, "spec.md"), "w").write("# spec\n")
    if plan:
        open(os.path.join(fdir, "plan.md"), "w").write("# plan\n")
    if tasks:
        body = "- [X] T001 a\n- [%s] T002 b\n" % ("X" if tasks_done else " ")
        open(os.path.join(fdir, "tasks.md"), "w").write(body)
    return root


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

    scenarios = [
        ("no arch -> D1 blocked", dict(arch=False), "D1", "blocked", None),
        ("arch but no override -> D1 blocked", dict(override=False), "D1", "blocked", None),
        ("arch+override, no spec -> D2 specify", dict(), "D2", "ready", SPECIFY),
        ("spec, no plan -> D3 plan", dict(spec=True), "D3", "ready", PLAN),
        ("plan, no tasks -> D4 tasks", dict(spec=True, plan=True), "D4", "ready", TASKS),
        ("tasks (incomplete) -> D5 implement", dict(spec=True, plan=True, tasks=True), "D5", "ready", IMPLEMENT),
        ("tasks all done -> complete", dict(spec=True, plan=True, tasks=True, tasks_done=True), "complete", "complete", None),
    ]
    for label, kw, gate, status, cmd in scenarios:
        with tempfile.TemporaryDirectory() as tmp:
            root = _mkworkspace(tmp, **kw)
            action, *_ = run(root, None, None)
            check(label, action.gate == gate and action.status == status and action.command == cmd)

    # determinism: same state -> identical output
    with tempfile.TemporaryDirectory() as tmp:
        root = _mkworkspace(tmp, spec=True, plan=True)
        a1, *_ = run(root, None, None)
        a2, *_ = run(root, None, None)
        check("deterministic: repeated runs agree", a1.to_dict("x", "y", "z") == a2.to_dict("x", "y", "z"))

    # D4 carries the TDD directive (D-02) and emits check_tdd (P6)
    with tempfile.TemporaryDirectory() as tmp:
        root = _mkworkspace(tmp, spec=True, plan=True)
        a, *_ = run(root, None, None)
        check("D4 carries the D-02 TDD directive", any("TDD" in d for d in a.directives))
        check("D4 emits check_tdd.py (P6)", any("check_tdd.py" in c for c in a.checks))

    # D5 + complete target the CODE for post-implement drift (P6), not plan.md
    with tempfile.TemporaryDirectory() as tmp:
        root = _mkworkspace(tmp, spec=True, plan=True, tasks=True)
        a, *_ = run(root, None, None)
        check("D5 post-implement drift targets the code (check_scope --code)",
              any("check_scope.py" in c and "--code" in c for c in a.checks)
              and not any("check_constitution.py" in c and "plan.md" in c for c in a.checks))
        root = _mkworkspace(tmp, spec=True, plan=True, tasks=True, tasks_done=True)
        a, *_ = run(root, None, None)
        check("complete re-check targets the code (check_scope --code)",
              any("check_scope.py" in c and "--code" in c for c in a.checks))

    # D3 emits the constitution check command
    with tempfile.TemporaryDirectory() as tmp:
        root = _mkworkspace(tmp, spec=True)
        a, *_ = run(root, None, None)
        check("D3 emits check_constitution command", any("check_constitution.py" in c for c in a.checks))

    # A3: D1 pins the constitution; every later gate re-checks against the pin
    with tempfile.TemporaryDirectory() as tmp:
        root = _mkworkspace(tmp, override=False)         # D1 wiring (override-build) block
        a, *_ = run(root, None, None)
        check("D1 pins the architecture half (check_drift --pin)",
              any("check_drift.py" in c and "--pin" in c for c in a.checks))
        for kw, label in [(dict(), "D2"), (dict(spec=True), "D3"),
                          (dict(spec=True, plan=True), "D4"),
                          (dict(spec=True, plan=True, tasks=True), "D5"),
                          (dict(spec=True, plan=True, tasks=True, tasks_done=True), "complete")]:
            root = _mkworkspace(tmp, **kw)
            a, *_ = run(root, None, None)
            check("%s re-checks constitution integrity (check_drift --against)" % label,
                  any("check_drift.py" in c and "--against" in c for c in a.checks))

    # A5: D3 guards the entry (override+pin) and D4 verifies the plan carries the gate
    with tempfile.TemporaryDirectory() as tmp:
        root = _mkworkspace(tmp, spec=True)
        a, *_ = run(root, None, None)
        check("D3 emits the A5 entry guard (check_entry, no --plan)",
              any("check_entry.py" in c and "--plan" not in c for c in a.checks))
        root = _mkworkspace(tmp, spec=True, plan=True)
        a, *_ = run(root, None, None)
        check("D4 verifies the plan carries the gate (check_entry --plan)",
              any("check_entry.py" in c and "--plan" in c for c in a.checks))

    # D5 recommends analyze before implement
    with tempfile.TemporaryDirectory() as tmp:
        root = _mkworkspace(tmp, spec=True, plan=True, tasks=True)
        a, *_ = run(root, None, None)
        check("D5 recommends /speckit-analyze first", a.recommended_before == ANALYZE)

    # exit-code contract: blocked -> 1, ready -> 0
    with tempfile.TemporaryDirectory() as tmp:
        root = _mkworkspace(tmp, arch=False)
        a, *_ = run(root, None, None)
        check("exit-code: blocked -> 1", (BLOCKED if a.blocked else OK) == BLOCKED)
        root = _mkworkspace(tmp, spec=True)
        a, *_ = run(root, None, None)
        check("exit-code: ready -> 0", (BLOCKED if a.blocked else OK) == OK)

    print("\nself-test: %d passed, %d failed" % (passed, failed))
    return OK if failed == 0 else BLOCKED


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="gate_driver.py",
        description="Deterministic gate router: resolve workspace state and emit the next spec-kit call.")
    parser.add_argument("root", nargs="?", default=".", help="consumer workspace root (default: cwd)")
    parser.add_argument("--feature", help="active feature name (else SPECIFY_FEATURE / feature.json / latest)")
    parser.add_argument("--arch", help="landed release dir (else newest architecture/arch-*)")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixtures and exit")
    ns = parser.parse_args(argv)

    if ns.self_test:
        return self_test()

    if not os.path.isdir(ns.root):
        print("error: workspace root not found: %s" % ns.root, file=sys.stderr)
        return ERROR

    action, feature, feature_dir, arch, root = run(ns.root, ns.feature, ns.arch)
    report(action, feature, feature_dir, arch, root, as_json=ns.json)
    return BLOCKED if action.blocked else OK


if __name__ == "__main__":
    sys.exit(main())
