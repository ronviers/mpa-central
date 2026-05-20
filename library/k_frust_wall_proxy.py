"""k_frust Wall round-trip -- OPTION 1 (substrate-level chaos proxy, annealed).

Drive a frustrated loop out of existence through chaos, then withdraw the chaos
and let structure re-form, and ask whether the cyclic current J comes back with
the same sign. J is the bulletproof meter (k_frust_meter.py).

CAVEAT (stated, load-bearing): MPA does not specify substrate-level coupling
reformation -- that is derived only in the meta-ledger tower (option 2). So this
imposes a plasticity rule (directional Hebbian) and the verdict is CONDITIONAL:
  J reforms same-sign  -> frustration is a dynamical attractor -> escalate to
                          option 2 (the faithful Wall) to confirm.
  J -> 0 / sign-flips  -> BROKE candidate, but could be the rule -> option 2
                          is the arbiter.

Phases: [baseline | chaos (gamma scrambled + wild drive) | reform | measure].
Couplings are ANNEALED (plastic) so 'does the same loop reform?' is a real
question, not trivially yes (quenched) -- the structural twin of 'pushing a
vertex to r is not enough'.

Run: python H:/mpa-central/library/k_frust_wall_proxy.py
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path("H:/mpa-central/library/output/diagnostics")
OUT.mkdir(parents=True, exist_ok=True)

G0, L = 1.20, 1.00
RHO_SAT = 1.0
G = 0.5
S0 = 1.0e-3
SIGMA = 0.02
RHO_FLOOR = 1.0e-7
DT = 0.005
N_REAL = 512
H_PERT = 0.05

# plasticity (annealing) -- the imposed reformation rule
ETA = 0.04          # Hebbian learning rate
GAMMA_DECAY = 0.015  # weak decay toward 0
GAMMA_CAP = 1.5 * G  # soft magnitude cap on couplings

G_FRUST = G * np.array([[0, 1, -1], [-1, 0, 1], [1, -1, 0]], float)

# phase schedule (steps)
T_BASE = 6000      # frustrated baseline (gamma fixed)
T_CHAOS = 6000     # destruction: scramble gamma + wild drive
T_REFORM = 12000   # withdraw chaos, let rho-gamma co-relax (plastic)
T_MEAS = 6000      # measurement window (gamma frozen at reformed value)


def finite(name, x):
    x = np.asarray(x, float)
    if not np.all(np.isfinite(x)):
        raise FloatingPointError(f"NON-FINITE in '{name}' (MPA NaN tripwire): bad test or boundary attainment.")
    return x


def antisym_strength(gmat):
    """Projection of gamma onto the cyclic-antisymmetric (frustrated) mode.
    +G_FRUST direction => frustrated; opposite => anti-frustrated; 0 => symmetric."""
    A = 0.5 * (gmat - gmat.T)               # antisymmetric part
    basis = 0.5 * (G_FRUST - G_FRUST.T)
    return float(np.sum(A * basis) / np.sum(basis * basis))


def chirality(rho, rho_prev):
    m = rho.mean(axis=1)
    a = rho[:, 0] - m
    b = (rho[:, 1] - rho[:, 2]) / np.sqrt(3.0)
    mp = rho_prev.mean(axis=1)
    adot = ((rho[:, 0] - m) - (rho_prev[:, 0] - mp)) / DT
    bdot = ((rho[:, 1] - rho[:, 2]) - (rho_prev[:, 1] - rho_prev[:, 2])) / (np.sqrt(3.0) * DT)
    r2 = a * a + b * b
    good = r2 > 1e-10
    return float(np.mean((a[good] * bdot[good] - b[good] * adot[good]) / r2[good])) if good.any() else 0.0


def step(rho, gmat, gain0, rng, sigma):
    S = rho.sum(axis=1, keepdims=True)
    gain = gain0[None, :] / (1.0 + S / RHO_SAT)
    cross = rho * (rho @ gmat.T) / RHO_SAT
    drift = (gain - L) * rho - cross + S0
    noise = sigma * np.sqrt(np.maximum(rho, 0.0)) * rng.standard_normal(rho.shape) * np.sqrt(DT)
    return np.maximum(rho + drift * DT + noise, RHO_FLOOR)


def hebbian_update(gmat, rho, rho_prev, rng, gamma_noise):
    """Directional Hebbian: gamma_ij grows when mode i high coincides with mode
    j declining (i suppresses j). Ensemble-averaged. Plus decay + optional noise
    (chaos scrambles wiring). Off-diagonal only."""
    rdot = (rho - rho_prev) / DT
    # corr_ij = <rho_i * rdot_j>  (negative => i suppresses j => grow gamma_ij)
    corr = (rho[:, :, None] * rdot[:, None, :]).mean(axis=0)   # (3,3)
    dg = ETA * (-corr) - GAMMA_DECAY * gmat
    g2 = gmat + dg * DT
    if gamma_noise > 0:
        g2 = g2 + gamma_noise * rng.standard_normal((3, 3)) * np.sqrt(DT)
    np.fill_diagonal(g2, 0.0)
    g2 = np.clip(g2, -GAMMA_CAP, GAMMA_CAP)
    return g2


def run(seed):
    rng = np.random.default_rng(seed)
    rho = np.tile([0.06, 0.03, 0.01], (N_REAL, 1)).astype(float)
    gmat = G_FRUST.copy()
    g0 = np.array([G0, G0, G0])
    total = T_BASE + T_CHAOS + T_REFORM + T_MEAS
    chir = np.zeros(total)
    asym = np.zeros(total)
    for t in range(total):
        if t < T_BASE:
            sigma, gnoise, plastic, drive = SIGMA, 0.0, False, g0
        elif t < T_BASE + T_CHAOS:                      # CHAOS: destroy structure
            # scramble the WIRING (gamma) hard + elevated bounded noise; keep
            # gain at g0 so saturation bounds rho (no gain-boost blowup).
            sigma, gnoise, plastic, drive = 0.10, 1.0, True, g0
        elif t < T_BASE + T_CHAOS + T_REFORM:           # REFORM: withdraw chaos
            sigma, gnoise, plastic, drive = SIGMA, 0.0, True, g0
        else:                                           # MEASURE: freeze gamma
            sigma, gnoise, plastic, drive = SIGMA, 0.0, False, g0
        rho_prev = rho.copy()
        rho = step(rho, gmat, drive, rng, sigma)
        if plastic:
            gmat = hebbian_update(gmat, rho, rho_prev, rng, gnoise)
        chir[t] = chirality(rho, rho_prev)
        asym[t] = antisym_strength(gmat)
    finite("chirality", chir); finite("antisym", asym)
    # phase J = mean chirality over last 3rd of each phase window
    def phase_J(lo, hi):
        w = slice(lo + 2 * (hi - lo) // 3, hi)
        return float(np.mean(chir[w]))
    Jb = phase_J(0, T_BASE)
    Jc = phase_J(T_BASE, T_BASE + T_CHAOS)
    Jm = phase_J(T_BASE + T_CHAOS + T_REFORM, total)
    asym_final = float(np.mean(asym[-T_MEAS // 3:]))
    return chir, asym, Jb, Jc, Jm, asym_final


def main():
    seeds = [1, 2, 3, 4, 5]
    rows = []
    chir0 = asym0 = None
    for s in seeds:
        chir, asym, Jb, Jc, Jm, af = run(s)
        if chir0 is None:
            chir0, asym0 = chir, asym
        rows.append((s, Jb, Jc, Jm, af))
        print(f"seed {s}: J_base={Jb:+.4e}  J_chaos={Jc:+.4e}  J_reformed={Jm:+.4e}  antisym_final={af:+.3f}")

    Jb = np.array([r[1] for r in rows]); Jm = np.array([r[3] for r in rows])
    af = np.array([r[4] for r in rows])
    print(f"\nbaseline  J = {Jb.mean():+.4e} +/- {Jb.std(ddof=1):.2e}")
    print(f"reformed  J = {Jm.mean():+.4e} +/- {Jm.std(ddof=1):.2e}")
    print(f"antisym strength reformed = {af.mean():+.3f} +/- {af.std(ddof=1):.3f}  (1=frustrated, 0=symmetric, -1=anti)")
    survived = Jm.mean() > 0.3 * Jb.mean() and (Jm > 0).mean() >= 0.8
    print(f"\nVERDICT (conditional on Hebbian rule): "
          f"{'FRUSTRATION SURVIVED -> escalate to option 2' if survived else 'DID NOT REFORM -> BROKE candidate (confirm w/ option 2)'}")

    total = len(chir0)
    tt = np.arange(total) * DT
    bounds = [0, T_BASE, T_BASE + T_CHAOS, T_BASE + T_CHAOS + T_REFORM, total]
    names = ["baseline", "CHAOS", "reform", "measure"]
    fig, ax = plt.subplots(2, 1, figsize=(14, 9), sharex=True)
    ax[0].plot(tt, chir0, lw=0.5, color="tab:red")
    ax[0].axhline(0, color="k", lw=0.6)
    ax[0].set_ylabel("cyclic current (chirality)"); ax[0].set_title("k_frust Wall round-trip (option 1, seed 1): does J reform after chaos?")
    ax[1].plot(tt, asym0, lw=0.7, color="tab:purple")
    ax[1].axhline(1, color="gray", ls="--", lw=0.8, label="frustrated (antisym)")
    ax[1].axhline(0, color="gray", ls=":", lw=0.8, label="symmetric")
    ax[1].set_ylabel("antisym strength of gamma"); ax[1].set_xlabel("time"); ax[1].legend(fontsize=8)
    for a in ax:
        for i, nm in enumerate(names):
            a.axvspan(bounds[i] * DT, bounds[i + 1] * DT, alpha=0.06,
                      color=["green", "red", "orange", "blue"][i])
            a.text((bounds[i] + bounds[i + 1]) / 2 * DT, a.get_ylim()[1] * 0.9, nm,
                   ha="center", fontsize=8, alpha=0.7)
    fig.tight_layout()
    png = OUT / "k_frust_wall_proxy.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
