# heston — Heston stochastic volatility with jumps

**Domain:** Financial / econometric (stochastic regime switching)
**Reference:** Kaggle Heston-Jump dataset (MIT); fsynth library.
**Implementation:** Self-contained Euler-Maruyama Heston SDE with
Poisson-jump augmentation.

```
dS/S = (μ − λ·κ_J)·dt + √V·dW₁ + (e^J − 1)·dN
dV   = κ·(θ − V)·dt + ξ·√V·dW₂   (Cox-Ingersoll-Ross variance)
ρ = corr(dW₁, dW₂)
```

## Operating points

Market regime, encoded as (μ, κ, θ, ξ, ρ, λ, σ_J):

| regime         | gt | flavor |
|---------------|----|--------|
| bull           | c  | steady drift, low vol |
| mid            | s  | moderate vol |
| bear           | s  | negative drift, mid vol |
| crisis-low     | k  | low-frequency big jumps |
| crisis-high    | r  | high-frequency violent jumps |

## ẋ choices

- `log-return`     — Δlog(S_t).
- `log-relative`   — log(S_t) − log(S_{t_snap}).

## τ_env

Variance mean-reversion timescale 1/κ (in step units).
