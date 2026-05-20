# Pre-registration — Test 1: ξ = τ_obs/τ_env scale-relativity crossover

**Authored:** 2026-05-05, before reading the sweep_G data through the
ξ lens. Reference: [`H:/mpa-central/ONE_TRUE_TEST_ROADMAP.md`](../ONE_TRUE_TEST_ROADMAP.md)
"Test 1 — The ξ = 1 scale-relativity crossover"; v8 §2 scale-relativity;
[`H:/mpa-central/RULES.md`](../RULES.md) rule 7 (substrate-class hierarchy
direction inversion) and rule 12 (broad-τ × late-dt plateau region).

This document fixes the prediction *before* the analysis runs, so any
agreement between data and prediction is honest and any disagreement is
a substrate-class scoping result rather than a tuned-to-fit overclaim.

## What's predicted

Define
- τ_obs — the EMA kernel width of the multi-window FDR primitive
  (mpa-brain `tau_window`; mpc-glass `tau_window`; mpc-quantum `tau_window`).
- τ_env — the substrate's intrinsic relaxation timescale at the current
  operating point. Per-substrate operationalisation in §"Operationalisation".
- ξ ≡ τ_obs / τ_env.

**Claim (Test 1).** Under the snapshot-relative ẋ choice (which
RULES rule 12 has already established as the discriminating coordinate
for the broad-τ × late-dt plateau on all three substrates), the *direction*
in which the regime classifier walks as τ_obs increases reverses sharply
at ξ = 1:

- **ξ < 1** (observer faster than substrate, τ_obs ≲ τ_env). Increasing
  τ_obs at fixed τ_env walks the regime label **c → s → r**.
- **ξ > 1** (observer slower than substrate). Increasing τ_obs walks
  the regime label **r → s → c**.
- **ξ ≈ 1**. The regime label is maximally ambiguous; sign of
  ∂R/∂log(τ_obs) flips here.

R below denotes a scalar regime classifier (operationalised in
§"Regime classifier scalar"). The signed slope ∂R/∂log(τ_obs)
should be a function of ξ alone, with a sign change at ξ = 1, *the
same function across the three substrates after rescaling τ_obs
by τ_env(operating point)*.

## Acceptance criteria

The test is **positive** ("compelling for MPA") if all four of:

1. ∂R/∂log(τ_obs) at fixed operating point has a single sign change
   along the τ_obs axis on each of the three substrates.
2. The sign-change location, expressed as ξ_crossover ≡ τ_obs(crossover)
   / τ_env(operating point), falls in [0.5, 2.0] on all three substrates.
3. The sign-change location is consistent *across operating points
   within a substrate* (within ±50% in ξ, allowing for τ_env
   estimation noise).
4. After rescaling, the four-scenario walks of all three substrates
   collapse onto a substrate-shared curve in (log ξ, R) space — within
   the noise envelope of each substrate's R measurement (visualised as
   error bars or the ±σ_d of the per-window FDR slope).

The test is **negative** ("rule 7 stays as a categorical escape clause")
if any of:

- The slope ∂R/∂log(τ_obs) does not change sign within the τ_obs grid
  on at least one substrate (regime classifier is monotone — the
  hierarchy direction is locked, not ξ-conditional).
- The sign-change location is consistent within a substrate but
  *substrate-specific* and falls well outside [0.5, 2.0] on at least
  one substrate (e.g. ξ_crossover = 100 on quantum).
- The walks do not collapse after rescaling — substrate-specific
  curves with different shapes, even if each individually has a
  ξ ≈ 1 sign change.

The test is **inconclusive** if τ_env cannot be estimated reliably from
the existing data (e.g. the C(t, t_w) decay does not converge cleanly
on a ≤ t_obs window on one or more operating points). In that case the
test is deferred to a follow-up sweep that explicitly measures τ_env
per operating point.

## Operationalisation

### τ_env per substrate

- **Brain (Langevin overdamped).** τ_env(scenario) is the autocorrelation
  decay timescale of the *raw readout* (position x(t), or velocity if
  position is non-stationary) at the substrate's current operating point.
  Operational definition: fit a single-exponential to C(t-t_w) /
  C(0,t_w) over the `all_samples` trajectory and take τ_env as the
  1/e timescale.
- **Glass (3D EA Ising aging).** τ_env(T) is the autocorrelation decay
  timescale of the spin overlap with the post-equilibration snapshot,
  q(t,t_w). Same operational definition: 1/e timescale of C(t-t_w).
  Note critical slowing down near Tc may make this exceed t_obs;
  in that case mark the operating point as "τ_env > t_obs" and treat
  ξ as < 1 across the entire τ_obs grid.
- **Quantum (surface-code syndromes).** τ_env(p) is the inverse
  effective detection rate per stabiliser per round, 1/p_eff. Two
  candidate operationalisations:
  - **Analytic (cheap):** τ_env ≈ 1/p_base. At p_base = 1e-4, 1e-3,
    5e-3, 2e-2 this gives τ_env ∈ {10000, 1000, 200, 50} rounds.
  - **Empirical (consistency check):** 1/e timescale of the syndrome
    C(t-t_w) decay, same as brain and glass.
  If the two disagree by more than 2× on any operating point, prefer
  the empirical.

The unified per-substrate definition is "1/e timescale of the substrate's
*pre-EMA* autocorrelation function C(t-t_w) at the operating point."
Falling back to `last_sample.C` and `all_samples[*].C` is the operational
recipe; `C` here is the substrate-emitted Pearson autocorrelation between
the snapshot reference and the current sample, available in every
multi-window-FDR result on every substrate.

