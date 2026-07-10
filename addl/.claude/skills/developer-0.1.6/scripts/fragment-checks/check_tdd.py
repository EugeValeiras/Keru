#!/usr/bin/env python3
"""check_tdd.py -- deterministic TDD-first verification of a spec-kit tasks.md (P6 / D-02).

spec-kit's /speckit-tasks is TEST-OPTIONAL by default: unless it is explicitly directed
toward TDD, it ships tasks.md with no tests and D5 cannot pass honestly. Our D-02 rule
requires tests-first. This makes the check deterministic instead of an eyeball pass.

spec-kit (0.11.x) organizes tasks BY USER STORY: a "## Phase N: User Story M" block, with
a "### Tests for User Story M" subsection FOLLOWED BY an "### Implementation for User Story
M" subsection. The "## Phase 1: Setup" and "## Phase 2: Foundational" phases are blocking
infrastructure (project scaffolding, base entities) -- legitimately NOT test-first, and
spec-kit even puts the foundational tests AFTER the foundational scaffolding. So the TDD
rule is applied PER USER STORY only; Setup/Foundational/Polish are exempt. Within each user
story: there must be >=1 test task, and no implementation task may precede the first test
task.

    check_tdd.py <tasks.md>

Exit codes:  0 TDD-first / 1 not TDD-first (gate blocked) / 2 usage / file not found
Stdlib-only. Self-test:  check_tdd.py --self-test
"""

import argparse
import os
import re
import sys

OK, FINDINGS, ERROR = 0, 1, 2

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
# a task line: "- [ ] T001 ...", "- [X] T017[P] ...", "- [x] T019Create ..." (spec-kit is
# inconsistent about the space after the id, so do not require one).
TASK_RE = re.compile(r"^\s*[-*]\s*\[[ xX]\]\s*(T\d+[a-zA-Z]?)")
STORY_RE = re.compile(r"user\s+story\s*#?\s*(\d+)", re.IGNORECASE)
US_TAG_RE = re.compile(r"\[US(\d+)\]")
# a task whose description names a test file / test path, used when the heading context is
# ambiguous. Section context ("### Tests for ...") is the primary signal; this is the backup.
TEST_HINT_RE = re.compile(
    r"(?:^|[\s`(/])tests?/"          # a tests/ or test/ path segment
    r"|/tests?/"
    r"|\btest_\w"                    # test_foo
    r"|\w_test[._]"                  # foo_test.
    r"|\.test[._]"                   # .test.
    r"|\.spec[._]"                   # .spec.
    r"|\w(?:Test|Tests)\.\w",        # ResultTests.cs
    re.IGNORECASE)


def parse_tasks(text):
    """Walk the file, tracking (user-story, test/impl) context from headings, and return an
    ordered list of {id, story, is_test}. story is None for Setup/Foundational/Polish."""
    story = None
    test_ctx = False
    out = []
    for ln in text.splitlines():
        m = HEADING_RE.match(ln)
        if m:
            level, title = len(m.group(1)), m.group(2)
            sm = STORY_RE.search(title)
            if level <= 2:
                # a top-level phase boundary resets the story (we may have left it)
                story = int(sm.group(1)) if sm else None
            elif sm:
                story = int(sm.group(1))
            low = title.lower()
            if "test" in low:
                test_ctx = True
            elif "implement" in low:
                test_ctx = False
            else:
                test_ctx = False  # neutral heading (e.g. the "## Phase N: User Story M" line)
            continue
        tm = TASK_RE.match(ln)
        if not tm:
            continue
        us = US_TAG_RE.search(ln)
        st = int(us.group(1)) if us else story
        is_test = test_ctx or bool(TEST_HINT_RE.search(ln))
        out.append({"id": tm.group(1), "story": st, "is_test": is_test})
    return out


def check(text):
    tasks = parse_tasks(text)
    if not tasks:
        return ["no task lines (- [ ] TNNN ...) found -- this is not a spec-kit tasks.md"]

    findings = []
    by_story = {}
    for t in tasks:
        if t["story"] is None:
            continue  # Setup / Foundational / Polish -- not feature behavior, exempt
        by_story.setdefault(t["story"], []).append(t)

    if not by_story:
        # no user-story structure at all: cannot verify per-story ordering, so enforce the
        # minimum D-02 bar -- tests must at least exist somewhere.
        if not any(t["is_test"] for t in tasks):
            findings.append("no user-story sections and no test tasks found -- tasks.md is not "
                            "TDD-structured; direct /speckit-tasks toward TDD (D-02)")
        return findings

    for s in sorted(by_story):
        grp = by_story[s]
        test_pos = [i for i, t in enumerate(grp) if t["is_test"]]
        impl_pos = [i for i, t in enumerate(grp) if not t["is_test"]]
        if impl_pos and not test_pos:
            findings.append("User Story %d has %d implementation task(s) but NO test task(s) -- "
                            "spec-kit ships test-optional; D-02 requires a TDD-first list" % (s, len(impl_pos)))
        elif test_pos and impl_pos and min(impl_pos) < min(test_pos):
            findings.append("User Story %d: implementation task %s precedes any test task -- "
                            "not TDD-first (D-02)" % (s, grp[min(impl_pos)]["id"]))
    return findings


