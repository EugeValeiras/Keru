#!/usr/bin/env python3
"""
run-evals.py -- recon's deterministic false-anchor MUTATION HARNESS.

No test framework: run it with `python3 evals/run-evals.py`.
Exit 0 = every eval passed; exit 1 = one or more failed.

WHAT THIS IS (and is not). The four `tools/test-*.py` files unit-test each
validator in isolation. This harness is the layer above them: it stands up ONE
coherent, realistic recon fixture -- a tiny under-documented brownfield repo plus
the clean R1 `system-cartography.md` fragment a faithful run would emit -- proves
that fragment passes ALL FOUR validators (the BASELINE is green), then injects
exactly one false-anchor regression at a time and asserts the matching validator
flips to a hard FAIL (exit 1). It answers a question the unit tests do not:
"does the deterministic layer, taken together, catch each regression class it was
built for, against the same evidence a real fragment carries?"

The five regression classes it mutates (each maps to RE-01 / RE-05 doctrine):
  1. past-EOF anchor          -> check-anchors.py  (line cited beyond file end)
  2. off-by-one content       -> check-anchors.py  (snippet cited on wrong line)
  3. count drift              -> check-counts.py   (verify-block number lies)
  4. uncovered file           -> repo-census.py coverage  ("nothing lost" broken)
  5. misplaced workspace file -> check-workspace.py (recon artifact in docs/architecture/)

Deterministic and offline: repo-census runs with --no-git; no validator writes,
networks, or needs a git repo. Same fixture in -> same verdicts out.

This is the CI-able half of the recon eval set. The model-driven half -- R1..R4
routing and gate discipline -- lives in `evals/recon-prompts.md` (run by hand
against the skill, since it needs the LLM and cannot be made deterministic). See
`evals/README.md`.
"""

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.normpath(os.path.join(HERE, "..", "tools"))
CHECK_ANCHORS = os.path.join(TOOLS, "check-anchors.py")
CHECK_COUNTS = os.path.join(TOOLS, "check-counts.py")
CHECK_WORKSPACE = os.path.join(TOOLS, "check-workspace.py")
REPO_CENSUS = os.path.join(TOOLS, "repo-census.py")

_failures = []


def check(name, ok):
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        _failures.append(name)


