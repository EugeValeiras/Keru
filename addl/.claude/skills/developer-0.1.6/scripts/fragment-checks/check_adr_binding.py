#!/usr/bin/env python3
"""check_adr_binding.py -- D1 handoff-form validation for binding ADRs (CHK-12).

Q6 (binding-ADR conformance) can only be meaningful if every binding ADR carries a
populated, evaluable "Conformance check" condition AND is enumerable from the
handoff manifest. If a future release ships a `Binding: Yes` ADR with an empty
Conformance check, Q6 has nothing to evaluate; if a binding ADR is not listed in
the manifest, the gate cannot enumerate it (CHK-12). This check makes D1 reject
either malformation up front -- the hard half of the Architect <-> Developer ADR seam.

Per adr-contract.md S3, a `## Binding scope` table with `Binding: Yes` MUST carry
non-empty `Claims`, `Constrains`, and `Conformance check`. Per S6 / CHK-12, every
binding ADR is listed in the manifest's `## Binding ADRs` table (and every listed
ADR exists and is binding).

    check_adr_binding.py architecture/arch-X.Y.Z/

Exit codes:  0 every binding ADR well-formed + enumerated / 1 malformed (gate blocked)
             2 usage error
Stdlib-only. Self-test:  check_adr_binding.py --self-test
"""

import argparse
import glob
import os
import re
import sys

OK, FINDINGS, ERROR = 0, 1, 2

H2_RE = re.compile(r"^##\s+(.*\S)\s*$")
ADR_RE = re.compile(r"\bADR-\d{2,}\b")
_PLACEHOLDER_RE = re.compile(r"^[\[(<].*[\])>]$")


def _section(text, title_lower):
    """Body under the first '## <title>' (case-insensitive), to the next '## '."""
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        m = H2_RE.match(ln)
        if m and m.group(1).strip().lower() == title_lower:
            start = i + 1
            break
    if start is None:
        return None
    body = []
    for ln in lines[start:]:
        if H2_RE.match(ln):
            break
        body.append(ln)
    return "\n".join(body)


def _cells(row):
    r = row.strip()
    if r.startswith("|"):
        r = r[1:]
    if r.endswith("|"):
        r = r[:-1]
    return [c.strip() for c in r.split("|")]


def parse_binding_scope(adr_text):
    """Field -> value from the '## Binding scope' table (field names lowercased,
    markdown emphasis stripped). Empty dict if the section is absent."""
    body = _section(adr_text, "binding scope")
    out = {}
    if body is None:
        return out
    for ln in body.splitlines():
        if not ln.strip().startswith("|"):
            continue
        cells = _cells(ln)
        if len(cells) < 2:
            continue
        field = cells[0].replace("*", "").replace("`", "").strip().lower()
        if not field or field == "field" or set(cells[0]) <= set("-: "):
            continue
        out[field] = cells[1].strip()
    return out


def _empty_or_placeholder(v):
    v = v.strip()
    if not v:
        return True
    if _PLACEHOLDER_RE.match(v):
        return True
    if v.lower() in ("todo", "tbd", "n/a", "na", "none", "...", "-", "--"):
        return True
    return bool(re.search(r"\b(tbd|todo)\b", v, re.I))


_VAGUE_PHRASES = (
    "should be fine", "as appropriate", "as needed", "to be defined", "to be determined",
    "handled appropriately", "make sense", "makes sense", "best effort", "reasonable",
    "where applicable", "if needed", "etc.",
)


def _vague_conformance(v):
    """A partial heuristic: a Conformance check must be evaluable (Q6 answers yes/no).
    Reject the obviously-vague (too short / hedge phrases). Full semantic evaluability
    is not deterministically decidable -- this is a mitigation, not a guarantee."""
    s = v.strip()
    if len(s) < 20:
        return True
    low = s.lower()
    return any(p in low for p in _VAGUE_PHRASES)


def parse_manifest_binding(manifest_text):
    """Set of ADR ids listed in the manifest's '## Binding ADRs' TABLE (first cell of
    each data row). The gate enumerates from the table, so a bare prose mention of an
    ADR id under the section does NOT count as enumeration (adr-contract S6 / CHK-12)."""
    body = _section(manifest_text, "binding adrs")
    if body is None:
        return set()
    ids = set()
    for line in body.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        first = _cells(s)[0] if _cells(s) else ""
        if first.lower() == "adr" or set(first) <= set("-: "):
            continue
        m = ADR_RE.search(first)
        if m:
            ids.add(m.group(0))
    return ids


