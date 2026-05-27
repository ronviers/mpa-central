# MPA Implementation Rules

Cross-substrate discipline for implementing MPA observables on substrates.
Substrate-neutral. Substrate-specific findings live in each project's
`docs/journey/FOOTING.md`.

**Companion: testing methodology.** [`METHODOLOGY.md`](METHODOLOGY.md) is the program-wide testing discipline (substrate scope, evidence scope, artifact scope, infrastructure scope). RULES.md handles substrate-implementation discipline; METHODOLOGY.md handles testing-validation discipline. Together they define what counts as MPA work.

**Theory.** Operational source of truth has migrated from v8 to the unified `mpav1` document in `mpa-atlas`:

- [`H:\mpa-atlas\framework\mpav1_compressed.md`](../mpa-atlas/framework/mpav1_compressed.md) — one phenomenology, two readings joined at one spine. The STRUCTURAL reading (operator algebra, capacity bounds, FDR signatures, Compression Axiom) and the CHARACTER reading (continuous physical economics, chit unit, two-mode kernel, heat-tax tower, FDR apparatus, ten cascade adoptions) are the two wings of this single file.
- [`H:\mpa-atlas\framework\mpav1_receipts.md`](../mpa-atlas/framework/mpav1_receipts.md) — line-keyed justifications.
- v8 (`v8_MPA_A_Dynamical_Semantics_for_Resource-Bounded_Inference.md`, this directory) is preserved as historical archive; rules that cite v8 sections cite the mpav1 equivalent in addition to or in place of v8.

