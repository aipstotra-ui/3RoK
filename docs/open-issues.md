# Open issues

Known gaps that are deliberately deferred. Each one names its source and the phase that must close it. Remove an entry only in the PR that resolves it.

## Device schema: needed before Phase 2 rate physics (physics-reviewer, PR #5)
1. **Weibull fit object** `{let_th, w, s, sigma_sat, normalization: bit|device}`, plus a proton fit (Bendel A/B or σ(E)). Today LETth and σsat are loose rows, and W and s can't be stored.
2. **Structured test conditions**, replacing free text:
   - particle and energy (MeV), or ion plus LET
   - whether the die was thinned or overlaid
   - temperature (°C), supply voltage, and operating or power mode
   - dose rate and source for TID
   - bias, and sample size
3. **Fluence and event count**, so Poisson confidence limits can be computed. For example, "no SEL at 1e7 ions/cm² on 3 parts" implies σ_SEL < ~1e-7 cm²/device at 95% CL. That limit is what an SEL-rate model needs.
4. **Uncertainty** (σ or confidence level) per measurement.
5. **`capacity_bits`** (bits under test) for per-bit ↔ per-device conversion.
6. **Controlled vocabularies** for `quantity` and `unit`. The `effect` enum and `kind` exist since PR #5.
7. **Missions:**
   - eccentricity
   - epoch
   - a structured altitude tolerance (Starlink ±30 km, ISS 330–425 km)
8. **Environment-specific rates** (e.g. the Frontgrade GEO SEU rate): the environment model and shielding as fields.

## Research gaps (UNVERIFIED; flagged `heuristic` if used)
- **Devices:**
  - DDR4 Weibull W and s
  - DDR5 numbers
  - standalone HBM3
  - absolute A100/H100 rates
  - TPU v6e SEL
  - the rad-hard SRAM LEO rate
  - latchup-protection prevention probability
- **Orbits and drag:**
  - a published Vallado/SMAD SSO table
  - a measured ISS decay rate between reboosts (plan: derive it from TLEs)
  - GMAT eclipse configuration
  - Starlink v1.5 mass and area
- **Not yet researched (stopped 2026-10-05 to save tokens; to be redone just in time on Sonnet):**
  - radiation references (published dose-depth, ISS dosimetry, CREME96 examples, GCR/cutoff and SEP models, AP9 terms)
  - forecasts (NOAA 3-day archive, OMNI timing, on-orbit upset counts, thermal constants, checkpoint formulas)
  - workloads (ResNet-50, ~1B LLM, fault-injection and SDC studies)

## Data licensing before going public (researcher, Phase 0)
- CelesTrak GP/SATCAT and SupGP redistribution terms
- GOES-R SGPS licence
- NOAA SWPC SEP list terms
- upstream licences of the BRHSpaceX-derived files

## Tooling (physics-reviewer, PR #1)
- `manifest verify` checks bundle hashes only. Per-file (tar member) hashes must also be checked once data is used after unpacking.
