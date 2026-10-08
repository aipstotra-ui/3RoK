# 3RoK: from hackathon demo to an open-source toolkit for AI chips in orbit

## Context

BRHSpaceX (also called 3rok and StarMind Nav) was built in about two days for BigRed//Hacks 2026. The question it answers stays the same: **for an AI chip flown in low Earth orbit, how long does it last on a given orbit, what limits it (radiation dose, single-event upsets, drag, heat), how do storms change that, which orbit is best, and what should the payload do when a storm arrives?**

The new goal is an **open-source toolkit good enough that radiation, astrodynamics and GPU-reliability engineers (the SpaceX and NVIDIA kind) trust it, use it and remember it.** The web app becomes the showcase.

Your decisions so far:
- Remove Grok and xAI completely.
- Start a **brand-new 3RoK repo**. BRHSpaceX `origin/main` (990eeb4) serves only as reference material; the local checkout is 19 commits behind and is not the source.
- Use a **Python scientific core (PyPI) plus a thin TypeScript package (npm)**.
- Choose a **new descriptive name** in Phase 0.
- Only you and Claude Code work on it.

**Starting stance: assume nothing in the old system is good enough, including the 3D globe and the spacecraft model** (procedural boxes in `components/globe/StarmindModel.tsx`). Old code is reference only. Nothing comes over until it passes a reference test in the new repo.

## The quality bar (what makes SpaceX and NVIDIA engineers take it seriously)

1. **Every number can be traced and checked against something they already trust**, such as SPENVIS, CREME96, NRLMSIS, Orekit and flight data. A public validation report shows the residuals, including where we're wrong.
2. **Correct reference frames and time scales:** TEME, GCRS and ITRS frames; UTC, TT and UT1 time. Units are explicit at every boundary. Reviewers check these first.
3. **Answers in their language:**
   - **For NVIDIA:** silent-data-corruption rate per GPU-hour, HBM/SRAM upsets, ECC and scrub effects, checkpoint overhead and goodput, and accuracy loss of a real model under the predicted upset rate.
   - **For SpaceX:** fleet-level answers for a whole shell (expected failures per year, compute availability, decay under storms), tested against the real Feb 2022 Starlink loss, with the known storm-time under-prediction of empirical density models reported.
4. **Honest uncertainty:** ranges, not single numbers. Assumptions are typed and listed with every result. No overclaiming anywhere: README, docs or UI.
5. **Engineering polish:**
   - `pip install` and `npm i` just work, with typed APIs and a CLI.
   - Reproducible data with DOIs, CI on everything, fast vectorized code, a beautiful and physically correct 3D view.
   - Notebooks they can run in 5 minutes.
6. **A flagship write-up:** a methodology paper (JOSS or arXiv) and 3 case studies that people share.

## Review findings (summary; full detail came from 3 read-only audits)

**Science**
- The SEU cross-section of 1e-14 cm²/bit is invented and about 3–5 orders of magnitude too high. The ECC fractions and the die-area rule are invented too.
- The storm multiplier is applied to trapped protons, which storms don't raise. SEP and cosmic rays are not modeled.
- Density is taken at a single point, local midnight, so lifetimes come out too long. The storm drag factor applies for the whole lifetime.
- Thermal has no solar, albedo or Earth-IR heat input, so it never affects the optimizer. Eclipse is never scored.
- There are 3 conflicting SAA models.
- About 145 estimate or UNVERIFIED labels, some on exact constants. No tests compare results with reference values.
- Worth keeping as an *approach*: the AP8/AE8 + SHIELDOSE-2 grid (`scripts/orbit/dose_table.py`).

**ML**
- About 1 h of data leakage: OMNI row t covers [t, t+1) but is used at time t, and `ml/tests/test_leakage.py` can't catch it.
- Calibration reuses the early-stopping slice. Dst +24 h coverage is 0.72 against a 0.80 target.
- Skill is measured only against persistence.
- The policy classifier is flawed: a lag bug in `ml/oof_forecasts.py:39-41`, labels built with hindsight, the test set scored twice, about 1.8 % real gain, and a simple formula would do the same job.

