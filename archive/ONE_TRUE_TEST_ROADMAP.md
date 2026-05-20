# MPA — Roadmap to a one-true-test

**Status as of 2026-05-05.** Three substrates (brain, glass, quantum)
report concordant evidence at the rule-12 level: snapshot-relative ẋ
shows broad-τ × late-dt plateau scenario discrimination on all three.
This is necessary for MPA, not sufficient. The framework's strongest
remaining open commitments are testable but unmeasured. This document
sketches what a clean invalidate-or-validate looks like.

**Library is the new prerequisite (2026-05-05 update).** The
[`MPA library`](library/) at `H:/mpa-central/library/` characterizes
the multi-window FDR observable across substrates × operating points ×
ẋ choices on τ_env-anchored grids (RULES rule 13). With the library in
place, **Tests 1, 3, 4, 5 below reduce to library queries** rather
than new substrate runs — a substantial change in implementation cost
estimates. Test 1 in particular is now a re-run-against-library
exercise once the τ_env_measured field is populated by substrate-side
emission. Each test below carries its updated cost annotation.

**A first-pass attempt at Test 1 against pre-library data** is recorded
at [`pre_registered/test1_xi_crossover_findings_2026-05-05.md`](pre_registered/test1_xi_crossover_findings_2026-05-05.md).
The strong form (sharp ξ=1 reversal universal across substrates) was
not supported by sweep_G data using analytic τ_env placeholders. The
test is properly redoable against the library once it lands; the
pre-registration discipline (write the prediction first) holds for all
five tests below.

## What "one true test" means

A single coordinated experiment whose outcome determines MPA's status
on a binary axis:

- **Compelling**: the experiment surfaces a sharp prediction MPA makes
  that no neighbouring framework predicts, with universal scaling
  across substrates of different physical content.
- **Invalidated**: the experiment shows the prediction does not hold,
  or holds only with substrate-specific scaling consistent with each
  substrate's own theory and not with MPA's universality claim.

The bar isn't "MPA agrees with each substrate's data" — that bar is
already cleared by the s-regime FDR shape (validated on Langevin and
syndromes; cross-substrate confirmation just landed at rule 12). The
bar is "MPA predicts something new and substrate-agnostic that the
substrates' own theories don't, and the data falls on the predicted
manifold."

## Framework-layer coverage

Each candidate test probes a different layer of v8's structure. A
complete invalidate-or-validate program needs all five layers:

| layer | candidate test | v8 anchor |
|---|---|---|
| scale-relativity | **Test 1** — ξ = τ_obs/τ_env crossover | §2 scale-relativity, rule 7 |
| subgraph topology | **Test 2** — engineered k-frust on syndromes | §5 frustration signature |
| vertex dynamical asymmetry | **Test 3** — hysteresis-gap-as-regime-invariant | §3 trail history-dependence |
| edge / composite | **Test 4** — c–s mentor lag asymmetry | §3.5 composite catalogue |
| meta-ledger flow | **Test 5** — Wall-cusp ν(d) universality | §6 / Appendix G |

Tests are listed in increasing implementation cost. Test 1 is testable
*now* on data we already have; Test 5 is the heaviest but the headline
universality test.

## The five candidate one-true-tests

### Test 1 — The ξ = 1 scale-relativity crossover (lightest, partially data-driven)

**The prediction.** v8 §2 says the same trail reads c / s / r depending
on the observation kernel width τ_obs. Rule 7 currently codifies a
*substrate-class hierarchy direction* — Langevin walks narrow τ → c-
like, broad τ → r-like; glass and quantum walk inverted (F-018). This
test sharpens rule 7 from a categorical substrate-class label into a
quantitative criterion.

Define ξ = τ_obs / τ_env, where τ_env is the substrate's intrinsic
relaxation timescale at its current operating point. The prediction:

- For **ξ < 1** (observer faster than substrate), increasing τ_env
  drives c → s → r.
- For **ξ > 1** (observer slower than substrate), the same increase
  drives r → s → c.
- The reversal at **ξ = 1** is sharp — observer and substrate
  timescales match, and the regime label is maximally ambiguous.

