#!/usr/bin/env python3
"""check_drift.py -- constitution / architecture integrity hash (A3).

The whole governance layer rests on one premise: the constitution's **architecture
half** (the principle + binding rules, landed verbatim from the handoff) and the
**binding ADRs** are the Architect's, and the Developer edits ONLY the implementation
half (the [TODO] principles). check_principle.py guards the principle CLAUSES against
the source; this guards the architecture half against EDITS BETWEEN GATES.

At D1 (constitution approved) we PIN a sha256 of the frozen region (everything except
the implementation half) and of the binding-ADR files. At every later gate we re-check:
- a change to the architecture half / binding ADRs BLOCKS -- it cannot come from the
  Developer; it is an upstream re-land of a new arch-X.Y.Z (re-enter D1, re-pin).
- a change to the implementation half is the Developer's and legitimate, but is reported
  as a NOTE so the affected step can be re-opened for an impact assessment.

    check_drift.py <constitution.md> <arch-dir> --pin <pinfile>        # D1: write the pin
    check_drift.py <constitution.md> <arch-dir> --against <pinfile>    # D2..D5: re-check

Exit codes:  0 no architecture-half drift / 1 architecture-half or binding-ADR drift
             2 usage error / file not found / pin unreadable
Stdlib-only. Self-test:  check_drift.py --self-test
"""

import argparse
import glob
import hashlib
import json
import os
import re
import sys

OK, FINDINGS, ERROR = 0, 1, 2

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
IMPL_HALF_RE = re.compile(r"implementation\s+half", re.IGNORECASE)
ADR_RE = re.compile(r"ADR-\d{2,}")
# binding declared either as a colon line ("Binding: Yes") or a `## Binding scope`
# table row ("| **Binding** | Yes |") -- the real handoff uses only the table form.
BINDING_YES_RE = re.compile(r"(?im)^\s*(?:[-*]\s*)?\|?\s*\**\s*binding\**\s*(?::|\|)\s*\**\s*yes\b")


def _norm(lines):
    """Join lines, stripping per-line trailing whitespace and outer blank lines, so a
    benign reformat (trailing spaces, a stray final newline) is not read as drift while
    any real content change still is."""
    out = [ln.rstrip() for ln in lines]
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out)


def split_halves(text):
    """Return (frozen_text, impl_text). The implementation half is the slice from the
    'Implementation half' heading to the next heading of same-or-higher level; the frozen
    region is everything else (preamble, Current Architecture, Architecture half,
    Governance). If there is no implementation-half heading, the whole file is frozen."""
    lines = text.splitlines()
    start = level = None
    for i, ln in enumerate(lines):
        m = HEADING_RE.match(ln)
        if m and IMPL_HALF_RE.search(m.group(2)):
            start, level = i, len(m.group(1))
            break
    if start is None:
        return _norm(lines), ""
    end = len(lines)
    for j in range(start + 1, len(lines)):
        m = HEADING_RE.match(lines[j])
        if m and len(m.group(1)) <= level:
            end = j
            break
    frozen = lines[:start] + lines[end:]
    impl = lines[start:end]
    return _norm(frozen), _norm(impl)


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def binding_adr_blob(arch_dir):
    """(sorted binding-ADR ids, concatenated normalized contents). The decisions dir is
    the pinned release; any change to a binding ADR between gates is drift."""
    decisions = os.path.join(arch_dir, "decisions")
    ids, blobs = [], []
    if os.path.isdir(decisions):
        for path in sorted(glob.glob(os.path.join(decisions, "*.md"))):
            with open(path, encoding="utf-8") as fh:
                body = fh.read()
            if not BINDING_YES_RE.search(body):
                continue
            m = ADR_RE.search(os.path.basename(path)) or ADR_RE.search(body)
            if m:
                ids.append(m.group(0))
                blobs.append("=== %s ===\n%s" % (m.group(0), _norm(body.splitlines())))
    order = sorted(range(len(ids)), key=lambda k: ids[k])
    return [ids[k] for k in order], "\n".join(blobs[k] for k in order)


