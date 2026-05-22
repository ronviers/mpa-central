# Session handoff — 2026-05-21 (two-frame → laser/ring → substrate-inversion → five-vector → Reed-Muller → noisy-frustrated Banach)

**Disposable master baton for one long session.** Captures the whole arc and the
owed framework-landings. Companion batons it builds on:
[`handoff_two_frame_gfdr.md`](handoff_two_frame_gfdr.md) (technical) and
[`H:/mpa-atlas/framework/cdv1_character_reconception_handoff.md`](../../mpa-atlas/framework/cdv1_character_reconception_handoff.md)
(conceptual/decision). Delete when its owed items are landed or abandoned.

## The arc in one paragraph

Closed two-frame direction (1) (external X) on the OU/SL testbeds, then pushed both
frames onto **real substrates** (class-B laser, then the in-library `driven_ring` NESS).
That surfaced the session's spine finding: **the self-probe frame travels cleanly across
every substrate; the external X frame is substrate-bespoke** — so the self-probe is the
*native* reading. Chasing X's fragility upstream produced two things: (a) the
**substrate-inversion** insight — non-glass test viability is gated on aiming the τ_obs
camera, upstream of the chi-lookup and the five-vector; and (b) the realization that the
**five-vector inversion + its domain gate** is the principled X machine (now closed).
Then the **Reed-Muller closure test** resolved the RM/k_frust algebra, and the
**noisy-frustrated Banach** reference instanced the dimensionless dream. cdv1_compressed
spine was never touched.

## Findings (each: status · artifact · where recorded)

1. **Two-frame direction (1) closed on testbeds + real substrates.** External X built/tared
   (rotational OU exact; SL bootstrapped). Then **laser** (`two_frame_laser.py`) and
   **driven_ring** (`two_frame_driven_ring.py`) — real substrates, both gave a **closed
   self-frame** (TUR T≥1; ring has the *exact* ⟨σ⟩=J·A bridge the laser only approximated;
   T→1 TUR saturation). External frame agrees on *verdict* not magnitude, and is
   substrate-bespoke (laser magnitude-divergent; ring cos-observable drift-dominated →
   needs velocity Harada–Sasa). **Self-frame is the robust, traveling reading.**
   Recorded: FALSIFICATION.md §TWO-FRAME (bricks 2/3), `handoff_two_frame_gfdr.md`.
   PNGs: `two_frame_{T_meter,external_X,external_SL,laser,driven_ring}.png`.

2. **Substrate-inversion finding.** Non-glass character-test viability is gated on
   **τ_obs camera placement** (RFC-S §0.2/§1), *upstream* of the chi-convention lookup and
   the five-vector. glass=interior (X recoverable), brain=τ_obs→0 floor (C-decay below
   resolution), QEC=τ_obs→∞ (migrated to r) — all gt=s, only glass's camera is aimed.
   Artifact: `substrate_inversion_camera.py` / `.png`. Recorded: conform handoff §Reframe,
   memory `project_substrate_inversion_test_viability`.

3. **Five-vector inversion CLOSED.** `mpa-conform/conformer/compute/five_vector.py` gained
   multi-start + a **domain-of-validity gate** (`RESIDUAL_GATE`, `in_domain`). Validated
   (`mpa-conform/scripts/test_five_vector_fit.py`): two_temp_ou X≤0.01, kww_oracle full
   5-vector round-trip, sine_wave + running driven_ring **gated OUT**, r-glass IN.
   **FALSIFICATION FINDING 2 closed.** Remaining: integration into `invert()`+schema;
   aging-glass blocked on the library null-tau_env-below-Tc (a substrate-inversion gap).

4. **Reed-Muller closure test (Phase 3) — RESOLVED.** `rm_closure_test.py`: the ANF
   identity ¬x=x⊕1 holds via **K(·,⊤) with 1=⊤** — and that is **already v9's Boolean
   section** (M₂≅(𝔹,∧,∨,⊕,¬), K↔⊕, C↔∧, R↔¬). **RM is "the MPA way" because v9 already
   IS the deformed {⊕,∧,1} ring** — not new machinery. The reconception's **1↔G₀ is a
   category error** (G₀ is the drive, not an M₂ element); G₀'s real role is the
   *deformation coordinate* chit=ln(G₀/L). R↔¬ is a one-way (c→r) shadow, not a dynamical
   involution — R's irreversibility *is* the finite-D deformation. So "integrate RM" = a
   receipts/framing note, NOT a spine refactor → no interface disturbance.

