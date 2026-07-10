#!/usr/bin/env python3
"""
test-check-anchors.py -- persistent test for the check-anchors.py validator.

No test framework: run it with `python3 test-check-anchors.py`.
Exit 0 = all pass; exit 1 = one or more failures.

Covers the unit (pure-function) layer and the end-to-end exit-code/output layer,
anchored on two real bug shapes:
  * 2026-06-16: a past-EOF anchor (`Dockerfile:42` on a short file) must be a
    deterministic VIOLATION, while an in-bounds anchor, a missing file, and a
    prose token (`node:20`) must not hard-fail.
  * 2026-06-17: an off-by-one CONTENT false anchor (`dapr.yaml:18` cited for a
    credential that lives on line 17) must be a deterministic CONTENT violation
    when the anchor carries a `~ snippet`, while a snippet on its true line --
    even indented differently -- must pass.
"""

import importlib.util
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "check-anchors.py")

# Load check-anchors.py as a module (its filename has a hyphen, so import via spec).
_spec = importlib.util.spec_from_file_location("check_anchors", SCRIPT)
ca = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ca)

_failures = []


def check(name, ok):
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        _failures.append(name)


def run(fragment, root):
    """Run the validator as a subprocess; return (exit_code, stdout)."""
    p = subprocess.run(
        [sys.executable, SCRIPT, fragment, root],
        capture_output=True, text=True,
    )
    return p.returncode, p.stdout


# ---- unit: pure functions -------------------------------------------------

check("cited_lines expands a comma-list", ca.cited_lines("2,4,42") == [2, 4, 42])
check("cited_lines expands a range to its endpoints", ca.cited_lines("1-3") == [1, 3])
check("cited_lines keeps a high range endpoint", ca.cited_lines("5-99") == [5, 99])
check("cited_lines tolerates whitespace", ca.cited_lines(" 7 ") == [7])

check("spanned_lines fills a range", ca.spanned_lines("9-12") == [9, 10, 11, 12])
check("spanned_lines merges singletons and ranges", ca.spanned_lines("3,9-10") == [3, 9, 10])
check("spanned_lines dedupes overlaps", ca.spanned_lines("9-11,10") == [9, 10, 11])
check("spanned_lines normalizes a reversed range", ca.spanned_lines("12-9") == [9, 10, 11, 12])

check("normalize_ws collapses indentation", ca.normalize_ws('    "type": "module",') == '"type": "module",')
check("normalize_ws collapses internal runs", ca.normalize_ws("a   b\tc") == "a b c")

# The combined regex must capture an optional snippet (group 3) and leave plain
# anchors untouched (group 3 == None).
_plain = ca.ANCHOR_RE.search("see `gateway/Dockerfile:33` here")
check("ANCHOR_RE leaves a plain anchor's snippet None", _plain.group(3) is None)
_snip = ca.ANCHOR_RE.search("`dapr.yaml:17 ~ DATABASE_URL`")
check("ANCHOR_RE captures path/spec/snippet", (_snip.group(1), _snip.group(2), _snip.group(3)) == ("dapr.yaml", "17", "DATABASE_URL"))
# A snippet bearing a colon+digits token must not spawn a second anchor match.
_one = list(ca.ANCHOR_RE.finditer("`tickstream.yaml:9-10 ~ host=192.168.10.3:30102`"))
check("a colon-token inside a snippet is not re-scanned as an anchor", len(_one) == 1)

with tempfile.TemporaryDirectory() as d:
    f_nl = os.path.join(d, "nl.txt")
    with open(f_nl, "w") as fh:
        fh.write("a\nb\nc\n")
    check("line_count counts 3 lines with trailing newline", ca.line_count(f_nl) == 3)

    f_no_nl = os.path.join(d, "nonl.txt")
    with open(f_no_nl, "w") as fh:
        fh.write("a\nb\nc")
    check("line_count counts a final unterminated line", ca.line_count(f_no_nl) == 3)

    f_empty = os.path.join(d, "empty.txt")
    open(f_empty, "w").close()
    check("line_count of empty file is 0", ca.line_count(f_empty) == 0)


# ---- end-to-end: exit codes + output --------------------------------------

