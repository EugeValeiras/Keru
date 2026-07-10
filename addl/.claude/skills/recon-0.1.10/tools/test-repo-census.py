#!/usr/bin/env python3
"""
test-repo-census.py -- persistent test for the repo-census.py inventory tool.

No test framework: run it with `python3 test-repo-census.py`.
Exit 0 = all pass; exit 1 = one or more failures.

Covers the pure typing ruleset (classify), the enumeration fallback (walk),
the census grouping, and the coverage "nothing is lost" check end-to-end with
`--no-git` so the test needs no git repo.
"""

import importlib.util
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "repo-census.py")

_spec = importlib.util.spec_from_file_location("repo_census", SCRIPT)
rc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rc)

_failures = []


def check(name, ok):
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        _failures.append(name)


def run(*args):
    p = subprocess.run([sys.executable, SCRIPT] + list(args),
                       capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


# ---- unit: classify (the deterministic ruleset) ---------------------------

check("go source", rc.classify("pkg/actors/orders/orders_actor.go") == "source:go")
check("go test by suffix", rc.classify("pkg/actors/orders/orders_actor_test.go") == "test")
check("test by dir segment", rc.classify("tests/helpers/setup.go") == "test")
check("js spec by infix", rc.classify("web/src/app.spec.js") == "test")
check("markdown is docs", rc.classify("docs/actors/orders.md") == "docs")
check("puml is docs", rc.classify("docs/diagrams/tick.puml") == "docs")
check("http request spec is docs", rc.classify("pkg/actors/orders/orders_api.http") == "docs")
check("README is docs", rc.classify("README") == "docs")
check("CLAUDE.md is docs", rc.classify("CLAUDE.md") == "docs")
check("k8s yaml is iac-deploy", rc.classify("k8s/deploy/market-stream.yaml") == "iac-deploy")
check("terraform is iac-deploy", rc.classify("infra/main.tf") == "iac-deploy")
check("sql is schema-migration", rc.classify("k8s/pgsql/trade_ticks.sql") == "schema-migration")
check("migrations dir", rc.classify("db/migrations/001_init.py") == "schema-migration")
check("Dockerfile is build-ci", rc.classify("services/feature/Dockerfile") == "build-ci")
check("go.mod is build-ci", rc.classify("go.mod") == "build-ci")
check("package.json is build-ci (not config)", rc.classify("gateway/package.json") == "build-ci")
check("workflow is build-ci", rc.classify(".github/workflows/ci.yml") == "build-ci")
check("go.sum is generated-lock", rc.classify("go.sum") == "generated-lock")
check("package-lock is generated-lock", rc.classify("web/package-lock.json") == "generated-lock")
check("min.js is generated-lock", rc.classify("web/static/vendor.min.js") == "generated-lock")
check("png is asset-binary", rc.classify("docs/diagrams/trader-flows.png") == "asset-binary")
check("compiled binary is asset-binary", rc.classify("services/feature/go_build_feature") == "unclassified")  # no ext -> unclassified
check("html is source:html", rc.classify("web/index.html") == "source:html")
check("css is source:css", rc.classify("web/src/styles/app.scss") == "source:css")
check("plain yaml is config", rc.classify("config/app.yaml") == "config")
check("excluded cache dir is filtered", rc.is_excluded("pkg/.gocache/aa/deadbeef-d"))
check("excluded DS_Store is filtered", rc.is_excluded("docs/.DS_Store"))
check("real source path is not excluded", not rc.is_excluded("pkg/actors/orders/orders_actor.go"))
check("installed .claude tooling is filtered", rc.is_excluded(".claude/skills/x/SKILL.md"))
check(".gitignore is filtered", rc.is_excluded(".gitignore"))
check(".github CI is NOT excluded (real build info)", not rc.is_excluded(".github/workflows/ci.yml"))
check("env is config", rc.classify(".env") == "config")
check("unknown ext is unclassified", rc.classify("data/weird.xyz") == "unclassified")
check("no-extension file is unclassified", rc.classify("Procfile") == "unclassified")
check("build-ci precedes test-segment for package.json", rc.classify("tests/package.json") == "build-ci")

# ---- unit: coverage predicate --------------------------------------------

_frag = "See `pkg/actors/orders/orders_actor.go:54` and the `services/market-order` module."
check("exact path is covered", rc.is_covered("pkg/actors/orders/orders_actor.go", _frag))
check("ancestor dir is covered", rc.is_covered("services/market-order/main.go", _frag))
check("unmentioned file is uncovered", not rc.is_covered("services/risk/cmd/main.go", _frag))
# Root fix: a dot-path left in-census (e.g. .github CI) must be coverable by reference.
check("dot-path is captured as a token", ".github/workflows/ci.yml" in rc.referenced_paths("see `.github/workflows/ci.yml`"))
check("dot-path is coverable by exact mention", rc.is_covered(".github/workflows/ci.yml", "build: `.github/workflows/ci.yml`"))
check("dot-dir covers its file", rc.is_covered(".github/workflows/ci.yml", "CI lives under `.github/`"))
check("prose ellipsis is not a path token", "..." not in rc.referenced_paths("wait... then go"))
check("uncovered() filters correctly",
      rc.uncovered(["pkg/actors/orders/orders_actor.go", "services/risk/cmd/main.go"], _frag)
      == ["services/risk/cmd/main.go"])

# ---- unit: census grouping -----------------------------------------------

_files = ["a.go", "a_test.go", "README.md", "k8s/x.yaml", "go.sum", "mystery.xyz"]
_cen = rc.census(_files)
check("census groups by category", _cen["source:go"] == ["a.go"] and _cen["test"] == ["a_test.go"])
check("census captures unclassified", _cen["unclassified"] == ["mystery.xyz"])

# ---- end-to-end: census + coverage over a tmp repo (--no-git) -------------

with tempfile.TemporaryDirectory() as root:
    os.makedirs(os.path.join(root, "pkg"))
    os.makedirs(os.path.join(root, "docs"))
    os.makedirs(os.path.join(root, "node_modules", "dep"))  # must be excluded by walk
    for rel, body in [
        ("pkg/orders.go", "package pkg\n"),
        ("pkg/orders_test.go", "package pkg\n"),
        ("docs/design.md", "# design\n"),
        ("go.mod", "module x\n"),
        ("weird.xyz", "?\n"),
        ("node_modules/dep/index.js", "// dep\n"),
    ]:
        with open(os.path.join(root, rel), "w") as fh:
            fh.write(body)

    code, out, err = run("census", root, "--no-git")
    check("census exits 0", code == 0)
    check("census excludes node_modules via walk", "node_modules" not in out)
    check("census reports the unclassified file", "weird.xyz" in out)
    check("census counts source:go", "source:go" in out)

    code, out, err = run("census", root, "--no-git", "--json")
    check("census --json exits 0", code == 0)
    check("json manifest types the doc", '"docs"' in out and "docs/design.md" in out)

    # The fragment lives OUTSIDE the repo (recon writes to docs/reverse-engineer/, its
    # own workspace -- not part of the target inventory the census walks).
    with tempfile.TemporaryDirectory() as wsdir:
        # A fragment that references most files but misses weird.xyz and orders_test.go.
        frag = os.path.join(wsdir, "cart.md")
        with open(frag, "w") as fh:
            fh.write("Inventory: `pkg/orders.go`, `docs/design.md`, `go.mod`.\n")
        code, out, err = run("coverage", frag, root, "--no-git")
        check("coverage flags the unreferenced source test as UNCOVERED", "UNCOVERED  pkg/orders_test.go" in out)
        check("coverage flags weird.xyz", "weird.xyz" in out)
        check("coverage exits 1 when files are uncovered", code == 1)

        # Now cover everything (reference the dir prefixes + the stray file).
        with open(frag, "w") as fh:
            fh.write("Covers `pkg/`, `docs/`, `go.mod`, and excluded: `weird.xyz` (scratch).\n")
        code, out, err = run("coverage", frag, root, "--no-git")
        check("coverage exits 0 when every file is accounted for", code == 0)
        check("coverage prints no UNCOVERED when clean", "UNCOVERED" not in out)


print()
if _failures:
    print("%d FAILURE(S): %s" % (len(_failures), ", ".join(_failures)))
    sys.exit(1)
print("all checks passed")
sys.exit(0)
