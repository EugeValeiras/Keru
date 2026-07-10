#!/usr/bin/env python3
"""
repo-census.py -- deterministic, exhaustive file census + typed inventory for R1.

Mechanical companion to `system-cartography` (R1). It does the ONE part of the
cartography that is mechanical and must lose nothing: enumerate EVERY file in the
target repo and tag each with a category type, deterministically. It does NOT
interpret what a file means -- that stays judgment (the R1 producer walks the
census file-by-file to build the anchored cartograph). Census = mechanical =
script; interpretation = judgment = LLM. Never the reverse: a script that tried
to infer the architecture from file contents is exactly the confabulation recon
exists to prevent.

Two modes:

  census  <repo-root> [--json] [--no-git]
      Enumerate + type every file. Default source is `git ls-files` (tracked) +
      `git ls-files --others --exclude-standard` (untracked but not gitignored),
      so the census respects .gitignore and includes uncommitted-but-real files
      while excluding dependencies/build output. `--no-git` falls back to an
      os.walk with a fixed dependency-exclude list (use off a git repo). Output:
      a per-category count table (stdout); with `--json`, the full typed manifest
      (every path + its category) for a machine to track. Deterministic: same
      repo state -> identical, sorted output.

  coverage <fragment.md> <repo-root> [--no-git]
      The "nothing is lost" check. Re-runs the census, then for EVERY censused
      file confirms it is accounted for in the cartography fragment: its path (or
      an ancestor directory) is referenced in the fragment text -- inventoried, or
      listed in an explicit `## Census coverage` exclusions block with a reason. A
      file present in the repo but absent from the fragment is an UNCOVERED
      violation (exit 1). `unclassified` files are always listed -- they are the
      safety net: anything the ruleset could not type MUST be looked at by a human,
      never silently dropped.

Typing is a fixed, judgment-free ruleset (first match wins), so it is
deterministic, not an LLM call. Anything the ruleset does not recognise lands in
`unclassified` -- the bucket that guarantees nothing escapes unseen.

Read-only. Never writes. No third-party dependencies, no network.

Exit codes:
    census:    0 ok | 2 usage / IO error
    coverage:  0 every file covered | 1 uncovered file(s) | 2 usage / IO error
"""

import os
import re
import subprocess
import sys

# --- typing ruleset (extension / path -> category) -------------------------

SOURCE_EXT = {
    ".go": "go", ".js": "js", ".jsx": "js", ".mjs": "js", ".cjs": "js",
    ".ts": "ts", ".tsx": "ts", ".py": "python", ".cs": "csharp", ".java": "java",
    ".rb": "ruby", ".rs": "rust", ".kt": "kotlin", ".kts": "kotlin",
    ".c": "c", ".h": "c", ".cc": "cpp", ".cpp": "cpp", ".hpp": "cpp", ".cxx": "cpp",
    ".php": "php", ".swift": "swift", ".scala": "scala", ".sh": "shell", ".bash": "shell",
    ".m": "objc", ".mm": "objc", ".dart": "dart", ".ex": "elixir", ".exs": "elixir",
    ".clj": "clojure", ".vue": "js", ".svelte": "js",
    ".html": "html", ".htm": "html", ".css": "css", ".scss": "css",
    ".sass": "css", ".less": "css",
}
DOC_EXT = {".md", ".mdx", ".markdown", ".rst", ".adoc", ".asciidoc",
           ".puml", ".plantuml", ".http", ".rest"}
CONFIG_EXT = {".yaml", ".yml", ".json", ".toml", ".ini", ".env",
              ".conf", ".cfg", ".properties", ".xml"}
ASSET_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".pdf",
             ".woff", ".woff2", ".ttf", ".otf", ".eot", ".mp4", ".mov", ".mp3",
             ".zip", ".gz", ".tar", ".tgz", ".jar", ".war", ".exe", ".bin",
             ".so", ".dll", ".dylib", ".wasm", ".class", ".o", ".a"}
