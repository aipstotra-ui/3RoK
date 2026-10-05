# orbitlife (repo: 3RoK)

Open-source toolkit answering: **how long will an AI chip last on a given orbit, what limits it (radiation dose, single-event upsets, drag, heat), how do space-weather storms change that, which orbit is best, and what should the payload do in a storm?**

Audience: radiation, astrodynamics and GPU-reliability engineers. The bar: an expert at SpaceX or NVIDIA reads any number and can trace and check it.

Owner: Aiden (coding beginner). Explain each step in plain language as you work.

## Phase gate (mandatory)
- The roadmap is `docs/roadmap.md`. Work happens one phase at a time.
- At the end of a phase, post a phase report (built items and PRs, each exit criterion with evidence, subagent tables, new numbers with sources, open issues, needs from Aiden) and **stop**.
- Do not start the next phase until Aiden explicitly says so. Approval never carries over to the next phase.

## Layout
- `packages/py/orbitlife`: published Python core. **Source of truth for all physics and ML.**
- `packages/py/orbitlife-build`: unpublished builders for grids, models and fault-injection runs. Heavy dependencies live here only.
- `packages/ts/core`: `@orbitlife/core`. Only interpolates published grids, runs geometry and ONNX. It must match the Python golden fixtures in `fixtures/golden/`; never re-derive physics in TypeScript.
- `apps/web`: showcase site (Phase 6).
- `validation/`: reference cases (YAML), written before the code they check.
- `docs/adr/`: architecture decisions. Add an ADR before changing one.

## Ground rules
1. **No invented numbers.** Every constant lives in the constants registry as a typed `Quantity` with `source.kind` ∈ exact | measured | reference_model | fit | assumption | heuristic, plus a `docs/refs.bib` key when it has a source. Missing fact → call `researcher`.
2. **Heuristics are visible.** A `heuristic` or `assumption` value may feed a headline output only if the result's `flags` list it.
3. **Validation first.** Add `validation/` cases and unit tests before building a module. Report residuals honestly, including misses.
4. **ML hygiene.** Features at issue time T use only data available before T. Each test set is scored once and logged in `validation/score-log.md`. Calibration has its own slice.
5. **Frames, time and units are explicit** at every function boundary (name the frame, time scale and unit).
6. **Data never goes in git.** Data products are GitHub Release assets with a sha256 manifest.
7. Never weaken a test, tolerance or threshold to make a check pass.
8. No secrets in the repo. There is no server-side API key in this project.
9. Python: typed (`mypy --strict`), ruff-clean. TypeScript: strict, zod at external boundaries, no `any`.

## Work loop (each work item = one branch + PR)
1. Scope: goal, files, checks (in the PR description).
2. Research gate: `researcher` for any new external fact. `BLOCKING: yes` → stop and ask Aiden.
3. Validation first: add failing cases and tests.
4. Build.
5. Review: `physics-reviewer` if physics paths changed; `ml-auditor` if forecast/decide/ML paths changed; `/code-review` always.
6. Verify: `verifier` always; `validation-analyst` if science changed; `ui-qa` if `apps/web` or `assets/3d` changed.
7. Skeptic: `expert-skeptic` if any user-facing claim or number changed.
8. Open the PR with the gate results. Aiden merges.

Max 3 fix loops per gate. After the 3rd failure, or any BLOCKED, stop and report the failing rows.

## Commands
- `just setup`: install everything.
- `just verify`: all checks. Run before every commit.
- `just fmt`: auto-format.

## Git
- Never commit to `main` directly after Phase 0; use a branch per work item.
- Never force-push or delete anything on GitHub without Aiden's explicit OK.