**App and 3D**
- One giant client page with duplicated fetch and ONNX pipelines.
- About 9 MB of feed data on every load, ONNX WebAssembly from a CDN, and 18.7 MB of snapshots packed into a serverless function.
- Globe defects: the trail is never added, the spacecraft doesn't move, the map may be mirrored east–west, and LTAN never changes RAAN.
- The optimizer recomputes on the main thread every frame. The spacecraft is boxes.
- Dead code and two CSS systems.

**Repo**
- About 58 MB of data in plain git with no refresh process.
- No CI, and verification needs a local 565 MB venv.
- Five names for the project, duplicated Cursor/Claude agent setups, stale docs, about 11 merged branches.

## Target architecture

```
orbitlife/                          GitHub aipstotra-ui/3RoK (rename later; GitHub redirects)
  pyproject.toml                 uv workspace: ruff, mypy --strict, pytest, hypothesis
  pnpm-workspace.yaml            pnpm, TS strict, vitest, Playwright, Biome
  justfile                       one entry point: just verify | validate | build-data | web
  packages/py/orbitlife/            PyPI core. src/orbitlife/
      quantity, constants, schema      typed values with provenance, constants registry, pydantic models
      time, frames, orbit              astropy/skyfield-backed frames & time scales; J2 propagation, SSO, beta, eclipse
      env/                             trapped belts (AP8/AE8 grid; AP9/AE9 optional), GCR, SEP, geomagnetic cutoff, aurora
      effects/                         TID, SEE (proton Bendel/Weibull, heavy-ion LET-Weibull), SEL (destructive latchup), displacement-damage hook
      drag, thermal                    NRLMSIS orbit-averaged density + lifetime; radiative heat balance
      workload/                        SDC & goodput: ECC/scrub, Young–Daly checkpointing, model-level fault impact
      fleet/                           whole-constellation Monte Carlo (NumPy; optional JAX/CuPy GPU backend)
      forecast, decide                 space-weather quantile forecasts; expected-cost decisions
      mission, rank, cli, data         assess(), Pareto ranking, CLI, pooch data fetch
  packages/py/orbitlife-build/      unpublished: grid builders (SpacePy/IRBEM, pymsis), ML training, fault-injection runs
  packages/ts/core/              npm @orbitlife/core: generated zod types, grid interpolation, geometry, lifetime,
                                 ONNX runner (self-hosted WebAssembly), decide(), SWPC feed clients
  apps/web/                      Vite + React static site; CesiumJS globe (lazy-loaded)
  assets/3d/                     glTF spacecraft + its source and license
  schemas/  fixtures/golden/  validation/  data-products/  notebooks/  docs/  paper/
  .claude/agents/  CLAUDE.md  LICENSE(MIT)  CONTRIBUTING.md  CITATION.cff
```

**Ground rules (these go into `CLAUDE.md`)**
1. **Python is the single source of truth.** TypeScript only interpolates the grids Python publishes and runs geometry that has to match golden fixtures generated by Python.
2. **Schemas:** pydantic v2 → `schemas/*.json` → generated zod. Every document carries `schemaVersion`: MissionSpec, DeviceSpec, WorkloadSpec, FleetSpec, Assessment, ForecastBundle, CostMatrix, DataManifest.
3. **Provenance is typed:** `Quantity{value, unit, uncertainty?, source{kind: exact|measured|reference_model|fit|assumption|heuristic, ref?: bibkey}}`.
   - One constants registry links to `docs/refs.bib`.
   - A heuristic value can't feed a headline result unless the Assessment flags it.
   - This keeps the hackathon's best habit (honest labels) and makes it enforceable.
4. **Validation comes first.** Reference cases are written before the module. Each test set is scored once and logged.
5. **Data lives outside git:**
   - Each `data-vYYYY.N` GitHub Release carries a manifest (sha256, generator version, input hashes, licenses).
   - Zenodo gives every release a DOI.
   - A scheduled CI job refreshes the live-feed snapshots.

## Subagents (new roster, in `.claude/agents/`)

