# voter — in-library substrate primitive

**Domain:** Network dynamics / opinion dynamics
**Reference dataset:** Mobilia 2023, "Voter model under time-fluctuating
influences" — Leeds repository [doi:10.5518/1311](https://archive.researchdata.leeds.ac.uk/1080/)
**License of reference dataset:** CC-BY 4.0
**Implementation:** Thin self-contained simulator (the deposited data is
pre-aggregated; the paper's Gillespie protocol is reproduced in
`measurements.py`).

## Operating-point axis

`nu` (switching rate of an external two-state bias field). Five points
log-spaced across the slow/fast crossover:

| ν     | regime                          | gt |
|-------|---------------------------------|----|
| 0.001 | slow-switching (polarised)      | s  |
| 0.01  | mid-slow                        | s  |
| 0.1   | near crossover                  | k  |
| 1.0   | mid-fast                        | r  |
| 10.0  | fast-switching (mean-field avg) | r  |

`gt` is the substrate-conditional regime letter per RULES §10.

## ẋ choices

- `opinion-flip` — Δs_i(t) = s_i(t) − s_i(t−1) ∈ {−2, 0, +2}. Per-step
  velocity-analogue. EMA accumulates in phase A.
- `opinion-relative` — Δs_i(t) = s_i(t) − s_i(t_snap). Snapshot-relative;
  EMA accumulates from t_snap = t_w + 5·τ_max (kernel warmup).

Mirrors mpc-glass's spin-flip / spin-relative pair, glass-vocabulary in
opinion form per RULES §10.

## Population and update

- `N = 200` agents (mean-field; fully connected). All-to-all coupling
  reproduces the Mobilia setup's high-density limit.
- One sweep = `N` random single-agent updates.
- An external two-state bias `h_ext(t) ∈ {+h, −h}` flips with rate ν per
  unit time. During a sweep with bias state σ_ext, each updated agent
  adopts its target with the bias-tilted majority rule.

## What "h_field" means here

`h_field` controls the perturbed branch's effective bias amplitude.
Per the paired-protocol convention, the unperturbed branch sees the
switching bias only (mean zero over long times); the perturbed branch
sees the switching bias + a steady additive bias of magnitude `h_field`.
chi is the linear response of mean opinion to this steady extra bias.

## τ_env

Slow-switching regime (small ν) dominates the long-time scale:
`τ_env ≈ 1/ν` in mean-field. The grid uses `τ_env_analytic = 1/ν`,
fallback (None → fixed grid) for ν above the cap.

## Output

Cells land at
`H:/mpa-central/library/data/voter/voter__nu<X>__<xdot>.json`,
matching LIBRARY_SPEC v1.0 with SEM populated (the simulator emits
per-replica values internally).

## Run

```powershell
python H:/mpa-central/library/primitives/voter/grind.py --smoke
python H:/mpa-central/library/primitives/voter/grind.py
```

Smoke mode: tiny budgets, no writes; verifies imports and shape.
Production mode: full 5×2 = 10 cells, 256 realisations each.

## Caveats

- Mean-field topology is a coarse model of Mobilia 2023's stochastic
  block-model variants. A future session can swap the all-to-all
  adjacency for a sparse SBM without changing the cell schema.
- Two-state switching field is the simplest noise process; richer
  spectra (Lévy, telegraphic) are open extensions.
