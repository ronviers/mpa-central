"""Finite-T mean-field depinning interface — criticality verification (step 1).

The falsification test (cdv1 vs the ABBM report): does a driven CRITICAL system
read X=1 (equilibrium, deep-r — report's claim, => BROKE) or X<1 (aging,
s-regime — cdv1's claim, => survives) under MPA's gFDR?

This script is STEP 1 only: establish that the substrate is genuinely critical
(avalanche exponent tau ~ 3/2, mean-field depinning class) BEFORE any FDR reading.
A non-critical substrate makes the FDR test meaningless (branch 3).

Model (mean-field, overdamped, Langevin):
    du_i/dt = k*(ubar - u_i) + F - A*sin(u_i + phi_i) + sqrt(2T) xi_i(t)
  ubar = mean_i u_i ; phi_i random per site ; F drive ; A pinning ; k coupling.
Single-site depins at F=A; mean-field coupling sets a collective threshold F_c.
At F just above F_c the mean velocity v=d(ubar)/dt is intermittent (avalanches).
"""
from __future__ import annotations

import sys, time
from pathlib import Path
import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

OUT = Path("H:/mpa-central/library/output/diagnostics/depinning_criticality.png")


def evolve(F, T, N=2000, A=1.0, k=1.0, dt=0.01, nsteps=20000, seed=0,
           u0=None, phi=None, record_v=False, rng=None):
    """Euler-Maruyama. Returns (u_final, phi, mean_v, v_series_or_None)."""
    if rng is None:
        rng = np.random.default_rng(seed)
    if phi is None:
        phi = rng.uniform(0, 2 * np.pi, N)
    u = (rng.uniform(0, 2 * np.pi, N) if u0 is None else u0.copy())
    v_series = np.empty(nsteps) if record_v else None
    sqrt2Tdt = np.sqrt(2.0 * T * dt)
    ubar_prev = u.mean()
    vsum = 0.0
    for t in range(nsteps):
        ubar = u.mean()
        force = k * (ubar - u) + F - A * np.sin(u + phi)
        u = u + force * dt + sqrt2Tdt * rng.standard_normal(N)
        ubar_new = u.mean()
        v = (ubar_new - ubar_prev) / dt
        ubar_prev = ubar_new
        if record_v:
            v_series[t] = v
        if t >= nsteps // 2:
            vsum += v
    mean_v = vsum / (nsteps - nsteps // 2)
    return u, phi, mean_v, v_series


def sweep_Fc(T=0.002, Fs=None, seed=0):
    """Locate the depinning threshold: <v> vs F."""
    if Fs is None:
        Fs = np.linspace(0.6, 1.15, 12)
    rng = np.random.default_rng(seed)
    phi = rng.uniform(0, 2 * np.pi, 2000)
    u = rng.uniform(0, 2 * np.pi, 2000)
    out = []
    for F in Fs:
        u, phi, mv, _ = evolve(F, T, N=2000, phi=phi, u0=u, nsteps=15000,
                               rng=rng)
        out.append((float(F), float(mv)))
        print(f"  F={F:.3f}  <v>={mv:.4f}", flush=True)
    return out


def fit_tau_logbin(sizes, s_min, s_max_frac=0.15, nbins=22):
    s_max = sizes.max()
    edges = np.geomspace(s_min * 0.8, s_max + 1, nbins + 1)
    counts, _ = np.histogram(sizes, bins=edges)
    widths = np.diff(edges); centers = np.sqrt(edges[:-1] * edges[1:])
    P = counts / widths / counts.sum()
    fit_hi = s_max_frac * s_max
    m = (centers >= s_min) & (centers <= fit_hi) & (P > 0)
    slope, icpt = np.polyfit(np.log10(centers[m]), np.log10(P[m]), 1)
    return centers, P, -slope, (s_min, fit_hi), (slope, icpt)


def measure_avalanches(F, T=0.002, seed=1):
    """At F just above F_c: velocity time series -> avalanche sizes (excursions)."""
    rng = np.random.default_rng(seed)
    # warm up to steady creep
    u, phi, mv, _ = evolve(F, T, N=2000, nsteps=20000, rng=rng)
    _, _, _, v = evolve(F, T, N=2000, phi=phi, u0=u, nsteps=400000,
                        record_v=True, rng=rng)
    v = np.clip(v, 0, None)
    # avalanche = excursion above threshold (fraction of mean); size = integral
    v_th = 0.5 * v.mean()
    above = v > v_th
    sizes = []
    cur = 0.0; on = False
    for vi, a in zip(v, above):
        if a:
            cur += (vi - v_th); on = True
        elif on:
            sizes.append(cur); cur = 0.0; on = False
    sizes = np.asarray([s for s in sizes if s > 0])
    return sizes, float(v.mean()), v_th


def main():
    print("[depinning] step 1: locate F_c and verify criticality\n--- F sweep ---", flush=True)
    sweep = sweep_Fc()
    Fs = np.array([f for f, _ in sweep]); vs = np.array([v for _, v in sweep])
    # F_c ~ where <v> first rises clearly above noise floor
    floor = vs[0]
    above_floor = Fs[vs > floor + 0.02]
    F_c = float(above_floor[0]) if above_floor.size else float(Fs[len(Fs) // 2])
    F_test = F_c + 0.03
    print(f"\n  estimated F_c ~ {F_c:.3f}; measuring avalanches at F={F_test:.3f}", flush=True)

    sizes, vmean, v_th = measure_avalanches(F_test)
    print(f"  {sizes.size} avalanches; <v>={vmean:.4f}; v_th={v_th:.4f}; "
          f"size range [{sizes.min():.3g}, {sizes.max():.3g}]", flush=True)

    s_min = np.quantile(sizes, 0.3)
    centers, P, tau, (s_lo, s_hi), (slope, icpt) = fit_tau_logbin(sizes, s_min=s_min)
    print(f"\n===== DEPINNING CRITICALITY =====")
    print(f"  avalanche tau (log-bin, s in [{s_lo:.3g},{s_hi:.3g}]) = {tau:.3f}")
    print(f"  cdv1 mean-field prediction: tau = 3/2")
    crit = "looks critical (tau ~ 3/2)" if abs(tau - 1.5) < 0.25 else \
           "NOT cleanly 3/2 -- reconsider model/operating point before FDR"
    print(f"  -> {crit}")

    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].plot(Fs, vs, "o-", color="black"); ax[0].axvline(F_c, color="C3", ls="--", label=f"F_c~{F_c:.2f}")
    ax[0].set_xlabel("drive F"); ax[0].set_ylabel("<v>"); ax[0].set_title("depinning transition")
    ax[0].legend(); ax[0].grid(alpha=0.3)
    ax[1].loglog(centers, P, "o", color="black", label="P(S)")
    sref = np.geomspace(s_lo, s_hi, 40)
    ax[1].loglog(sref, 10**icpt * sref**-1.5, "C3-", lw=2, label="τ=3/2 (cdv1)")
    ax[1].loglog(sref, 10**icpt * sref**slope, "C0--", lw=1.5, label=f"fit τ={tau:.2f}")
    ax[1].set_xlabel("avalanche size S"); ax[1].set_ylabel("P(S)")
    ax[1].set_title(f"avalanches at F={F_test:.3f}  (τ={tau:.3f})")
    ax[1].legend(); ax[1].grid(which="both", alpha=0.2)
    fig.suptitle("DEPINNING SUBSTRATE — step 1: criticality verification")
    fig.tight_layout(); OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=140); plt.close(fig)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
