# east — East model (kinetically-constrained spin chain)

**Domain:** Kinetically constrained models / facilitated dynamics
**Reference:** Faggionato-Roberto-Toninelli KCM literature; East model
canonical glassy KCM.
**Implementation:** 1D chain, length L=200, single-spin-flip Glauber with
the East kinetic constraint (spin i can flip only if neighbor i−1 is +1).

## Operating points

T ∈ {0.4, 0.7, 1.0, 1.5, 2.0}. Equilibrium up-density
c_eq(T) = 1/(1 + exp(1/T)).

| T   | regime          | gt |
|-----|-----------------|----|
| 0.4 | deep glass      | c  |
| 0.7 | slow glass      | s  |
| 1.0 | mid             | k  |
| 1.5 | weakly glassy   | s  |
| 2.0 | nearly free     | r  |

## ẋ choices

`spin-flip`, `spin-relative`.

## τ_env

KCM super-Arrhenius: τ_env ≈ exp(1/T) for moderate T, capped to keep
the grid manageable.
