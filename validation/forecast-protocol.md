# Forecast evaluation protocol v2 (pre-registered, Phase 1)

This protocol fixes, **before any model exists**, how orbitlife's space-weather forecasts will be scored.
- v1 (commit `abcc9c5`) incorporated the ml-auditor review of PR #12 (round 1: 7 BLOCKERs, 8 SHOULD-FIX; round 2: 5 clarifications).
- v2 (Phase 1 extension E5, 2026-10-08) closes expert-skeptic gap 9 (docs/open-issues.md). See "Changes from v1" at the end.

Sources: `docs/research/phase1-forecast.md`. Values marked `assumption` are design choices pending a sourced number (docs/open-issues.md).

## 0. Change control
- v2 replaces v1 outright. That is allowed because **no model, and no score on any split, existed** when v2 was written.
- After **any** test-split score exists, this protocol may only change by creating a new version.
- A result under a later version **never replaces** the result under the version in force at the first look. Both are reported.
- Every protocol change is a git commit. The score log records the protocol commit hash.

## 1. Targets and horizons
- **Kp:** GFZ definitive Kp (`matzka2021kpdata`), in thirds.
- **Dst:** WDC Kyoto. Use final where available, otherwise provisional. Quicklook is never used as truth.
  - Hours with no final or provisional value are **dropped** from Dst scoring, and the count is reported.
  - The truth version (final or provisional) is recorded per month.
  - **Coverage checked 2026-10-08** (`kyoto_dst_index_2026`): final 1957–2020, provisional 2021-01 → 2026-07, quicklook only from 2026-08. So train, early stop and calibration 2020 are final; calibration 2021 and the **whole test split (2022-03 → 2025-12) are provisional**.
  - **Truth is frozen at the first look.** The Dst and Kp truth files are downloaded once, before the first look, and their sha256 is recorded in the score log. If Kyoto later issues final values for test months, a rescore against final truth is a separately logged look and never replaces the headline.
- **Issue times T:** every 3 h on block boundaries (00, 03, …, 21 UT).
- **Horizons:**
  - Kp at horizon h ∈ {3, 6, 12, 24} h is the Kp of the block **[T + h − 3 h, T + h)**. So +3 h is the block that starts at T.
  - Dst at horizon h is the hourly value for the hour **[T + h − 1 h, T + h)**, using Kyoto's hour-ending labels mapped to this interval in code (a tested function).
- **Output:** 21 quantiles at levels **0.01**, 0.05, 0.10, …, 0.95, **0.99**. Quantiles are **sorted** before scoring (no crossing).
  - The 19 **inner** levels (0.05 … 0.95, equally spaced) feed CRPS and twCRPS (§5), so the estimator is unchanged from v1.
  - The two **tail** levels (0.01, 0.99) feed tail coverage, tail pinball loss and event probabilities (§5).

## 2. Data splits (time-blocked, purged)

| Split | Period | Use |
|---|---|---|
| train | ≤ 2016-12-31 | fitting, input normalisation statistics |
| early stop | 2017–2019 | stopping, model selection, **event decision thresholds** (§5) |
| calibration | 2020–2021 | conformal calibration only |
| test | **2022-03-01 → 2025-12-31** | see §6 |

- Each boundary has a 48 h purge on both sides. January–February 2022 is unused.
- **No refit** on train + early stop after calibration, and **no recalibration on test**. Calibration on solar-minimum years (2020–21) may give poor storm coverage at the cycle-25 maximum, and that is reported exactly as it comes out.
- The test start matches the NOAA 3-day forecast archive (`noaa_ngdc_3day_archive`, from 2022-03).

## 3. Information available at issue time T
Every input is defined by its **availability time** (when that version of the value was published), not by its observation time.

1. **Version.** A feature at T uses the value *as published by T*. Planned inputs:
   - real-time L1 solar wind (SWPC RTSW)
   - GFZ **nowcast** Kp
   - Kyoto **quicklook** Dst

   If archived real-time data cannot be obtained for training and test, the headline result is labelled **"definitive-input hindcast"**. In that case a **degraded-input sensitivity run** is mandatory (quicklook-like Dst, nowcast-like Kp, RTSW-like gaps and noise), and **no claim of operational superiority over NOAA** may be made from definitive-input scores.
2. **Solar wind.** Live RTSW is time-shifted with **the same method OMNI uses** (`omniweb_data_doc`, "magnetosphere-arrival times"), so training and serving inputs agree.
   - An OMNI row covers [t, t + 1 h) in shifted time. Its **availability time = t + 1 h + RTSW latency**, and the row is usable only if its availability time ≤ T. With the 1 h assumption below, the newest usable row is [T − 2 h, T − 1 h).
   - The RTSW latency is UNVERIFIED; `assumption` until sourced: 1 h.
