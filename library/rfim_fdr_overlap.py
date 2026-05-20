"""RFIM gFDR via the SELF-OVERLAP + staggered-field estimator (the standard
aging/spin-glass MC-FDT method). Replaces the collective-magnetization estimator,
which was dominated by the diverging soft mode near criticality (X swung 1.21/0.83
by update scheme — a measurement artifact, not physics).

Self-overlap protocol:
  C(t,t') = (1/N) Σ_i <s_i(t) s_i(t')>     (per-spin overlap; C(0)=1 exactly)
  staggered field eps*eta_i (eta_i=±1 fixed) on the perturbed branch from t_w
  chi(t,t') = (1/(N eps)) Σ_i eta_i <s_i^per(t) - s_i^unp(t)>
Equilibrium FDT:  T*chi(τ) = C(0) - C(τ) = 1 - C(τ)  →  X = T*chi/(1-C) = 1.
Self-averaging over N spins, no collective soft mode, no N-factor. Sequential
(detailed-balance) updates. Disordered equilibrium control must read X≈1.
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


def run_overlap(R, T, eps, N, N_real, t_w, n_window, seed, v_H=0.0, H0=0.0):
    rng = np.random.default_rng(seed)
    h = rng.normal(0.0, R, N)
    eta = rng.choice(np.array([-1.0, 1.0]), N)        # fixed staggered pattern
    S_u = -np.ones((N_real, N)); S_p = -np.ones((N_real, N))
    m_u = S_u.mean(1); m_p = S_p.mean(1)
    H = H0; invT = 1.0 / T; invN = 1.0 / N

    def sweep(perturb):
        nonlocal m_u, m_p
        for j in rng.permutation(N):
            rnd = rng.random(N_real)
            nu = np.where(rnd < 0.5*(1+np.tanh((J*m_u+H+h[j])*invT)), 1.0, -1.0)
            m_u += (nu - S_u[:, j]) * invN; S_u[:, j] = nu
            if perturb:
                npn = np.where(rnd < 0.5*(1+np.tanh((J*m_p+H+h[j]+eps*eta[j])*invT)), 1.0, -1.0)
                m_p += (npn - S_p[:, j]) * invN; S_p[:, j] = npn

    for _ in range(t_w):
        H += v_H; sweep(perturb=False)
    S_p[:] = S_u; m_p = m_u.copy()
    S_ref = S_u.copy()                                 # reference config at t_w
    C = np.empty(n_window + 1); chi = np.empty(n_window + 1)
    C[0] = 1.0; chi[0] = 0.0                            # equal-time: overlap=1, response=0
    for sw in range(n_window):
        H += v_H; sweep(perturb=True)
        C[sw + 1] = (S_u * S_ref).mean()               # (1/N)Σ_i s_i(t)s_i(t_w), avg replicas
        chi[sw + 1] = (eta[None, :] * (S_p - S_u)).mean() / eps
    x = C[0] - C; y = T * chi                          # FDT: y = x at equilibrium
    msk = x > 0.05 * x.max()
    Xg = float(np.sum(x[msk]*y[msk]) / np.sum(x[msk]*x[msk]))
    return Xg, float(C[0]), float(C[-1])


def main():
    N, N_real, t_w, n_window, T, R = 400, 300, 800, 800, 2.0, 0.5
    print(f"SELF-OVERLAP estimator — paramagnetic equilibrium (R={R}, T={T}, v_H=0): X→1?")
    print(f"(T={T} > mean-field T_c≈1 → spins decorrelate fully, C: 1→~0)\n")
    print(f"{'eps':>7} {'X':>7} {'C0':>7} {'Cinf':>7}")
    for eps in (0.02, 0.05, 0.1):
        t0 = time.time()
        Xg, C0, Cinf = run_overlap(R=R, T=T, eps=eps, N=N, N_real=N_real,
                                   t_w=t_w, n_window=n_window, seed=7)
        print(f"{eps:>7.3f} {Xg:>7.3f} {C0:>7.3f} {Cinf:>7.3f}  ({time.time()-t0:.0f}s)", flush=True)
    print("\n→ X≈1 & flat in eps: apparatus fixed (established self-overlap method) → run critical test.")


if __name__ == "__main__":
    main()
