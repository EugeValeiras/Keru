#!/usr/bin/env python3
"""check_fragment.py -- deterministic structural checks on a SAD fragment.

Tier-2 of the fragment-check suite (Tier-1 = reconcile_flow + check_counts).
These are auditor checks that the constitution already marks `deterministic`
but that the LLM auditor used to run by reading the fragment -- which made the
result non-reproducible across runs (the smoke-test S1a: iter-1 applied 3
lenses, iter-2 found 20 more; only a ledger-completeness *script* fails that
deterministically). Each check is mechanical and self-gates on its markers, so
it stays silent on a fragment that does not contain the relevant section
(HIGH PRECISION, ZERO FALSE POSITIVES).

  check_fragment.py <fragment.md>     # exit 1 + report on any violation
  check_fragment.py --self-test

Covers: R-27 Lens Coverage Ledger completeness (L1-L12, non-empty verdicts) +
OQ entry shape; R-13 stressor typing presence; R-02 taxonomy typing; R-06
naming + R-05 tech-vocab on component names; R-15 NFR Source non-empty. R-03
edge-parse / R-18 / R-19 traces stay in the auditor (they need cross-table
residue resolution -- not yet a clean script).
"""

import argparse
import re
import sys

STRESSOR_TYPES = {"Structural", "Topological", "Business", "Combined"}
LAYER_KEYWORDS = ["Client", "Manager", "Engine", "ResourceAccess",
                  "Resource Access", "Resource", "Utility"]
# Substring (not word-boundary): component names are camelCase/PascalCase with
# no separators, so `KafkaAccess` must match `kafka`. Mirrors the auditor's
# case-insensitive R-05 vocabulary check.
TECH_VOCAB = re.compile(
    r"(aws|azure|gcp|lambda|sqs|sns|kafka|kubernetes|k8s|docker|postgres|"
    r"mysql|mongodb|redis|dynamo|grpc|graphql|websocket|oauth|jwt)", re.I)
NAME_RE = re.compile(r"^[A-Z][a-z0-9]+([A-Z][a-z0-9]+)*(Manager|Engine|Access)$")


class Violation:
    def __init__(self, rule, msg):
        self.rule, self.msg = rule, msg

    def __str__(self):
        return f"{self.rule}: {self.msg}"


def _cells(line):
    parts = [c.strip() for c in line.split("|")]
    if parts and parts[0] == "":
        parts = parts[1:]
    if parts and parts[-1] == "":
        parts = parts[:-1]
    return parts


def _clean(cell):
    """Strip markdown emphasis / code ticks / surrounding punctuation."""
    return cell.replace("**", "").replace("`", "").strip()


def _is_sep(cells):
    return cells and all(set(c) <= set("-:") for c in cells if c)


def _iter_tables(lines):
    """Yield (header_cells, [row_cells, ...]) for each markdown table."""
    i, n = 0, len(lines)
    while i < n:
        if lines[i].lstrip().startswith("|") and i + 1 < n and _is_sep(_cells(lines[i + 1])):
            header = _cells(lines[i])
            rows = []
            j = i + 2
            while j < n and lines[j].lstrip().startswith("|"):
                c = _cells(lines[j])
                if not _is_sep(c):
                    rows.append(c)
                j += 1
            yield header, rows
            i = j
        else:
            i += 1


# --------------------------------------------------------------------------
# R-27 -- Lens Coverage Ledger completeness + OQ entry shape
# --------------------------------------------------------------------------

def check_lens_ledger(text):
    out = []
    if "Lens Coverage Ledger" not in text:
        return out
    lines = text.splitlines()
    found = {}  # lens number -> verdict non-empty?
    for header, rows in _iter_tables(lines):
        h0 = _clean(header[0]).lower() if header else ""
        if not h0.startswith("lens"):
            continue
        for r in rows:
            if not r:
                continue
            m = re.match(r"L(\d+)\b", _clean(r[0]))
            if not m:
                continue
            num = int(m.group(1))
            verdict = _clean(r[1]) if len(r) > 1 else ""
            found[num] = bool(verdict)
    if not found:
        return out
    missing = [n for n in range(1, 13) if n not in found]
    if missing:
        out.append(Violation("R-27 lens-ledger",
                             f"Lens Coverage Ledger is missing lens(es) "
                             f"{', '.join('L%d' % n for n in missing)} "
                             f"-- every L1-L12 must carry an explicit verdict"))
    blank = [n for n, ok in sorted(found.items()) if not ok]
    if blank:
        out.append(Violation("R-27 lens-ledger",
                             f"lens(es) {', '.join('L%d' % n for n in blank)} "
                             f"have a blank verdict -- use OQ IDs or the literal "
                             f"`none`, never empty"))
    return out


