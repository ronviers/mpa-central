"""Is MPA fixed? Re-run the damping check against cdv1 AS IT NOW STANDS.

Before: cdv1 §Stability froze γ_RO=γ_s/2 -> Q monotonic-unbounded, diverging from
the class-B laser. After the mpa-legal correction (pasted): cdv1 carries the exact
forms γ_RO=(γ_s/2)e^chit, ω_RO=√[2Lγ_s(e^chit−1)−(γ_s/2)²e^{2chit}],
Q=√[2L(e^chit−1)/γ_s − e^{2chit}/4]·e^{−chit}.

Three curves vs the SAME class-B laser Jacobian ground truth:
  GROUND TRUTH  -- exact Q from the class-B laser Jacobian eigenvalues.
  cdv1 OLD      -- frozen γ_RO=γ_s/2 (the bug): Q=√(2L(e^chit−1)/γ_s).
  cdv1 NOW      -- the pasted exact forms.
If 'cdv1 NOW' lands on GROUND TRUTH (and OLD is the monotonic outlier), MPA is fixed.

Params consistent with laser_conform_Q.py: laser cavity loss κ=1 (intensity), and
Model B's pinning κ=2L => L=0.5 (amplitude); γ_s=0.10.

Run: python H:/mpa-central/library/ro_damping_fixed_check.py
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path("H:/mpa-central/library/output/diagnostics")
GAMMA_S, KAPPA = 0.10, 1.0       # laser intensity-loss cavity rate
L = KAPPA / 2.0                  # Model B pin: amplitude rate L = κ/2


def Q_ground_truth(chit):
    """Exact class-B laser Jacobian: J=[[0,Gn*],[-κ,-(γ_∥+Gn*)]], Gn*=γ_s(e^chit−1)."""
    Gn = GAMMA_S * (np.exp(chit) - 1.0)
    J = np.array([[0.0, Gn], [-KAPPA, -(GAMMA_S + Gn)]])
    ev = np.linalg.eigvals(J)
    g = -ev.real.mean(); w = np.max(np.abs(ev.imag))
    return (w / (2 * g)) if (g > 0 and w > 0) else 0.0


def Q_cdv1_old(chit):            # frozen γ_RO=γ_s/2 (the bug)
    return np.sqrt(np.maximum(2 * L * (np.exp(chit) - 1.0) / GAMMA_S, 0.0))


def Q_cdv1_now(chit):            # pasted exact form
    inside = 2 * L * (np.exp(chit) - 1.0) / GAMMA_S - np.exp(2 * chit) / 4.0
    return np.sqrt(inside) * np.exp(-chit) if inside > 0 else 0.0


def main():
    chits = np.linspace(0.02, 2.4, 300)
    gt = np.array([Q_ground_truth(c) for c in chits])
    old = np.array([Q_cdv1_old(c) for c in chits])
    now = np.array([Q_cdv1_now(c) for c in chits])

    band = chits[now > 1e-9]
    resid = np.max(np.abs(now[gt > 1e-9] - gt[gt > 1e-9]))
    print(f"params: γ_s={GAMMA_S}, κ={KAPPA}, L=κ/2={L}\n")
    print(f"{'chit':>6} | {'GROUND TRUTH':>12} | {'cdv1 OLD (frozen)':>17} | {'cdv1 NOW (fixed)':>16}")
    for c in [0.05, np.log(2), 0.80, 1.20, 1.80, 2.30]:
        print(f"{c:>6.3f} | {Q_ground_truth(c):>12.4f} | {Q_cdv1_old(c):>17.4f} | {Q_cdv1_now(c):>16.4f}")
    print(f"\npeak(GT) at chit={chits[np.argmax(gt)]:.3f} (ln2={np.log(2):.3f}); "
          f"peak(NOW) at chit={chits[np.argmax(now)]:.3f}")
    print(f"max |cdv1_NOW − GROUND_TRUTH| over the live band = {resid:.2e}")
    if resid < 1e-9:
        print("\n================ FIXED ================")
        print("cdv1 NOW reproduces the class-B laser Jacobian Q(chit) to machine precision.")
        print("The corrected forms ARE the laser eigenstructure (κ=2L). The frozen-γ_RO OLD curve")
        print("is the monotonic-unbounded outlier we removed. Non-monotonic, peaks at chit=ln2,")
        print("overdamped at both ends -- matches physics. The smuggled constant is gone.")
    else:
        print(f"\nNOT exactly coincident (resid={resid:.2e}) -- inspect (param mismatch or residual term).")

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(chits, old, color="tab:red", lw=2, label="cdv1 OLD (frozen γ_RO) — monotonic, the bug")
    ax.plot(chits, gt, color="tab:green", lw=4, alpha=0.45, label="class-B laser Jacobian — GROUND TRUTH")
    ax.plot(chits, now, color="tab:blue", lw=1.8, ls="--", label="cdv1 NOW (pasted exact forms)")
    ax.axvline(np.log(2), color="gray", ls=":", lw=1, label="chit=ln2 (Q peak)")
    ax.set_xlabel("chit = ln(G₀/L)"); ax.set_ylabel("Q (RO quality factor)")
    ax.set_title(f"Is MPA fixed? cdv1 NOW (blue dashed) lands on the laser ground truth (green);\n"
                 f"OLD frozen-γ_RO (red) was the monotonic outlier.  max|NOW−GT|={resid:.1e}")
    ax.set_ylim(0, max(old.max(), gt.max()) * 1.05); ax.legend(fontsize=9); ax.grid(alpha=0.3)
    fig.tight_layout()
    png = OUT / "ro_damping_fixed_check.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
