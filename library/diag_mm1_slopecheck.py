"""Check: is the 'coherent divergence' in the running-slope panel real,
or an artifact of (cubic fit) -> (analytic derivative) -> (divide by origin slope)?

Recompute the local slope MODEL-FREE: finite differences between adjacent
locus points, no cubic, no origin-normalization. If the drama vanishes,
it was the construction.

Run: python H:/mpa-central/library/diag_mm1_slopecheck.py
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

DATA = Path("H:/mpa-central/library/data/mm1_queue")
OUT = Path("H:/mpa-central/library/output/diagnostics")
RHOS = ["0.5", "0.8", "0.95", "0.99", "0.999"]
XDOT = "queue-increment"


def load(rho):
    c = json.loads((DATA / f"mm1_queue__rho{rho}__{XDOT}.json").read_text(encoding="utf-8"))
    s = c["results"]["all_samples"]
    dt = np.array([float(e["dt"]) for e in s])
    C = np.array([float(e["C_mean"]) for e in s])
    chi = np.array([float(e["chi_mean"]) for e in s])
    o = np.argsort(dt)
    return dt[o], C[o], chi[o], c["operating_point"]["gt"]


fig, axes = plt.subplots(2, 3, figsize=(17, 9.5))
axes = axes.ravel()
print(f"{'rho':>7} {'gt':>3} {'dC monotone in lag?':>20} {'#sign flips in dC':>18}")
for i, rho in enumerate(RHOS):
    dt, C, chi, gt = load(rho)
    dC = C[0] - C
    # is dC (memory shed) even a monotone function of lag? if not, the
    # parametric x-axis is degenerate and 'local slope vs memory' is noise.
    ddC = np.diff(dC)
    flips = int(np.sum(np.diff(np.sign(ddC[ddC != 0])) != 0))
    monotone = bool(np.all(ddC >= -1e-9))
    # model-free local slope between adjacent points
    dchi = np.diff(chi)
    with np.errstate(divide="ignore", invalid="ignore"):
        local = dchi / ddC
    ax = axes[i]
    ax.plot(dt[1:], local, "o-", ms=3, lw=0.8)
    ax.axhline(0, color="k", lw=0.6, alpha=0.5)
    ax.set_title(f"rho={rho} (gt={gt})  monotone-dC={monotone}  flips={flips}")
    ax.set_xlabel("lag tau")
    ax.set_ylabel("model-free local slope  dchi/d(C0-C)")
    ax.grid(alpha=0.3)
    ax.set_ylim(np.nanpercentile(local, 5) - 1, np.nanpercentile(local, 95) + 1)
    print(f"{rho:>7} {gt:>3} {str(monotone):>20} {flips:>18}")

# also show dC vs lag directly: is memory-shed monotone, or noise around 0?
ax = axes[5]
for rho in RHOS:
    dt, C, chi, gt = load(rho)
    dC = C[0] - C
    ax.plot(dt, dC / (np.abs(dC).max() or 1), "o-", ms=3, lw=0.8, label=f"rho={rho}")
ax.axhline(0, color="k", lw=0.6, alpha=0.5)
ax.set_title("memory shed (C0-C)/max vs lag  —  is the x-axis even monotone?")
ax.set_xlabel("lag tau")
ax.set_ylabel("(C0-C)/max")
ax.legend(fontsize=7)
ax.grid(alpha=0.3)

fig.suptitle("mm1_queue: model-free local slope (no cubic, no origin-normalization)", fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.97])
out = OUT / "mm1_slopecheck__queue-increment.png"
fig.savefig(out, dpi=130)
print(f"\nwrote {out}")
