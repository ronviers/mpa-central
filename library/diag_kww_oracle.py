"""Rung-5 diagnostic: does conform's 5-vector inversion recover the full
prescribed (q_EA, tau_alpha, beta_KWW, tau_beta, X) on the kww_oracle control?

Three-curve convention (FALSIFICATION.md):
  black = measured (±SEM)        → tests the grinder
  red   = analytic mode-sum C/χ  → the substrate's true correlator (prescribed)
  blue  = fit_kww5 recovery      → conform's 5-vector inversion

  black on red → grinder faithful (substrate honors its KWW ground truth)
  blue  on red → the 5-vector inversion recovers the full vector
                 (the thing two_temp_ou could NOT establish — there only X
                  was identifiable; here the C-shape params are non-degenerate)

Run:
    python H:/mpa-central/library/diag_kww_oracle.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

# conform on sys.path so we call the REAL five-vector fitter.
CONFORM = Path("H:/mpa-conform")
if str(CONFORM) not in sys.path:
    sys.path.insert(0, str(CONFORM))
# library primitives on sys.path for the analytic ground-truth helper.
PRIM = Path("H:/mpa-central/library/primitives")
if str(PRIM) not in sys.path:
    sys.path.insert(0, str(PRIM))

from conformer.compute import five_vector, gfdr_model       # noqa: E402
from kww_oracle.measurements import kww_C_chi               # noqa: E402

DATA_ROOT = Path("H:/mpa-central/library/data")
OUT_DIR = Path("H:/mpa-central/library/output/diagnostics")
SUBSTRATE = "kww_oracle"
OP_LABELS = ["X1", "X0.5", "X0.2"]
XDOT = "velocity"


def load_cell(op_label):
    p = DATA_ROOT / SUBSTRATE / f"{SUBSTRATE}__{op_label}__{XDOT}.json"
    cell = json.loads(p.read_text(encoding="utf-8"))
    s = cell["results"]["all_samples"]
    scale = float((cell.get("tau_env_analytic") or {}).get("value") or 1.0)
    return {
        "dt": np.array([float(e["dt"]) for e in s]),
        "C": np.array([float(e["C_mean"]) for e in s]),
        "C_sem": np.array([float(e["C_sem"] or 0.0) for e in s]),
        "chi": np.array([float(e["chi_mean"]) for e in s]),
        "chi_sem": np.array([float(e["chi_sem"] or 0.0) for e in s]),
        "op": cell["operating_point"],
        "scale": scale,
    }


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = len(OP_LABELS)
    fig, axes = plt.subplots(2, n, figsize=(6 * n, 8.5))

    hdr = (f"{'cell':>6} | {'param':>9} {'prescribed':>11} {'recovered':>10}")
    print(hdr); print("-" * len(hdr))

    for j, lab in enumerate(OP_LABELS):
        d = load_cell(lab)
        op = d["op"]; scale = d["scale"]
        tau_dim = d["dt"] / scale  # dimensionless lag

        # Prescribed params in DIMENSIONLESS lag units (the fitter's units).
        pres = {
            "q_EA": op["q_EA"],
            "tau_alpha": op["tau_alpha"] / scale,
            "beta_KWW": op["beta_KWW"],
            "tau_beta": op["tau_beta"] / scale,
            "X": op["X"],
        }

        # Red: substrate's true correlator (mode-sum), drawn in raw lag then
        # read at the measured dt.
        C_red, chi_red = kww_C_chi(d["dt"], op["q_EA"], op["tau_alpha"],
                                   op["beta_KWW"], op["tau_beta"], op["X"])
        rms_C = float(np.sqrt(np.mean((d["C"] - C_red) ** 2)))
        rms_chi = float(np.sqrt(np.mean((d["chi"] - chi_red) ** 2)))

        # Blue: the real 5-vector fit on dimensionless-lag rows.
        rows = [{"tau": float(t), "C": float(c), "chi": float(x)}
                for t, c, x in zip(tau_dim, d["C"], d["chi"])]
        fit = five_vector.fit_kww5(rows, T=1.0)
        rec = {"q_EA": fit.q_EA, "tau_alpha": fit.tau_alpha,
               "beta_KWW": fit.beta_KWW, "tau_beta": fit.tau_beta, "X": fit.X}
        for k in ("q_EA", "tau_alpha", "beta_KWW", "tau_beta", "X"):
            print(f"{lab:>6} | {k:>9} {pres[k]:>11.4f} {rec[k]:>10.4f}")
        print(f"{lab:>6} | {'resid':>9} {'':>11} {fit.residual:>10.4f}")

        locus = gfdr_model.generate_kww_glass_locus(
            fit.chit, q_EA=fit.q_EA, tau_alpha=fit.tau_alpha,
            beta_KWW=fit.beta_KWW, tau_beta=fit.tau_beta, X=fit.X, T=fit.T)
        bl_tau = np.asarray(locus["tau"]); bl_C = np.asarray(locus["C"])
        bl_chi = np.asarray(locus["chi"])
        sel = (bl_tau >= tau_dim.min() * 0.5) & (bl_tau <= tau_dim.max() * 2)

        axC, axchi = axes[0][j], axes[1][j]
        axC.errorbar(tau_dim, d["C"], yerr=d["C_sem"], fmt="o", color="black",
                     ms=4, capsize=2, zorder=3, label="measured")
        axC.plot(tau_dim, C_red, color="C3", lw=1.8, zorder=2,
                 label=f"analytic (RMS={rms_C:.4f})")
        axC.plot(bl_tau[sel], bl_C[sel], color="C0", lw=1.4, zorder=2,
                 label="fit_kww5")
        axC.set_xscale("log"); axC.set_xlim(tau_dim.min() * 0.5, tau_dim.max() * 2)
        axC.set_ylabel("C(τ)")
        axC.set_title(f"{lab}   prescribed X={op['X']:g}\n"
                      f"rec: q_EA={fit.q_EA:.2f} τ_α={fit.tau_alpha:.2f} "
                      f"β={fit.beta_KWW:.2f} τ_β={fit.tau_beta:.3f} X={fit.X:.2f}",
                      fontsize=8)
        axC.legend(loc="best", fontsize=8, frameon=False); axC.grid(True, alpha=0.25)

        axchi.errorbar(tau_dim, d["chi"], yerr=d["chi_sem"], fmt="o", color="black",
                       ms=4, capsize=2, zorder=3, label="measured")
        axchi.plot(tau_dim, chi_red, color="C3", lw=1.8, zorder=2,
                   label=f"analytic (RMS={rms_chi:.4f})")
        axchi.plot(bl_tau[sel], bl_chi[sel], color="C0", lw=1.4, zorder=2,
                   label="fit_kww5")
        axchi.set_xscale("log"); axchi.set_xlim(tau_dim.min() * 0.5, tau_dim.max() * 2)
        axchi.set_xlabel("τ (dimensionless = lag / τ_α)")
        axchi.set_ylabel("χ(τ)")
        axchi.legend(loc="best", fontsize=8, frameon=False); axchi.grid(True, alpha=0.25)

    fig.suptitle(
        "RUNG 5 — kww_oracle · velocity (full 5-vector recovery)\n"
        "black=measured(±SEM)  red=analytic mode-sum truth  blue=conform fit_kww5",
        fontsize=10)
    fig.tight_layout()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"inversion_{SUBSTRATE}__{XDOT}.png"
    fig.savefig(out, dpi=140); plt.close(fig)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
