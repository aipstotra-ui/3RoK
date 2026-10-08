# ADR 0007: Radiation flux geometry conventions

- Status: Accepted (2026-10-06, Phase 1 extension E4)
- Sources: `docs/research/phase1-radiation.md` ("Flux geometry"). The two SPENVIS equations were viewed directly by the main agent.

## Context
Every SEU, SEL and dose rate multiplies a particle flux by a cross-section or area. The flux can be *omnidirectional* (integrated over all directions, 4π) or *directional* (per steradian), and an isotropic flux crosses a surface according to its geometry. Mixing these up causes three classes of error (physics-reviewer, PR #13 and E4):
- per-sr vs omnidirectional: a factor of 4π ≈ 12.6
- π vs 4π in a rate prefactor: a factor of 4
- one vs both faces of a thin plate: a factor of 2

## Definitions (ECSS-E-ST-10-12C §3.2, `ecss2008st1012c`)
- **Omnidirectional flux** Φ_omni: the scalar integral of the flux over all directions (cm⁻² s⁻¹). It is not the same as an *isotropic* flux.
- **Directional flux** I: per steradian (cm⁻² sr⁻¹ s⁻¹).
- For an **isotropic** environment, Φ_omni = 4π·I.

## Decision
1. **Internal representation.**
   - orbitlife stores and passes **omnidirectional** fluxes, with the unit in the name: `flux_omni_per_cm2_s` (integral) or `diff_flux_omni_per_cm2_s_MeV` (differential).
   - Every omni quantity also carries a **shielding stage** tag (`unshielded` or `behind_<X>_gcm2_al_sphere`), so shielding is never applied twice.
   - A per-sr value is accepted only through an explicit converter, which multiplies by 4π and records the isotropy assumption.
2. **Source conventions, recorded per tool:**
   - **AP8:** omnidirectional over 4π (`cremeMC_omni_trapped_proton`).
   - **CREME96 LET spectra and differential flux files:** per sr (`cremeMC_letspec_help`, `spenvis_creme_seu_help`).
   - **CREME96 TRP output:** unit string "per sr" (`cremeMC_trp_help`). The AP8 → per-sr step is **UNVERIFIED**, so convert explicitly and flag it.
   - **Earth shadow:** for each source, record whether the solid-Earth shadow is already applied. In LEO the Earth blocks about 33% of 4π at 400 km, 31% at 550 km and 27% at 800 km (computed from the half-angle asin(R/(R+h))). Never apply it twice.
   - **TI square-approximation flux** (`ti2023sbok084`): convention **UNKNOWN**. TI's table multiplies a CREME96 integral flux by σ_sat with no 4π or π visible, while CREME96 LET spectra are per sr. The TI cases therefore check bookkeeping only and must not be used to validate geometric factors.
3. **Heavy-ion (RPP) rate.** Use the Adams form as given on the SPENVIS CREME page (`spenvis_creme_seu_help`, equation image verified):

   U = π · A · (X/e) · Q_c · ∫ D[p(L)] · F(L) / L² dL

   - Symbols and units:
     - A is the **total surface area** of the sensitive volume (SV), A = 2(ab + bc + ca) from the RPP dimensions a × b × c. It is **never σ_sat**: σ_sat ≈ ab is one face at normal incidence.
     - X is the energy per electron–hole pair (3.6 eV in Si); e is the elementary charge; Q_c is the critical charge (pC).
     - p is the chord length through the SV (µm), and D(p) is the normalised differential chord-length distribution.
     - L is the LET (MeV·cm²/mg; conversion to deposited charge per µm needs ρ_Si); the lower integration limit is L_min = X·Q_c/(e·p_max).
     - F is the integral LET spectrum **per sr**.
     - (X/e)·Q_c/L² is the Jacobian dp/dL with p = X·Q_c/(e·L), so π·A is the whole geometric prefactor.
   - The RPP depth c (collection or funnel depth) is an `assumption` flag; the rate is very sensitive to it.
   - Because π·A·F = (A/4)·Φ_omni, this is Cauchy's mean-projected-area theorem (`slepian2012averageprojectedarea`): a convex body presents S/4 on average to an isotropic flux.
   - A thin plate counted on both faces gives a·Φ_omni/2 ("the ½"); one exposed face gives a·Φ_omni/4 ("the ¼"). These are the same law applied to different areas, so always state which area is used.
4. **Proton (nuclear-recoil) SEU and SEL rate.** U = ∫ σ(E) · Φ_omni(E) dE, with **no further geometric factor**.
   - SPENVIS writes this as U = 10⁻⁴ · 4π · ∫ f(E) σ(E) dE (equation image verified), with f in m⁻² s⁻¹ sr⁻¹ MeV⁻¹, σ in cm² per bit or per device, and U in s⁻¹ per bit or per device. The 4π converts to omnidirectional; the 10⁻⁴ converts m⁻² to cm⁻².
   - Why no geometric factor: σ is defined per unit beam fluence and assumed independent of direction, so summing σ·I·dΩ over all directions gives σ·Φ_omni.
5. **Square-approximation SEL (TI method).** rate = σ_sat × integral flux above onset, as TI computes it. The flux convention is UNKNOWN (item 2), so this is a bookkeeping check only. It is not used once our own environment path exists.
6. **Mandatory `flags` on every rate result:**
   - (a) isotropic environment assumed
   - (b) σ(E) measured at normal incidence and treated as angle-independent (ECSS-E-HB-10-12A notes σ can vary by almost an order of magnitude with angle; `ecss2010hb1012a`). **Not valid** for low-energy proton direct ionization or multi-node, charge-sharing sensitive volumes in deep-submicron parts (e.g. 4–7 nm accelerators). Those need a dedicated model.
   - (c) AP8 anisotropy ignored, which is acceptable for spinning or randomly oriented spacecraft and questionable for orientation-stabilised ones (`cremeMC_omni_trapped_proton`). The main cause is the east–west asymmetry of trapped protons near the SAA, from proton gyroradius and atmospheric loss. Its size at our orbits is not yet sourced.
   - (d) Earth shadow included or not included, with the source named.
   - (e) spherical-shell shielding equivalent, no sector analysis. Sector analysis would need directional fluxes, attenuated before reduction to omni.

## Consequences
- Phase 2 rate code takes only omnidirectional, shielding-tagged fluxes, so the 4π and π-vs-4π error classes disappear at the API. The area choice (one face, both faces, or the total RPP surface) remains an explicit user input that is always reported.
- Remaining unknowns are tracked in `docs/open-issues.md`:
  - the CREME96 TRP per-sr derivation
  - primary sources (Adams 1983, Tylka 1997, Petersen 2011) are not yet read; their citations come only from the SPENVIS page
  - an angular-dependence model (σ_max(E) per ECSS-E-HB-10-12A) is a later refinement