3. **Kp.** Only blocks whose nowcast was **published** before T. GFZ nowcast latency is UNVERIFIED; `assumption` until sourced: exclude the most recent completed block, so the newest usable block ends at T − 3 h.
4. **Dst.** Only hours whose real-time value was published before T. Kyoto quicklook latency is UNVERIFIED; `assumption` until sourced: 2 h.
5. **Leakage property test** (required before any score):
   - (a) Hypothesis perturbs every record whose **availability time > T**; all features at T must be unchanged.
   - (b) Explicit boundary cases: changing the record whose availability time is exactly T must not change features, and changing the newest record available before T **must** change them (a non-vacuity check).
   - (c) The same test applies to every baseline builder: persistence, recurrence, climatology, the O'Brien–McPherron start state and drivers, the Newell window (§4.5), and the NOAA issue selector (§4.4).
   - (d) It also applies to each step of the model's own fallback chain (§3.6).
6. **Every forecast at every T (no dropping for missing inputs).** Our model must issue a forecast at every issue time, using this pre-registered fallback chain:
   1. The full model, when its solar-wind window is usable: at least 2 of the 3 hourly slots ending at T − 1 h, T − 2 h and T − 3 h are valid (§3.2).
   2. Otherwise, a **no-solar-wind sub-model**: the same architecture without solar-wind features, trained, early-stopped and calibrated on the same splits.
   3. If the Kp or Dst history it needs is also missing, the dressed persistence forecast; if that is missing too, climatology.

   - The count of each fallback step is reported overall and for storm-only targets (§5).
   - **No T is dropped for missing inputs**, for any model. The only allowed drops are missing Dst truth (§1) and a missing NOAA file (§4.4).
   - TypeScript parity (§6) covers the fallback path with its own golden fixtures.

## 4. Baselines (scored on the same issue times and the same inputs rules)
1. **Persistence:** the latest value available at T (§3.3 and §3.4).
2. **Climatology:** fitted on **all data available before the test start** (≤ 2021-12-31), conditioned on UT block and calendar month.
3. **27-day recurrence:** the value 27 days earlier, using the version available at T.
4. **NOAA SWPC 3-day forecast:**
   - **Headline comparison at matched information.** Our forecasts issued at T ∈ {00:00, 12:00} UT are compared with NOAA's 00:30 / 12:30 issues for the same target blocks. NOAA gets 30 min more data, which is conservative for us.
   - **Issue selection:** use the header `:Issued:` time, and the newest (amended) issue at or before T + 30 min.
   - **Missing NOAA file:** that T is dropped from *every* model's NOAA comparison, so all models share one common sample. The number of dropped T is reported.
   - NOAA's two-decimal values are converted to exact thirds: round(3x)/3.
