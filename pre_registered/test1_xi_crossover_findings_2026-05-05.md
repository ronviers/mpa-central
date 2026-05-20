# Test 1 first-pass findings (2026-05-05)

**Pre-registration:** [`test1_xi_crossover.md`](test1_xi_crossover.md)

**Status:** Partial. Existing sweep_G data does not suffice to settle
Test 1 in either direction; what it does settle is documented below.

## Summary

The strong form of Test 1 (sharp ξ = 1 sign change in df/d log τ_obs,
on every substrate, with cross-substrate collapse after rescaling)
**is not supported by existing sweep_G data on three substrates** under
analytic τ_env estimates. One suggestive outlier — brain conflict
(gt = k) at ξ ∈ [0.84, 1.5] — sits cleanly at the predicted
crossover and warrants a focused re-analysis with substrate-direct
τ_env. The other 11 of 12 (substrate × scenario) combinations either
show no sign change or show the change at ξ values unrelated to 1.

The first-order falloff applies: under the pre-registration's binary
acceptance criteria, the test reads **negative** — rule 7's
substrate-class hierarchy-direction-inversion is *not* absorbed into
rule 12's universality machinery by the present data. Two large
caveats follow.

## Caveats up front

1. **Analytic τ_env is approximate.** The roadmap's claim that
   τ_env-relevant data is already emitted in sweep_G results does not
   match the actual JSONs — the substrate-emitted `C(t,t_w)` is the
   *trail-vector* autocorrelation, not the raw-readout autocorrelation
   that τ_env requires. So τ_env was operationalised analytically:
   - Quantum: τ_env = 1/p_base ∈ {10000, 1000, 200, 50}.
   - Glass: τ_env(T) = |T-1.1+0.05|^(-6) (zν=6, 3D-EA Tc≈1.1; large for
     T<Tc, finite for T>Tc).
   - Brain: a hand-calibrated table τ_env(scenario) ∈ {committed: 1000,
     suspended: 300, conflict: 500, reset: 50}.
   These estimates are not measured per operating point; they're a
   first-pass placeholder. Glass below Tc gets τ_env ≈ 1e6 (essentially
   ∞ on the t_obs ≤ 10000 budget) and so glass-side ξ values are not
   trustworthy for the cold scenarios.

2. **f might be the wrong regime-walk scalar.** The pre-registration
   used f = (C_d_diag - C_d)/C_d_diag because rule 12 already validates
   the f-plateau in the broad-τ × late-dt corner as scenario-
   discriminating. The v8 hierarchy-direction prediction (§5,
   Appendix E) is stated in terms of the FDR locus shape on the
   parametric (ΔC, χ) plot, *not* in terms of f. f's monotone
   decrease with τ_obs may be a coordinate-asymptote effect (rule 5;
   broad-τ = trail differentiated from snapshot, ratio collapses) that
   doesn't track the underlying regime label. A locus-shape based
   classifier (X = dχ/dΔC) might walk differently.

Both caveats can be removed by substrate-side primitive updates that
emit τ_env-relevant raw autocorrelation alongside the trail observables,
plus an analysis pass that computes the FDR slope X parametrically
across τ_obs. Both are doable; neither is in the present pre-registered
test scope.

## Per-substrate readings

### Quantum (events-since-snap, τ_env = 1/p_base)

| scenario | gt | p_base | τ_env | grid ξ range | f range | df/d log τ | sign change |
|---|---|---|---|---|---|---|---|
| deep-r | r | 1e-4 | 10000 | [3e-4, 0.1] | 0.99 → 0.34 | uniformly negative | none |
| deep-s | s | 1e-3 | 1000 | [0.003, 1.0] | 0.94 → 0.05 | uniformly negative | none |
| smoke | s | 5e-3 | 200 | [0.015, 5.0] | 0.74 → 0.02 | uniformly negative | none |
| near-thr | k | 0.02 | 50 | [0.06, 20] | 0.42 → 0.01 | mostly neg, tiny + uptick | ξ ≈ 8-15 (noise floor) |

**Read:** all four scenarios walk f monotonically downward with log τ.
Even deep-s, whose grid straddles ξ = 1 cleanly, shows no kink.
near-thr's late-τ uptick (slope -0.007 → +0.007) is consistent with a
floor effect: f has decayed to ~0.005-0.01, and noise on the smallest
fs flips the sign of the local derivative.

**No ξ = 1 reversal.** Inverted direction relative to v8 §2 prose
holds (broad-τ → c-like, narrow-τ → r-like) — that's RULES rule 7's
quantum-class assignment — but the direction is monotone, not
ξ-conditional.

### Glass (spin-relative, τ_env from zν=6 power law around Tc=1.1)

