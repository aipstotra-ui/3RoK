# orbitlife API sketch (Phase 1)

This is a design document, not code. It fixes the public surface that Phase 2–4 will implement, so validation cases, the TypeScript package and the web app can be planned against it.

Names and signatures may change in review. Each change must update the validation cases that target it (`validation/cases/**/*.yaml` → `target:`).

## Conventions (all public functions)

- **Units in names.** Parameters and fields carry their unit: `altitude_km`, `beta_deg`, `dose_rad_si_per_yr`, `flux_cm2_s`. Inside numerical code these are plain floats or NumPy arrays (ADR 0003).
- **Time** is a timezone-aware UTC `datetime` or an ISO-8601 string ending in `Z`. Internally `astropy.time.Time` handles UTC/TT/UT1 (ADR 0002).
- **Orbit elements** are mean elements, circular unless `eccentricity` is given.
  - `altitude_km` = mean semi-major axis − 6378.137 km. This is **not** geodetic height (see `validation/reference/missions.yaml`).
  - `ltan_h` is the mean local time of the ascending node.
- **Results are typed.** Headline results are `Quantity` objects (`value`, `unit`, `uncertainty`, `source`) inside a pydantic result model with a `flags` list. Every `heuristic` or `assumption` input that affected the result appears in `flags` (ground rule 2).
- **No silent zeros.** When a device has no data for an effect, the result says `no_data`, never 0.

## Building blocks (targets of current validation cases)

```python
# orbitlife.orbit
def sso_inclination_deg(altitude_km: float, eccentricity: float = 0.0) -> float:
    """Mean inclination of a sun-synchronous orbit (first-order J2 secular node rate)."""


def eclipse_duration_min(
    altitude_km: float, beta_deg: float, shadow_model: Literal["cylindrical", "conical"] = "conical"
) -> float:
    """Time in Earth's shadow per revolution at a given beta angle."""


# orbitlife.drag
def days_to_altitude(
    start_epoch_utc: str,
    start_altitude_km: float,
    end_altitude_km: float,
    inclination_deg: float,
    ballistic_coefficient_m2_per_kg: float,
    eccentricity: float = 0.0,
    density_model: str = "nrlmsis2",
    space_weather: Literal["historical", "forecast", "climatology"] = "historical",
) -> float:
    """Propagate orbital decay until the mean altitude reaches end_altitude_km."""


def storm_drag_ratio(
    perigee_km: float,
    apogee_km: float,
    inclination_deg: float,
    storm_window_utc: tuple[str, str],
    averaging: str,
    statistic: str,
    step_s: float,
    baseline: str,
    baseline_ap: float,
    baseline_ap_mode: str,
    storm_ap_mode: str,
    raan_source: str,
    space_weather: str,
) -> float:
    """Ratio of storm-time to quiet-baseline drag on one orbit (see the Starlink G4-7 case)."""
```

```python
# orbitlife.radiation
def tid_dose_rad_si(
    altitude_km: float,
    start_epoch_utc: str,
    duration_yr: float,  # Julian years (365.25 d)
    geometry: Literal["solid_sphere_center", "slab_two_sided", "slab_one_sided"],
    shielding_mm_al: float | None = None,  # exactly one of mm Al or g/cm2 Al
    shielding_g_cm2_al: float | None = None,
    rear_shielding_g_cm2_al: float | None = None,  # slab_two_sided only
    inclination_deg: float | None = None,  # exactly one of inclination_deg or sun_synchronous
    sun_synchronous: bool = False,
    ltan_h: float
    | None = None,  # no effect on static AP8/AE8 or a Stormer cutoff; kept for later models
    target_material: Literal["si"] = "si",
    trapped_proton_model: str = "ap8min",
    trapped_electron_model: str = "ae8max",
    solar_proton_model: str | None = None,  # design mode is explicit, e.g. "esp_psychic"
    solar_proton_confidence: float | None = None,  # required when solar_proton_model is set
    sep_magnetic_shielding: str = "stormer_quiet",
    include_gcr: bool = False,
) -> DoseResult:
    """Total ionizing dose behind aluminium (circular orbits only).

    Geometry (SHIELDOSE-2 conventions, Seltzer 1994):
    - solid_sphere_center: 4 pi isotropic dose at the centre of a solid Al sphere.
    - slab_one_sided: 2 pi isotropic incidence on a semi-infinite Al slab (no doubling).
    - slab_two_sided: front slab (2 pi) plus rear slab (2 pi), summed.
    Trapped-proton anisotropy is ignored (AP8 is omnidirectional).

    DoseResult.value is the total in rad(Si). DoseResult.components splits it into trapped
    protons, trapped electrons with bremsstrahlung, SEP and GCR. DoseResult.flags lists every
    assumption or heuristic used (ground rule 2).
    """
```

```python
# orbitlife.forecast
def noaa_3day_kp(issue_utc: str, block_start_utc: str) -> float:
    """NOAA SWPC 3-day forecast Kp for one 3-hour block, exactly as printed (two decimals), from the archived text product."""


def noaa_baseline_kp(issue_time_utc: str, block_start_utc: str) -> float:
    """NOAA baseline for our forecast issued at T (protocol section 4.4): newest issue at or before T + 30 min, converted to exact thirds."""
```

