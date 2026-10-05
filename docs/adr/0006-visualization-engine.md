# ADR 0006: CesiumJS for the 3D globe

- Status: Accepted (2026-10-05)

## Context
The hackathon globe was hand-written three.js. Its trail was never drawn, the spacecraft stood still, the map may have been mirrored east–west, and the spacecraft was a set of boxes.

## Decision
- Use CesiumJS (Apache-2.0), lazy-loaded only on routes that show the globe.
- It provides WGS84 and inertial frames, a time-dynamic clock, terrain and imagery, and CZML.
- Use the offline Natural Earth II imagery that ships with Cesium, so no Cesium Ion token is needed.
- Draw custom layers (radiation flux slices, SAA contour, aurora, SEP cutoff) as Cesium primitives and imagery layers.
- The spacecraft is a glTF model with a recorded license.
- Scenarios export as CZML so they open in Cesium and STK.

## Consequences
- Cesium is large (several MB), so it must stay out of the initial bundle (see the budgets in docs/roadmap.md).
- Globe correctness is checked automatically against Skyfield (sub-satellite point within 1 km).