def check_oq_shape(text):
    out = []
    if "OQ-" not in text:
        return out
    lines = text.splitlines()
    for header, rows in _iter_tables(lines):
        hl = [_clean(c).lower() for c in header]
        if "status" not in hl or "source" not in hl:
            continue
        if not any(_clean(c).lower() in ("id", "oq", "open question") for c in header) \
                and not any("question" in c for c in hl):
            continue
        for r in rows:
            if not r or not re.match(r"OQ-\d+", _clean(r[0])):
                continue
            empties = [header[k] if k < len(header) else f"col{k}"
                       for k in range(min(len(header), len(r)))
                       if not _clean(r[k])]
            if len(r) < len(header) or empties:
                out.append(Violation("R-27 OQ-shape",
                                     f"{_clean(r[0])} has empty/missing cell(s) "
                                     f"-- every OQ needs ID / question / Affects / "
                                     f"Status / Source"))
    return out


# Card-format Open Questions (sad-1.17.14+): one `#### OQ-N - <Status> -- <title>`
# heading per question, with a **Question:** paragraph, an optional **Answer:**
# (present once partially or fully answered), and a `<sub>**Affects:** ... --
# **PRD:** ...</sub>` footer. The status -- `Open` / `Open (partial)` / `Resolved`
# -- lives in the heading. Complements check_oq_shape (the table form); each is a
# no-op for the other layout, so a fragment may use either. Dashes are matched by
# escape so this source stays US-ASCII.
_OQ_CARD_HEAD = re.compile(r"^#{2,6}\s+(OQ-\d+)\b(.*)$", re.I)
_OQ_TITLE_DELIM = re.compile(r"\s(?:\u2014|\u2013|--)\s")
_ANY_HEAD = re.compile(r"^#{1,6}\s")
_FENCE = re.compile(r"^\s*(?:```|~~~)")


def check_oq_cards(text):
    out = []
    if "OQ-" not in text:
        return out
    lines = text.splitlines()
    # Headings inside a fenced code block are literal answer content, not cards.
    heads = []
    fenced = False
    for i, ln in enumerate(lines):
        if _FENCE.match(ln):
            fenced = not fenced
            continue
        if fenced:
            continue
        m = _OQ_CARD_HEAD.match(ln)
        if m:
            heads.append((i, m))
    for i, m in heads:
        oid = m.group(1)
        # Status region: the heading text after the id, before the title delimiter
        # (so a title word like "open" can never be read as a status).
        region = _OQ_TITLE_DELIM.split(m.group(2) or "", 1)[0]
        # Card body up to the next (non-fenced) heading; fenced lines are skipped
        # so a `**Question:**` buried in a code fence cannot satisfy the shape.
        body = []
        bfenced = False
        for j in range(i + 1, len(lines)):
            ln = lines[j]
            if _FENCE.match(ln):
                bfenced = not bfenced
                continue
            if bfenced:
                continue
            if _ANY_HEAD.match(ln):
                break
            body.append(ln)
        missing = []
        if not re.search(r"\b(open|resolved|answered)\b", region, re.I):
            missing.append("a Status (Open / Open (partial) / Resolved) in the heading")
        if not any(re.match(r"\s*\*\*Question:\*\*\s*\S", ln) for ln in body):
            missing.append("a **Question:** line")
        if not any("**Affects:**" in ln for ln in body):
            missing.append("an Affects/Source footer (<sub>**Affects:** ... **PRD:** ...</sub>)")
        if missing:
            out.append(Violation("R-27 OQ-shape",
                                 f"{oid} card is missing {'; '.join(missing)}"))
    return out


# --------------------------------------------------------------------------
# R-13 -- every stressor row carries a valid Type
# --------------------------------------------------------------------------

