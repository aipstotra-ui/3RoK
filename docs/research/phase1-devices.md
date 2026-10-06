# Phase 1 research: device radiation test data

Source: `researcher` subagent, 2026-10-05. Values are transcribed unchanged. Citation keys refer to `docs/refs.bib`.

Units used throughout:
- **LET:** MeV·cm²/mg
- **cross-section σ:** cm² per bit or per device, as stated
- **TID:** krad(Si)

Anything marked UNVERIFIED must be flagged `heuristic` if it is used at all.

## Full researcher rows (verbatim, 2026-10-05)

This section keeps the researcher's original rows unabridged, so every detail used in `validation/reference/devices.yaml` can be traced. Restored after physics-reviewer (PR #5) found that an earlier summary had dropped details.

### Google TPU v6e (Trillium): Project Suncatcher (`aguera2025suncatcher`, arXiv:2511.19468v2)

| # | Item | Value | Unit | Conditions | Locator | Status | Note |
|---|---|---|---|---|---|---|---|
| 6.1 | Test conditions | UC Davis Crocker Nuclear Lab, 76-inch cyclotron, 67 MeV protons, 8 cm aperture, beam 2 pA (~2 rad/min) to 1 nA (1 krad/min) | — | whole package (logic die + HBM), irradiated from the underside through ~1 mm Al chassis, a secondary heatsink and the PCB | §4.3 | CONFIRMED | "the energy spectrum incident is not monoenergetic 67 MeV" (heatsink straggling and secondaries). Test temperature not stated; run at full power with heatsinks. Number of chips not stated. |
| 6.2 | Mission TID requirement | ~150 /yr; ~750 over 5 yr | rad(Si) | SSO LEO, ~10 mm Al equivalent | §2.3 | CONFIRMED | Google's estimate, not a validation reference |
| 6.3 | HBM TID onset | 2 ("began to show irregularities") | krad(Si) | 67 MeV p, degraded spectrum | §2.3 | CONFIRMED | Criterion: HBM-specific stress tests |
| 6.4 | Max TID, no hard failure | 15 (max tested) | krad(Si) | single chip | §2.3 | CONFIRMED | Test limit, not a failure point |
| 6.5 | SDC (core logic + on-chip SRAM) | 14.4–20 rad/event, so σ ≈ 6e-9 to 9e-9 | cm²/chip | transformer end-to-end workloads | §4.3 | CONFIRMED | Paper's conversion: 1 rad ≈ 7.9e6 p/cm², so σ ≈ 1.27e-7/D. §2.3: "~1 event/17 rad" in flight |
| 6.6 | HBM UECC | ~44 rad/event (203 events), so σ ≈ 3e-9 | cm²/chip | — | §4.3 | CONFIRMED | HBM correctable-error counts "were not reliably available" |
| 6.7 | System SEFI (crash) | 1 per 5 krad per chip, so σ ≈ 2e-11 | cm²/chip | — | §4.3 | CONFIRMED | The paper's formula gives 1.27e-7/5000 = 2.5e-11; the paper rounds to 2e-11 |
| 6.8 | Host system SEFI | 1 per 450 (CPU); 1 per 400 (RAM) | rad(Si)/event | — | §2.3 | CONFIRMED | Host parts not identified |
| 6.9 | SEL | not reported | — | — | — | UNVERIFIED | No mention of latchup in the paper |

### DDR4 SDRAM (`dufour2022ddr4`, RADECS 2022)

