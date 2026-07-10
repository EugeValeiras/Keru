#!/usr/bin/env python3
"""
test-check-counts.py -- persistent test for the check-counts.py count verifier.

No test framework: run it with `python3 test-check-counts.py`.
Exit 0 = all pass; exit 1 = one or more failures.

Covers the pure parsing/safety layer and the end-to-end re-run/compare layer,
plus the SAFETY guarantee: a non-whitelisted or redirection-bearing command is
warned and NEVER executed (anchored on the real 0.1.6 actor-count miss shape).
"""

import importlib.util
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "check-counts.py")

_spec = importlib.util.spec_from_file_location("check_counts", SCRIPT)
cc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cc)

_failures = []


def check(name, ok):
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        _failures.append(name)


def run(fragment, root):
    p = subprocess.run([sys.executable, SCRIPT, fragment, root],
                       capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


# ---- unit: parse + normalize ---------------------------------------------

_frag = (
    "Intro.\n\n```verify\ngrep -rn foo pkg | wc -l\n21\n```\n\n"
    "```python\nnot a verify block\n```\n\n"
    "```verify\ngit ls-files | wc -l\n156\n```\n"
)
_blocks = cc.parse_verify_blocks(_frag)
check("parses both verify blocks", len(_blocks) == 2)
check("captures command + expected", _blocks[0] == ("grep -rn foo pkg | wc -l", "21"))
check("ignores non-verify fences", _blocks[1][0] == "git ls-files | wc -l")
check("normalize trims trailing blanks", cc._normalize("3\n\n\n") == "3")
check("normalize trims trailing ws", cc._normalize("a  \nb\t\n") == "a\nb")
check("normalize trims wc-style left pad", cc._normalize("      21\n") == "21")

# ---- unit: pipeline split + safety ---------------------------------------

check("splits a pipeline into stages",
      cc.pipeline_stages("grep -rn x pkg | wc -l") == [["grep", "-rn", "x", "pkg"], ["wc", "-l"]])
check("redirection makes it unsafe (None)", cc.pipeline_stages("cat x > y") is None)
check("semicolon makes it unsafe (None)", cc.pipeline_stages("grep x; rm y") is None)
check("command substitution unsafe (None)", cc.pipeline_stages("echo $(rm -rf /)") is None)
check("grep pipeline is safe", cc.is_safe(cc.pipeline_stages("grep -rc foo . | wc -l")))
check("git ls-files is safe", cc.is_safe(cc.pipeline_stages("git ls-files | wc -l")))
check("git push is NOT safe", not cc.is_safe(cc.pipeline_stages("git push origin main")))
check("rm is NOT safe", not cc.is_safe(cc.pipeline_stages("rm -rf /")))
check("awk is NOT whitelisted", not cc.is_safe(cc.pipeline_stages("awk '{print}' f")))
check("unsafe-token command is_safe(None) is False", not cc.is_safe(None))

# ---- end-to-end: re-run + compare ----------------------------------------

with tempfile.TemporaryDirectory() as root:
    with open(os.path.join(root, "a.txt"), "w") as fh:
        fh.write("foo\nfoo\nbar\n")        # 2 lines match foo
    with open(os.path.join(root, "b.txt"), "w") as fh:
        fh.write("foo\n")                  # 1 line matches foo

    # Correct count -> verified, exit 0. (grep -c on a single file prints just N.)
    ok_frag = os.path.join(root, "ok.md")
    with open(ok_frag, "w") as fh:
        fh.write("count:\n\n```verify\ngrep -c foo a.txt\n2\n```\n")
    code, out, err = run(ok_frag, root)
    check("correct count verifies (no MISMATCH)", "MISMATCH" not in out)
    check("correct count exits 0", code == 0)

    # Wrong count (the 0.1.6 actor-count shape) -> MISMATCH, exit 1.
    bad_frag = os.path.join(root, "bad.md")
    with open(bad_frag, "w") as fh:
        fh.write("claims 5:\n\n```verify\ngrep -c foo a.txt\n5\n```\n")
    code, out, err = run(bad_frag, root)
    check("wrong count is a MISMATCH", "MISMATCH" in out)
    check("MISMATCH shows expected vs actual", "expected: 5" in out and "actual:   2" in out)
    check("wrong count exits 1", code == 1)

    # SAFETY: a redirection command must WARN and NOT execute (no file written).
    evil_path = os.path.join(root, "pwned.txt")
    evil_frag = os.path.join(root, "evil.md")
    with open(evil_frag, "w") as fh:
        fh.write("```verify\ncat a.txt > pwned.txt\n(none)\n```\n")
    code, out, err = run(evil_frag, root)
    check("redirection command is warned, not run", "cannot verify" in out)
    check("redirection command did NOT write its file", not os.path.exists(evil_path))
    check("an unverifiable command alone does not fail the run", code == 0)

    # A pipeline over explicit files (no recursion -> no pollution from the .md
    # fragments that also contain "foo") -> deterministic count.
    multi_frag = os.path.join(root, "multi.md")
    with open(multi_frag, "w") as fh:
        fh.write("```verify\ngrep -l foo a.txt b.txt | wc -l\n2\n```\n")
    code, out, err = run(multi_frag, root)
    check("multi-file pipeline verifies", code == 0 and "MISMATCH" not in out)


print()
if _failures:
    print("%d FAILURE(S): %s" % (len(_failures), ", ".join(_failures)))
    sys.exit(1)
print("all checks passed")
sys.exit(0)
