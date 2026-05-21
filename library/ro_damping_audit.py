"""mpa-LEGAL audit: the smuggled constant in cdv1 receipts §13.

Receipts §13 states (verbatim): "gamma_RO = gamma_s/2 ... substrate-FIXED, while
omega_RO tracks the chit." That is a damping RATE declared constant -- it does not
flow with the operating point. Two tests:

(1) CHARACTER LEGALITY. Character is NESS-against-a-bath; everything dissipates /
    is maintained / flows. An inert constant (operating-point-independent) is
    foreign (the char-zero is a square wave, not a constant; the literal 'constant'
    substrate sits below the floor). A frozen damping rate fails this.

(2) LASER FIDELITY (the physics §13 cites). Derive gamma_RO from the class-B rate
    equations directly:
        n_dot = (G N - kappa) n ,   N_dot = P - gamma_par N - G N n .
    Linearize at steady state (G N* = kappa, stimulated rate G n* = gamma_par(r-1),
    r = pump ratio = G0/L = e^chit):
        J = [[0, G n*], [-kappa, -(gamma_par + G n*)]]
        gamma_RO = (gamma_par + G n*)/2 = (gamma_par/2) * r = (gamma_s/2) e^chit
        omega_RO^2 = det(J) - gamma_RO^2 ;  det(J) = kappa * G n* = kappa gamma_par (r-1)
    So the LEGAL damping rate carries the pump-ratio factor r = e^chit -- it FLOWS
    with the operating point. cdv1 dropped that factor and froze it at the r=1
    (threshold) value gamma_s/2.

Consequence checked here: cdv1-as-written gives Q monotically increasing in chit
(unbounded 'many cycles deep in c'); the LEGAL form gives a NON-MONOTONIC Q that
peaks at intermediate chit and ->0 at BOTH the s-threshold and deep-c -- i.e. the
relaxation-oscillation ringing lives in a BAND, overdamped at both ends, which is
the standard class-B laser result. The constant is both illegal AND wrong.

Run: python H:/mpa-central/library/ro_damping_audit.py
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
OUT.mkdir(parents=True, exist_ok=True)
GAMMA_S, L = 1.0, 1.0   # canonical scale (shape is what matters)


def observables(chit):
    e = np.exp(chit) - 1.0
    omega = np.sqrt(np.maximum(2.0 * GAMMA_S * L * e, 0.0))     # same for both readings
    g_const = GAMMA_S / 2.0                                     # cdv1 as-written (frozen)
    g_legal = (GAMMA_S / 2.0) * np.exp(chit)                    # class-B: gamma_RO ∝ pump ratio r
    return omega, g_const, g_legal


def zeta_Q(omega, g):
    zeta = np.where(omega > 1e-9, g / np.maximum(omega, 1e-9), np.inf)
    Q = np.where(omega > 1e-9, omega / (2.0 * g), 0.0)
    return zeta, Q


def main():
    chit = np.linspace(0.005, 4.0, 1000)
    omega, gc, gl = observables(chit)
    zc, Qc = zeta_Q(omega, gc)
    zl, Ql = zeta_Q(omega, gl)

    # critical-damping points (zeta=1) for the legal form: (gamma_s/2)e^chit = omega
    # -> (1/4)e^{2chit} = 2(e^chit-1) -> x^2 - 8x + 8 = 0, x=e^chit (for gamma_s=L=1)
    xs = np.roots([1, -8, 8])
    crit_legal = sorted(np.log(x) for x in xs if x > 1)
    crit_const = np.log(1.0 + (GAMMA_S / (8.0 * L)))            # single zeta=1 point as-written
    chit_peakQ = chit[np.argmax(Ql)]

    print("mpa-LEGAL audit of receipts §13  (gamma_s = L = 1)\n")
    print(f"{'chit':>6} | {'omega_RO':>9} | {'gamma_RO const':>14} {'Q const':>8} {'zeta const':>10} |"
          f" {'gamma_RO legal':>14} {'Q legal':>8} {'zeta legal':>10}")
    for c in [0.02, 0.12, 0.50, 1.0, 1.92, 3.0]:
        w, g0, g1 = observables(c)
        z0, q0 = zeta_Q(w, g0); z1, q1 = zeta_Q(w, g1)
        print(f"{c:>6.2f} | {w:>9.4f} | {g0:>14.3f} {q0:>8.3f} {z0:>10.3f} |"
              f" {g1:>14.3f} {q1:>8.3f} {z1:>10.3f}")

    print("\n================ mpa-LEGAL VERDICT ================")
    print("(1) ILLEGAL: receipts §13 freezes gamma_RO = gamma_s/2 'substrate-fixed' -- an inert")
    print("    damping rate that does not flow with the operating point. Foreign to character.")
    print("(2) WRONG PHYSICS: the class-B rate equations §13 cites give gamma_RO = (gamma_s/2) e^chit")
    print(f"    (pump-ratio factor r=e^chit). The frozen form dropped it.")
    print(f"AS-WRITTEN (constant): one critical-damping point chit*={crit_const:.3f}, then UNDERDAMPED")
    print(f"    forever -- Q grows without bound deep in c ('many cycles of headroom'). Unphysical.")
    print(f"LEGAL (flowing): TWO critical-damping points chit = [{crit_legal[0]:.3f}, {crit_legal[1]:.3f}];")
    print(f"    underdamped RINGING only in that BAND (peak Q at chit={chit_peakQ:.3f}); OVERDAMPED at")
    print(f"    BOTH ends -- s-threshold (critical SLOWING) and deep-c (RO damps out). Standard class-B.")
    print("CASCADE: cdv1 §Stability 'deep c -> many cycles (high Q)' and §17 active-probe S/N=Q both")
    print("    inherit the monotonic artifact. Legal Q is non-monotonic -> those readings need revisit.")
    print("FIX (character-legal + laser-faithful): gamma_RO = (gamma_s/2) e^chit (= (gamma_s/2) G0/L),")
    print("    which FLOWS with chit. No constant. Recompute Q, zeta, §Stability damping table, §17.")

    fig, ax = plt.subplots(1, 2, figsize=(14, 5.5))
    ax[0].plot(chit, Qc, color="tab:red", lw=2, label="Q as-written (gamma_RO=gamma_s/2 CONST)")
    ax[0].plot(chit, Ql, color="tab:green", lw=2, label="Q LEGAL (gamma_RO=(gamma_s/2)e^chit)")
    ax[0].axhline(0.5, color="gray", ls="--", lw=1, label="Q=1/2 (critical damping)")
    ax[0].plot(chit_peakQ, Ql.max(), "v", color="tab:green", ms=10)
    ax[0].set_xlabel("chit"); ax[0].set_ylabel("Q (RO quality factor)")
    ax[0].set_title("Smuggled constant: monotonic-unbounded Q (red, wrong)\nvs flowing: non-monotonic banded Q (green, class-B)")
    ax[0].set_ylim(0, 4); ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3)

    ax[1].semilogy(chit, np.clip(zc, 1e-2, 1e3), color="tab:red", lw=2, label="zeta as-written (CONST)")
    ax[1].semilogy(chit, np.clip(zl, 1e-2, 1e3), color="tab:green", lw=2, label="zeta LEGAL (flowing)")
    ax[1].axhline(1.0, color="k", ls="--", lw=1, label="zeta=1 (critical DAMPING)")
    for cc in crit_legal:
        ax[1].axvline(cc, color="tab:green", ls=":", lw=1)
    ax[1].axvspan(crit_legal[0], crit_legal[1], color="tab:green", alpha=0.08, label="LEGAL underdamped ringing band")
    ax[1].set_xlabel("chit"); ax[1].set_ylabel("zeta (log)")
    ax[1].set_title("Legal zeta: overdamped at BOTH ends (s-slowing & deep-c),\nringing only in the band. Const: underdamped-forever-deep-c")
    ax[1].set_ylim(0.05, 50); ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3, which="both")
    fig.suptitle("mpa-legal audit: the §13 'gamma_RO=gamma_s/2 substrate-fixed' constant is illegal AND wrong (class-B)",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    png = OUT / "ro_damping_audit.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
