"""mm1_queue FDR-locus diagnostic — the BEND, not a single slope.

A single linear slope collapses the regime story. The FDR locus
chi(tau) vs C(0)-C(tau) is a bent curve: steep (~slope 1, quasi-
equilibrium) at short lag, bending shallow (aging slope alpha_s) at
long lag, flattening to a plateau (P_s). The bend is the fingerprint.

This diagnostic:
  - colors locus points by lag (so we see the trajectory direction),
  - fits a cubic through the origin (bendy curve, per request),
  - reads the RUNNING LOCAL SLOPE: quasi-eq slope at the origin end vs
    aging slope at the long-lag end (the physically-meaningful pair).

Run: python H:/mpa-central/library/diag_mm1_locus.py
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8")

import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm

DATA = Path("H:/mpa-central/library/data/mm1_queue")
OUT = Path("H:/mpa-central/library/output/diagnostics")
OUT.mkdir(parents=True, exist_ok=True)

RHOS = ["0.5", "0.8", "0.95", "0.99", "0.999"]
XDOT = "queue-increment"


def load(rho):
    c = json.loads((DATA / f"mm1_queue__rho{rho}__{XDOT}.json").read_text(encoding="utf-8"))
    s = c["results"]["all_samples"]
    dt = np.array([float(e["dt"]) for e in s])
    C = np.array([float(e["C_mean"]) for e in s])
    chi = np.array([float(e["chi_mean"]) for e in s])
    chisem = np.array([float(e["chi_sem"] or 0.0) for e in s])
    order = np.argsort(dt)
    return dt[order], C[order], chi[order], chisem[order], c["operating_point"]["gt"]


def cubic_through_origin(x, y):
    """Fit y = a*x + b*x^2 + c*x^3 (no constant: locus passes through origin).
    Returns coeffs and the running local slope dy/dx = a + 2b x + 3c x^2."""
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    if len(x) < 4:
        return None
    A = np.vstack([x, x**2, x**3]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    a, b, c = coef
    return a, b, c


fig, axes = plt.subplots(2, 3, figsize=(17, 9.5))
axes = axes.ravel()

print(f"{'rho':>7} {'gt':>3} {'slope@origin(quasi-eq)':>22} {'slope@long-lag(aging)':>22}")
for i, rho in enumerate(RHOS):
    dt, C, chi, chisem, gt = load(rho)
    C0 = C[0]
    dC = C0 - C                       # grows with lag
    # normalize x to [0,1] within this cell so cubic and slopes are comparable
    xmax = dC.max() if dC.max() != 0 else 1.0
    x = dC / xmax
    fit = cubic_through_origin(x, chi)

    ax = axes[i]
    sc = ax.scatter(x, chi, c=dt, cmap="viridis", s=28, zorder=3, edgecolor="k", lw=0.3)
    ax.errorbar(x, chi, yerr=chisem, fmt="none", ecolor="gray", lw=0.5, capsize=2, zorder=2)
    if fit is not None:
        a, b, c = fit
        xs = np.linspace(0, 1, 100)
        ys = a*xs + b*xs**2 + c*xs**3
        ax.plot(xs, ys, "b-", lw=1.8, zorder=4, label="cubic fit (through origin)")
        s0 = a                         # local slope at origin (quasi-eq)
        s1 = a + 2*b + 3*c             # local slope at x=1 (long-lag aging)
        print(f"{rho:>7} {gt:>3} {s0:>22.3g} {s1:>22.3g}")
        # reference slope-1 line scaled to the response magnitude
        chi_scale = np.nanmax(np.abs(chi))
        ax.plot(xs, chi_scale*xs, "k--", lw=1.0, alpha=0.6, label="slope 1 ref (equilibrium)")
    ax.set_title(f"rho={rho}  (gt={gt})  C(0)={C0:.3g}")
    ax.set_xlabel("(C(0)-C(tau)) / max   [memory shed ->]")
    ax.set_ylabel("chi(tau)  [response]")
    ax.legend(fontsize=7, loc="upper left")
    ax.grid(alpha=0.3)
    cb = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("lag tau", fontsize=8)

# running-local-slope panel: dy/dx of the cubic for each rho
ax = axes[5]
for rho in RHOS:
    dt, C, chi, chisem, gt = load(rho)
    dC = C[0] - C
    xmax = dC.max() if dC.max() != 0 else 1.0
    x = dC / xmax
    fit = cubic_through_origin(x, chi)
    if fit is None:
        continue
    a, b, c = fit
    xs = np.linspace(0, 1, 100)
    slope = a + 2*b*xs + 3*c*xs**2
    # normalize running slope by its origin value so we see the BEND ratio
    s0 = a if a != 0 else 1.0
    ax.plot(xs, slope/s0, "-", lw=1.4, label=f"rho={rho} (gt={gt})")
ax.axhline(1.0, color="k", ls="--", lw=1.0, alpha=0.6, label="no bend (constant slope)")
ax.set_title("running local slope / origin slope  —  the BEND")
ax.set_xlabel("(C(0)-C(tau)) / max   [memory shed ->]")
ax.set_ylabel("local slope ratio  (1 = equilibrium, <1 = aging)")
ax.legend(fontsize=7, loc="best")
ax.grid(alpha=0.3)

fig.suptitle("mm1_queue FDR locus — reading the BEND (quasi-eq -> aging), not a single slope",
             fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.97])
out = OUT / "mm1_locus_bend__queue-increment.png"
fig.savefig(out, dpi=130)
print(f"\nwrote {out}")