The 3 hackathon agents (`researcher`, `ml-auditor`, `verifier`) get rewritten for the new repo. The `.cursor/` copies are dropped. Every agent is read-only except where noted, returns a fixed-format table, and never commits.

| Agent | Tools | When it runs | Returns |
|---|---|---|---|
| **researcher** | Read, Grep, Glob, WebSearch, WebFetch | Before building anything that needs a fact not yet in `docs/refs.bib` or the constants registry: a model spec, device test data, a dataset format, a published reference value | `Item, Value, Unit, Source (DOI/URL), Accessed, Status (CONFIRMED/CORRECTED/UNVERIFIED), BibTeX`; ends with `BLOCKING: yes/no` |
| **physics-reviewer** | Read, Grep, Glob, Bash (read-only commands) | Any diff touching `orbit, frames, time, env, effects, drag, thermal, fleet` or a grid builder | `Severity (BLOCKER/SHOULD-FIX/OK), File:line, Issue (units, frame/time scale, model used outside its valid range, double counting, sign, wrong population), Reference, Fix` |
| **ml-auditor** | Read, Grep, Glob, Bash | Any diff touching `forecast, decide, workload` fault-injection stats, or `-build/ml` | Leakage, split purging, test-set reuse (checks the score log), calibration on its own slice, honest baselines, features unavailable in real time. Same severity table |
| **verifier** | Bash, Read, Grep, Glob (no edits) | End of every work item and after every fix | `VERIFY <item> attempt n: PASS/FAIL/BLOCKED` plus a check table. Always runs `just verify` first |
| **validation-analyst** | Bash, Read, Grep, Glob (no edits) | When a science module or data release changes; also nightly | Runs `just validate` and explains each residual as a *bug*, a *model limitation* (with a cited reason) or a *reference mismatch*; drafts text for the validation report |
| **ui-qa** | Built-in browser tools (or gstack `/browse`, per your global CLAUDE.md), Read, Bash | Any change under `apps/web` or `assets/3d` | Console errors, performance budgets, accessibility (axe), mobile layout, URL-state round-trip, globe correctness (sub-satellite point vs Skyfield, terminator vs sun position, east/west), screenshots |
| **expert-skeptic** | Read, Grep, Glob, WebSearch | Before any change to user-facing claims (README, docs, UI copy, paper, case studies) and before every release | Reviews like a SpaceX radiation/astrodynamics engineer and an NVIDIA GPU-reliability engineer: overclaims, missing caveats, numbers that would lose a reader's trust, missing comparisons. `Claim, Where, Concern, Required evidence or rewording` |

General correctness review uses the built-in `/code-review`; no custom agent is needed for that.

**Work loop for each work item (each item is one PR)**
1. **Scope:** I write a short task note in the PR description covering goal, files and checks.
2. **Research gate:** call `researcher` if the item needs a new external fact. `BLOCKING: yes` means I stop and ask you.
3. **Validation first:** add or extend `validation/` cases and unit tests. They fail at this point.
4. **Build.**
5. **Review gates:** `physics-reviewer` and/or `ml-auditor` if their trigger paths changed, plus `/code-review`.
6. **Verify:** `verifier` always; `validation-analyst` if science changed; `ui-qa` if the web app changed.
7. **Skeptic:** `expert-skeptic` if any claim or user-facing number changed.
8. Open the PR with the gate results. You review and merge.
9. At the end of the phase, post the phase report and **wait for your go-ahead** (see "Phase gate" below).

At most 3 fix loops per gate. After that, or on any BLOCKED, I stop and report the failing rows.

## Per-module disposition (source: BRHSpaceX origin/main)

