# logistic_chaos — INVALIDATOR substrate

**Role:** Falsification target attacking the **stochasticity premise**.
Logistic map `x ← r·x·(1−x)` in the chaotic regime. **Deterministic —
there is no thermal noise, no bath, no temperature.** The ensemble is
over random initial conditions only; each trajectory is fully
deterministic given its seed.

**No dataset.** Pure construction.

## The MPA premise under test

MPA (RULES, stochasticity requirement) is built for *stochastic*
trajectories with a fluctuation–dissipation structure: the conjugate
perturbation produces a *linear response* that relaxes. A deterministic
chaotic map has no such structure — a parameter perturbation `r → r+h`
causes the perturbed and unperturbed trajectories to **diverge
exponentially** at the Lyapunov rate λ, so the "response" χ ~ e^{λt}/h
does not relax; it saturates at O(1/h) once the trajectories decorrelate
on the bounded attractor.

## Falsifier

**MPA is invalidated here if it returns a confident, finite,
FDT-respecting regime classification (c/s/k/r with a sensible X) on a
system that has no stochastic bath and whose response is Lyapunov-
divergent rather than relaxational.** The correct behavior is either to
flag the input as out-of-domain (no stochasticity) or to show a
manifestly broken FDT signature — *not* to manufacture a tidy regime
story.

This is a scope-boundary test: does the apparatus know the difference
between thermal noise and deterministic chaos, or does it read chaos as
a heat bath?

## Operating points

r ∈ {3.6, 3.7, 3.8, 3.9, 4.0} (chaotic band; Lyapunov exponent grows
toward r=4). `gt = "k"` placeholder; the invalidator block carries the
real claim. ICs drawn uniform on (0,1), transient burned in.

## ẋ choices

`velocity` (x(t) − x(t−1)), `position-relative` (x(t) − x(snap)).
