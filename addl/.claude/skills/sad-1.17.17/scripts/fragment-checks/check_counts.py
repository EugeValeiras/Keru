#!/usr/bin/env python3
"""check_counts.py -- deterministic prose-vs-table count reconciliation.

A SAD fragment recites aggregate numbers in prose ("31 Structural, 8
Topological...", "14 operation-columns", "N = 53", "X = 0, Y = 10, S = 12")
that are *derivable from a table in the same fragment*. When a row is re-typed
or a column re-designed and the prose is not re-derived, the two disagree --
the exact class of defect the auditor kept catching one gate too late and one
iteration too expensive (feedback F-02; audit-iter-5 "9 Topological / 6
Combined" vs table 8/7; audit-iter-6 "17 operation-columns" vs 14, "N = 56" vs
53). It is mechanical and deterministic, so it is a script, not LLM prose
(shared/mechanical-determinism-snippet.md).

  check_counts.py <fragment.md>            # exit 1 + report on any mismatch
  check_counts.py --self-test              # built-in regression checks

Design principle: HIGH PRECISION, ZERO FALSE POSITIVES. A check fires only when
BOTH the table-derived value AND a prose claim parse confidently in a recognized
pattern; anything it cannot parse is left silent (it is not the gate's job to
guess). It runs every check whose markers are present, so it works on a single
fragment and on the assembled sad.md alike.
"""

import argparse
import re
import sys

TYPES = ["Structural", "Topological", "Business", "Combined"]
_SIGMA = "Σ"  # the table uses the Sigma glyph; keep this script US-ASCII


class Finding:
    def __init__(self, section, msg):
        self.section, self.msg = section, msg

    def __str__(self):
        return f"COUNT MISMATCH [{self.section}]: {self.msg}"


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------

def _cells(line):
    """Pipe-row -> list of stripped, bold-stripped cells (edges dropped)."""
    parts = [c.strip().strip("*").strip() for c in line.split("|")]
    # drop the empty cells produced by leading/trailing pipes
    if parts and parts[0] == "":
        parts = parts[1:]
    if parts and parts[-1] == "":
        parts = parts[:-1]
    return parts


def _int(cell):
    m = re.fullmatch(r"-?\d+", cell.strip().strip("*").strip())
    return int(m.group()) if m else None


# --------------------------------------------------------------------------
# S3 -- stressor-catalog: per-Type distribution vs the Type column tally
# --------------------------------------------------------------------------

def _stressor_tally(text):
    """Tally the Type column of the stressor-catalog table (header 1st cell
    '#', 2nd 'Type'). Returns (saw_table, {type: count}). Shared by the S3
    distribution check and the S7 total-stressor-count check so both read the
    same table the same way."""
    lines = text.splitlines()
    tally = {t: 0 for t in TYPES}
    in_table = False
    saw_table = False
    for line in lines:
        cells = _cells(line) if line.lstrip().startswith("|") else None
        if cells and len(cells) >= 2 and cells[0] == "#" and cells[1] == "Type":
            in_table, saw_table = True, True
            continue
        if in_table:
            if not (cells and len(cells) >= 2):
                in_table = False
                continue
            if set(cells[0]) <= set("-:"):  # separator row
                continue
            if re.fullmatch(r"\**S?\d+\**", cells[0]) and cells[1] in TYPES:
                tally[cells[1]] += 1
    return saw_table, tally


def check_stressor_distribution(text):
    findings = []
    saw_table, tally = _stressor_tally(text)
    if not saw_table or sum(tally.values()) == 0:
        return findings  # no catalog table here -> nothing to reconcile

    # Find a prose distribution claim: the four types, in order, each with a count.
    pat = re.compile(
        r"(\d+)\s+Structural\b.{0,40}?(\d+)\s+Topological\b.{0,40}?"
        r"(\d+)\s+Business\b.{0,40}?(\d+)\s+Combined\b", re.DOTALL)
    for m in pat.finditer(text):
        prose = dict(zip(TYPES, (int(m.group(i)) for i in range(1, 5))))
        for t in TYPES:
            if prose[t] != tally[t]:
                findings.append(Finding(
                    "stressor-catalog distribution",
                    f"prose says {prose[t]} {t} but the Type column tallies "
                    f"{tally[t]}"))
    return findings


