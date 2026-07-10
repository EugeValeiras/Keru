#!/usr/bin/env python3
"""
check-anchors.py -- deterministic RE-01 anchor validator for recon fragments.

Mechanical companion to the recon-auditor's RE-01 checks. It does the parts of
false-anchor detection that need no judgment, leaving only true judgment calls
to the heuristic walk (recon-auditor Step 3).

It performs TWO deterministic checks per anchor, against the target repo root:

  (1) LINE-EXISTENCE (always).  For every `path:line`, `path:line-range`, or
      `path:N,M,K` anchor it confirms the file exists and every cited line is
      within the file (line <= the file's line count). A line past EOF -- e.g.
      `gateway/Dockerfile:42` when the file ends at line 33 -- is a DETERMINISTIC
      false anchor (the 2026-06-16 market-trading V1 bug).

  (2) SNIPPET-ON-LINE (opt-in).  An anchor MAY carry an expected snippet after a
      `~` marker, inside the same code span:

          `market-trading-2/dapr.yaml:17 ~ DATABASE_URL`

      meaning "line 17 must contain the text `DATABASE_URL`". When present, the
      script confirms the snippet actually appears on the cited line (or, for a
      range, on some line within it). This catches the OFF-BY-ONE content false
      anchor -- the line exists but proves the wrong fact -- which check (1)
      cannot see and which forced the 2026-06-17 R1 re-audits (`dapr.yaml:18`
      cited for a credential that lives on line 17; `gateway/package.json:5`
      cited for `"type":"module"` that lives on line 4). That class was the bulk
      of the iter-1/iter-2 findings and previously depended on a fallible manual
      read; the snippet makes it a hard, reproducible failure.

      Matching is whitespace-normalized (the producer need not reproduce source
      indentation) and case-sensitive substring (copy the literal source token).
      A snippet runs from `~` to the closing backtick / end of line, so it cannot
      itself contain a backtick. An anchor with no `~` is checked for line
      existence only -- fully backward-compatible with existing fragments.

Read-only. Never writes. No third-party dependencies.

Usage:
    check-anchors.py <fragment.md> <repo-root>

Exit codes:
    0  every cited line resolves and every snippet matches (clean, or only
       unresolved-path warnings)
    1  one or more VIOLATIONS -- a past-EOF line, or a snippet not on its line
    2  usage / IO error

Output: one line per finding.
    VIOLATION  <file>:<line>  past EOF (file has <N> lines)
    CONTENT    <file>:<spec> ~ "<snippet>"  not on cited line; found at line <N>
    CONTENT    <file>:<spec> ~ "<snippet>"  not on cited line; not within +/-5 lines
    warn       <file>:<line>  file not found under repo root (verify manually)
"""

import os
import re
import sys

# path : linespec [ ~ snippet ]
#   linespec is N | N-M, optionally comma-repeated.
#   The optional `~ snippet` (group 3) runs to the closing backtick or EOL, so a
#   snippet cannot contain a backtick. Capturing it in the SAME match means
#   finditer consumes the snippet text and will not re-scan its tokens (e.g. a
#   `host:5432` inside a snippet) as spurious anchors.
# The path class excludes ':' so `http://host:80` does not match as path='http'.
ANCHOR_RE = re.compile(
    r"(?<![\w/])([\w][\w./-]*?):(\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*)"
    r"(?:\s*~\s*([^`\n]+?)\s*(?=`|\n|$))?"
)

# How far around the cited span to look when reporting an off-by-one hint.
HINT_RADIUS = 5


def line_count(path):
    """Number of lines in a file (counts a final unterminated line)."""
    with open(path, "rb") as fh:
        data = fh.read()
    if not data:
        return 0
    n = data.count(b"\n")
    if not data.endswith(b"\n"):
        n += 1
    return n


