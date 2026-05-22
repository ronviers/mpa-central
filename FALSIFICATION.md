# FALSIFICATION — the open attack front

**This is the session entry point for the invalidation program.** Open it
first and ask *"what are we trying to break, and what's the status?"* —
not *"what substrate could we add?"*. Coverage substrates only confirm;
this ledger tracks attempts to falsify MPA, which is where the program's
marginal value is. Operational complement to [`POSITION.md`](POSITION.md)
(the Lakatosian stance); this is the front line.

Stance discipline: aim falsification energy at the framework and the
pipeline, never at the collaborator. (See the program's working-relationship
notes; obsequious is bad, belligerent is worse.)

---

## How the apparatus is layered (read this once)

A verdict on any substrate splits **three ways**, and you cannot tell
them apart without a positive control:

1. **MPA invalidated** — a claim fails on a substrate whose ground truth
   we know.
2. **MPA survives** — the claim holds / the apparatus correctly refuses
   an out-of-domain input.
3. **Pipeline fault** — the grinder or inversion is buggy; tells you
   nothing about MPA's claims.

The whole point of the **positive-control ladder** is to eliminate branch
(3) so a "BROKE" verdict is unambiguous.

Three measurement layers, each separately falsifiable:

| layer | produces | validated by |
|---|---|---|
| **grinder** | library cell: C(τ), χ(τ), per-window trail observables | measured vs analytic ground truth (black-vs-red diagnostic) |
| **inversion** (conform) | chit, regime, (owed: 5-vector incl. X) | recovered vs prescribed (blue-vs-red diagnostic) |
| **verdict** (auditor) | regime story, audit deltas | not yet exercised on controls |

**Three-curve diagnostic convention** (matches mpa-conform's
`output/diagnostics/kww_*.png`):
- **black** = measured (±SEM) → tests the grinder
- **red** = analytic ground truth (what we prescribed/know)
- **blue** = post-inversion recovery (what conform returns)
- black-on-red → grinder faithful; blue-on-red → inversion faithful;
  **blue-off-red while black-on-red → fault localized to the inversion.**

---

## Where the apparatus lives

- **Substrates:** `H:/mpa-central/library/primitives/<name>/` — each a thin
  self-contained simulator (`measurements.py` + `grind.py` + `README.md`).
  Shared protocol: `_shared/protocol.py` (phase A → snapshot → paired
  evolution → sample). Shared grind loop / parallelism / SEM:
  `_shared/runtime.py` (`run_parallel`, per-cell ProcessPoolExecutor,
  `OMP_NUM_THREADS=1` pinned; 1024 realizations default).
- **Cells:** `H:/mpa-central/library/data/<substrate>/<substrate>__<op>__<xdot>.json`.
- **Grinder-level diagnostics:** `H:/mpa-central/library/diag_ladder.py`
  → `library/output/diagnostics/control_*.png` (black-vs-red).
- **Inversion-overlay diagnostic:** `H:/mpa-central/library/diag_inversion.py`
  → `library/output/diagnostics/inversion_*.png` (adds blue; imports the
  REAL `conformer.compute.inversion.invert`, not a re-implementation).
- **Run any substrate:** `python H:/mpa-central/library/primitives/<name>/grind.py [--smoke] [--workers N] [--only-op LABEL] [--only-xdot KIND]`.

Each control/invalidator carries a machine-readable block in every
operating-point dict: `control` (with `expected_X` etc.) or `invalidator`
(with `prediction_under_test`, `falsifier`).

---

## Positive-control ladder (tares before it weighs)

Climb bottom-up; **stop at the first rung that breaks** — that localizes
the failure to the simplest input that exposes it. A rung only counts as
a test once the substrate is shown to honor its own ground truth.

| rung | substrate | adds | grinder status | inversion status |
|---|---|---|---|---|
| 0 (below floor) | *(constant — dropped)* | zero dynamics, no dissipation → below domain floor; cdv1 can't process it | n/a | n/a |
| char-zero | `square_wave` | dynamics but featureless character (the **constant of character space**); phase-randomized; measures the **resolution floor** | **PASS** — C traces analytic triangle, RMS 0.007–0.011; χ≈0 | not yet |
| char-zero (smooth) | `sine_wave` | pure single tone; C=cos(2πτ/P), oscillates, never relaxes | **PASS** — C traces cosine, RMS 0.006–0.008; χ≈0 | **see FINDING 2** |
| 1 | `white_noise` | memoryless dissipative floor, trivial-r | **PASS** — C statistically 0; scatter ∝ σ²/√N (amplitude-invariance is a *scale-awareness* question for the inversion) | not yet |
| 3 | `ou_equilibrium` | single-exp memory, FDT holds, **X=1** | **PASS** — verified raw χ/(1−C) ≈ 1.0 | (X=1 recovers via two_temp_ou below) |
| 4 | `two_temp_ou` | known **FDT violation X=T/T_eff** (oracle); C=e^{−τ/τ_relax}, χ=X(1−C) | **PASS** — raw FDR slope = X to ~2% (1.018/0.509/0.102 for 1.0/0.5/0.1) | **PARTIAL — see finding below** |
| 5 | `kww_oracle` | full 5-vector (q_EA, τ_α, β_KWW, τ_β, X) | **BUILT + PASS (2026-05-21)** — full vector round-trips (dimensionless): q_EA 0.7±0.07, τ_α 1.0±0.2, β 0.6±0.08, τ_β 0.05±0.02, X 1.0/0.5/0.2→0.99/0.55/0.26 | **5-vector fitter closed** (multi-start + domain gate) |

