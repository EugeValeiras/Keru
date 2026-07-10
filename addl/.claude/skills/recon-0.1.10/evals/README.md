# recon evals

Two layers, matching recon's mechanical-determinism doctrine (deterministic +
correctness-critical work is a tested hard-fail script, not prose):

| Layer | File | Deterministic? | Where it runs |
|---|---|---|---|
| False-anchor mutation harness | `run-evals.py` | **Yes** | CI / `python3 evals/run-evals.py` |
| Routing & gate-discipline prompts | `recon-prompts.md` | No (needs the model) | by hand, against the installed skill |

## `run-evals.py` — the deterministic half

Stands up one coherent fixture (a tiny brownfield repo + the clean R1
`system-cartography.md` a faithful run would emit), proves that fragment passes
**all four** validators (baseline green), then injects one false-anchor
regression at a time and asserts the matching validator hard-fails (exit 1):

| Mutation | Regression class | Validator | Doctrine |
|---|---|---|---|
| 1 | line cited past EOF | `check-anchors.py` | RE-01 |
| 2 | snippet on the wrong line (off-by-one) | `check-anchors.py` | RE-01 |
| 3 | verify-block count drift | `check-counts.py` | RE-01 |
| 4 | a repo file left uncovered | `repo-census.py coverage` | RE-01 ("nothing lost") |
| 5 | recon artifact in `docs/architecture/` | `check-workspace.py` | RE-05 |

```bash
python3 evals/run-evals.py     # exit 0 = every eval passed | 1 = one or more failed
```

Offline and git-free (census runs `--no-git`); no validator writes or networks.
It complements, not replaces, the per-validator unit tests in `tools/test-*.py`:
those test each script's internals; this proves the layer as a whole catches each
regression class against the same evidence a real fragment carries.

## `recon-prompts.md` — the model-driven half

The part that cannot be deterministic: does the skill route to the right gate,
hold gate discipline (one fragment per turn, refuse to skip/batch, reopen
cleanly), anchor every claim, and decline out-of-scope (redesign / review /
greenfield) work? Run each prompt against a real brownfield target (see EAI-89)
and score against the stated Expected behavior.
