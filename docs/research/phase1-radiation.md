# Phase 1 research: radiation references

Source: `researcher` subagent (Sonnet), 2026-10-06. The researcher read most PDFs through a text-conversion proxy, so the main agent re-checked the key tables against the original PDFs (pypdf), marked **[verified]** below. Citation keys refer to `docs/refs.bib`.

## Dose-depth: AP8/AE8 + SHIELDOSE-2 (`sinclair2013radiation`) [verified]
- **SPENVIS inputs (Table 1):**
  - 1 mission segment, 5-year duration, heliosynchronous orbit
  - start 1 Jan 2011, 800 km altitude, 06:00 local ascending node
  - AP-8 at **solar minimum** (protons), AE-8 at **solar maximum** (electrons)
  - ESP-PSYCHIC total solar-proton fluence at 80% confidence (H to H)
  - galactic cosmic rays H to U, default magnetic shielding
  - **SHIELDOSE-2, centre of Al spheres, silicon target**
- **Table 3 (star-tracker sectoring):** the contributed 5-year dose is "derived from the total dose in the SHIELDOSE-2 report file multiplied by the fraction of sphere":

  | Element | Fraction | Al thickness | Contributed dose |
  |---|---|---|---|
  | Lens | 22% | 20 mm | 0.39 krad |
  | Chassis side | 53% | 2.5 mm | 9.34 krad |
  | Satellite body | 25% | 10 mm | 0.64 krad |
  | Total | | | 10.37 krad |

- **Full-sphere SHIELDOSE-2 dose at each depth** (derived by dividing, using the paper's stated method):

  | Depth | Dose | Rounding error |
  |---|---|---|
  | 2.5 mm | 17.62 krad(Si) | ±1.0% |
  | 10 mm | 2.56 krad(Si) | ±2.8% |
  | 20 mm | 1.77 krad(Si) | ±3.6% |

  Rounding comes from the 2-decimal doses and whole-percent fractions. The values fall steadily with depth (the researcher's "non-monotonic" remark was wrong).

## Measured dose behind slabs: Shields-1 (`thomsen2022shields1`) [verified]
- **Orbit:** NORAD 43850, 500 km, 85°, launched 16 Dec 2018 (solar minimum). It operated for about 10 months.
- **Geometry:** "Infinite slab, geometry approximation", ">95% incident radiation through shielding sample", "Large sample field of views, thick backing". Table column headers: "2pi str omnidirectional".
- **Results table** ("Experimental TID (Rad (Si))/Year"):

  | Dosimeter | Shield | Measured | Modeled, AP8 AE8 + SOLPRO via NOVICE | Modeled with a 6 g/cm² backslab added |
  |---|---|---|---|---|
  | UDOS 1 | Al 6.00 g/cm² (2.22 cm) | 70.0 ± 3.0 | 13.69 ± 0.07 | 27.38 ± 0.11 |
  | UDOS 2 | Al 3.00 g/cm² (1.11 cm) | 73.6 ± 3.2 | 22.13 ± 0.09 | 35.82 ± 0.11 |

- **Caveats:**
  - Measured values are per-year rates, but the accumulation interval behind them is not stated in the extract (a figure shows a 17-day accumulation period).
  - The thinnest Al sample is listed as both 1.29 and 1.26 g/cm² in the same document, so it is not used.
  - The model under-predicts by 2–5×.

## Measured ISS dose: DOSIS / DOSIS 3D (`berger2017dosis`) [verified, Table 6]
DOSTEL silicon detectors in the Columbus module.

| Phase | Dates | ISS altitude | DOSTEL-1 | DOSTEL-2 | LiF TLD |
|---|---|---|---|---|---|
| DOSIS 1 | 15 Jul–27 Nov 2009 | 339–348 km | 248 ± 20 | 231 ± 12 | 261 ± 21 |
| DOSIS 3D 3 | 28 Mar–11 Sep 2013 | 407–416 km | 297 ± 23 | 259 ± 13 | 294 ± 7 |
| DOSIS 3D 7 | 27 Mar–11 Dec 2015 | 398–405 km | 254 ± 20 | 221 ± 15 | 237 ± 7 |

All rates are in µGy/day. Table 6 has 10 phases (2009–2016).

- **Units:** DOSTEL measures energy deposited **in silicon**. Dose in water = dose in Si × 1.23 (§2). The text after Table 6 refers to the DOSTEL values "(in silicon)".
- **Location:** a Nomex box under the European Physiology Module. The paper says the DOSTELs "are heavier shielded", **but gives no shielding thickness**, so a validation case is deferred (docs/open-issues.md).
- **Secondary compilation** (`gutierrez2023cots`, review; cross-check only):
  - PADLES 247–360 µGy/d (2008–09, 352 km)
  - ISS-RAD 255 µGy/d (2016–17, 411 km, "12 mm Al")

## Other single-depth or inferred dose
- **NuSat-5** (`acha2020ybco`): ~2 Gy(Si) over 433 d behind an effective 9 mm Al, at 500 km and 97.33°. One depth only; geometry and AP8/AE8 phase not stated.
- **LabOSat-01** (`finazzi2025labosat`): measured 3.9–15.1 Gy over 1100 d at 476–490 km and 97.34°. SHIELDOSE-2 was used to *infer* the effective shielding (2.9–5.7 mm Al), so these are not forward-model references.

## SEU rates (CREME96 and flight)
- **ISS TMS44400 1Mx4 DRAM** (`koontz2020issee`, slides):

  | | 10 g/cm² median shielding | 40 g/cm² median shielding |
  |---|---|---|
  | CREME-96 prediction | 1.1e-7 | 3.1e-8 |
  | In flight (2010–2017) | 8.5e-8 | 7.0e-8 |
  | FLUKA | 8.8e-8 | 7.2e-8 |

  All in SEU/bit/day. The device cross-section slide is garbled (σsat exponent unclear, W unreadable), so this is **UNVERIFIED for parameters**. Case deferred.
- **4 Mbit RHBD SRAM** (`zebrev2017compact`, preprint): CREME96 RPP gives 3.57e-11 (solar min) and 4.50e-12 (solar max); in flight 1.8e-10 errors/bit/day. The orbit is not stated, so it can't be used alone.
- **Kintex UltraScale 20 nm Weibull** (`lee2015kintexus`):
  - configuration memory: LETth 0.8, W 27, s 0.88, σsat 2.0e-9 cm²/bit
  - BRAM: LETth 0.9, W 53, s 1.0, σsat 1.0e-8 cm²/bit

  These are GEO parameters, useful only to unit-test the Weibull integration.
- **No fully specified LEO CREME96 worked example found** (UNVERIFIED). Not yet tried: Tylka et al. 1997.