**Why it's the smartest immediate test.** Rule 7 currently says
"hierarchy direction is substrate-class-conditional." That's an escape
clause — it tells us *that* directions differ but not *why*. This
prediction would absorb rule 7's hierarchy-direction inversion into
rule 12's universality machinery: there's one universal walk,
parameterised by ξ, with the direction set by which side of ξ = 1 each
substrate sits on. Universal at the framework level; substrate-
conditional only via the substrate-specific value of τ_env.

**Why it's testable now.** Both glass and quantum sweeps from this
session vary the substrate parameter (T or p) that controls τ_env.
Each operating point already carries an embedded τ_obs sweep (the
11-point τ_window grid). The (τ, dt) tableaux from
[`mpc-glass/docs/results/sweep_g_glass_*`](../mpc-glass/docs/results/)
and
[`mpc-quantum/docs/results/sweep_g_quantum_*`](../mpc-quantum/docs/results/)
contain the data — we just need:

1. Operationalize τ_env per substrate per operating point.
   - Glass: 1/(decorrelation rate of q_initial) at given T;
     measurable from the substrate observable already emitted.
   - Quantum: 1/p_eff (event rate per stabiliser per round); also
     already emitted as `detection_rate_base`.
   - Brain: 1/(autocorrelation decay of velocity / position-relative
     trail) at given scenario.
2. Compute ξ at each (operating-point, τ_obs) cell.
3. Read the τ_obs walk direction (slope of regime classifier output
   vs τ) at each operating point.
4. Verify the direction reverses at ξ ≈ 1 in each substrate's data.

**Acceptance.** Direction of the regime walk (sign of ∂R/∂log(τ_obs))
flips sharply when ξ crosses 1, on each substrate independently. If the
flip is smooth or doesn't align with ξ = 1, MPA's scale-relativity
claim is sharper than data supports — falls back to rule 7's categorical
substrate-class label.

**Implementation cost.** Lightest of the five.

