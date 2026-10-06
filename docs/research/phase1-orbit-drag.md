# Phase 1 research: reference missions, orbit geometry and drag

Source: `researcher` subagent, 2026-10-05. Values are transcribed unchanged. Citation keys refer to `docs/refs.bib`.

Status meanings:
- **CONFIRMED**: a primary source was opened.
- **CORRECTED**: the published value contradicts its own inputs; the corrected value is used.
- **UNVERIFIED**: there is no primary source. Never use these as evidence.

## Reference missions

| Mission | Altitude | Inclination | Source | Status | Note |
|---|---|---|---|---|---|
| Starlink shell 1 (authorized) | 550 km (±30 km) | 53° | `fcc2021spacex_mod3` ¶4, fn 17 | CONFIRMED | 72 planes × 22 = 1,584 satellites. The same order also covers 540 km/53.2° and 570 km/70° shells. |
| Starlink shell 1 (operated, 2026) | ~480 km planned | 53° | news only | UNVERIFIED | Possible operating-altitude change; 550 km stays the regulatory reference |
| Starlink polar | 560 km (must stay below 580) | 97.6° | `fcc2021spacex_mod3` ¶4, ¶6 | CONFIRMED | 348 satellites (6 × 58) plus 172 satellites (4 × 43) |
| OneWeb | ~1200 km | 87.9° | `fcc2022oneweb` ¶2, ¶6 | CONFIRMED | No primary source gives a measured operating altitude |
| ISS | 330–425 km (kept up by reboosts); ~415 km in 2024 | 51.6° | `nasa2017ssp51071` §3.0; `nasa2024issdeorbit` p.3 | CONFIRMED | Lifetime "roughly one-to-two years without reboosts" |

## Sun-synchronous inclination

**Constants from Boain** (`boain2004sso`, Eq. 1, §III, CONFIRMED):
- J2 = 0.00108263
- required node rate 0.9856°/day
- aₑ = 6378.14 km
- Boain does not give μ.

**Published worked pair:** Aqua at h = 705.3 km has i = 98.2° (§IX). CONFIRMED.

**Pairs computed by the researcher** (Boain Eq. 1 with an assumed μ = 398600.4418 km³/s²). These are **UNVERIFIED** because no published table was opened (Vallado and SMAD are paywalled):

| Altitude (km) | Inclination (°) |
|---|---|
| 500 | 97.402 |
| 560 | 97.632 |
| 600 | 97.788 |
| 700 | 98.188 |
| 800 | 98.603 |

Self-check: 705.3 km gives 98.210°, which matches Aqua's published 98.2°.

## Eclipse and beta angle

- **Aqua worked example** (`boain2004sso` §IX–X):
  - Inputs: h = 705.3 km, i = 98.2°, mean local time 13:40:30, β_min ≈ 17° (July), ρ = 64.2°, Φ/2 = 62.9°.
  - Published maximum eclipse: **38.9 min**. That contradicts Boain's own inputs: the period P = 86400·16/233 s = 98.88 min, so (2·62.94°/360°)·P = **34.6 min** (CORRECTED). Use 34.6, not 38.9.
  - β range: 17–29° in 2004 and 18–31° in 2005 (Fig. 8).
- **Independent reference tools:**
  - **Orekit 13.1.9** (`orekit_13_1_9`): `EclipseDetector(sun, SUN_RADIUS, OneAxisEllipsoid(WGS84))`, with `.withUmbra()` or `.withPenumbra()`. This is the recommended reference.
  - **Skyfield 1.55** (`skyfield_1_55`): `is_sunlit()` treats Earth as a sphere and the Sun as a point, with no penumbra, so it is a rough cross-check only.
  - **GMAT:** documentation unreachable (UNVERIFIED).

## Drag and decay references