**Resolution floor (from `square_wave`):** the apparatus resolves the
character zero to **±0.03–0.09 in dimensionless f** (tightest mid-regime,
loosest near the C=−1 extreme). *No deviation smaller than ~0.05 in f can
be called a falsification.* This is the anchor every BROKE verdict must clear.

---

## KEY FINDING — 1-param inversion cannot recover FDT-violation X *(2026-05-19)*

**What:** Ran the real conform inversion (`conformer.compute.inversion.invert`,
stage-1 analytical chit) on the `two_temp_ou` control, which has a
*prescribed, known* FDT-violation ratio X. Result:

| cell | prescribed X | raw FDR slope (grinder) | inversion chit / regime | inversion locus slope | residual |
|---|---|---|---|---|---|
| X1.0 | 1.0 | 1.018 | −2.0 / deep_r | 1.00 | 0.001 |
| X0.5 | 0.5 | 0.509 | 0.10 / s_critical | ~0.95 | 0.079 |
| X0.1 | 0.1 | 0.102 | 0.18 / s_critical | ~0.92 | 0.246 |

**Reading:**
- The conform inversion **runs cleanly** on the new in-library cells →
  integration works, branch (3) "crash" closed.
- The **grinder is faithful** — raw FDR-locus slope recovers X to ~2%.
- At **X=1 the inversion recovers perfectly** (deep_r, slope 1.0).
- At **X<1 the 1-param cdv1 inversion cannot recover X.** Recovered locus
  slope stays pinned ~0.92–0.95; residual climbs as X drops. A dialed-in
  X=0.5 is read back as effective ~0.95.

**Why (structural, not a bug):** the 1-param cdv1 family couples C-shape
to χ-slope through a single knob — deep_r gives full-decay C *and* slope-1
χ; s_critical gives plateau C *and* reduced-slope χ. `two_temp_ou` has
**r-like C (full decay) with reduced-slope χ** — a combination outside the
1-param family. The owed **5-vector inversion** decouples these (C-shape
via q_EA, χ-slope via X) and is exactly what's needed.

