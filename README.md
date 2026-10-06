# orbitlife

**How long will an AI chip last in orbit, and what will shorten its life?**

> **Status: pre-alpha (Phase 0, foundations).** No models have shipped yet. The plan is in [docs/roadmap.md](docs/roadmap.md).

`orbitlife` will be an open-source toolkit for engineers planning AI compute in low Earth orbit. For a satellite and the chips it carries, it will estimate both the satellite's **orbital lifetime** and the chip's **radiation and reliability budget**:

- **radiation effects:**
  - total ionizing dose (TID) behind shielding
  - single-event effects (upsets and multi-bit upsets, which are soft errors) from trapped protons, galactic cosmic rays and solar energetic particles

  Single-event latchup and displacement damage are not yet in scope (see the roadmap).
- **orbital lifetime:** atmospheric drag, including the effect of geomagnetic storms
- **thermal margin:** direct sunlight, Earth albedo and Earth infrared, through eclipse and beta-angle cycles
- **workload impact:** silent data corruption and goodput for AI workloads, and fleet-level reliability for a whole constellation
- **storm response:** Kp and Dst quantile forecasts scored against NOAA SWPC's official forecast, and the lowest expected-cost action under a cost matrix you supply

**How we check it:**
- Every number will carry its source and uncertainty, and every model will have a validation case.
- **Implementation checks** compare against reference codes that use the same models (SPENVIS, CREME96, Orekit/GMAT).
- **Physics checks** compare against flight data where it exists: ISS decay, the Feb 2022 Starlink loss, and on-orbit memory upset rates.
- Values with no public reference are labelled `heuristic`.

This project grew out of a BigRed//Hacks 2026 entry ([BRHSpaceX](https://github.com/aipstotra-ui/BRHSpaceX)). The hackathon code used invented constants and had no reference tests. It is being rebuilt from scratch, with agreement against reference tools and flight data as the acceptance test.

## Layout

| Path | What it is |
|---|---|
| `packages/py/orbitlife` | Python library (to be published on PyPI): the source of truth for all physics and models |
| `packages/py/orbitlife-build` | Unpublished tools that build data products and train models (not released to PyPI) |
| `packages/ts/core` | `@orbitlife/core` (to be published on npm): runs the published data and models in browsers and Node |
| `docs/` | Roadmap, architecture decisions (`docs/adr/`), science notes |
| `validation/` | Reference cases, each with a stated tolerance, that every model is checked against (written in Phase 1) |

## Development

Requires [uv](https://docs.astral.sh/uv/), [pnpm](https://pnpm.io/), [just](https://just.systems/), Python ≥ 3.11 and Node ≥ 22.

```bash
just setup    # install everything
just verify   # run every check
```

## License

MIT. See [LICENSE](LICENSE).
