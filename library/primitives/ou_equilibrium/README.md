# ou_equilibrium — INVALIDATOR substrate

**Role:** Falsification target, not coverage. Ornstein–Uhlenbeck process
sampled in **exact thermal equilibrium**.

**No dataset.** Pure analytic construction — the whole point is that the
ground truth is known in closed form.

## The MPA prediction under test

For an equilibrium process the fluctuation–dissipation theorem holds
exactly:

```
C(t, t_w) = a^(t - t_w),     a = exp(-1/τ)        (stationary, TTI)
χ(t, t_w) = (1 - C) / T,     T_eff = 1 (our normalization)
X(t, t_w) = T · dχ/d(1-C) = 1   everywhere
```

The substrate is normalized to stationary variance 1, so T_eff = 1 and
the parametric χ-vs-(1−C) plot must be the straight line of slope 1 with
**X = 1 at every (τ, dt)**. There is no aging, no FDT violation, no
regime walk — the operating-point axis only changes the relaxation
time τ, never the regime.

## Falsifier

**MPA is invalidated here if any cell reports |X − 1| larger than a few
× SEM in steady state, or classifies any operating point as c/s/k
(aging) rather than the trivial FDT-respecting attractor.** A framework
that "detects" aging in equilibrium OU is manufacturing signal.

This is the cleanest invalidator in the battery: the answer is analytic,
so any deviation is unambiguous.

## Operating points

τ (relaxation time, step units) ∈ {1, 5, 20, 50, 100}. All equilibrium.
`tau_env_analytic = τ` is exact (not a placeholder).

## ẋ choices

`velocity`, `position-relative`.