def check_stressor_typing(text):
    out = []
    lines = text.splitlines()
    for header, rows in _iter_tables(lines):
        if len(header) < 2 or _clean(header[0]) != "#" or _clean(header[1]) != "Type":
            continue
        for r in rows:
            if not r or not re.match(r"S?\d+", _clean(r[0])):
                continue
            t = _clean(r[1]) if len(r) > 1 else ""
            if t not in STRESSOR_TYPES:
                out.append(Violation("R-13 typing",
                                     f"stressor {_clean(r[0])} has type "
                                     f"{t!r} -- must be one of "
                                     f"Structural/Topological/Business/Combined"))
    return out


# --------------------------------------------------------------------------
# R-02 / R-05 / R-06 -- component taxonomy: layer, tech-vocab, naming
# --------------------------------------------------------------------------

def _valid_layer(cell):
    low = _clean(cell).lower()
    return any(k.lower() in low for k in LAYER_KEYWORDS)


def check_taxonomy(text):
    out = []
    lines = text.splitlines()
    for header, rows in _iter_tables(lines):
        hl = [_clean(c).lower() for c in header]
        if "layer" not in hl or "component" not in hl:
            continue
        li, ci = hl.index("layer"), hl.index("component")
        for r in rows:
            if max(li, ci) >= len(r):
                continue
            layer, name = r[li], _clean(r[ci])
            if not _clean(layer):
                continue  # spacer / continuation row
            if not _valid_layer(layer):
                out.append(Violation("R-02 typing",
                                     f"component {name or '<unnamed>'} has invalid "
                                     f"layer {_clean(layer)!r}"))
            if not name:
                continue
            if TECH_VOCAB.search(name):
                out.append(Violation("R-05 tech-vocab",
                                     f"component name {name!r} contains technology "
                                     f"vocabulary"))
            if name.endswith(("Manager", "Engine", "Access")) and not NAME_RE.match(name):
                out.append(Violation("R-06 naming",
                                     f"component name {name!r} is not two-part "
                                     f"PascalCase with a valid suffix"))
    return out


# --------------------------------------------------------------------------
# R-15 -- every Derived-NFR row has a non-empty Source
# --------------------------------------------------------------------------

def check_nfr_source(text):
    out = []
    lines = text.splitlines()
    for header, rows in _iter_tables(lines):
        hl = [_clean(c) for c in header]
        hl_low = [c.lower() for c in hl]
        if "source" not in hl_low:
            continue
        # Only Derived-NFR tables: header pairs Source with NFR/Attribute.
        if not ({"nfr", "attribute"} & set(hl_low)):
            continue
        si = hl_low.index("source")
        # name column = the NFR / Attribute column
        ni = hl_low.index("nfr") if "nfr" in hl_low else hl_low.index("attribute")
        for r in rows:
            if si >= len(r) or ni >= len(r):
                continue
            name = _clean(r[ni])
            if not name:
                continue
            if not _clean(r[si]):
                out.append(Violation("R-15 NFR-source",
                                     f"NFR {name!r} has an empty Source cell"))
    return out


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------

ALL = [check_lens_ledger, check_oq_shape, check_oq_cards, check_stressor_typing,
       check_taxonomy, check_nfr_source]


def run(text):
    out, seen = [], set()
    for chk in ALL:
        for v in chk(text):
            key = (v.rule, v.msg)
            if key not in seen:
                seen.add(key)
                out.append(v)
    return out


def _run_file(path):
    with open(path, encoding="utf-8") as fh:
        viols = run(fh.read())
    if viols:
        print(f"FRAGMENT CHECK FAILED: {len(viols)} violation(s) in {path}:")
        for v in viols:
            print(f"  - {v}")
        return 1
    print(f"FRAGMENT CHECK OK: {path} passes the Tier-2 structural checks.")
    return 0


