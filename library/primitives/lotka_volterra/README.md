# lotka_volterra — Stochastic Lotka-Volterra predator-prey

**Domain:** Ecological dynamics / coupled population stochastics
**Reference:** standard SLV / chemical-master-equation literature.
**Implementation:** Self-contained tau-leap stochastic Lotka-Volterra.

Per step, expected counts:
    Δprey = α·X − β·X·Y
    Δpred = δ·X·Y − γ·Y
Poisson draws per reaction channel. State X (prey), Y (predator).

## Operating points

Prey reproduction rate α ∈ {0.5, 0.8, 1.0, 1.2, 1.6} with β=γ=δ=1.0.

| α   | regime          | gt |
|-----|-----------------|----|
| 0.5 | predator wins → extinction | r |
| 0.8 | damped oscillations | s |
| 1.0 | sustained cycles | k |
| 1.2 | strong cycles | s |
| 1.6 | predator can't keep up → blow-up bursts | c |

## ẋ choices

- `pop-velocity`   — (Δprey, Δpred) per step.
- `pop-relative`   — (X-X_snap, Y-Y_snap).

## τ_env

Linearized cycle period 2π/√(α·γ) capped to 5000.
