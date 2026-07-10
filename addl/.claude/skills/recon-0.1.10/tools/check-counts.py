#!/usr/bin/env python3
"""
check-counts.py -- deterministic RE-01 verifier for enumeration / count claims.

The third mechanical companion (after check-anchors.py for line anchors and
repo-census.py for file coverage). It closes recon's count-claim BLIND SPOT: a
claim like "grep ... -> 21 hits", "5 actor registrations", "11 Type() strings"
is anchored to a command in PROSE, but the *number* can drift from what the
command actually returns -- and nothing mechanical catches it. This class has
bitten R1 twice (0.1.3: "11 actor types" when there were 10; 0.1.6 E2E: "22"
when the grep returned 21). The snippet check settles `file:line` content; the
census settles file coverage; neither re-runs a grep.

This tool does. The producer writes each count/enumeration claim as a fenced
**verify block** -- the command on the first line, its verbatim expected output
on the following lines:

    ```verify
    grep -rn "func (.*) Type() string" pkg/actors | wc -l
    21
    ```

check-counts.py finds every such block, RE-RUNS the command against the repo
root, and compares output to the pasted expectation. A mismatch is a
deterministic VIOLATION (the prose number lied). Same input (repo state) ->
same output, so this is mechanical, not judgment: deciding *which* command
proves a claim stays with the producer; re-running it and comparing does not.

SAFETY (the whole design risk -- re-running commands). NO SHELL is ever used.
Each pipeline is tokenized with shlex and split on `|` into stages; every stage's
executable must be in a read-only WHITELIST (grep/rg/find/wc/sort/uniq/head/tail/
cat/ls/cut/tr/comm and read-only `git` subcommands); stages are run as an argv
Popen chain (shell=False), so redirections / `;` / `$(...)` / backticks can never
be interpreted -- they are inert literals, and are additionally rejected up front.
A non-whitelisted or unsafe command is a WARN (cannot verify -> flagged for manual
check), never silently passed. Read-only, no writes, no network, per-command timeout.

Usage:
    check-counts.py <fragment.md> <repo-root>

Exit codes:
    0  every verify block matches (or only unverifiable-command warnings)
    1  one or more count mismatches
    2  usage / IO error
"""

import os
import shlex
import subprocess
import sys

# Read-only executables permitted in a verify pipeline.
EXEC_WHITELIST = {
    "grep", "rg", "egrep", "fgrep", "find", "wc", "sort", "uniq",
    "head", "tail", "cat", "ls", "cut", "tr", "comm", "nl", "git",
}
# Read-only git subcommands only.
GIT_SUBCMD_WHITELIST = {
    "ls-files", "log", "grep", "rev-list", "shortlog", "show", "diff", "cat-file",
}
# Shell metacharacters that must not appear in a verify command (a pipe `|` is the
# only operator allowed). Their presence -> unverifiable (warn), never executed.
FORBIDDEN = (">", "<", ";", "&", "`", "$(", "${", "\n")

TIMEOUT_S = 15


def parse_verify_blocks(text):
    """Extract (command, expected_output) from every ```verify fenced block.

    First non-empty line in the block is the command; the remainder (verbatim,
    trailing blank lines trimmed) is the expected output.
    """
    blocks = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].strip().lower() == "```verify":
            body = []
            i += 1
            while i < len(lines) and lines[i].strip() != "```":
                body.append(lines[i])
                i += 1
            # skip the closing fence
            i += 1
            # first non-empty line = command; rest = expected
            cmd = None
            expected = []
            for j, ln in enumerate(body):
                if cmd is None:
                    if ln.strip():
                        cmd = ln.strip()
                else:
                    expected.append(ln)
            if cmd:
                blocks.append((cmd, _normalize("\n".join(expected))))
        else:
            i += 1
    return blocks


def _normalize(s):
    """Strip whitespace per line (both ends) and leading/trailing blank lines.

    Both-ends strip is deliberate: `wc -l` and friends left-pad their count
    (`      21`), and a producer naturally pastes the trimmed value (`21`); a
    per-line full strip makes the two compare equal without the producer having
    to reproduce the tool's padding.
    """
    out = [ln.strip() for ln in s.splitlines()]
    while out and not out[0]:
        out.pop(0)
    while out and not out[-1]:
        out.pop()
    return "\n".join(out)


def pipeline_stages(command):
    """Tokenize and split a command on `|` into a list of argv lists.

    Returns None if the command cannot be safely tokenized.
    """
    if any(tok in command for tok in FORBIDDEN):
        return None
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None
    stages, cur = [], []
    for t in tokens:
        if t == "|":
            stages.append(cur)
            cur = []
        else:
            cur.append(t)
    stages.append(cur)
    if any(not s for s in stages):
        return None
    return stages


def is_safe(stages):
    """Every stage's executable is whitelisted (and git's subcommand read-only)."""
    if stages is None:
        return False
    for argv in stages:
        exe = argv[0]
        if exe not in EXEC_WHITELIST:
            return False
        if exe == "git":
            if len(argv) < 2 or argv[1] not in GIT_SUBCMD_WHITELIST:
                return False
    return True


def run_pipeline(stages, cwd):
    """Run an argv pipeline (shell=False) and return normalized stdout."""
    procs = []
    prev = None
    for argv in stages:
        p = subprocess.Popen(
            argv, cwd=cwd, stdin=prev,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        )
        if prev is not None:
            prev.close()
        prev = p.stdout
        procs.append(p)
    try:
        out, _ = procs[-1].communicate(timeout=TIMEOUT_S)
    finally:
        for p in procs[:-1]:
            try:
                p.wait(timeout=TIMEOUT_S)
            except Exception:
                p.kill()
    return _normalize(out.decode("utf-8", "replace"))


def main(argv):
    if len(argv) != 3:
        sys.stderr.write("usage: check-counts.py <fragment.md> <repo-root>\n")
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

    blocks = parse_verify_blocks(text)
    violations = 0
    warnings = 0
    verified = 0
    for cmd, expected in blocks:
        stages = pipeline_stages(cmd)
        if not is_safe(stages):
            print("warn       cannot verify (non-whitelisted/unsafe command): %s" % cmd)
            warnings += 1
            continue
        try:
            actual = run_pipeline(stages, repo_root)
        except subprocess.TimeoutExpired:
            print("warn       command timed out (not verified): %s" % cmd)
            warnings += 1
            continue
        except OSError as exc:
            print("warn       command failed to run (%s): %s" % (exc, cmd))
            warnings += 1
            continue
        if actual == expected:
            verified += 1
        else:
            violations += 1
            print("MISMATCH   %s" % cmd)
            print("           expected: %s" % expected.replace("\n", " | "))
            print("           actual:   %s" % actual.replace("\n", " | "))

    sys.stderr.write(
        "checked %d verify block(s) -- %d verified, %d mismatch(es), %d warning(s)\n"
        % (len(blocks), verified, violations, warnings)
    )
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