def compute(constitution_text, arch_dir):
    frozen, impl = split_halves(constitution_text)
    ids, blob = binding_adr_blob(arch_dir)
    return {
        "version": 1,
        "arch_half_sha256": _sha(frozen),
        "impl_half_sha256": _sha(impl),
        "binding_adrs_sha256": _sha(blob),
        "binding_adr_ids": ids,
    }


def diff(pin, now):
    """(blocking_findings, notes). Architecture-half / binding-ADR change BLOCKS; an
    implementation-half change is a NOTE."""
    blocking, notes = [], []
    if pin.get("arch_half_sha256") != now["arch_half_sha256"]:
        blocking.append("the constitution's ARCHITECTURE HALF changed since it was pinned at D1 "
                        "-- it is the handoff's and immutable from the Developer side. A change is "
                        "an upstream re-land (a new arch-X.Y.Z): re-enter D1 and re-pin; do not "
                        "edit it locally.")
    if pin.get("binding_adrs_sha256") != now["binding_adrs_sha256"]:
        before, after = pin.get("binding_adr_ids", []), now["binding_adr_ids"]
        extra = " (binding ADRs %s -> %s)" % (before, after) if before != after else ""
        blocking.append("a BINDING ADR changed since D1%s -- the decisions/ release is pinned; "
                        "re-land + re-pin if the architecture genuinely changed." % extra)
    if pin.get("impl_half_sha256") != now["impl_half_sha256"]:
        notes.append("the implementation half changed since D1 -- legitimate (the Developer owns "
                     "it), but re-open the affected step for an impact assessment.")
    return blocking, notes


def report(blocking, notes, constitution_path, mode):
    print("Constitution / architecture integrity (A3)  [%s]" % mode)
    print("  constitution: %s" % constitution_path)
    print()
    for n in notes:
        print("  NOTE: %s" % n)
    if not blocking:
        print("VERDICT: no architecture-half drift -- the pinned architecture half and binding "
              "ADRs are byte-stable since D1.")
        return
    print("Findings (%d):" % len(blocking))
    for f in blocking:
        print("  - %s" % f)
    print()
    print("VERDICT: BLOCKED -- the architecture side of the constitution moved mid-flow. "
          "Architecture Supremacy: the Developer never edits it; a real change is an upstream "
          "re-land, re-entered at D1.")


# --- self-test -----------------------------------------------------------------
_CONST = """# Sync Impact Report
> generated by speckit-constitution

# EV -- Project Constitution

## Current Architecture
**Binding ADRs (this release):** ADR-001.

# Architecture half

## I. Service Decomposition by Residue
- Managers MUST NOT call other Managers synchronously.
- Engines MUST NOT call Managers and MUST be stateless.

**Binding ADRs.** A runtime decision captured in an ADR is binding.

# Implementation half

## [TODO] Testing strategy
## [TODO] Observability

# Governance
- Amending the architecture half is an upstream re-land.

<!-- version: 1.0.0 -->
"""
_ADR_OK = "# ADR-001 -- Dapr\n\n| Field | Value |\n|---|---|\n| **Binding** | Yes |\n"


