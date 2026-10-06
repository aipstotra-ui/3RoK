# ADR 0007: Radiation flux geometry conventions

- Status: Accepted (2026-10-06, Phase 1 extension E4)
- Sources: `docs/research/phase1-radiation.md` ("Flux geometry"). The two SPENVIS equations were viewed directly by the main agent.

## Context
Every SEU, SEL and dose rate multiplies a particle flux by a cross-section or area. The flux can be *omnidirectional* (integrated over all directions, 4π) or *directional* (per steradian), and an isotropic flux crosses a surface according to its geometry. Mixing these up is a factor-of-2-to-4 error (physics-reviewer, PR #13).

## Definitions (ECSS-E-ST-10-12C §3.2, `ecss2008st1012c`)
- **Omnidirectional flux** Φ_omni: the scalar integral of the flux over all directions (cm⁻² s⁻¹). It is not the same as an *isotropic* flux.
- **Directional flux** I: per steradian (cm⁻² sr⁻¹ s⁻¹).
- For an **isotropic** environment, Φ_omni = 4π·I.

## Decision
1. **Internal representation.**
   - orbitlife stores and passes **omnidirectional** fluxes, with the unit in the name (e.g. `flux_omni_cm2_s`).
   - A per-sr value is accepted only through an explicit converter, which multiplies by 4π and records the isotropy assumption.
2. **Source conventions, recorded per tool:**
   - **AP8:** omnidirectional over 4π (`cremeMC_omni_trapped_proton`).
   - **CREME96 LET spectra and differential flux files:** per sr (`cremeMC_letspec_help`, `spenvis_creme_seu_help`).
   - **CREME96 TRP output:** unit string "per sr" (`cremeMC_trp_help`). The AP8 → per-sr step is **UNVERIFIED**, so convert explicitly and flag it.
3. **Heavy-ion (RPP) rate.** Use the Adams form as given on the SPENVIS CREME page (`spenvis_creme_seu_help`, equation image verified):

   U = π · A · (X/e) · Q_c · ∫ D[p(L)] · F(L) / L² dL

   - A is the **total surface area** of the sensitive volume.
   - F is the integral LET spectrum **per sr**.
   - Because π·A·F = (A/4)·Φ_omni, this is Cauchy's mean-projected-area theorem (`slepian2012averageprojectedarea`): a convex body presents S/4 on average to an isotropic flux.
   - A thin plate counted on both faces gives a·Φ_omni/2 ("the ½"); one exposed face gives a·Φ_omni/4 ("the ¼"). These are the same law applied to different areas, so always state which area is used.
4. **Proton (nuclear-recoil) SEU and SEL rate.** U = ∫ σ(E) · Φ_omni(E) dE, with **no further geometric factor**. SPENVIS writes this as U = 10⁻⁴ · 4π · ∫ f(E) σ(E) dE, where f is per sr in m⁻² (equation image verified): 4π converts to omnidirectional, and 10⁻⁴ converts m⁻² to cm⁻².
5. **Square-approximation SEL (TI method).** rate = σ_sat × integral flux above onset, using the flux convention of the source that supplied it (TI SLVK046, geometry folded in). Not used once our own environment path exists, except as a bookkeeping check.
6. **Mandatory `flags` on every rate result:**
   - (a) isotropic environment assumed
   - (b) σ(E) measured at normal incidence and treated as angle-independent (ECSS-E-HB-10-12A notes σ can vary by almost an order of magnitude with angle; `ecss2010hb1012a`)
   - (c) AP8 anisotropy ignored, which is acceptable for spinning or randomly oriented spacecraft and questionable for orientation-stabilised ones (`cremeMC_omni_trapped_proton`)

## Consequences
- Phase 2 rate code takes only omnidirectional fluxes, so the class of factor-4 errors disappears at the API.
- Remaining unknowns are tracked in `docs/open-issues.md`:
  - the CREME96 TRP per-sr derivation
  - primary sources (Adams 1983, Tylka 1997, Petersen 2011) are not yet read; their citations come only from the SPENVIS page
  - an angular-dependence model (σ_max(E) per ECSS-E-HB-10-12A) is a later refinement
