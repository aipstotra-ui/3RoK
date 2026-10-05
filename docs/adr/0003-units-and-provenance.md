# ADR 0003: Units and provenance

- Status: Accepted (2026-10-05)

## Context
The hackathon tagged numbers with comment strings ("estimate", "UNVERIFIED"). It even tagged exact constants as estimates, and nothing enforced the tags.

## Decision
- **Inside numerical code:** plain floats and NumPy arrays, with the unit in the name (`altitude_km`, `flux_cm2_s`, `dose_rad_si_per_yr`). This keeps the code fast and readable.
- **At the boundaries** (constants registry, public API results, schemas): a typed `Quantity` with `value`, `unit` (a UCUM-style string), optional `uncertainty`, and `source`. The source records its `kind` (exact | measured | reference_model | fit | assumption | heuristic) and an optional `ref` (a `docs/refs.bib` key).
- Results carry `flags` that list every `heuristic` or `assumption` input that affected them. A test enforces this.

## Consequences
- The docs can generate the assumptions table automatically.
- Contributors must register constants rather than writing literals inline. A lint test looks for unexplained numeric literals in physics modules.