```python
# orbitlife.effects
def sel_rate_per_device_day(
    method: Literal["square_approximation", "weibull"],
    sigma_sat_cm2_per_device: float,
    onset_let_eff_si_mev_cm2_mg: float | None = None,  # square_approximation
    weibull: WeibullParams | None = None,  # weibull: let_th, w, s (LET_EFF in Si)
    integral_flux_above_onset_per_cm2_day: float
    | None = None,  # square_approximation with a given flux
    environment: LetSpectrum | None = None,  # or computed from an integral LET spectrum (LET in Si)
    test_temperature_c: float | None = None,
    sigma_confidence_level: float
    | None = None,  # e.g. 0.95 when sigma is an upper limit from zero events
) -> RateResult:
    """Single-event latchup rate per device per day.

    LET is the effective LET in silicon (LET_EFF) throughout. No angle or cosine-law correction is
    applied in the square method. The given flux follows the TI SLVK046 convention: CREME96 integral
    LET flux per cm2 per day, with any geometry factor already folded in. The omnidirectional-vs-per-sr
    and planar-target factor must be recorded before Phase 2 computes the flux from an environment.
    Exactly one input path is allowed per method; other combinations are rejected.
    RateResult.value is events/device/day. RateResult.flags carry the test temperature (SEL
    sensitivity rises with temperature), the sigma confidence level, and the environment percentile
    (e.g. worst week is not a mission average).
    """
```

## Top-level API

```python
import orbitlife as ol

mission = ol.MissionSpec(
    orbit=ol.Orbit(
        altitude_km=550, inclination_deg=53
    ),  # or ol.Orbit.from_reference("starlink-shell1")
    shielding_mm_al=3.0,
    duration_yr=5.0,
    devices=[ol.DeviceSpec.from_reference("ddr4-micron-8gb", count=16)],
    vehicle=ol.Vehicle(
        mass_kg=800, drag_area_m2=10, cd=2.2
    ),  # inputs, flagged as assumptions if not sourced
)

a: ol.Assessment = ol.assess(mission)
a.orbital_lifetime  # Quantity with uncertainty (drag), plus the solar-activity scenario used
a.tid_dose  # per device, behind shielding
a.see_rates  # per device and effect (SEU/MBU/SEFI/SDC), split by trapped / GCR / SEP
a.sel  # destructive and recoverable latchup per device-year, or no_data
a.thermal_margin  # orbit-average and worst-case, from beta and eclipse
a.binding_limit  # which mechanism ends the mission first, and when
a.flags  # every heuristic or assumption that touched a headline number
a.data_version  # data release tag and manifest hashes used

ranked: ol.RankResult = ol.rank(
    mission,
    altitudes_km=range(400, 1201, 50),
    inclinations_deg=[53, "sso"],
    ltan_h=[6, 10.5, 12],
    weights=ol.Weights(...),
)  # Pareto front plus weighted score

fc: ol.ForecastBundle = ol.forecast(issue_time_utc="now", horizons_h=[3, 6, 12, 24])
fc.kp.quantiles  # 0.05 ... 0.95 per horizon
fc.dst.quantiles

action: ol.Decision = ol.decide(
    fc, ol.CostMatrix(...)
)  # lowest expected-cost action, with expected costs

w: ol.WorkloadImpact = ol.workload.impact(
    a, ol.WorkloadSpec.from_reference("resnet50-inference"), ecc="secded", scrub_interval_s=3600
)
w.sdc_per_gpu_hour
w.detected_errors_per_gpu_hour
w.goodput
w.optimal_checkpoint_interval_s

f: ol.FleetResult = ol.fleet.simulate(
    ol.FleetSpec(mission=mission, satellites=1000), scenarios=1000, seed=0, backend="numpy"
)  # or "jax"/"cupy"
f.chip_failures_per_year
f.compute_availability
f.replacement_rate
```

Phase 1 reference sets (`validation/reference/*.yaml`) become `from_reference(...)` constructors, so examples and validation share the same inputs.

## Schemas (ADR 0004)

pydantic v2 models, each with `schemaVersion`, exported to `schemas/*.json` and generated as zod types for `@orbitlife/core`:

- MissionSpec
- DeviceSpec (evolves from `orbitlife_build.reference.Device`; see docs/open-issues.md for the Phase 2 additions: Weibull fit object, structured conditions, fluence and counts)
- WorkloadSpec
- FleetSpec
- Assessment
- RankResult
- ForecastBundle
- CostMatrix
- Decision
- WorkloadImpact
- FleetResult
- DataManifest

## CLI

```
orbitlife assess   --alt 550 --inc 53 --shield-mm 3 --device ddr4-micron-8gb [--json]
orbitlife rank     --mission mission.yaml [--json]
orbitlife forecast [--issue now] [--horizons 3,6,12,24]
orbitlife decide   --forecast fc.json --costs costs.yaml
orbitlife data     fetch|verify [--release data-vYYYY.N]
orbitlife validate [--strict]
orbitlife schema   export
```

Every command can emit JSON (`--json`), so results are scriptable and match the schemas.

## Open questions for Phase 2 review
1. Return `Quantity` objects from the building blocks too, or only from top-level results? Proposal: building blocks return floats (fast, simple); top-level results return `Quantity`.
2. Default density model: NRLMSIS 2.0 (`nrlmsis2`). The Tiangong-1 case pins `nrlmsise00` because its B was fitted with it.
3. The default shadow model is conical (umbra plus penumbra), while the Aqua case asks for cylindrical. Both stay available.