def self_test():
    import tempfile
    passed = failed = 0

    def expect(label, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print("  ok    %s" % label)
        else:
            failed += 1
            print("  FAIL  %s" % label)

    def arch_with(adr):
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, "decisions"))
        with open(os.path.join(d, "decisions", "ADR-001.md"), "w") as fh:
            fh.write(adr)
        return d

    arch = arch_with(_ADR_OK)
    pin = compute(_CONST, arch)

    # identical -> no drift
    b, n = diff(pin, compute(_CONST, arch))
    expect("identical constitution + ADRs -> no drift", not b and not n)

    # SEEDED: architecture-half clause weakened -> BLOCK
    weakened = _CONST.replace("- Engines MUST NOT call Managers and MUST be stateless.",
                              "- Engines MAY call Managers.")
    b, n = diff(pin, compute(weakened, arch))
    expect("architecture-half edit BLOCKS", any("ARCHITECTURE HALF" in x for x in b))

    # implementation-half edit -> NOTE only (no block)
    impl_edit = _CONST.replace("## [TODO] Observability",
                               "## Observability\nUse OpenTelemetry traces on every span.")
    b, n = diff(pin, compute(impl_edit, arch))
    expect("implementation-half edit is a NOTE, not a block", not b and any("implementation half" in x for x in n))

    # SEEDED: a binding ADR file changed -> BLOCK
    arch2 = arch_with(_ADR_OK + "\nA snuck-in extra clause.\n")
    b, n = diff(pin, compute(_CONST, arch2))
    expect("binding-ADR file change BLOCKS", any("BINDING ADR" in x for x in b))

    # benign reformat of the frozen region (trailing whitespace) -> NOT drift
    reformatted = _CONST.replace("- Engines MUST NOT call Managers and MUST be stateless.",
                                 "- Engines MUST NOT call Managers and MUST be stateless.   ")
    b, n = diff(pin, compute(reformatted, arch))
    expect("trailing-whitespace reformat of the frozen region is not drift", not b)

    # a NEW binding ADR appearing in the release -> BLOCK (the pinned set moved)
    arch3 = arch_with(_ADR_OK)
    with open(os.path.join(arch3, "decisions", "ADR-002.md"), "w") as fh:
        fh.write("# ADR-002 -- Postgres\nBinding: Yes\n")
    b, n = diff(pin, compute(_CONST, arch3))
    expect("a newly added binding ADR BLOCKS (pinned set changed)",
           any("BINDING ADR" in x and "ADR-002" in x for x in b))

    print("\nself-test: %d passed, %d failed" % (passed, failed))
    return OK if failed == 0 else FINDINGS


def _read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_drift.py",
        description="Constitution / architecture integrity hash (A3): pin at D1, re-check at every gate.")
    parser.add_argument("constitution", nargs="?", help=".specify/memory/constitution.md")
    parser.add_argument("arch", nargs="?", help="architecture/arch-X.Y.Z/ (the pinned release)")
    parser.add_argument("--pin", metavar="PINFILE", help="D1: compute and WRITE the pin to PINFILE")
    parser.add_argument("--against", metavar="PINFILE", help="later gates: re-check against PINFILE")
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixtures and exit")
    ns = parser.parse_args(argv)

    if ns.self_test:
        return self_test()
    if not ns.constitution or not ns.arch:
        parser.error("expected <constitution.md> <arch-dir> with --pin or --against (or --self-test)")
    if not ns.pin and not ns.against:
        parser.error("choose a mode: --pin <file> (D1) or --against <file> (later gates)")
    if not os.path.isfile(ns.constitution):
        print("error: file not found: %s" % ns.constitution, file=sys.stderr)
        return ERROR
    if not os.path.isdir(ns.arch):
        print("error: arch dir not found: %s" % ns.arch, file=sys.stderr)
        return ERROR

    now = compute(_read(ns.constitution), ns.arch)

    if ns.pin:
        with open(ns.pin, "w", encoding="utf-8") as fh:
            json.dump(now, fh, indent=2)
        print("Constitution / architecture integrity (A3)  [pin]")
        print("  pinned the architecture half + %d binding ADR(s) %s to %s"
              % (len(now["binding_adr_ids"]), now["binding_adr_ids"], ns.pin))
        return OK

    try:
        with open(ns.against, encoding="utf-8") as fh:
            pin = json.load(fh)
    except (OSError, ValueError) as exc:
        print("error: cannot read pin %s: %s" % (ns.against, exc), file=sys.stderr)
        return ERROR
    blocking, notes = diff(pin, now)
    report(blocking, notes, ns.constitution, "check")
    return FINDINGS if blocking else OK


if __name__ == "__main__":
    sys.exit(main())
