#!/usr/bin/env python3
"""
check-workspace.py -- deterministic enforcer of the recon WORKSPACE FOLDER RULE.

The fourth mechanical companion (after check-anchors.py, repo-census.py,
check-counts.py). It closes a structural BLIND SPOT introduced when the recon
flow moved out of docs/architecture/ into its own role folder
docs/reverse-engineer/ (0.1.8): which directory each recon artifact belongs in
was left as PROSE -- restated across ~11 files and guarded only by the hope that
the Reverse-Engineer subagent "does not correct the path back to
docs/architecture/". Prose is non-deterministic; a misplaced FLOW.md or
audit-iter-N.md under docs/architecture/ collides by name with the SAD
deliverable, and nothing mechanical catches it.

The rule is simple and binary, so it is a SCRIPT, not prose (RE-05 workspace
coherence; SKILL.md "Doctrine: mechanical determinism"):

    Recon writes its WHOLE flow -- the FLOW.md tracker, the four R1-R4
    fragments, the r1-inventory.json census manifest, the audit reports, and
    the phase0-evidence.md bundle -- ONLY under <root>/docs/reverse-engineer/.
    docs/architecture/ is reserved for the downstream SAD deliverable; recon
    never writes there.

check-workspace.py walks <root>/docs/ and flags every recon-OWNED artifact
(matched by canonical basename) that does NOT live under docs/reverse-engineer/.
A recon artifact under docs/architecture/ (or sitting loose elsewhere in docs/)
is a deterministic MISPLACED violation. The SAD's own files in docs/architecture/
are not recon-owned, so they are ignored. Same input (file tree) -> same output,
so this is mechanical, not judgment. Read-only: no writes, no network, no shell.

Usage:
    check-workspace.py <repo-root>

Exit codes:
    0  every recon artifact lives under docs/reverse-engineer/ (or none exist)
    1  one or more recon artifacts are misplaced (outside docs/reverse-engineer/)
    2  usage / IO error
"""

import os
import sys

# The recon role's own workspace folder. Everything recon writes lives here.
RECON_WORKSPACE = os.path.join("docs", "reverse-engineer")

# Canonical recon-owned artifact basenames (exact match).
RECON_FILES = {
    "FLOW.md",                          # the gate tracker
    "system-cartography.md",            # R1 fragment
    "behavior-reconstruction.md",       # R2 fragment
    "reconstructed-business-view.md",   # R3 fragment
    "asbuilt-stressors.md",             # R4 fragment
    "phase0-evidence.md",               # handoff bundle
    "r1-inventory.json",                # R1 typed census manifest
}
# Recon-owned artifact basename PREFIXES (audit reports are numbered / ref'd):
# audit-iter-<N>.md (by-gate / end-to-end) and audit-drift-<ref>.md (diff mode).
RECON_PREFIXES = ("audit-iter-", "audit-drift-")


def is_recon_artifact(basename):
    """True if a basename is a recon-owned artifact (exact name or audit prefix)."""
    if basename in RECON_FILES:
        return True
    if basename.endswith(".md") and basename.startswith(RECON_PREFIXES):
        return True
    return False


def find_misplaced(repo_root):
    """Return sorted repo-relative paths of recon artifacts outside the workspace.

    Walks <repo_root>/docs/. A recon-owned artifact whose path is not under
    docs/reverse-engineer/ is misplaced (the canonical violation is one sitting
    under docs/architecture/, the SAD's tree). The workspace subtree itself is
    skipped wholesale.
    """
    docs_root = os.path.join(repo_root, "docs")
    workspace = os.path.join(repo_root, RECON_WORKSPACE)
    misplaced = []
    for dirpath, _dirs, files in os.walk(docs_root):
        # Skip the legitimate workspace subtree entirely.
        if dirpath == workspace or dirpath.startswith(workspace + os.sep):
            continue
        for fn in files:
            if is_recon_artifact(fn):
                full = os.path.join(dirpath, fn)
                misplaced.append(os.path.relpath(full, repo_root))
    return sorted(misplaced)


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: check-workspace.py <repo-root>\n")
        return 2
    repo_root = argv[1]
    if not os.path.isdir(repo_root):
        sys.stderr.write("repo-root is not a directory: %s\n" % repo_root)
        return 2

    docs_root = os.path.join(repo_root, "docs")
    if not os.path.isdir(docs_root):
        # No docs/ tree at all -> nothing recon could have misplaced.
        sys.stderr.write("no docs/ directory -- nothing to check\n")
        return 0

    workspace = RECON_WORKSPACE.replace(os.sep, "/")
    misplaced = find_misplaced(repo_root)
    for rel in misplaced:
        print("MISPLACED  %s -- recon artifact must live under %s/, not elsewhere in docs/"
              % (rel.replace(os.sep, "/"), workspace))

    sys.stderr.write(
        "checked docs/ -- %d misplaced recon artifact(s); workspace is %s/\n"
        % (len(misplaced), workspace)
    )
    return 1 if misplaced else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