with tempfile.TemporaryDirectory() as root:
    os.makedirs(os.path.join(root, "gateway"))
    # 6-line Dockerfile.
    with open(os.path.join(root, "gateway", "Dockerfile"), "w") as fh:
        fh.write(
            'FROM node:20-alpine\nWORKDIR /app\nCOPY package.json .\n'
            'RUN npm ci\nCOPY src .\nCMD ["node","index.js"]\n'
        )

    # Fragment mixing past-EOF, in-bounds, a missing file, and a prose token.
    bad_frag = os.path.join(root, "bad.md")
    with open(bad_frag, "w") as fh:
        fh.write(
            "| pkg | node, npm ci | `gateway/Dockerfile:2,4,42` |\n"
            "| range past end | `gateway/Dockerfile:5-99` |\n"
            "| missing file | `web/package.json:11` |\n"
            "Prose mentioning node:20 should not hard-fail.\n"
        )
    code, out = run(bad_frag, root)
    check("past-EOF :42 is reported as a VIOLATION", "gateway/Dockerfile:42  past EOF" in out)
    check("range endpoint :99 past EOF is a VIOLATION", "gateway/Dockerfile:99  past EOF" in out)
    check("in-bounds :2 is NOT flapped as past-EOF", "gateway/Dockerfile:2  past EOF" not in out)
    check("missing file is a warn, not a VIOLATION", "warn       web/package.json:11" in out)
    check("prose token node:20 is a warn, not a VIOLATION", "node:20" in out and "VIOLATION  node:20" not in out)
    check("exit code is 1 when there is a past-EOF violation", code == 1)

    # A fragment whose every anchor is in bounds -> clean, exit 0.
    good_frag = os.path.join(root, "good.md")
    with open(good_frag, "w") as fh:
        fh.write("| pkg | the build span | `gateway/Dockerfile:1-3` and `gateway/Dockerfile:2,4` |\n")
    code, out = run(good_frag, root)
    check("clean fragment prints no VIOLATION", "VIOLATION" not in out)
    check("exit code is 0 for an all-in-bounds fragment", code == 0)


# ---- end-to-end: snippet-on-line (the 2026-06-17 off-by-one shape) ---------

with tempfile.TemporaryDirectory() as root:
    # Reproduces market-trading-2/dapr.yaml: credential on line 17, command on 18.
    with open(os.path.join(root, "dapr.yaml"), "w") as fh:
        fh.write(
            "version: 1\ncommon:\n  env:\n    TICK_TFS: \"5m\"\n"      # 1-4
            "    DATABASE_URL: \"user=arturo host=192.168.10.3 port=5432\"\n"  # 5
        )
    # Pad so the credential is on line 17 and the command on line 18, like the real file.
    with open(os.path.join(root, "dapr.yaml"), "w") as fh:
        body = ["x"] * 16
        body[15] = '    DATABASE_URL: "user=arturo host=192.168.10.3 port=5432"'  # line 16
        body.append('    DATABASE_URL: "user=arturo host=192.168.10.3 port=5432"')  # line 17
        body.append('    command: ["go", "run", "."]')                              # line 18
        fh.write("\n".join(body) + "\n")

    # Correct snippet anchor: line 17 really holds DATABASE_URL.
    ok_frag = os.path.join(root, "ok.md")
    with open(ok_frag, "w") as fh:
        fh.write("| creds | `dapr.yaml:17 ~ DATABASE_URL` |\n")
    code, out = run(ok_frag, root)
    check("a snippet on its true line is not a CONTENT violation", "CONTENT" not in out)
    check("correct snippet anchor exits 0", code == 0)

    # Indentation-insensitive: snippet has no leading spaces, source line does.
    ws_frag = os.path.join(root, "ws.md")
    with open(ws_frag, "w") as fh:
        fh.write('| creds | `dapr.yaml:17 ~ DATABASE_URL: "user=arturo` |\n')
    code, out = run(ws_frag, root)
    check("snippet match is whitespace-normalized", "CONTENT" not in out and code == 0)

    # The real bug: :18 cited for the credential. Off by one -> CONTENT violation
    # WITH an off-by-one finger-point to line 17.
    off_frag = os.path.join(root, "off.md")
    with open(off_frag, "w") as fh:
        fh.write("| creds | `dapr.yaml:18 ~ DATABASE_URL` |\n")
    code, out = run(off_frag, root)
    check("off-by-one snippet is a CONTENT violation", 'CONTENT    dapr.yaml:18 ~ "DATABASE_URL"' in out)
    check("CONTENT violation points at the true line", "found at line 17" in out)
    check("off-by-one snippet exits 1", code == 1)

    # Snippet nowhere near the cited line -> CONTENT violation, no finger-point.
    far_frag = os.path.join(root, "far.md")
    with open(far_frag, "w") as fh:
        fh.write("| nope | `dapr.yaml:2 ~ DATABASE_URL` |\n")
    code, out = run(far_frag, root)
    check("absent snippet is a CONTENT violation", 'CONTENT    dapr.yaml:2 ~ "DATABASE_URL"' in out)
    check("absent snippet reports not-within-radius", "not within +/-5 lines" in out)

    # Range snippet: the token lives on one line inside the span -> passes.
    range_frag = os.path.join(root, "range.md")
    with open(range_frag, "w") as fh:
        fh.write("| span | `dapr.yaml:16-18 ~ command` |\n")
    code, out = run(range_frag, root)
    check("snippet anywhere within a cited range passes", "CONTENT" not in out and code == 0)

    # A plain anchor (no `~`) is line-existence-only -- unchanged behavior.
    plain_frag = os.path.join(root, "plain.md")
    with open(plain_frag, "w") as fh:
        fh.write("| plain | `dapr.yaml:18` cites a real line, no snippet |\n")
    code, out = run(plain_frag, root)
    check("a snippetless anchor gets no CONTENT check", "CONTENT" not in out and code == 0)


print()
if _failures:
    print("%d FAILURE(S): %s" % (len(_failures), ", ".join(_failures)))
    sys.exit(1)
print("all checks passed")
sys.exit(0)
