# two_temp_ou — CONTROL substrate (rung 4: known FDT violation)

**Role:** Positive control — the first rung with a *non-trivial known
answer*. An Ornstein–Uhlenbeck mode whose fluctuations and response are
mismatched, producing a **prescribed constant FDT-violation ratio X**
(the effective-temperature model, X = T/T_eff).

**No dataset.** Pure construction — an oracle: we dial X in, the pipeline
must read it back.

## Analytic ground truth

Exact discrete OU, stationary variance 1, relaxation time τ_relax:

```
a       = exp(-1/τ_relax)
x_unp(t+1) = a·x_unp + sqrt(1-a²)·ξ
x_per(t+1) = a·x_per + sqrt(1-a²)·ξ + b,   b = X·h·(1-a)   (CRN: same ξ)

C(τ)   = a^τ = exp(-τ/τ_relax)              (variance 1)
χ(τ)   = X·(1 - C(τ))                        (single-slope FDT violation)
```

So in the parametric FDR plane (1−C, χ) the locus is a **straight line of
slope X**. X=1 recovers equilibrium OU (FDT holds — identical to
`ou_equilibrium`). X<1 is aging / FDT-violated; X→0 is frozen.

The X-scaling of the response is the effective-temperature mismatch:
fluctuations at T_eff = T/X, response at the bath T. Realizing a
prescribed X this way is deliberate — it's a calibration standard, not a
model derived from microscopics. We know the answer; the pipeline's job
is to recover it.

## Operating points

X (the prescribed FDT-violation ratio) ∈ {1.0, 0.7, 0.5, 0.3, 0.1},
τ_relax = 20 fixed. This walks FDT-violation space from equilibrium
(X=1) to nearly frozen (X=0.1).

| X   | regime | gt |
|-----|--------|----|
| 1.0 | equilibrium (FDT holds) | r |
| 0.7 | weak aging | s |
| 0.5 | aging | s |
| 0.3 | strong aging | k |
| 0.1 | nearly frozen | c |

## Falsifier / recovery target

Grinder layer: the measured FDR locus must have slope = X (raw-fit slope
≈ prescribed X). Inversion layer (next move): conform's recovered X must
match the prescribed X. If it doesn't — and the grinder slope does — the
fault is the inversion.

## ẋ choices

`velocity`, `position-relative`.