| # | Part | Value | Unit | Conditions | Locator | Status | Note |
|---|---|---|---|---|---|---|---|
| 1.1 | Micron MT40A512M16JY-075E AIT:B (8 Gb x16) | SEL: none up to LET 60 at 95 °C, VDDmax, 1e7 ions/cm², 3 parts. Heavy-ion SEU Weibull: LETth 0.5; σsat 1.14e-10 (static) / 4.49e-11 (dynamic) cm²/bit. SEFI at Xe LET 60.88: 28/1.02e6 = 2.75e-5 (dynamic) and 19/9.71e5 = 1.96e-5 (static) cm²/device (researcher's conversion, count/fluence) | MeV·cm²/mg; cm²/bit; cm²/device | RADEF, die thinned to ~75 µm; SEU at room temperature, nominal VDD; DDR4-2666 | Tab. XII–XIII, p. 7 | CONFIRMED | W and s not reported. Step current increases under Xe needed a manual power cycle; authors call them SEFI, "not pure SELs". SBU and MBU both seen, MBU fraction not given. Stuck bits from LET ~2.6 |
| 1.2 | Micron MT40A512M16, TID | 99 krad(Si), Co-60, 180 rad/h, room temperature, 10 parts (5 biased static, 5 grounded) | krad(Si) | — | §IV, Tab. XIV | CONFIRMED | Part 6 (biased) drew excess current at the 99 krad step and still failed after a 168 h anneal. One part broke in socket insertion. Other biased parts stayed in spec. The previous passing step is not given in the research |
| 1.3 | SK hynix H5AN8G6NCJR-VKI (8 Gb) | SEL: none up to LET 60 at 125 °C. Weibull LETth 0.5; σsat 8.5e-11 (static) / 2.3e-11 (dynamic) cm²/bit. SEFI at Xe LET 62: 7.5e-6 (dynamic) / 2.4e-6 (static) cm²/device (researcher's conversion). TID: 100 krad(Si), no failure | as above | as above | Tab. VIII–IX | CONFIRMED | MBU from LET 8.3. Up to ~2205 stuck bits in one run at LET 62 (2e6 ions/cm²). W and s not reported |
| 1.4 | Samsung K4A4G165WF-BITD (4 Gb) | SEL: none up to LET 60 at 125 °C. Weibull: static LETth 2.5, σsat 3.1e-11; dynamic LETth 0.2, σsat 8.9e-13 cm²/bit. TID: not tested | as above | as above | Tab. VI–VII | CONFIRMED | Table I says "K4A4G165WE-BITD" but the text says WF |
| 1.5 | Micron MT40A256M16LY-062E IT:F (4 Gb) | SEL: none up to LET 60 at 95 °C. Weibull LETth 0.5, σsat 2.6e-11 cm²/bit (static and dynamic). TID: 100 krad(Si), no failure | as above | as above | Tab. IV–V | CONFIRMED | One MBU (Xe) |
| 1.6 | Nanya NT5AD256M16D4-HRI (4 Gb) | SEL: none up to LET 62 at 95 °C (5e6 ions/cm²); non-destructive current steps up to 100 mA. Weibull LETth 1.45, σsat 4.4e-12 cm²/bit. TID: 99 krad(Si), IPP drift that recovered after anneal | as above | as above | Tab. X–XI | CONFIRMED | No MBU. Table XI dynamic row internally inconsistent |
| 1.7 | Teledyne e2v DDR4T04G72M (rad-tolerant), `teledyne_ddr4t04g72` | SEL LETth > 60.88; SEU LETth 8.19, σ 5.55e-12 cm²/bit at LET 60.88; SEFI LETth 2.6, σ 2.22e-4 cm²/device at LET 60.88; TID target 100 krad | MeV·cm²/mg; cm²/bit | heavy ions | product page | CONFIRMED | Distributor copy of manufacturer figures. Die source and SEL temperature not stated |
| 1.8 | DDR4 proton SEU vs temperature, `ryu2025ddr4temp` | error density 5.59e-6 (373 K) to 9.77e-10 (153 K) | dimensionless | 48 MeV p | abstract | CONFIRMED | Not a cm²/bit cross-section; temperature trend only |
| 1.9 | Mercury 4N1G72T-24BM module, `obryan2023compendium` | stuck bits at 60 and 200 MeV; ~50 mA current increase | — | MGH, Dec 2022 | Table (ref [23]) | CONFIRMED | No cross-section given |
| 1.10 | DDR4 in Snapdragon 820 package, `obryan2017compendium` | stuck bits 1e-17 cm²/bit; SEFI 1e-9 cm² | — | 200 MeV p, MGH, Oct 2016 | Table I | CONFIRMED | The SEFI may belong to the SoC |
| 1.11 | Commercial DDR4 proton σ and Bendel A/B | — | — | — | — | UNVERIFIED | Paywalled |

### DDR5 and HBM

| # | Item | Value | Status | Note |
|---|---|---|---|---|
| 2.1 | DDR5 proton SEE, `li2025ddr5` | cross-section vs energy measured; vendor- and PMU-dependent | UNVERIFIED (numbers) | Paywalled |
| 2.2 | DDR5 heavy-ion SEU/SEL | — | UNVERIFIED | None found |
| 3.1 | Standalone HBM2/2e/3 data | — | UNVERIFIED | Only the TPU v6e in-system rows |
| 3.2 | Volta stacked HBM2, neutrons, `dossantos2021due` | ECC on raises DUE FIT up to 13.7× | CONFIRMED | Arbitrary units only |

### NVIDIA GPUs and SoCs

| # | Device | Value | Unit | Conditions | Locator | Status | Note |
|---|---|---|---|---|---|---|---|
| 4.1 | Jetson TX1 (20 nm), `wyrwas2019tx2` / `obryan2017compendium` | SEU σ average 6.22e-8 (range 2.65e-9 to 5.05e-7) | cm²/device | 200 MeV p, MGH | Tab. 3 / Tab. I | CONFIRMED | |
| 4.2 | Jetson TX2 (20 nm), `wyrwas2019tx2` | SEU σ average 1.02e-9 (range 2.50e-10 to 4.17e-9) | cm²/device | 200 MeV p, MGH, Jun 2019, 2 parts | §6, Tab. 2 | CONFIRMED | SEFI in every run, each needing a power cycle. Part 2 failed catastrophically in its first run (~60 rad(Si)), root cause pending. Die ~25 °C above room temperature at full load |
| 4.3 | Jetson TX2, `coelho2025tx2` | No SEL at LET 37 up to 80 °C | MeV·cm²/mg | 3 facilities | abstract | CONFIRMED | Crash σ ≈ 4× SDC σ with heavy ions. Full text not accessed |
| 4.4 | Xavier NX (12 nm), `cannon2023xavier` | OS-crash SEFI σ 3.97e-9 to 6.71e-9 | cm²/device | 125 and 200 MeV p, Northwestern Medicine Chicago Proton Center, Jul 2021 | Tab. 2 | CONFIRMED | Data-error σ are upper limits (0 events): ~5.7e-10 to 9.6e-10. The range is not resolved by energy in the research |
| 4.5 | Xavier NX heavy-ion SEFI, `cannon2023xavier` | from 2.95e-7 (LET 0.106) to 4.48e-3 (LET 40.4) | cm²/device | TAMU K500, 15 MeV/u, LET 0.1–52, thinned die | Tab. 5 (DCNN without SMM) | CONFIRMED | No Weibull fit given |
| 4.6 | Xavier NX SEL, `cannon2023xavier` | destructive at LET 40 with die heated up to 100 °C: second ~2 A spike, then persistent failure | — | TAMU | §V (p. 8) | CONFIRMED | Conflicts with an earlier test (not thinned, pulsed beam); authors say more work needed |
| 4.7 | Orin NX (7 nm), `rodriguezferrandez2024orin` | SoC SEU σ 3.90e-9 (15 W), 4.43e-9 (10 W), 2.50e-9 (<10 W). SEFI 1.59e-9, 1.51e-9, 6.81e-10. GPU SEU 3.52e-10; GPU SEFI 6.54e-10 | cm²/device | 480 MeV p, TRIUMF BL1B | Tab. II–V | CONFIRMED | Three suspected SEL current surges in the POW2 region recovered after the power meter cut power; source (module vs carrier regulator) not identified. Temperature not stated |
| 4.8 | Orin / Xavier heavy-ion SEL, `rodriguezferrandez2025jetsonhi` | — | — | — | abstract | UNVERIFIED | Values not accessible |
| 4.9 | Tesla K20X, `tiwari2015gpu` via `asorey2022exascale` | σSDC (4.8±0.4)e-7; σcrash (2.7±0.2)e-7 | cm² | neutrons, ISIS and LANSCE, 10–750 MeV | p. 15 | CONFIRMED (secondary) | |
| 4.10 | A100/H100 absolute rates | — | — | — | — | UNVERIFIED | Normalized FIT only |

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
