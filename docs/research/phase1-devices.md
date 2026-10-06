# Phase 1 research: device radiation test data

Source: `researcher` subagent, 2026-10-05. Values are transcribed unchanged. Citation keys refer to `docs/refs.bib`.

Units used throughout:
- **LET:** MeV·cm²/mg
- **cross-section σ:** cm² per bit or per device, as stated
- **TID:** krad(Si)

Anything marked UNVERIFIED must be flagged `heuristic` if it is used at all.

## Google TPU v6e (Trillium): Project Suncatcher (`aguera2025suncatcher`, arXiv:2511.19468v2)

**Test setup:**
- 67 MeV protons at the UC Davis Crocker Nuclear Lab.
- The beam passed through ~1 mm Al, a heatsink and the PCB, so the spectrum at the chip was degraded, not a clean 67 MeV.
- Test temperature and number of chips were not stated.

**Results:**

| Quantity | Value | Status |
|---|---|---|
| Mission TID requirement (Google's estimate, SSO, ~10 mm Al) | ~150 rad(Si)/yr; ~750 rad(Si) over 5 yr | CONFIRMED (not a validation reference) |
| HBM irregularities begin | 2 krad(Si) | CONFIRMED (stress-test criterion) |
| Highest TID tested, no hard failure | 15 krad(Si) | CONFIRMED (a test limit, not a failure point) |
| SDC (logic plus on-chip SRAM) | 14.4–20 rad per event, so σ ≈ 6–9e-9 cm²/chip | CONFIRMED |
| HBM uncorrectable errors | ~44 rad per event (203 events), so σ ≈ 3e-9 cm²/chip | CONFIRMED |
| System SEFI (crash) | 1 per 5 krad per chip, so σ ≈ 2e-11 cm²/chip | CONFIRMED |
| Host CPU / RAM SEFI | 1 per 450 / 1 per 400 rad(Si) | CONFIRMED (parts not identified) |
| SEL | not reported | **UNVERIFIED: no data** |

The paper's dose-to-fluence conversion is 1 rad ≈ 7.9e6 protons/cm².

## DDR4 SDRAM (`dufour2022ddr4`, RADECS 2022; heavy ions at RADEF; dies thinned to ~75 µm)

SEU was tested at room temperature and nominal VDD. The Weibull width W and shape s are **not reported** (UNVERIFIED).

| Part | SEL | SEU Weibull (LETth; σsat static / dynamic, cm²/bit) | SEFI (cm²/device) | TID |
|---|---|---|---|---|
| Micron MT40A512M16JY-075E (8 Gb) | none up to LET 60 at 95 °C | 0.5; 1.14e-10 / 4.49e-11 | 2.75e-5 dynamic, 1.96e-5 static at LET 60.9 | 99 krad: 1 biased part failed at that step |
| SK hynix H5AN8G6NCJR-VKI (8 Gb) | none up to LET 60 at 125 °C | 0.5; 8.5e-11 / 2.3e-11 | 7.5e-6 dynamic, 2.4e-6 static at LET 62 | 100 krad, no failure |
| Samsung K4A4G165WF-BITD (4 Gb) | none up to LET 60 at 125 °C | static 2.5, 3.1e-11; dynamic 0.2, 8.9e-13 | — | not tested |
| Micron MT40A256M16LY-062E (4 Gb) | none up to LET 60 at 95 °C | 0.5; 2.6e-11 | — | 100 krad, no failure |
| Nanya NT5AD256M16D4-HRI (4 Gb) | none up to LET 62 at 95 °C | 1.45; 4.4e-12 | — | 99 krad: IPP drift that recovered after anneal |

SEFI values are the researcher's conversion of count ÷ fluence.

Caveats from the paper:
- Current steps under Xe ions needed a manual power cycle. The authors call them SEFI, "not pure SELs".
- Several parts showed stuck bits.

**Other DDR4 sources:**
- **Rad-tolerant Teledyne e2v DDR4T04G72M** (`teledyne_ddr4t04g72`, distributor copy of manufacturer data):
  - SEL LETth > 60.88
  - SEU LETth 8.19; σ 5.55e-12 cm²/bit at LET 60.88
  - SEFI LETth 2.6; σ 2.22e-4 cm²/device
  - TID target 100 krad
- **Proton SEU vs temperature** (`ryu2025ddr4temp`, abstract only): error density ranges from 5.59e-6 at 373 K to 9.77e-10 at 153 K, at 48 MeV. Use it as a temperature trend only.
- **Proton tests at 200 MeV** (`obryan2017compendium`, `obryan2023compendium`): stuck bits 1e-17 cm²/bit and SEFI 1e-9 cm² (DDR4 inside a Snapdragon 820 package). A Mercury DDR4 module showed stuck bits and a ~50 mA current increase.
- **Commercial DDR4 proton cross-section and Bendel A/B:** UNVERIFIED (paywalled).

## DDR5 and HBM
- **DDR5 protons** (`li2025ddr5`): measured, but the numbers are paywalled (UNVERIFIED).
- **DDR5 heavy ions:** none found (UNVERIFIED, so `heuristic`).
- **Standalone HBM2/2e/3:** none found (UNVERIFIED). The only HBM data are the TPU v6e in-system rows above.
- **Volta stacked HBM2 under neutrons** (`dossantos2021due`): turning ECC on raised the detected-unrecoverable-error (DUE) FIT up to 13.7×. Rates are in arbitrary units only.

## NVIDIA GPUs

| Device | Test | Result | Source |
|---|---|---|---|
| Jetson TX1 (20 nm) | 200 MeV p | SEU σ average 6.22e-8 cm²/device | `wyrwas2019tx2`, `obryan2017compendium` |
| Jetson TX2 (20 nm) | 200 MeV p | SEU σ average 1.02e-9 cm²/device. SEFI in every run. 1 of 2 units failed catastrophically at ~60 rad(Si) (cause pending) | `wyrwas2019tx2` |
| Jetson TX2 | heavy ion | **No SEL at LET 37 up to 80 °C**; crash σ ≈ 4× SDC σ | `coelho2025tx2` (abstract only) |
| Xavier NX (12 nm) | 125/200 MeV p | OS-crash SEFI σ 3.97–6.71e-9 cm²/device | `cannon2023xavier` |
| Xavier NX | heavy ion | SEFI from 2.95e-7 (LET 0.1) to 4.48e-3 (LET 40.4) cm²/device. **Destructive SEL at LET 40, die heated up to 100 °C** | `cannon2023xavier` (conflicts with an earlier test) |
| Orin NX (7 nm) | 480 MeV p | SoC SEU 2.5–4.4e-9 cm²/device; GPU SEU 3.52e-10. 3 suspected SEL current surges were recovered by cutting power | `rodriguezferrandez2024orin` |
| Orin / Xavier | heavy-ion SEL | compared in the paper, but values not accessible | `rodriguezferrandez2025jetsonhi` (UNVERIFIED) |
| Tesla K20X | neutrons | σSDC (4.8±0.4)e-7 cm²; σcrash (2.7±0.2)e-7 cm² | `tiwari2015gpu` via `asorey2022exascale` (secondary) |
| A100 / H100 | any | absolute rates not public | UNVERIFIED, so `heuristic` |

## Rad-hard SRAM: Frontgrade/CAES UT8R1M39/2M39/4M39 (`frontgrade_ut8rxm39`)
- TID: 100 krad(Si)
- SEL immune up to LET 110
- SEU: 7.3e-7 errors/bit-day (GEO, Adams 90% worst case, 100 mil Al)
- Not given (UNVERIFIED): a LEO rate, Weibull parameters, the SEL test temperature.

## DRAM field reliability and ECC (workload-model references)
- **Google fleet DRAM errors** (`schroeder2009dram`):
  - 25,000–70,000 FIT/Mbit
  - 8.2% of DIMMs per year with correctable errors
  - 0.22% of DIMMs per year with uncorrectable errors
  - These count errors, not faults, and hard errors dominate.
- **DDR3 fault FIT** (`sridharan2015memory`, preferred):
  - 25 (Hopper) vs 40 (Cielo) FIT/device.
  - Fault modes: 78.9% single-bit, 5.9% column, 9.2% row, 4.3% bank, 0.6% multi-bank, 1.0% multi-rank.
  - Faults undetectable by SECDED: 21.7 / 1.8 / 0.2 FIT/device for vendors A/B/C.
  - Chipkill gives a 42× lower uncorrected error rate than SECDED (secondary citation).

## Latchup protection
- **Space Electronics latchup protection** (`techbriefs_lpt`): recovery shown with 45 µs and 2.5 ms supply-off times; peak latchup current 146–267 mA. Detection delay and prevention probability are **not stated**.
- **Latent damage** (`becker2002latent`): after a protected (non-destructive) latchup, voids in the metal lines can cut interconnect cross-section by 1–2 orders of magnitude.
- **Probability that protection prevents destructive SEL:** no quantitative source (UNVERIFIED, so `heuristic`, as the roadmap expects).

## Coverage note
The researcher's web searches hit a session limit near the end, so the HBM and latchup-mitigation searches may be incomplete.
