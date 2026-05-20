# sine_wave — CONTROL substrate (pure-tone character zero)

**Role:** The smooth sibling of [`square_wave`](../square_wave/). Same
family — driven, deterministic, periodic, **no bath, no dissipation** —
but a single frequency instead of a fundamental-plus-odd-harmonics. Its
phase-averaged autocorrelation is therefore a clean **cosine**, not a
triangle.

**No dataset.** Pure construction.

## Analytic ground truth

x(t) = √2·sin(2π·(t + φ_r)/P),  φ_r ~ Uniform[0, P) per replica
(phase-randomized → phase-stationary ensemble; the √2 normalizes the
variance to 1 so C(0)=1, matching `square_wave`).

```
C(τ) = ⟨x(t) x(t+τ)⟩_φ = cos(2π·τ/P)        ∈ [-1, +1], period P
```

Smooth, analytic, oscillates forever — never relaxes to r (no dissipation).

## Why it's the sharp test

The cdv1 inversion loci are all **monotonic decays** (C falls from 1 to a
plateau or to 0). A cosine smoothly turns around and comes back up. So
this isolates the question: how far does a monotone-relaxation fit track
a signal that recurs? Expectation: the inversion follows the first
quarter-period (τ ∈ [0, P/4], where cos looks like a decay) and peels off
once the cosine turns up. Where it peels off, and whether it reports a
confident "relaxation regime" anyway, is the diagnostic.

Compared with `square_wave`: same C(0)=1 and same period, but triangle
(harmonics) vs cosine (pure tone). Differences between the two inversions
isolate the effect of harmonic content from the effect of periodicity.

## Operating points

Period P ∈ {10, 30, 100, 300, 1000} (step units), phase-randomized.
Character should be P-invariant after τ_env rescaling.

## ẋ choices

`velocity`, `position-relative`. Perturbation: small phase shift h_field
(steps).

## τ_env

τ_env = P (the period; the only timescale — no relaxation time exists).
