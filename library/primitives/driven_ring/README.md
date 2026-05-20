# driven_ring — INVALIDATOR substrate

**Role:** Falsification target. Overdamped particle on a ring in a
tilted-washboard potential — a driven non-equilibrium **steady state**
(NESS) that sustains a probability current indefinitely.

```
dθ = (F - A·sin θ)·dt + sqrt(2·D·dt)·ξ
```

For F > A the particle "runs" — a persistent current ⟨θ̇⟩ > 0 that never
decays. For F < A it is locked near a potential minimum.

**No dataset.** Pure construction.

## The MPA axiom under test

LIBRARY_SPEC's load-bearing physics insight: *"every finite-flux
structure decays to r at infinity… the maintenance bookkeeping budget
runs out for any c and s trail given enough time."* A running NESS
**never** relaxes to a structureless r-asymptote — it maintains a
current forever, on a fixed energy throughput.

## Falsifier

**MPA is invalidated here if it forces an r-classification on the
running NESS (F > A), or if its regime vocabulary cannot represent a
sustained, non-decaying current.** Either the →r axiom is too strong
(NESS is a counterexample), or the framework must explicitly carve out
driven steady states — and that carve-out should be stated, not
discovered by a substrate breaking it.

The locked cells (F < A) are the control: those genuinely relax and
should behave normally.

## Operating points

F (drive) ∈ {0.5, 0.9, 1.0, 1.5, 3.0} with barrier A = 1, D = 0.5.
`gt = "r"` for locked (F<A), `"s"` for running (F>A, sustained holding).
The invalidator block carries the sustained-current claim.

## ẋ choices

`velocity` (Δθ per step — captures the current directly),
`position-relative` (unwrapped θ(t) − θ(snap)).
