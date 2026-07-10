#!/usr/bin/env python3
"""reconcile_flow.py -- deterministic FLOW.md table <-> Mermaid reconciliation.

The Gate tracker table in a project's FLOW.md is the AUTHORITATIVE gate state
(`FLOW.md` "if the two ever disagree, this table wins"). The Mermaid state
diagram is a visual companion that must be derived from it. In practice the
gate-approval step mutates the table row but forgets the two things the Mermaid
node needs (label mark + `:::class`) and the gate node `Gn` -- so the diagram
drifts and an operator reconciles it by hand every transition (feedback F-01).

This script makes that reconciliation mechanical:

  reconcile_flow.py <FLOW.md> --check   # exit 1 + report if the Mermaid drifted
  reconcile_flow.py <FLOW.md> --fix     # rewrite the Mermaid nodes from the table
  reconcile_flow.py --self-test         # built-in regression checks

It is deliberately conservative: it edits ONLY the state-diagram ```mermaid
block (never the ```diff examples under "How to update state"), and only nodes
whose id is a known gate/step. Anything it cannot parse is left untouched and,
in --check, reported as "unparsed" rather than silently passed.

Mechanical + deterministic -> a tested script, not LLM prose
(shared/mechanical-determinism-snippet.md).
"""

import argparse
import re
import sys

# State token (inside the leading [..] of a label) -> classDef name.
STATE_CLASS = {
    " ": "pending",
    "~": "in_progress",
    "?": "awaiting_review",
    "x": "approved",
    "!": "blocked",
    "i": "iterating",
}
VALID_STATES = set(STATE_CLASS)

# Step node ids (the Mermaid `Sn[...]` nodes and the table rows).
STEP_IDS = ["S1a", "S1b", "S2", "S3", "S4", "S5", "S6", "S7", "S8a", "S8b"]
# Step -> its approval-gate node id. S8b has no gate node.
STEP_TO_GATE = {
    "S1a": "G1a", "S1b": "G1b", "S2": "G2", "S3": "G3", "S4": "G4",
    "S5": "G5", "S6": "G6", "S7": "G7", "S8a": "G8a",
}

# A label's leading state token: `[ ]`, `[x]`, `[~]`, `[?]`, `[!]`, `[i]`.
_STATE_TOK = r"\[(?P<state>[ ~?x!i])\]"
# Step node:  Sx["[?] label<br/>..."]:::class
_STEP_RE = re.compile(r'^(?P<pre>\s*)(?P<id>S(?:1a|1b|2|3|4|5|6|7|8a|8b))'
                      r'\["' + _STATE_TOK + r'(?P<rest>.*?)"\]:::(?P<cls>\w+)')
# Gate node:  Gx{"[ ] label<br/>..."}:::class
_GATE_RE = re.compile(r'^(?P<pre>\s*)(?P<id>G(?:1a|1b|2|3|4|5|6|7|8a))'
                      r'\{"' + _STATE_TOK + r'(?P<rest>.*?)"\}:::(?P<cls>\w+)')


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

def parse_gate_table(text):
    """Return {step_id: state_char} from the authoritative Gate tracker table.

    A row looks like:  | S1a | business-view.md | `[ ]` | -- |
    Only rows whose first cell is a known step id are taken.
    """
    table = {}
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = line.split("|")
        if len(cells) < 5:
            continue
        gate = cells[1].strip()
        if gate not in STEP_IDS:
            continue
        m = re.search(_STATE_TOK, cells[3])
        if not m:
            continue
        table[gate] = m.group(1)
    return table


def find_state_diagram(lines):
    """Return (start, end) line indices (exclusive of the fences) of the
    state-diagram ```mermaid block -- the one carrying `classDef approved`.
    Returns (None, None) if not found. This deliberately skips ```diff blocks.
    """
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].strip() == "```mermaid":
            j = i + 1
            while j < n and lines[j].strip() != "```":
                j += 1
            block = "\n".join(lines[i + 1:j])
            if "classDef approved" in block or "flowchart" in block:
                return i + 1, j
            i = j + 1
        else:
            i += 1
    return None, None


# --------------------------------------------------------------------------
# Expected state
# --------------------------------------------------------------------------

def expected_for_step(step_id, table):
    """(state_char, class) a step node should carry, per the table."""
    st = table.get(step_id)
    if st is None:
        return None
    return st, STATE_CLASS[st]


def expected_for_gate(gate_id, table):
    """(state_char, class) a gate node should carry. A gate is `approved`
    iff its step is `[x]`; otherwise it is `pending`. The gate answers
    'is this fragment approved?' -- binary, not the intermediate step state.
    """
    step = next((s for s, g in STEP_TO_GATE.items() if g == gate_id), None)
    if step is None or step not in table:
        return None
    return ("x", "approved") if table[step] == "x" else (" ", "pending")


# --------------------------------------------------------------------------
# Drift detection + fix
# --------------------------------------------------------------------------

class Drift:
    def __init__(self, node, kind, got, want):
        self.node, self.kind, self.got, self.want = node, kind, got, want

    def __str__(self):
        return (f"{self.node}: {self.kind} is [{self.got[0]}]/:::{self.got[1]} "
                f"-- table requires [{self.want[0]}]/:::{self.want[1]}")