def read_lines(path):
    """File as a list of text lines (newline stripped), 1-indexed via [n-1]."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read().splitlines()


def cited_lines(linespec):
    """Expand 'N,M-K' into the set of endpoint line numbers to bounds-check."""
    out = []
    for part in linespec.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-", 1)
            out.append(int(lo))
            out.append(int(hi))
        else:
            out.append(int(part))
    return out


def spanned_lines(linespec):
    """Expand 'N,M-K' into EVERY line number it covers (ranges fully filled).

    cited_lines() returns only range endpoints (enough for a bounds check);
    the snippet check must scan every line inside a range, so it uses this.
    """
    out = set()
    for part in linespec.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-", 1)
            lo, hi = int(lo), int(hi)
            if hi < lo:
                lo, hi = hi, lo
            out.update(range(lo, hi + 1))
        else:
            out.add(int(part))
    return sorted(out)


def normalize_ws(s):
    """Collapse all whitespace runs to single spaces and strip ends.

    Lets a snippet match a source line without reproducing its indentation.
    """
    return " ".join(s.split())


def snippet_on_span(lines, total, span, snippet):
    """Is the (ws-normalized) snippet on any cited line?

    Returns (True, None) if it is. Otherwise (False, hint) where hint is the
    nearest line within +/-HINT_RADIUS that DOES contain it (an off-by-one
    finger-point), or None if it is nowhere nearby.
    """
    norm = normalize_ws(snippet)

    def has(n):
        return 1 <= n <= total and norm in normalize_ws(lines[n - 1])

    if any(has(n) for n in span):
        return True, None

    lo = max(1, min(span) - HINT_RADIUS)
    hi = min(total, max(span) + HINT_RADIUS)
    near = [n for n in range(lo, hi + 1) if has(n)]
    if not near:
        return False, None
    # Nearest line to the cited span (ties resolve to the lower line number).
    nearest = min(near, key=lambda n: (min(abs(n - s) for s in span), n))
    return False, nearest


def main(argv):
    if len(argv) != 3:
        sys.stderr.write("usage: check-anchors.py <fragment.md> <repo-root>\n")
        return 2
    fragment, repo_root = argv[1], argv[2]
    try:
        with open(fragment, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError as exc:
        sys.stderr.write("cannot read fragment: %s\n" % exc)
        return 2
    if not os.path.isdir(repo_root):
        sys.stderr.write("repo-root is not a directory: %s\n" % repo_root)
        return 2

    eof_violations = 0
    content_violations = 0
    warnings = 0
    seen = set()
    for m in ANCHOR_RE.finditer(text):
        rel, linespec, snippet = m.group(1), m.group(2), m.group(3)
        key = (rel, linespec, snippet)
        if key in seen:
            continue
        seen.add(key)
        target = os.path.join(repo_root, rel)
        if not os.path.isfile(target):
            # Could be a real broken path, or a prose token like `node:20`.
            # Lower severity: flagged for manual check, does not fail the run.
            print("warn       %s:%s  file not found under repo root (verify manually)" % (rel, linespec))
            warnings += 1
            continue
        total = line_count(target)

        past_eof = False
        for ln in cited_lines(linespec):
            if ln > total or ln < 1:
                print("VIOLATION  %s:%d  past EOF (file has %d lines)" % (rel, ln, total))
                eof_violations += 1
                past_eof = True

        # Snippet check: only when a snippet is present AND every cited line is
        # in bounds (a past-EOF anchor is already a hard fail; re-flagging its
        # content would be noise).
        if snippet is not None and not past_eof:
            lines = read_lines(target)
            ok, hint = snippet_on_span(lines, total, spanned_lines(linespec), snippet)
            if not ok:
                where = ("found at line %d" % hint) if hint else "not within +/-%d lines" % HINT_RADIUS
                print('CONTENT    %s:%s ~ "%s"  not on cited line; %s' % (rel, linespec, snippet, where))
                content_violations += 1

    violations = eof_violations + content_violations
    sys.stderr.write(
        "checked %d distinct anchors -- %d past-EOF + %d content violation(s), "
        "%d unresolved-path warning(s)\n"
        % (len(seen), eof_violations, content_violations, warnings)
    )
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
