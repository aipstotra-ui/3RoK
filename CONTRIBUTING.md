# Contributing to orbitlife

Thanks for helping. orbitlife's value depends on trust, so contributions follow a few strict rules.

## Ground rules
1. **No unsourced numbers.** Every constant enters the constants registry as a typed `Quantity` with a source kind (`exact`, `measured`, `reference_model`, `fit`, `assumption`, `heuristic`) and, when it has one, a `docs/refs.bib` entry.
2. **Validation first.** A new model or a change to one comes with a case in `validation/` comparing it with a trusted reference. Report misses honestly.
3. **Never loosen a tolerance** just to make a check pass. If a reference disagrees, explain why in the case file.
4. **ML hygiene.** No future data in features, separate calibration and test slices, and each test set scored once (logged in `validation/score-log.md`).
5. **No data in git.** Data products are published as GitHub Release assets with a sha256 manifest.

## Setup
```bash
just setup
just verify
```

## Workflow
- One branch and one pull request per change. Describe the goal, the files changed and how it was checked.
- `just verify` must pass. CI runs the same checks.
- Architecture changes need an ADR in `docs/adr/`.
