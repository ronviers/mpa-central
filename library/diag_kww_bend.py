"""kww_oracle FDR locus — a REAL bend, model-free (contrast to mm1 artifact).

Three cells share identical C(tau) but differ only in prescribed FDR-
violation ratio X (1.0 / 0.5 / 0.2). The FDR locus chi vs (1-C) should:
  - fan out by X (long-lag/aging slope tracks the prescribed X),
  - give a CLEAN model-free local slope (C decays monotonically here, so
    adjacent-point slopes are signal, not the noise mm1 gave).

This is the validation that 'read the bend/slope' recovers known physics.

Run: python H:/mpa-central/library/diag_kww_bend.py
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

DATA = Path("H:/mpa-central/library/data/kww_oracle")
OUT = Path("H:/mpa-central/library/output/diagnostics")
CELLS = [("1", 1.0, "r"), ("0.5", 0.5, "s"), ("0.2", 0.2, "k")]
COLORS = {"1": "tab:green", "0.5": "tab:orange", "0.2": "tab:red"}


def load(Xtag):
    c = json.loads((DATA / f"kww_oracle__X{Xtag}__velocity.json").read_text(encoding="utf-8"))
    s = c["results"]["all_samples"]
    dt = np.array([float(e["dt"]) for e in s])
    C = np.array([float(e["C_mean"]) for e in s])
    chi = np.array([float(e["chi_mean"]) for e in s])
    chisem = np.array([float(e["chi_sem"] or 0.0) for e in s])
    o = np.argsort(dt)
    return dt[o], C[o], chi[o], chisem[o]


def slope_through_origin(x, y):
    m = np.isfinite(x) & np.isfinite(y)
    return float(np.sum(x[m]*y[m]) / np.sum(x[m]*x[m]))


fig, axes = plt.subplots(2, 3, figsize=(17, 9.5))

# top row: per-cell locus chi vs (1-C), colored by lag, with slope fit
print(f"{'X_prescribed':>13} {'gt':>3} {'recovered slope (chi vs 1-C)':>30}")
for i, (Xtag, Xval, gt) in enumerate(CELLS):
    dt, C, chi, chisem = load(Xtag)
    x = 1.0 - C                          # memory shed, C0=1 reference
    m = slope_through_origin(x, chi)
    ax = axes[0, i]
    sc = ax.scatter(x, chi, c=dt, cmap="viridis", s=26, edgecolor="k", lw=0.3, zorder=3)
    ax.errorbar(x, chi, yerr=chisem, fmt="none", ecolor="gray", lw=0.5, capsize=2, zorder=2)
    xs = np.linspace(0, x.max(), 50)
    ax.plot(xs, Xval*xs, "--", color="k", lw=1.2, label=f"prescribed X={Xval}")
    ax.plot(xs, m*xs, "-", color="b", lw=1.5, label=f"recovered={m:.3f}")
    ax.set_title(f"X={Xval} (gt={gt})")
    ax.set_xlabel("1 - C(tau)   [memory shed ->]")
    ax.set_ylabel("chi(tau)")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(alpha=0.3)
    fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04).set_label("lag tau", fontsize=8)
    print(f"{Xval:>13} {gt:>3} {m:>30.4f}")

# bottom-left: all three loci together -> the FAN-OUT by X
ax = axes[1, 0]
for Xtag, Xval, gt in CELLS:
    dt, C, chi, chisem = load(Xtag)
    x = 1.0 - C
    ax.plot(x, chi, "o-", ms=3, lw=1.0, color=COLORS[Xtag], label=f"X={Xval} (gt={gt})")
xs = np.linspace(0, 1, 30)
for Xval in (1.0, 0.5, 0.2):
    ax.plot(xs, Xval*xs, "--", color="gray", lw=0.8, alpha=0.7)
ax.set_title("all three loci: fan-out by X (the differentiation)")
ax.set_xlabel("1 - C(tau)")
ax.set_ylabel("chi(tau)")
ax.legend(fontsize=8, loc="upper left")
ax.grid(alpha=0.3)

# bottom-middle: MODEL-FREE local slope vs lag (should be clean here)
ax = axes[1, 1]
for Xtag, Xval, gt in CELLS:
    dt, C, chi, chisem = load(Xtag)
    x = 1.0 - C
    dx = np.diff(x)
    flips = int(np.sum(np.diff(np.sign(dx[dx != 0])) != 0))
    with np.errstate(divide="ignore", invalid="ignore"):
        local = np.diff(chi) / dx
    ax.plot(dt[1:], local, "o-", ms=3, lw=0.8, color=COLORS[Xtag],
            label=f"X={Xval}  (dx sign-flips={flips})")
    for Xval2 in [Xval]:
        ax.axhline(Xval2, color=COLORS[Xtag], ls=":", lw=0.8, alpha=0.6)
ax.set_title("model-free local slope vs lag  (contrast: mm1 was noise)")
ax.set_xlabel("lag tau")
ax.set_ylabel("d chi / d(1-C)")
ax.set_ylim(-0.2, 1.6)
ax.legend(fontsize=7, loc="upper right")
ax.grid(alpha=0.3)

# bottom-right: C(tau) decay (the shared backbone) + q_EA plateau
ax = axes[1, 2]
for Xtag, Xval, gt in CELLS:
    dt, C, chi, chisem = load(Xtag)
    ax.plot(dt, C, "o-", ms=3, lw=0.8, color=COLORS[Xtag], label=f"X={Xval}")
ax.axhline(0.7, color="k", ls="--", lw=1.0, alpha=0.6, label="q_EA=0.7 (plateau/knee)")
ax.set_title("C(tau): shared backbone (all three identical)")
ax.set_xlabel("lag tau")
ax.set_ylabel("C(tau)")
ax.set_xscale("log")
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

fig.suptitle("kww_oracle FDR locus — a REAL, model-free bend: loci fan out by prescribed X", fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.97])
out = OUT / "kww_bend__velocity.png"
fig.savefig(out, dpi=130)
print(f"\nwrote {out}")
