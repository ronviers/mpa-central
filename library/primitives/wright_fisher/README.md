# wright_fisher — Two-allele Wright-Fisher population dynamics

**Domain:** Population genetics / discrete demographic noise
**References:** Dryad doi:10.5061/dryad.wdbrv162z (CC0); Zenodo 18001835.
**Implementation:** Self-contained two-allele Wright-Fisher with selection.

Population N=1000 haploid individuals. Each generation, allele A
frequency p_t+1 ~ Binomial(N, q(p_t)) / N where
q(p) = (1+s)p / [(1+s)p + (1-p)] (selection coefficient s).

## Operating points

s ∈ {−0.05, −0.01, 0.0, 0.01, 0.05}.

| s     | regime               | gt |
|-------|----------------------|----|
| −0.05 | A drives to extinction | r |
| −0.01 | weak negative selection | s |
| 0.0   | neutral drift          | k |
| 0.01  | weak positive selection | s |
| 0.05  | A drives to fixation   | c |

## ẋ choices

- `frequency-velocity`  — Δp(t) = p(t) − p(t−1).
- `frequency-relative`  — Δp(t) = p(t) − p(t_snap).

## τ_env

τ_drift ≈ N for neutral; with selection τ ≈ 1/(N·s²) capped to N.
