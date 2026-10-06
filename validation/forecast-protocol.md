# Forecast evaluation protocol (pre-registered, Phase 1)

This protocol fixes, **before any model exists**, how orbitlife's space-weather forecasts will be scored. Changing it after any test-set score has been computed requires a new protocol version, a reason, and an entry in `validation/score-log.md`. The ml-auditor checks this.

Sources: `docs/research/phase1-forecast.md`.

## 1. Targets
- **Kp:** GFZ definitive Kp (`matzka2021kpdata`), in thirds (0, 0.33, …, 9).
- **Dst:** WDC Kyoto. Use final where available, otherwise provisional. Quicklook is never used as truth.
- **Issue times:** every 3 h on Kp block boundaries (00, 03, …, 21 UT).
- **Horizons:** +3, +6, +12, +24 h. Each forecast is a set of quantiles (0.05, 0.10, …, 0.95).

## 2. Data splits (time-blocked, purged)

| Split | Years | Use |
|---|---|---|
| train | ≤ 2016 | fitting |
| early stop | 2017–2019 | stopping and model selection only |
| calibration | 2020–2021 | conformal calibration only |
| **test** | **2022-03-01 → 2025-12-31** | scored once per model version |

- Each split boundary has a 48 h purge on both sides.
- The test start is 2022-03-01 so that it matches the NOAA 3-day forecast archive (`noaa_ngdc_3day_archive`). Every test issue time therefore has a NOAA forecast to compare against.

## 3. Information available at issue time T (leakage rules)
1. **OMNI hourly rows** cover [t, t+1 h) (`omniweb_data_doc`), so a feature at T may use only rows with t ≤ T − 1 h.
2. **OMNI L1 data** are time-shifted to expected magnetosphere arrival. Real-time L1 data's shift status is UNVERIFIED (docs/open-issues.md). Until resolved, features are built so they do not depend on the shift: lagged by at least the maximum L1-to-magnetosphere propagation time used by OMNI. The exact value must be sourced before training.
3. **Kp:** only fully completed 3-hour blocks before T.
4. **Dst:** only hours whose real-time value would have been published before T. The latency is UNVERIFIED and must be sourced before training.
5. A hypothesis property test must show that changing any input at or after T leaves every feature at T unchanged.

## 4. Baselines (all scored on the same test issue times)
1. Persistence (last completed block or hour).
2. Climatology: the training-period distribution conditioned on UT block and season.
3. 27-day recurrence.
4. **NOAA SWPC 3-day forecast** (`noaa_ngdc_3day_archive`): the Kp-in-thirds block forecast for the matching block, from the latest forecast issued before T. NOAA gives a point value, so for CRPS it is scored as a degenerate (point) distribution, and it is compared with our median on MAE and RMSE.

## 5. Metrics
- **Probabilistic:** CRPS and pinball loss per quantile. Central 80% interval coverage overall and in storms (Kp ≥ 5). The target coverage band is 0.78–0.82.
- **Point** (median): MAE and RMSE.
- **Events** (Kp ≥ 5, Kp ≥ 7; Dst ≤ −50, Dst ≤ −100 nT): POD, FAR, CSI, HSS and Brier score, with reliability diagrams.
- **Skill:** relative to every baseline. Losses are reported as clearly as wins.

## 6. Published context (not pass/fail; different periods and definitions)
- **SWPC 2013 daily-maximum Kp** (`swpc_max_kp_verification`):
  - RMSE 1.321 / 1.306 / 1.265 and skill −0.148 / −0.123 / −0.052, for days 1–3.
  - G1+ next-day POD 0.42 and FAR 0.76. That figure is from an image, not re-checked.
  - For a like-for-like comparison, orbitlife also reports the **daily-maximum Kp** version of its own forecast on the test period.
- **Chakraborty & Morley 2020** (`chakraborty2020kp`): 3 h Kp RMSE 0.78, MAE 0.59, r 0.82 on 2001–2010, using definitive OMNI inputs (not real-time). It is context only, because it uses a different period and an input regime that would count as leakage under rule 3.2.

## 7. Scoring discipline
- Each model version is scored on the test split **once**. The result is appended to `validation/score-log.md` with the commit hash.
- Calibration and early-stop slices are never reused for anything else.
- Results are reported to two decimals, with bootstrap 95% confidence intervals by month blocks.