5. **Physics baselines** (one per target). Both use only inputs available at T under §3. Neither is fitted on early stop, calibration or test (the shared steps in §4.7 and §5 apply to them as to every forecast).
   - **Dst: O'Brien & McPherron 2000** (`obrien2000ring`), with published constants and **no refit**:
     - Dst* = Dst − 7.26·√P + 11 nT, with P the solar-wind dynamic pressure in nPa; dDst*/dt = Q − Dst*/τ.
     - Q = −4.4 nT h⁻¹ (mV/m)⁻¹ × (VBs − Ec) for VBs > Ec, else 0, with Ec = 0.49 mV/m.
     - τ = 2.40·exp[9.74/(4.69 + VBs)] h.
     - **Inputs:**
       - VBs = V·Bs·10⁻³ mV/m, with V the bulk flow speed in km/s and Bs = −Bz(GSM) in nT when Bz < 0, else 0.
       - P is the OMNI hourly "flow pressure" field. For live RTSW it is computed with the formula OMNI documents (`omniweb_data_doc`; UNVERIFIED until read; the alpha-particle term matters at the ~20% level). Whether OMNI's P matches the P that O'Brien & McPherron fitted (7.26, 11) is also UNVERIFIED (≈1.4 nT at 4 nPa for a 1.2 ratio).
     - **Time convention.** Every hourly value (Dst, P, VBs) is an average over [t, t + 1 h) and is labelled by its hour end t + 1 h.
       - The start state is the newest quicklook Dst hour available at T (§3.4), ending at t_s (t_s ≤ T − 2 h under the latency assumption).
       - The target is the Dst hour ending at T + h (§1), so the model runs for **Δt = (T + h) − t_s** hours. For example, h = 1 h and t_s = T − 2 h give a 3 h run.
     - **Drivers.** Observed hourly drivers are used hour by hour from t_s up to the newest usable OMNI-shifted hour (§3.2). The last one is then held constant ("frozen driver") to T + h.
       - Each hour uses the exact solution for a constant driver: Dst*(t + Δ) = Qτ + (Dst*(t) − Qτ)·e^(−Δ/τ).
       - Dst is converted to Dst* with the P of the start hour, and Dst* back to Dst with the frozen P.
     - **Missing or stale input.** Fallback to the dressed persistence forecast for that T if any of these holds:
       - the start Dst, or the P of the start hour (the OMNI row ending at t_s), is missing;
       - the start state is older than 6 h (t_s < T − 6 h; `assumption`);
       - any driver hour between t_s and the newest usable hour is missing;
       - the newest usable driver hour ends more than 3 h before T − 1 h (`assumption`: maximum driver age 3 h).

       The fallback keeps the sample paired with every other model. The count is reported. Scores excluding those T are a sensitivity result, with the same T excluded for **every** model in the comparison; the full sample is the headline.
     - **Applicability flag `obrien_out_of_fit_range`:** the start Dst* or the forecast Dst* is below −150 nT, the fitted range in the abstract. Scores are reported with and without flagged hours (paired across models; the full sample is the headline).
     - **UNVERIFIED** (secondary sources; docs/research/phase1-forecast.md): the slope 4.4, Ec, the Bs convention, and V as bulk speed rather than |Vx|. Ec = 0.5 is reported as a sensitivity run.
   - **Kp: physics-informed baseline using the Newell et al. 2007 coupling** (`newell2007universal`):
     - dΦ/dt = v^(4/3)·B_T^(2/3)·sin^(8/3)(θc/2), with v in km/s, B_T = √(By² + Bz²) GSM in nT, and θc = atan2(|By|, Bz) ∈ [0, π] (equal to arccos(Bz/B_T)). dΦ/dt = 0 when B_T = 0. Formula UNVERIFIED (secondary sources).
     - **Feature:** dΦ/dt computed from each hourly OMNI-shifted row (not from higher-cadence data), averaged over the 3 hourly slots ending at T − 1 h, T − 2 h and T − 3 h (shifted time, under the §3.2 latency). At least 2 of the 3 slots must be valid; otherwise the fallback is dressed persistence, and the count is reported. `assumption`: the 3-hour window matches the Kp block length.
     - **Model:** linear quantile regression of Kp(T + h) on **(dΦ/dt)^½**, per horizon and quantile level (all 21), fitted on **train only**.
       - `assumption`: the square root is chosen because Kp is quasi-logarithmic and dΦ/dt is heavy-tailed. No Kp regression is published in the sources read.
       - The coupling form is published; the mapping to Kp is our design. So this is a *physics-informed* baseline, not published physics.
   - Both are scored exactly like the other baselines (§5), including the NOAA common sample.
