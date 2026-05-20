"""Inversion-overlay diagnostic: does conform's inversion recover the
prescribed FDT-violation X on the two_temp_ou control?

Adds the THIRD curve (blue = post-inversion cdv1 locus) on top of the
black (measured) and red (prescribed) curves. The inversion fits the
1-param chit (gfdr_model.generate_locus); X is NOT a direct fit parameter
(it lives in the owed KWW 5-vector). So the question this answers is:
can the 1-param cdv1 locus reproduce a known slope-X FDR line, or does
it need the 5-vector?

  black on red  → grinder faithful
  blue  on red  → 1-param inversion recovers the known violation
  blue off red  (while black on red) → fault localized to the inversion
                 (here: most likely the 1-param prior's expressivity limit,
                  i.e. the documented '5-vector owed' situation)

Run:
    python H:/mpa-central/library/diag_inversion.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

# conform on sys.path so we call the REAL inversion (not a re-implementation).
CONFORM = Path("H:/mpa-conform")
if str(CONFORM) not in sys.path:
    sys.path.insert(0, str(CONFORM))

from conformer.compute import inversion, gfdr_model  # noqa: E402

DATA_ROOT = Path("H:/mpa-central/library/data")
OUT_DIR = Path("H:/mpa-central/library/output/diagnostics")


def load_cell(substrate, op_label, xdot):
    p = DATA_ROOT / substrate / f"{substrate}__{op_label}__{xdot}.json"
    cell = json.loads(p.read_text(encoding="utf-8"))
    s = cell["results"]["all_samples"]
    tau_scale = float((cell.get("tau_env_analytic") or {}).get("value") or 1.0)
    return {
        "dt": np.array([float(e["dt"]) for e in s]),
        "C": np.array([float(e["C_mean"]) for e in s]),
        "C_sem": np.array([float(e["C_sem"] or 0.0) for e in s]),
        "chi": np.array([float(e["chi_mean"]) for e in s]),
        "chi_sem": np.array([float(e["chi_sem"] or 0.0) for e in s]),
        "op": cell["operating_point"],
        "tau_scale": tau_scale,
    }


def invert_cell(d):
    tau_dim = d["dt"] / d["tau_scale"]
    rows = [{"tau": float(t), "C": float(c), "chi": float(x)}
            for t, c, x in zip(tau_dim, d["C"], d["chi"])]
    fit = inversion.invert(rows, skip_stage2=True)   # stage1 analytical chit
    locus = gfdr_model.generate_locus(fit.chit)
    return fit, locus, tau_dim


def plot_inversion_C_chi(substrate, op_labels, xdot, analytic_C, title_extra=""):
    """General inversion overlay: C and χ vs dimensionless τ, with the blue
    cdv1 locus from the real conform inversion. For substrates where the
    C-vs-τ shape (not the FDR slope) is the interesting story — e.g. an
    oscillating C meeting a monotone-decay cdv1 family."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = len(op_labels)
    fig, axes = plt.subplots(2, n, figsize=(6 * n, 8))
    if n == 1:
        axes = axes.reshape(2, 1)
    print(f"{'cell':>8} {'chit':>7} {'regime':>10} {'resid':>8}")
    for j, lab in enumerate(op_labels):
        d = load_cell(substrate, lab, xdot)
        fit, locus, tau_dim = invert_cell(d)
        print(f"{lab:>8} {fit.chit:>7.3f} {fit.regime:>10} {fit.locus_residual:>8.4f}")

        axC, axchi = axes[0][j], axes[1][j]
        Ca = analytic_C(d["dt"], d["op"])
        axC.errorbar(tau_dim, d["C"], yerr=d["C_sem"], fmt="o", color="black",
                     ms=4, capsize=2, zorder=3, label="measured")
        axC.plot(tau_dim, Ca, color="C3", lw=1.8, zorder=2, label="analytic")
        axC.plot(locus["tau"], locus["C"], color="C0", lw=1.4, zorder=2,
                 label=f"inversion cdv1 (chit={fit.chit:.2f}, {fit.regime})")
        axC.set_xscale("log"); axC.set_xlim(tau_dim.min() * 0.5, tau_dim.max() * 2)
        axC.set_ylabel("C(tau)"); axC.set_title(lab, fontsize=10)
        axC.axhline(0.0, color="gray", lw=0.6, alpha=0.5)
        axC.legend(loc="best", fontsize=8, frameon=False); axC.grid(True, alpha=0.25)

        axchi.errorbar(tau_dim, d["chi"], yerr=d["chi_sem"], fmt="o", color="black",
                       ms=4, capsize=2, zorder=3, label="measured")
        axchi.plot(locus["tau"], locus["chi"], color="C0", lw=1.4, zorder=2,
                   label="inversion cdv1 chi")
        axchi.set_xscale("log"); axchi.set_xlim(tau_dim.min() * 0.5, tau_dim.max() * 2)
        axchi.set_xlabel("tau (dimensionless = lag / tau_scale)")
        axchi.set_ylabel("chi(tau)")
        axchi.legend(loc="best", fontsize=8, frameon=False); axchi.grid(True, alpha=0.25)

    fig.suptitle(
        f"INVERSION OVERLAY: {substrate} · {xdot}  {title_extra}\n"
        f"black=measured  red=analytic  blue=conform 1-param cdv1 inversion",
        fontsize=10)
    fig.tight_layout()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"inversion_{substrate}__{xdot}.png"
    fig.savefig(out, dpi=140); plt.close(fig)
    print(f"wrote {out}")
    return out


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Sine wave: oscillating cosine C meets the monotone-decay cdv1 family.
    plot_inversion_C_chi(
        "sine_wave", ["P30", "P100", "P1000"], "velocity",
        analytic_C=lambda dt, op: np.cos(2.0 * np.pi * dt / float(op["P"])),
        title_extra="(pure tone — how far does monotone cdv1 follow a cosine?)",
    )

    substrate, xdot = "two_temp_ou", "velocity"
    op_labels = ["X1.0", "X0.5", "X0.1"]

    n = len(op_labels)
    fig, axes = plt.subplots(2, n, figsize=(6 * n, 8))
    print(f"{'cell':>8} {'X_pre':>6} {'chit':>7} {'regime':>10} "
          f"{'raw_slope':>9} {'blue_slope':>10} {'resid':>8}")
    for j, lab in enumerate(op_labels):
        d = load_cell(substrate, lab, xdot)
        X_pre = float(d["op"]["X"])
        fit, locus, tau_dim = invert_cell(d)

        # raw-fit slope of measured FDR locus (through origin)
        omc = 1.0 - d["C"]
        denom = float(np.sum(omc * omc))
        raw_slope = float(np.sum(omc * d["chi"]) / denom) if denom > 0 else float("nan")

        # blue locus FDR slope (fit through origin over its own 1-C range)
        bl_omc = 1.0 - np.asarray(locus["C"])
        bl_chi = np.asarray(locus["chi"])
        bden = float(np.sum(bl_omc * bl_omc))
        blue_slope = float(np.sum(bl_omc * bl_chi) / bden) if bden > 0 else float("nan")

        print(f"{lab:>8} {X_pre:>6.2f} {fit.chit:>7.3f} {fit.regime:>10} "
              f"{raw_slope:>9.3f} {blue_slope:>10.3f} {fit.locus_residual:>8.4f}")

        axC, axfdr = axes[0][j], axes[1][j]
        # C vs dimensionless tau
        Ca = np.exp(-d["dt"] / d["tau_scale"])  # analytic exp in raw lag; tau_dim=dt/scale
        axC.errorbar(tau_dim, d["C"], yerr=d["C_sem"], fmt="o", color="black",
                     ms=4, capsize=2, zorder=3, label="measured")
        axC.plot(tau_dim, Ca, color="C3", lw=1.8, zorder=2, label="analytic exp")
        axC.plot(locus["tau"], locus["C"], color="C0", lw=1.4, zorder=2,
                 label=f"inversion cdv1 (chit={fit.chit:.2f}, {fit.regime})")
        axC.set_xscale("log"); axC.set_xlim(tau_dim.min() * 0.5, tau_dim.max() * 2)
        axC.set_ylabel("C(tau)"); axC.set_title(f"{lab}  (prescribed X={X_pre:g})", fontsize=10)
        axC.legend(loc="best", fontsize=8, frameon=False); axC.grid(True, alpha=0.25)

        # FDR parametric
        xline = np.linspace(0.0, float(np.max(omc)), 50)
        axfdr.errorbar(omc, d["chi"], xerr=d["C_sem"], yerr=d["chi_sem"], fmt="o",
                       color="black", ms=4, capsize=2, zorder=3, label="measured")
        axfdr.plot(xline, X_pre * xline, color="C3", lw=1.8, zorder=2,
                   label=f"prescribed X={X_pre:g}")
        axfdr.plot(bl_omc, bl_chi, color="C0", lw=1.4, zorder=2,
                   label=f"inversion locus (slope~{blue_slope:.2f})")
        axfdr.set_xlim(0, float(np.max(omc)) * 1.05)
        axfdr.set_xlabel("1 - C(tau)"); axfdr.set_ylabel("chi(tau)")
        axfdr.legend(loc="best", fontsize=8, frameon=False); axfdr.grid(True, alpha=0.25)

    fig.suptitle(
        "INVERSION RECOVERY: two_temp_ou · velocity\n"
        "black=measured  red=prescribed X  blue=conform 1-param cdv1 inversion",
        fontsize=10)
    fig.tight_layout()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "inversion_two_temp_ou__velocity.png"
    fig.savefig(out, dpi=140); plt.close(fig)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
