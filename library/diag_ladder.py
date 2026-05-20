"""Diagnostic plots for the validation-ladder / control substrates.

Mirrors the mpa-conform KWW diagnostic format (top row C, bottom row chi,
columns = operating points, black markers ± SEM), but overlays the
ANALYTIC GROUND TRUTH (red) instead of a fitted model. For a positive
control we know the answer in closed form, so the question the picture
answers is: do the measured points land on the known curve?

Run:
    python H:/mpa-central/library/diag_ladder.py
Writes PNGs to H:/mpa-central/library/output/diagnostics/.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

DATA_ROOT = Path("H:/mpa-central/library/data")
OUT_DIR = Path("H:/mpa-central/library/output/diagnostics")


def load_cell(substrate: str, op_label: str, xdot: str) -> dict:
    p = DATA_ROOT / substrate / f"{substrate}__{op_label}__{xdot}.json"
    cell = json.loads(p.read_text(encoding="utf-8"))
    s = cell["results"]["all_samples"]
    return {
        "dt": np.array([float(e["dt"]) for e in s]),
        "C": np.array([float(e["C_mean"]) for e in s]),
        "C_sem": np.array([float(e["C_sem"] or 0.0) for e in s]),
        "chi": np.array([float(e["chi_mean"]) for e in s]),
        "chi_sem": np.array([float(e["chi_sem"] or 0.0) for e in s]),
        "op": cell["operating_point"],
        "schedule": cell["schedule"],
    }


def _tri(dt: np.ndarray, P: float) -> np.ndarray:
    """Phase-averaged square-wave autocorrelation: triangular wave, period P."""
    x = ((dt + P / 2.0) % P) - P / 2.0
    return 1.0 - 4.0 * np.abs(x) / P


def plot_control(substrate: str, op_labels: list[str], xdot: str,
                 analytic_C, analytic_chi=None, chi_note: str = "",
                 title_extra: str = ""):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = len(op_labels)
    fig, axes = plt.subplots(2, n, figsize=(6 * n, 8), sharey="row")
    if n == 1:
        axes = axes.reshape(2, 1)

    for j, lab in enumerate(op_labels):
        d = load_cell(substrate, lab, xdot)
        dt = d["dt"]
        axC, axchi = axes[0][j], axes[1][j]

        Ca = analytic_C(dt, d["op"])
        rms_C = float(np.sqrt(np.mean((d["C"] - Ca) ** 2)))
        axC.errorbar(dt, d["C"], yerr=d["C_sem"], fmt="o", color="black",
                     ms=4, capsize=2, zorder=3, label="measured")
        axC.plot(dt, Ca, color="C3", lw=1.8, zorder=2,
                 label=f"analytic (RMS={rms_C:.4f})")
        axC.set_xscale("log")
        axC.set_ylabel("C(tau)")
        axC.set_title(lab, fontsize=10)
        axC.legend(loc="best", fontsize=8, frameon=False)
        axC.grid(True, alpha=0.25)

        axchi.errorbar(dt, d["chi"], yerr=d["chi_sem"], fmt="o", color="black",
                       ms=4, capsize=2, zorder=3, label="measured")
        if analytic_chi is not None:
            chia = analytic_chi(dt, d["op"])
            rms_chi = float(np.sqrt(np.mean((d["chi"] - chia) ** 2)))
            axchi.plot(dt, chia, color="C3", lw=1.8, zorder=2,
                       label=f"analytic (RMS={rms_chi:.4f})")
        if chi_note:
            axchi.text(0.5, 0.92, chi_note, transform=axchi.transAxes,
                       fontsize=8, ha="center", va="top", color="gray")
        axchi.set_xscale("log")
        axchi.set_xlabel("tau (sample.dt = lag)")
        axchi.set_ylabel("chi(tau)")
        axchi.legend(loc="best", fontsize=8, frameon=False)
        axchi.grid(True, alpha=0.25)

    fig.suptitle(
        f"CONTROL LADDER: {substrate}  ·  xdot={xdot}  {title_extra}\n"
        f"black = measured (±SEM)   red = analytic ground truth",
        fontsize=10,
    )
    fig.tight_layout()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"control_{substrate}__{xdot}.png"
    fig.savefig(out, dpi=140)
    plt.close(fig)
    print(f"wrote {out}")
    return out


def plot_fdr_recovery(substrate: str, op_labels: list[str], xdot: str,
                      analytic_C, X_of_op, title_extra: str = ""):
    """Recovery diagnostic for rungs with a known FDT-violation X.

    Top row: C(τ) vs τ (lag), black measured ±SEM vs red analytic.
    Bottom row: PARAMETRIC FDR plot — χ vs (1−C). The prescribed FDT
    violation is a straight line of slope X; a raw linear fit to the
    measured locus recovers the grinder-level X (compared to prescribed).
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = len(op_labels)
    fig, axes = plt.subplots(2, n, figsize=(6 * n, 8))
    if n == 1:
        axes = axes.reshape(2, 1)

    for j, lab in enumerate(op_labels):
        d = load_cell(substrate, lab, xdot)
        dt = d["dt"]
        axC, axfdr = axes[0][j], axes[1][j]

        Ca = analytic_C(dt, d["op"])
        rms_C = float(np.sqrt(np.mean((d["C"] - Ca) ** 2)))
        axC.errorbar(dt, d["C"], yerr=d["C_sem"], fmt="o", color="black",
                     ms=4, capsize=2, zorder=3, label="measured")
        axC.plot(dt, Ca, color="C3", lw=1.8, zorder=2,
                 label=f"analytic exp (RMS={rms_C:.4f})")
        axC.set_xscale("log")
        axC.set_ylabel("C(tau)")
        axC.set_title(lab, fontsize=10)
        axC.legend(loc="best", fontsize=8, frameon=False)
        axC.grid(True, alpha=0.25)

        # Parametric FDR: x = 1 - C, y = chi.
        X_pre = float(X_of_op(d["op"]))
        omc = 1.0 - d["C"]
        chi = d["chi"]
        # Raw linear fit through origin: slope = sum(omc*chi)/sum(omc^2).
        denom = float(np.sum(omc * omc))
        slope_raw = float(np.sum(omc * chi) / denom) if denom > 0 else float("nan")
        order = np.argsort(omc)
        axfdr.errorbar(omc, chi, xerr=d["C_sem"], yerr=d["chi_sem"], fmt="o",
                       color="black", ms=4, capsize=2, zorder=3, label="measured")
        xline = np.linspace(0.0, float(np.max(omc)), 50)
        axfdr.plot(xline, X_pre * xline, color="C3", lw=1.8, zorder=2,
                   label=f"prescribed slope X={X_pre:g}")
        axfdr.plot(xline, slope_raw * xline, color="C0", lw=1.2, ls="--", zorder=2,
                   label=f"raw-fit slope={slope_raw:.3f}")
        axfdr.set_xlabel("1 - C(tau)")
        axfdr.set_ylabel("chi(tau)")
        axfdr.legend(loc="best", fontsize=8, frameon=False)
        axfdr.grid(True, alpha=0.25)
        _ = order

    fig.suptitle(
        f"CONTROL LADDER (recovery): {substrate}  ·  xdot={xdot}  {title_extra}\n"
        f"top: C vs lag (black=measured, red=analytic).   "
        f"bottom: FDR locus χ vs (1−C) — red=prescribed slope X, blue=raw fit",
        fontsize=10,
    )
    fig.tight_layout()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"control_{substrate}__{xdot}__fdr.png"
    fig.savefig(out, dpi=140)
    plt.close(fig)
    print(f"wrote {out}")
    return out


