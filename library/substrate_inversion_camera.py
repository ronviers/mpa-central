r"""Substrate inversion = where is the tau_obs camera pointed on the c->s->r migration?

The viability question for MPA character tests, made visual. Three library substrates
are ALL ground-truth gt='s' (the grinder intends them as s-regime). But the tau_obs
camera (RFC-S 0.2: tau_obs is the camera; the canonical representation is the RG-flow
fixed-point set AT the observer position) is aimed differently for each:

  glass T=0.5   : dC=1-C spans 0.06..0.44 -> camera in the MIGRATION INTERIOR (sees the
                  FDT regime + aging onset). X recoverable.
  brain suspended: dC pinned 0.92..0.98, but chi STILL EVOLVING (0.006->0.23) -> RFC-S 6
                  tau_obs->0 floor: the C-relaxation is BELOW the lag resolution; the
                  s-dynamics are present in the response channel but the camera is too
                  coarse to resolve the correlation decay. No internal FDT anchor.
  QEC p=0.0012  : dC~1.0 and chi FLAT (~13) -> RFC-S 6 tau_obs->infinity: fully coarse-
                  grained, all structure migrated to r. The framework correctly reads r.

The Banach substrate (banach-substrate-reference.md) is the calibration RULER: its depth
nu IS tau_obs, and generate_locus(chit) traces the canonical c->s->r migration. Overlaying
it shows where each substrate's window sits on the migration. "Substrate inversion" is
placing tau_obs so the migration interior is in frame; only then can the five-vector fit
recover X. The fit is downstream of the camera placement.

Self-contained: the three substrate reads are pure mpa-central library JSON (no conform
pipeline). The Banach ruler vendors `generate_locus`/`vertex_regime` VERBATIM from
mpa-conform `conformer/compute/gfdr_model.py` (read 2026-05-21) so there is no live import.

Run: python H:/mpa-central/library/substrate_inversion_camera.py
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA = Path("H:/mpa-central/library/data")
OUT = Path("H:/mpa-central/library/output/diagnostics")
OUT.mkdir(parents=True, exist_ok=True)

# ---- VENDORED VERBATIM from mpa-conform/conformer/compute/gfdr_model.py (read 2026-05-21).
# The dialed-in canonical cdv1 leading-order forward model. Do not edit here; if the
# conform model changes, re-vendor. This is the Banach ruler's generator.
N_LOCUS_POINTS = 80


def vertex_regime(chit: float) -> str:
    if chit >= 0.7:
        return "deep_c"
    if chit >= 0.2:
        return "c_near_s"
    if chit > -0.2:
        return "s_critical"
    if chit > -0.7:
        return "r_near_s"
    return "deep_r"


def alpha_s(chit: float) -> float:
    return 0.5 + 0.3 * float(np.exp(-abs(chit) * 4))


def plateau_height(chit: float) -> float:
    return max(0.05, 1.0 - float(np.exp(-max(0.0, chit + 0.2) * 1.5)))


def generate_locus(chit: float, regime: str | None = None, n_points: int = N_LOCUS_POINTS) -> dict:
    if regime is None:
        regime = vertex_regime(chit)
    tau_min, tau_max = 0.01, 1000.0
    ts = np.linspace(0.0, 1.0, n_points)
    tau = tau_min * np.power(tau_max / tau_min, ts)
    C = np.zeros_like(tau); chi = np.zeros_like(tau)
    if regime in ("deep_c", "c_near_s"):
        depth = float(np.exp(-chit * 1.5))
        tau_c = 4.0 + 6.0 / max(0.1, chit)
        dC = 0.18 * depth * (1.0 - np.exp(-tau / tau_c))
        C = 1.0 - dC
        chi = (0.02 if regime == "deep_c" else 0.08) * dC
    elif regime == "s_critical":
        a = alpha_s(chit); P_s = plateau_height(chit)
        dC_short = (1.0 - P_s) * (1.0 - np.exp(-tau / 0.5))
        dC_long = P_s * (1.0 - np.power(1.0 + tau / 50.0, -a))
        dC = dC_short + dC_long
        C = 1.0 - dC
        chi = np.where(dC <= (1.0 - P_s), dC, (1.0 - P_s) + a * (dC - (1.0 - P_s)))
    else:  # r_near_s, deep_r
        tau_eq = max(0.5, 1.0 + 0.5 * float(np.exp(chit)))
        dC = 1.0 - np.exp(-tau / tau_eq)
        C = 1.0 - dC
        chi = dC
    return {"tau": tau, "C": C, "chi": chi}
# ---- end vendored block ----


def load_cell(rel):
    c = json.load(open(DATA / rel))
    s = sorted(c["results"]["all_samples"], key=lambda e: e["dt"])
    C = np.array([e["C_mean"] for e in s]); chi = np.array([e["chi_mean"] for e in s])
    op = c["operating_point"]
    return dict(dC=1.0 - C, C=C, chi=chi, T=op.get("T"), gt=op.get("gt"), label=op.get("label"))


REGIME_COL = {"deep_c": "#1f77b4", "c_near_s": "#2ca02c", "s_critical": "#d62728",
              "r_near_s": "#9467bd", "deep_r": "#7f7f7f"}


def main():
    glass = load_cell("glass/glass__T0.500__spin-flip.json")
    brain = load_cell("brain/brain__suspended__velocity.json")
    qec = load_cell("quantum/quantum__p1e-03__detection-event.json")
    subs = [("glass T=0.5", glass), ("brain suspended", brain), ("QEC p=0.0012", qec)]

    print("substrate        | gt | T     | dC range        | chi range        | tau_obs reading")
    print("-" * 96)
    readings = {
        "glass T=0.5": "MIGRATION INTERIOR  (FDT anchor in frame -> X recoverable)",
        "brain suspended": "tau_obs->0 FLOOR    (C-decay below resolution; chi still evolving)",
        "QEC p=0.0012": "tau_obs->inf        (migrated to r; chi flat)",
    }
    for name, d in subs:
        chi_trend = "evolving" if (d["chi"].max() - d["chi"].min()) > 0.3 * abs(d["chi"].mean()) else "flat"
        print(f"{name:>16} | {d['gt']:>2} | {str(d['T']):>5} | "
              f"{d['dC'].min():.3f}..{d['dC'].max():.3f} | "
              f"{d['chi'].min():7.3f}..{d['chi'].max():7.3f} ({chi_trend:>8}) | {readings[name]}")
    print("\nAll three are ground-truth gt='s'. Only glass's tau_obs catches the s-migration.")
    print("brain chi EVOLVING while dC pinned => s-dynamics present, C-channel unresolved (camera too fine-grained-blind).")
    print("QEC chi FLAT, dC~1 => genuinely migrated to r at this tau_obs.")

    chits = [1.0, 0.5, 0.3, 0.1, 0.0, -0.3, -0.7, -1.2]
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))

    # ---- LEFT: calibrated parametric plane + Banach ruler + glass overlay ----
    seen = set()
    for ch in chits:
        loc = generate_locus(ch); reg = vertex_regime(ch)
        lbl = reg if reg not in seen else None
        seen.add(reg)
        ax[0].plot(1.0 - loc["C"], loc["chi"], "-", color=REGIME_COL[reg], lw=1.4,
                   alpha=0.55, label=lbl)
    dl = np.linspace(0, 1, 50)
    ax[0].plot(dl, dl, "k--", lw=1.0, label="FDT line (X=1)")
    ax[0].plot(glass["dC"], glass["T"] * glass["chi"], "o", color="black", ms=6,
               label="glass T=0.5  (T·χ, calibrated)")
    ax[0].set_xlabel(r"$\Delta C = 1 - C$  (migration progress)")
    ax[0].set_ylabel(r"$T\cdot\chi$  (canonical FDT axis)")
    ax[0].set_title("Banach ruler (c→s→r canonical loci) + the one calibrated camera\n"
                    "glass (gt=s) lands ON the ruler, in the migration interior")
    ax[0].set_xlim(0, 1); ax[0].set_ylim(0, 1.05)
    ax[0].legend(fontsize=8, loc="upper left"); ax[0].grid(alpha=0.3)

    # ---- RIGHT: convention-free dC-coverage strip (where each camera is pointed) ----
    ax[1].axvspan(0.0, 0.5, color="#2ca02c", alpha=0.08)
    ax[1].axvspan(0.5, 0.9, color="#d62728", alpha=0.07)
    ax[1].axvspan(0.9, 1.0, color="#7f7f7f", alpha=0.13)
    ax[1].text(0.25, 3.55, "migration interior\n(FDT + aging onset)", ha="center", fontsize=8, color="#2ca02c")
    ax[1].text(0.70, 3.55, "decorrelating", ha="center", fontsize=8, color="#d62728")
    ax[1].text(0.95, 3.55, "fully\ndecorrelated\n(r)", ha="center", fontsize=7.5, color="#555")
    ys = {"glass T=0.5": 3, "brain suspended": 2, "QEC p=0.0012": 1}
    bar_col = {"glass T=0.5": "black", "brain suspended": "tab:orange", "QEC p=0.0012": "tab:purple"}
    for name, d in subs:
        y = ys[name]
        ax[1].plot([d["dC"].min(), d["dC"].max()], [y, y], "-", color=bar_col[name], lw=9, alpha=0.85,
                   solid_capstyle="butt")
        ax[1].plot(d["dC"], [y] * len(d["dC"]), "|", color="white", ms=10, mew=1.2)
        ax[1].text(0.02, y + 0.22, name, fontsize=9, color=bar_col[name], weight="bold")
        ax[1].text(0.02, y - 0.30, readings[name].split("(")[0].strip(), fontsize=7.5, color="#444")
    ax[1].set_xlim(0, 1.02); ax[1].set_ylim(0.3, 3.9)
    ax[1].set_yticks([]); ax[1].set_xlabel(r"$\Delta C = 1 - C$  (convention-free; no χ calibration needed)")
    ax[1].set_title("where each τ_obs camera is pointed on the migration\n"
                    "all gt=s — but brain/QEC are parked at the decorrelated tail")
    ax[1].grid(alpha=0.3, axis="x")

    fig.suptitle("Substrate inversion: aiming the τ_obs camera (RFC-S) against the Banach ruler", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    png = OUT / "substrate_inversion_camera.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
