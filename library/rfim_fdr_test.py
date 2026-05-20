"""NESS-sweep gFDR on the critical RFIM — THE TEST.

Does a driven critical system read X=1 (equilibrium, deep-r — BROKE) or X<1
(aging, s-regime — MPA survives)? Substrate: mean-field RFIM, verified critical
at R_c=sqrt(2/π) (rfim_substrate.py). Measurement: MPA's own paired-trajectory
gFDR — observable m, common-random-numbers thermal coupling, small step field dh
on the perturbed branch, X(τ) from the FD relation.

FDT normalization: the field dh couples to every spin, so the conjugate of the
intensive m is N*dh. The dynamic FDT is therefore  T*chi_m(τ) = N*(C(0)-C(τ))
at equilibrium → X=1. (X = T*chi / [N*(C0 - C)].) The equilibrium control is the
guard: if it doesn't read X≈1, the normalization/apparatus is wrong and no
verdict is read off the driven case.

Conditions:
  equilibrium     : v_H=0, equilibrated         → must read X≈1 (control)
  driven-critical : v_H>0 sweep through H_c, R_c → THE TEST
  driven-noncrit  : v_H>0 sweep, R deep disorder → reference (driven, not critical)
"""
from __future__ import annotations

import sys, time
from pathlib import Path
import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

OUT = Path("H:/mpa-central/library/output/diagnostics/rfim_fdr_test.png")
J = 1.0


def run_condition(R, T, v_H, dh, H0, N, N_real, t_w, n_window, seed):
    rng = np.random.default_rng(seed)
    h = rng.normal(0.0, R, N)                 # one disorder realization (shared)
    S_unp = -np.ones((N_real, N))
    S_per = -np.ones((N_real, N))
    H = H0
    invT = 1.0 / T
    # phase A: equilibrate / drive up to window start; per tracks unp (no dh yet)
    for _ in range(t_w):
        H += v_H
        m = S_unp.mean(1)
        p = 0.5 * (1.0 + np.tanh((J * m[:, None] + H + h[None, :]) * invT))
        S_unp = np.where(rng.random((N_real, N)) < p, 1.0, -1.0)
        S_per = S_unp.copy()
    # measurement window: dh on perturbed branch, shared CRN
    mu = np.empty((n_window, N_real))
    mp = np.empty((n_window, N_real))
    for t in range(n_window):
        H += v_H
        m_u = S_unp.mean(1); m_p = S_per.mean(1)
        rnd = rng.random((N_real, N))                       # common random numbers
        p_u = 0.5 * (1.0 + np.tanh((J * m_u[:, None] + H + h[None, :]) * invT))
        p_p = 0.5 * (1.0 + np.tanh((J * m_p[:, None] + H + h[None, :] + dh) * invT))
        S_unp = np.where(rnd < p_u, 1.0, -1.0)
        S_per = np.where(rnd < p_p, 1.0, -1.0)
        mu[t] = S_unp.mean(1); mp[t] = S_per.mean(1)
    ref = mu[0]
    C = (mu * ref[None, :]).mean(1) - mu.mean(1) * ref.mean()   # connected, thermal
    chi = (mp - mu).mean(1) / dh                                # integrated step response
    return C, chi


def analyze(C, chi, T, N):
    C0 = C[0]
    x = N * (C0 - C)            # FDT abscissa; at equilibrium = T*chi
    y = T * chi
    # global FDR slope X (fit through origin over the resolved range)
    m = np.isfinite(x) & np.isfinite(y) & (x > 0.02 * x.max())
    X_global = float(np.sum(x[m] * y[m]) / np.sum(x[m] * x[m]))
    # late-lag (aging-sector) slope: last third of lags
    k = len(C) * 2 // 3
    xa, ya = x[k:], y[k:]
    dX = np.polyfit(xa, ya, 1)[0] if xa.size > 3 else float("nan")
    return x, y, X_global, float(dX)


def main():
    R_c = float(np.sqrt(2.0 / np.pi))
    N, N_real, t_w, n_window, T, dh = 2000, 400, 2500, 2500, 0.30, 0.02
    v = 2.0e-4
    # center the sweep so H passes through H_c=0 mid-window
    H0_driven = -(t_w + n_window // 2) * v

    conds = {
        "equilibrium (control)":  dict(R=R_c, T=T, v_H=0.0, dh=dh, H0=0.0,
                                       seed=10),
        "driven-critical (TEST)": dict(R=R_c, T=T, v_H=v,   dh=dh, H0=H0_driven,
                                       seed=20),
        "driven-noncritical":     dict(R=2.0, T=T, v_H=v,   dh=dh, H0=H0_driven,
                                       seed=30),
    }
    results = {}
    for name, kw in conds.items():
        t0 = time.time()
        C, chi = run_condition(N=N, N_real=N_real, t_w=t_w, n_window=n_window, **kw)
        x, y, Xg, dX = analyze(C, chi, T, N)
        results[name] = (C, chi, x, y, Xg, dX)
        print(f"  {name:>24}: X_global={Xg:.3f}  late-lag slope={dX:.3f}  "
              f"({time.time()-t0:.1f}s)", flush=True)

    print("\n===== gFDR VERDICT =====")
    Xeq = results["equilibrium (control)"][4]
    Xdr = results["driven-critical (TEST)"][4]
    ctrl_ok = abs(Xeq - 1.0) < 0.15
    print(f"  control (equilibrium): X={Xeq:.3f}  -> "
          f"{'apparatus VALID (X≈1)' if ctrl_ok else 'CONTROL FAILED — no verdict (apparatus/equilibration off)'}")
    if ctrl_ok:
        print(f"  driven-critical TEST : X={Xdr:.3f}")
        if abs(Xdr - 1.0) < 0.15:
            print("  -> X≈1 at criticality: driven criticality read as EQUILIBRIUM (deep-r)")
            print("     => BROKE CANDIDATE (MPA misclassifies driven criticality)")
        else:
            print(f"  -> X<1 (={Xdr:.3f}): s-regime / CK ratio => MPA SURVIVES this test")

    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 7))
    colors = {"equilibrium (control)": "C2", "driven-critical (TEST)": "C3",
              "driven-noncritical": "C0"}
    xmax = 0.0
    for name, (C, chi, x, y, Xg, dX) in results.items():
        ax.plot(x, y, "o-", ms=3, color=colors[name], alpha=0.8,
                label=f"{name}: X={Xg:.2f}")
        xmax = max(xmax, np.nanmax(x))
    xl = np.linspace(0, xmax, 50)
    ax.plot(xl, xl, "k--", lw=1.2, label="FDT line (X=1, equilibrium)")
    ax.set_xlabel("N·[C(0) − C(τ)]   (= T·χ at equilibrium)")
    ax.set_ylabel("T·χ(τ)")
    ax.set_title("RFIM NESS-sweep gFDR — parametric FD plot\n"
                 "slope = X.  X=1 → equilibrium/deep-r;  X<1 → s-regime (CK)")
    ax.legend(loc="best"); ax.grid(alpha=0.3)
    fig.tight_layout(); OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=140); plt.close(fig)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
