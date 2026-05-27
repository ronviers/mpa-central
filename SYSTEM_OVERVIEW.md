# MPA Suite — system overview

**Evolving document.** What MPA actually is, how the pieces communicate, and
how data flows from substrate physics to auditor verdict. For people who want
to understand the system as a whole before reading any individual repo.

Last refreshed 2026-05-22 (§2 + §2b at v0.4 / 5-vector). The §4–5
confidence-apparatus prose still describes the v0.3 audit_delta shape and is
the next refresh.

---

## 1. The suite at a glance

The MPA suite is a substrate-agnostic framework for characterizing complex
systems through the lens of generalized Fluctuation-Dissipation (gFDR)
relations. It runs across several repos, each with one job:

| Repo | Role |
|---|---|
| **[mpa-central](https://github.com/ronviers/mpa-central)** | Framework rules + substrate library (grind cells) + this overview. Authoritative `RULES.md`, `METHODOLOGY.md`, `SUITE_BLOCK_IN.md`. |
| **[mpa-atlas](https://github.com/ronviers/mpa-atlas)** | RFC specifications + schemas + cdv1 (canonical-dimension v1) framework prose. Thin-RFC discipline: half a page per object. |
| **[mpa-solver](https://github.com/ronviers/mpa-solver)** | Forward substrate physics. Takes operating points, produces observation rows (τ, C, χ). |
| **[mpa-scale-solver](https://github.com/ronviers/mpa-scale-solver)** | Canonical-space runtime. Rust-canonical. `apply_translation`, `regime_at`, `gamut_classify`, `forward_sweep_invert`, `flow`, `intent_map`. |
| **[mpa-lens-solver](https://github.com/ronviers/mpa-lens-solver)** | Fits per-substrate-class `TranslationField` instances from observations + cdv1 priors. The substrate's "ICC profile". |
| **[mpa-conform](https://github.com/ronviers/mpa-conform)** | Compute hub. Curator path (library → declaration bundles), researcher path (uploads → declaration bundles), shot renderer, character tests, sweep harness. Agentic by design. |
| **[mpa-auditor](https://github.com/ronviers/mpa-auditor)** | Pure-static browser app. Reads signed declaration bundles + driver profiles, renders audit verdicts. No LLM at runtime, no network after download. |

Architectural authority for the compute/viewer split:
[`H:/mpa-central/SUITE_BLOCK_IN.md`](SUITE_BLOCK_IN.md). For the three
solvers: [`H:/mpa-conform/docs/SOLVERS_BLOCK_IN.md`](../mpa-conform/docs/SOLVERS_BLOCK_IN.md).

---

## 2. Data flow

End-to-end, what happens when a substrate is characterized and a verdict
ends up in the auditor:

```
1. substrate physics   (mpa-solver / in-library self-simulators)
   forward simulation per operating point
   --> multi-window FDR rows (tau, C, chi) over a tau_obs fan, anchored to tau_env
        |
        v
2. library packaging   (mpa-central/library/grind_library.py)
   observations packaged as cells; each row carries C_mean/chi_mean + C_sem/chi_sem (grain)
   --> H:/mpa-central/library/data/<substrate>/<cell>.json
        |
        v
3. canonical-coordinate fitting   (two independent paths, one shape)
   a. lens-solver fit_translation_field (batched)  --> chit   (TranslationField = ICC profile)
   b. conform/inversion.invert (two-stage)         --> chit, gamma_AB + FitDiagnostics
   NOTE: gamma_AB is unobservable from a single-mode locus (RFC-S App.B) -> carried unconstrained
        |
        v
3b. substrate-thermodynamic refinement -- THE 5-VECTOR (the fingerprint)
   [invert(): live 2026-05-22 | bundle persistence: owed, v0.5]
   conform/inversion fits KWW+FDT (q_EA, tau_alpha, beta_KWW, tau_beta, X) on
   dimensionless lag (raw native lag / logged tau_scale -- guarded), per-channel S/N gate
   --> X + 5-vector + IN/OUT verdict ("could Banach adapt to this data?")
   surfaced by cmd_invert; curator (walk_library) persistence + schema field still owed
        |
        v
4. confidence apparatus
   conform/calibration: per-substrate baseline percentiles; cross-path agreement
   |chit_two_stage - chit_lens|; + per-channel noise-floor gate (residual vs grain)
        |
        v
5. declaration bundle   (curator path, declaration-bundle.v0.4)
   conform/curator/walk_library.py assembles v0.4:
   tau = framework lag (= sample.dt); display_tau = community plot axis;
   observable.data carries C/chi + C_sem/chi_sem; fit_provenance: (chit, gamma_AB),
   predicted locus, per-row residuals, regime, in_gamut, diagnostics, cross-path.
   (the 5-vector from 3b is NOT yet persisted here -- owed with the v0.5 bump)
   --> mpa-conform/output/seed-corpus/<class>/<cell>.bundle.json
        |
        v
6. PR into auditor's seed-corpus   (file-import boundary)
   bundles + driver profiles land at mpa-auditor/seed-corpus/ via PR.
   The ONLY place mpa-conform writes into another repo.
        |
        v
7. auditor reads, renders verdict
   mpa-auditor (pure-static browser app, offline after download): applies driver
   profile, computes verdict, badges via percentiles + cross-path agreement.
   (still ingests CSV today; v0.4 bundle ingestion pending)
```

**Key property:** the boundary between conform (compute) and auditor (viewer)
is the *whole* coupling. No callbacks, no live links, no inference of one
repo's runtime from the other's. Conform writes the bundle; auditor reads
the bundle. Bundle schema (`declaration-bundle.v0.4.json` today) is the
contract.

---

## 2b. The full characterization → comparison flow (definitive, 2026-05-22)

§2 above is the **audit branch** (substrate → bundle → auditor verdict) and is
written at v0.3 — it predates the 5-vector refinement, the v0.4 lag/display
split, and the camera-placement reframe. This section is the **render/compare
branch** (substrate → Banach overlay), and it carries those newer pieces. Both
branches share steps 1–4; they fork after canonical translation. Status tags:
**[live]** implemented and exercised; **[partial]** exists but not wired
end-to-end; **[open]** designed, not yet solved.

> **Load-bearing principle — the substrate is never touched.** "Conform" means
> we conform the **Banach analytical reference *to* the substrate's pristine
> data**, not the reverse. The substrate's empirical (τ, C, χ) sits in the bundle
> unchanged (native frame); everything we fit, scale, place, or clamp is **Banach**
> — which is regenerable from a closed form, so "corrupting" it is meaningless.
> `tau_scale` is logged reversible metadata, not a data edit (native ÷ scale
> reproduces the fit bit-for-bit). Intents (RFC-S §3) clamp *canonical* states for
> gamut-mapping and are **not** used for viewing; the viewport's job is
> non-destructive **view transforms** (e.g. X-faithful) that shape *how Banach is
> shown beside the data*. Whenever the operand seems to be the substrate, stop —
> it's Banach.

1. **Substrate, native state** **[live]** — the system in its own environment,
   intrinsic time, intrinsic τ_env. Bacterial colony, surface code, glass.

2. **Observation & extraction (mpa-solver / grinder)** **[live]** — forward
   physics extracts two intertwined curves, C(τ) (autocorrelation) and χ(τ)
   (integrated response), across a fan of observer windows (τ_obs) anchored to
   the substrate's relaxation timescale τ_env. In-library primitives self-
   simulate; `grind_library.py` packages.

3. **Library indexing (mpa-central)** **[live]** — crystallized into immutable
   triples keyed by (substrate, operating-point, ẋ-choice).

4. **Canonical translation — the prism / ICC profile** **[live]** — native data
   mapped to canonical (chit, γ_AB). Two independent routes both produce it: the
   lens-solver `TranslationField` (the ICC profile) and `conform/inversion`.
   chit is **fit**, not looked up — a substrate-specific leading-order rule seeds
   it (glass chit=Tc−T, surface code chit=ln(p_threshold/p_base)) and the
   inversion refines it. **γ_AB is structurally unobservable from a single-mode
   gFDR locus (RFC-S App. B item 4)** — carried unconstrained unless the
   substrate supplies a phase-locking observable r.

5. **Substrate-thermodynamic refinement — the 5-vector (the fingerprint)**
   **[live, 2026-05-22]** — beyond the leading-order (chit, γ_AB),
   `conform/inversion.invert` fits the KWW+FDT 5-vector (q_EA, τ_α, β_KWW, τ_β,
   **X**) with a per-channel signal-to-noise gate. This is the substrate's
   *fingerprint*, quantified — the deviation from the universal form that RULES
   §15 names as the API surface. The gate answers one question: **could the
   Banach substrate adapt to this data?** (residual within each channel's noise
   grain → IN; the model can't focus → OUT). Inputs must be fed at dimensionless
   lag (raw native lag ÷ logged tau_scale), or the fit silently corrupts —
   guarded in `invert()`.

5b. **Identifiability — per-parameter confidence (the errors we keep)** **[live,
   2026-05-22]** — ORTHOGONAL to the gate. The domain gate asks "is this in the
   KWW-FDT family?"; identifiability asks "is each parameter actually *pinned* by
   the data?" Computed by parametric bootstrap (perturb the data within its grain,
   refit, measure per-parameter spread): bounded params (q_EA, β, X) gated on
   absolute std, timescales (τ_α, τ_β) on coefficient of variation, plus a
   bound-railing check. A fit can be IN-family with **X pinned but the timescales
   mush** — goodness-of-fit ≠ identifiability. **Read protocol:** trust parameter
   *p* iff `in_domain ∧ assessable ∧ identified[p]`. Validated against the
   breakage map (X most robust; τ_β the soft direction). Cells with no grain
   (zero-filled brain/sir) come back **not assessable** — the honest verdict that
   closes the degenerate-IN census hole. Surfaced by `cmd_invert`; rides on the
   `Identifiability` record. *X-faithful etc. are the eventual view-transforms that
   read this record to foreground the pinned signature and grey the mush.*

6. **Scale management — the camera (conform owns this, via mpa-scale-solver)** —
   *cadence matching* via the closed-form contraction operator (Cν /
   Asymptotic-Closure) **[live]**; *camera framing*, setting tau_scale so τ_obs
   tracks the substrate's intrinsic time and frames the s→r migration interior.
   The **mechanism is proven scale-invariant** **[live]** — stretching an
   in-family substrate's relaxation from native to 30 Myr (×10¹³ absolute time,
   tau_scale tracking) recovers a byte-identical 5-vector; the camera absorbs
   absolute timescale. What's **open** is conform *auto-deriving* tau_scale + the
   window when a substrate doesn't declare a clean intrinsic time — placed for
   glass; not yet placed by us for brain (τ_obs→0 floor) and QEC (τ_obs→∞). This
   is conform's work, not an external dependency. Camera-tracking is necessary
   but not sufficient: `voter`/`driven_ring` track the migration yet gate OUT.

7. **Analytical calibration — the Banach reference** **[live]** — closed-form
   calibration zero, chit(ν)=chit₀·exp(−ν), ν=τ_obs/τ_scale. Pure RG flow, no
   exotic substrate behavior; the ruler the substrate is read against.

8. **Trajectory rendering (Mode B) & comparative overlay** — 2D parametric
   overlay (empirical vs Banach in the ΔC–T·χ plane) via
   `conform/compare/banach_overlay` **[live]**; 3D volumetric particle field
   (axes γ_AB, log₁₀ν, chit; regime color blue→cyan→green→orange→red) and the
   paired empirical-vs-Banach Mode B render **[partial]** — shots exist, the
   bundle→trajectory-render wiring is hand-driven. The **visual divergence is the
   fingerprint of step 5 made visible**: where the substrate's trajectory pulls
   away from the smooth Banach reference is exactly where the 5-vector/X lives.

## 3. mpa-lens-solver in detail

### What it does

Takes substrate library cells (operating points + observation rows) and
produces a `mpa_scale_solver.TranslationField` — a lookup table mapping
substrate-native operating points to canonical (chit, γ_AB, k_frust)
coordinates. The framework reads canonical; the substrate speaks native;
lens-solver is the bridge.

The optical-lens metaphor is load-bearing: a substrate has its own physics,
the framework has its own coordinates, and a *lens* — in the camera sense —
is the per-instrument calibration that bridges them. Chromatic aberration
correction maps directly: same camera (`τ_obs` per RFC-S §0.2), different
lenses per substrate, the framework speaks the same words regardless of
whether the substrate is glassy magnetism, bacterial colony dynamics, or a
surface-code quantum memory.

### Public surface

One function: `mpa_lens_solver.fit_translation_field(substrate, cells,
xdot_kind, *, max_passes, tolerance, n_candidates, rng_seed, guard_regime,
min_delta, k_step, trail_window, bootstrap, bootstrap_seed_range)`.

- `max_passes=0` → pure cdv1 prior, no scoring, no observation read.
- `max_passes>0` → predictor-corrector hill climb on chit (γ_AB is
  unobservable from the single-mode gFDR locus per RFC-S Appendix B item 4),
  under two stacked guards:
  - **Regime-band guard**: candidates whose `vertex_regime` differs from the
    seed's are rejected. Catches gfdr-score-attractor crossings.
  - **Predictor-corrector bracket**: candidates outside the trajectory's
    extrapolated bracket are rejected. Bracket width is adaptive: wide where
    the trajectory migrates aggressively (QEC), tight where it moves in
    small steps (glass).
- `bootstrap=None` (default; landed 2026-05-18) → dispatches per substrate:
  known substrates (`_PRIOR_DISPATCH`: glass / quantum / brain) use the
  cdv1 prior; unknown substrates fall through to bootstrap. Explicit
  `True`/`False` overrides. **A fourth substrate now arrives with zero
  code change here or downstream** — the dispatch + bootstrap fallback +
  per-substrate baseline auto-populate (§5) handle it.
- `bootstrap=True` (explicit) → cdv1 prior masked, initial chit drawn
  uniform-random within `bootstrap_seed_range`. The predictor then reads
  refined-chit history (no prior trajectory exists). Used to exercise the
  prior-less path on substrates whose prior IS available (calibration; the
  prior'd run provides ground truth) and as the auto-engaged path for
  substrates without a registered prior.
- `bootstrap_seed_range=None` (default; landed 2026-05-18) → per-substrate
  dispatch from `_BOOTSTRAP_SEED_RANGE_DISPATCH` padded ~25% beyond each
  known substrate's prior envelope (glass `(-1.0, 1.2)`, quantum
  `(-2.5, 5.5)`, brain `(-1.0, 1.0)`). Unknown substrates fall back to
  `(-2.0, 2.0)`. Explicit tuple overrides.

### cdv1 character framing

How the three cdv1-foundational substrates' character flows through
lens-solver (priors as leading-order universality forms; regime guard
as the c/s/r ontology in code; adaptive bracket as substrate-class
character speaking back through the apparatus; refinement-against-data
as measurement of substrate-thermodynamic deviation from leading-order)
is documented at
[mpa-lens-solver/docs/CHARACTER_FRAMING.md](https://github.com/ronviers/mpa-lens-solver/blob/main/docs/CHARACTER_FRAMING.md).
Required reading before reasoning about the score function,
TranslationField shape, observable conventions, or new-substrate
onboarding. Cited from lens-solver's CLAUDE.md as gate on those
decisions.

### Upstream (reads from)

| Repo | What |
|---|---|
| [mpa-central/library](https://github.com/ronviers/mpa-central) | Substrate cells (`H:/mpa-central/library/data/{glass,quantum,brain}/*.json`). Read-only. |
| [mpa-scale-solver](https://github.com/ronviers/mpa-scale-solver) | Output types (`TranslationField`, `TranslationRule`, `OperatingPoint`, `CanonicalPoint`), score function (`gfdr_model.locus_residual`). |
| [mpa-atlas](https://github.com/ronviers/mpa-atlas) | RFC-S §4 (driver-profile vocabulary), cdv1 (chit conventions per substrate; resolved Q-glass-chit-sign). |

### Downstream (writes to)

Nothing. lens-solver's *output* is consumed by mpa-conform; it does not
write to other repos. `fit_translation_field` returns a frozen dataclass;
mpa-conform's shot rendering and curator path read it.

### Confidence quantities (v1.2)

Every cell's `canonical.extras` carries a `fit_diagnostics` dict:

| Field | Meaning |
|---|---|
| `residual_final` | Raw final residual; lower = better fit. Natural path scale. |
| `regime_confidence` | `1 − (off-regime candidate fraction)`. Range `[0, 1]`. High = score pinned. |
| `predictor_gap` | `\|fit_chit − predicted_chit\|` in chit units. `None` when predictor inactive. |
| `source` | `"lens_solver_prior"` or `"lens_solver_bootstrap"`. |
| `n_passes` | Refinement passes used. |

**Raw signals only.** No thresholds. Calibration apparatus lives downstream
in mpa-conform — see §5 below.

---

## 4. The conform/inversion → auditor pipeline

### Curator path (live; the only path today)

`conformer/curator/walk_library.py::run()`:

1. Group all 60 library cells by substrate (glass, quantum, brain).
2. **Per substrate batch**: compute cross-path disagreements. Two
   independent paths fit each cell:
   - `conformer.compute.inversion.invert` — two-stage analytical grid +
     ensemble refine per cell.
   - `mpa_lens_solver.fit_translation_field` — batched call with the
     substrate's full trajectory (predictor active).
   
   Per cell: `|chit_two_stage − chit_lens_solver|` in chit units.

3. **Per cell**: build a `declaration-bundle.v0.3` carrying:
   - Native (τ, C, χ) observation rows (unchanged).
   - The two-stage fit's `(chit, γ_AB)`.
   - Predicted locus at the fitted chit (analytical generation).
   - Per-row residuals (empirical vs predicted).
   - Regime label + in-gamut check from `mpa_scale_solver`.
   - **v0.3 audit_delta extensions**:
     - `fit_diagnostics`: raw FitDiagnostics from the two-stage fit.
     - `diagnostic_percentiles`: where this fit's diagnostic values sit in
       this substrate's known-good distribution.
     - `cross_path_disagreement`: the per-cell value from step 2.
   - Provenance trail (citation, license, version_context).
   - SHA-256 manifest hash + signature stub.

4. Per substrate, build a driver profile from the leading-order canonical
   seeds across cells (the profile is built from priors, not refined fits;
   refined fits feed `audit_delta`, not the profile's lookup table).

5. Write bundles to `mpa-conform/output/seed-corpus/<class>/`. (Gitignored;
   the repo's job is the pipeline + schema, not the data.)

### Researcher path (scaffolded; lands later)

Will take raw user uploads (CSV, time-series, pre-computed FDR), use an LLM
to elicit declarations + identify substrate class, run the same fit
pipeline, produce signed bundles in the `tier="user"` flavor with validation
status fences. The schema doesn't change — only the producer.

### File-import boundary to mpa-auditor

mpa-conform writes bundles + driver profiles to its local `output/seed-
corpus/`. A separate (currently human-driven) PR step copies these into
`mpa-auditor/seed-corpus/`. That is the *only* place mpa-conform writes
into another repo, by design.

mpa-auditor reads them as static assets at build time. No live link, no
inference of conform's runtime, no API calls. The bundle schema
(`declaration-bundle.v0.3.json`, also at
`mpa-conform/schema/`) is the *whole* coupling.

### What the auditor does

Reads bundle, applies the substrate-class's driver profile to convert
operating point → canonical state, computes audit verdict against the
declared canonical trail. For each fit, badges based on:
- `diagnostic_percentiles` (substrate-relative position, e.g. p90 = yellow,
  p99 = red), and
- `cross_path_disagreement` (chit-unit distance; a single user-tunable
  threshold like 0.3 chit units).

Renders the verdict in a pure-static browser app. No LLM at runtime, no
network after the initial download.

---

## 5. Confidence quantities — calibration-free by construction (v0.3)

### Why this exists in this shape

Five iterations on per-fit confidence (May 2026) all failed in the same
structural way: the lens-solver's robustness mechanisms (regime guard,
predictor bracket, grid search, random-perturbation refinement)
intentionally produce fits that don't expose any single analytical
structure to peg confidence against. The conclusion is in
[`H:/mpa-conform/docs/open_fit_confidence_framing.md`](../mpa-conform/docs/open_fit_confidence_framing.md).

The salvage: split per-fit confidence into three primitives, each
calibration-free in a different way.

### The three signals

**1. Per-substrate baseline percentiles.** Each substrate has a baseline
distribution of `fit_diagnostics` values from known-good fits (clean +
near-clean inputs). A new fit's `residual_final = 0.42` doesn't mean much
in isolation — but "p89 within glass's known-good distribution" or "p3
within quantum's" is interpretable directly.

- **Storage**: `H:/mpa-central/library/baselines/<substrate>.json` per
  (path, field) percentile array.
- **Computation**: `H:/mpa-conform/conformer/calibration/baselines.py`,
  run when the library expands or the solver changes.
- **Lookup**: `H:/mpa-conform/conformer/calibration/percentile.py`,
  `np.interp` over stored percentile array. Returns `None` when no
  baseline exists yet for substrate (new substrate → falls back to raw
  inspection).

**Self-improving property**: new substrate added → sweep runs on its
cells → baseline JSON written → all subsequent fits get percentiles
automatically. No human picks thresholds per substrate.

**2. Cross-path agreement.** The curator already runs two independent
fits per cell (two-stage and lens-solver-prior). `|chit_two_stage −
chit_lens_solver|` in chit units is a calibration-free per-cell signal:
zero means independent paths agreed; large means at least one was wrong.

- **Computation**: `H:/mpa-conform/conformer/calibration/cross_path.py`,
  batched lens-solver call (predictor active across substrate trajectory).

**3. Raw fit_diagnostics.** The three lens-solver / two-stage fields
(`residual_final`, `regime_confidence`, `predictor_gap`) ride along in the
bundle for forensics. Auditor uses percentiles for normal flow; raw
signals when a fit looks pathological and someone wants to see why.

### What the auditor user dials

Two user-tunable thresholds, both global:
- Diagnostic percentile threshold (e.g. p90 = yellow, p99 = red).
- Cross-path disagreement threshold in chit units (e.g. > 0.3 = warn).

**No per-substrate dialing.** The per-substrate baseline absorbs the
substrate-scale differences (quantum's natural `residual_final` p50 ≈ 147
vs glass's ≈ 0.2 becomes invisible to the auditor — both are "p50, normal
for the substrate").

---

## 6. What changes and what doesn't

### Stable (versioned, deliberate bumps only)

- Bundle schema (`declaration-bundle.vX.Y.json`). Current: v0.3 (additive
  over v0.2 with three new audit_delta fields).
- `TranslationField` wire format (frozen dataclasses; JSON via
  `dataclasses.asdict` + `json.dumps`).
- The compute/viewer split: conform writes, auditor reads, nothing in
  between.
- Three-solver split: substrate physics (mpa-solver) → canonical runtime
  (mpa-scale-solver) → ICC profile (mpa-lens-solver).

### Grows continuously

- Substrate library (`mpa-central/library/data/`). Each new substrate
  extends the baseline calibration set automatically.
- Per-substrate baselines (`mpa-central/library/baselines/`). Re-run when
  library expands or the solver changes.
- Auditor verdict templates. Bundle schema is stable; what the auditor
  does with it can evolve without a schema bump.

### Iterates

- The lens-solver itself (refinement algorithm, score function richness).
  Versioned in `mpa-lens-solver/pyproject.toml`; each version's calibration
  baseline is re-runnable.
- Curator and researcher paths. Different shapes (curator: library
  walker; researcher: LLM-driven elicitation), same bundle output.

---

## 7. Per-repo reading order

For a new contributor or reader, in this order:

1. **[mpa-central/SUITE_BLOCK_IN.md](SUITE_BLOCK_IN.md)** — the
   compute/viewer architectural commitment.
2. **[mpa-central/METHODOLOGY.md](METHODOLOGY.md)** — the four cuts
   that govern what counts as MPA testing.
3. **[mpa-conform/docs/SOLVERS_BLOCK_IN.md](../mpa-conform/docs/SOLVERS_BLOCK_IN.md)**
   — the three-solver split.
4. **[mpa-lens-solver/README.md](../mpa-lens-solver/README.md)** — the
   ICC-profile solver in detail.
5. **[mpa-conform/CLAUDE.md](../mpa-conform/CLAUDE.md)** — the compute
   hub's session discipline.
6. **[mpa-atlas/CLAUDE.md](../mpa-atlas/CLAUDE.md)** — the thin-RFC
   discipline (for protocol-shaped artifacts).

This document (`SYSTEM_OVERVIEW.md`) sits above all of those as the
single-page "what is this thing" answer.

**Intellectual orientation** (the Lakatosian framing of the program —
what it claims, what attacks it expects, what ground it gives and
doesn't): [POSITION.md](POSITION.md). Read when you want the stance
on legitimacy or criticism; not required for technical orientation.

---

## Maintenance

This document is intentionally evolving. Refresh when:
- A new repo joins or leaves the suite.
- Bundle schema bumps (v0.3 → v0.4).
- The compute/viewer boundary changes (e.g., researcher path lands and
  changes the curator-only flow).
- A new confidence quantity is added (or one is retired).
- The substrate library expands meaningfully (new class).

Keep the data-flow diagram in §2 honest. If actual data flow diverges from
the diagram, the document — not the system — is wrong.