def report(findings, path):
    print("TDD-first verification (P6 / D-02)")
    print("  tasks: %s" % path)
    print()
    if not findings:
        print("VERDICT: TDD-first -- every user story leads with its tests.")
        return
    print("Findings (%d):" % len(findings))
    for f in findings:
        print("  - %s" % f)
    print()
    print("VERDICT: BLOCKED -- a user story is missing tests or lists implementation before "
          "its tests. Re-run /speckit-tasks directing it to a TDD-first list (tests precede "
          "their implementation, per user story); do not patch tasks.md by hand.")


# --- self-test -----------------------------------------------------------------
_SETUP = """# Tasks: Demo

## Phase 1: Setup (Shared Infrastructure)
- [ ] T001 Create project structure with src/ and tests/ folders.
- [ ] T002 [P] Configure linting and formatting tools.

## Phase 2: Foundational (Blocking Prerequisites)
- [ ] T003 Create src/Domain/Result.cs scaffolding.
- [ ] T004 Create src/Domain/Error.cs base entity.
"""
_US1_TDD = """
## Phase 3: User Story 1 - Record entry (Priority: P1)

### Tests for User Story 1 (write FIRST, ensure they FAIL) [warn]
- [ ] T005 [P] [US1] Contract test in tests/contract/test_record.py
- [ ] T006 [P] [US1] Integration test in tests/integration/test_record.py

### Implementation for User Story 1
- [ ] T007 [US1] Implement src/services/RecordManager.cs
- [ ] T008 [US1] Wire src/api/Endpoint.cs
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

    # clean per-story TDD-first; also proves Setup/Foundational impl-before-tests is exempt
    expect("clean per-story TDD-first passes (Setup/Foundational exempt)",
           not check(_SETUP + _US1_TDD))

    # SEEDED: a user story with implementation tasks but no Tests subsection
    omitted = _SETUP + """
## Phase 3: User Story 1 - Record entry (Priority: P1)

### Implementation for User Story 1
- [ ] T005 [US1] Implement src/services/RecordManager.cs
- [ ] T006 [US1] Wire src/api/Endpoint.cs
"""
    f = check(omitted)
    expect("user story with impl but no tests is caught",
           any("User Story 1" in x and "no test" in x.lower() for x in f))

    # SEEDED: implementation listed before the tests within a story
    reordered = _SETUP + """
## Phase 3: User Story 1 - Record entry (Priority: P1)

### Implementation for User Story 1
- [ ] T005 [US1] Implement src/services/RecordManager.cs

### Tests for User Story 1
- [ ] T006 [US1] Unit test in tests/unit/test_record.py
"""
    f = check(reordered)
    expect("implementation before tests (within a story) is caught",
           any("User Story 1" in x and "precedes" in x and "T005" in x for x in f))

    # SEEDED: second story omits tests while the first is fine -- proves it is per-story
    two = _SETUP + _US1_TDD + """
## Phase 4: User Story 2 - List entries (Priority: P2)

### Implementation for User Story 2
- [ ] T009 [US2] Implement src/services/ListManager.cs
"""
    f = check(two)
    expect("second story missing tests is caught (per-story, not just the first)",
           any("User Story 2" in x and "no test" in x.lower() for x in f) and
           not any("User Story 1" in x for x in f))

    # no user-story structure + no tests -> minimum D-02 bar fails
    nostory_notests = """# Tasks: Demo
## Phase 1: Setup
- [ ] T001 Create the project structure and modules.
## Phase 2: Core
- [ ] T002 Implement src/x.py
- [ ] T003 Implement src/y.py
"""
    expect("no-story + no-tests is caught (minimum D-02 bar)",
           any("TDD-structured" in x for x in check(nostory_notests)))

    # no user-story structure but tests exist somewhere -> passes the minimum bar
    nostory_tests = """# Tasks: Demo
## Phase 1: Setup
- [ ] T001 Create the project structure and modules.
## Phase 2: Tests First
- [ ] T002 Contract test in tests/contract/test_x.py
## Phase 3: Core
- [ ] T003 Implement src/x.py
"""
    expect("no-story but tests-present passes the minimum bar", not check(nostory_tests))

    # the US-tag assigns a story even when the heading is generic
    tag_only = _SETUP + """
## Phase 3: Feature work
- [ ] T005 [US1] Implement src/services/RecordManager.cs
"""
    expect("US-tag assigns the story (impl-only US1 -> no tests) is caught",
           any("User Story 1" in x for x in check(tag_only)))

    print("\nself-test: %d passed, %d failed" % (passed, failed))
    return OK if failed == 0 else FINDINGS


def _read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_tdd.py",
        description="Deterministic TDD-first verification of a spec-kit tasks.md (D-02).")
    parser.add_argument("tasks", nargs="?", help="the feature tasks.md")
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixtures and exit")
    ns = parser.parse_args(argv)

    if ns.self_test:
        return self_test()
    if not ns.tasks:
        parser.error("expected <tasks.md> (or --self-test)")
    if not os.path.isfile(ns.tasks):
        print("error: file not found: %s" % ns.tasks, file=sys.stderr)
        return ERROR

    findings = check(_read(ns.tasks))
    report(findings, ns.tasks)
    return FINDINGS if findings else OK


if __name__ == "__main__":
    sys.exit(main())