# --------------------------------------------------------------------------
# S7 -- assembler exec summary: total stressor count vs the catalog tally
# --------------------------------------------------------------------------

# The exec summary recites "the number of stressors analyzed" (sad-assembler
# SKILL.md Step 4). Anchor the prose tightly: a count immediately on "stressor"
# AND a catalog/analysis word in the same clause, so a bare "5 stressors
# survived" or "unknown future stressors" never matches. Two shapes cover the
# real wordings: word-before ("Stressor analysis covers 22 stressors",
# "22-stressor catalog") and word-after ("22 stressors analyzed",
# "22 stressors in the catalog").
_STRESSOR_TOTAL_BEFORE = re.compile(
    r"(?:analy[sz]e[sd]?|analysis|catalog(?:ue)?)\b.{0,40}?"
    r"\b(\d+)[- ]stressors?\b",
    re.DOTALL | re.IGNORECASE)
_STRESSOR_TOTAL_AFTER = re.compile(
    r"\b(\d+)\s+stressors?\b.{0,40}?"
    r"(?:analy[sz]e[sd]?|analysis|catalog(?:ue)?)\b",
    re.DOTALL | re.IGNORECASE)


def check_stressor_total(text):
    findings = []
    saw_table, tally = _stressor_tally(text)
    total = sum(tally.values())
    if not saw_table or total == 0:
        return findings  # no catalog table here -> nothing to reconcile
    for pat in (_STRESSOR_TOTAL_BEFORE, _STRESSOR_TOTAL_AFTER):
        for m in pat.finditer(text):
            if int(m.group(1)) != total:
                findings.append(Finding(
                    "exec-summary stressor total",
                    f"prose says {m.group(1)} stressors but the catalog Type "
                    f"column tallies {total}"))
    return findings


# --------------------------------------------------------------------------
# S7 -- assembler exec summary: Looping Signals count vs the S4 table
# --------------------------------------------------------------------------

# The exec summary recites "the count of Looping Signals" (sad-assembler
# SKILL.md Step 4). The S4 Looping Signals table (sad/contagion-analysis
# Step 7) has header first cell "Residue #", second "Stressor"; every data row
# is one Combined residue. The prose anchor requires the literal phrase
# "Looping Signals" (capital S) right after the count, so an unrelated number
# never matches. The table can be empty/absent -> stay silent.
_LOOPING_COUNT = re.compile(r"\b(\d+)\s+Looping Signals\b")


def check_looping_signals(text):
    findings = []
    lines = text.splitlines()
    count = 0
    in_table = False
    saw_table = False
    for line in lines:
        cells = _cells(line) if line.lstrip().startswith("|") else None
        if (cells and len(cells) >= 2 and cells[0] == "Residue #"
                and cells[1] == "Stressor"):
            in_table, saw_table = True, True
            count = 0
            continue
        if in_table:
            if not cells:
                in_table = False
                continue
            if set(cells[0]) <= set("-:"):  # separator row
                continue
            # a Looping Signals data row keys on a residue id (e.g. "21",
            # "#21", "S46", "**S70**"); anything else ends the table. Mirrors
            # the `\**S?\d+\**` row-id shape check_stressor_distribution uses.
            if re.fullmatch(r"\**#?\s*S?\d+\**", cells[0]):
                count += 1
            else:
                in_table = False
    if not saw_table:
        return findings  # no Looping Signals table here -> nothing to reconcile
    for m in _LOOPING_COUNT.finditer(text):
        if int(m.group(1)) != count:
            findings.append(Finding(
                "exec-summary Looping Signals",
                f"prose says {m.group(1)} Looping Signals but the Looping "
                f"Signals table has {count} row(s)"))
    return findings


# --------------------------------------------------------------------------
# S4 -- contagion matrix: operation-column count, N = rows + cols, Sigma == K
# --------------------------------------------------------------------------

