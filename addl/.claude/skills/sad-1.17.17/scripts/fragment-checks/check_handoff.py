#!/usr/bin/env python3
"""check_handoff.py -- deterministic RDAG handoff-conformance reconciliation.

The S8 speckit-handoff emits a handoff directory (`handoff/arch-X.Y.Z/`): a
handoff-manifest plus the Tier-1 artifacts a Spec-Driven-Development consumer
reads (service-catalog, nfr-register, use-cases, binding ADRs). Conformance to
the RDAG standard (sdd-interface/standard/rdag-conformance.md) is otherwise
checked by prose CHK-NN review, so a count that drifts from its source list --
the manifest's artifact inventory not matching the files actually emitted, a
recited service/binding-ADR count not matching the enumerated rows, a binding
ADR not locatable -- slips past silently. Those reconciliations are mechanical
and deterministic, so they are a script, not LLM prose
(shared/mechanical-determinism-snippet.md).

It is **self-contained over the emitted artifact set**: it never opens the
upstream SAD. It makes the *deterministic subset* of CHK-11 / CHK-12 / CHK-14
mechanical:

  - inventory <-> files: every inventoried `architecture/` artifact exists in
    the handoff dir, and every emitted Tier-1 artifact file is inventoried
    (handoff-manifest-contract sect.3 "the landing-zone map"; CHK-11).
  - recited counts: any "N services" / "N binding ADRs" recited in the manifest
    equals the corresponding enumerated tally (CHK-14 coherence).
  - service-catalog internal count: a service count recited in the catalog or
    manifest equals the catalog's `#### service` entries.
  - binding ADRs locatable: every ADR enumerated in the manifest Binding-ADRs
    table resolves to a `decisions/ADR-*.md` file (CHK-12 deterministic core).

  check_handoff.py <handoff-dir>          # exit 1 + report on any mismatch
  check_handoff.py --self-test            # built-in regression checks

Design principle: HIGH PRECISION, ZERO FALSE POSITIVES. A check fires only when
BOTH sides parse confidently in a recognized pattern; anything it cannot parse
is left silent (it is not the gate's job to guess). Stdlib only, US-ASCII.
"""

import argparse
import os
import re
import sys


class Finding:
    def __init__(self, section, msg):
        self.section, self.msg = section, msg

    def __str__(self):
        return f"HANDOFF MISMATCH [{self.section}]: {self.msg}"


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------

def _cells(line):
    """Pipe-row -> list of stripped, bold-stripped cells (edges dropped)."""
    parts = [c.strip().strip("*").strip() for c in line.split("|")]
    if parts and parts[0] == "":
        parts = parts[1:]
    if parts and parts[-1] == "":
        parts = parts[:-1]
    return parts


def _is_sep(cell):
    return bool(cell) and set(cell) <= set("-:")


# The release-directory prefix a landing zone carries in the manifest, e.g.
# `architecture/arch-1.0.0/system-design/service-catalog.md`. We strip it to get
# the path relative to the handoff dir (which *is* the `arch-X.Y.Z/` directory).
_ARCH_PREFIX = re.compile(r"^architecture/arch-\d+\.\d+\.\d+/")
_BACKTICK_PATH = re.compile(r"`([^`]+)`")


# --------------------------------------------------------------------------
# manifest parsing
# --------------------------------------------------------------------------

def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _section(md, name):
    """Return the body of a `## <name>` section, or '' if absent."""
    m = re.search(rf"^##\s+{re.escape(name)}\b.*$", md, re.M)
    if not m:
        return ""
    body = md[m.end():]
    nxt = re.search(r"^##\s+\S", body, re.M)
    return body[:nxt.start()] if nxt else body


def parse_inventory(manifest):
    """Return the list of in-handoff relative paths the Artifact-inventory
    table declares (only landing zones under the release directory; the
    constitution-principle entry that lands at `.specify/` is excluded). High
    precision: only `architecture/arch-X.Y.Z/...` backticked paths are taken."""
    body = _section(manifest, "Artifact inventory")
    paths = []
    for line in body.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = _cells(line)
        if len(cells) < 2 or _is_sep(cells[0]):
            continue
        if cells[0].lower() in ("artifact",):  # header row
            continue
        rel = None
        for c in cells[1:]:
            for m in _BACKTICK_PATH.finditer(c):
                cand = m.group(1).strip()
                if _ARCH_PREFIX.match(cand):
                    rel = _ARCH_PREFIX.sub("", cand)
                    break
            if rel:
                break
        if rel:
            paths.append(rel)
    return paths


