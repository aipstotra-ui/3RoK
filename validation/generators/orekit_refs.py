"""Generate orbit-geometry reference values with Orekit (an independent implementation).

Run (needs Java and a pinned orekit-data zip; see validation/generators/README.md):

    JAVA_HOME=... uv run --no-project --with orekit-jpype==<ver> \
        python validation/generators/orekit_refs.py OREKIT_DATA_ZIP > orekit_refs.out.json

Outputs JSON with the reference values and every version needed to reproduce them.
Conventions match docs/api-sketch.md:
- circular two-body orbits; altitude = a - 6378.137 km
- RAAN in GCRF; beta = asin(orbit normal . Sun direction) in GCRF
- eclipses: spherical Earth (R = 6378.137 km), Sun as a sphere of radius Constants.SUN_RADIUS
"""

from __future__ import annotations

import hashlib
import importlib.metadata as md
import json
import math
import sys
from pathlib import Path

import orekit_jpype as orekit

orekit.initVM()

from orekit_jpype.pyhelpers import setup_orekit_curdir  # noqa: E402

DATA_ZIP = Path(sys.argv[1])
setup_orekit_curdir(str(DATA_ZIP))

from org.hipparchus.geometry.euclidean.threed import Vector3D  # noqa: E402
from org.orekit.bodies import CelestialBodyFactory, OneAxisEllipsoid  # noqa: E402
from org.orekit.frames import FramesFactory  # noqa: E402
from org.orekit.orbits import CircularOrbit, PositionAngleType  # noqa: E402
from org.orekit.propagation.analytical import KeplerianPropagator  # noqa: E402
from org.orekit.propagation.events import EclipseDetector, EventsLogger  # noqa: E402
from org.orekit.propagation.events.handlers import ContinueOnEvent  # noqa: E402
from org.orekit.time import AbsoluteDate, TimeScalesFactory  # noqa: E402
from org.orekit.utils import Constants, IERSConventions  # noqa: E402

R_EQ_M = 6378137.0
UTC = TimeScalesFactory.getUTC()
GCRF = FramesFactory.getGCRF()
ITRF = FramesFactory.getITRF(IERSConventions.IERS_2010, False)
SUN = CelestialBodyFactory.getSun()
MU = Constants.WGS84_EARTH_MU


def _date(iso: str) -> AbsoluteDate:
    return AbsoluteDate(iso.replace("Z", ""), UTC)


def itrs_to_gcrs(epoch_utc: str, r_km: tuple[float, float, float]) -> list[float]:
    t = ITRF.getTransformTo(GCRF, _date(epoch_utc))
    p = t.transformPosition(Vector3D(r_km[0] * 1e3, r_km[1] * 1e3, r_km[2] * 1e3))
    return [p.getX() / 1e3, p.getY() / 1e3, p.getZ() / 1e3]


def _orbit(epoch_utc: str, altitude_km: float, inc_deg: float, raan_deg: float) -> CircularOrbit:
    a = R_EQ_M + altitude_km * 1e3
    return CircularOrbit(
        a,
        0.0,
        0.0,
        math.radians(inc_deg),
        math.radians(raan_deg),
        0.0,
        PositionAngleType.TRUE,
        GCRF,
        _date(epoch_utc),
        MU,
    )


def beta_deg(epoch_utc: str, inc_deg: float, raan_deg: float) -> float:
    orbit = _orbit(epoch_utc, 500.0, inc_deg, raan_deg)
    pv = orbit.getPVCoordinates()
    n = Vector3D.crossProduct(pv.getPosition(), pv.getVelocity()).normalize()
    s = SUN.getPVCoordinates(orbit.getDate(), GCRF).getPosition().normalize()
    return math.degrees(math.asin(Vector3D.dotProduct(n, s)))


def sun_distance_au(epoch_utc: str) -> float:
    d = SUN.getPVCoordinates(_date(epoch_utc), GCRF).getPosition().getNorm()
    return d / Constants.IAU_2012_ASTRONOMICAL_UNIT


def eclipse_minutes(
    epoch_utc: str, altitude_km: float, inc_deg: float, raan_deg: float, penumbra: bool
) -> float:
    """Duration of the first full shadow passage within two revolutions (two-body propagation)."""
    orbit = _orbit(epoch_utc, altitude_km, inc_deg, raan_deg)
    earth = OneAxisEllipsoid(R_EQ_M, 0.0, ITRF)
    detector = EclipseDetector(SUN, Constants.SUN_RADIUS, earth)
    detector = detector.withPenumbra() if penumbra else detector.withUmbra()
    detector = detector.withThreshold(1.0e-4).withHandler(ContinueOnEvent())
    logger = EventsLogger()
    prop = KeplerianPropagator(orbit)
    prop.addEventDetector(logger.monitorDetector(detector))
    prop.propagate(orbit.getDate().shiftedBy(2.0 * orbit.getKeplerianPeriod()))
    events = list(logger.getLoggedEvents())
    entry = next(e for e in events if not e.isIncreasing())  # g decreasing: entering shadow
    exit_ = next(
        e for e in events if e.isIncreasing() and e.getDate().durationFrom(entry.getDate()) > 0
    )
    return exit_.getDate().durationFrom(entry.getDate()) / 60.0


ECLIPSE_EPOCH = "2025-06-21T00:00:00Z"
ORBITS = {
    # name: (altitude_km, inclination_deg, raan_deg in GCRF)
    "aqua-like-705": (705.3, 98.2, 150.0),
    "iss-415": (415.0, 51.6, 90.0),  # RAAN 90: beta is sensitive to RAAN sign/frame errors here
}
FRAME_EPOCH = "2004-04-06T07:51:28.386009Z"
FRAME_POINT_KM = (-1033.4793830, 7901.2952754, 6380.3565958)

out: dict[str, object] = {
    "versions": {
        "orekit-jpype": md.version("orekit-jpype"),
        "orekit": "Orekit Java library bundled with orekit-jpype (same major.minor.patch)",
        "orekit_data_zip": DATA_ZIP.name,
        "orekit_data_sha256": hashlib.sha256(DATA_ZIP.read_bytes()).hexdigest(),
    },
    "constants": {
        "earth_mu_m3_s2": MU,
        "earth_radius_eclipse_m": R_EQ_M,
        "sun_radius_m": Constants.SUN_RADIUS,
        "astronomical_unit_m": Constants.IAU_2012_ASTRONOMICAL_UNIT,
    },
    "eclipse_epoch_utc": ECLIPSE_EPOCH,
    "sun_distance_au": sun_distance_au(ECLIPSE_EPOCH),
    "orbits": {},
    "frames": {
        "epoch_utc": FRAME_EPOCH,
        "itrf_km": FRAME_POINT_KM,
        "gcrf_km": itrs_to_gcrs(FRAME_EPOCH, FRAME_POINT_KM),
        "conventions": "IERS 2010, EOP from orekit-data (simpleEOP=False)",
    },
}
for name, (h, inc, raan) in ORBITS.items():
    out["orbits"][name] = {  # type: ignore[index]
        "altitude_km": h,
        "inclination_deg": inc,
        "raan_deg": raan,
        "beta_deg": beta_deg(ECLIPSE_EPOCH, inc, raan),
        "umbra_min": eclipse_minutes(ECLIPSE_EPOCH, h, inc, raan, penumbra=False),
        "penumbra_min": eclipse_minutes(ECLIPSE_EPOCH, h, inc, raan, penumbra=True),
    }
print(json.dumps(out, indent=2))
