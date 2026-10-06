# Forecast evaluation protocol v1 (pre-registered, Phase 1)

This protocol fixes, **before any model exists**, how orbitlife's space-weather forecasts will be scored. v1 incorporates the ml-auditor review of PR #12 (round 1: 7 BLOCKERs, 8 SHOULD-FIX; round 2: 5 clarifications).

Sources: `docs/research/phase1-forecast.md`. Values marked `assumption` are design choices pending a sourced number (docs/open-issues.md).

## 0. Change control
- After **any** test-split score exists, this protocol may only change by creating a new version.
- A result under a later version **never replaces** the result under the version in force at the first look. Both are reported.
- Every protocol change is a git commit. The score log records the protocol commit hash.

## 1. Targets and horizons
- **Kp:** GFZ definitive Kp (`matzka2021kpdata`), in thirds.
- **Dst:** WDC Kyoto. Use final where available, otherwise provisional. Quicklook is never used as truth.
  - Hours with no final or provisional value are **dropped** from Dst scoring, and the count is reported.
  - The truth version (final or provisional) is recorded per period. Train is mostly final; test may be provisional.
- **Issue times T:** every 3 h on block boundaries (00, 03, …, 21 UT).
- **Horizons:**
  - Kp at horizon h ∈ {3, 6, 12, 24} h is the Kp of the block **[T + h − 3 h, T + h)**. So +3 h is the block that starts at T.
  - Dst at horizon h is the hourly value for the hour **[T + h − 1 h, T + h)**, using Kyoto's hour-ending labels mapped to this interval in code (a tested function).
- **Output:** 19 quantiles at levels 0.05, 0.10, …, 0.95. Quantiles are **sorted** before scoring (no crossing).

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
2. **Solar wind.** Live RTSW is time-shifted with **the same method OMNI uses** (`omniweb_data_doc`, "magnetosphere-arrival times"), so training and serving inputs agree. Features then use shifted times ≤ T − 1 h, because OMNI rows cover [t, t + 1 h).
   - Formula: **availability time = shifted row end + RTSW latency**, and a row is usable if its availability time ≤ T.
   - The RTSW latency is UNVERIFIED; `assumption` until sourced: 1 h.
3. **Kp.** Only blocks whose nowcast was **published** before T. GFZ nowcast latency is UNVERIFIED; `assumption` until sourced: exclude the most recent completed block, so the newest usable block ends at T − 3 h.
4. **Dst.** Only hours whose real-time value was published before T. Kyoto quicklook latency is UNVERIFIED; `assumption` until sourced: 2 h.
5. **Leakage property test** (required before any score):
   - (a) Hypothesis perturbs every record whose **availability time > T**; all features at T must be unchanged.
   - (b) Explicit boundary cases: changing the record whose availability time is exactly T must not change features, and changing the newest record available before T **must** change them (a non-vacuity check).
   - (c) The same test applies to every baseline builder (persistence, recurrence, climatology).

## 4. Baselines (scored on the same issue times and the same inputs rules)
1. **Persistence:** the latest value available at T (§3.3 and §3.4).
2. **Climatology:** fitted on **all data available before the test start** (≤ 2021-12-31), conditioned on UT block and calendar month.
3. **27-day recurrence:** the value 27 days earlier, using the version available at T.
4. **NOAA SWPC 3-day forecast:**
   - **Headline comparison at matched information.** Our forecasts issued at T ∈ {00:00, 12:00} UT are compared with NOAA's 00:30 / 12:30 issues for the same target blocks. NOAA gets 30 min more data, which is conservative for us.
   - **Issue selection:** use the header `:Issued:` time, and the newest (amended) issue at or before T + 30 min.
   - **Missing NOAA file:** that T is dropped from *every* model's NOAA comparison, so all models share one common sample. The number of dropped T is reported.
   - NOAA's two-decimal values are converted to exact thirds: round(3x)/3.
5. **Distributions for point baselines.** Point baselines are turned into distributions with empirical error quantiles per horizon:
   - persistence, recurrence: errors from train
   - NOAA: errors from leave-one-month-out within the test period (this only helps NOAA)

   Undressed (point) scores are kept as a secondary result.

## 5. Metrics
- **CRPS:** 2 × mean pinball loss over the 19 levels, for every forecast including the baselines.
- **Interval coverage:** half-open central interval **[q0.10, q0.90)**. For the discrete Kp grid, a randomised PIT is also reported.
  - **Pass rule:** the point estimate lies in 0.78–0.82, with the bootstrap CI reported.
  - Storm-only coverage uses Kp ≥ 5.0 (5o and above) and Dst ≤ −50 nT.
- **Point** (the median): MAE and RMSE. **The headline NOAA comparison is point-vs-point MAE/RMSE** (§4.4).
- **Events:**
  - Thresholds: Kp ≥ 5.0, Kp ≥ 7.0, Dst ≤ −50 nT, Dst ≤ −100 nT.
  - Event probability is read from the forecast CDF, built by linear interpolation between sorted quantiles.
  - Tails: F(x) = 0.05 for x < q0.05 and F(x) = 0.95 for x > q0.95. That puts a 5% floor on tail-event probabilities, and the same rule applies to every model.
  - The **decision threshold** for POD, FAR, CSI and HSS is fixed on the **early-stop slice** (the value that maximises HSS there) and then frozen.
  - The Brier score uses the probability directly.
  - Event counts are always reported next to the scores.
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
- Each `validation/score-log.md` row records: date, model, protocol commit hash, look number, model artifact sha256 (the ONNX file), metrics file, and commit.
- **Parity:** only the scored artifact (by sha256) may ship. TypeScript features must match Python golden fixtures built from **live-format inputs** (RTSW, nowcast Kp, quicklook Dst).

## 7. Published context (not pass/fail)
- **SWPC 2013 daily-maximum Kp** (`swpc_max_kp_verification`, p. 2 table): RMSE 1.321 / 1.306 / 1.265 and skill −0.148 / −0.123 / −0.052 for days 1–3. The G1+ contingency table (POD 0.42, FAR 0.76) is from an image and not re-checked.
- **Chakraborty & Morley 2020** (`chakraborty2020kp`, Table 4 verified): 3 h Kp RMSE 0.78, MAE 0.59, r 0.82 on 2001–2010, using **definitive** OMNI inputs. That is an input-*quality* regime that §3.1 does not allow for a headline result, so it is context only.
