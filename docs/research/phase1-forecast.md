# Phase 1 research: space-weather forecast references

Source: `researcher` subagent (Sonnet), 2026-10-06, plus direct checks by the main agent.

Tags:
- **[verified]**: re-checked directly by the main agent.
- **[direct]**: read in full by the researcher, not re-checked.
- **[PROXY]**: read through a summariser only.
- UNVERIFIED: no source opened.

## NOAA SWPC 3-day forecast (the official baseline)
- **Archive** (`noaa_ngdc_3day_archive`) **[verified]**: https://www.ngdc.noaa.gov/stp/space-weather/swpc-products/daily_reports/3day_forecast/
  - Year folders run 2022–2026; the first month is **2022-03**.
  - Files are named `yyyymmddHHMMthree_day_forecast.txt` and issued at 0030 and 1230 UTC.
- **Example** **[verified]**: `2025/10/202510011230three_day_forecast.txt`, ":Issued: 2025 Oct 01 1230 UTC".
  - Section "NOAA Kp index breakdown Oct 01-Oct 03 2025" gives eight 3-hour UT blocks by three days, with Kp in thirds and G-scale tags.
  - Example values: 21-00UT Oct 01 = **5.67 (G2)**; 00-03UT Oct 01 = 5.33 (G1).
- **Live** (current forecast only): https://services.swpc.noaa.gov/text/3-day-forecast.txt [PROXY].
- **Pre-2022 archive:** SWPC FTP warehouse, coverage UNVERIFIED.

## Published verification of NOAA forecasts
- **SWPC "Max Kp and GPRA"** (`swpc_max_kp_verification`, undated SWPC web PDF) **[verified, p. 2 table]**:
  - Scope: daily **maximum** Kp (integer 0–9), calendar 2013, N = 365, verified against NOAA estimated Kp.

    | Lead | MAE | RMSE | ME | Linear assoc. | Skill vs observed climatology |
    |---|---|---|---|---|---|
    | Day 1 | 0.989 | 1.321 | +0.479 | 0.447 | **−0.148** |
    | Day 2 | 1.011 | 1.306 | +0.408 | 0.400 | **−0.123** |
    | Day 3 | 0.975 | 1.265 | +0.197 | 0.357 | **−0.052** |

  - The negative skill means the forecast was worse than climatology in 2013.
- **SWPC next-day G1+ contingency table, 2012-07-25 to 2013-12-31** [PROXY: the table on p. 4 is an image that could not be text-read; values UNVERIFIED]:
  - hits 14, misses 19, false alarms 44, correct nulls 448
  - POD 0.42, FAR 0.76, CSI 0.18, bias 1.76
  - Only 33 events.
- **Sharpe & Murray (arXiv 1804.02985):** verifies **UK Met Office** forecasts, not NOAA's (the main agent's question was wrong). Not opened.

## Published ML benchmarks (context only; different periods and inputs)
- **Chakraborty & Morley 2020** (`chakraborty2020kp`) **[verified, Table 4 of arXiv 2007.02733]**:
  - Kp 3 h ahead, test 2001–2010, OMNI (definitive, not real-time) inputs.

    | Model | Case | r | RMSE | MAE | R² |
    |---|---|---|---|---|---|
    | μOMNI | full test set | 0.82 | 0.78 | 0.59 | 0.67 |
    | μOMNI+ (adds X-ray flux) | full test set | 0.83 | 0.77 | 0.58 | 0.68 |
    | μOMNI | storm intervals | 0.69 | 1.48 | 1.11 | 0.29 |
    | μOMNI+ | storm intervals | 0.75 | 0.90 | 0.67 | 0.56 |

  - Values are from the arXiv preprint (the storm rows were re-checked against the text); the journal version may differ slightly.
- **Gruet et al. 2018** (Dst, 1–6 h) and **Wintoft et al. 2017** (Kp): numbers from abstracts or search only. UNVERIFIED, not used.

## Data timing (leakage-critical)
- **OMNI hourly** (`omniweb_data_doc`) **[verified]**:
  - "Decimal Hour … average for '1' is from 01:00 to 02:00", so the row for hour t averages **[t, t+1 h)**.
  - "Time-shifts of higher resolution data to expected magnetosphere-arrival times are done for data from spacecraft in L1 orbits … prior to taking hourly averages."
  - The page does **not** use the words "bow-shock nose", so cite the source's wording.
- **SWPC real-time solar wind (DSCOVR/ACE at L1):** whether it is time-shifted is UNVERIFIED (search summary only; the SWPC page is silent).
- **GFZ nowcast Kp latency** and **Kyoto quicklook Dst latency:** UNVERIFIED. The pages say only "realtime" and that quicklook Dst may contain noise and baseline shifts.

## NOAA issue-selection example [verified]
For the target block 2025-10-01 21-00UT, the two issues disagree:
- the 0030 UTC issue (`202510010030`) gives **3.00**
- the 1230 UTC issue (`202510011230`) gives **5.67 (G2)**

This pair is used in `validation/cases/forecast/forecast-noaa-issue-selection-*.yaml`.