def check(adrs, manifest_text):
    """adrs: {adr_id: text}. Returns findings list."""
    findings = []
    binding_yes = set()
    for aid, text in sorted(adrs.items()):
        fields = parse_binding_scope(text)
        if not fields:
            continue  # not an ADR with a Binding scope section; skip
        if fields.get("binding", "").strip().lower() != "yes":
            continue
        binding_yes.add(aid)
        for req in ("claims", "constrains"):
            if _empty_or_placeholder(fields.get(req, "")):
                findings.append("%s is Binding: Yes but its '%s' field is empty or a placeholder "
                                "(adr-contract S3)" % (aid, req.title()))
        conf = fields.get("conformance check", "")
        if _empty_or_placeholder(conf):
            findings.append("%s is Binding: Yes but its 'Conformance check' is empty or a placeholder "
                            "(adr-contract S3; Q6 cannot evaluate it)" % aid)
        elif _vague_conformance(conf):
            findings.append("%s 'Conformance check' is too vague for Q6 to answer yes/no: %r" % (aid, conf))

    listed = parse_manifest_binding(manifest_text)
    for aid in sorted(binding_yes - listed):
        findings.append("binding %s is not listed in the manifest's 'Binding ADRs' table "
                        "(CHK-12: the gate enumerates binding ADRs from the manifest)" % aid)
    for aid in sorted(listed):
        if aid not in adrs:
            findings.append("the manifest lists binding %s but decisions/%s.md is missing" % (aid, aid))
        elif aid not in binding_yes:
            findings.append("the manifest lists %s as binding but its ADR is not 'Binding: Yes'" % aid)
    return findings


def scan_decisions(files):
    """files: [(basename, text)] -> (adrs{id:text}, findings). Flags an ADR-looking file
    with no well-formed ADR-NNN id, and two files resolving to the same id (which would
    otherwise overwrite silently, hiding a binding/CHK-13 issue)."""
    adrs, findings = {}, []
    for base, text in files:
        m = ADR_RE.search(base) or ADR_RE.search(text)
        if not m:
            if "adr" in base.lower():
                findings.append("decisions/%s has no well-formed ADR-NNN id (adr-contract / CHK-13)" % base)
            continue
        aid = m.group(0)
        if aid in adrs:
            findings.append("duplicate ADR id %s -- two files in decisions/ resolve to it (CHK-13 append-only)" % aid)
        else:
            adrs[aid] = text
    return adrs, findings


def run(arch_dir):
    decisions_dir = os.path.join(arch_dir, "decisions")
    manifest_path = os.path.join(arch_dir, "handoff-manifest.md")
    files = []
    if os.path.isdir(decisions_dir):
        for p in sorted(glob.glob(os.path.join(decisions_dir, "*.md"))):
            with open(p, encoding="utf-8") as fh:
                files.append((os.path.basename(p), fh.read()))
    adrs, extra = scan_decisions(files)
    manifest_text = ""
    if os.path.isfile(manifest_path):
        with open(manifest_path, encoding="utf-8") as fh:
            manifest_text = fh.read()
    return check(adrs, manifest_text) + extra, len(adrs)


def report(findings, n_adrs, arch_dir):
    print("Binding-ADR handoff-form validation (CHK-12) -- D1")
    print("  release: %s" % arch_dir)
    print("  ADRs:    %d" % n_adrs)
    print()
    if not findings:
        print("VERDICT: every binding ADR is well-formed (Conformance check populated) and "
              "enumerated in the manifest.")
        return
    print("Findings (%d):" % len(findings))
    for f in findings:
        print("  - %s" % f)
    print()
    print("VERDICT: BLOCKED -- a binding ADR is malformed or unenumerated; Q6 cannot bind the "
          "plan to it. Re-land a conformant release (an ADR defect is the Architect's).")