def _find_matrix(lines):
    """Return (header_idx, sigma_col_idx, n_cols, n_rows) or None.
    The matrix header carries a trailing 'Sigma Row' cell; the totals row's
    first cell is 'Sigma Col'/'Sigma Column'."""
    header_idx = None
    for i, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            continue
        cells = _cells(line)
        if cells and cells[0] == "#" and any(
                re.fullmatch(rf"{_SIGMA}?\s*Row", c) for c in cells[-1:]):
            header_idx = i
            break
    if header_idx is None:
        return None
    header = _cells(lines[header_idx])
    n_cols = len(header) - 2  # drop '#' and 'Sigma Row'
    # data rows + the Sigma-Col totals row
    n_rows, sigma_idx = 0, None
    for j in range(header_idx + 1, len(lines)):
        line = lines[j]
        if not line.lstrip().startswith("|"):
            break
        cells = _cells(line)
        if not cells:
            break
        first = cells[0]
        if re.fullmatch(rf"{_SIGMA}?\s*Col(?:umn)?", first):
            sigma_idx = j
            break
        if set(first) <= set("-:"):
            continue
        if re.match(r"S\d+", first):  # 'S1', 'S1 (T)', etc. -- Topological rows carry (T)
            n_rows += 1
    return header_idx, sigma_idx, n_cols, n_rows


def check_contagion(text):
    findings = []
    lines = text.splitlines()
    mx = _find_matrix(lines)
    if mx is None:
        return findings
    _, sigma_idx, n_cols, n_rows = mx

    # (a) operation/component-column count vs every prose claim of it.
    for m in re.finditer(r"(\d+)\s+(?:operation|component)[- ]columns?", text):
        if int(m.group(1)) != n_cols:
            findings.append(Finding(
                "contagion operation-columns",
                f"prose says {m.group(1)} operation-columns but the matrix "
                f"header prints {n_cols}"))

    # (b) N = rows + cols, against every explicit "N = <num>" claim.
    if n_rows:
        for m in re.finditer(r"\bN\s*=\s*(\d+)\b", text):
            if int(m.group(1)) != n_rows + n_cols:
                findings.append(Finding(
                    "contagion N",
                    f"prose says N = {m.group(1)} but the matrix has "
                    f"{n_rows} rows + {n_cols} columns = {n_rows + n_cols}"))

    # (c) Sigma-Col row sums to K.
    if sigma_idx is not None:
        cells = _cells(lines[sigma_idx])[1:]  # drop the 'Sigma Col' label
        col_sum, k_in_row = 0, None
        for c in cells:
            if "K" in c and "=" in c:
                km = re.search(r"\d+", c)
                if km:
                    k_in_row = int(km.group())
            else:
                v = _int(c)
                if v is not None:
                    col_sum += v
        k_decl = k_in_row
        if k_decl is None:
            km = re.search(r"\bK\s*=\s*(\d+)\b", text)
            k_decl = int(km.group(1)) if km else None
        if k_decl is not None and col_sum and col_sum != k_decl:
            findings.append(Finding(
                "contagion Sigma==K",
                f"the Sigma-Col row sums to {col_sum} but K is declared "
                f"{k_decl}"))
    return findings


# --------------------------------------------------------------------------
# S6 -- empirical test: X / Y / S vs the survives table, and Ri arithmetic
# --------------------------------------------------------------------------

_YES = {"1", "yes", "y", "true"}
_NO = {"0", "no", "n", "false", "-"}