def _emitted_artifact_files(handoff_dir):
    """The Tier-1 artifact files actually present in the handoff dir, as paths
    relative to it. Tier-1 = the release-directory artifacts: system-design/
    register + catalog, use-cases/, decisions/. The integration/ inputs (drop-in
    principle, scaffold, gate wiring, sync report) are NOT Tier-1 inventory rows,
    so they are excluded."""
    found = []
    for sub in ("system-design", "use-cases", "decisions"):
        d = os.path.join(handoff_dir, sub)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name.endswith(".md"):
                found.append(f"{sub}/{name}")
    return found


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

def check_inventory_files(handoff_dir, manifest):
    """Inventory <-> files present, both directions (CHK-11 / contract sect.3)."""
    findings = []
    inv = parse_inventory(manifest)
    if not inv:
        return findings  # no parseable inventory -> nothing to reconcile
    inv_set = set(inv)
    # (a) every inventoried artifact exists on disk
    for rel in inv:
        if not os.path.isfile(os.path.join(handoff_dir, rel)):
            findings.append(Finding(
                "inventory -> files",
                f"manifest inventories `{rel}` but no such file exists in the "
                f"handoff dir"))
    # (b) every emitted Tier-1 artifact file is inventoried
    for rel in _emitted_artifact_files(handoff_dir):
        if rel not in inv_set:
            findings.append(Finding(
                "files -> inventory",
                f"`{rel}` is emitted in the handoff dir but is not listed in "
                f"the manifest Artifact inventory"))
    return findings


def _table_rows(body, header_first_cell):
    """Return the data rows of the first table whose header's first cell matches
    `header_first_cell` (case-insensitive). None if no such table."""
    in_table = False
    rows = []
    for line in body.splitlines():
        if not line.lstrip().startswith("|"):
            if in_table:
                break
            continue
        cells = _cells(line)
        if not cells:
            continue
        if not in_table:
            if cells[0].lower() == header_first_cell.lower():
                in_table = True
            continue
        if _is_sep(cells[0]):
            continue
        rows.append(cells)
    if not in_table:
        return None
    return rows


def check_binding_adrs(handoff_dir, manifest):
    """Binding-ADRs enumerated in the manifest are all locatable as
    decisions/ADR-*.md files (CHK-12 deterministic core), and any recited
    "N binding ADRs" count equals the table tally (CHK-14)."""
    findings = []
    body = _section(manifest, "Binding ADRs")
    if not body:
        return findings
    rows = _table_rows(body, "ADR")
    if rows is None:
        return findings
    adr_ids = []
    for r in rows:
        m = re.search(r"\bADR-\d+\b", r[0])
        if m:
            adr_ids.append(m.group())
    if not adr_ids:
        return findings  # no confidently-parsed ADR ids -> silent
    # (a) each enumerated binding ADR resolves to a decisions/ file
    dec_dir = os.path.join(handoff_dir, "decisions")
    present = set()
    if os.path.isdir(dec_dir):
        for name in os.listdir(dec_dir):
            for m in re.finditer(r"\bADR-\d+\b", name):
                present.add(m.group())
    for adr in adr_ids:
        if adr not in present:
            findings.append(Finding(
                "binding ADRs locatable",
                f"manifest enumerates binding ADR {adr} but no matching "
                f"decisions/ADR-*.md file exists in the handoff dir"))
    # (b) a recited "N binding ADRs" count == enumerated table rows
    for m in re.finditer(r"(\d+)\s+binding\s+ADRs?\b", manifest, re.I):
        if int(m.group(1)) != len(adr_ids):
            findings.append(Finding(
                "binding ADRs count",
                f"prose says {m.group(1)} binding ADRs but the Binding-ADRs "
                f"table enumerates {len(adr_ids)}"))
    return findings


# A catalog service entry: a level-4 heading naming a Lowy-suffixed service in
# backticks, e.g. "#### `ChargeSessionManager`". The suffix anchor keeps it from
# matching narrative `####` headings.
_SVC_ENTRY = re.compile(
    r"^####\s+`?[A-Za-z][A-Za-z0-9]*(Manager|Engine|Access)`?\s*$", re.M)


def _catalog_service_count(catalog):
    return len(_SVC_ENTRY.findall(catalog))


