# white_noise — CONTROL substrate (the dissipative floor)

**Role:** Calibration reference — the bottom rung of the *positive-control*
ladder, the simplest substrate that genuinely has bath coupling. Where
`square_wave` is the character zero (driven, no bath), white noise is
the **memoryless dissipative limit**: instantaneous decorrelation, the
trivial-`r` character.

**No dataset.** Pure construction.

## Analytic ground truth

x(t) = σ·ξ(t), ξ ~ N(0,1) fresh i.i.d. every step. Two-time correlation:

```
C(t, t_w) = ⟨x(t) x(t_w)⟩ = 0   for t > t_w   (memoryless)
```

So the measured C must sit at 0 within SEM for every lag. There is no
relaxation to track — decorrelation is instantaneous. Character: trivial
`r` everywhere.

## What it tests

1. The pipeline must read **C ≈ 0 / no structure** — it must not
   hallucinate a regime from a featureless stochastic signal.
2. **Amplitude is not regime.** The operating axis is σ
   ∈ {0.5, 1, 2, 5, 10}. Changing σ rescales magnitudes but must NOT
   induce a c→s→k→r walk. If the recovered character moves with σ, the
   pipeline is reading amplitude as regime.

## ẋ choices

`velocity` (Δx per step), `position-relative` (x(t) − x(snap)). Both are
differences of independent draws → also memoryless. Perturbation is a
DC bias h_field on the perturbed branch (CRN: same ξ).

## τ_env

Memoryless → no relaxation time. Fixed small reference (τ_env = 5) only
so the time grid is compact; the point is C should already be ~0 at the
first lag.
