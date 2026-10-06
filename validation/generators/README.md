# Reference generators

Scripts that compute validation reference values with **independent** tools, so the numbers can be reproduced exactly. Each generated case records the tool version, the input data version, and this script in its `computed_with`.

## orekit_refs.py (Phase 1 extension E3)
- Computes beta angles, conical umbra/penumbra eclipse durations, and an ITRS→GCRS transform using **Orekit 13.1.9** (via `orekit-jpype`).
- Output: `orekit_refs.out.json`. Cases: `validation/cases/orbit/orbit-beta-*`, `orbit-eclipse-*-{umbra,penumbra}`, and `validation/cases/frames/*`.

To reproduce:
1. Install Java 11 or newer.
2. Download orekit-data commit `2422a7d06ee2cc3b5a503a47271203b0706f3e82` as a zip (sha256 `3f1cdf30…2761e`):
   ```bash
   curl -L -o orekit-data.zip https://gitlab.orekit.org/orekit/orekit-data/-/archive/2422a7d06ee2cc3b5a503a47271203b0706f3e82/orekit-data-2422a7d06ee2cc3b5a503a47271203b0706f3e82.zip
   ```
3. Run:
   ```bash
   JAVA_HOME=/path/to/jdk uv run --no-project --with orekit-jpype==13.1.9.0 python validation/generators/orekit_refs.py orekit-data.zip
   ```

Orekit is not a project dependency; it is used only here to make references.
