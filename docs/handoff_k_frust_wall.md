# Handoff — k_frust topological-invariance falsification (Wall round-trip)

**Written 2026-05-20.** This document lets a cold session pick up the k_frust
falsification campaign exactly where it paused: an option-2 meta-ledger-tower
block-in with PRIMARY A/B refined, **PRIMARY-C (derived reformation) is the next
move.** It also gets you up to speed on the cdv1 framework being tested.

---

## 0. TL;DR (read this, then §6 for predictions and §10 for where to start)

- **What we're attacking:** cdv1/v9's claim that `k_frust` (frustration) is a
  **topological invariant** of the coupling graph — invariant under observer
  scale and under the framework's flow; a frustrated loop "never resolves into a
  clean c or r" and is "not resolvable by D."
- **The strong test (user's design):** drive a frustrated loop *through the
  Complexity Wall* (ε→1, into forced NRT chaos), bring it back, and ask whether
  the frustration **reforms**. Going negative / to r is *not enough* — that's a
  vertex-level op and can't falsify a subgraph-level invariant (§5 type argument).
- **STATE — CAMPAIGN SURVIVED (2026-05-20).** PRIMARY-C exposed that the annealed
  verdict is *representation-dependent*; the user reframed that into a
  **falsification ladder** (R1 operating sweep, R2 Wall round-trip dual-lens, R3
  gradient/detailed-balance), each a distinct kill-shot, all **SURVIVE**. The
  campaign produced a **framework refinement now PROMOTED** to cdv1_compressed:
  *k_frust is defined by an irreducible NESS — a topologically-forced,
  drive-independent Schnakenberg cycle current (broken detailed balance) — with
  stable-focus and repelling-focus/limit-cycle as two sub-regimes; the complex
  spectrum, not fixed-point non-existence, is the invariant.* Justification in
  [`cdv1_receipts.md`](../../mpa-atlas/framework/cdv1_receipts.md)
  §Topological-drain/§8. See §10 for what's still owed.
- **Entry point of record:** [`../FALSIFICATION.md`](../FALSIFICATION.md)
  Finding 4 (LADDER RESULT) + the `k_frust` attack-front row. This handoff expands
  the framework primer (§3) and the campaign's history; §10 is the resume point.

---

## 1. Get oriented (read order)

1. [`../FALSIFICATION.md`](../FALSIFICATION.md) — the invalidation program's
   session entry point. Read the layering (three-way verdict, positive-control
   ladder) and Findings 3–4.
2. This handoff §3–§5 (framework primer + the claims under test).
3. [`H:/mpa-atlas/framework/v9_compressed.md`](../../mpa-atlas/framework/v9_compressed.md)
   — structural source of truth (operator algebra, capacity, FDR signatures,
   Compression Axiom). §Scale-relativity, §Subgraph (k_frust), §Compression
   Axiom are the load-bearing sections for this test.
4. [`H:/mpa-atlas/framework/cdv1_compressed.md`](../../mpa-atlas/framework/cdv1_compressed.md)
   — Character projection (the dynamics). §Topological drain, §Stability
   (Wall-forces-NRT), §Heat-tax tower, §gFDR signatures are the ones you need.
5. **Discipline:** [`H:/mpa-atlas/CLAUDE.md`](../../mpa-atlas/CLAUDE.md) (thin-RFC),
   and the user-memory note that a **NaN is a falsification tripwire** (§9 here).

---

## 2. The working relationship (how this session ran — keep it)

- **Single-move, PNG-driven:** ship one move + one inspectable artifact, look at
  it together, decide the next move from what's on screen. Resist multi-step
  plans and option menus.
- **Falsification over coverage:** lead with "what would break this." An
  *invalidator* surviving is a result you score; a *control* can only confirm the
  apparatus (it cannot break the framework). Do not drift into running controls
  and calling it progress — the user will (rightly) call it out.
- **Direct pushback wanted.** Push back with specifics. The user self-flags
  sunk costs; when they redirect, flag concerns once then commit.
- **Block-in discipline:** capture the complete *silhouette* first (all
  load-bearing masses present + runnable), then refine PRIMARY (masses that
  change the outline), then SECONDARY. Do not get sidetracked by anything that
  doesn't change the silhouette.

---

## 3. cdv1 framework primer (the target, in one screen)

cdv1 ("MPA-Character") is the continuous-physics dynamics on top of v9's discrete
structure. Substrate-neutral; applies to glass, QEC, neural, behavioral, etc.

- **chit = ln(G₀/L)** — the central unit. G₀ = maintenance budget (gain), L =
  decay (loss). chit > 0 → **c** (committed, sustained); chit → 0⁺ → **s**
  (suspended / near-threshold, critical); chit < 0 → **r** (reset / collapsed).
- **Universal two-mode kernel:** ∂ρ_A/∂t = (G₀−L)ρ_A − γ_AB ρ_A ρ_B + 𝒟[…].
  γ_AB = signed shear (cooperative <0 / orthogonal ≈0 / conflicting >0).
- **gFDR signatures** (fluctuation-dissipation, χ vs C plane): c → X_c=0
  (suppressed); s → aging-diagonal slope α_s and plateau P_s (Cugliandolo–Kurchan);
  r → X_r=1 (unit-slope FDR); **k_frust → transient NEGATIVE response N_f**.
- **k_frust (the target):** a cycle of ≥3 modes with obstructive (non-reciprocal /
  cyclic) shear. **No stationary P_ss**, an attracting limit cycle, a
  drive-independent **Schnakenberg cyclic current**, no Lyapunov function. v9:
  "topological invariant of the coupling graph… not resolvable by D… does not
  migrate" under τ_obs. This is the claim under test.
- **Compression Axiom / heat-tax tower:** ledgers track substrate; meta-ledgers
  track ledgers. The level-to-level map contracts at rate **ε = ‖𝒞‖ < 1**
  (derived via Mori–Zwanzig projection + heat-tax substitution). **Complexity
  Wall at ε→1**: the tower diverges. cdv1's **Wall-forces-NRT chain** asserts
  meta-ledger chaos is *forced* past the Wall (Cobham wait → DDE Hopf per ascent →
  3-torus → Newhouse–Ruelle–Takens chaos at N≥3 ascents).
- **Scale-relativity:** τ_obs is the observer "camera." Vertex labels (c/s/r)
  **migrate** with τ_obs; k_frust is claimed **invariant** (topological).
- **Asymptotic closure:** every framework-prediction observable lives in an
  **open** interval; boundaries 0/1/∞ are never attained at finite operating
  points. ⇒ **a NaN in the apparatus is never normal** (see §9).

---

## 4. The specific claims under test

1. **(weak) τ_obs invariance:** sweeping the observer kernel migrates vertex
   labels but not k_frust; a frustrated loop never reads clean c/r at any τ_obs.
2. **(strong, user's framing) Wall survival:** drive the frustrated loop through
   the Complexity Wall (ε→1) into forced NRT chaos and back; the topological
   invariant should **reform**. If it does not, the topological-protection
   pillar — and a core MPA cross-field contribution — is falsified.

The strong test pins the framework on its **own** Wall-forces-NRT commitment,
which closes the asymptotic-closure escape ("ε=1 is unreachable"): if post-Wall
chaos is *forced and real*, the round trip is in-domain.

---

## 5. Test design — the two non-negotiables

**Type argument (why "to r" isn't enough):** you cannot falsify a *subgraph-level*
invariant with a *vertex-level* operation. Pushing a vertex negative or to r
changes **labels**, not **wiring**. k_frust is the sign-product/non-reciprocity
of the loop — one type up. Only a structural-level operation (the Wall / chaos)
can threaten it.

**Quenched vs annealed (the crux, PRIMARY):**
- **Quenched** = wiring (γ) fixed. Survival is then near-trivial (the topology
  literally can't change → re-trapping). Confirms the claim but proves little.
- **Annealed** = wiring free to be scrambled by the chaos. Only this asks the
  real question: *does the same loop reform frustrated?* The structural twin of
  "to-r-is-not-enough": a quenched graph is a no-op at the structural level.

**The no-escape falsifier:** the frustrated loop reads a *clean, definite c or r*
at some operating point, OR the cyclic current J fails to reform after a
**derived** Wall round-trip. Mere *fading* of the negative signal does NOT count
(the framework can blame observer resolution).

**The branch-3 trap (why option-1 failed):** any *imposed* substrate-level
coupling-plasticity rule either fights frustration or builds it in — so it tests
the rule, not MPA. The reformation must be **derived** (the framework's own RG
flow). That is option 2, and it is the whole point of PRIMARY-C.

---

## 6. The sealed predictions (call-your-shot, recorded before the verdict)

**User's prediction / stance.** Frustration **should survive** the round trip
through chaos — it is topologically protected; bring it back and it remains. The
user holds this as one of MPA's most important potential cross-field
contributions ("reality depends on it"). The *through-the-Wall-and-back, not
just to-r* framing is the user's design contribution. **If it does not survive,
MPA is invalid.**

**Claude's prediction (sealed before option-2 ran).** It **survives — via
re-trapping**, not "topological invariants always survive": MPV-spin-glass
frustration is robust because it *forbids settling* — wherever chaos throws the
system, when ε returns below 1 the loop re-obstructs any stationary rest and the
cyclic current re-establishes. Confidence: **~60–65% clean survival; ~25% it
exposes a hidden quenched-vs-annealed scope condition** (survives only quenched,
forcing the spec to state a scope it currently doesn't); **~10% clean BROKE.**
The knife-edge / path to a real BROKE: does the **same loop** reform frustrated,
or does chaos produce generic frustration *elsewhere* while *this* loop's
invariant is lost?

*(Quenched arm of the option-2 block-in already came in SURVIVES, consistent with
both predictions — but the quenched case is the near-trivial one. The real
verdict awaits the derived-annealed test, PRIMARY-C.)*

---

## 7. What's been done this campaign (results)

**mm1_queue — MIS-SPECIFIED (Finding 3).** The corpus's flagship self-named
falsifier ("α_s = ½ heavy-traffic exponent") is a **category error**: ½ is the
reflected-BM time-scaling exponent (lives in C-decay timescale), α_s is the FDR
effective-temperature slope (lives in the χ-vs-C plane) — different planes. Also
window-limited (heavy-traffic relaxation ~(1−ρ)⁻² outruns the window). M/M/1 is
reversible → equilibrium FDT → X≈1 (measured slopes ~0.9, not ½). Not a BROKE;
falsifier needs reframing. Structural tension kept: cdv1 maps heavy-traffic M/M/1
into s-aging, but reversibility forces X=1 — the sharp version is the
`ising_equilibrium` test (still PENDING).

**Apparatus lesson (all X-reads):** a single linear FDR slope is biased *up* on
aging loci (validated on kww_oracle: prescribed X=0.2 reads 0.47 single-slope vs
0.26 with the segmented `fit_kww5`). Read X via the segmented/5-vector fit, never
a single slope. High-res X-recovery calibration runner exists:
`library/kww_calibration_run.py` (background; recovered-vs-prescribed curve;
does not touch canonical cells).

**k_frust meter — BULLETPROOF.** Minimal frustrated 3-cycle (antisymmetric/cyclic
γ, non-reciprocal → Schnakenberg cyclic current, no P_ss) vs matched control
(symmetric γ, reciprocal → detailed balance, no current). Same magnitude →
amplitude-matched. Meter = intrinsic cyclic current **J (chirality of
ρ-rotation), observer-independent**: frust **J=+5.87e-2±3.1e-3** vs control
**−1.55e-3±1.0e-3** (38×, sign-definite, 6 seeds). No NaN, no boundary-pinning.

**Option-1 (substrate chaos proxy) — INCONCLUSIVE (rule artifact).** Annealed via
a directional-Hebbian rule. Apparent J non-reformation, BUT the **sustain control
(plasticity on, NO chaos) showed the rule decays an existing frustration
(antisym 0.93→0.41)** — the frustrated state isn't a fixed point of an
instantaneous-Hebbian rule. So non-reformation is the rule, not MPA. ⇒ the
faithful test needs *derived* reformation ⇒ option 2.

**Option-2 (meta-ledger tower) — BLOCK-IN + PRIMARY A/B done.** See §8/§10.
Quenched arm **SURVIVES** (J +5.88e-2→+6.74e-2 after deep destruction, loop
amplitude →0.10×). Annealed arm still on the **crude** random γ-scramble (its
collapse is the option-1 artifact again — NOT a BROKE).

---

## 8. Apparatus inventory (`H:/mpa-central/library/`)

Run any with `python H:/mpa-central/library/<name>.py`. Diagnostics land in
`library/output/diagnostics/`. (Note: the shell CWD drifts; use absolute paths.)

| script | role | status |
|---|---|---|
| `k_frust_meter.py` | bulletproof J meter; matched frust/control loops | **canonical** |
| `k_frust_jcheck.py` | J robustness across seeds (38× separation) | canonical |
| `k_frust_wall_tower.py` | **option-2 meta-ledger tower; block-in + PRIMARY A/B** | **active — work here** |
| `k_frust_wall_proxy.py` | option-1 substrate proxy (rule-limited) | reference |
| `k_frust_sustain_check.py` | proves option-1 rule can't sustain frustration | reference |
| `k_frust_prototype.py` | first τ_obs-sweep prototype (ambiguous fade) | **superseded** by meter |
| `kww_calibration_run.py` | background X-recovery calibration (segmented fit) | tool |
| `diag_mm1_locus.py`, `diag_mm1_slopecheck.py` | mm1 FDR-locus + model-free slope | reference |
| `diag_kww_bend.py` | kww two-step bend / X fan-out | reference |

Key diagnostics PNG: `k_frust_wall_tower_blockin.png` (the current silhouette:
ε-trapezoid, tower ignition + L_eff, J quenched-survives / annealed-collapses).

**`k_frust_wall_tower.py` shape (the seven masses):** level-0 frustrated loop
(ρ, γ) + 3 coupled **Stuart–Landau** oscillators (μ = MU·(ε−1) → Hopf at the
Wall, bounded chaos at ε>1 via the cubic term, incommensurate ω = NRT route);
**downward heat-tax** (only *excess* tower activity above QUIET_FLOOR raises
level-0 loss L_eff → drives the loop to deep r); ε(t) trapezoid through the Wall;
J meter at level 0 (read in the *quiet* before/after phases — /r² spikes during
deep destruction, so destruction is confirmed separately via amplitude collapse);
the `annealed` switch. Verdict printed as J_before / J_after + rho destruction
ratio. PRIMARY/SECONDARY are marked inline in the docstring + comments.

---

## 9. Load-bearing disciplines (do not relearn these the hard way)

- **NaN = falsification tripwire (never fallback-fill).** A NaN/inf is either a
  bad test (almost always) or the §Asymptotic-closure falsifier (a boundary
  0/1/∞ attained). Halt and diagnose; never `np.nan`-return or `nan_to_num`.
  **Never hard-clip a state variable at 0** — that manufactures the excluded
  zero; use a spontaneous-emission floor (constant influx) + multiplicative noise
  that vanishes at ρ→0, so boundaries are approached, never attained. (This
  caught a real ρ→∞ blowup this session.) Memory:
  `feedback_nan_is_falsification_tripwire`.
- **Control-bracketing.** Before any verdict, prove the apparatus can honor known
  ground truth (the sustain control caught the option-1 rule artifact; the
  matched control gives the meter its 38× baseline).
- **Meter conditioning (lesson):** a *single* FDR slope collapses the regime
  story and is biased; read the *shape* (segmented/5-vector). The cyclic-current
  J via per-replica /r² is the validated meter but spikes when ρ→floor — read it
  only in quiet phases; confirm destruction via amplitude, not via J during the
  Wall. (Do not chase a single meter that's clean across a 100× amplitude swing —
  that was a rabbit hole.)
- **Don't over-process a diagnostic.** A cubic-derivative-of-the-locus normalized
  by origin-slope manufactured a fake "coherent divergence" (sign-flipping
  divisor). When something looks dramatic, check it's not a construction artifact.

---

## 10. PICK UP HERE — campaign SURVIVED; three threads still owed

The ladder (R1/R2/R3) closed the campaign as **SURVIVES** and promoted the
NESS-circulation refinement (see §0, FALSIFICATION.md Finding 4, and
`cdv1_receipts.md` §Topological-drain/§8). What a cold session should do next:

1. **VERIFY THE cdv1 PASTE LANDED.** The surgical edit to `cdv1_compressed.md`
   (§Topological drain, §Stability k_frust row, §Framework-primitives §8) was
   handed to the user to paste manually (framework edits are user-pasted here).
   Confirm the three spots now read in terms of *irreducible NESS circulation /
   broken detailed balance*, with stable-focus and limit-cycle as **sub-regimes**,
   and the old "no stationary fixed point" / "no P_ss" phrasing softened to "no
   *equilibrium* (detailed-balance) steady state." If not yet pasted, re-offer the
   edit (it's reconstructable from the receipts entry).

2. **§8-triality-as-numbered-PRIMITIVE — STILL STEEPING (do not promote yet).** The
   compressed edit makes the triality the *definitional core* of k_frust in place.
   Formally relisting it as a numbered framework primitive (alongside the five
   leading-order posits) is the steeper claim — earned by a **real cross-substrate
   instance** (glass/QEC/brain exhibiting a stable-focus vs limit-cycle k_frust
   sub-regime), NOT one synthetic loop. Watch for that instance; promote then.

3. **The N>3 knife-edge (Claude's sealed path-to-BROKE) is UNTESTED.** A single
   3-cycle has only one frustration loop, so "does the *same* loop reform vs does
   chaos make *generic* frustration elsewhere" (§6) is not representable. Testing
   it needs a larger graph (≥2 distinct cycles) where chaos could destroy one
   loop's chirality while seeding another. Separate move; only worth it if the
   cross-substrate instance (thread 2) motivates it.

**Apparatus (all canonical now):** `k_frust_r1_sweep.py` + `k_frust_r1_threshold.py`
(R1), `k_frust_wall_tower.py` (R2, dual-lens + K_REP scan), `k_frust_r3_lyapunov.py`
(R3, spectrum/detailed-balance). `k_frust_wall_proxy.py` / `k_frust_sustain_check.py`
(option-1) remain **reference** (the rule-artifact lesson). PNGs:
`k_frust_r1_sweep.png`, `k_frust_wall_tower_r2.png`, `k_frust_r3_lyapunov.png`.

**Sealed predictions — both UPHELD** for the invariant that's actually robust (the
current). The protection is more *specific* than "no P_ss": broken detailed balance,
which a stable focus can carry. Recorded as **Survived**, not confirmation drift.

---

## 11. Pointers

- Ledger / entry point: [`../FALSIFICATION.md`](../FALSIFICATION.md) (Findings 3–4,
  `k_frust` row).
- Framework: [`v9_compressed.md`](../../mpa-atlas/framework/v9_compressed.md),
  [`cdv1_compressed.md`](../../mpa-atlas/framework/cdv1_compressed.md)
  (cdv1_receipts.md is large — search it, don't read whole).
- Discipline: [`H:/mpa-atlas/CLAUDE.md`](../../mpa-atlas/CLAUDE.md) (thin-RFC),
  [`../CLAUDE.md`](../CLAUDE.md) (mpa-central session discipline).
- Memory (auto-loaded): `feedback_nan_is_falsification_tripwire`,
  `feedback_falsification_over_coverage`, `feedback_control_failure_is_fixable`,
  `feedback_single_move_design`.
