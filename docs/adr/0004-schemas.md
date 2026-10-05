# ADR 0004: Schemas defined in pydantic, generated for TypeScript

- Status: Accepted (2026-10-05)

## Decision
- Pydantic v2 models in `orbitlife.schema` define every exchanged document: MissionSpec, DeviceSpec, WorkloadSpec, FleetSpec, Assessment, ForecastBundle, CostMatrix and DataManifest. Each document carries `schemaVersion`.
- `orbitlife schema export` writes `schemas/*.json` (JSON Schema). A generator then produces zod schemas and TypeScript types in `packages/ts/core/src/generated/`.
- CI regenerates both and fails if git shows a diff (the schema-drift check).

## Consequences
- The Python and TypeScript types for a document cannot diverge.
- Generated files are committed so readers can see them, and they are never edited by hand.