def run(*argv):
    """Run a validator as a subprocess; return (exit_code, stdout+stderr)."""
    p = subprocess.run([sys.executable, *argv], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


# ---------------------------------------------------------------------------
# The fixture: a tiny brownfield target repo a recon run would reverse-engineer.
# Line numbers are load-bearing -- the fragment anchors cite them by hand.
# ---------------------------------------------------------------------------

REPO_FILES = {
    # 6-line Dockerfile (build-ci). Anchors cite :1-3; :99 is the past-EOF mutant.
    "gateway/Dockerfile": (
        "FROM node:20-alpine\n"   # 1
        "WORKDIR /app\n"          # 2
        "COPY package.json .\n"   # 3
        "RUN npm ci\n"            # 4
        "COPY src .\n"            # 5
        'CMD ["node","index.js"]\n'  # 6
    ),
    # source:go -- line 2 holds `func main`, the content-anchor target.
    "gateway/server.go": (
        "package gateway\n"       # 1
        "func main() {}\n"        # 2
    ),
    "gateway/server_test.go": "package gateway\n",   # 1  (test)
    # config -- line 4 holds DATABASE_URL, the snippet-anchor target.
    "config/app.yaml": (
        "service: gateway\n"                              # 1
        "port: 8080\n"                                    # 2
        "env:\n"                                          # 3
        "  DATABASE_URL: postgres://localhost:5432/app\n"  # 4
    ),
    "README.md": "# gateway\n",   # 1  (docs)
    "go.mod": "module gateway\n",  # 1  (build-ci)
}

# The clean R1 fragment a faithful recon run emits for that repo. Every anchor is
# in-bounds; every `~ snippet` sits on its cited line; the verify block's number
# is the real grep count; and every non-excluded repo file is referenced (so the
# census coverage check is satisfied). Mutations below each break exactly one of
# those properties.
CLEAN_FRAGMENT = (
    "# R1 -- system-cartography (eval fixture)\n"
    "\n"
    "## Entry points & build\n"
    "- Container build: `gateway/Dockerfile:1-3` (FROM / WORKDIR / COPY).\n"
    "- HTTP server entry: `gateway/server.go:2 ~ func main`.\n"
    "- Module manifest: `go.mod:1`.\n"
    "\n"
    "## Config & data stores\n"
    "- App config + DB URL: `config/app.yaml:4 ~ DATABASE_URL`.\n"
    "\n"
    "## Tests & docs\n"
    "- Server test: `gateway/server_test.go:1`.\n"
    "- Overview: `README.md:1`.\n"
    "\n"
    "## Count claims\n"
    "\n"
    "```verify\n"
    'grep -c "func main" gateway/server.go\n'
    "1\n"
    "```\n"
)


def build_repo(root):
    """Materialize REPO_FILES under root."""
    for rel, body in REPO_FILES.items():
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(body)


def write_fragment(wsdir, text, name="system-cartography.md"):
    """Write a fragment into the recon workspace (kept OUTSIDE the target repo,
    exactly as recon does: fragments live under docs/reverse-engineer/, never in
    the inventory the census walks)."""
    path = os.path.join(wsdir, name)
    with open(path, "w") as fh:
        fh.write(text)
    return path


def anchors_exit(fragment, root):
    return run(CHECK_ANCHORS, fragment, root)


def counts_exit(fragment, root):
    return run(CHECK_COUNTS, fragment, root)


def coverage_exit(fragment, root):
    return run(REPO_CENSUS, "coverage", fragment, root, "--no-git")


# ---------------------------------------------------------------------------
# BASELINE: the clean fragment must pass all four content validators (exit 0).
# If the baseline is not green, every mutation result below is meaningless, so
# this is asserted first.
# ---------------------------------------------------------------------------

with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as ws:
    build_repo(root)
    frag = write_fragment(ws, CLEAN_FRAGMENT)

    code, out = anchors_exit(frag, root)
    check("BASELINE check-anchors: clean fragment exits 0", code == 0)
    check("BASELINE check-anchors: no VIOLATION on clean fragment", "VIOLATION" not in out)

    code, out = counts_exit(frag, root)
    check("BASELINE check-counts: clean fragment exits 0", code == 0)
    check("BASELINE check-counts: no MISMATCH on clean fragment", "MISMATCH" not in out)

    code, out = coverage_exit(frag, root)
    check("BASELINE coverage: every repo file accounted for, exits 0", code == 0)
    check("BASELINE coverage: no UNCOVERED on clean fragment", "UNCOVERED" not in out)


# ---------------------------------------------------------------------------
# MUTATION 1 -- past-EOF anchor (RE-01). Cite a line beyond the file's end.
# check-anchors must report it as a deterministic VIOLATION and exit 1.
# ---------------------------------------------------------------------------

with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as ws:
    build_repo(root)
    mutant = CLEAN_FRAGMENT.replace("gateway/Dockerfile:1-3", "gateway/Dockerfile:99")
    check("mut1 mutation applied (anchor moved past EOF)", mutant != CLEAN_FRAGMENT)
    frag = write_fragment(ws, mutant)
    code, out = anchors_exit(frag, root)
    check("mut1 past-EOF anchor is a VIOLATION", "gateway/Dockerfile:99  past EOF" in out)
    check("mut1 past-EOF anchor exits 1", code == 1)
    # And the regression is scoped: the count check still passes on this fragment.
    code, _ = counts_exit(frag, root)
    check("mut1 is isolated: check-counts still exits 0", code == 0)


# ---------------------------------------------------------------------------
# MUTATION 2 -- off-by-one CONTENT anchor (RE-01). The snippet's true line is 4;
# cite it on line 3. check-anchors must raise a CONTENT violation and exit 1.
# ---------------------------------------------------------------------------

with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as ws:
    build_repo(root)
    mutant = CLEAN_FRAGMENT.replace("config/app.yaml:4 ~ DATABASE_URL",
                                    "config/app.yaml:3 ~ DATABASE_URL")
    check("mut2 mutation applied (snippet line off by one)", mutant != CLEAN_FRAGMENT)
    frag = write_fragment(ws, mutant)
    code, out = anchors_exit(frag, root)
    check("mut2 off-by-one snippet is a CONTENT violation", "CONTENT" in out)
    check("mut2 CONTENT violation finger-points at the true line 4", "found at line 4" in out)
    check("mut2 off-by-one snippet exits 1", code == 1)


# ---------------------------------------------------------------------------
# MUTATION 3 -- count drift (RE-01). The grep really returns 1; claim 5 instead.
# check-counts must re-run the command, see the mismatch, and exit 1.
# ---------------------------------------------------------------------------

with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as ws:
    build_repo(root)
    mutant = CLEAN_FRAGMENT.replace('gateway/server.go\n1\n', 'gateway/server.go\n5\n')
    check("mut3 mutation applied (claimed count drifted to 5)", mutant != CLEAN_FRAGMENT)
    frag = write_fragment(ws, mutant)
    code, out = counts_exit(frag, root)
    check("mut3 count drift is a MISMATCH", "MISMATCH" in out)
    check("mut3 MISMATCH shows expected 5 vs actual 1",
          "expected: 5" in out and "actual:   1" in out)
    check("mut3 count drift exits 1", code == 1)
    # Anchors are untouched -> still clean.
    code, _ = anchors_exit(frag, root)
    check("mut3 is isolated: check-anchors still exits 0", code == 0)


# ---------------------------------------------------------------------------
# MUTATION 4 -- uncovered file (RE-01 "nothing lost"). Drop the only reference to
# config/app.yaml; the census coverage check must flag it UNCOVERED and exit 1.
# ---------------------------------------------------------------------------

with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as ws:
    build_repo(root)
    mutant = CLEAN_FRAGMENT.replace(
        "- App config + DB URL: `config/app.yaml:4 ~ DATABASE_URL`.\n", "")
    check("mut4 mutation applied (config reference dropped)", mutant != CLEAN_FRAGMENT)
    frag = write_fragment(ws, mutant)
    code, out = coverage_exit(frag, root)
    check("mut4 dropped file is reported UNCOVERED", "UNCOVERED  config/app.yaml" in out)
    check("mut4 uncovered file exits 1", code == 1)


# ---------------------------------------------------------------------------
# MUTATION 5 -- misplaced workspace artifact (RE-05). A recon-owned file leaks
# into the SAD's docs/architecture/ (the name-collision 0.1.8 fixed).
# check-workspace must flag it MISPLACED and exit 1.
# ---------------------------------------------------------------------------

def write_ws_file(root, *parts):
    path = os.path.join(root, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("x\n")


with tempfile.TemporaryDirectory() as root:
    # Clean baseline: the whole flow under docs/reverse-engineer/; SAD owns
    # docs/architecture/ legitimately.
    write_ws_file(root, "docs", "reverse-engineer", "FLOW.md")
    write_ws_file(root, "docs", "reverse-engineer", "system-cartography.md")
    write_ws_file(root, "docs", "architecture", "software-architecture.md")
    code, out = run(CHECK_WORKSPACE, root)
    check("BASELINE check-workspace: clean layout exits 0", code == 0)
    check("BASELINE check-workspace: no MISPLACED on clean layout", "MISPLACED" not in out)

    # Mutate: leak FLOW.md into docs/architecture/.
    write_ws_file(root, "docs", "architecture", "FLOW.md")
    code, out = run(CHECK_WORKSPACE, root)
    check("mut5 recon artifact in docs/architecture/ is MISPLACED",
          "MISPLACED" in out and "FLOW.md" in out)
    check("mut5 misplaced artifact exits 1", code == 1)


print()
if _failures:
    print("%d EVAL FAILURE(S): %s" % (len(_failures), ", ".join(_failures)))
    sys.exit(1)
print("all evals passed")
sys.exit(0)