def compute_drifts(text):
    """Return (drifts, unparsed) without modifying anything."""
    lines = text.splitlines()
    table = parse_gate_table(text)
    start, end = find_state_diagram(lines)
    drifts, unparsed = [], []
    if start is None:
        return drifts, ["no state-diagram ```mermaid block found"]
    for idx in range(start, end):
        line = lines[idx]
        ms, mg = _STEP_RE.match(line), _GATE_RE.match(line)
        if ms:
            want = expected_for_step(ms.group("id"), table)
            if want is None:
                unparsed.append(f"line {idx+1}: step {ms.group('id')} not in table")
                continue
            got = (ms.group("state"), ms.group("cls"))
            if got != want:
                drifts.append(Drift(ms.group("id"), "step", got, want))
        elif mg:
            want = expected_for_gate(mg.group("id"), table)
            if want is None:
                continue
            got = (mg.group("state"), mg.group("cls"))
            if got != want:
                drifts.append(Drift(mg.group("id"), "gate", got, want))
    return drifts, unparsed


def apply_fix(text):
    """Return (new_text, n_changed) with every step/gate node in the state
    diagram rewritten to match the table."""
    lines = text.splitlines(keepends=True)
    plain = [l.rstrip("\n") for l in lines]
    table = parse_gate_table(text)
    start, end = find_state_diagram(plain)
    if start is None:
        return text, 0
    changed = 0
    for idx in range(start, end):
        line = plain[idx]
        ms, mg = _STEP_RE.match(line), _GATE_RE.match(line)
        if ms:
            want = expected_for_step(ms.group("id"), table)
            if want is None:
                continue
            new = (f'{ms.group("pre")}{ms.group("id")}["[{want[0]}]'
                   f'{ms.group("rest")}"]:::{want[1]}')
        elif mg:
            want = expected_for_gate(mg.group("id"), table)
            if want is None:
                continue
            new = (f'{mg.group("pre")}{mg.group("id")}{{"[{want[0]}]'
                   f'{mg.group("rest")}"}}:::{want[1]}')
        else:
            continue
        # preserve any trailing content after the matched node (rare) + newline
        tail = line[ms.end() if ms else mg.end():]
        eol = "\n" if lines[idx].endswith("\n") else ""
        rebuilt = new + tail + eol
        if rebuilt != lines[idx]:
            lines[idx] = rebuilt
            changed += 1
    return "".join(lines), changed


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _run_check(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    drifts, unparsed = compute_drifts(text)
    for u in unparsed:
        print(f"WARN  {u}", file=sys.stderr)
    if drifts:
        print(f"FLOW DRIFT: {len(drifts)} node(s) in the Mermaid diagram do not "
              f"match the authoritative Gate tracker table:")
        for d in drifts:
            print(f"  - {d}")
        print("Fix: run reconcile_flow.py <FLOW.md> --fix")
        return 1
    print("FLOW OK: Mermaid diagram matches the Gate tracker table.")
    return 0


def _run_fix(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    new, changed = apply_fix(text)
    if changed:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new)
    print(f"FLOW reconciled: {changed} node(s) rewritten from the table.")
    return 0


def _self_test():
    base = """## Gate tracker
| Gate | Fragment | State | Approved on |
|---|---|---|---|
| S1a | business-view.md | `[x]` | 2026-06-19 |
| S1b | naive-architecture.md | `[x]` | 2026-06-19 |
| S2 | flow-analysis.md | `[?]` | -- |
| S3 | stressor-catalog.md | `[ ]` | -- |

## Diagram
```mermaid
flowchart TD
    S1a["[ ] S1a - business view"]:::pending
    S1b["[x] S1b - naive arch"]:::approved
    S2["[?] S2 - flow"]:::awaiting_review
    S3["[ ] S3 - stressors"]:::pending
    G1a{"[ ] Gate 1a"}:::pending
    G1b{"[x] Gate 1b"}:::approved
    G2{"[ ] Gate 2"}:::pending
    classDef approved fill:#b2f2bb
    classDef pending fill:#f1f3f5
```

## How to update state
```diff
- S1a["[ ] S1a"]:::pending
+ S1a["[~] S1a"]:::in_progress
```
"""
    # table parse
    t = parse_gate_table(base)
    assert t == {"S1a": "x", "S1b": "x", "S2": "?", "S3": " "}, t
    # drift: S1a should be [x]/approved (table) but diagram shows [ ]/pending;
    #        G1a should be approved (S1a==x) but shows pending.
    drifts, unparsed = compute_drifts(base)
    nodes = sorted(d.node for d in drifts)
    assert nodes == ["G1a", "S1a"], nodes
    assert not unparsed, unparsed
    # fix makes it clean and idempotent, and does NOT touch the ```diff example
    fixed, changed = apply_fix(base)
    assert changed == 2, changed
    assert '+ S1a["[~] S1a"]:::in_progress' in fixed, "diff example must be untouched"
    assert 'S1a["[x] S1a - business view"]:::approved' in fixed
    assert 'G1a{"[x] Gate 1a"}:::approved' in fixed
    d2, _ = compute_drifts(fixed)
    assert not d2, d2
    f2, c2 = apply_fix(fixed)
    assert c2 == 0 and f2 == fixed, "fix must be idempotent"
    # gate stays pending while step is only awaiting-review
    assert 'G2{"[ ] Gate 2"}:::pending' in fixed
    print("SELF-TEST PASSED")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Reconcile FLOW.md Mermaid against its Gate tracker table.")
    ap.add_argument("path", nargs="?", help="path to a project FLOW.md")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true", help="report drift, exit 1 if any")
    g.add_argument("--fix", action="store_true", help="rewrite the Mermaid from the table")
    ap.add_argument("--self-test", action="store_true", help="run built-in regression checks")
    args = ap.parse_args(argv)
    if args.self_test:
        return _self_test()
    if not args.path:
        ap.error("a FLOW.md path is required (or use --self-test)")
    if args.fix:
        return _run_fix(args.path)
    return _run_check(args.path)  # --check is the default


if __name__ == "__main__":
    sys.exit(main())
