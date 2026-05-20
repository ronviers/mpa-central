# fbm — Fractional Brownian Motion

**Domain:** Anomalous diffusion / single-particle stochastic processes
**Reference:** AnDi-datasets (CC-BY); Seckler et al. 2024
**Implementation:** Self-contained Davies-Harte fBM generator.

Operating axis: Hurst exponent H ∈ {0.2, 0.35, 0.5, 0.65, 0.85}.
H < 0.5: anti-persistent / sub-diffusive.
H = 0.5: standard Brownian.
H > 0.5: persistent / super-diffusive.

| H    | regime | gt |
|------|--------|----|
| 0.2  | strongly anti-persistent | r |
| 0.35 | weakly anti-persistent | r |
| 0.5  | Brownian | k |
| 0.65 | weakly persistent | s |
| 0.85 | strongly persistent | c |

## ẋ choices

`velocity`, `position-relative`.

## τ_env

fBM is scale-free; τ_env_analytic = fixed reference (100 steps), letting
the operating-point axis explore the regime-walk through the integrated
autocorrelation rather than through a substrate-set timescale.
