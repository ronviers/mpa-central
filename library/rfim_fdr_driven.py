"""THE TEST — driven-critical RFIM gFDR on the validated self-overlap apparatus.

Equilibrium control reads X=1.00 (rfim_fdr_overlap.py), so the self-overlap +
staggered-field estimator is trustworthy. Now measure X for a DRIVEN CRITICAL
system and read the verdict:
  X≈1 at all lags  → driven criticality read as equilibrium (deep-r) → BROKE
  X<1 (aging/CK)   → s-regime → MPA survives this front.

Conditions (all on the validated estimator):
  equilibrium control : paramagnet, v_H=0            → must stay X≈1
  driven-critical     : R=R_c, sweep H through H_c   → THE TEST
  driven-noncritical  : R large, sweep H             → reference
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
OUT = Path("H:/mpa-central/library/output/diagnostics/rfim_fdr_driven.png")


def run_overlap(R, T, eps, N, N_real, t_w, n_window, seed, v_H=0.0, H0=0.0):
    rng = np.random.default_rng(seed)
    h = rng.normal(0.0, R, N)
    eta = rng.choice(np.array([-1.0, 1.0]), N)
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
    S_p[:] = S_u; m_p = m_u.copy(); S_ref = S_u.copy()
    C = np.empty(n_window + 1); chi = np.empty(n_window + 1)
    C[0] = 1.0; chi[0] = 0.0
    for sw in range(n_window):
        H += v_H; sweep(perturb=True)
        C[sw + 1] = (S_u * S_ref).mean()
        chi[sw + 1] = (eta[None, :] * (S_p - S_u)).mean() / eps
    x = C[0] - C; y = T * chi
    msk = x > 0.05 * x.max()
    Xg = float(np.sum(x[msk]*y[msk]) / np.sum(x[msk]*x[msk]))
    return x, y, Xg


def main():
    R_c = float(np.sqrt(2.0 / np.pi))
    N, N_real, t_w, n_window, eps = 400, 300, 800, 800, 0.05
    half = 0.3; v = 2.0 * half / n_window               # sweep ±half through H_c=0
    H0_drv = -half - t_w * v

    conds = {
        "equilibrium (control)":  dict(R=0.5,  T=2.0, v_H=0.0, H0=0.0,    seed=11),
        "driven-critical (TEST)": dict(R=R_c,  T=0.3, v_H=v,   H0=H0_drv, seed=21),
        "driven-noncritical":     dict(R=2.0,  T=0.3, v_H=v,   H0=H0_drv, seed=31),
    }
    res = {}
    for name, kw in conds.items():
        t0 = time.time()
        x, y, Xg = run_overlap(N=N, N_real=N_real, t_w=t_w, n_window=n_window,
                               eps=eps, **kw)
        res[name] = (x, y, Xg)
        print(f"  {name:>24}: X = {Xg:.3f}   ({time.time()-t0:.0f}s)", flush=True)

    Xeq = res["equilibrium (control)"][2]
    Xdr = res["driven-critical (TEST)"][2]
    print("\n===== gFDR VERDICT (validated self-overlap apparatus) =====")
    ok = abs(Xeq - 1.0) < 0.1
    print(f"  control X={Xeq:.3f} → {'VALID' if ok else 'CONTROL DRIFTED — recheck'}")
    if ok:
        print(f"  driven-critical X={Xdr:.3f}")
        if abs(Xdr - 1.0) < 0.1:
            print("  → X≈1: driven criticality read as EQUILIBRIUM → ** BROKE CANDIDATE **")
        else:
            print(f"  → X<1 (={Xdr:.3f}): CK / s-regime signature → ** MPA SURVIVES this front **")

    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.5, 7))
    col = {"equilibrium (control)": "C2", "driven-critical (TEST)": "C3",
           "driven-noncritical": "C0"}
    xm = 0.0
    for name, (x, y, Xg) in res.items():
        ax.plot(x, y, "o-", ms=3, color=col[name], alpha=0.85, label=f"{name}: X={Xg:.2f}")
        xm = max(xm, float(np.nanmax(x)))
    xl = np.linspace(0, xm, 50)
    ax.plot(xl, xl, "k--", lw=1.2, label="FDT line X=1 (equilibrium)")
    ax.set_xlabel("C(0) − C(τ)   [self-overlap]"); ax.set_ylabel("T·χ(τ)   [staggered]")
    ax.set_title("RFIM driven-critical gFDR — validated self-overlap estimator\n"
                 "slope = X. X=1 → equilibrium/deep-r; X<1 → s-regime (CK)")
    ax.legend(loc="best"); ax.grid(alpha=0.3)
    fig.tight_layout(); OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=140); plt.close(fig)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