6. **Distributions for point baselines.** Point baselines (including O'Brien–McPherron) are turned into distributions with empirical error quantiles per horizon, at all 21 levels:
   - **Error definition:** e = y − ŷ. The forecast quantile is q_τ = ŷ + Q_τ(e), where Q_τ is the empirical quantile with linear interpolation (Hyndman–Fan type 7).
   - persistence, recurrence, O'Brien–McPherron: errors from train, computed under the **same input regime as the scored forecast** (§3.1). If train lacks archived real-time inputs, the definitive-input label and the degraded-input run apply to the baselines exactly as to the model.
   - NOAA: errors from leave-one-month-out within the test period (this only helps NOAA)

   Undressed (point) scores are kept as a secondary result.
7. **Equal calibration.** The same calibration step is applied to our model and to every distributional baseline **except NOAA and climatology**, so no comparison favours the model through calibration alone.
   - Climatology is exempt because its quantiles are empirical by construction and it is fitted on data that include the calibration split.
   - **Method (pre-registered):** for each horizon and each of the 21 levels τ, the shift δ_τ is the empirical τ-quantile (Hyndman–Fan type 7) of (y − q_τ) over the calibration split (2020–21). The calibrated quantile is q_τ + δ_τ, and all 21 are then re-sorted. No finite-sample correction is applied.
   - **Order, for every forecast:** fit δ on 2020–21; apply it to the early-stop forecasts; then choose the event decision thresholds on 2017–19 (§5). No test data are used.

## 5. Metrics
- **Sorting:** all 21 quantiles are sorted together first. The inner 19 are then taken from the sorted set.
- **CRPS:** 2 × mean pinball loss over the 19 inner levels, for every forecast including the baselines.
- **Threshold-weighted CRPS (twCRPS)**, the storm-focused score (`allen2023transformed`, Proposition 1; `gneiting2011comparing`):
  - Kp thresholds t = 5.0 and 7.0 use the upper-tail projection v(z) = max(z, t). Dst thresholds t = −50 and −100 nT use the lower-tail projection v(z) = min(z, t).
  - **Computation:** apply v to each sorted inner quantile and to the observation, then use the CRPS estimator above. v is non-decreasing, so the projected quantiles are quantiles of the projected forecast.
  - Dst lower tail: this is Eq. (6) of `allen2023transformed` with ν the Lebesgue measure on (−∞, t], whose chaining function is min(z, t).
  - It ignores errors that stay entirely on the quiet side of t. It is reported per horizon with skill against every baseline, as a **secondary** result (CRPS stays the headline).
  - **Known limitation at Kp ≥ 7:** a forecast whose q0.95 < 7 has every projected inner quantile equal to 7, so its twCRPS is (y − 7)⁺ whatever the forecast. This is checked **per forecast**: when it holds for ≥ 95% of that forecast's issues, its Kp ≥ 7 twCRPS is labelled uninformative. A twCRPS skill is reported only when the model's own twCRPS is informative; an uninformative baseline is reported as reducing to (y − 7)⁺. The tail measures there are the 0.99 pinball loss and the Kp ≥ 7 Brier score.
- **Interval coverage:** half-open central interval **[q0.10, q0.90)**. For the discrete Kp grid, a randomised PIT is also reported.
  - **Pass rule:** the point estimate lies in 0.78–0.82, with the bootstrap CI reported.
  - Storm-only coverage uses Kp ≥ 5.0 (5o and above) and Dst ≤ −50 nT.
  - **Tail coverage** of [q0.01, q0.99) (nominal 0.98) and the pinball loss at 0.01 and 0.99 are reported, with no pass rule.
- **Point** (the median): MAE and RMSE. **The headline NOAA comparison is point-vs-point MAE/RMSE** (§4.4).
- **Events:**
  - Thresholds: Kp ≥ 5.0, Kp ≥ 7.0, Dst ≤ −50 nT, Dst ≤ −100 nT.
  - Event probability is read from the forecast CDF, built by linear interpolation between sorted quantiles.
  - Tails: F(x) = 0.01 for x < q0.01 and F(x) = 0.99 for x > q0.99. That puts a 1% floor on tail-event probabilities (v1 had 5%, which made every Kp ≥ 7 probability at least 5%), and the same rule applies to every model.
  - The **decision threshold** for POD, FAR, CSI and HSS is fixed on the **early-stop slice** (the value that maximises HSS there) and then frozen.
    - This applies **identically to every forecast**: our model, persistence, recurrence, climatology, both physics baselines and NOAA. NOAA has no early-stop forecasts in the archive, so it uses a probability threshold of 0.5. Its result is also reported with the threshold that maximises HSS on test, which only helps NOAA.
    - Choosing this threshold is not "fitting" in the §4.5 sense.
    - **Any claim that our model beats NOAA on POD, FAR, CSI or HSS must hold against NOAA's test-optimal threshold** (the bound that favours NOAA). NOAA's own categorical forecast (its point Kp at or above the threshold) is reported alongside.
  - The Brier score uses the probability directly.
  - Event counts are always reported next to the scores.
  - **Too few events.** An event score (and a twCRPS at that threshold) is labelled "too few events to be informative" if it rests on fewer than **10 events** or fewer than **3 independent storm episodes**. Such a score is shown with its bootstrap CI, never as a skill claim.
    - An event is a scored target block (Kp), hour (Dst) or UT day (daily-maximum Kp) at or beyond the threshold.
    - An episode is a run of events separated from the next by at least 24 h.
    - Both are counted per horizon, on the exact sample of each comparison (after the Dst-missing and NOAA-common-sample drops).
    - `assumption`: 10 and 3 are design choices made before any test target was examined.
- **Skill:** 1 − mean(S_model) / mean(S_baseline).
- **Uncertainty:** paired moving-block bootstrap with 1-month blocks and B = 2000, with identical resamples for the model and each baseline. Report 3 significant figures.
- **Daily maximum Kp** (for SWPC-style comparison):
  - Built from the **00 UT issue**, using all eight 3-hourly horizons 3, 6, …, 24 h, which cover that UT day (a separate product from the 4 headline horizons).
  - Derived from 1000 sample paths drawn from the per-block forecast distributions, with an empirical copula fitted on train.
  - Compared against **NOAA day 1** of the 00:30 issue for the same UT day, on the same 2022–25 test period. SWPC's 2013 numbers are context only (different period and solar cycle).

## 6. Test-set discipline and the score log
- The test split is scored **once for headline purposes** per (target, test split), in total, not once per model version. Kp and Dst have separate headlines.
- A **look** is any computation that combines a candidate model's output with test-period targets, including partial scoring, storm plots, and debugging on test targets.
- Every later evaluation on test is a logged **"test reused (look n)"** with a running count. It may be reported, but it can never be the headline.
- Each `validation/score-log.md` row records: date, model, version, test set, protocol commit hash, look number, model artifact sha256 (the ONNX file), truth sha256 (Kp and Dst files, §1), input manifest sha256 (the archived input snapshots, since quicklook files are overwritten), metrics file, and commit.
- **Parity:** only the scored artifact (by sha256) may ship. TypeScript features must match Python golden fixtures built from **live-format inputs** (RTSW, nowcast Kp, quicklook Dst).

## 7. February 2022 storm replay (not a score)
On 2022-02-03/04 a moderate storm raised drag enough to destroy most of a fresh Starlink batch (the `drag-starlink-g47-*` cases). The replay shows how a frozen model behaves on that event.
- **Window:** issue times every 3 h from 2022-01-29 00:00 to 2022-02-08 21:00 UT. That lies inside the unused January–February 2022 gap (§2) and clear of both purges, so it is **not** test data and not a look.
- **No development use.** January–February 2022 is never used for development, including exploratory analysis.
- **Frozen model:** the replay runs only after the headline artifact's sha256 is in the score log, and with that same artifact. It may never be used for model selection, tuning or calibration. Every replay run is logged in the score log's "Replays" table (date, artifact sha256, commit).
- **Output:** per-issue quantile fans for Kp and Dst at each horizon, with the truth, persistence and both physics baselines. Per-block errors may be listed, but no aggregate score or skill is computed from it.
  - NOAA issues are included only if a pre-2022-03 archive is sourced. The cited archive starts in 2022-03, and earlier coverage is UNVERIFIED.
- **Truth for the window** follows §1 (February 2022 Dst is provisional).

## 8. Published context (not pass/fail)
- **SWPC 2013 daily-maximum Kp** (`swpc_max_kp_verification`, p. 2 table): RMSE 1.321 / 1.306 / 1.265 and skill −0.148 / −0.123 / −0.052 for days 1–3. The G1+ contingency table (POD 0.42, FAR 0.76) is from an image and not re-checked.
- **Chakraborty & Morley 2020** (`chakraborty2020kp`, Table 4 verified): 3 h Kp RMSE 0.78, MAE 0.59, r 0.82 on 2001–2010, using **definitive** OMNI inputs. That is an input-*quality* regime that §3.1 does not allow for a headline result, so it is context only.

## Changes from v1
| Change | Section | Why |
|---|---|---|
| Tail quantiles 0.01 and 0.99 (21 levels); tail floor 5% → 1%; tail coverage and tail pinball reported | §1, §5 | v1's 5% floor made Kp ≥ 7 scores uninformative |
| Threshold-weighted CRPS at the event thresholds | §5 | Storm-focused score; plain CRPS is dominated by quiet times |
| "Too few events" rule (< 10 test events) | §5 | Stops a skill claim resting on a handful of storms |
| Physics baselines: O'Brien–McPherron (Dst, published constants), Newell-coupling quantile regression (Kp, physics-informed) | §4.5 | Beating persistence is easy; a physics-based reference is a harder test |
| Equal calibration and identical event thresholds for every forecast | §4.7, §5 | No comparison favours the model through procedure alone |
| Score log records truth and input-manifest sha256 | §6 | Provisional and quicklook files change over time |
| Every forecast at every T: pre-registered model fallback chain, no drops for missing inputs | §3.6 | Solar-wind gaps cluster in the biggest storms; skipping them would flatter the model |
| Calibration method and order defined; NOAA event claims must beat its test-optimal threshold | §4.7, §5 | Makes "applied identically" checkable and keeps the NOAA comparison conservative |
| Kyoto coverage checked; truth frozen and hashed at first look | §1 | The whole test split is provisional Dst |
| February 2022 storm replay | §7 | Shows the Starlink G4-7 storm without spending a test look |
