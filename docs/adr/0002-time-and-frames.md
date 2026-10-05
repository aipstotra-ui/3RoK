# ADR 0002: astropy for time scales and frames; Skyfield as an independent check

- Status: Accepted (2026-10-05)

## Context
Experts check frames and time scales first. The hackathon code mixed geographic and magnetic latitude, ignored UT1/TT, and had an east–west mirror in the globe.

## Decision
- `orbitlife.time` and `orbitlife.frames` wrap `astropy.time` and `astropy.coordinates` (TEME, GCRS, ITRS, geodetic).
- `sgp4` (the Vallado reference implementation) propagates TLE and OMM data.
- Skyfield is a **test-only** dependency, used as an independent second implementation in validation and globe-correctness checks.
- Every public function names its frame and time scale in its parameter names or docstring.

## Consequences
- astropy is a heavy dependency, but it's standard across the community.
- Hot loops (orbit averaging) use vectorized NumPy on top of a single frame conversion, not per-point astropy calls.