### ISS
- **Mass:** 419,725 kg (`nasa_iss_facts`, CONFIRMED, preferred). Also ">430,000 kg" (`nasa2024issdeorbit`, a lower bound).
- **Design-era drag inputs:** C_D = 2.2, A = 2673 m², m = 420,000 kg, so C_D·A/m = 0.014 m²/kg (`smith1997issdensity`, CONFIRMED). This is a pre-assembly estimate.
- **Measured decay rate between reboosts:** no primary source found (**UNVERIFIED**).
  - Plan: derive the reference ourselves from Space-Track TLEs for NORAD 25544 between reboosts, plus GFZ F10.7/Kp.
  - Label the tolerance as our own choice.

### Tiangong-1 (`pardini2019tiangong1`, CONFIRMED)
- **Mass:**
  - 8,506 kg at launch, including 1,000 kg of propellant
  - ~7,500–7,550 kg at end of mission
  - ~7,150 kg dry
- **Inclination:** ≈ 42.8° (`esa2018tiangong_blog`).
- **Mean altitude** (US TLEs):

  | Date | Altitude |
  |---|---|
  | 2016-03-16 | ~390 km |
  | 2018-03-03 | ~250 km |
  | 2018-03-28 | 200 km |
  | 2018-04-01 16:07 UTC | 150 km |

- **Semi-major-axis decay rate:**

  | Period | Rate |
  |---|---|
  | Mar–Dec 2016 | 105 m/day |
  | 2017 | 216 m/day |
  | Jan 2018 | 389 m/day |
  | Feb 2018 | 591 m/day |
  | Mar 2018 | 2.96 km/day |
  | Last 2 days | ~27 km/day |

  The 81-day mean F10.7 stayed below 100 sfu (below 70 sfu from Feb 2018).
- **Ballistic parameter:** B = C_D·A/M = 0.007388 m²/kg (σ 6.7%), from an NRLMSISE-00 fit to 8 Jan–1 Apr 2018.
- **Reentry:**
  - 80 km interface at 2018-04-02 00:10 UTC ± 1 min (JSpOC; preferred for decay models).
  - Surface impact ~00:16 UTC at 13.6°S 164.3°W (ESA).

### Starlink Group 4-7 loss, Feb 2022 (all CONFIRMED)
- **Launch:** 2022-02-03 18:13 UTC, 49 satellites, deployed at ~210 km perigee / 350 km apogee / 53° (`spacex2022geostorm`, `fang2022starlink`).
- **Losses:** 38 of 49 (`fang2022starlink`, `dang2022starlink`, `hapgood2022spacex`).
- **SpaceX:** drag "up to 50 percent higher than during previous launches", from onboard GPS.
- **Geomagnetic conditions:**
  - Kp (GFZ definitive, `matzka2021kpdata`): 5− and 5+ on 3 Feb, 5+ and 5− on 4 Feb. Daily Ap 26 and 32.
  - Dst (provisional, `kyoto_dst_202202`): minimum −66 nT on 3 Feb (hour ending 11 UT) and −62 nT on 4 Feb.
- **Density enhancement:**
  - `fang2022starlink` (full text read; preferred): WAM-IPE gives 50–125% at 200–400 km, but MSIS-00 gives at most 20%.
  - `dang2022starlink`: ~20–30% at ~210 km (abstract only).
  - `kataoka2022starlink`: drag up to 50%; NRLMSIS 2.0 gives below 25% (abstract only).
  - **This gap is a known weakness of NRLMSIS-class models during storms. Our validation must report it honestly.**
- **Decay model inputs** (`baruah2024starlink`, JB2008):
  - m = 227 kg, C_D = 1, ram area 1.00 or 4.48 m².
  - Storm decay was 6 h faster (1.00 m²) or 2 h faster (4.48 m²) than in quiet conditions.
  - The 227 kg looks like the v1.0 mass, but Group 4-7 flew v1.5, whose mass is **UNVERIFIED**.
- **Response:** the next launch used a 300 km initial orbit and 46 satellites (`hapgood2022spacex`).

## Open items
- Vallado or SMAD SSO table (UNVERIFIED; we can use Boain's Aqua pair plus our own computed values, labelled as such).
- ISS measured decay rate (to be derived from TLEs).
- GMAT eclipse configuration.
- Starlink v1.5 mass and area.