# --- self-test -----------------------------------------------------------------
_ADR_OK = """# ADR-001 -- Adopt Dapr

## Binding scope

| Field | Value |
|---|---|
| **Binding** | Yes |
| **Claims** | Inter-service invocation + pub/sub runtime. |
| **Constrains** | All Managers. |
| **Conformance check** | The plan's Manager -> Manager paths go through Dapr pub/sub; no synchronous Manager call appears. |

## Consequences
...
"""
_ADR_NONBINDING = """# ADR-003 -- JSON logging

## Binding scope

| Field | Value |
|---|---|
| **Binding** | No |

## Consequences
...
"""
_MANIFEST_OK = """# Handoff Manifest

## Binding ADRs

| ADR | Claims | Constrains |
|---|---|---|
| ADR-001 | Inter-service invocation + pub/sub | All Managers |

## Back-channels
...
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

    ok_adrs = {"ADR-001": _ADR_OK, "ADR-003": _ADR_NONBINDING}
    expect("well-formed binding ADR + manifest passes", not check(ok_adrs, _MANIFEST_OK))

    # SEEDED: binding ADR with an empty Conformance check
    empty_conf = _ADR_OK.replace(
        "| **Conformance check** | The plan's Manager -> Manager paths go through Dapr pub/sub; no synchronous Manager call appears. |",
        "| **Conformance check** | |")
    f = check({"ADR-001": empty_conf, "ADR-003": _ADR_NONBINDING}, _MANIFEST_OK)
    expect("empty Conformance check is caught", any("Conformance check" in x and "empty or a placeholder" in x for x in f))

    # SEEDED: placeholder Conformance check
    ph_conf = _ADR_OK.replace(
        "| **Conformance check** | The plan's Manager -> Manager paths go through Dapr pub/sub; no synchronous Manager call appears. |",
        "| **Conformance check** | [TODO] |")
    f = check({"ADR-001": ph_conf}, _MANIFEST_OK)
    expect("placeholder Conformance check is caught", any("Conformance check" in x for x in f))

    # SEEDED: binding ADR not listed in the manifest
    f = check({"ADR-001": _ADR_OK}, "# Handoff Manifest\n## Binding ADRs\n\n(none)\n")
    expect("binding ADR missing from the manifest is caught (CHK-12)",
           any("not listed in the manifest" in x for x in f))

    # SEEDED: manifest lists an ADR that does not exist
    f = check({}, _MANIFEST_OK)
    expect("manifest lists a missing ADR is caught", any("is missing" in x for x in f))

    # SEEDED: manifest lists an ADR that is not Binding: Yes
    f = check({"ADR-001": _ADR_NONBINDING.replace("ADR-003", "ADR-001")}, _MANIFEST_OK)
    expect("manifest lists a non-binding ADR is caught", any("not 'Binding: Yes'" in x for x in f))

    # SEEDED (Fix C): the ADR is mentioned only in PROSE under Binding ADRs, not a table row
    prose_manifest = "# Handoff Manifest\n\n## Binding ADRs\n\nRemember that ADR-001 is binding.\n"
    f = check({"ADR-001": _ADR_OK}, prose_manifest)
    expect("prose-only manifest mention does not count as enumeration (Fix C)",
           any("not listed in the manifest" in x for x in f))

    # SEEDED (Fix D): a vague-but-non-empty Conformance check
    vague = _ADR_OK.replace(
        "| **Conformance check** | The plan's Manager -> Manager paths go through Dapr pub/sub; no synchronous Manager call appears. |",
        "| **Conformance check** | should be fine |")
    f = check({"ADR-001": vague}, _MANIFEST_OK)
    expect("vague Conformance check is caught (Fix D)", any("too vague" in x for x in f))

    # SEEDED (Fix E): duplicate ADR id across two files, and an ADR-looking file with no id
    adrs2, extra = scan_decisions([("ADR-001.md", _ADR_OK), ("ADR-001-old.md", _ADR_OK), ("ADR_002.md", "# bad id\n")])
    expect("duplicate ADR id is caught (Fix E)", any("duplicate ADR id ADR-001" in x for x in extra))
    expect("malformed ADR-id filename is caught (Fix E)", any("no well-formed ADR-NNN id" in x for x in extra))

    print("\nself-test: %d passed, %d failed" % (passed, failed))
    return OK if failed == 0 else FINDINGS


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_adr_binding.py",
        description="D1: validate every binding ADR is well-formed + enumerated in the manifest (CHK-12).")
    parser.add_argument("arch_dir", nargs="?", help="the landed release dir architecture/arch-X.Y.Z/")
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixtures and exit")
    ns = parser.parse_args(argv)

    if ns.self_test:
        return self_test()
    if not ns.arch_dir:
        parser.error("expected <arch-dir> (or --self-test)")
    if not os.path.isdir(ns.arch_dir):
        print("error: release dir not found: %s" % ns.arch_dir, file=sys.stderr)
        return ERROR
    findings, n = run(ns.arch_dir)
    report(findings, n, ns.arch_dir)
    return FINDINGS if findings else OK


if __name__ == "__main__":
    sys.exit(main())
