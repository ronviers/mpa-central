# ising_equilibrium — INVALIDATOR substrate

**Role:** Falsification target. 2D nearest-neighbor Ising on an L=32
torus, Glauber/Metropolis dynamics, sampled in **equilibrium steady
state** (long equilibration, no quench). Contrast with `mpc-glass`,
which *quenches* and *ages*.

**No dataset.** Pure construction.

## The MPA prediction under test

In equilibrium the FDT holds even at criticality. Critical slowing-down
near Tc ≈ 2.269 lengthens the relaxation time τ_env, but it does **not**
produce aging or FDT violation once the system is equilibrated: X = 1.

MPA's headline claim is that it distinguishes *slow* (long τ, still
equilibrium) from *aging* (genuine non-stationarity, X < 1). This
substrate is the clean separation test.

## Falsifier

**MPA is invalidated here if it reports persistent X < 1 in the
equilibrated system — especially near Tc — i.e. if it mistakes critical
slowing-down for aging.** A correct framework reports X = 1 at every
temperature, with only τ_env (not the regime) changing across the axis.

## Operating points

T ∈ {1.5, 2.0, 2.269, 2.6, 3.5} spanning Tc ≈ 2.269. `gt = "r"`
(equilibrium, FDT-respecting) for all; the invalidator block carries
`expected_X = 1.0`.

## ẋ choices

`spin-flip`, `spin-relative`. Checkerboard Metropolis update (fully
vectorized; CRN shared across paired branches).
