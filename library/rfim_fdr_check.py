"""Apparatus check for the RFIM gFDR: validate X=1 on an EASY equilibrium case
and test linearity in dh. The full test's equilibrium control failed (X=2.36);
this isolates whether that's a normalization bug or near-critical equilibration.

Disordered regime (R=2.0, H=0, v_H=0): equilibrates fast, FDT X=1 is guaranteed
at equilibrium (theorem, coupling notwithstanding). If X≈1 and flat in dh here,
the apparatus is sound and the R_c failure was critical slowing; if X≠1 here,
the normalization is wrong.
"""
from __future__ import annotations
import sys, time
from pathlib import Path
import numpy as np
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass
J = 1.0


def run(R, T, dh, N, N_real, t_w, n_window, seed, v_H=0.0, H0=0.0):
    rng = np.random.default_rng(seed)
    h = rng.normal(0.0, R, N)
    S_unp = -np.ones((N_real, N)); S_per = -np.ones((N_real, N))
    H = H0; invT = 1.0 / T
    for _ in range(t_w):
        H += v_H
        m = S_unp.mean(1)
        p = 0.5 * (1.0 + np.tanh((J * m[:, None] + H + h[None, :]) * invT))
        S_unp = np.where(rng.random((N_real, N)) < p, 1.0, -1.0)
        S_per = S_unp.copy()
    mu = np.empty((n_window, N_real)); mp = np.empty((n_window, N_real))
    for t in range(n_window):
        H += v_H
        m_u = S_unp.mean(1); m_p = S_per.mean(1)
        rnd = rng.random((N_real, N))
        S_unp = np.where(rnd < 0.5*(1+np.tanh((J*m_u[:,None]+H+h[None,:])*invT)), 1.0, -1.0)
        S_per = np.where(rnd < 0.5*(1+np.tanh((J*m_p[:,None]+H+h[None,:]+dh)*invT)), 1.0, -1.0)
        mu[t] = S_unp.mean(1); mp[t] = S_per.mean(1)
    ref = mu[0]
    C = (mu * ref[None, :]).mean(1) - mu.mean(1) * ref.mean()
    chi = (mp - mu).mean(1) / dh
    x = N * (C[0] - C); y = T * chi
    m = x > 0.05 * x.max()
    Xg = float(np.sum(x[m]*y[m]) / np.sum(x[m]*x[m]))
    return Xg, float(C[0]), float(chi[-1])


def main():
    N, N_real, t_w, n_window, T = 800, 256, 1500, 1500, 0.5
    print(f"disordered equilibrium control (R=2.0, T={T}, v_H=0): X should be ~1\n")
    print(f"{'dh':>7} {'X':>7} {'C0':>10} {'chi_inf':>10}")
    for dh in (0.002, 0.005, 0.01, 0.02):
        t0 = time.time()
        Xg, C0, chi_inf = run(R=2.0, T=T, dh=dh, N=N, N_real=N_real,
                              t_w=t_w, n_window=n_window, seed=7)
        print(f"{dh:>7.3f} {Xg:>7.3f} {C0:>10.2e} {chi_inf:>10.3f}  ({time.time()-t0:.0f}s)",
              flush=True)
    print("\n→ X≈1 & flat in dh: apparatus sound (R_c failure = critical slowing).")
    print("  X≠1 here: normalization bug to fix before any verdict.")


if __name__ == "__main__":
    main()