### Regime classifier scalar R

The per-window FDR primitive emits five scalars per (τ_obs, t) cell:
C_d, C_d_diag, chi_d, d_norm, sigma_d, plus the derived `f` ∈ [0, 1]
where f = (C_d_diag - C_d) / C_d_diag is the trail-vector denominator
fraction.

For Test 1 the natural scalar is f itself, read at the late-dt edge
(last `all_samples` entry) for each (operating point, τ_obs) cell.
The roadmap's "regime walk direction" is then sign of df/dlog(τ_obs).

Scenario→regime mapping for the rescaling step:
- f → 0 corresponds to deep c-like (trail has not differentiated from
  zero in snapshot-relative coordinates — see rule 8/12).
- f → 1 corresponds to deep r-like (EMA has decorrelated from snapshot;
  C_d → 0 while C_d_diag stays finite).
- f intermediate (the broad-τ × late-dt plateau) is the s-like
  signature.

So df/dlog(τ_obs) > 0 reads **c → s → r** as τ_obs widens (the
"narrow-τ → c-like" direction of v8 §2's literal prose). Negative
slope reads inverted.

## Direction prediction by substrate

A substrate's literal-default-prediction direction depends on whether
its committed structure lives at fine timescales (then ξ = τ_obs/τ_env
< 1 across the grid means we read narrow → c, the §2 prose direction)
or coarse timescales (rule 7 inversion: ξ > 1 across the grid, narrow →
r-like, broad → c-like).

Pre-registered expectations (rule 7's substrate-class assignment, now
read through ξ):

- **Brain:** committed structure at fine timescales. τ_env ~ 1/well-stiffness
  is short relative to the 3..1000 τ_obs grid for at least the deep-r
  scenario. Expectation: most of the grid sits in ξ > 1, so the walk
  reads inverted (broad-τ → c-like). RULES rule 12 records f spread
  0.005..0.226 with k lowest, c→s→r monotone — consistent with broad-τ
  reading c-like (f near 0) and narrow-τ reading r-like (f → 1) for
  the suspended/reset axis. The *crossover* — where the slope of f vs
  log τ flips sign — is the new prediction.
- **Glass:** committed structure at coarse timescales (aging diagonal).
  Rule 7 records "walks r → s → c as τ widens" — so most of the grid
  sits in ξ > 1 territory (the broad-τ corner reads c-like, f near 0).
  Crossover at ξ = 1 should be reachable in the high-T (paramagnetic)
  scenario where τ_env is short.
- **Quantum:** committed structure at coarse timescales (syndrome
  freeze-out). At deep-r (p_base = 1e-4), τ_env ≈ 1/p_base ~ 10000 ≫
  τ_obs_max = 1000 — entire grid sits in ξ < 1 territory. At
  near-thr (p_base = 0.02), τ_env ~ 50 — most of the grid sits in
  ξ > 1. So the operating-point sweep should *traverse* ξ = 1, with
  the slope of f vs log τ flipping sign as p_base increases.

The cleanest single-substrate evidence of Test 1 should come from
**quantum**, because its operating-point sweep spans 2.6 decades in
τ_env (50 to 10000), covering both sides of ξ = 1 within the same
τ_obs grid. Brain and glass span less; their evidence is the
**cross-substrate collapse** check (criterion 4 above).

## What the analysis does, concretely

1. Read the latest sweep_G JSON on each substrate.
2. For each (substrate, scenario, snapshot-relative ẋ choice):
   a. Extract C(t-t_w) from `all_samples[*].C`.
   b. Fit single-exponential decay; record τ_env(scenario).
   c. For each τ_obs in `tau_windows`, read the late-dt f from
      `last_sample.per_window[τ_obs].f`. Record (τ_obs, f) curve.
3. Compute ξ = τ_obs / τ_env per cell.
4. Plot f vs log(ξ) per substrate, scenario; check for sign change
   in df/dlog(ξ) and its location.
5. Overlay all substrates on the same axes; check for collapse.

Steps 1–4 are the minimum to read the result. Step 5 is the
cross-substrate universality check.

## Scope discipline

This pre-registration covers Test 1 only. It does not commit to:

- Adding Test 1's analysis to the visualizer (visualizer-side work
  is owed independently).
- Substrate-side primitive changes to emit τ_env directly. The roadmap's
  Test 1 implementation cost mentions "possible substrate-side primitive
  update" as a follow-on; the present pre-registration uses only what
  current sweep_G data already exposes.
- The other four tests (engineered k-frust, hysteresis-gap,
  c-s mentor lag, Wall-cusp ν(d)). Each will get its own pre-registration
  if and when it gets picked up.

## Follow-ons regardless of outcome

If positive: rule 7's substrate-class hierarchy-direction-inversion
gets absorbed into rule 12's universality machinery; RULES.md gets
edited to fold rule 7 into rule 12's "the region is universal; the
direction is set by ξ", and rule 7 stays only as the substrate-class
note that classifies which side of ξ = 1 each substrate sits on at its
default operating points.

If negative: rule 7 stays as the categorical escape clause; the
pre-registration is filed as a substrate-class scoping result; the
ξ = 1 crossover is recorded as a *partial* universality (within
substrate, perhaps, but not across the constellation).

If inconclusive: the next sweep_G run on each substrate adds a τ_env
emission step (substrate-side primitive update) and Test 1 is rerun
on the new data.