- **Re-analysis of existing sweep_g data** (this session's output) to
  extract τ_env and ξ. Most of the work is shared analysis code.
- **Cross-substrate ξ collapse plot and possible substrate-side primitive update**:
  emit τ_env directly from each `multi_window_fdr_iter` as a sample-time substrate
  observable. Test if the operational definition of τ_env is locked.

Could absorb rule 7 into rule 12.

### Test 2 — Engineered k-frust signature on syndromes (medium cost, narrow but sharp)

**The prediction.** v8 §5 says the k-frust regime (topologically
frustrated subgraph) has a transient *negative* response signature
that uncorrelated noise doesn't produce. F-014 / F-018 already noted
the k-signature does not appear under uncorrelated depolarising noise
(as expected — there's no frustrated cycle on the syndrome graph
under that noise). The test condition: *engineer* a noise model that
generates frustrated cycles on the syndrome graph (via Stim's
`CORRELATED_ERROR` instructions), and check whether the negative-FDR
signature surfaces.

**Why it's a sharp test.** Either the negative response appears under
the engineered correlated noise — vindicating v8's k-frust prediction
on a substrate where the topology can be controlled — or it doesn't,
in which case the k-frust observable is at best detecting frustration
but not predicting it.

**Acceptance.** A `CORRELATED_ERROR` circuit designed to close
frustrated loops on the syndrome graph produces sustained negative
χ_d signal at the cycle scale, with magnitude predicted by v8's
geometric-shear product around the cycle. If no negative signal
appears, the k-frust universality is falsified on syndromes (might
still hold on substrates with native frustration like glass or
random-3-SAT).

**Implementation cost.** Medium-narrow. Substrate-localized:

- **Engineer the correlated-noise circuit.** Stim's `CORRELATED_ERROR`
  syntax is well-documented; designing a correlated error pattern that
  closes frustrated loops on a distance-3 surface code requires care
  but is a single-substrate problem.
- **Run multi-window FDR on the engineered circuit and compare against v8's quantitative prediction.**
  v8 §5's geometric- shear product around the cycle gives the predicted χ_d magnitude;
  this requires a small calculation per circuit.

**Caveat.** Single-substrate, so doesn't establish universality —
just whether the prediction holds on the one substrate where the
engineering is most natural. Less probative than tests 1, 3, 4, or 5
by itself, but cheap enough to do as a stepping stone.

### Test 3 — Hysteresis-gap as regime invariant (medium cost, sharp prediction)

**The prediction.** The (τ, dt) plateau f read forward vs reverse
should differ by a gap whose magnitude correlates with the regime
label invariantly across substrates: gap ≈ 0 for r-regime cells; gap
maximal for s-regime cells; small gap for c-regime cells; chiral
(direction-dependent) gap for k-regime cells.

**Why it's substantial.** The substrate-conditional direction of the
forward plateau (rule-12-confirmed, but messy) is replaced by a
substrate-invariant *dynamical asymmetry* signal. The gap is a direct
probe of metastability, not a static plateau decoration. If the
prediction holds, MPA earns its second universal observable (gap-as-
regime-invariant) on top of the first (region-as-universal).

**Acceptance.** All three substrates show:
- s-scenario (suspended / aging / sub-threshold-syndrome): forward-
  reverse gap large.
- r-scenario (reset / paramagnetic / deep-r): forward-reverse gap ≈ 0.
- c-scenario (committed / frozen / deep-frozen): small gap.
- k-scenario (conflict / critical / near-thr): chiral gap (sign or
  magnitude depends on reverse direction).

If the gap doesn't track regime label across substrates, the dynamical-
asymmetry-as-regime-invariant claim is falsified (rule 7 still holds —
direction is substrate-conditional — but the gap doesn't add new
universality).

**Implementation cost.** Medium. Per-substrate work:

- **Substrate-side `reverse_replay` flag** in `multi_window_fdr_iter`.
  Glass: ~30 LOC (record per-sweep Δs, run EMA forward then reverse).
  Quantum: ~20 LOC (Stim arrays already in memory; reverse-index them).
  Brain: ~50 LOC (record per-step ẋ; replay reversed).

- **Visualizer-side gap panel** (Chunk D.2 in mpa-visualizer handoff).
- **Per-substrate hysteresis sweep and cross-substrate gap-vs-regime-label collapse analysis.**

### Test 4 — c–s mentor lag asymmetry under time-reversal (heavy substrate scaffolding, sharpest quantitative prediction)

**The prediction.** v8 §3.5's c–s mentor composite is asymmetric: the
committed proposition stabilises the suspended one, while the suspended
one *pumps* the committed one. Under time-reversal of the drive
protocol, the pump direction reverses.

In a two-node substrate with engineered cooperative coupling
γ_AB < 0, measure the cross-correlation C_AB(t, t_w). Forward in time:
A (committed) leads B (suspended) with a positive lag. Under
time-reversal of the drive protocol: the lag inverts — B appears to
lead A. The asymmetry quantifies the net information flow, which v8
predicts equals the maintenance cost differential

$$\text{lag}_\text{fwd} - \text{lag}_\text{rev} \;=\; 2 \kappa\bigl(|\lambda_B| - |\lambda_A|\bigr)$$

where κ is the framework's flux-cost constant and λ_A, λ_B are the
single-trail Lyapunov rates from §2.

**Why it's the sharpest deep prediction.** Three commitments:

1. **Sign**: the lag *reverses* under time-reversal. Binary; trivially
   falsifiable if it doesn't.
2. **Magnitude**: the lag asymmetry *equals* a specific function of
   measurable framework parameters. Quantitative; falsifiable to within
   sampling noise.
3. **Edge-level universality**: the same prediction holds on any
   substrate where you can engineer a c–s mentor pair — Langevin
   coupled wells, glass coupled subsystems, neural-culture paired
   electrodes, coupled oscillators. Substrate-class universal at the
   composite layer.

**Why it tests a layer the others don't.** Tests 1–3, 5 all probe
single-trail (vertex), subgraph, or meta-ledger structure. Test 4 is
the only candidate that probes the *pair-action* — the edge / composite
layer of §3.5. v8's composite catalogue has seven rows
(c–c aligned / orthogonal / opposed; c–s; s–s; frustrated-cycle;
oscillatory–c) and none have been measured yet. The c–s mentor row is
the one with a sharp quantitative prediction tied to substrate-
measurable framework parameters.

**Acceptance.**

- Forward / reverse cross-correlation lag *signs* differ across the
  four-scenario rig (or its analog) on at least two substrates.
- Magnitudes of (lag_fwd − lag_rev) match 2κ(|λ_B| − |λ_A|) within
  ±20% across operating points and substrates.
- If the magnitudes match within ±5% across substrates of different
  microphysics, MPA earns a *quantitative* cross-substrate prediction
  of unprecedented sharpness.

If the sign reverses but the magnitude fits each substrate separately,
the framework holds at the qualitative composite-pairing level but
loses universality on the magnitude. If the sign doesn't reverse at
all, the §3.5 mentor composite is wrong.

**Implementation cost.** Heaviest *substrate scaffolding* of the five
because no current substrate has the c–s mentor pair set up natively.

- **Substrate scaffolding.** Two paths, in roughly increasing cost:
  - **mpa-brain coupled-wells extension.** Add a fifth scenario
    "c–s mentor pair" to `mpa_brain_packs.scenarios` with engineered
    γ_AB < 0 cooperative coupling between two anchors. The Langevin
    machinery is the same; just two coupled potential wells with
    mismatched trail kernels (committed = deep, suspended = shallow).
  - **mpc-glass dual-subsystem extension.** Phase 1 already landed
    the dual-subsystem schema in
    [`mpc_glass_packs/glass_socket/`](../mpc-glass/mpc_glass_packs/glass_socket/);
    F-007 row 17 (s–s competitive) was tested at J_AB=0.5. Extend to
    a c–s pair via temperature mismatch between subsystems.
- **Time-reversal-aware measurement primitive.** Use the
  `reverse_replay` machinery from Test 3 to flip the drive protocol;
  measure C_AB(t, t_w) forward and reverse.
- **Calibration of κ, λ_A, λ_B.** Per substrate, per operating point.
  Single-trail λ already comes out of `enrich_sample`; κ requires
  substrate-specific identification (existing material on Langevin;
  needs work for glass coupled).
- **Cross-substrate lag-asymmetry collapse plot.**

### Test 5 — The Wall-cusp universality (highest evidential power, heaviest infrastructure)

**The prediction.** v8 §6 / Appendix G says the Compression Axiom flow
contracts with rate ε = ‖𝒞‖_op < 1 below the Complexity Wall. Sweeping
a substrate's control parameter Δp toward the Wall, ε approaches 1
from below — but the *shape* of the approach is power-law:

$$\epsilon(\Delta p) \sim |\Delta p|^{-\nu(d)}$$

with ν an exponent depending on graph dimension d. ν is the universal
quantity. Substrates of different d sit on different ν.

**Why it's the strongest test.** Three commitments at once:

1. **Cusp not crossover.** A phase-transition signature, falsifying
   the polynomial / smooth-degradation alternatives in v8 §7.1.
2. **Power-law form.** Specific functional form, falsifiable by
   any non-power-law shape (exponential, logarithmic, etc.).
3. **Universal exponent across substrates of same d.** Testable by
   running multiple substrates at the same effective d and checking
   ν matches. Substrate-class universality is the hardest claim to
   falsify by accident.

**Acceptance.** Curves from glass (d=3 EA), quantum (d=2 surface code),
brain (d=1 effective for single-particle Langevin) collapse onto a
universal ν(d) curve when each substrate's ε is rescaled by its
substrate-specific Δp_crit. If ν is substrate-specific (no collapse),
MPA's universality claim is falsified at the meta-ledger flow level.
If the cusp is smooth (no power-law), the sharpness commitment is
falsified.

**Implementation cost.** Heaviest of the five. Requires:

- **Operationalize cluster-digest streams** on each substrate. Currently
  no substrate has these; the Compression Axiom test is listed in v8's
  claims register as "experimentally accessible, not yet measured" with
  no operational definition. Per-substrate cluster-digest definition is
  the bottleneck.
- **Operationalize ε measurement.** Spectral gap of the contraction
  operator if available; operator-norm ratio of level-(n+1) over level-n
  variance otherwise.
- **Wall-crossing parameter sweep + power-law fit** on each substrate.
- **Cross-substrate ν(d) collapse analysis.**
- **Visualizer panel.** for cross-substrate Wall-cusp
  rendering.


## Recommended sequencing

**Track A** Test 1 (ξ = 1 crossover).
Re-analyse existing sweep_g data; operationalize τ_env per substrate;
verify the direction-reversal at ξ ≈ 1. The smartest immediate move
because the data is already collected — we just need to change how we
read it. If the prediction holds, rule 7's substrate-class hierarchy-
direction-inversion gets absorbed into rule 12's universality machinery.
If it doesn't, rule 7 stays as the categorical escape clause. Either
outcome is informative.

**Track B** Test 2 (engineered k-frust on
syndromes). Single-substrate, narrow but sharp test of v8's strongest
unmeasured prediction in the claims register. Cheap; orthogonal to
Track A's analysis work.

**Track C** Test 3 (hysteresis-gap-as-regime-invariant).
Substrate-side `reverse_replay` flag + visualizer Chunk D.2 + cross-
substrate gap analysis. Builds on the snapshot-relative ẋ infrastructure
landed this session. Earns the dynamical-asymmetry universal observable
as a complement to rule 12's static plateau.

**Track D** Test 4 (c–s mentor lag asymmetry). Needs the
substrate scaffolding for two-node coupled systems (mpa-brain extension
or mpc-glass dual-subsystem). The quantitative lag = 2κΔ|λ| prediction
is the sharpest single observable in the program; if this lands cleanly
across two substrates, MPA has empirical content beyond what any single
substrate's theory predicts.

**Track E** Test 5 (Wall-cusp ν(d)). The headline
universality test. Cluster-digest stream operationalization is the
project's biggest single blocker; it unlocks the Compression Axiom test
that has been "experimentally accessible, not yet measured" since v6.

Order rationale: lighter tests first to lock partial wins (Track A
absorbs rule 7; Track B nails the k-frust falsification check). The
heavy infrastructure (Tracks D and E) starts after the cheap evidential
wins are in. Track C sits in the middle — moderate cost, sharp
prediction, builds on this session's infrastructure.

## What "compelling" looks like end-to-end

If all five tests come back positive:

- **Test 1 positive**: ξ = 1 crossover sharp on every substrate. Rule
  7's substrate-conditional escape clause for hierarchy direction is
  absorbed into rule 12's universality. The framework now predicts the
  direction of the τ_obs walk from a single universal criterion.
- **Test 2 positive**: engineered k-frust noise produces the predicted
  negative-FDR signature on syndromes. The k-frust regime's universal
  observable is empirically grounded on a substrate where the topology
  is controllable.
- **Test 3 positive**: gap-as-regime-invariant cross-substrate. The
  dynamical-asymmetry signal complements the static plateau as a
  universal observable.
- **Test 4 positive**: lag asymmetry ≈ 2κΔ|λ| across two substrates.
  MPA earns a quantitative cross-substrate prediction at the composite
  layer. Sharpest single result in the program.
- **Test 5 positive**: ν(d) collapse across glass / quantum / brain on
  a universal curve. MPA's RG-flow / Compression-Axiom / universality-
  class structure has empirical content of the same flavour as
  critical-phenomena universality.

That five-of-five would establish MPA as a published, falsifiable
framework with cross-substrate empirical content of a kind no
neighbouring framework has on the same substrates simultaneously.
Compelling at the level critical-phenomena universality is compelling.

## What "invalidated" looks like

The framework's universality claim is the load-bearing part. Per-test
falsification thresholds:

- **Test 1 negative**: ξ = 1 crossover isn't sharp or doesn't align with
  the predicted point. Rule 7 stays as a categorical substrate-class
  label; the universality at the scale-relativity layer is weaker than
  v8 §2 commits to.
- **Test 2 negative**: engineered correlated noise doesn't produce the
  predicted negative-FDR signature on syndromes. The k-frust observable
  may detect frustration but not predict it; the substrate-class scope
  for k narrows.
- **Test 3 negative**: gap doesn't track regime label cross-substrate.
  The dynamical-asymmetry-as-regime-invariant prediction is wrong; the
  metastability claim is not falsifiable through dynamics, only through
  static (τ, dt) plateau (which we already have).
- **Test 4 negative**: lag asymmetry doesn't reverse, or reverses but
  with substrate-specific magnitude. The §3.5 mentor composite is
  qualitatively right but quantitatively substrate-specific —
  substantial weakening of the composite-layer universality claim.
- **Test 5 negative**: ν is substrate-specific (no collapse). The
  Compression-Axiom flow is not a universality class in MPA's sense.
  v8 §6 / Appendix G's RG-flow framing weakens to "each substrate has
  its own contraction operator with its own scaling," still useful
  descriptively but losing the universality content.

Three-of-five negative would seriously challenge MPA's strong-form
universality claims and push the framework back to "useful descriptive
vocabulary, not predictive theory." One-of-five negative is informative
but recoverable; we'd refile the negative result as a substrate-class
scoping rule under rule 7. Two-of-five negative is borderline — depends
on which two.

## What's owed before any test

Four infrastructure pieces are shared across the program:

0. **The MPA library** (Tests 1, 3, 4, 5 — analysis-only after this).
   Status: spec landed 2026-05-05 at [`library/LIBRARY_SPEC.md`](library/LIBRARY_SPEC.md);
   grinder ready to run. ~10-14 hours of unattended workstation compute
   produces the canonical characterized-lightfield. Once it exists,
   four of the five tests query it instead of running new substrate
   sweeps.
1. **τ_env operational definition per substrate** (Test 1; library
   placeholder). The simplest piece — measurable from already-emitted
   substrate observables, but currently uses analytic placeholders in
   the library schema (`tau_env_measured: null`, `tau_env_analytic:
   {…}`). ~30 LOC per substrate to emit measured τ_env on the
   primitive's `init` event; populates the library field on next grind.
2. **Reverse-replay flag** (Test 3 + Test 4). Small substrate change
   per substrate.
3. **Cluster-digest stream definition** (Test 5). The biggest single
   blocker. New operational content; the Compression Axiom hasn't
   been measured because nobody has written down what level-n and
   level-(n+1) state look like on each substrate.

The cleanest order is: (0) library grind first (the canonical artifact
every test queries). Then (1) τ_env_measured emission to populate the
library's `tau_env_measured` field properly (Test 1 lands cleanly after
this). Then (2) reverse-replay (Test 3 + Test 4). Then (3)
cluster-digest streams (Test 5). At each step the library accumulates;
nothing else is rerun.

