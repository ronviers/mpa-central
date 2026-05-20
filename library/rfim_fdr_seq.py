"""RFIM gFDR with SEQUENTIAL spin updates (detailed balance → clean FDT).

The synchronous-update apparatus gave X≈1.21 on a disordered equilibrium case
where FDT X=1 is a theorem — a known artifact of parallel Glauber updates (they
break detailed balance; every mean-field spin reacts to a stale m). Sequential
single-spin updates (m refreshed between flips) restore the equilibrium FDT.

This re-validates the apparatus: disordered equilibrium (R=2.0, v_H=0) must read
X≈1, flat in dh. Only then is a verdict on the driven-critical case meaningful.
Vectorized over replicas; the spin loop is serial (required for detailed balance
in mean field).
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


def run_seq(R, T, dh, N, N_real, t_w, n_window, seed, v_H=0.0, H0=0.0):
    rng = np.random.default_rng(seed)
    h = rng.normal(0.0, R, N)
    S_u = -np.ones((N_real, N)); S_p = -np.ones((N_real, N))
    m_u = S_u.mean(1); m_p = S_p.mean(1)
    H = H0; invT = 1.0 / T; invN = 1.0 / N

    def sweep(perturb):
        nonlocal m_u, m_p
        order = rng.permutation(N)
        for j in order:
            rnd = rng.random(N_real)
            eu = J * m_u + H + h[j]
            nu = np.where(rnd < 0.5 * (1.0 + np.tanh(eu * invT)), 1.0, -1.0)
            m_u += (nu - S_u[:, j]) * invN; S_u[:, j] = nu
            if perturb:
                ep = J * m_p + H + h[j] + dh
                npn = np.where(rnd < 0.5 * (1.0 + np.tanh(ep * invT)), 1.0, -1.0)
                m_p += (npn - S_p[:, j]) * invN; S_p[:, j] = npn

    for _ in range(t_w):
        H += v_H
        sweep(perturb=False)
    S_p[:] = S_u; m_p = m_u.copy()
    mu = np.empty((n_window, N_real)); mp = np.empty((n_window, N_real))
    for sw in range(n_window):
        H += v_H
        sweep(perturb=True)
        mu[sw] = m_u; mp[sw] = m_p
    ref = mu[0]
    C = (mu * ref[None, :]).mean(1) - mu.mean(1) * ref.mean()
    chi = (mp - mu).mean(1) / dh
    x = N * (C[0] - C); y = T * chi
    msk = x > 0.05 * x.max()
    Xg = float(np.sum(x[msk] * y[msk]) / np.sum(x[msk] * x[msk]))
    return Xg, float(C[0])


def main():
    N, N_real, t_w, n_window, T = 400, 300, 800, 800, 0.5
    print(f"SEQUENTIAL updates — disordered equilibrium (R=2.0, T={T}, v_H=0): X→1?\n")
    print(f"{'dh':>7} {'X':>7} {'C0':>10}")
    for dh in (0.005, 0.02):
        t0 = time.time()
        Xg, C0 = run_seq(R=2.0, T=T, dh=dh, N=N, N_real=N_real,
                         t_w=t_w, n_window=n_window, seed=7)
        print(f"{dh:>7.3f} {Xg:>7.3f} {C0:>10.2e}  ({time.time()-t0:.0f}s)", flush=True)
    print("\n→ X≈1: apparatus fixed, sequential dynamics validated → proceed to critical test.")
    print("  X still ≠1: deeper issue (discrete-time FDT convention) to chase.")


if __name__ == "__main__":
    main()
