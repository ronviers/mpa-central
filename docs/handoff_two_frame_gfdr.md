# Handoff — two-frame gFDR program (continuation)

**Disposable baton.** Created 2026-05-21. Delete when the three next-step
directions are either done or abandoned. This is the *technical* continuation
handoff; the *conceptual/refactor* decision lives in
[`H:/mpa-atlas/framework/cdv1_character_reconception_handoff.md`](../../mpa-atlas/framework/cdv1_character_reconception_handoff.md).

## The claim (one paragraph)

gFDR has **two conjugate frames** for the fluctuation-response relation.
- **External frame**: (amplitude × external field $h$) → violation factor $X$
  (with $\alpha_s,P_s$ the aging observables). The standard c/s/r story; needs
  an external probe.
- **Self-probe frame**: (current $J$ × intrinsic affinity $A$) → the system's
  *own* topologically-forced circulation is the reference. Violation factor is
  the TUR-tightness $T=\langle\sigma\rangle\,\tau\,\mathrm{Var}(J)/(2\langle J\rangle^2)$,
  with measurable core $\mathrm{SNR}_J=\langle J\rangle^2/\mathrm{Var}(J)\le\langle\sigma\rangle/2$.
  **Dimensionless by construction** (affinity in nats); **defined iff a current
  exists** (k_frust-bearing). Harada–Sasa is the bridge: external integrated
  FDR-violation $=\langle\sigma\rangle=J\!\cdot\!A$. Effect: k_frust becomes the
  *measurement reference* — centralizing it as method, not (yet) as spec spine.

## Status (what's done, where it lives)

Staged in [`mpa-atlas/framework/cdv1_receipts.md`](../../mpa-atlas/framework/cdv1_receipts.md)
as a **STAGED CANDIDATE** (`### §gFDR / §16 — two-frame gFDR …`). NOT promoted to
`cdv1_compressed` (the peel round-trip is still open; this is method, not spine).
Ledger: [`FALSIFICATION.md`](../FALSIFICATION.md) §"TWO-FRAME gFDR".

- **Brick 1 — self-frame coheres + co-onsets** (`library/k_frust_two_frame_gfdr.py`,
  PNG `output/diagnostics/k_frust_two_frame_gfdr.png`). On the 3-mode synthetic
  loop, interpolating reciprocal→non-reciprocal: at detailed balance the self-frame
  is degenerate ($\langle J\rangle\approx0$, $\mathrm{SNR}_J\approx0$, $|\mathrm{Im(eig)}|=0$);
  as non-reciprocity rises, self-frame $\mathrm{SNR}_J$, structural $|\mathrm{Im(eig)}|$,
  and external-probe $\chi_J$ all onset together — corr 0.85 / 0.92.
- **Brick 2 — $\langle\sigma\rangle$ meter built + tared; $T$ closed**
  (`library/two_frame_T_meter.py`, PNG `output/diagnostics/two_frame_T_meter.png`).
  Binned probability-current meter $\langle\sigma\rangle=\int P|v_{\text{curr}}|^2/D_0$,
  $v_{\text{curr}}=A-D_0\nabla\ln P$. **Tared against the exact rotational-OU value
  $\langle\sigma\rangle=2\omega^2/\kappa$** (the stable-circulating-focus sub-regime):
  ~13% mean error (2% at high $\sigma$), $\approx0$ at equilibrium, $\langle J\rangle$
  recovers $\omega$. $T$ then computed for **both** k_frust sub-regimes (rotational
  OU = stable focus; Stuart–Landau = repelling focus + limit cycle); **TUR floor
  $T\ge1$ respected** everywhere a current exists ($\mu=1$ limit cycle nearly
  saturates, $T\approx1.2$; foci loose, $T\sim15$–$32$).
- **Brick 3 — external frame $X$ built + tared; two-frame agreement on the testbeds**
  (`two_frame_T_meter.py` Parts C/D, PNGs `two_frame_external_X.png`,
  `two_frame_external_SL.png`). Genuine external frame (perturbed step-response run,
  field $h$ on $x$): parametric $(\Delta C,\chi)$ locus. **Tared on rotational OU vs
  exact** $C_{xx}=(D_0/\kappa)e^{-\kappa\tau}\cos\omega\tau$, $\chi_{\text{step}}$, and
  $V_{ext}=\omega^2/[\kappa(\kappa^2+\omega^2)]$ — measured within 5–7%, $X(\tau\!\to\!0)\approx1$,
  $V_{ext}\!\to\!0$ at $\omega=0$. Bootstrapped onto Stuart–Landau (untared, same
  validate-on-OU discipline as the $\langle\sigma\rangle$ meter): limit cycle reads
  near-total FDT suppression ($\chi\approx0$ loops; the phase Goldstone mode absorbs
  the field). **Agreement:** external violation co-varies with self-frame
  $\langle\sigma\rangle$ across *both* k_frust sub-regimes (OU/SL clusters monotone on
  the $\Delta_{FDT}$–$\langle\sigma\rangle$ scatter). This is **direction (1) below,
  closed on the testbeds** — $T$ and $X$ give the same verdict where both are computable
  and ground truth is controlled.

## Honest caveats (do not lose these)

