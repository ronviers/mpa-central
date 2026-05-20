# square_wave — CONTROL substrate (the character zero)

**Role:** Calibration reference, not coverage and not (only) an
invalidator. The square wave is the **constant function of character
space** — it has dynamics (so it clears the domain floor the constant
fails), but its character is perfectly featureless and non-evolving:
the same flip forever, no aging, no timescale distribution, no FDT
structure that goes anywhere.

**No dataset.** Pure construction.

## Two jobs

1. **Tare / character zero.** The pipeline should map a phase-randomized
   square-wave ensemble to a single, stable, featureless character
   point. That point *defines* "no character."
2. **Resolution floor.** Whatever spread the pipeline reports back —
   across τ-windows, operating points (period P), and realizations — is
   its own noise floor in character space. You cannot call any
   invalidator's deviation a falsification if it is smaller than this
   spread. The square wave measures the smallest character-difference
   the apparatus can resolve.

## Why phase-randomized

Each replica gets an independent uniform random phase φ ∈ [0, P). A
fixed-phase deterministic square wave is **not** ensemble-trivial — its
rigid periodicity leaks structure that reads as character. Random phase
makes the ensemble phase-stationary, collapsing it to a single
character point.

## Analytic ground truth

Phase-averaged autocorrelation of a ±1 square wave of period P is the
**triangular wave**:

```
C(τ) = 1 - 4·|((τ + P/2) mod P) - P/2| / P     ∈ [-1, +1], period P
```

C(0)=1, C(P/2)=−1, C(P)=1. It oscillates forever — never relaxes to r.
That non-decay is the signature of "no dissipation": the square wave is
driven, not relaxing. The grinder's measured C must reproduce this
triangle.

## Operating points

Period P ∈ {10, 30, 100, 300, 1000} (step units). Character should be
**P-invariant** after τ_env rescaling (a square wave is a square wave;
P only rescales time). If the recovered character moves with P, that is
pipeline sensitivity to a parameter that must not matter.

## ẋ choices

`velocity` (Δx per step — the flip spikes), `position-relative`
(x(t) − x(snap)). Perturbation is a small phase shift h_field (steps),
so the perturbed branch's flips land slightly off the unperturbed ones.

## τ_env

τ_env = P (the period). No relaxation time exists; the period is the
only timescale, and the grid spans a few periods.
