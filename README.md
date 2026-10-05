# orbitlife

**How long will an AI chip last in orbit, and what will shorten its life?**

`orbitlife` is an open-source toolkit for engineers planning AI compute in low Earth orbit. For a chip on a given orbit it will estimate:

- **radiation damage:** total ionizing dose behind shielding, and single-event upsets from trapped protons, cosmic rays and solar particle events
- **orbital lifetime:** atmospheric drag, including what geomagnetic storms do to it
- **thermal margin:** sunlight, Earth's glow and eclipses
- **workload impact:** silent data corruption and goodput for AI workloads, and fleet-level reliability for a whole constellation
- **storm response:** probabilistic space-weather forecasts and the cheapest action to take when a storm is coming

Every number will carry its source, its uncertainty, and a validation case comparing it with trusted references (SPENVIS, CREME96, NRLMSIS, Orekit, flight data).

## Status

**Phase 0 (foundations), in progress.** No physics has shipped yet. The plan is in [docs/roadmap.md](docs/roadmap.md).

This project grew out of a BigRed//Hacks 2026 entry ([BRHSpaceX](https://github.com/aipstotra-ui/BRHSpaceX)) and is being rebuilt from scratch to a research-grade standard.

## Layout

| Path | What it is |
|---|---|
| `packages/py/orbitlife` | Python library (PyPI): the source of truth for all physics and models |
| `packages/py/orbitlife-build` | Private tools that build data products and train models |
| `packages/ts/core` | `@orbitlife/core` (npm): runs the published data and models in browsers and Node |
| `docs/` | Roadmap, architecture decisions (`docs/adr/`), science notes |
| `validation/` | Reference cases each model must match |

## Development

Requires [uv](https://docs.astral.sh/uv/), [pnpm](https://pnpm.io/), [just](https://just.systems/), Python ≥ 3.11 and Node ≥ 22.

```bash
just setup    # install everything
just verify   # run every check
```

## License

MIT. See [LICENSE](LICENSE).
