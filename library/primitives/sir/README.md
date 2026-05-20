# sir — Stochastic SIR epidemic

**Domain:** Network dynamics / epidemic compartment models
**References:** CDC `cfa-gam-rt` (public domain); Figshare Zika
Trajectories (Figshare Standard).
**Implementation:** Self-contained tau-leap stochastic SIR.

Population N=10000. Each step: S→I draws Binomial(S, 1−exp(−β·I/N)),
I→R draws Binomial(I, 1−exp(−γ)).

## Operating points

R0 = β/γ, with γ = 0.1 fixed.

| R0  | regime                     | gt |
|-----|----------------------------|----|
| 0.5 | sub-critical, fast extinction | r |
| 0.9 | sub-critical, slow extinction | s |
| 1.0 | critical                   | k |
| 1.5 | super-critical, outbreak   | s |
| 3.0 | super-critical, fast burnout | c |

## ẋ choices

- `incidence`        — Δ(new infected this step) (per-step)
- `cumulative-relative` — cumulative-incidence − cumulative(t_snap)

## τ_env

1 / |R0 − 1| (critical slowing) capped at large values, fallback at R0=1.