- The $\langle\sigma\rangle$ meter has a ~0.12 additive bias floor at equilibrium
  and ~13% error — fine for a tared first-cut, not production.
- Brick-2 testbeds are minimal *models* of the two sub-regimes, not real substrates.
- Brick 1's "external frame" used a constant-field current-response $\chi_J$ as a
  co-onset **proxy**, not the full $(\chi,C)$-plane $X$. **Superseded by Brick 3** —
  the genuine $(\chi,\Delta C)$ external frame is now built and tared.
- Brick-3 caveats: $V_{ext}=\langle\sigma\rangle$ holds only in *verdict/onset*, not
  numerically ($V_{ext}/\langle\sigma\rangle$ drifts with $\omega$; exact identity needs
  the velocity-frame Harada–Sasa integral). On SL, $\Delta_{FDT}$ is window-robust not
  asymptotic (period $>\tau_{\max}$), so only the *cross-regime* trend is load-bearing,
  not within-SL ordering; and $X(\tau\!\to\!0)$ on SL is not $\approx1$ (off-cycle start,
  small-$h$ noise, nongradient drift).
- Additive isotropic noise was used for clean entropy accounting; the original R1
  loop uses multiplicative noise. The qualitative co-onset held on the multiplicative
  apparatus; the EP meter is currently additive-noise only.

## The three next directions (concrete)

1. **Real external-frame $X$ on the same models** — **DONE 2026-05-21 (Brick 3
   above).** Built the perturbed-response run + $(\chi,\Delta C)$ locus in
   `two_frame_T_meter.py` Parts C/D, tared on rotational OU vs exact $V_{ext}$, showed
   $T$-vs-$X$ verdict agreement across both sub-regimes. Remaining sliver: exact
   $V_{ext}=\langle\sigma\rangle$ via the velocity-frame Harada–Sasa integral (owed,
   below). The gate now narrows to direction (2).
2. **Real substrate** (the actual promotion gate, biggest payoff/lift). Push a
   k_frust-bearing library cell through both frames. Constraint: the self-frame is
   defined iff a current exists, so pick a substrate with broken detailed balance /
   a sustained current (candidate: `driven_ring` invalidator, or a primitive with a
   NESS current — audit `library/primitives/` and `library/data/`). External $X$
   read at the raw-slope layer per FALSIFICATION.md adjudication policy (the 1-param
   inversion can't carry $X$; 5-vector owed). Verdict: do $T$ and $X$ agree?
3. **Frustrated + noisy Banach extension** (serves the dimensionless-Banach dream).
   The current Banach substrate
   ([`mpa-conform/docs/banach-substrate-reference.md`](../../mpa-conform/docs/banach-substrate-reference.md))
   is deterministic ($D_{\text{noise}}=0\Rightarrow\mathrm{Var}(J)=0\Rightarrow T$
   degenerate) and two-mode (no current). Build an $N\ge3$ obstructive-cycle,
   $D_{\text{noise}}>0$ Banach-class reference whose canonical quantity is the
   dimensionless $T$. This is hypothesis, not closure — flagged in both the receipts
   entry and FALSIFICATION.md.

## Owed refinements

- Schnakenberg $J\!\cdot\!A$ cross-check of the binned $\langle\sigma\rangle$ meter.
- Multiplicative-noise / higher-D entropy-production meter (current one is additive,
  2D).
- ~~Genuine external-frame $X$ (not the $\chi_J$ proxy).~~ **Done (Brick 3).**
- Exact $V_{ext}=\langle\sigma\rangle$ via the velocity-frame Harada–Sasa frequency
  integral (Brick 3 shows verdict/onset agreement, not numerical identity).

## Promotion gate (what earns promotion to cdv1_compressed)

Either: (1) calibrated $\langle\sigma\rangle\to T$ **and** $T$-vs-$X$ two-frame
agreement **on a real substrate**; or (2) the payoff instance — a real substrate
read **self-probe-only** (external probe infeasible) where $T$ recovers a verdict the
external frame cannot reach. Same bar §846 holds k_frust to: a real cross-substrate
instance, not a synthetic model. **Falsifier for the claim:** a substrate where, both
probes feasible, $T$ and $X$ give *contradictory* regime verdicts.

## Apparatus inventory + run commands

```
python H:/mpa-central/library/k_frust_two_frame_gfdr.py     # brick 1 (co-onset)
python H:/mpa-central/library/two_frame_T_meter.py          # bricks 2 + 3 (sigma meter + T; external X + agreement)
```
Both write PNGs to `library/output/diagnostics/`. Brick-1 reuses
`k_frust_r1_sweep.py` (`step`, `cyclic_J`, `CYC`, `SYM`). Bricks 2+3 are
self-contained in one script (rotational OU + Stuart–Landau + binned EP meter,
analytic $2\omega^2/\kappa$ tare = Parts A/B; external $(\chi,\Delta C)$ frame with
exact $V_{ext}$ tare + cross-regime agreement = Parts C/D). Writes
`two_frame_T_meter.png` (bricks 1–2), `two_frame_external_X.png` (OU external, tared),
`two_frame_external_SL.png` (SL external + agreement scatter).

All artifacts uncommitted as of 2026-05-21. The cdv1_compressed spine is untouched.