| Source | Disposition |
|---|---|
| Orbit geometry `lib/engine/orbit/{elements,angles,sun,eclipse,j2,sso,hohmann,range}.ts` | **Rebuild** in Python on astropy/skyfield frames; old code is a cross-check only |
| `scripts/orbit/dose_table.py` (AP8/AE8+SHIELDOSE-2), `ml/{parse_omni,fetch_goes_history,fetch_gfz_kp,scrape_sep,may2024}.py`, `lib/data/{swpc,donki}.ts` | **Port after tests** (useful data-ingest and IRBEM know-how) |
| Everything else in `lib/engine/**`, `lib/presets.ts`, `lib/scenario/*`, `ml/{features,splits,train_forecast,evaluate,export_onnx,climatology}.py` | **Rebuild** (reference only) |
| `lib/cases/*` (zod + localStorage case store) | **Rebuild** on the generated schemas; the idea of a case is kept |
| `components/**`, `app/**`, `lib/engine/globe/*`, workers, `3rok-design-system/` | **Rebuild**. Keep only the design tokens and fonts, if you still like the look |
| `lib/grok/*`, `app/api/grok/*`, `Copilot.tsx`, `VoiceTest.tsx`, `AiAnalysis.tsx`, `useAiAnalysis.ts`, policy pipeline (`ml/{build_oracle,oof_forecasts,train_policy,evaluate_policy}.py`, `lib/ml/policy*.ts`, `lib/engine/{actions,costCheck}.ts`), `lib/globe/*`, shadcn/Tailwind leftovers | **Drop** |
| `docs/research/{reference-values,engine-constants,data-sources,orbit-model,findings,benchmarks}.md`, `data/orbit/refs/citations.md` | **Mine** for sources → `refs.bib`; the researcher re-confirms each one |
| `.cursor/`, old agents, `docs/{cursor-log,PLAN-v2}.md`, `docs/archive`, hackathon-only docs | **Drop** |

## Phases

Order: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7. Every work item follows the loop above.

**Phase gate (required):** at the end of every phase I stop and post a phase report. The report covers:
- what was built and the merged PRs
- each exit criterion with its PASS/FAIL evidence
- the final subagent tables
- new numbers and their sources
- open issues
- what I need from you

**I do not start the next phase until you explicitly confirm.** Approving one phase does not carry over to the next. If you ask for changes, I make them inside the same phase and report again. Phases 3 and 4 don't depend on each other, but they still run one after the other, each with its own approval.

### Phase 0: Foundations and agents
- **Name:** `orbitlife` (chosen 2026-10-05; free on PyPI and npm).
- **Repo:** the old 3RoK repo was deleted and recreated empty (Aiden, 2026-10-05); the scaffold is the first history.
- **Tooling:**
  - uv and pnpm workspaces, plus `just`.
  - GitHub Actions jobs:
    - `py-core` (Python 3.11–3.13, Ubuntu and macOS)
    - `py-build` (IRBEM cached)
    - `ts` (Node 22/24)
    - `schema-drift`, `golden-parity`, `data-manifest`, `docs`, `web`
    - nightly `validate`
- **Agents and docs:**
  - Write the 7 subagents and `CLAUDE.md` (ground rules plus work loop), `CONTRIBUTING.md` and `CITATION.cff`.
  - Write ADRs for: frames/time library, units, schema generation, the visualization engine (CesiumJS), data hosting.
- **Data and packages:**
  - Publish the old data as `data-v0`.
  - Name reservation on PyPI and npm moved to Phase 7 (Aiden, 2026-10-05): GitHub alone is enough until release.
- **Exit:**
  - CI is green on empty packages.
  - Each agent runs on a dummy PR and returns its table format.
  - `data-v0` downloads and passes its hash check.

### Phase 1: Requirements and validation-first spec
- **Reference missions:**
  - 550 km / 53° (Starlink shell)
  - 560 km / 97.6° (Starlink polar)
  - dawn-dusk SSO at 600 and 800 km
  - ISS 420 km / 51.6°
  - 1200 km / 87.9° (OneWeb-like)
- **Reference devices,** each with cited test data (TID, SEU, and **SEL**: LET threshold and saturated cross-section, or "no SEL up to LET X") or flagged `heuristic`:
  - DDR4/DDR5
  - HBM3 stack
  - GPU on-die SRAM
  - a rad-hard SRAM
  - Google's TPU v6e proton results (Project Suncatcher, 2025; the researcher confirms the numbers)
