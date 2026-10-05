# Validation cases

Each case compares an orbitlife output with a trusted reference, such as SPENVIS, CREME96, Orekit/GMAT, NRLMSIS, Vallado, or flight data.

The cases are written **before** the code they check (Phase 1), so they start out failing.

The format is one YAML file per case. It is defined in Phase 1, and each file records:
- `id`, `quantity`, `unit`
- the `inputs` (orbit, epoch, shielding, device…)
- the `reference` value plus its `source` (a `docs/refs.bib` key)
- the `tolerance` and why that tolerance was chosen

Run them all with `just validate` (added in Phase 1).
