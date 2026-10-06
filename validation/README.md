# Validation cases

Each case compares one orbitlife output with a trusted reference. Cases are written **before** the code they check (Phase 1), so they start as `NOT_IMPLEMENTED`.

There are two kinds of check:
- **`implementation`**: same model as a reference code (SPENVIS, CREME96, Orekit/GMAT, a textbook table). Agreement shows our code is right, not that the physics is.
- **`physics`**: against measured flight or ground data (e.g. Shields-1 measured dose, the Feb 2022 Starlink drag report). Agreement shows the physics is right.

## Case format

One YAML file per case, in `validation/cases/<module>/<id>.yaml`. Fields:

```yaml
id: orbit-sso-inclination-600km        # lowercase, digits, hyphens; unique
title: Sun-synchronous inclination at 600 km
module: orbit                           # orbit | drag | thermal | radiation | see | sel | forecast | workload | fleet
check: implementation                   # implementation | physics
target: orbitlife.orbit.sso_inclination_deg   # function that must reproduce the reference
inputs:                                 # keyword arguments passed to target
  altitude_km: 600
quantity: inclination
unit: deg
reference:
  value: 97.79
  uncertainty: 0.01                     # optional, same unit
  source: vallado2013                   # must be a key in docs/refs.bib
  locator: "Table 9-3"                  # table, figure, section or page
  status: CONFIRMED                     # CONFIRMED | CORRECTED | UNVERIFIED (from researcher)
  computed_with: null                   # tool and version, if the reference was computed rather than published
tolerance:
  kind: abs                             # abs | rel | factor
  value: 0.01                           # factor tolerances must be > 1 (2 means within ×2 either way)
  rationale: "Table rounds to 0.01 deg"   # required: why this margin is fair (it is an assumption)
expected:                               # optional: only for a documented, explained miss
  kind: documented_miss
  reason: "why the miss is expected, with sources"
notes: optional free text
```

The loader rejects a case if any of these is true:
- a field is missing
- the source isn't in `docs/refs.bib`
- the id is duplicated
- the tolerance rationale is empty

## Outcomes

| Outcome | Meaning |
|---|---|
| `PASS` | Within tolerance of a CONFIRMED reference |
| `PASS_UNVERIFIED_REF` | Within tolerance, but the reference is UNVERIFIED, so it is not evidence |
| `FAIL` | The target exists and is outside tolerance |
| `KNOWN_MISS` | Outside tolerance, as documented in the case's `expected` block (never counted as a pass; CI stays green; the residual is still reported) |
| `NOT_IMPLEMENTED` | The target function doesn't exist yet |
| `ERROR` | The target raised an exception |

## Running

```bash
just validate            # fails on FAIL or ERROR
just validate --strict   # also fails on NOT_IMPLEMENTED and PASS_UNVERIFIED_REF (required at the Phase 2 exit)
```

Results are written to `validation/last-run.json`, which is git-ignored. CI runs the suite nightly and on pull requests that touch validation, the bibliography or Python code.