LOCK_NAMES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "go.sum",
              "Cargo.lock", "poetry.lock", "Gemfile.lock", "composer.lock"}
BUILD_NAMES = {"Makefile", "Jenkinsfile", "go.mod", "package.json", "pom.xml",
               "build.gradle", "build.gradle.kts", "settings.gradle",
               "pyproject.toml", "setup.py", "setup.cfg", "Cargo.toml", "Gemfile",
               "composer.json", "CMakeLists.txt", ".gitlab-ci.yml", ".travis.yml",
               "requirements.txt"}
BUILD_EXT = {".csproj", ".sln", ".vbproj", ".fsproj"}
IAC_SEGMENTS = {"k8s", "kubernetes", "helm", "charts", "terraform", "deploy", "manifests"}
IAC_EXT = {".tf", ".tfvars"}
IAC_NAMES = {"Chart.yaml", "kustomization.yaml", "values.yaml"}
TEST_SEGMENTS = {"test", "tests", "spec", "__tests__", "testdata", "fixtures"}
# Dependency / build-output / cache / tooling dirs that carry no system information.
# Excluded in BOTH modes (a repo may not .gitignore its build cache -- e.g. a
# committed-or-untracked `.cache/go-build/` -- so git mode applies this too, by the
# operator's "exclude deps" intent). Matched as a path segment. Deterministic list.
EXCLUDE_DIR_SEGMENTS = {".git", "node_modules", "vendor", "dist", "build", "out",
                        "bin", "obj", ".venv", "venv", "__pycache__", ".next",
                        ".nuxt", "target", ".idea", ".vscode", "coverage",
                        ".gradle", ".terraform", ".cache", ".gocache",
                        ".pytest_cache", ".mypy_cache", ".tox",
                        ".claude", ".cursor"}
# OS / VCS noise files: not information-bearing, excluded by basename.
# (These are excluded by POLICY -- they carry no system information -- not by
# necessity: PATH_TOKEN_RE now captures leading-dot tokens, so a dot-path left
# in-census, e.g. `.github/workflows/*`, is still coverable.)
EXCLUDE_NAMES = {".DS_Store", "Thumbs.db", ".gitkeep", ".keep",
                 ".gitignore", ".gitattributes", ".dockerignore", ".editorconfig"}


def is_excluded(rel):
    """True for dependency/build/cache/noise paths excluded from the census."""
    parts = rel.split("/")
    if parts[-1] in EXCLUDE_NAMES:
        return True
    return any(seg in EXCLUDE_DIR_SEGMENTS for seg in parts[:-1])


