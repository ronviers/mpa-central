"""k_frust ladder R1 -- high-power near-threshold probe (settles the one ambiguous
R1 point). As chit->0+ the loop enters the s-regime and the /r2 current estimator
loses power (small amplitude, few healthy realizations). The R1 sweep flagged
chit=0.02 (sep<3) -- but frust and control overlapped within error, so it could
not be scored. Here we POWER IT UP (more realizations, longer window, more seeds)
and ask the honest question:

  Is the frustrated cyclic current at a finite ALIVE chit>0 statistically
  distinguishable from the matched reciprocal control (true P_ss, J=0)?
    distinguishable  -> still a drain, NO resolution (survives)
    consistent w/ 0  -> the loop resolved near threshold (KILL)

We also report the healthy-r2 fraction (estimator power) so a null is only scored
when the measurement is actually powered -- verify nulls before they count.

Run: python H:/mpa-central/library/k_frust_r1_threshold.py
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from k_frust_r1_sweep import step, CYC, SYM, RHO_FLOOR, DT

N_REAL, T_EQ, T_OBS = 384, 5000, 10000
SEEDS = [1, 2, 3, 4, 5, 6]
L, SIGMA, GMAG = 1.00, 0.02, 0.50
G0_GRID = [1.01, 1.02, 1.04, 1.07, 1.10]


def cyclic_J_power(rho, rp):
    """Return (J contribution, healthy fraction) for this step."""
    m = rho.mean(1); mp = rp.mean(1)
    a = rho[:, 0] - m; b = (rho[:, 1] - rho[:, 2]) / np.sqrt(3.0)
    adot = ((rho[:, 0] - m) - (rp[:, 0] - mp)) / DT
    bdot = ((rho[:, 1] - rho[:, 2]) - (rp[:, 1] - rp[:, 2])) / (np.sqrt(3.0) * DT)
    r2 = a * a + b * b
    good = r2 > 1e-10
    J = float(np.mean((a[good] * bdot[good] - b[good] * adot[good]) / r2[good])) if good.any() else 0.0
    return J, float(good.mean())


def run(gmat, G0, seed):
    rng = np.random.default_rng(seed)
    g = GMAG * gmat
    rho = np.tile([0.06, 0.03, 0.01], (N_REAL, 1)).astype(float)
    for _ in range(T_EQ):
        rho = step(rho, g, G0, L, SIGMA, rng)
    chir = np.zeros(T_OBS); hf = 0.0
    for t in range(T_OBS):
        rp = rho.copy()
        rho = step(rho, g, G0, L, SIGMA, rng)
        chir[t], h = cyclic_J_power(rho, rp)
        hf += h
    return float(np.mean(chir)), hf / T_OBS, float(rho.mean())


def main():
    print(f"N_REAL={N_REAL} T_OBS={T_OBS} seeds={len(SEEDS)}  (sigma={SIGMA}, gmag={GMAG})\n")
    print(f"{'chit':>6} {'amp':>7} {'healthy':>8} | {'J_frust':>11} {'+/-':>9} | {'J_ctrl':>11} {'+/-':>9} | "
          f"{'2-sample sep':>12} | verdict")
    kills = []
    for G0 in G0_GRID:
        chit = np.log(G0 / L)
        Jf = np.array([run(CYC, G0, s) for s in SEEDS])
        Jc = np.array([run(SYM, G0, s) for s in SEEDS])
        jf, hf, amp = Jf[:, 0], Jf[:, 1].mean(), Jf[:, 2].mean()
        jc = Jc[:, 0]
        mf, sf = jf.mean(), jf.std(ddof=1)
        mc, sc = jc.mean(), jc.std(ddof=1)
        # two-sample separation of frust vs control (pooled SE)
        se = np.sqrt(sf**2 / len(jf) + sc**2 / len(jc))
        sep = abs(mf - mc) / max(se, 1e-12)
        powered = hf > 0.5
        if powered and sep < 2.0:
            verdict = "** KILL: J ~ control (resolved)"; kills.append((chit, sep))
        elif not powered:
            verdict = f"underpowered (healthy={hf:.2f}) -- inconclusive"
        else:
            verdict = "drain persists (survives)"
        print(f"{chit:>6.3f} {amp:>7.4f} {hf:>8.2f} | {mf:>+11.4e} {sf:>9.1e} | {mc:>+11.4e} {sc:>9.1e} | "
              f"{sep:>12.1f} | {verdict}")

    print("\n================ R1 near-threshold verdict ================")
    if kills:
        print(f"KILL at {len(kills)} powered point(s): the frustrated current became statistically "
              f"indistinguishable from the reciprocal P_ss control at a finite alive chit>0.")
    else:
        print("SURVIVES: at every POWERED alive chit>0 the frustrated current stayed statistically "
              "above the reciprocal control. Near-threshold weakening is amplitude vanishing at the "
              "critical limit (chit=0 unattainable), not a resolution to clean c/r.")


if __name__ == "__main__":
    main()