- **Reference workloads:** ResNet-50 inference; a ~1B-parameter LLM's inference and a training step.
- **`validation/` cases:** written now, with source, quantity and tolerance (the tolerance being a labeled design choice):
  - SPENVIS dose-depth curves
  - CREME96 SEE rates
  - CREME96 SEL rates for a device with a published SEL Weibull fit
  - Orekit/GMAT eclipse and beta angle
  - Vallado SSO inclination
  - ISS decay between reboosts
  - Tiangong-1 final year
  - Feb 2022 Starlink Group 4-7 loss
  - NOAA SWPC 3-day forecast verification
  - published on-orbit memory upset rates
- **API sketch:** `assess`, `rank`, `forecast`, `decide`, `fleet.simulate`, `workload.impact`, plus the CLI verbs.
- **Exit:**
  - Every case is in YAML with a resolved source; the researcher has run on all of them.
  - The suite runs and is red where expected.
  - `expert-skeptic` has reviewed the case list for gaps.

### Phase 1 extension (approved by Aiden 2026-10-06, after the Phase 1 exit review)
Closes the expert-skeptic's top gaps (docs/open-issues.md, "Phase 1 exit") before any physics code exists.

| Item | Work | Needs Aiden? |
|---|---|---|
| E1 | Expected-miss marker: `expected: documented_miss` plus a reason. It reports KNOWN_MISS, never PASS, doesn't break CI, and keeps the residual | no |
| E2 | Shields-1 same-model cases (reproduce the source's NOVICE values) | no |
| E3 | Orbit geometry: beta angle (Boain), Orekit umbra/penumbra (we run Orekit, open source), Vallado 2006 SGP4 verification vectors, one GCRS↔ITRS example | no |
| E4 | Flux-geometry ADR (omnidirectional vs per-sr; planar-target factor), sourced | no (researcher) |
| E5 | Forecast protocol v2: Feb 2022 replay, threshold-weighted CRPS, tail quantiles, physics baselines (Newell / Burton), Kyoto provisional coverage | no (researcher) |
| E6 | Data for GPU memory: an on-die SRAM entry, MBU/ECC fields, a sea-level (JESD89A) cross-check, a Weibull SEL source, plus schema hygiene (effect vs outcome, CONFIRMED_ABSTRACT) | no (researcher) |
| E7 | Self-run **CREME96** SEU/SEL cases (Kintex Weibull, a proton case, a Weibull SEL) for the reference missions | **yes: CREME96 account; Aiden runs the inputs Claude prepares** |
| E8 | Self-run **SPENVIS** dose-depth for every reference mission, all settings recorded | **yes: SPENVIS account; same** |
| E9 | Drag cases a correct model should pass: ISS TLE decay between reboosts, May 2024 storm decay | **yes: Space-Track account to download TLE history**; plus researcher for published May 2024 analyses |

Exit: E1–E9 merged (or a documented reason for each that cannot be done), and expert-skeptic re-reviews the case list.

### Phase 2: Python physics core
- **Time and frames:** built on astropy/skyfield. Orbit-averaging uses vectorized J2 propagation sampled across precession cycles.
- **Environment:**
  - AP8/AE8 grid over altitude 300–1500 km × inclination 0–100° × shielding 0.5–20 mm Al × solar min/max (AP9/AE9 mean and 95th percentile optional if licensing allows)
  - GCR from ISO 15390 or Badhwar-O'Neill, with a geomagnetic cutoff that depends on Kp
  - SEP worst-day and worst-week percentiles from the event record
  - ESP-PSYCHIC design-confidence SEP fluence (Xapsos et al.), needed by the SPENVIS dose-depth cases (added PR #9); research and an ADR before building
  - the SAA defined from the flux grid (one model, not three)
- **Effects:**
  - TID behind shielding
  - SEE: proton Bendel/Weibull fits, heavy-ion LET-Weibull with RPP and integral-LET
  - storms act on SEP and outer-belt electrons only
  - multi-bit upsets get their own parameter
- **Single-event latchup (SEL), added 2026-10-05 at Aiden's request:**
  - heavy-ion SEL rate from the device's LET-Weibull fit (same RPP and integral-LET machinery as SEE), plus proton-induced SEL where test data show it
  - temperature dependence (SEL sensitivity rises with temperature), driven by the thermal model's operating temperature; sourced per device or flagged `heuristic`
  - storms raise SEL risk through SEP heavy ions; trapped protons only matter for proton-sensitive parts
  - mitigation: a latchup protection circuit (current sense and power cycle) turns a destructive event into a recoverable one with a stated probability and downtime; probability sourced or flagged `heuristic`
  - outputs: destructive SEL probability per chip per year (with uncertainty) and recoverable SEL events and downtime per year
  - devices with no SEL test data say so in the result; they never get a silent zero
- **Drag and lifetime:**
  - NRLMSIS 2.0 averaged over latitude and local time
  - F10.7/Ap percentile schedules
  - storm Ap applied only during the storm window
  - uncertainty on the ballistic coefficient
- **Thermal:** orbit-averaged and transient balance with solar, albedo and Earth-IR terms, driven by beta angle and eclipse.
- **`assess()` and `rank()`:**
  - Pareto ranking over altitude × inclination × LTAN
  - Monte Carlo uncertainty
  - the binding limit explained per mechanism
- **Exit:**
  - Every Phase 1 science case is green, or documented as a model limitation by `validation-analyst`.
  - SEL rates match CREME96 within a factor of 2 for the same Weibull parameters.
  - `physics-reviewer` is clean.
  - `docs/science/validation.md` is generated automatically.
  - `data-v1` is released.

### Phase 3: Space-weather forecasting and decisions (ML redo)
- **Leakage:**
  - Use only rows up to T−1 h and only finished Kp blocks.
  - Make the leakage test exclusive, and add a hypothesis property test: changing any data at or after T must leave the features unchanged.
  - Real-time solar wind gets the same L1-to-bow-shock lag treatment as OMNI.
- **Splits:** train up to 2016; early stopping 2017–19; calibration 2020–21; test 2022–25; 48 h purges; each set scored once and logged.
- **Model:** multi-quantile LightGBM at 21 levels (0.01, 0.05–0.95, 0.99), calibrated with the per-level shift in `validation/forecast-protocol.md` §4.7. A no-solar-wind sub-model is the pre-registered fallback (§3.6). All self-hosted ONNX files ship as one hashed bundle.
- **Metrics:**
  - CRPS and pinball loss, coverage overall and in storms
  - threshold-weighted CRPS at the storm thresholds (protocol v2)
  - baselines: persistence, climatology, 27-day recurrence, **NOAA SWPC's archived 3-day forecast**, and the physics baselines O'Brien–McPherron (Dst) and a Newell-coupling regression (Kp)
  - storm-event scores: hit rate, false-alarm rate, Heidke skill score, Brier score, reliability diagrams
  - model cards
  - the February 2022 storm replay (protocol v2 §7, not a score)
- **Decision layer:** `decide(quantiles, CostMatrix)` chooses by expected cost. Measure regret against the oracle, always-nominal and a persistence threshold.
- **Exit:**
  - `ml-auditor` is clean.
  - The model beats climatology and persistence on CRPS at every horizon.
  - The comparison with NOAA is reported honestly whichever way it goes.

### Phase 4: AI-workload and fleet reliability (the NVIDIA and SpaceX hook)
- **`workload/`:**
  - Upset rate → silent-data-corruption (SDC) and detected-error rates per GPU-hour, from memory footprint, ECC type (SECDED or chipkill) and scrub interval.
  - Young–Daly optimal checkpoint interval, goodput, and the compute lost per storm.
- **Fault-injection harness** (in `-build`, PyTorch, CUDA if available):
  - Flip bits in weights and activations for the reference workloads.
  - Publish accuracy-vs-upset-rate curves as a data product so `workload.impact()` can use them.
- **`fleet/`:** whole-shell Monte Carlo giving expected chip failures per year (TID wear-out plus destructive SEL), compute availability, storm-driven decay and replacement rate. NumPy by default, optional JAX/CuPy GPU backend with a benchmark.
- **Exit:**
  - The analytic SDC model matches injection results within the stated tolerance.
  - A fleet run of 10,000 satellites × 1,000 scenarios has a published benchmark.
  - `physics-reviewer`, `ml-auditor` and `expert-skeptic` are clean.

### Phase 5: `@orbitlife/core` (TypeScript)
- Scope: zod types, a trilinear interpolator, geometry, the lifetime integrator, the ONNX runner, `decide()`, a light `workload` lookup and the feed clients.
- **Exit:**
  - Golden parity within 1e-6 relative error (1 % for the integrator).
  - Works in Node and the browser.
  - Under 60 KB gzipped, not counting onnxruntime.

### Phase 6: Web showcase and 3D rebuild
- **Routes:**
  - `/explore`: orbit, device and workload → lifetime, what limits it, SDC per GPU-hour, goodput
  - `/compare`: Pareto plot
  - `/fleet`
  - `/weather`: live fan charts plus a recommended action
  - `/replay`: Oct 2003, Feb 2022, May 2024
  - `/cases`
  - docs
- **State and export:**
  - A versioned MissionSpec in the URL hash.
  - Export to JSON, Markdown or PDF with a provenance table and data version.
- **3D, rebuilt from scratch on CesiumJS (lazy-loaded):**
  - **Frames:** correct inertial and Earth-fixed frames, time-dynamic with a clock and timeline.
  - **Imagery:** offline Natural Earth imagery, so no Cesium Ion token is needed.
  - **Lighting:** sun direction, day/night terminator, eclipse shadow.
  - **Radiation:** AP8 flux shown as altitude slices or isosurface shells, the SAA contour at the chosen altitude, live OVATION aurora, and the SEP polar-cap cutoff moving with Kp.
  - **Starlink:** live GP elements propagated with SGP4 in a worker and drawn as instanced points.
  - **Your spacecraft:**
    - Ground track and 3D path, colored by dose rate.
    - A real **glTF spacecraft** (self-authored or from NASA 3D Resources, license recorded): PBR materials, nadir-pointing attitude, sun-tracking arrays, and a true-scale/exaggerated toggle with a label.
  - **Interop:** CZML export so engineers can open the scenario in Cesium or STK.
- **Budgets:**
  - initial JS under 200 KB gzipped; the globe chunk loads only on globe routes
  - LCP under 2 s
  - globe at 60 fps with 6,000 or more satellites
  - ranking runs in a worker
- **Exit:**
  - `ui-qa` is clean on every route, including the globe-correctness checks: sub-satellite point within 1 km of Skyfield, terminator matching the sun.
  - Lighthouse performance is 90 or higher.
  - Playwright and visual-regression tests pass in CI.

### Phase 7: Release 1.0 and outreach
- **Publishing:**
  - Create PyPI and npm accounts (Aiden), check `orbitlife` is still free, then publish via trusted publishing.
  - Docs site: quickstart, science, validation report, model cards, "add your device or workload".
  - Zenodo DOIs.
- **Notebooks and case studies:**
  1. "Where should an orbital AI data center fly?"
  2. "The May 2024 superstorm through a GPU constellation"
  3. "Re-analyzing the Feb 2022 Starlink loss"
- **Paper:** a JOSS paper plus an arXiv methodology preprint.
- **Showcase:** a 2-minute demo video and a launch post.
- **Exit:**
  - `pip install orbitlife && orbitlife assess --alt 550 --inc 53 --shield-mm 3 --device hbm3 --workload llm-1b` works on a clean machine.
  - `expert-skeptic` signs off on the README, docs and paper.

## Verification
- **Each work item:** `verifier` runs `just verify` (ruff, mypy, pytest, vitest, schema drift, golden parity, builds), and CI repeats it on GitHub.
- **Science:** `just validate` runs every `validation/` case. The generated validation report, with residual plots, is the evidence. `validation-analyst` classifies every miss.
- **ML:** the leakage property test, the single-score log, and CRPS and coverage against all four baselines.
- **Web and 3D:** `ui-qa` drives each route in the browser (console, budgets, axe accessibility, URL state, export, globe frame checks against Skyfield), and Playwright, visual regression and Lighthouse run in CI.
- **Claims:** `expert-skeptic` reviews every user-facing number before merge and before release.