def _parse_survives(text):
    """Parse the S6 survives table (header has two 'survives' columns, one of
    them 'residual'). Returns (X, Y, S) or None when no table is present or any
    cell is not a confident yes/no. Shared by check_empirical (X/Y/S/Ri) and
    check_unstressed (S - Y), so both apply the identical parse + guard."""
    lines = text.splitlines()
    naive_col = resid_col = None
    rows = []
    in_table = False
    for line in lines:
        if not line.lstrip().startswith("|"):
            in_table = False
            continue
        cells = _cells(line)
        low = [c.lower() for c in cells]
        survives_cols = [k for k, c in enumerate(low) if "survives" in c]
        if len(survives_cols) == 2:
            resid_col = next(k for k in survives_cols if "resid" in low[k])
            naive_col = next(k for k in survives_cols if k != resid_col)
            in_table = True
            rows = []
            continue
        if in_table:
            if set(cells[0]) <= set("-:"):
                continue
            if re.fullmatch(r"\**T?\d+\**", cells[0]):
                rows.append(cells)
    if naive_col is None or not rows:
        return None

    def survived(cell):
        v = cell.strip().strip("*").strip().lower()
        if v in _YES:
            return True
        if v in _NO:
            return False
        return None  # unparseable

    X = Y = 0
    for r in rows:
        if max(naive_col, resid_col) >= len(r):
            return None
        nv, rv = survived(r[naive_col]), survived(r[resid_col])
        if nv is None or rv is None:
            return None  # do not guess on a non-yes/no cell
        X += 1 if nv else 0
        Y += 1 if rv else 0
    return X, Y, len(rows)


def check_empirical(text):
    findings = []
    parsed = _parse_survives(text)
    if parsed is None:
        return findings
    X, Y, S = parsed

    for var, val in (("X", X), ("Y", Y), ("S", S)):
        m = re.search(rf"\b{var}\s*=\s*(\d+)\b", text)
        if m and int(m.group(1)) != val:
            findings.append(Finding(
                "empirical X/Y/S",
                f"prose says {var} = {m.group(1)} but the survives table gives "
                f"{var} = {val}"))
    # Ri = (Y - X) / S stated as a parenthesised triple
    for m in re.finditer(r"Ri\s*=\s*\(\s*(\d+)\s*-\s*(\d+)\s*\)\s*/\s*(\d+)", text):
        a, b, c = (int(g) for g in m.groups())
        if (a, b, c) != (Y, X, S):
            findings.append(Finding(
                "empirical Ri formula",
                f"prose Ri = ({a} - {b}) / {c} but the table gives "
                f"(Y - X) / S = ({Y} - {X}) / {S}"))
    return findings


# --------------------------------------------------------------------------
# S6 -- empirical test: unstressed-surfaces count vs the survives table
# --------------------------------------------------------------------------

# An unstressed surface is a test stressor the residual architecture did NOT
# survive (S6 SKILL.md Step 6: residual survives = 0). Their count is therefore
# (rows - residual-survivors) = S - Y from the same survives table. Anchor the
# prose to the literal phrase "unstressed surface(s)" right after a digit, so a
# count spelled as a word ("two unstressed surfaces") -- the worked-example
# style -- never matches and a digit-count drift does.
_UNSTRESSED_COUNT = re.compile(r"\b(\d+)\s+unstressed surfaces?\b", re.IGNORECASE)


def check_unstressed(text):
    findings = []
    parsed = _parse_survives(text)
    if parsed is None:
        return findings  # same guard as check_empirical: silent if unparseable
    _, Y, S = parsed
    unstressed = S - Y
    for m in _UNSTRESSED_COUNT.finditer(text):
        if int(m.group(1)) != unstressed:
            findings.append(Finding(
                "empirical unstressed surfaces",
                f"prose says {m.group(1)} unstressed surfaces but the survives "
                f"table gives S - Y = {S} - {Y} = {unstressed} "
                f"(residual survives = 0 rows)"))
    return findings


# --------------------------------------------------------------------------
# S5 -- residual-design: component-taxonomy per-Layer counts vs the prose
# --------------------------------------------------------------------------

# The five IDesign service layers, in the canonical order the taxonomy summary
# lists them. A single composite match anchors on ALL FIVE in order, so an
# incidental phrase ("the naive baseline had 1 Manager", "1 Client surface +
# 1 Client fleet = 2 Clients") never matches -- only the real per-layer summary
# does. ResourceAccess is matched before Resource and Resource carries a \b that
# "ResourceAccess" cannot satisfy, so the substring never cross-fires.
_TAX_ORDER = ["Manager", "Engine", "ResourceAccess", "Resource", "Utility"]
_TAX_SUMMARY = re.compile(
    r"(\d+)\s+Managers?\b.{0,220}?"
    r"(\d+)\s+Engines?\b.{0,220}?"
    r"(\d+)\s+ResourceAccess(?:es)?\b.{0,220}?"
    r"(\d+)\s+Resources?\b.{0,220}?"
    r"(\d+)\s+Utilit(?:y|ies)\b",
    re.DOTALL)