**Protocol surface.** RFCs in [`H:\mpa-atlas\rfcs\`](../mpa-atlas/rfcs/) (RFC-1 spec object, RFC-2 FDR signatures, RFC-3 consistency, RFC-S scale management, RFC-V vocabulary, RFC-RI realizer interface, RFC-C calibration). Rule 14 below names the RFC-S compliance prerequisite.

**Rewrite-on-your-way-out:** when a session locks a cross-substrate
truth, edit this file before signing off. Keep it lean — prune
content that has migrated to substrate FOOTINGs.

---

## 1. Trail vector is the EMA of ẋ — velocity, not state

v9 §Setting and §Operators: $d_A(t) = \int K_A(t-s) \dot{x}(s) \, ds$ — kernel-weighted history of change while proposition $A$ is active. (v8 Appendix A original.) The integrand is the substrate's natural notion of *change*, not the static state.

| Substrate | natural state $x$ | substrate-correct $\dot{x}$ |
|---|---|---|
| Continuous Langevin (mpc-brain) | particle position $x(t)$ | velocity $\dot{x}(t)$ |
| Surface code (mpc-quantum) | stabiliser readout $s_i(t)$ | detection event $e_i(t) = s_i(t) \oplus s_i(t-1)$ |
| Ising glass (mpc-glass) | spin state $s_i(t)$ | spin-flip $\Delta s_i(t) \in \{-2, 0, +2\}$ |
| Discrete Markov | state index $\sigma(t)$ | transition indicator $\mathbb{1}[\sigma(t) \neq \sigma(t-1)]$ |

If you EMA the state $x$ instead, every downstream observable is
computed on the wrong object. $\|d_A\|$ asymptotes to substrate-
equilibrium quantities (EA order parameter on glass, etc.) instead of
the rate-of-change object v8 names.

## 2. ẋ must be locally bounded in time

mpav1 §Operators (and §FDR signatures) locality requirement: an event at time $s$ has bounded
effect on observables at later times. Substrates whose natural readout
violates this (raw stabiliser measurements: one error flips every
future adjacent stabiliser) require canonical local preprocessing as
input. The XOR for surface codes (v9 §Substrate-conditional reading rules F.2; original v8 Appendix F.2) is *the* worked
instance — the same XOR also delivers $\dot{x}$ as state-change.
Don't conflate these two jobs on substrates that need only one.

## 3. Streaming-primitive event shape

Each substrate's measurement primitive is an iterator yielding typed
events. Same shape across substrates so visualizer drivers, offline
replay, and batch wrappers all carry:

- `init` — config + planned `sample_times`
- `phase_a` — equilibration progress (sparse, optional)
- `snapshot` — at the $t_w$ reference time
- `phase_b` — observation progress (sparse, optional)
- `sample` — at scheduled $t > t_w$; carries `{C, chi, substrate, per_window}`
- `complete` — end-of-run

The `sample` event splits *raw* observables (`C`, `chi`, `per_window
{C_d, C_d_diag, chi_d, d_norm, sigma_d}`) from regime classification
and locus-geometry enrichment. Enrichment is a post-pass helper
(`enrich_sample`) that consumers apply selectively.

Reference implementations:

- mpc-glass: [`mpc_glass_packs/measurements.py`](../mpc-glass/mpc_glass_packs/measurements.py) `multi_window_fdr_iter`
- mpc-quantum: [`mpc_quantum_packs/measurements.py`](../mpc-quantum/mpc_quantum_packs/measurements.py) `multi_window_fdr_iter`

## 4. Substrate produces, visualizer consumes — one direction

Substrate code does not know the visualizer exists. The visualizer
imports substrate primitives read-only via `sys.path`. The streaming
event shape is the contract. If the visualizer's driver finds itself
implementing science, the math leaked — push it back to the substrate.

Per-substrate contract documents (visualizer-side):

- glass: `H:\mpc-visualizer\docs\` (in driver source)
- quantum: [`H:\mpa-visualizer\docs\quantum_tab_event_protocol.md`](../mpa-visualizer/docs/quantum_tab_event_protocol.md)
- brain:   [`H:\mpa-visualizer\docs\brain_v8_event_protocol.md`](../mpa-visualizer/docs/brain_v8_event_protocol.md)

## 5. Coordinate-space discipline

The CK 1993 parametric plot lives in **raw-readout denom space**:
$1 - C(t, t_w)$, bounded above by $1 - q_{EA}$. Trail-vector observables
live in **trail-vector denom space**: $C_d^{\text{diag}} - C_d$, bounded
above by $C_d^{\text{diag}} - C_d^\infty$. These are *different intervals*.

**The breakpoint must be in the same coordinate space as the empirical
trajectory.** Reading the breakpoint from raw-readout $C$ and applying
it to a trail-vector plot is a coordinate mismatch that produces
spurious empirical-vs-envelope gaps.

**The discipline generalizes to a family of coordinate spaces indexed
by ẋ choice.** Rule 1 names the substrate-correct ẋ — the prescriptive
entry the framework's primitives are computed against. Alternative ẋ
choices are sometimes used as research moves, to surface complementary
substrate properties along the same trajectory. Each ẋ choice defines
its own trail-vector denom space (its own $C_d^{\text{diag}} - C_d$
bounds, its own $C_d^{\text{diag}} - C_d^{\infty}$ envelope) and its
own breakpoint within that space. The discipline above applies *within*
each family member:

- The breakpoint must live in the *same* ẋ-coordinate space as the
  empirical trajectory it is being compared to.
- Bounds, envelopes, and FDR-shape categories computed in one
  ẋ-coordinate space do not transfer to another.
- Cross-coordinate comparisons (e.g. velocity-d-FDR vs
  position-relative-d-FDR on the same substrate) compare complementary
  slices of the same physics, not two competing readings of the same
  observable. Both readings can be coordinate-correct yet disagree at
  face value, because they live in different intervals.

Worked instance: mpa-brain `F-002` (Sweeps A–G, 2026-05-04). The
substrate-side findings record migrated 2026-05-05 to
[`H:\mpa-brain\docs\journey\mpa_brain_sweep_findings.md`](../mpa-brain/docs/journey/mpa_brain_sweep_findings.md);
the canonical F-entry lives at
[`H:\mpa-brain\docs\journey\FOOTING.md`](../mpa-brain/docs/journey/FOOTING.md)
in the mpa-brain repo (<https://github.com/ronviers/mpa-brain>).
Same overdamped Langevin substrate, same four-scenario test plan. In
velocity-d-FDR coordinates the late-dt f-fingerprint reads flat-r-like
at f ≈ 0.93 across all four scenarios — no scenario separation. In
position-relative-d-FDR coordinates (ẋ = $x(t) - x(t_{\text{snap}})$)
the same fingerprint reads as a tight scenario-discriminating plateau
in the broad-τ × late-dt corner: f(c) = 0.085, f(s) = 0.150,
f(k) = 0.005, f(r) = 0.226 at τ = 1000. Both coordinate readings see
the substrate truthfully; they read different (τ, dt) regions where
each coordinate's discriminating signal lives.

## 6. Multi-source calibration: when a parameter has ≥2 estimators, surface them all

Any framework parameter with multiple natural estimators ($q_{EA}$ from
raw-$C$ saturation; from FDR-shape locus breakpoint; from trail-vector
$C_d^{\text{diag}}$ saturation) gets all of them displayed
simultaneously. Agreement = MPA reads the substrate consistently.
**Disagreement is the signal** — it identifies which estimator is
biased and at what scale. Do not reduce to a single number.

## 7. Substrate-conditional readings are first-class

Reading rules adjust how observables are *interpreted* on a substrate
while leaving the framework's primitives intact. They are part of
substrate-application discipline, not framework content (v9 §Substrate-conditional reading rules; original v8 Appendix F.3).
Earned by application work; recorded with substrate class and empirical
evidence.

Patterns earned so far:

- **Sign-magnitude split.** On Markovian-flavored substrates,
  $\gamma$-sign predictions invert while magnitudes and FDR shapes are
  preserved. Use $|\gamma|$ and FDR shape jointly, not sign alone
  (v9 §Substrate-conditional reading rules F.1; original v8 Appendix F.1).
- **Hierarchy direction inversion.** v9's §Scale-relativity ("vertex label depends on $\tau_{obs}$"; original v8 §5) holds when the substrate's committed structure lives
  at fine timescales (Langevin). It **inverts** on substrates with
  emergent *coarse-time* committed structure (surface-code syndromes,
  glass aging) — those walk r → s → c as $\tau$ widens. The hierarchy
  itself is substrate-invariant; the direction is not. Canonical
  syndrome-substrate entry: mpc-quantum FOOTING `F-018`.

## 8. Kernel warmup: budget run-length, don't engineer around it

EMA-kernel trail vectors $d_A(t) = \sum_{s \le t} K_A(t-s)\,\dot{x}(s)$ with
discrete realisation $d(t) = (1-\alpha)\,d(t-1) + \dot{x}(t)$, $\alpha =
e^{-1/\tau}$, have effective memory $\sim \tau$. Until ~5τ rounds since
the kernel's zero-initialisation, the trail's amplitude is dominated by
the boundary condition, not the substrate's stationary behaviour. Any
classifier (FDR-shape, $\lambda_A$, locus geometry) reading a window
$\tau_k$ at time $t$ is honest only if $t \gtrsim 5\tau_k$ from kernel
init.

The fix is the run-length budget, not the display:

- **Default to $t_w + t_{\text{obs}} \ge 10\,\tau_{\max}$.** Compute is
  cheap on the workstations these substrates run on; cutting runs short
  to "see something faster" produces transient-dominated rows that look
  like real findings. Always size the run to the widest kernel.
- **Equilibration and warmup are independent budgets.** $t_w$ buys
  substrate equilibration; kernel warmup is paid in $t_w + t_{\text{obs}}$
  jointly because the EMA accumulates across both phases. Lengthening
  $t_w$ alone does not fix a transient widest-τ row.
- **Display only what's earned.** A cell at $(τ_k, t)$ with $t < 5\tau_k$
  is a warmup artefact. If the run-length budget is met, every displayed
  cell is past warmup and the labels mean what they say.
- **(τ, dt)-region matters per ẋ choice (operational addendum).**
  Within an ẋ choice's coordinate space (rule 5), the discriminating
  substrate signal does not live uniformly across the (τ, dt) plane.
  *Per-step* ẋ (velocity, Δs, detection events, transition indicators)
  typically encode the signal at small dt (dt ≲ τ) before the EMA
  decorrelates the trail from the snapshot; at large dt the per-step
  trail has fully decorrelated and $f \to 1$ regardless of regime.
  *Snapshot-relative* ẋ (e.g. mpa-brain's $x(t) - x(t_{\text{snap}})$)
  encode the signal at large dt (dt ≳ 5τ), once the trail has
  accumulated coherent drift; at small dt the trail has not yet
  differentiated from zero and $f \to 0$. Read each ẋ choice in its
  honest (τ, dt) region; reading at the wrong region returns the
  EMA-decorrelation limit ($f \approx 1$) or the trail-buildup limit
  ($f \approx 0$), neither of which carries scenario information.
  mpa-brain `F-002` surfaced this on Langevin; cross-substrate
  confirmation owed before the (τ, dt) plateau structure earns its
  own first-class rule.

Substrates that have hit this: glass (τ=2000 row "all grey at
t_obs=2000" in the 2026-05-04 dial-in); quantum (τ=300 row
non-monotonically r_like at t_obs=600 in the 2026-05-03 step-2 smoke).
Both runs were under-budgeted at the wide end; both substrates show
clean walks where the budget was met. The 2026-05-03 step-3 glass
ẋ-rewrite landed with t_w + t_obs = 10200 vs 10·τ_max = 10000 — at
the budget edge for the τ=1000 row; the τ=10000 production-scale
re-run still owed.

## 9. Pin substrate-specific findings to the substrate

Substrate-internal action items, prescriptions, and verifications go in
that substrate's `docs/journey/FOOTING.md`, not here. This file holds
substrate-neutral discipline only. Cross-substrate transfer claims and
universality findings (where they hold and where they need
substrate-conditional rules) belong here as Rule-7-style entries.

Canonical substrate entry points:

- [`H:\mpc-brain\docs\journey\FOOTING.md`](../mpc-brain/docs/journey/FOOTING.md) — Langevin, v8 Appendix A worked instance
- [`H:\mpc-glass\docs\journey\FOOTING.md`](../mpc-glass/docs/journey/FOOTING.md) — 3D EA Ising aging (ẋ rewrite landed `F-011` 2026-05-03; refined CK calibration owed per `P-006`)
- [`H:\mpc-quantum\docs\journey\FOOTING.md`](../mpc-quantum/docs/journey/FOOTING.md) — surface-code syndromes (`F-007`, `F-018`)

## 10. Inherit substrate vocabulary; don't invent

When MPA's primitives have an established name in the substrate's existing
literature, use that name. The framework's structural insight is preserved
by the rename; the friction of new vocabulary is not. Inventing new MPA
names for objects substrates have already named is the ego-trap that turns
"we read the same structure" into "you must learn our terms" — which costs
the cross-substrate transfer claim its credibility with the substrate's
experts.

The worked instance is the K cavity-method correspondence (v9 §Operators K row + §Boolean section; original v8 §3, Appendices A, B, C, integrated 2026-05-03):

| MPA term | Substrate term | Source field |
|---|---|---|
| $K$ (Conflict operator) | XOR / parity-check operator over $\mathbb{F}_2$ | random constraint satisfaction (Mézard–Ricci-Tersenghi–Zecchina 2003) |
| $\mathcal{M}_2 = \{c, r\}$ (Boolean section) | Frozen core | cavity method (Krzakala et al. 2007) |
| Input-side quotient on $\mathcal{M}(\infty)$ | Survey-propagation-guided decimation | cavity method (Mézard–Parisi–Zecchina 2002) |
| Difference-trail Boolean messages | Warning propagation | cavity method (Braunstein–Mézard–Zecchina 2005) |

The K rename is what made mpc-sat (step 5) tractable. Same discipline
applies to any future substrate where MPA's primitives line up with an
existing field's vocabulary. Spend 30 minutes in the substrate's textbook
before naming anything.

This rule covers vocabulary alignment for *primitives*; rule 7 covers
substrate-conditional *interpretation* of observables. They are
complementary: rule 7 says "the substrate may read MPA's observables in
substrate-specific ways"; rule 10 says "the substrate's existing names
are the right names for MPA's structures when they line up."

## 11. Smoke runs need a fluxing trajectory — the Boolean limit is operational, not just theoretical

v9 §Setting names the Boolean limit as the singular point where MPA
degenerates: $\Phi^* \to \infty$ (so $D \to \infty$), $\mathcal{M}$ collapses onto
$\mathcal{M}_2$, the trail vector has nothing to integrate. (Original v8 Theorem 8.) The
operational form is that any substrate state with $\dot{x} = 0$
throughout phase B produces an identically-degenerate reading: by rule
1 the trail is the EMA of $\dot{x}$, so $\dot{x} = 0$ ⇒ $d \to 0$ as
$\exp(-t/\tau)$, and every per-window observable
($C_d$, $C_d^{\text{diag}}$, $\chi_d$, $d_{\text{norm}}$, $\sigma_d$)
reads exactly 0.

This is *substrate-truthful* — a substrate at a fixed point genuinely
has zero flux, so its trail genuinely should be zero — but *degenerate
as a contract test*: there is nothing to classify, no shape on the
parametric plot, no contour to assign. The streaming primitive's
"non-degenerate observables" property cannot be verified from a
fixed-point reading.

The discipline:

- **Pick the smoke / sanity operating point so the substrate fluxes
  throughout phase B.** Substrate-conditional. On WalkSAT, $\alpha$
  above the algorithmic SAT–UNSAT threshold (the solver is incomplete
  on UNSAT and keeps fluxing). On glass, $T \gtrsim T_g$ above the
  glass transition. On surface codes, finite physical-error rate. On
  Langevin, finite temperature with no absorbing well.
- **If a smoke run produces all-zero observables, check whether
  $\dot{x}$ went to zero before concluding the primitive is broken.**
  The substrate-block liveness counter is usually enough to tell
  (`n_unsat` for SAT, `energy_density`'s drift for glass,
  `detection_rate` for quantum syndromes). Zero flux + everything-zero
  trail is the rule-1 prediction acting correctly, not a measurement
  bug.
- **Fixed-point readings remain legitimate science readings.** When a
  substrate genuinely reaches a fixed point in a science run, the
  long-time regime IS r-equilibrated / decorrelated; the trail decay is
  its honest signature. Document it as such. Do not confuse it with a
  degenerate-observable bug, and do not promote it as evidence the
  streaming primitive yields non-degenerate observables on a fluxing
  trajectory.

Earned at mpc-sat first session (2026-05-03). Smoke at $\alpha = 4.0$,
$N = 200$ entered a fixed point in phase A — WalkSAT trivially solved
a sub-threshold instance, $\dot{x} \to 0$, every per-window observable
read 0.000 at every sample. Bumped to $\alpha = 4.30$, $N = 500$
(typically UNSAT, WalkSAT incomplete on UNSAT, trajectory keeps
fluxing); contract verified, all per-window observables non-degenerate
(four windows reading k-regime — the frustrated-cycle signature on
unsatisfiable random 3-SAT — with $|R|$ ranging 5.4 to 17.5 across
$\tau \in \{10, 30, 100, 300\}$).

The rule applies on every substrate. It surfaces *first* on SAT
because SAT-the-formula *is* v8 Theorem 8's singular point —
finding a satisfying assignment IS reaching the Boolean limit, with a
hard wall against further flux. Other substrates have softer
Boolean-limit boundaries (glass equilibrium is approached gradually,
quantum decoherence is bounded but never absolute, Langevin
stationary distributions still fluctuate) so the trap surfaces as
smoke-run noise instead of hard-zero. The fix is the same on all of
them: choose the operating point to keep the substrate fluxing through
phase B.

## 12. (τ, dt)-region carries scenario-discriminating signal under each ẋ choice

The discriminating signal in the (τ, dt) plane lives in a
coordinate-space-specific region, not uniformly across the plane.
Reading at the wrong region returns a coordinate-asymptote that carries
no scenario information. Two regions and the ẋ choices that read them
honestly:

- **Per-step ẋ** (velocity, Δs, detection events, transition
  indicators). Discriminating region: **small dt, dt ≲ τ** — before the
  EMA decorrelates the trail from the snapshot. At large dt the per-step
  trail has fully decorrelated and *f* → 1 regardless of regime.
- **Snapshot-relative ẋ** (mpa-brain's $x(t) - x(t_{\text{snap}})$,
  mpc-glass's $s_i(t) - s_i(t_{\text{snap}})$, mpc-quantum's
  events-since-snap). Discriminating region: **broad τ × late dt,
  dt ≳ 5τ** — once the trail has accumulated coherent drift since
  snapshot. At small dt the trail has not yet differentiated from zero
  and *f* → 0.

Within its discriminating region, each ẋ choice produces a stable
plateau in *f* whose value separates scenarios. The plateau values
themselves are substrate-conditional — different substrates carry
different orderings of c/s/k/r along the *f*-axis at the same (τ, dt)
cell, exactly the hierarchy-direction inversion rule 7 codifies. **The
region is substrate-invariant; the direction is not.**

The (τ, dt)-region rule supersedes any "single (τ, dt) point fingerprint"
pattern. Reading scenario discrimination at one cell is fragile to
coordinate-asymptote bleed-through; reading the plateau across the
discriminating region is robust to it.

**Cross-substrate evidence.** F-002 (mpa-brain Langevin), F-019
(mpc-quantum syndromes), and the analogous glass entry (mpc-glass) form
the empirical foundation. Each substrate's broad-τ × late-dt
events-/displacement-relative *f* plateau separates its scenarios:

| substrate | snapshot-relative ẋ | broad-τ × late-dt *f* spread |
|---|---|---|
| mpa-brain Langevin | $x(t) - x(t_{\text{snap}})$ | 0.005..0.226 (4 scenarios at τ=1000, dt~10000) |
| mpc-glass 3D EA | $s_i(t) - s_i(t_{\text{snap}})$ | 0.095..0.266 (4 T-scenarios at τ=1000, dt=10000; n_real=32) |
| mpc-quantum syndromes | events-since-snap | 0.010..0.343 (4 p-scenarios at τ=1000, dt~9450; n_seeds=8) |

The orderings differ: brain reads c→s→r monotonic with k lowest; glass
reads bimodally peaked at metastable mid-T; quantum reads monotonic
descending in p. All three substrates show scenario discrimination
within the broad-τ × late-dt corner of the snapshot-relative ẋ
coordinate space, and at no other corner of the (τ, dt) plane in that
coordinate space.

**Operational consequences.**

- Each substrate's primitive ships with at least the per-step ẋ choice
  (literal rule 1 prescriptive) and the snapshot-relative ẋ choice. The
  visualizer's tab template reads the appropriate (τ, dt) region per
  ẋ choice; the cross-substrate side-by-side panel reads the broad-τ ×
  late-dt corner of each substrate's snapshot-relative coordinate.
- Comparing scenarios across coordinate spaces (e.g.
  velocity-d-FDR vs position-relative-d-FDR) compares
  *complementary slices of the same physics*, not two competing
  readings. Each ẋ choice is read in its honest region (rule 5).
- Substrate-conditional direction is recorded in each substrate's
  FOOTING; this rule pins only the region.

When a new substrate joins the constellation, its primitive should
expose both ẋ choices, and the cross-substrate gate applied to the
broad-τ × late-dt plateau in snapshot-relative coordinates becomes the
quickest empirical check of v8 substrate-fit. If the broad-τ × late-dt
corner of the snapshot-relative ẋ does NOT separate the substrate's
operating-point scenarios, the substrate is not in the v8 universality
class for vertex regimes (the appropriate response is to confirm
operating-point coverage, then if confirmed file a substrate-class
note under rule 7).

## 13. Time grids must be τ_env-anchored, not substrate-global

Sample-time and τ_obs grids should scale with each operating point's
intrinsic relaxation timescale τ_env, not be set once globally for a
substrate.

**Physics rationale.** v9 §"Compression Axiom / meta-ledger flow" (terminal-attractor reading; original v8 Appendix G): every
finite-flux trail eventually decays to *r*. Without external reinforcement,
the maintenance bookkeeping budget runs out for any *c* and *s* in
finite time. (Character §"Fraying sequence" and §"Pattern formation and self-organization" give the dynamic / SOC reading of the same fact.) The *interesting* observation window per operating point is
bounded above by τ_env — past ~10·τ_env the substrate has dissolved into
the r-asymptote and the trail vector reads no scenario-discriminating
signal. Past ~100·τ_env it reads exactly what the trivial r-equilibrium
would read. *Conversely* below ~0.01·τ_env the substrate has not yet
relaxed from the snapshot at all, and the trail is in pure pre-aging
territory.

A library or sweep that uses one fixed grid across operating points
*either* burns realizations confirming the post-aging r-asymptote (when
the chosen grid extends past the operating point's actual aging window),
*or* misses the aging window entirely (when the chosen grid stops short
of it). Both are observable failures: the F-002 plateau values are
scenario-distinct only inside the substrate's aging window per operating
point.

**Operational form.**

- **Per-operating-point τ_obs grid.** Span 0.05·τ_env to 2·τ_env (or
  similar 1.5–2 decades around τ_env) so each operating point's grid
  brackets the regime walk v8 §5 predicts. Cap τ_obs_max at a
  compute-budget-driven ceiling (e.g. 5000) when τ_env is very large.
- **Per-operating-point t_obs.** Take the maximum of the rule-8 floor
  (10·τ_obs_max) and the aging coverage target (~30·τ_env). Cap globally
  at a compute-budget-driven ceiling so very-slow-relaxing operating
  points don't blow the wall. Within the cap, the sample times log-space
  inside [t_w + t_kw, t_w + t_kw + t_obs] naturally concentrate around
  τ_env.
- **Per-operating-point t_w.** ≥ 5·τ_env so substrate equilibration is
  complete before snapshot. (Operating points where 5·τ_env exceeds an
  affordable t_w cap surface as "below-Tc"-class on glass and similar
  unbounded-aging regimes; characterize as the substrate ages,
  honestly bounded by what fits in t_obs.)
- **Operating points with τ_env effectively > t_obs cap** (glass below
  Tc, syndromes deep below threshold once code-distance corrections
  are accounted for): fall back to a fixed grid within budget, and
  record the finding as "aging-window-bounded" rather than fudging a
  scaled grid that lies outside the affordable range.

**Where this rule applies.**

The τ_env-anchored discipline is load-bearing for any multi-operating-point
characterization: the MPA library (`H:/mpa-central/library/`), any
substrate-side sweep across an operating-point axis, and any
visualizer-side comparison across operating points. Single-operating-point
sanity runs and dial-in sweeps where τ_env is unknown can use a
substrate-default grid, marked as such; the discipline applies once the
goal becomes characterization rather than discovery.

**Substrate-side τ_env emission is owed.** Currently the library uses
analytic τ_env placeholders (1/p_base for quantum, critical-slowing
power-law for glass, scenario table for brain) — leading-order correct
but unmeasured. Each substrate's `multi_window_fdr_iter` should emit a
raw-readout autocorrelation timescale per operating point on the `init`
event, replacing the analytic placeholder with the measured value. ~30
LOC per substrate. Until that lands, the placeholders are robust to
factor-of-~2 wobble (the 1.5-decade τ_obs window absorbs that error
without losing the aging window).

Earned 2026-05-05 at the MPA library design — when the user pushed
back on a fixed-grid library spec with the strong claim "every c and s
becomes r at infinity, sample selectively." The rule formalizes the
discipline that physical claim demands of any honest characterization.

## 14. RFC-S compliance is the structural prerequisite for framework-canonical testing

Substrate FDR-prediction tests are framework-canonical only when the substrate emits in the [`RFC-S`](../mpa-atlas/rfcs/MPA-RFC-S_Scale-Management.md) canonical-representation form: drive $D = \Phi^*/\kappa$ as a first-class observable, $\tau_{obs}$ scheduled by an explicit driver profile per [RFC-S §4](../mpa-atlas/rfcs/MPA-RFC-S_Scale-Management.md), and predictions stated in $(D, \tau_{obs})$-space.

Substrates currently emit native parameters ($T$, $p_{base}$, $h$) and $\tau_{env}$ analytic placeholders, but not $D$ as a typed canonical observable. Until that gap closes, FDR-prediction tests on substrate data are *substrate-conventional*, not *framework-canonical* — the readings are scientifically real but cannot be cross-substrate compared at the framework's universality-class resolution.

**Operational consequence.** Before claiming a substrate instance of any mpav1 cross-substrate observable ($\alpha_s$, $P_s$, $X_c$, $X_r$, $N_f$ — §"FDR signatures"; or any of the cascade-earned observables: $Q$, $\omega_{RO}$, $I_{\text{pred}}$, Schnakenberg cycle currents, heavy-traffic queue exponent, etc.), confirm:

1. Substrate emits $D$ as a typed quantity on the `init` event (not a derived analytic placeholder).
2. $\tau_{obs}$ schedule comes from an explicit RFC-S driver profile, not a substrate-default grid.
3. Predicted observable is stated in $(D, \tau_{obs})$-space, not in substrate-native parameters.

Without these, test results are honest substrate-conditional readings (rule 7) but should not be promoted to v9-canonical or character-canonical claims. The rerun-after-RFC-S-emission protocol applies whenever a substrate's empirical workstream comes online to the framework's canonical layer.

Earned at the cFDT first analysis (2026-05-09 archive session). Follows from [RFC-S §1–§4](../mpa-atlas/rfcs/MPA-RFC-S_Scale-Management.md) which makes canonical-representation typing the prerequisite for any cross-substrate comparison.

## 15. Refinement deviation from the cdv1 prior is substrate-thermodynamic content, not fit error

The cdv1 priors per substrate are each substrate's **leading-order universality form**: glass `chit = Tc − T` (Landau distance from criticality); QEC `chit = ln(p_threshold/p_base)` (laser-analogue ln(G_0/L) that character §"Bridge to v9" fixes); brain scenario table. When refinement against real (C, χ) data deviates from the prior, the deviation IS the substrate-thermodynamic content character §"Open items" catalogs as *predictions awaiting empirical contact* — universality fixes the exponent, substrates fix the amplitude.

**The deviation is not error.** Read it as the substrate's measurement on its leading-order posit, not as fit pathology to correct. Refinement that "beats" the prior is the framework's API surface earning weight on that posit. Refinement that doesn't is honest: the substrate's deviation from leading-order is below the apparatus's resolution.

**Worked instances** (substrates whose refinement paths surface this on mpa-lens-solver):

| Substrate | Prior shape | Deviation reading |
|---|---|---|
| Glass (CK-glassy) | `chit = Tc − T` (linear Landau) | $\alpha_s$ — CK aging-diagonal slope; departure from linear near $T_c$ |
| Surface-code QEC | `chit = ln(p_threshold/p_base)` (laser-analogue) | departure from pure-laser at regime boundaries (discrete syndrome dynamics) |
| Brain (neural-population) | scenario table | context-modulated departures from the table |

**Operational consequence.** When scoring depth, refinement weights, or observable-normalization choices are under consideration, frame them as *"measuring substrate X's deviation from posit Y"* — not as *"making the score function fit better."* The trigger for a richer score is a specific posit's deviation on a specific substrate, named up front. Generic depth without a posit/substrate hook is over-engineering; the lens-solver v1.2 raw-FitDiagnostics surface + mpa-conform percentile absorption is the resting state until the trigger fires.

**Companion to rule 14.** Rule 14 names RFC-S canonical-representation typing as the structural prerequisite for cross-substrate comparison. Rule 15 names what to DO with substrate data once it is in canonical form: read deviations as posit measurements, not error.

Earned at the mpa-lens-solver v1.0 / v1.2 / bootstrap-dispatch sessions (2026-05-17/18). Full frame at [`H:/mpa-lens-solver/docs/CHARACTER_FRAMING.md`](https://github.com/ronviers/mpa-lens-solver/blob/main/docs/CHARACTER_FRAMING.md).

## 16. The model's time variable is lag; display conventions are substrate-conditional

The gFDR parametric plot's mathematical time variable is **lag since snapshot**: τ = t − t_w, the second argument of the two-time correlation $C(t, t_w)$. The analytical forward model `gfdr_model.generate_locus(...)` is a function of lag. Substrate observables — raw-readout C and χ, trail-vector $C_d$ and $\chi_d$, per-window decompositions — all compute against lag.

Substrate communities have their own display conventions for the FDR x-axis:

- **Glass-CK** (Cugliandolo–Kurchan 1993 and downstream): plot vs sample-time $t = t_w + \mathrm{dt}$. Early-lag samples cluster near $t = t_w$ on a log-$t$ axis — the visual "hairpin" of clustered points is what very-early-lag data looks like under this convention.
- **Surface-code QEC**: typically vs syndrome-round count $r$, a discrete time aligned to the error-correction cycle. Some plots use absolute time when comparing across code distances.
- **Brain**: trial-relative time and stimulus-relative time are both common; the choice is lab-conventional.

These display choices are physically equivalent (every monotonic transform preserves the parametric content). They are **not** equivalent for the model's evaluation: the model must consume lag, always, regardless of what the community plots.

**The discipline.** Bundle schemas emit **lag** (the framework canonical time, the model's input) AND **display_tau** (the substrate-community display convention, the plot's x-axis) as separate fields. The model reads lag; viewers render the x-axis at display_tau, falling back to lag when display_tau is absent. Conflating the two roles — emitting one field labeled "tau" that does both jobs — produces coordinate-axis artifacts that look like fit failures but are actually display artifacts of the model being evaluated at the wrong time variable.

**Operational form.**

- **The substrate primitive's `sample` event emits both `t` (sample-time) and `dt` (lag since snapshot)** as explicit fields. All three substrates' grinder cells already do this (mpa-central library v1.0 cells carry `all_samples[].t` and `all_samples[].dt`).
- **The curator path (mpa-conform `walk_library._extract_observable`) reads the substrate's community display convention from the substrate class profile** and emits both `tau` (= lag, canonical) and `display_tau` (= community choice) in `observable.data[]`. For glass-CK that means `display_tau = sample.t`; other substrates declare their own convention.
- **Model-fitting consumers read `tau` (lag).** Inversion (`inversion.invert`), lens-solver (`fit_translation_field`), Banach canonical-state propagation (`BanachSubstrate.state_at`), per-window enrichment passes — all evaluate at lag.
- **Viewers read `display_tau` for the x-axis** when present, fall back to `tau` when absent (v0.3 and earlier bundles). banach_overlay, the auditor's data-engine, the shot pipeline.

**Companion to rules 5 and 14.** Rule 5 (coordinate-space discipline) covers the **ẋ-coordinate-family** for trail vectors — *different ẋ choices read complementary slices of the substrate's physics*. Rule 16 covers the **time-coordinate distinction** — *one canonical model time (lag), many community display choices*. Rule 14 (RFC-S compliance as framework-canonical prerequisite) names canonical typing of $D = \Phi^*/\kappa$ and τ_obs as the cross-substrate-comparison prerequisites; rule 16 names the data-side analogue at the bundle schema layer. All three are structural prerequisites at distinct layers — coordinate, canonical typing, and time-axis separation — not substrate-conditional readings.

Earned at the v0.4 schema bump (2026-05-19). The ck-glassy T = 0.5 cell's first-lag samples (dt = 1 to 12 MC-steps) cluster in a 2% sliver of log-sample-time space near $t = t_w = 500$; in log-lag-space the same samples spread across 1.5 decades. The hairpin in the sample-time view appeared as an unmatched empirical cluster the 1-parameter chit fit could not reach. The fix was structural at the bundle schema, not parameterization: emit lag as the model's canonical time and display_tau as the community display field, separately. Same physics renders correctly under any monotonic display transform when the model evaluates at lag. The hairpin becomes a *predicted* feature of the rapid β-piece KWW decay rendered into the community's x-axis layout, not an unreachable cluster of empirical points. Full frame at [`H:/mpa-conform/docs/papers/lag_display_kww_extension.md`](../mpa-conform/docs/papers/lag_display_kww_extension.md).

---

*Last updated: 2026-05-19 (rule 16 — model's time variable is lag; display conventions are substrate-conditional — earned at the v0.4 schema bump that separated bundle observable `tau` (lag, canonical) from `display_tau` (substrate-community plot axis). Resolves the coordinate-axis-identification artifact that produced the ck-glassy T=0.5 "hairpin" of clustered empirical points; the hairpin is a display-convention feature, not a fit failure.).*

*Earlier: rule 15 — refinement deviation from the cdv1 prior is substrate-thermodynamic content, not fit error — earned at the mpa-lens-solver v1.0/v1.2/bootstrap-dispatch sessions (2026-05-17/18); companion to rule 14, names what to do with substrate data once in canonical form. Rule 14 — RFC-S compliance as framework-canonical prerequisite — promoted from a tail note to a first-class rule on 2026-05-10; theory anchors throughout document migrated from v8 to v9 + character (mpa-atlas/framework/) at the same time, with v8 references preserved as historical context. Rule 13 — time grids must be τ_env-anchored — earned at the MPA library design (2026-05-05); rule 12 — (τ, dt)-region carries scenario-discriminating signal under each ẋ choice — earned at the glass + quantum cross-substrate confirmation of mpa-brain F-002, ports the "(τ, dt)-region matters per ẋ choice" addendum from the tail of rule 8 to a first-class rule (rule 8's operational addendum preserved as per-substrate note); rule 5 extension — coordinate-space family indexed by ẋ choice — and rule 8 (τ, dt)-region operational addendum both earned at mpa-brain F-002 / Sweeps A–G; rule 11 — Boolean-limit trap is operational — added at the mpc-sat first-real-session; rule 10 — vocabulary inheritance — added at the K cavity-method correspondence session; rule 8 — kernel warmup — added at mpc-visualizer quantum-tab landing; rules 1–9 stable; document consolidated from `H:\mpc-visualizer\docs\MPA_implementation_notes.md`.*

