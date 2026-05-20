# sk — Sherrington–Kirkpatrick mean-field spin glass

**Domain:** Spin systems (mean-field spin glass)
**Reference dataset:** Zenodo [4318983](https://zenodo.org/records/4318983) (CC-BY 4.0)
**Implementation:** Self-contained Glauber MC simulator on N=100 spins.

Beyond mpc-glass's 3D Edwards–Anderson model: SK is the canonical
mean-field spin glass ("the hydrogen atom of spin-glass theory").
All-to-all couplings J_ij ~ N(0, 1/√N) with frozen disorder per replica.

## Operating points

T ∈ {0.4, 0.7, 1.0, 1.3, 1.6}; Tc = 1.0.

| T   | regime | gt |
|-----|--------|----|
| 0.4 | deeply frozen, aging | c |
| 0.7 | aging, RSB | s |
| 1.0 | critical | k |
| 1.3 | paramagnetic | r |
| 1.6 | high-T paramagnetic | r |

## ẋ choices

`spin-flip`, `spin-relative`.

## τ_env

`(|T - Tc| + ε)^(-zν)` with zν = 4 (mean-field). Below Tc → fallback grid.