# "<n> IDesign components (6+9+7+6+1)" -- the total, anchored to an explicit
# additive formula so a bare "<n> components" elsewhere never matches. The
# [\s*]* tolerates a bold close ("components** (...)").
_TAX_TOTAL = re.compile(
    r"(\d+)\s+IDesign\s+components\b[\s*]*\(\s*\d+(?:\s*\+\s*\d+)+\s*\)")


def check_taxonomy(text):
    findings = []
    lines = text.splitlines()
    # The ASSEMBLED SAD carries TWO "Layer | Component" tables -- the naive
    # baseline (S1b) and the residual (S5). Tally each table separately (reset
    # at each header); summing them is the assembled-SAD false positive. The
    # prose summary describes the residual -- the only table carrying all five
    # service layers (the naive baseline has no Utility). Reconcile that one.
    tables = []
    tally = None
    for line in lines:
        cells = _cells(line) if line.lstrip().startswith("|") else None
        if cells and len(cells) >= 2 and cells[0] == "Layer" and cells[1] == "Component":
            tally = {}
            tables.append(tally)
            continue
        if tally is not None:
            if not (cells and len(cells) >= 2):
                tally = None
                continue
            if set(cells[0]) <= set("-:"):  # separator row
                continue
            if cells[0]:
                tally[cells[0]] = tally.get(cells[0], 0) + 1
    qualifying = [t for t in tables if all(l in t for l in _TAX_ORDER)]
    if len(qualifying) != 1:
        return findings  # zero or ambiguous -> stay silent (no false positive)
    tally = qualifying[0]

    # (a) per-layer: the composite summary's five counts vs the Layer tally.
    for m in _TAX_SUMMARY.finditer(text):
        for i, layer in enumerate(_TAX_ORDER):
            claimed = int(m.group(i + 1))
            if claimed != tally[layer]:
                findings.append(Finding(
                    "residual-design taxonomy",
                    f"prose summary says {claimed} {layer} but the Component "
                    f"Taxonomy Layer column tallies {tally[layer]}"))

    # (b) total: "<n> IDesign components" == sum of the five service layers
    # (the Client surface is counted separately by convention, e.g.
    # "29 IDesign components (6+9+7+6+1) plus the 2 Clients").
    expected = sum(tally[l] for l in _TAX_ORDER)
    for m in _TAX_TOTAL.finditer(text):
        if int(m.group(1)) != expected:
            findings.append(Finding(
                "residual-design taxonomy total",
                f"prose says {m.group(1)} IDesign components but the "
                f"service-layer tally is {expected} (Managers+Engines+"
                f"ResourceAccess+Resources+Utilities; Clients counted "
                f"separately)"))
    return findings


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------

ALL_CHECKS = [check_stressor_distribution, check_stressor_total, check_looping_signals,
              check_contagion, check_empirical, check_unstressed, check_taxonomy]


def run(text):
    findings, seen = [], set()
    for chk in ALL_CHECKS:
        for f in chk(text):
            key = (f.section, f.msg)
            if key not in seen:
                seen.add(key)
                findings.append(f)
    return findings