def _self_test():
    # R-27 ledger: stops at L10 (the smoke-test S1a iter-1 defect) + a blank verdict
    led = "#### Lens Coverage Ledger\n\n| Lens | Verdict |\n|---|---|\n"
    led += "".join(f"| L{n} x | none |\n" for n in range(1, 10))
    led += "| L10 x |  |\n"  # blank verdict
    v = check_lens_ledger(led)
    msgs = " ".join(x.msg for x in v)
    assert "L11" in msgs and "L12" in msgs, msgs       # missing
    assert "L10" in msgs and "blank" in msgs, msgs     # blank verdict
    full = "#### Lens Coverage Ledger\n\n| Lens | Verdict |\n|---|---|\n" + \
        "".join(f"| L{n} x | none |\n" for n in range(1, 13))
    assert not check_lens_ledger(full), check_lens_ledger(full)

    # R-27 OQ shape -- table form
    oq = "| ID | Question | Affects | Status | Source |\n|---|---|---|---|---|\n" \
         "| OQ-1 | q | G1 | Open | PRD:L1 |\n| OQ-2 | q2 | G2 |  | PRD:L2 |\n"
    v = check_oq_shape(oq)
    assert any("OQ-2" in x.msg for x in v) and not any("OQ-1" in x.msg for x in v), [str(x) for x in v]
    assert not check_oq_cards(oq), [str(x) for x in check_oq_cards(oq)]  # table form is a no-op for the card check

    # R-27 OQ shape -- card form (middle-dot separator, emoji status, em-dash title)
    card_ok = ("#### OQ-1 \u00b7 \U0001f7e1 Open (partial) \u2014 RTP threshold\n\n"
               "**Question:** what is the configured RTP threshold?\n\n"
               "**Answer:** no default % range per level yet\n\n"
               "<sub>**Affects:** INV-2 \u2014 **PRD:** L42</sub>\n")
    assert not check_oq_cards(card_ok), [str(x) for x in check_oq_cards(card_ok)]
    assert not check_oq_shape(card_ok), [str(x) for x in check_oq_shape(card_ok)]  # card form is a no-op for the table check
    # a card missing the Status (in heading) AND the **Question:** is flagged; a
    # title word like "open" must NOT satisfy the status (it sits after the title delimiter)
    card_bad = ("#### OQ-2 \u2014 keep this open for later\n\n"
                "some prose, no question label\n\n"
                "<sub>**Affects:** x</sub>\n")
    v = check_oq_cards(card_bad)
    assert any("OQ-2" in x.msg and "Status" in x.msg for x in v), [str(x) for x in v]
    assert any("OQ-2" in x.msg and "Question" in x.msg for x in v), [str(x) for x in v]
    # a fenced fake OQ heading inside an answer is literal content, not a card:
    # it must neither be validated as a (malformed) card nor terminate the real one
    card_fenced = ("#### OQ-1 - Open (partial) -- t\n\n"
                   "**Question:** real q?\n\n"
                   "**Answer:** example:\n\n"
                   "```text\n"
                   "#### OQ-9 - Resolved -- fake heading in fence\n"
                   "**Question:** fake one\n"
                   "```\n\n"
                   "<sub>**Affects:** x -- **PRD:** L1</sub>\n")
    assert not check_oq_cards(card_fenced), [str(x) for x in check_oq_cards(card_fenced)]

    # R-13 typing presence
    st = "| # | Type | Stressor |\n|---|---|---|\n| S1 | Topological | a |\n| S2 | Bogus | b |\n"
    v = check_stressor_typing(st)
    assert any("S2" in x.msg for x in v) and not any("S1" in x.msg for x in v), [str(x) for x in v]

    # R-02 / R-05 / R-06 taxonomy
    tax = ("| Layer | Component | Responsibility |\n|---|---|---|\n"
           "| Manager | `OrderManager` | x |\n"
           "| ResourceAccess | `KafkaAccess` | x |\n"
           "| Bogus | `Thing` | x |\n"
           "| Engine | `lowercaseEngine` | x |\n")
    v = check_taxonomy(tax)
    rules = {x.rule.split()[0] for x in v}
    assert "R-05" in rules and "R-02" in rules and "R-06" in rules, [str(x) for x in v]
    assert not any("OrderManager" in x.msg for x in v), [str(x) for x in v]

    # R-15 NFR source
    nfr = "| NFR | Source | Specification |\n|---|---|---|\n" \
          "| Latency | Coupling #1 | p99 |\n| Availability |  | 24/7 |\n"
    v = check_nfr_source(nfr)
    assert any("Availability" in x.msg for x in v) and not any("Latency" in x.msg for x in v), [str(x) for x in v]

    print("SELF-TEST PASSED")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Deterministic structural checks on a SAD fragment.")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return _self_test()
    if not args.path:
        ap.error("a fragment path is required (or use --self-test)")
    return _run_file(args.path)


if __name__ == "__main__":
    sys.exit(main())