## Cross-link to existing prediction infrastructure

- **(τ, dt) plateau on snapshot-relative ẋ** ([RULES.md rule 12](RULES.md))
  — already validated; the foundation rule 12 establishes for the
  region-as-universal claim.
- **ξ = 1 scale-relativity crossover** — Test 1 above. Sharpens rule 7.
- **k-frust on engineered correlated-error circuits** — Test 2. Open
  prediction in v8 claims register; substrate-side engineering in
  mpc-quantum F-014 / F-018 follow-up.
- **Hysteresis gap** — Test 3. Framing developed in
  [mpa-visualizer handoff Chunk D.2](../mpa-visualizer/docs/handoff_next_session.md).
- **c–s mentor lag asymmetry** — Test 4. Substrate scaffolding owed
  in mpa-brain (coupled wells) or mpc-glass (dual-subsystem,
  Phase 1 socket already landed).
- **Wall-cusp ε ∼ |Δp|⁻ⁿ** — Test 5. v8 paper claims register entry
  "Compression Axiom on cluster-digest streams" needs refinement to
  include the cusp + power-law structure.

## Discipline for whichever test gets picked up

- **Pre-register the prediction.** Before running, write down the
  expected curve, plateau values, gap structure, exponent — whatever
  the test predicts, in a `pre_registered/` doc on each substrate.
  After the run, compare. This avoids the dial-in trap of tuning the
  prediction to match the data.
- **Cross-substrate first, single-substrate second.** A positive
  result on one substrate is interesting; a positive result with
  cross-substrate collapse is the framework's claim. Don't claim
  validation from a single-substrate positive without the universality
  check.
- **Honest negative reporting.** If a test fails, document the failure
  mode in the substrate's FOOTING + a paper-level claim register
  entry. Failure of universality is a substrate-class scoping result
  under rule 7, not a claim of validation with weaker content. Don't
  write the latter when the former is what happened.