def check_service_count(handoff_dir, manifest):
    """Any recited "N services" count (in the catalog or the manifest) equals
    the catalog's `#### <Lowy-suffixed service>` entry tally (CHK-14)."""
    findings = []
    cat_path = os.path.join(handoff_dir, "system-design", "service-catalog.md")
    if not os.path.isfile(cat_path):
        return findings
    catalog = _read(cat_path)
    n = _catalog_service_count(catalog)
    if n == 0:
        return findings  # no confidently-parsed service entries -> silent
    pat = re.compile(r"(\d+)\s+services\b", re.I)
    for src_name, text in (("service-catalog", catalog), ("handoff-manifest", manifest)):
        for m in pat.finditer(text):
            # skip future/anticipated-services phrasings (the catalog lists them)
            pre = text[max(0, m.start() - 24):m.start()].lower()
            if "future" in pre or "anticipat" in pre:
                continue
            if int(m.group(1)) != n:
                findings.append(Finding(
                    "service count",
                    f"{src_name} says {m.group(1)} services but the catalog "
                    f"enumerates {n} `####` service entries"))
    return findings


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------

ALL_CHECKS = [check_inventory_files, check_binding_adrs, check_service_count]


def run(handoff_dir):
    manifest_path = os.path.join(handoff_dir, "handoff-manifest.md")
    if not os.path.isfile(manifest_path):
        return None  # not a handoff dir
    manifest = _read(manifest_path)
    findings, seen = [], set()
    for chk in ALL_CHECKS:
        for f in chk(handoff_dir, manifest):
            key = (f.section, f.msg)
            if key not in seen:
                seen.add(key)
                findings.append(f)
    return findings


def _run_dir(path):
    findings = run(path)
    if findings is None:
        print(f"HANDOFF CHECK SKIPPED: no handoff-manifest.md in {path} "
              f"(not a handoff dir).")
        return 0
    if findings:
        print(f"HANDOFF CHECK FAILED: {len(findings)} reconciliation "
              f"mismatch(es) in {path}:")
        for f in findings:
            print(f"  - {f}")
        print("Fix: align the manifest inventory / recited counts with the "
              "files and tables actually emitted, or emit the missing artifact.")
        return 1
    print(f"HANDOFF CHECK OK: the manifest, inventory, counts, and binding "
          f"ADRs in {path} all reconcile with the emitted artifact set.")
    return 0


# --------------------------------------------------------------------------
# self-test (in-memory temp dirs; no dependency on files on disk)
# --------------------------------------------------------------------------

