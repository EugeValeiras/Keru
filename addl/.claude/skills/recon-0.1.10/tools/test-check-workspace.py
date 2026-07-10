#!/usr/bin/env python3
"""
test-check-workspace.py -- persistent test for the check-workspace.py folder-rule check.

No test framework: run with `python3 test-check-workspace.py`.
Exit 0 = all pass; exit 1 = one or more failures.

Covers the pure classifier (is_recon_artifact / find_misplaced) and the
end-to-end exit-code contract: a recon artifact under docs/reverse-engineer/ is
clean; the same artifact under docs/architecture/ (the collision 0.1.8 fixed) or
loose under docs/ is a MISPLACED violation; a non-recon file in docs/architecture/
(the SAD's own deliverable) is ignored.
"""

import importlib.util
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "check-workspace.py")

_spec = importlib.util.spec_from_file_location("check_workspace", SCRIPT)
cw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cw)

_failures = []


def check(name, ok):
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        _failures.append(name)


def run(root):
    p = subprocess.run([sys.executable, SCRIPT, root], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def write(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("x\n")


# ---- unit: classifier ----------------------------------------------------

check("FLOW.md is a recon artifact", cw.is_recon_artifact("FLOW.md"))
check("R1 fragment is a recon artifact", cw.is_recon_artifact("system-cartography.md"))
check("r1-inventory.json is a recon artifact", cw.is_recon_artifact("r1-inventory.json"))
check("audit-iter-N is a recon artifact", cw.is_recon_artifact("audit-iter-3.md"))
check("audit-drift-ref is a recon artifact", cw.is_recon_artifact("audit-drift-v1.md"))
check("phase0-evidence is a recon artifact", cw.is_recon_artifact("phase0-evidence.md"))
check("a SAD doc is NOT a recon artifact", not cw.is_recon_artifact("software-architecture.md"))
check("README is NOT a recon artifact", not cw.is_recon_artifact("README.md"))
check("audit-iter without .md is NOT matched", not cw.is_recon_artifact("audit-iter-3.txt"))

# ---- end-to-end: exit-code contract --------------------------------------

# Clean: the whole flow lives under docs/reverse-engineer/; the SAD's own
# deliverable coexists in docs/architecture/ -- legitimately, so it is ignored.
with tempfile.TemporaryDirectory() as root:
    for fn in ("FLOW.md", "system-cartography.md", "behavior-reconstruction.md",
               "reconstructed-business-view.md", "asbuilt-stressors.md",
               "r1-inventory.json", "audit-iter-1.md", "phase0-evidence.md"):
        write(os.path.join(root, "docs", "reverse-engineer", fn))
    write(os.path.join(root, "docs", "architecture", "software-architecture.md"))
    code, out, err = run(root)
    check("clean workspace exits 0", code == 0)
    check("clean workspace reports no MISPLACED", "MISPLACED" not in out)

# Violation: FLOW.md leaked into docs/architecture/ (the collision 0.1.8 fixed).
with tempfile.TemporaryDirectory() as root:
    write(os.path.join(root, "docs", "reverse-engineer", "system-cartography.md"))
    write(os.path.join(root, "docs", "architecture", "FLOW.md"))
    code, out, err = run(root)
    check("FLOW.md under docs/architecture/ is MISPLACED", "MISPLACED" in out and "FLOW.md" in out)
    check("misplaced artifact exits 1", code == 1)

# Violation: an audit report leaked into docs/architecture/.
with tempfile.TemporaryDirectory() as root:
    write(os.path.join(root, "docs", "architecture", "audit-iter-2.md"))
    code, out, err = run(root)
    check("audit-iter under docs/architecture/ exits 1", code == 1)

# Violation: a fragment sitting loose directly under docs/ (in neither folder).
with tempfile.TemporaryDirectory() as root:
    write(os.path.join(root, "docs", "system-cartography.md"))
    code, out, err = run(root)
    check("fragment loose under docs/ is MISPLACED", code == 1 and "MISPLACED" in out)

# Ignored: only the SAD's own files under docs/architecture/ -> clean.
with tempfile.TemporaryDirectory() as root:
    write(os.path.join(root, "docs", "architecture", "software-architecture.md"))
    write(os.path.join(root, "docs", "architecture", "diagrams", "c4.puml"))
    code, out, err = run(root)
    check("SAD-only docs/architecture/ exits 0", code == 0)

# No docs/ tree at all -> nothing to check, exit 0.
with tempfile.TemporaryDirectory() as root:
    write(os.path.join(root, "src", "main.py"))
    code, out, err = run(root)
    check("no docs/ dir exits 0", code == 0)

# find_misplaced returns repo-relative paths; the workspace subtree is excluded.
with tempfile.TemporaryDirectory() as root:
    write(os.path.join(root, "docs", "reverse-engineer", "FLOW.md"))      # clean
    write(os.path.join(root, "docs", "architecture", "FLOW.md"))          # misplaced
    mis = cw.find_misplaced(root)
    check("find_misplaced flags only the architecture copy",
          mis == [os.path.join("docs", "architecture", "FLOW.md")])


print()
if _failures:
    print("%d FAILURE(S): %s" % (len(_failures), ", ".join(_failures)))
    sys.exit(1)
print("all checks passed")
sys.exit(0)