**Consequence (load-bearing for the whole program):** this is the *same*
inversion used on production glass/quantum/brain. Therefore **the
production pipeline currently cannot recover FDT-violation X on any
substrate** — it only fits chit/regime. Any falsification verdict that
hinges on X (e.g. `mm1_queue`'s α_s match, the equilibrium X=1 checks) is
**unmeasurable through the 1-param inversion today.**

**Adjudication policy (decided 2026-05-19):** the **raw FDR-locus slope
measures X faithfully now** (it nailed all three). So X-based verdicts are
adjudicated at the **raw-slope layer**, not the 1-param inversion. The
1-param inversion is validated as **equilibrium-only** (X=1). Building the
5-vector fitter is reserved for when the *inversion itself* (e.g. the
auditor's regime story) must carry X — not required for the falsification
verdicts.

**Reproduce:** `python H:/mpa-central/library/primitives/two_temp_ou/grind.py`
then `python H:/mpa-central/library/diag_inversion.py`. Diagnostic:
`library/output/diagnostics/inversion_two_temp_ou__velocity.png`.

---

## FINDING 2 — no domain-of-validity gate; inversion confidently regime-classifies a pure oscillation *(2026-05-19)*

**What:** Ran the real conform inversion on the `sine_wave` control
(C=cos(2πτ/P), a driven non-dissipative tone — out of MPA's domain).

| cell | chit | regime | locus_residual |
|---|---|---|---|
| sine P30 | 0.175 | s_critical | 0.824 |
| sine P100 | 0.175 | s_critical | 0.829 |
| sine P1000 | 0.175 | s_critical | 0.558 |

**Reading (see `inversion_sine_wave__velocity.png`):**
- Grinder faithful — measured C traces the cosine (RMS 0.006–0.008).
- The cdv1 locus **tracks the cosine's first descent** (C: 1→0 over the
  first quarter-period, where the tone looks like relaxation) then
  **plateaus and goes flat** while the real C plunges to −1 and oscillates.
  The monotone-relaxation family follows the relaxation-shaped part and
  peels off at the recurrence. (This is the visual form of "the inversion
  gets a lot right" — real expressive overlap on the descent.)
- χ: measured ≈ 0 (driven, no FDT); the inversion **predicts χ ~ 0.7** —
  it manufactures a response that isn't in the substrate.

**The gap:** the bundle reports `regime_label`, `locus_residual`, and
`in_gamut` as **three independent fields with no gate that rejects a fit
on high residual.** `in_gamut` is a geometric check on (chit, gamma), not
fit quality. So the inversion does NOT refuse the sine — it returns a
confident `s_critical` and carries residual≈0.8 as a *non-gating* number.
A consumer reading regime_label without weighing residual gets a false
"s_critical" verdict for a pure oscillation. **The apparatus has no
"is this even a relaxing/dissipative substrate" gate.**

**Why it's not yet a clean BROKE (and is coupled to the owed 5-vector):**
the residual is the available domain-validity signal, but it doesn't
cleanly separate "out of domain" from "valid but 1-param-can't-express":
sine sits at ~0.8; the *genuinely-aging* two_temp_ou X=0.1 (a valid
substrate) sits at 0.25 — close. A naive residual threshold would either
pass the sine or reject real aging substrates. A clean domain gate needs
the **5-vector inversion first** (to absorb valid-aging residuals toward
~0), after which a residual threshold isolates out-of-domain cases.

**Status: CLOSED 2026-05-21.** The 5-vector inversion now absorbs valid-aging
residuals (two_temp_ou X=0.1 RMS 0.25 → 0.02) and a residual gate
(`five_vector.RESIDUAL_GATE`=0.10, `FiveVectorFit.in_domain`) cleanly isolates
out-of-domain inputs: in-family cells (two_temp_ou, kww_oracle, r-regime glass)
fit at RMS ~0.01–0.02 → IN; `sine_wave` (cosine) and the running `driven_ring`
NESS fit at RMS ~0.14–0.45 → flagged OUT. The pipeline now polices its own domain
of validity. Validated by `mpa-conform/scripts/test_five_vector_fit.py`. (Was: a
demonstrated pipeline gap pending the 5-vector fitter + gate.)

**Reproduce:** `python H:/mpa-central/library/primitives/sine_wave/grind.py`
then `python H:/mpa-central/library/diag_inversion.py` (sine block).

---

## FINDING 3 — mm1_queue falsifier is mis-specified (category error) + window-limited *(2026-05-20)*

**What:** Ran the corpus's flagship self-named falsifier. mm1_queue ground
(1024 real, ρ ∈ {0.5, 0.8, 0.95, 0.99, 0.999}); read the FDR locus χ vs
C(0)−C(τ) at the raw-slope layer.

**The falsifier as written is not well-posed.** `mm1_queue/README` equates
"α_s (FDR aging-diagonal slope)" with "the heavy-traffic exponent ½." These
are different objects in different planes:
- **½** is the reflected-BM time-scaling (Hurst) exponent — governs how
  *fast* C(τ) decays (queue relaxation time ~(1−ρ)⁻²). Lives in the C-vs-lag
  plane.
- **α_s** is the FDR effective-temperature slope. Lives in the χ-vs-C plane.

Testing "α_s ≠ ½ → BROKE" measures the wrong plane; the ½ cannot be read off
the FDR locus.

**Also window-limited.** Heavy-traffic relaxation time ~(1−ρ)⁻² outruns the
sampling window: at ρ=0.999 C decorrelates only 3.5% over the window, so α_s
is unresolvable there regardless of estimator.

**What the data leans (where resolvable):** M/M/1 is a reversible birth-death
process (detailed balance) → equilibrium FDT → X≈1. Normalized FDR slopes
across ρ clustered ~0.9 (range 0.59–1.3, noisy), **not ½** — consistent with
reversible equilibrium / critical *slowing*, not aging.

**Structural tension kept on the table (not adjudicated):** cdv1 §Load-handling
maps heavy-traffic M/M/1 (chit = −ln ρ → 0⁺) into the *s-regime*, whose FDR
signature is aging (X<1). But M/M/1 reversibility forces X=1. So either the
heavy-traffic→s-aging mapping over-claims, or s admits X=1 critical slowing
(which would blunt the c/s/r discriminator). Window + noise prevent a clean
verdict here; the **sharp version of this exact tension is the
`ising_equilibrium` test** (equilibrium critical slowing must read X=1).

**Verdict:** NOT a BROKE; NOT adjudicable as configured. The flagship falsifier
needs reframing — to test the heavy-traffic claim, either (i) measure the
C-decay-time scaling vs (1−ρ) [where the ½ actually lives], or (ii) extend the
window to ~(1−ρ)⁻² and read the FDR slope [expect ~1, reversible].

**Status:** mm1_queue PENDING → **MIS-SPECIFIED / parked** (falsifier reframe owed).

**Diagnostics:** `library/output/diagnostics/mm1_locus__queue-increment.png`,
`mm1_locus_bend__queue-increment.png`, `mm1_slopecheck__queue-increment.png`.
Scripts: `library/diag_mm1_locus.py`, `library/diag_mm1_slopecheck.py`.

**Apparatus lesson (load-bearing for ALL X-reads):** a single linear FDR slope
collapses the regime story and is biased *up* on aging loci — validated on the
`kww_oracle` control: prescribed X=0.2 reads 0.47 via single-slope vs 0.26 via
the segmented `fit_kww5`. Read X via the segmented / 5-vector fit, never a
single slope. And do **not** read a cubic-derivative-of-the-locus normalized by
origin-slope — that over-processing manufactured a spurious "coherent
divergence" (the divisor sign-flips across cells). High-resolution X-recovery
calibration runner (background, does not touch canonical cells):
`library/kww_calibration_run.py`.

---

## FINDING 4 — k_frust topological-invariance attack: option-1 substrate proxy inconclusive (rule-limited); escalating to option 2 *(2026-05-20)*

**Target:** v9 §Scale-relativity / cdv1 §Topological drain — k_frust is a
topological invariant of the coupling graph; a frustrated loop never resolves
into a clean c or r, and (the strong, user-proposed form) should survive being
driven through the Complexity Wall into chaos and brought back. *Type argument:*
you cannot falsify a subgraph-level invariant with a vertex-level operation
(going negative / to r changes labels, not wiring) — only a structural-level
operation (the Wall / chaos) can threaten it.

**Bulletproof meter built.** Minimal frustrated 3-cycle (antisymmetric/cyclic γ,
non-reciprocal → Schnakenberg cyclic current, no P_ss) vs matched control
(symmetric γ, reciprocal → detailed balance, no current). Same magnitude, only
reciprocity differs → amplitude-matched. Meter = intrinsic cyclic current J
(chirality of ρ-rotation), **observer-independent**. Clean: frust
J=+5.87e-2±3.1e-3 vs control −1.55e-3±1.0e-3 (38×, sign-definite, 6 seeds); no
NaN, no boundary-pinning, zero floor hits. Scripts:
`library/k_frust_meter.py`, `library/k_frust_jcheck.py`. (The τ_obs-sweep
observables N_f and X_v are weak/unnormalized observer-shadows — not the meter.)

**Option 1 (substrate chaos proxy) did NOT falsify — rule artifact.** Drove the
loop through chaos (scrambled wiring + bounded turbulence; the gain-boost variant
was rejected by the NaN tripwire as a ρ→∞ blowup = bad test) with annealed
(plastic) couplings, withdrew chaos, let ρ-γ co-relax. Apparent result: J did not
reform (reformed J≈6e-4, antisym≈0). **But the sustain control (plasticity on, NO
chaos) showed the imposed directional-Hebbian rule decays an EXISTING frustration
(antisym 0.93→0.41, J halving)** — the frustrated antisymmetric state is not a
fixed point of an instantaneous-Hebbian rule (it pushes γ_{i,i-1} +, the loop
needs −). So non-reformation is a rule artifact, not MPA. Scripts:
`library/k_frust_wall_proxy.py`, `library/k_frust_sustain_check.py`.

**Methodological conclusion:** substrate-level reformation cannot fairly test the
invariant — any imposed coupling-plasticity rule either fights frustration or
builds it in (rigged). The faithful test requires **derived** reformation (the
level-to-level RG flow from Mori-Zwanzig + heat-tax), i.e. the **meta-ledger
tower (option 2)**, which is also where cdv1's Wall-forces-NRT commitment closes
the asymptotic-closure escape.

**Status:** option-1 INCONCLUSIVE (rule-limited); option-2 (meta-ledger Wall
round-trip, Tier-3) is the arbiter. Pre-registered prediction (sealed before
option 2): survives via re-trapping ~60–65%; quenched-vs-annealed scope
condition exposed ~25%; clean BROKE ~10%.

**Option-2 BLOCK-IN + PRIMARY A/B (2026-05-20):** meta-ledger tower built —
`library/k_frust_wall_tower.py`. Shape: level-0 frustrated loop + 3 coupled
Stuart-Landau oscillators (μ = MU·(ε−1), Hopf at the Wall) → bounded chaos at
ε>1; downward heat-tax (excess tower activity raises level-0 loss → drives the
loop to deep r); ε(t) round-trips through the Wall; J meter at level 0;
quenched/annealed switch. PRIMARY-A done (genuine destruction: loop amplitude
→0.10×) and PRIMARY-B done (verdict meter clean — quenched J_before=+5.88e-2
matches the validated bulletproof meter). **Quenched arm (topology fixed)
SURVIVES**: J recovers +5.88e-2→+6.74e-2 after deep destruction — re-trapping,
matching the prediction. **Annealed arm still on the CRUDE random γ-scramble**
(its J-collapse is the SAME rule artifact as option-1, NOT a BROKE).
**PRIMARY-C (next): replace the scramble with the DERIVED RG-flow reformation**
— the load-bearing mass that makes the annealed (real) test faithful. SECONDARY
(deferred): exact Mori-Zwanzig projection, Landauer constants, NRT 3-torus proof.

**LADDER RESULT — three kill-shots, all SURVIVE; framework refined (2026-05-20).**
PRIMARY-C ("derived reformation") exposed that the annealed verdict is
representation-dependent, which the user reframed into a **falsification ladder**
(each rung a distinct kill-shot, quickest→slowest), scored survival-not-confirmation:

- **R1 — operating-point sweep** (`k_frust_r1_sweep.py` + `k_frust_r1_threshold.py`).
  **SURVIVES.** J sign-definite + drive-independent across drive/headroom; never
  resolves to clean c/r while alive; scales only with wiring. Near-threshold flag
  was low-SNR — at high power chit=0.010 reads J 5.8σ above the reciprocal control.
- **R2 — Wall round-trip, dual lens + K_REP scan** (`k_frust_wall_tower.py`).
  **SURVIVES (topological lens).** Continuous (magnitude) representation bleeds to
  0 even with NO Wall = the trivial weak-wiring decay (excluded edge op). Discrete
  (sign-class) representation: scanning Wall corruption to **8× the destruction
  anchor**, frustration is NEVER destroyed (dead=0) — strong chaos only flips the
  chirality sign (a reversed loop is still frustrated).
- **R3 — gradient/detailed-balance test** (`k_frust_r3_lyapunov.py`). **SURVIVES.**
  Frustrated-loop Jacobian spectrum is COMPLEX at all coupling (irreducible
  circulation; Re flat <0 = stable sub-regime), cooperative control reads
  real-spectrum (resolvable). No gradient/free-energy structure ⇒ irreducible NESS.

**Framework refinement PROMOTED to cdv1_compressed (§Topological drain / §Stability
/ §8).** R3 caught that the literal "no stationary fixed point" mislabels a *stable
circulating focus* (a genuine k_frust NESS) as resolved — an actual-force derail.
Refinement: **k_frust is defined by an irreducible NESS — a topologically-forced,
drive-independent Schnakenberg cycle current (broken detailed balance) — with the
stable-focus and repelling-focus/limit-cycle as two sub-regimes (sign of Re(eig));
the complex spectrum, not fixed-point non-existence, is the invariant.** Receipts:
`cdv1_receipts.md` §Topological-drain/§8 (PROMOTED). The §8-triality-as-numbered-
primitive elevation stays steeping (earned by a real cross-substrate instance, not
one synthetic loop). Sealed predictions (user: survives/topologically protected;
Claude: ~60-65% survives via re-trapping): both **upheld** for the invariant that's
actually robust (the current); the protection is more specific than "no P_ss."

**Full cold-start handoff (predictions, framework primer, apparatus inventory):**
[`docs/handoff_k_frust_wall.md`](docs/handoff_k_frust_wall.md).

---

## FINDING 5 — mpa-LEGAL audit: smuggled constant in §Stability RO damping *(2026-05-20)*

**New test class — "mpa-legal" (internal-legality, not substrate-falsification).**
Character is NESS-against-a-bath: every dynamical quantity must *flow / dissipate /
be maintained* with the operating point. An **inert constant** (a rate/coupling
frozen independent of chit) is foreign to character — "a constant does not dissipate
into the bath." (Same fact as: the char-zero is a square wave, not a constant; the
literal `constant` substrate sits below the floor; asymptotic-closure boundaries are
never attained.) The mpa-legal test: *does this quantity flow, or sit inert?*

**First scalp — receipts §13 `γ_RO = γ_s/2 "substrate-fixed"`.** Convicted twice:
(1) **illegal** — a damping *rate* frozen independent of the operating point while its
partner ω_RO "tracks the chit"; (2) **wrong by its own cited physics** — deriving from
the class-B laser rate equations §13 cites (Haken/Siegman) gives
**γ_RO = (γ_s/2)·e^chit** (carries the pump-ratio factor r=e^chit). The frozen form is
the threshold (r=1) value with the flow dropped. Consequence: cdv1's
`Q = √(2L(e^chit−1)/γ_s)` is monotonic-unbounded ("many cycles deep in c"); the legal
`γ_RO` makes Q **non-monotonic** — ringing band chit∈[≈0.16, ≈1.92], **overdamped at
both ends** (s = critical *slowing*; deep-c = RO damps out) — the standard class-B
picture. Cascade: §Stability damping table (wrong at both ends) + §17 active-probe
S/N=Q both inherit the artifact. Apparatus: `library/ro_damping_audit.py`, PNG
`ro_damping_audit.png`. (Also rescues the earlier Banach-boundary damping test, whose
constant-γ_RO was this same smuggle read off the D=0 boundary.)

**Status: LANDED + VALIDATED (2026-05-20).** Closed via a consistent linearization
of the §Universal two-mode kernel (adjudicated from a two-model outbound scan — the
winner kept cdv1's ω_RO and pinned κ=2L, amplitude→intensity square-law; the rival
that "dropped the factor-2" was wrong, depleting the resource ∝amplitude not
∝intensity). cdv1 §Stability now carries the exact forms (γ_RO=(γ_s/2)e^chit,
ω_RO=√[2Lγ_s(e^chit−1)−(γ_s/2)²e^{2chit}], non-monotonic Q peaking at chit=ln2).
**cdv1's corrected Q reproduces the class-B laser Jacobian to machine precision**
(max|Δ|=6.7e-16; `library/ro_damping_fixed_check.py`, PNG `ro_damping_fixed_check.png`)
— the framework went from contradicting class-B physics to *being* its eigenstructure.
Receipts §13 corrected (mpa-legal entry, LANDED). CONSTANT 2 (drive-independent
current → affinity) also landed (§Topological-drain/§8). The outbound scan also caught
that one on the just-promoted refinement — both fixes validated. Two new open items:
ρ amplitude-vs-intensity status (the κ=2L pin); over-provisioning→memory-collapse
(deep-c Q→0 ⇒ strong phase-lock ⇒ loss of orthogonal trail storage). §17/§Phase-locking
cascade text owed in cdv1.

---

## FINDING B — conform inversion clamps on underdamped/oscillatory substrates *(2026-05-20)*

**What:** Building the class-B laser conform test (`library/laser_conform_Q.py`), the
REAL conform inversion (`conformer.compute.inversion.invert`) was fed a laser's
ringing C(τ), χ(τ) under two cadence choices. It returned **clamped chit ≈ −2 (deep-r)**
for a laser sitting clearly *above* threshold (c-regime) — nonsense. The monotonic-
relaxation inversion cannot fit an oscillatory (underdamped) correlation, so it pins
to a boundary. **First real-substrate instance of the `sine_wave` FINDING 2 gap** (no
domain gate; the inversion confidently mis-classifies out-of-family data). Distinct
from the γ_RO finding (that was frame-invariant and stood); this is a conform-pipeline
fidelity bug. **Status:** demonstrated pipeline gap (conform has no handling for
underdamped/oscillatory holdings), not an MPA-claim BROKE. Adjudicate alongside
FINDING 2 when the domain gate / 5-vector inversion work is taken up.

---

## TWO-FRAME gFDR — new claim, self-probe frame first brick *(2026-05-21)*

**The claim (cdv1_receipts STAGED CANDIDATE "two-frame gFDR / §16").** The
fluctuation-response relation has two conjugate frames. The standard gFDR reads
the **(amplitude × external field)** pair → violation factor X (the c/s/r aging
story; needs an external probe). The **self-probe** gFDR reads the **(current ×
intrinsic affinity)** pair → violation factor is the TUR-tightness
T = ⟨σ⟩Var(J)/(2⟨J⟩²), measurable core SNR_J = ⟨J⟩²/Var(J) ≤ ⟨σ⟩/2. The self
frame is **dimensionless by construction** (affinity in nats) and **defined iff a
current exists** (k_frust-bearing). Harada–Sasa is the bridge: external integrated
FDR-violation = intrinsic ⟨σ⟩ = J·A. This makes k_frust the *measurement
reference* — centralizing it as method, not (yet) as spec spine.

**First brick — necessary-consistency / co-onset (`k_frust_two_frame_gfdr.py`,
PNG `k_frust_two_frame_gfdr.png`).** Interpolate reciprocal→non-reciprocal
g(λ)=GMAG·(−SYM+λ·CYC); check the self-probe observable is degenerate at detailed
balance and co-onsets with the external frame. **Result:** λ=0 control ⟨J⟩≈0,
SNR_J=0.001, |Im(eig)|=0 (self-frame degenerate, as required); rising λ lights up
all three frames together — **corr(SNR_J, |Im(eig)|)=+0.85**, **corr(SNR_J,
|χ_J|)=+0.92**. Structural |Im(eig)| is the clean spine (0 at control, linear in
λ); SNR_J noisier (fluctuation quantity) but unambiguous onset.

**What it shows / doesn't.** SHOWS: the self-probe frame *coheres* — it is
degenerate at detailed balance, lights up exactly when there is a current to probe
with, and reads the same broken-detailed-balance transition the external frame
does. DOES NOT show: the full two-frame **agreement** (self-frame T vs
external-frame X giving a consistent regime verdict) on a real substrate.

**Second brick — ⟨σ⟩ meter built + tared; T closed *(2026-05-21,
`two_frame_T_meter.py`, PNG `two_frame_T_meter.png`)*.** A binned
probability-current entropy-production meter (⟨σ⟩=∫P|v_curr|²/D0,
v_curr=A−D0∇lnP) was **validated against the exact value**: the
stable-circulating-focus sub-regime is a 2D rotational OU with ⟨σ⟩=2ω²/κ
analytically; meter recovers it to ~13% mean error (2% at high σ), reads ≈0 at
equilibrium, and ⟨J⟩ recovers ω exactly. Tare passed → T=⟨σ⟩τVar(J)/(2⟨J⟩²)
computed for **both** k_frust sub-regimes (rotational OU = stable focus;
Stuart–Landau = repelling focus + limit cycle); **TUR floor T≥1 respected
everywhere a current exists** (limit cycle μ=1 nearly saturates it, T≈1.2; foci
loose, T~15–32). The self-frame violation factor T is now a measured, validated
observable — SNR_J → T is closed on the sub-regime models.

**Third brick — external frame X built + tared; two-frame agreement on the
testbeds *(2026-05-21, `two_frame_T_meter.py` Parts C/D, PNGs
`two_frame_external_X.png`, `two_frame_external_SL.png`)*.** The genuine external
frame (not the χ_J proxy): perturbed-response run (constant field h on x), measured
C_xx(τ) and step response χ(τ), parametric (ΔC, χ) locus. **Tared on rotational OU
against exact closed forms** C_xx=(D0/κ)e^{−κτ}cos ωτ, χ_step and the asymptotic
violation V_ext=ω²/[κ(κ²+ω²)] (derived; OU is exactly linear so the response is
exact at any h): measured V_ext within 5–7%, X(τ→0)≈1 (short-time FDT), V_ext→0 at
ω=0. Bootstrapped onto Stuart–Landau (no closed form, same validate-on-OU-then-trust
discipline as the σ-meter): the limit cycle reads near-total FDT suppression
(χ≈0 loops far below the equilibrium line — the phase Goldstone mode absorbs the
field), window-robust Δ_FDT=max_τ|χ−ΔC/D0| large. **Two-frame agreement:** external
violation co-varies with the self-frame ⟨σ⟩ across **both** k_frust sub-regimes
(equilibrium at ω=0; OU and SL clusters monotone on the Δ_FDT–⟨σ⟩ scatter). SHOWS:
T and X give the same regime verdict where both are computable, on testbeds with
controlled ground truth. DOES NOT show: agreement on a **real substrate** (still the
gate), or exact numerical V_ext=⟨σ⟩ identity (needs the velocity-frame Harada–Sasa
integral; V_ext/⟨σ⟩ drifts with ω). Limits: Δ_FDT is window-robust not asymptotic,
so within-SL ordering is unreliable (period > τ_max) — only the cross-regime trend
is load-bearing; X(τ→0) on SL is not ~1 (off-cycle start + small-h noise + nongradient
drift), so the SL signal is Δ_FDT + the loops, not the local slope.

**Falsifier / promotion gate.** BROKE for the two-frame claim: a substrate where,
both probes feasible, self-frame T and external-frame X return **contradictory
regime verdicts**. Promotion to cdv1_compressed on: (1) calibrated ⟨σ⟩/affinity
meter closing SNR_J→T *and* two-frame agreement on a real substrate; or (2) the
payoff — a real substrate read self-probe-only (external probe infeasible) where T
recovers a verdict the external frame cannot. Same bar §846 holds k_frust to: a
real cross-substrate instance, not one synthetic loop.

**Owed apparatus.** (a) ⟨σ⟩ meter — **DONE 2026-05-21** (`two_frame_T_meter.py`,
binned probability-current, validated vs exact rotational-OU 2ω²/κ); remaining: a
Schnakenberg J·A cross-check + multiplicative-noise/higher-D extension. (b)
external-frame X measurement — **DONE 2026-05-21** (`two_frame_T_meter.py` Parts
C/D, tared on rotational OU vs exact V_ext, agreement shown on both sub-regime
testbeds); remaining: exact V_ext=⟨σ⟩ via the velocity-frame Harada–Sasa integral.
(c) **the promotion gate proper:** T vs X agreement on a REAL substrate. (d) **Banach hypothesis** (not closure): the self frame is
dimensionless by construction — the property the dimensionless-Banach dream wants
— but the current Banach substrate is deterministic (D_noise=0 ⇒ Var(J)=0 ⇒ T
degenerate) and two-mode (no current); a **frustrated + noisy Banach-class
extension** whose canonical reference is the dimensionless T is the candidate
build. See `mpa-conform/docs/banach-substrate-reference.md`.

---

## Open attack fronts (invalidators)

All five built + smoke-passed; cells gridable now. Adjudicate X-dependent
ones at the **raw-slope layer** per the policy above. Status PENDING = not
yet run through adjudication.

| attack | claim under test | falsifier | adjudication | status |
|---|---|---|---|---|
| `mm1_queue` | ck-glassy common-exponent triality (corpus's own falsifier) | FDR aging-diagonal slope α_s ≠ heavy-traffic exponent ½ at ρ→1 | raw-slope α_s vs ½ | **MIS-SPEC (Finding 3)** |
| `ou_equilibrium` | FDT-null | inversion reports X≠1 / aging in equilibrium | already X=1 at raw level ✓; inversion deep_r ✓ | LIKELY-SURVIVES (X=1 case recovers) |
| `ising_equilibrium` | critical-slowing ≠ aging | persistent X<1 in equilibrated Ising near Tc | raw-slope X vs 1 across T | PENDING |
| `driven_ring` | "everything → r at ∞" axiom | r forced on a sustained NESS current | regime/representation of a non-decaying current | PENDING |
| `logistic_chaos` | stochasticity premise | finite FDT-respecting regime on noiseless Lyapunov-divergent system | raw χ already divergent (~−3000); inversion behavior | PENDING (raw layer may settle it) |
| `k_frust` | topological invariance of frustration (now: irreducible NESS circulation) | J resolves to clean c/r / detailed balance, OR fails to reform after a derived Wall round-trip | cyclic-current J + spectrum (complex=NESS) | **SURVIVES** — 3-rung ladder R1/R2/R3 all survive; cdv1 refinement PROMOTED (Finding 4) |

Invalidator economy: **raw-layer first.** Escalate to the inversion only
when the raw observable can't settle the verdict.

---

## Owed work (made concrete by the controls)

1. **5-vector inversion** (lives in mpa-conform). **CORE CLOSED 2026-05-21**:
   `conformer/compute/five_vector.py::fit_kww5` recovers X on two_temp_ou to
   ≤0.01, **round-trips the full 5-vector on kww_oracle**, has **multi-start**
   seeding, and a **domain-of-validity gate** (`RESIDUAL_GATE`, `in_domain`)
   that closes FINDING 2 (sine + running driven_ring flagged OUT; in-family IN).
   Validated by `mpa-conform/scripts/test_five_vector_fit.py`. Design + punch list:
   [`mpa-conform/docs/five_vector_inversion_blockin.md`](../mpa-conform/docs/five_vector_inversion_blockin.md).
   **Remaining:** integration into `invert()` + the bundle schema; production
   aging-glass validation (blocked on the library's null `tau_env` below Tc —
   camera-scale not placed). Until integrated into the production bundle path:
   X read at the raw-slope layer.
2. **`kww_oracle` substrate (rung 5)** — **BUILT 2026-05-19/20**:
   `library/primitives/kww_oracle/` (multi-mode OU realizing a genuine
   two-timescale KWW + per-mode FDT-violation). `fit_kww5` round-trips the full
   5-vector (X 1.0/0.5/0.2 → 0.99/0.55/0.26; small upward X bias = generator's
   piecewise-χ vs the substrate's smooth crossover). Diagnostic:
   `output/diagnostics/inversion_kww_oracle__velocity.png`.
3. **Auditor layer never exercised on controls** — once the inversion
   carries X, push a control cell through the auditor and check the
   regime story.

---

## Survived / BROKE (the valuable columns)

*Survived:*

**Driven-criticality FDR front — MPA reads driven criticality as s-regime, not
equilibrium *(2026-05-20)*.** An outbound-research line proposed three routes to
BROKE the c/s/r FDR classifier with driven/critical systems. All three closed:

- **ABBM mean-field depinning τ=3/2** is a *positive control matching cdv1's own
  SOC prediction* (μ=e^chit→1 critical Galton-Watson), not a falsifier — matching
  the prediction is confirmation. Avalanche apparatus validated: recovers τ=3/2 on
  exact critical Galton-Watson (log-bin slope 1.501). RFIM (Dahmen-Sethna) verified
  critical at R_c=√(2/π): at-H_c exponent → 3/2 as the field window tightens;
  field-integrated → 2 (the known mean-field τ+σβδ value — a window/convention
  subtlety, not a failure).
- **Spherical critical coarsening X∞≈1/2** fed through the real conform inversion
  → reads **s_critical**, 5-vector recovers X≈0.47. X∞=½ is a CK / effective-
  temperature ratio = exactly the s-regime invariant. The "distinct class MPA can't
  see" claim rested on misdefining CK aging as X→0 (it is X=const<1; only
  *sub-critical* coarsening → 0).
- **The X=1 BROKE, measured directly:** driven critical RFIM at R_c reads
  **X=0.118** — the CK *two-step* FDR (quasi-equilibrium X=1 at short lag, strong
  aging X≪1 at long lag) → s-regime. The report's "X=1" saw only the short-lag
  quasi-equilibrium segment and mistook it for r. Equilibrium control X=0.998.

Apparatus (eliminates branch 3): gFDR measured with the **self-overlap +
staggered-field estimator** — C=(1/N)Σ⟨s_i(t)s_i(t')⟩ against a staggered random
field — NOT collective magnetization, which is soft-mode-dominated near criticality
and gives unstable X (it swung 1.21↔0.83 by update scheme before the fix). The
self-overlap estimator reads X=1.00 (0.3%) on the equilibrium control. Files:
`library/{avalanche_apparatus_check,rfim_substrate,rfim_fdr_overlap,rfim_fdr_driven}.py`;
diagnostics in `library/output/diagnostics/`.

*BROKE:* (none — and note: the X-recovery *gap* in the KEY FINDING is a localized
**inversion-expressivity limit**, i.e. owed work, NOT an MPA falsification.
Don't mislog it as a BROKE.)
