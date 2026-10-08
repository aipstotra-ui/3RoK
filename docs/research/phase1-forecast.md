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

## E5 additions (researcher on Sonnet, 2026-10-08; protocol v2)
The publisher pages for the JGR and JBES papers returned HTTP 403 to the researcher and showed a bot check to the main agent's browser. The main agent did not bypass it, so those papers' bodies were **not read**.

### O'Brien & McPherron 2000 (`obrien2000ring`), Dst physics baseline
- **[direct, abstract only]** via EarthRef ERR/23843:
  - Dst* = Dst − 7.26·P^½ + 11 nT, with P in nPa.
  - τ = 2.40·exp[9.74/(4.69 + VBs)] h, with VBs in mV/m. τ depends on VBs, not on Dst.
  - Fitted to 30 years of hourly data; valid for Dst > −150 nT. The Burton injection form is "essentially correct, with no injection below a threshold VBs".
- **UNVERIFIED (secondary only):**
  - dDst*/dt = Q − Dst*/τ; Q = −4.4·(VBs − Ec) nT/h, with Ec = 0.49 mV/m.
  - One secondary source (arXiv 1903.08466, Eq. 7) writes 0.5 instead. Protocol v2 uses 0.49 and reports 0.5 as a sensitivity run.
  - Bs as −Bz(GSM) for Bz < 0 is the usual convention; not seen in the source.
  - V as bulk flow speed rather than |Vx|: not seen in the source. The difference is usually a few percent.
- DOI correction: 10.1029/**1998**JA000437 (not 1999).

### Burton, McPherron & Russell 1975 (`burton1975empirical`)
- Constants were read only on the UC Berkeley SPRG page [PROXY]: a = 3.6×10⁻⁵ s⁻¹ (7.7 h), Ec = 0.5 mV/m, d = −1.5×10⁻³ nT/s per mV/m, b = 0.20 nT/(eV/cm³)^½, c = 20 nT.
- **Not used** for any number. Cited only as the origin of the injection–decay form.

### Newell et al. 2007 (`newell2007universal`), Kp physics baseline
- **UNVERIFIED (secondary only):** dΦMP/dt = v^(4/3)·B_T^(2/3)·sin^(8/3)(θc/2), with B_T = √(By² + Bz²) in GSM. Sources: Frontiers 10.3389/fspas.2022.990789 and the chaosmagpy documentation.
- **Clock angle:** the sources write it as arccos(Bz/B_T) or as arctan(By/Bz). orbitlife uses arccos(Bz/B_T) ∈ [0, π], which equals atan2(|By|, Bz). sin(θc/2) does not depend on the sign of By.
- **Units (UNVERIFIED, same secondary sources):** v in km/s and B in nT, with no 10⁻³ factor. chaosmagpy multiplies by 10⁻³, a library convention. The scale does not affect the Kp baseline, which is a regression on the feature.
- **Kp correlation:** not found.

### Threshold-weighted CRPS (`allen2023transformed`, `gneiting2011comparing`)
- **[direct, arXiv preprint]** Allen, Ginsbourger & Ziegel (arXiv 2202.12732):
  - §2.1 Eq. (6): twCRPS(F, y; ν) = ∫(F(z) − 1{y ≤ z})² dν(z).
  - Proposition 1, Eq. (7): twCRPS = E|v(X) − v(y)| − ½E|v(X) − v(X′)|, with v(x) − v(x′) = ν([x′, x)).
  - For the weight 1{z ≥ t}, v(z) = max(z, t).
- **Main-agent inference** (not stated in the paper): v is non-decreasing, so v applied to the quantiles gives the quantiles of v(F). twCRPS can therefore be computed from quantile forecasts with the usual pinball estimator.
- Gneiting & Ranjan 2011: paywalled; equation number not verified.

### Kyoto Dst coverage (`kyoto_dst_index_2026`) [direct, 2026-10-08]
- Final: 1957–2020.
- Provisional: 2021-01 → 2026-07. All 24 months of 2024–2025 are listed; the month pages were not opened.
- Real-time (quicklook) only: from 2026-08.