def classify(path):
    """Map a repo-relative path to a category. Deterministic; first match wins.

    Order is principled: hand-authored hard types keyed on the FILENAME / EXTENSION
    first (a `.sql` is schema, a `.png` is an asset, a `.md` is docs -- wherever it
    sits), then path-SEGMENT heuristics for files whose extension is ambiguous (a
    `.go` under `tests/` is a test; a `.yaml` under `k8s/` is deploy config).
    """
    path = path.replace("\\", "/")
    name = path.rsplit("/", 1)[-1]
    dot = name.rfind(".")
    if dot > 0:
        ext = name[dot:].lower()
    elif dot == 0 and name.count(".") == 1:
        ext = name.lower()           # pure dotfile, e.g. `.env`, `.gitignore`
    else:
        ext = ""
    dirsegs = path.split("/")[:-1]

    # 1. generated / lock -- never hand-authored
    if name in LOCK_NAMES or ext == ".lock" or name.endswith(".min.js") or name.endswith(".map"):
        return "generated-lock"
    # 2. build / CI / packaging (name- and path-keyed; e.g. package.json over config)
    if ".github/workflows/" in path or name in BUILD_NAMES or ext in BUILD_EXT \
            or name.startswith("Dockerfile") or name.startswith("docker-compose"):
        return "build-ci"
    # 3. documentation / intent -- by extension or doc filename (wherever it sits)
    if ext in DOC_EXT or name in ("README", "CHANGELOG", "LICENSE", "AGENTS.md", "CLAUDE.md", "NOTICE"):
        return "docs"
    # 4. schema / migration -- by extension
    if ext in (".sql", ".proto"):
        return "schema-migration"
    # 5. binary / asset -- by extension (a .png in docs/ is still an asset)
    if ext in ASSET_EXT:
        return "asset-binary"
    # 6. test -- path segment or filename convention (before source)
    if any(s in TEST_SEGMENTS for s in dirsegs) \
            or re.search(r"(_test|_spec)\.[A-Za-z0-9]+$", name) \
            or re.search(r"\.(test|spec)\.[A-Za-z0-9]+$", name) \
            or name.startswith("test_"):
        return "test"
    # 7. infra-as-code / deploy -- by path segment / .tf / iac filename
    if any(s in IAC_SEGMENTS for s in dirsegs) or ext in IAC_EXT or name in IAC_NAMES:
        return "iac-deploy"
    # 8. documentation by directory (a non-doc-ext note living under docs/)
    if "docs" in dirsegs:
        return "docs"
    # 9. schema / migration by directory
    if any(s in ("migrations", "migrate") for s in dirsegs):
        return "schema-migration"
    # 10. source code -- by extension
    if ext in SOURCE_EXT:
        return "source:" + SOURCE_EXT[ext]
    # 11. config / data -- by extension
    if ext in CONFIG_EXT:
        return "config"
    # 12. anything else -- the safety net that loses nothing
    return "unclassified"


# --- enumeration -----------------------------------------------------------

def git_files(root):
    """Tracked + untracked-not-ignored files, via git. None if not a git repo."""
    def run(args):
        return subprocess.run(["git", "-C", root] + args,
                              capture_output=True, text=True)
    inside = run(["rev-parse", "--is-inside-work-tree"])
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return None
    out = set()
    for args in (["ls-files"], ["ls-files", "--others", "--exclude-standard"]):
        p = run(args)
        if p.returncode != 0:
            return None
        out.update(line for line in p.stdout.splitlines() if line)
    return sorted(f for f in out if not is_excluded(f))


def walk_files(root):
    """Fallback enumeration: os.walk with the fixed dependency-exclude list."""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIR_SEGMENTS]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace("\\", "/")
            if not is_excluded(rel):
                out.append(rel)
    return sorted(out)


def list_repo_files(root, use_git=True):
    """Repo-relative file list, sorted. Git source preferred; walk fallback."""
    if use_git:
        g = git_files(root)
        if g is not None:
            return g, "git"
    return walk_files(root), "walk"


def census(files):
    """category -> sorted list of paths."""
    out = {}
    for f in files:
        out.setdefault(classify(f), []).append(f)
    return out


# --- coverage --------------------------------------------------------------

# A path-like token: an optional leading dot (so `.github/...` / `.gitignore` are
# captured and thus coverable), then a word char, then word/./-//. Excludes ':'
# so a `file.go:42` anchor yields `file.go`, not `file.go:42`. The optional dot
# needs a word char after it, so prose ellipses (`...`) never match.
PATH_TOKEN_RE = re.compile(r"\.?[A-Za-z0-9_][\w./-]*")


def referenced_paths(text):
    """The set of path-like tokens the fragment mentions (anchors, dir refs)."""
    return set(PATH_TOKEN_RE.findall(text))


def _covered_by_tokens(path, tokens):
    """Covered iff a token equals the file or names an ancestor directory of it.

    Directory coverage is by genuine path-prefix (token `pkg/` or `pkg` covers
    `pkg/orders.go`), NOT loose substring -- so a deep reference like
    `services/market-order` does NOT spuriously cover the sibling `services/risk`.
    """
    if path in tokens:
        return True
    for t in tokens:
        d = t[:-1] if t.endswith("/") else t
        if d and path.startswith(d + "/"):
            return True
    return False