def _self_test():
    import tempfile
    import pathlib

    def build(d, *, manifest, catalog=None, use_cases=None, adrs=None):
        root = pathlib.Path(d)
        (root / "handoff-manifest.md").write_text(manifest, encoding="utf-8")
        sd = root / "system-design"
        sd.mkdir()
        if catalog is not None:
            (sd / "service-catalog.md").write_text(catalog, encoding="utf-8")
        (sd / "nfr-register.md").write_text("# NFR Register\n", encoding="utf-8")
        uc = root / "use-cases"
        uc.mkdir()
        for name in (use_cases or ["uc-001-x.md"]):
            (uc / name).write_text("# UC\n", encoding="utf-8")
        dec = root / "decisions"
        dec.mkdir()
        for name in (adrs or ["ADR-001.md"]):
            (dec / name).write_text("# ADR\n", encoding="utf-8")

    GOOD_INV = (
        "## Artifact inventory\n\n"
        "| Artifact | Landing zone (consumer path) | Version |\n"
        "|---|---|---|\n"
        "| service-catalog | `architecture/arch-1.0.0/system-design/service-catalog.md` | arch 1.0.0 |\n"
        "| nfr-register | `architecture/arch-1.0.0/system-design/nfr-register.md` | arch 1.0.0 |\n"
        "| use-case UC-001 | `architecture/arch-1.0.0/use-cases/uc-001-x.md` | arch 1.0.0 |\n"
        "| ADR-001 | `architecture/arch-1.0.0/decisions/ADR-001.md` | arch 1.0.0 |\n"
        "| constitution principle | `.specify/memory/constitution.md` | RDAG 0.1.0 |\n\n"
    )
    GOOD_BIND = (
        "## Binding ADRs\n\n"
        "| ADR | Claims | Constrains |\n|---|---|---|\n"
        "| ADR-001 | x | y |\n\n"
    )
    GOOD_MANIFEST = "# Handoff Manifest\n\n" + GOOD_INV + GOOD_BIND
    GOOD_CATALOG = (
        "# Service Catalog\n\n## Catalog Entries\n\n### Managers\n\n"
        "#### `ChargeSessionManager`\n| Field | Value |\n|---|---|\n"
        "### Engines\n\n#### `AuthEngine`\n| Field | Value |\n|---|---|\n"
        "### ResourceAccess\n\n#### `CustomerAccess`\n| Field | Value |\n|---|---|\n"
    )  # 3 service entries

    failures = []

    def expect(label, findings, want):
        got = sorted(str(f) for f in findings)
        if want == "silent":
            if got:
                failures.append(f"{label}: expected silent, got {got}")
        else:
            if not any(want in g for g in got):
                failures.append(f"{label}: expected a finding containing "
                                f"'{want}', got {got}")

    # (1) fully coherent handoff -> silent
    with tempfile.TemporaryDirectory() as d:
        build(d, manifest=GOOD_MANIFEST, catalog=GOOD_CATALOG)
        expect("coherent handoff", run(d), "silent")

    # (2) inventoried file missing on disk (UC inventoried but not written)
    with tempfile.TemporaryDirectory() as d:
        bad = GOOD_MANIFEST.replace("uc-001-x.md", "uc-099-missing.md")
        build(d, manifest=bad, catalog=GOOD_CATALOG)
        expect("inventory -> files", run(d), "uc-099-missing.md")

    # (3) emitted file not inventoried (an extra UC on disk, not in inventory)
    with tempfile.TemporaryDirectory() as d:
        build(d, manifest=GOOD_MANIFEST, catalog=GOOD_CATALOG,
              use_cases=["uc-001-x.md", "uc-002-extra.md"])
        expect("files -> inventory", run(d), "uc-002-extra.md")

    # (4) binding ADR enumerated but no decisions/ file
    with tempfile.TemporaryDirectory() as d:
        bad = GOOD_MANIFEST.replace(
            "| ADR-001 | x | y |",
            "| ADR-001 | x | y |\n| ADR-007 | p | q |")
        bad = bad.replace(
            "| ADR-001 | `architecture/arch-1.0.0/decisions/ADR-001.md` | arch 1.0.0 |\n",
            "| ADR-001 | `architecture/arch-1.0.0/decisions/ADR-001.md` | arch 1.0.0 |\n"
            "| ADR-007 | `architecture/arch-1.0.0/decisions/ADR-007.md` | arch 1.0.0 |\n")
        # ADR-007 enumerated + inventoried, but its file is NOT emitted
        build(d, manifest=bad, catalog=GOOD_CATALOG, adrs=["ADR-001.md"])
        expect("binding ADRs locatable", run(d), "binding ADR ADR-007")

    # (5) recited "N binding ADRs" mismatches the table
    with tempfile.TemporaryDirectory() as d:
        bad = GOOD_MANIFEST + "\nThis handoff carries 3 binding ADRs.\n"
        build(d, manifest=bad, catalog=GOOD_CATALOG)
        expect("binding ADRs count", run(d), "3 binding ADRs but")

    # (6) recited "N services" mismatches the catalog entry tally
    with tempfile.TemporaryDirectory() as d:
        bad = GOOD_MANIFEST + "\nThe catalog defines 5 services.\n"
        build(d, manifest=bad, catalog=GOOD_CATALOG)
        expect("service count", run(d), "5 services but")

    # (7) a correct "N services" recital is silent; "future services" is ignored
    with tempfile.TemporaryDirectory() as d:
        ok = (GOOD_MANIFEST + "\nThe catalog defines 3 services.\n"
              "There are 9 anticipated future services not yet authorized.\n")
        build(d, manifest=ok, catalog=GOOD_CATALOG)
        expect("service count correct + future-skipped", run(d), "silent")

    # (8) not a handoff dir -> run() returns None (skipped, exit 0)
    with tempfile.TemporaryDirectory() as d:
        if run(d) is not None:
            failures.append("non-handoff dir: expected run() to return None")

    if failures:
        print("SELF-TEST FAILED:")
        for f in failures:
            print("  - " + f)
        return 1
    print("SELF-TEST PASSED")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Reconcile a handoff dir's manifest/inventory/counts/binding-ADRs "
                    "against the emitted artifact set.")
    ap.add_argument("path", nargs="?", help="path to a handoff dir (arch-X.Y.Z/)")
    ap.add_argument("--self-test", action="store_true",
                    help="run built-in regression checks")
    args = ap.parse_args(argv)
    if args.self_test:
        return _self_test()
    if not args.path:
        ap.error("a handoff-dir path is required (or use --self-test)")
    return _run_dir(args.path)


if __name__ == "__main__":
    sys.exit(main())