def _run_file(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    findings = run(text)
    if findings:
        print(f"COUNT CHECK FAILED: {len(findings)} prose-vs-table mismatch(es) "
              f"in {path}:")
        for f in findings:
            print(f"  - {f}")
        print("Fix: re-derive every aggregate cited in prose from its table "
              "(counts / N / K / X-Y-S), or correct the offending table row.")
        return 1
    print(f"COUNT CHECK OK: every aggregate in {path} reconciles with its table.")
    return 0


def _self_test():
    # --- S3: distribution drift (the audit-iter-5 class: prose vs Type tally) ---
    s3_bad = """**Count and distribution.** By Type:
**1 Structural**, **9 Topological**, **0 Business**, **6 Combined**.

| # | Type | Stressor | Detection |
|---|---|---|---|
| S1 | Topological | a | d |
| S2 | Topological | a | d |
| S3 | Structural | a | d |
| S4 | Combined | a | d |
"""
    f = check_stressor_distribution(s3_bad)
    secs = sorted(x.msg for x in f)
    assert any("9 Topological" in m and "tallies 2" in m for m in secs), secs
    assert any("6 Combined" in m and "tallies 1" in m for m in secs), secs
    # table is S=1, T=2, B=0, C=1; make the prose match exactly -> no finding
    s3_ok = s3_bad.replace("9 Topological", "2 Topological").replace("6 Combined", "1 Combined")
    assert not check_stressor_distribution(s3_ok), check_stressor_distribution(s3_ok)

    # --- S4: operation-columns + N (the audit-iter-6 case: 17 vs 14, 56 vs 53) ---
    s4_bad = ("against **17 operation-columns**. Summary NKP triple: N = 56, K = 7.\n\n"
              "| # | A | B | C | " + _SIGMA + " Row |\n|---|---|---|---|---|\n"
              "| S1 | 1 | 0 | 1 | 2 |\n| S2 | 0 | 1 | 1 | 2 |\n"
              "| " + _SIGMA + " Col | 1 | 1 | 2 |  |\n")
    f = check_contagion(s4_bad)
    msgs = [x.msg for x in f]
    assert any("17 operation-columns" in m and "prints 3" in m for m in msgs), msgs
    assert any("N = 56" in m and "= 5" in m for m in msgs), msgs        # 2 rows + 3 cols
    assert any("sums to 4" in m and "K is declared 7" in m for m in msgs), msgs
    s4_ok = ("against **3 operation-columns**. Summary NKP triple: N = 5, K = 4.\n\n"
             "| # | A | B | C | " + _SIGMA + " Row |\n|---|---|---|---|---|\n"
             "| S1 | 1 | 0 | 1 | 2 |\n| S2 | 0 | 1 | 1 | 2 |\n"
             "| " + _SIGMA + " Col | 1 | 1 | 2 | K = 4 |\n")
    assert not check_contagion(s4_ok), check_contagion(s4_ok)

    # --- S6: X/Y/S + Ri, yes/no and 0/1 cell styles ---
    s6_bad = """Naive fails (X = 0). Residual survives (Y = 9). S = 3.
Ri = (9 - 0) / 3.

| # | Test | Naive survives? | Residual survives? | Rationale |
|---|---|---|---|---|
| T1 | a | no | yes | r |
| T2 | a | no | yes | r |
| T3 | a | no | no | r |
"""
    f = check_empirical(s6_bad)
    msgs = [x.msg for x in f]
    assert any("Y = 9" in m and "Y = 2" in m for m in msgs), msgs       # table Y == 2
    assert any("(9 - 0) / 3" in m and "(2 - 0) / 3" in m for m in msgs), msgs
    s6_ok = s6_bad.replace("Y = 9", "Y = 2").replace("(9 - 0)", "(2 - 0)")
    assert not check_empirical(s6_ok), check_empirical(s6_ok)

    # --- S5: component-taxonomy per-Layer counts + total (the "8 ResourceAccess
    #         vs table 7" / "30 components vs 29" class) ---
    s5_bad = (
        "expresses the residual decomposition as **6 IDesign components** "
        "(1 Managers, 1 Engines, 2 ResourceAccess, 1 Resources, 1 Utility) "
        "plus 2 Clients; total **6 IDesign components** (1+1+2+1+1).\n\n"
        "| Layer | Component | Stereotype / Type | Responsibility | State | Residue |\n"
        "|---|---|---|---|---|---|\n"
        "| Client | OperatorConsole | Client | s | x | n |\n"
        "| Client | AgentTrader | Client | s | x | n |\n"
        "| Manager | M1 | Manager | s | x | n |\n"
        "| Engine | E1 | Engine | s | x | n |\n"
        "| ResourceAccess | RA1 | ResourceAccess | s | x | n |\n"
        "| Resource | R1 | Resource | s | x | n |\n"
        "| Utility | U1 | Utility | s | x | n |\n"
    )
    f = check_taxonomy(s5_bad)
    msgs = [x.msg for x in f]
    # table tallies: Manager 1, Engine 1, ResourceAccess 1, Resource 1, Utility 1 (service total 5)
    assert any("2 ResourceAccess" in m and "tallies 1" in m for m in msgs), msgs
    assert any("6 IDesign components" in m and "tally is 5" in m for m in msgs), msgs
    # correct the prose to match the table exactly -> no finding
    s5_ok = (s5_bad.replace("2 ResourceAccess", "1 ResourceAccess")
                   .replace("6 IDesign components", "5 IDesign components")
                   .replace("(1+1+2+1+1)", "(1+1+1+1+1)"))
    assert not check_taxonomy(s5_ok), check_taxonomy(s5_ok)
    # a non-taxonomy fragment (no "Layer | Component" header) is silent
    assert not check_taxonomy("the naive baseline had 1 Manager and 2 Engines.")

    # --- S7: total stressor count in the exec summary vs the catalog tally ---
    # Same catalog table as the S3 distribution test (S=1, T=2, B=0, C=1 -> 4).
    catalog = ("\n\n| # | Type | Stressor | Detection |\n|---|---|---|---|\n"
               "| S1 | Topological | a | d |\n| S2 | Topological | a | d |\n"
               "| S3 | Structural | a | d |\n| S4 | Combined | a | d |\n")
    s7_total_bad = ("Stressor analysis covers **9 stressors** producing 2 Looping "
                    "Signals." + catalog)
    f = check_stressor_total(s7_total_bad)
    msgs = [x.msg for x in f]
    assert any("9 stressors" in m and "tallies 4" in m for m in msgs), msgs
    # word-after wording also fires
    s7_total_bad2 = ("The 9 stressors analyzed in this iteration." + catalog)
    assert any("9 stressors" in x.msg and "tallies 4" in x.msg
               for x in check_stressor_total(s7_total_bad2)), \
        check_stressor_total(s7_total_bad2)
    # corrected prose (4 == tally) -> silent
    assert not check_stressor_total(s7_total_bad.replace("9 stressors", "4 stressors")), \
        check_stressor_total(s7_total_bad.replace("9 stressors", "4 stressors"))
    # negative: a bare "5 stressors survived" without a catalog/analysis word
    # next to it is NOT the total claim -> no false positive
    assert not check_stressor_total("5 stressors survived the test." + catalog), \
        check_stressor_total("5 stressors survived the test." + catalog)

    # --- S7: Looping Signals count vs the S4 Looping Signals table ---
    looping_tbl = ("\n\n| Residue # | Stressor | Survived by Combination of | Notes |\n"
                   "|---|---|---|---|\n"
                   "| 21 | a | #1, #2 | n |\n"
                   "| #22 | b | #3, #4 | n |\n")
    s7_loop_bad = ("The exec summary reports 3 Looping Signals this iteration." + looping_tbl)
    assert any("3 Looping Signals" in x.msg and "has 2 row" in x.msg
               for x in check_looping_signals(s7_loop_bad)), \
        check_looping_signals(s7_loop_bad)
    # corrected prose (2 == rows) -> silent
    assert not check_looping_signals(s7_loop_bad.replace("3 Looping", "2 Looping")), \
        check_looping_signals(s7_loop_bad.replace("3 Looping", "2 Looping"))
    # negative: no Looping Signals table present -> silent even with a number
    assert not check_looping_signals("There are 3 Looping Signals somewhere."), \
        check_looping_signals("There are 3 Looping Signals somewhere.")

    # --- S6: unstressed surfaces = S - Y from the survives table ---
    # table: S = 3 rows, residual survives 2 (T1,T2), 1 (T3) -> unstressed = 1
    s6_uns_bad = ("Two surfaces? prose claims **2 unstressed surfaces**.\n\n"
                  "| # | Test | Naive survives? | Residual survives? | Rationale |\n"
                  "|---|---|---|---|---|\n"
                  "| T1 | a | no | yes | r |\n"
                  "| T2 | a | no | yes | r |\n"
                  "| T3 | a | no | no | r |\n")
    assert any("2 unstressed surfaces" in x.msg and "= 3 - 2 = 1" in x.msg
               for x in check_unstressed(s6_uns_bad)), check_unstressed(s6_uns_bad)
    # corrected prose (1 == S - Y) -> silent
    assert not check_unstressed(s6_uns_bad.replace("2 unstressed", "1 unstressed")), \
        check_unstressed(s6_uns_bad.replace("2 unstressed", "1 unstressed"))
    # negative: count spelled as a word ("two unstressed surfaces") never matches
    assert not check_unstressed(s6_uns_bad.replace("2 unstressed surfaces",
                                                   "two unstressed surfaces")), \
        check_unstressed(s6_uns_bad.replace("2 unstressed surfaces", "two unstressed surfaces"))

    # --- S7: two "Layer|Component" tables (naive + residual) must NOT be summed;
    #         only the residual (all five service layers) is reconciled ---
    s7_two = (
        "Residual: **5 IDesign components** (1 Managers, 1 Engines, "
        "1 ResourceAccess, 1 Resources, 1 Utility) plus 2 Clients.\n\n"
        "| Layer | Component | Responsibility | Upholds |\n|---|---|---|---|\n"
        "| Manager | M0 | s | i |\n| Engine | E0 | s | i |\n"
        "| ResourceAccess | RA0 | s | i |\n| Resource | R0 | s | i |\n\n"
        "| Layer | Component | Stereotype | Responsibility | State | Residue |\n"
        "|---|---|---|---|---|---|\n"
        "| Client | OperatorConsole | Client | s | x | n |\n"
        "| Client | AgentTrader | Client | s | x | n |\n"
        "| Manager | M1 | Manager | s | x | n |\n| Engine | E1 | Engine | s | x | n |\n"
        "| ResourceAccess | RA1 | ResourceAccess | s | x | n |\n"
        "| Resource | R1 | Resource | s | x | n |\n| Utility | U1 | Utility | s | x | n |\n"
    )
    assert not check_taxonomy(s7_two), check_taxonomy(s7_two)  # naive not summed in
    bad7 = s7_two.replace("1 ResourceAccess,", "2 ResourceAccess,")
    assert any("2 ResourceAccess" in x.msg and "tallies 1" in x.msg
               for x in check_taxonomy(bad7)), check_taxonomy(bad7)  # still caught

    # --- looping signals: S-prefixed residue ids must count ---
    lo = ("**3 Looping Signals**.\n\n"
          "| Residue # | Stressor | Survived by Combination of | Notes |\n"
          "|---|---|---|---|\n"
          "| S46 | a | #S1, #S2 | n |\n| S47 | b | #S3 | n |\n| S70 | c | #S5 | n |\n")
    assert not check_looping_signals(lo), check_looping_signals(lo)
    lo_bad = lo.replace("3 Looping Signals", "4 Looping Signals")
    assert any("4 Looping Signals" in x.msg and "has 3 row" in x.msg
               for x in check_looping_signals(lo_bad)), check_looping_signals(lo_bad)

    print("SELF-TEST PASSED")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Reconcile prose aggregate counts against the fragment's tables.")
    ap.add_argument("path", nargs="?", help="path to a SAD fragment / sad.md")
    ap.add_argument("--check", action="store_true", help="(default) report mismatches, exit 1 if any")
    ap.add_argument("--self-test", action="store_true", help="run built-in regression checks")
    args = ap.parse_args(argv)
    if args.self_test:
        return _self_test()
    if not args.path:
        ap.error("a fragment path is required (or use --self-test)")
    return _run_file(args.path)


if __name__ == "__main__":
    sys.exit(main())