| scenario | gt | T | τ_env | grid ξ range | f range | df/d log τ | sign change |
|---|---|---|---|---|---|---|---|
| frozen | c | 0.30 | ~1e6 | [3e-6, 1e-3] | 0.19 → 0.10 → 0.10 | mostly neg, +uptick at τ=1000 | nominal at ξ ~ 3e-4 |
| aging | s | 0.66 | ~1e6 | [3e-6, 1e-3] | 0.30 → 0.25 → 0.27 | mostly neg, +uptick at τ=1000 | nominal at ξ ~ 3e-4 |
| critical | k | 1.00 | ~1e6 | [3e-6, 1e-3] | 0.34 → 0.26 → 0.27 | mostly neg, +uptick at τ=1000 | nominal at ξ ~ 5e-4 |
| paramagnetic | r | 1.50 | 120 | [0.025, 8.3] | 0.40 → 0.18 | uniformly negative | none |

**Read:** all four scenarios walk f down across most of the grid, with
an uptick at τ = 1000 in the three cold scenarios. The uptick lies at
τ_max where t_obs = 10·τ_max is the rule-8 budget edge — could be
kernel-warmup artifact (per RULES rule 8, "a cell at (τ_k, t) with
t < 5τ_k is a warmup artefact"). If real, the upticks are at ξ values
~ 1e-4 (for the cold T's where my analytic τ_env is severely
overestimated), nowhere near ξ = 1.

**Glass-side conclusion is clouded by τ_env overestimation** for cold
T. The high-T paramagnetic scenario is the cleanest reading and shows
no sign change.

### Brain (position-relative, τ_env from hand-calibrated scenario table)

| scenario | gt | h_field | τ_env | grid ξ range | f range | df/d log τ | sign change |
|---|---|---|---|---|---|---|---|
| committed | c | 0.05 | 1000 | [0.003, 1.0] | 0.47 → 0.085 | uniformly negative | none |
| suspended | s | 0.08 | 300 | [0.01, 3.3] | 0.56 → 0.15 | uniformly negative | none |
| conflict | k | 0.03 | 500 | [0.006, 2.0] | 0.15 → 0 → 0.005 | neg then small + at large τ | **ξ ∈ [0.84, 1.5]** |
| reset | r | 0.05 | 50 | [0.06, 20] | 0.56 → 0.23 | uniformly negative | none |

**Read:** committed and suspended walk monotonically. Reset's nominal
sign change at ξ ≈ 0.1 (slope +0.001 → -0.004) is below the noise
floor and not credible.

**Brain conflict (k-regime) is the single suggestive case.** The walk
goes f = 0.15 → 0 → 0.005 across τ ∈ [3, 1000], with the *minimum*
near τ = 175-313 and a small rise after. The detected sign-change
midpoint (ξ ≈ 0.84-1.5) sits cleanly at the predicted ξ = 1 location.

This is interesting on two grounds. First, conflict is the *k-frust*
scenario — RULES rule 12 records its f-plateau as the lowest of the
four scenarios (k = 0.005 in F-002), and v8 §5 / Appendix E records
the k_frust signature as a **transient negative response** at the
cycle scale. The non-monotonicity could be the residual k-frust shape
visible in the kernel-width sweep, not the ξ = 1 crossover Test 1
predicts. Second, brain's hand-calibrated τ_env table is the least
empirically grounded of the three; the ξ ≈ 1 location is set by
choosing τ_env(conflict) = 500 a priori, which is partially circular.

**Disposition:** record the brain conflict outlier as F-004 candidate
in mpa-brain FOOTING (open question), with the test condition that a
substrate-direct τ_env measurement would settle whether the location
is genuinely at ξ = 1.

## Pre-registered acceptance assessment

| criterion | required | observed | passes? |
|---|---|---|---|
| 1. Sign change on each substrate's f vs log τ | yes | quantum no, glass partial (cold-T artifacts), brain partial (1 of 4) | **no** |
| 2. ξ_crossover ∈ [0.5, 2.0] on all three | yes | only brain conflict ~ 1.1; quantum ~ 10; glass cold ~ 1e-4 | **no** |
| 3. Consistent across operating points within a substrate | yes | each substrate's scenarios disagree | **no** |
| 4. Cross-substrate collapse after rescaling | yes | walks have substrate-specific shapes; no collapse evident | **no** |

**Verdict:** under the pre-registered binary criteria, Test 1's strong
form is **not supported**. The default disposition is to keep
RULES rule 7 as the categorical substrate-class hierarchy-direction-
inversion escape clause; **rule 7 is not absorbed into rule 12** by
this analysis.

## What might still be true (and how to test it)

The strong form failed; weaker readings remain plausible and would
need different data or a different scalar:

- **The regime walk happens but f is the wrong scalar.** Test 1 with
  X = dχ/dΔC (the FDR locus slope, the original §5 / Appendix E
  observable) instead of f. Cheap follow-up: re-analyse the same
  sweep_G data, computing X parametrically across τ_obs at fixed late
  dt, and check whether X has a sign change near ξ = 1.
- **The crossover exists but at scales below the τ_obs grid floor.**
  Quantum's deep-r has τ_env = 10000 ≫ τ_obs_max = 1000, so the entire
  grid sits at ξ < 0.1 — we could be reading the entirely-narrow-τ
  branch of the walk and missing the reversal at higher τ. Follow-up:
  extend τ_obs grid up to 10·τ_env on each substrate's deep-r scenario.
- **Substrate-direct τ_env is needed.** Substrate-side primitive
  updates to emit a raw-readout autocorrelation timescale alongside the
  trail-vector C in each multi-window FDR result. ~30 LOC per substrate.
  Once available, re-run the Test 1 analysis with measured τ_env and
  see if the 11-of-12 negative readings consolidate into a real
  ξ-conditional walk.

## Recommended next steps (in order)

1. **Re-analyse with X = chi_d/(C_d_diag - C_d)** instead of f. **Done
   in this session, 2026-05-05.** See "Addendum — X-classifier
   re-analysis" below. Bottom line: also no clean ξ=1 crossover under
   X; multiple substrate-specific complications surface that limit
   what X can settle on existing data.
2. If (1) doesn't resolve, **substrate-side primitive update** to emit
   raw τ_env per operating point. Per RULES rule 9, this lives in each
   substrate's FOOTING as an action item; per the roadmap's "What's
   owed before any test" section, this is the cheap-but-not-free
   piece of infrastructure that unblocks not just Test 1 but any
   future test that needs ξ scaling. **Owed.**
3. If (1) and (2) don't resolve, the binary verdict above stands and
   the program proceeds to **Track B (Test 2 — engineered k-frust)** as
   the next substrate-side test (cheap, narrow, sharp, orthogonal to
   Test 1's analysis work).

## Addendum — X-classifier re-analysis (2026-05-05)

Step 1 of "next steps" was completed in the same session: ran the same
ξ analysis using X = chi_d/(C_d_diag - C_d) (the v8 §5 / App E
parametric FDR slope) instead of f. Three substrate-specific findings:

**Quantum.** X exhibits a *hump* shape (rise then fall) with a single
clear sign change in dX/dlog(τ_obs) per scenario:
- deep-s: peak at τ≈559, ξ≈0.56
- smoke: peak at τ≈98, ξ≈0.49
- near-thr: peak at τ≈17, ξ≈0.34

The peak location *correlates with* but does not lock onto ξ=1 — it
sits at ξ ∈ [0.3, 0.6] across the scenarios where it's measurable.
This is suggestive of a substrate-specific scaling but inconsistent
with the pre-registered ξ=1 prediction. The deep-r scenario shows
X ≈ 13000 with multiple noise-driven sign flips — its denominator
C_d_diag − C_d is ~10⁻³, putting X far outside v8 App E's defined
regime range (App E: "X ≫ 1 near-vertical region is *not* a regime").

**Glass.** All four T-scenarios walk X *monotonically down* from
values O(0.1-1.5) to O(0.001-0.01) with no sign change. The walk is
clean and substrate-T-conditional in slope but no scenario crosses a
regime boundary in X across the τ_obs grid. This is the pattern of
"all τ_obs sit in c-like territory" or "all τ_obs sit in r-like
territory but X is suppressed by the snapshot-relative denominator
inflation." Either way, no Test 1 crossover.

**Brain.** Brain's X is dominated by numerical-zero artifacts. At
conflict τ=175, C_d_diag − C_d ≈ −0.0075 (ratio noise around zero),
making X = -3.38 a denominator-blow-up, not a k-frust signature.
Brain's chi_d is small (O(0.05) at the late dt) and divides into f's
near-zero denominator territory; X is uninformative on brain at the
late-dt grid in the existing sweep.

**Net.** X yields a richer regime-walk picture than f on quantum
(hump shape, peak ξ ∈ [0.3, 0.6]) but does not deliver a ξ=1
crossover on any substrate. The peak ξ ∈ [0.3, 0.6] *could* be an
honest substrate-specific scaling that the pre-registration's [0.5, 2.0]
acceptance window mostly captures (smoke just inside; deep-s and
near-thr at the edge or outside). Promoting this to "supports Test 1"
would require:
- a fourth quantum operating point at p_base ~ 5e-4 to verify the
  peak ξ stays in [0.3, 0.6];
- glass and brain re-runs with substrate-direct τ_env, since the
  analytical τ_env masks the X-walk on those substrates entirely.

The honest reading is: existing data does not falsify a *substrate-
conditional* X-walk peak at sub-unity ξ on quantum, but it does
falsify the strong-form universal ξ=1 sharp reversal originally
pre-registered. Glass and brain show no comparable structure.

## Followups owed regardless

- Record this pre-registered negative as a candidate F-entry in each
  substrate's FOOTING:
  - mpa-brain F-004 (or next): "Test 1 ξ=1 crossover not supported in
    sweep_G_20260504_171021; conflict scenario shows a sign change near
    ξ=1 that may be a residual k-frust signature."
  - mpc-glass F-020 (or next): "Test 1 ξ=1 crossover not supported in
    sweep_g_glass_20260505_081934; cold-T scenarios show τ_max upticks
    consistent with rule-8 warmup edge, not ξ-crossover."
  - mpc-quantum F-020 (or next): "Test 1 ξ=1 crossover not supported in
    sweep_g_quantum_20260505_080643; all four scenarios walk f
    monotonically with no sign change at ξ=1."
- Annotate RULES.md so future agents know rule 7's hierarchy-direction
  -inversion is *not* yet superseded by Test 1's universality machinery.
  Don't promote or change rule 7; just add a footnote crosslink to
  this findings doc.
