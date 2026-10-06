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
   - sourced nominal altitudes (FCC, NASA) are taken as a − R_eq by assumption. Mean geodetic height is up to ~11 km higher near-polar (~10–15% drag density at 400–550 km). Resolve with TLE-derived mean elements in Phase 2 (physics-reviewer, PR #5, attempt 2).
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
  - radiation: GCR/cutoff and SEP model specifications, AP9/AE9 licence terms (dose-depth, ISS dosimetry and CREME96 searches done 2026-10-06; docs/research/phase1-radiation.md)
  - on-orbit upset counts, thermal constants, checkpoint formulas (forecast references done 2026-10-06; docs/research/phase1-forecast.md)
  - workloads (ResNet-50, ~1B LLM, fault-injection and SDC studies)

## Validation cases deferred (physics-reviewer, PR #7)
- **Tiangong-1 Feb 2018 decay-rate case removed.** Its start altitude (280 km) was a January value with no source; back-integrating Pardini's rates gives ≈268.5 km on 1 Feb. Restore it when `researcher` reads the 1 Feb mean altitude from pardini2019tiangong1 Fig. 4.
- **Starlink Group 4-7 orientation:** RAAN / local time must come from Space-Track TLEs (Phase 2). The 'previous launches' baseline in the SpaceX statement is undefined; our quiet-Ap baseline is a stated design choice.
- **An independent (non-fitted) drag physics case is still needed,** for example ISS decay between reboosts from TLEs. The Tiangong-1 reentry case is an implementation check because B was fitted with NRLMSISE-00.

## Radiation cases deferred (Phase 1.4b)
- **ISS DOSTEL dose rate (berger2017dosis):** measured rates are saved, but the Columbus/DOSTEL shielding thickness is not given ("heavier shielded"). The case needs a sourced shielding distribution for that location, and a GCR dose model (GCR dominates inside the ISS).
- **ISS TMS44400 DRAM in-flight SEU rate (koontz2020issee):** in-flight 8.5e-8 and 7.0e-8 SEU/bit/day are saved, but the device cross-section slide is unreadable (σsat exponent, W). Restore once the TI-44100 heavy-ion data are sourced.
- **No fully specified LEO CREME96 SEU (per-bit) worked example** found and readable (2026-10-06). Tylka 1997 and Petersen 2011 are paywalled; Engel et al. 2006 and the ESCIES Sturesson slides are unopened leads. Aiden could supply a paywalled source.
- **SEL flux reproduction:** the TI SEL cases take the CREME96 flux as an input. Reproducing it needs the CREME96 'ISS' orbit parameters, which the source does not state. The `researcher` could check whether CREME96's built-in ISS preset fixes altitude and inclination.
- **Flux geometry convention** (omnidirectional vs per sr; planar-target factor 1/4 to 1/2) must be recorded before Phase 2 computes SEL or SEU rates from an environment (physics-reviewer, PR #13).

## Radiation model gaps (physics-reviewer, PR #9)
- **ESP-PSYCHIC** (Xapsos et al. 2000, 2007) must be sourced and given an ADR before Phase 2 builds it. The SPENVIS dose-depth cases need it.
- **Geomagnetic field model and epoch for AP8/AE8 B,L** (this moves the SAA): pin it in an ADR.
- **GCR dose model:** needed to rerun the Shields-1 cases with `include_gcr` and to restore the ISS DOSTEL case.
- **Dose by species:** the validation report must show residuals broken down by species (trapped p, trapped e plus bremsstrahlung, SEP, GCR).

## Forecast protocol gaps (Phase 1, validation/forecast-protocol.md)
- **Real-time L1 solar wind (SWPC RTSW):** is it time-shifted to the magnetosphere? UNVERIFIED. Source this before training.
- **Maximum L1-to-magnetosphere propagation time used by OMNI:** needed for the leakage lag in protocol rule 3.2.
- **Real-time publication latency** of GFZ nowcast Kp and Kyoto quicklook Dst: UNVERIFIED (protocol rule 3.4).
- **SWPC verification is from 2013.** Pre-2022 3-day forecast files (SWPC FTP warehouse) are unverified, so SWPC's own 2013 numbers cannot yet be reproduced as an implementation check.
- **SWPC 2012–13 G1+ contingency counts** are in an image (not re-checked).
- **Protocol `assumption` latencies** (validation/forecast-protocol.md §3): RTSW 1 h, GFZ nowcast Kp (exclude the newest block), Kyoto quicklook Dst 2 h. Each must be replaced with a sourced value before training.
- **Archived real-time inputs** (RTSW, nowcast Kp, quicklook Dst) for 2022–2025: find a source, or the headline result must be labelled "definitive-input hindcast" (protocol §3.1).
- **NOAA reader cases still to add:** a missing file and an amended (reissued) forecast. No real examples found yet.

## Phase 1 exit gaps (validation-analyst, 2026-10-06)
- **No SEL case with a published Weibull fit.** The TI cases use the square approximation. This leaves the Phase 2 exit criterion "SEL rates match CREME96 within a factor of 2 for the same Weibull parameters" untestable until a source is found.
- **No beta-angle case.** The roadmap lists Orekit/GMAT eclipse *and* beta angle; only one (cylindrical) eclipse case exists.
- **Tiangong-1 covers only the last ~29.7 days** of the "final year" in the roadmap.
- **No machine-readable "expected FAIL" marker.** Once Phase 2 implements drag and radiation, the documented-miss cases (Starlink G4-7, Shields-1) will make `just validate` exit 1. This needs a decision from Aiden (or an ADR) before Phase 2.

## Data licensing before going public (researcher, Phase 0)
- CelesTrak GP/SATCAT and SupGP redistribution terms
- GOES-R SGPS licence
- NOAA SWPC SEP list terms
- upstream licences of the BRHSpaceX-derived files

## Tooling (physics-reviewer, PR #1)
- `manifest verify` checks bundle hashes only. Per-file (tar member) hashes must also be checked once data is used after unpacking.