def main():
    # ── square_wave: analytic C is the triangular wave; chi expected ~0 ──
    plot_control(
        "square_wave", ["P10", "P100", "P1000"], "velocity",
        analytic_C=lambda dt, op: _tri(dt, float(op["P"])),
        analytic_chi=lambda dt, op: np.zeros_like(dt),
        chi_note="expected ~0 (driven, no FDT response)",
        title_extra="(character zero — C must trace the triangle)",
    )

    # ── sine_wave: analytic C is the cosine (pure tone) ──
    plot_control(
        "sine_wave", ["P30", "P100", "P1000"], "velocity",
        analytic_C=lambda dt, op: np.cos(2.0 * np.pi * dt / float(op["P"])),
        analytic_chi=None,
        chi_note="phase-shift response (driven, no FDT)",
        title_extra="(pure-tone character zero — C must trace the cosine)",
    )

    # ── white_noise: analytic C = 0 (memoryless) ──
    plot_control(
        "white_noise", ["sigma0.5", "sigma2", "sigma10"], "velocity",
        analytic_C=lambda dt, op: np.zeros_like(dt),
        analytic_chi=None,
        chi_note="DC-bias response",
        title_extra="(dissipative floor — C must sit at 0; SEM scales with sigma^2)",
    )

    # ── two_temp_ou: known exponential C + FDR locus of prescribed slope X ──
    import math as _m
    def _ou_C(dt, op):
        tau = float(op["tau_relax"])
        return np.exp(-dt / tau)
    plot_fdr_recovery(
        "two_temp_ou", ["X1.0", "X0.5", "X0.1"], "velocity",
        analytic_C=_ou_C,
        X_of_op=lambda op: float(op["X"]),
        title_extra="(rung 4 — known FDT violation; grinder must reproduce slope X)",
    )


if __name__ == "__main__":
    main()
