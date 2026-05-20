# abp — Active Brownian Particles

**Domain:** Active matter / self-propelled colloids
**Reference:** amep (BSD-3); also Janus-motor literature (Quantifying
Photochemical Propulsion, ACS Figshare).
**Implementation:** Self-contained single-particle 2D ABP simulator.

Overdamped Langevin in 2D with rotational diffusion:
    dr = v0·n̂(θ) dt + √(2·D_t·dt) ξ_r
    dθ = √(2·D_r·dt) ξ_θ
Operating axis: Péclet number Pe = v0 / sqrt(D_t·D_r) → translational
ballistic vs diffusive regime crossover.

## Operating points

Pe ∈ {0, 1, 10, 50, 200}, with D_r = 1, D_t = 1.

| Pe  | regime | gt |
|-----|--------|----|
| 0   | passive Brownian | r |
| 1   | weakly active | r |
| 10  | active, mid-Pe | s |
| 50  | active, ballistic-dominated | s |
| 200 | strongly active | c |

## ẋ choices

`velocity`, `position-relative`.

## τ_env

Persistence time τ_r = 1/D_r (fixed = 1.0 here; the regime walk is
along Pe, not τ_r).