5. **Two-frame operational-interface implications (additive, not breaking).** The
   self-frame is a new *optional* block (present iff a current exists). Gains: probe-free
   violation factor (extends inversion to unperturbable/observational substrates);
   **dimensionless-by-construction → sidesteps the chi-convention layer**; built-in
   cross-frame consistency check (T-vs-X verdict agreement); current-based regime
   discriminator. Deepest: **dimensionless T is a candidate *canonical* observable** (lives
   in canonical space with no translation field; X stays the substrate-conditional one).

6. **Noisy-frustrated Banach reference — INSTANCED (linear).** `banach_frustrated.py`:
   N=3 cyclic non-reciprocal OU (rock-paper-scissors), complex eigenpair = k_frust
   signature, topologically forced (DB unreachable without deleting edges). Carries a
   **dimensionless, noise-independent canonical quantity: the affinity A (nats)** and the
   spectral ratio ω/γ — flat to 0.4%/0.0% across a 20× noise sweep; TUR T≥1 holds.
   **Correction to the dream:** the canonical quantity is the **affinity A, not T** (T is
   loose, the bounded violation factor) — which *vindicates* cdv1 §k_frust drain
   ("drive-independence lives at the affinity ∮v/D"). The two-frame self-frame was the
   enabler the deterministic two-mode Banach lacked.

## Owed framework-landings (the "needs mention in the framework" list)

These are the disciplined-thin homes; land deliberately (thin-RFC: receipts, not casual
compressed thickening).

- **RM as the MPA way** — a **v9_receipts** note: v9 §Operators/§Boolean section IS the
  finite-D deformation of the {⊕,∧,1} (ANF) ring (⊕↔K, ∧↔C, 1↔⊤; G₀=deformation coord;
  1↔G₀ rejected). A cdv1_receipts cross-ref on the C/R operators. NOT a compressed rewrite.
- **Two-frame gFDR** — already a cdv1_receipts STAGED CANDIDATE; its operational-interface
  payoff (probe-free, dimensionless-canonical) should be noted there. Promotion to
  cdv1_compressed stays gated (verdict-agreement on real substrates landed; full
  T-vs-X + a real *topologically-forced* instance still owed).
- **Noisy-frustrated Banach reference** — extend
  `mpa-conform/docs/banach-substrate-reference.md` with the dimensionless-affinity instance
  (new Banach-CLASS object alongside the deterministic one: deterministic = c/s/r backbone;
  noisy-frustrated = k_frust/current sector, canonical quantity = affinity).
  **Ron's possibility worth recording:** the noisy-frustrated Banach / k_frust-as-seed
  could *derive* the reference substrates currently enumerated in the framework rather than
  list them (the ANF-deformation-generates-c/s/r idea). Hypothesis, gated — this is the
  spine-refactor question, do not act on conviction.
- **Five-vector / X-recovery** — DONE: thin clause in cdv1_compressed (s-regime FDR line) +
  cdv1_receipts note + FALSIFICATION FINDING 2 closed + conform handoff.

## Gates still standing (do not let them merge)

- **§846 k_frust promotion** needs a **real, topologically-forced** cross-substrate instance.
  Laser/ring are *drive-forced*; the noisy-frustrated Banach is *synthetic*. None qualify.
- **Spine refactor** (k_frust as cdv1 organizer) stays gated; the RM result shows it's a
  re-description (cheap, additive) not a rewrite — but the non-negotiable holds (keep
  α_s/P_s universality uncoupled from k_frust).
- **Order-of-operations:** conform/solvers bind to the operational *interface* (regimes,
  gFDR, canonical state, five-vector), not the narrative. RM/two-frame/banach are additive
  or re-descriptive → safe to land without destabilizing downstream.

## Artifact inventory (all in `library/`, PNGs in `library/output/diagnostics/`)

`two_frame_T_meter.py` · `two_frame_laser.py` · `two_frame_driven_ring.py` ·
`substrate_inversion_camera.py` · `rm_closure_test.py` · `banach_frustrated.py` ·
(conform) `conformer/compute/five_vector.py` + `scripts/test_five_vector_fit.py`.

## Conform handoff

Already updated this session (`mpa-conform/docs/next-session-handoff.md`): §Reframe
(substrate-inversion reorders the non-glass priorities behind camera placement) + the
five-vector "core closed" note. No further conform-handoff work owed from this session.
