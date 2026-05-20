# levy_flight — Lévy flight (heavy-tailed CTRW)

**Domain:** Anomalous diffusion / Lévy stable processes
**Reference:** AnDi Challenge / Seckler et al. 2024 (CC-BY).
**Implementation:** Self-contained symmetric α-stable jump sampler
(Chambers–Mallows–Stuck).

x(t+1) = x(t) + S_α   where S_α ~ symmetric α-stable, scale 1.

Operating axis: tail exponent α ∈ {1.0, 1.3, 1.6, 1.9, 2.0}.

| α    | regime | gt |
|------|--------|----|
| 1.0  | Cauchy (extreme heavy tails) | c |
| 1.3  | strong heavy tails | s |
| 1.6  | moderate heavy tails | k |
| 1.9  | nearly Gaussian | r |
| 2.0  | Gaussian limit | r |

## ẋ choices

`velocity`, `position-relative`.

## τ_env

Scale-free; τ_env_analytic = 100 step reference. The operating axis
(α) is the substrate-conditional control, not τ_env.
