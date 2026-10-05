# ADR 0005: Data products live in GitHub Releases with a manifest

- Status: Accepted (2026-10-05)

## Context
The hackathon repo kept about 58 MB of data in git, with no record of when or how each file was produced.

## Decision
- Each data release is a GitHub Release tagged `data-vYYYY.N`. It contains the files and a `manifest.json` recording, for every file, its sha256, size, generator name and version, input hashes, source and license.
- Python fetches data with `pooch`, which checks the hashes. TypeScript checks the hashes after fetching.
- Releases get a Zenodo DOI once the repository is public.
- Data files are never committed (`.gitignore` excludes `*.parquet` and `data-cache/`).

## Consequences
- Results are reproducible: every assessment records the data version and hashes it used.