def is_covered(path, text):
    """A file is covered if its path or an ancestor directory is named in text."""
    return _covered_by_tokens(path, referenced_paths(text))


def uncovered(files, text):
    """Files present in the repo but not accounted for in the fragment text."""
    tokens = referenced_paths(text)
    return [f for f in files if not _covered_by_tokens(f, tokens)]


# --- cli -------------------------------------------------------------------

def _ordered_categories(cen):
    # source:* grouped together, then the rest alphabetically, unclassified last.
    keys = sorted(cen.keys())
    src = [k for k in keys if k.startswith("source:")]
    rest = [k for k in keys if not k.startswith("source:") and k != "unclassified"]
    tail = ["unclassified"] if "unclassified" in cen else []
    return src + rest + tail


def cmd_census(root, as_json, use_git):
    files, source = list_repo_files(root, use_git)
    cen = census(files)
    if as_json:
        import json
        manifest = {
            "source": source,
            "total": len(files),
            "counts": {k: len(v) for k, v in cen.items()},
            "files": {f: classify(f) for f in files},
        }
        print(json.dumps(manifest, indent=2, sort_keys=True))
    else:
        print("repo census (%s) -- %d files" % (source, len(files)))
        for cat in _ordered_categories(cen):
            print("  %5d  %s" % (len(cen[cat]), cat))
        if "unclassified" in cen:
            print("\nunclassified (MUST be reviewed -- nothing is dropped):")
            for f in cen["unclassified"]:
                print("  %s" % f)
    sys.stderr.write("censused %d files across %d categories (source: %s)\n"
                     % (len(files), len(cen), source))
    return 0


def cmd_coverage(fragment, root, use_git):
    try:
        with open(fragment, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError as exc:
        sys.stderr.write("cannot read fragment: %s\n" % exc)
        return 2
    files, source = list_repo_files(root, use_git)
    miss = uncovered(files, text)
    cen = census(files)
    unclassified = cen.get("unclassified", [])
    for f in miss:
        print("UNCOVERED  %s  (%s)  not referenced in fragment" % (f, classify(f)))
    for f in unclassified:
        if f not in miss:
            print("REVIEW     %s  unclassified -- confirm it carries nothing for the inventory" % f)
    sys.stderr.write(
        "coverage: %d censused (%s), %d uncovered, %d unclassified\n"
        % (len(files), source, len(miss), len(unclassified))
    )
    return 1 if miss else 0


def main(argv):
    if len(argv) < 2:
        sys.stderr.write(
            "usage: repo-census.py census <repo-root> [--json] [--no-git]\n"
            "       repo-census.py coverage <fragment.md> <repo-root> [--no-git]\n")
        return 2
    mode = argv[1]
    rest = argv[2:]
    use_git = "--no-git" not in rest
    as_json = "--json" in rest
    pos = [a for a in rest if not a.startswith("--")]

    if mode == "census":
        if len(pos) != 1:
            sys.stderr.write("usage: repo-census.py census <repo-root> [--json] [--no-git]\n")
            return 2
        if not os.path.isdir(pos[0]):
            sys.stderr.write("repo-root is not a directory: %s\n" % pos[0])
            return 2
        return cmd_census(pos[0], as_json, use_git)

    if mode == "coverage":
        if len(pos) != 2:
            sys.stderr.write("usage: repo-census.py coverage <fragment.md> <repo-root> [--no-git]\n")
            return 2
        if not os.path.isdir(pos[1]):
            sys.stderr.write("repo-root is not a directory: %s\n" % pos[1])
            return 2
        return cmd_coverage(pos[0], pos[1], use_git)

    sys.stderr.write("unknown mode %r -- use census | coverage\n" % mode)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
