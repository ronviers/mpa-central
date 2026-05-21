"""k_frust ladder -- MOVE A: is the cyclic-current invariant SPECIFIC to the
framework's NAMED frustration, or does it measure something else?

cdv1 fuses two vocabularies for k_frust:
  * NOTION 1 (named): "spin-glass loop / UNSAT / gridlock" -- signed-graph
    frustration, a property of the SYMMETRIC sign pattern of the couplings
    (the all-competitive triangle: every pair wants to differ, none can be
    satisfied). This is the textbook frustrated triangle.
  * NOTION 2 (operationalized): a drive-independent Schnakenberg CYCLIC CURRENT
    (broken detailed balance) -- the bulletproof J meter. This is a property of
    the ANTISYMMETRIC / NON-RECIPROCAL part of the coupling (rock-paper-scissors).

These are different objects. A symmetric coupling has a symmetric Jacobian ->
REAL spectrum -> NO cyclic current (J=0), no matter how frustrated its sign
pattern. A non-reciprocal coupling has a complex spectrum -> J!=0, even when its
sign pattern is perfectly balanced (unfrustrated).

KILL-SHOT: if J tracks the ANTISYMMETRIC part (non-reciprocity) and is BLIND to
signed-graph frustration -- i.e. the canonical spin-glass/UNSAT triangle reads
J~0 while a balanced non-reciprocal loop reads J!=0 -- then the campaign's
"k_frust invariant" measures non-reciprocal cyclic dominance, NOT the spin-glass
frustration the framework names. The two co-named phenomena diverge.

Five 3-mode couplings (gamma_ij>0 = competitive/conflicting per the cdv1 catalogue):
  RPS        antisymmetric cyclic            -- the meter's "frustrated loop" (notion 2 only)
  AFM        symmetric all-competitive       -- the NAMED spin-glass/UNSAT triangle (notion 1 only)
  COOP       symmetric all-cooperative       -- unfrustrated, reciprocal (neither)
  NR-COOP    cooperative + antisymmetric     -- non-reciprocal but signed-graph BALANCED (notion 2, not 1)
  NR-AFM     competitive + antisymmetric     -- both

Run: python H:/mpa-central/library/k_frust_A_specificity.py
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from k_frust_r1_sweep import step, cyclic_J, CYC, SYM

OUT = Path("H:/mpa-central/library/output/diagnostics")
G0, L, SIGMA, GMAG = 1.20, 1.00, 0.02, 0.50
N_REAL, T_EQ, T_OBS = 256, 4000, 8000
SEEDS = [1, 2, 3, 4]


def measure_J(gmat, seed):
    rng = np.random.default_rng(seed)
    rho = np.tile([0.06, 0.03, 0.01], (N_REAL, 1)).astype(float)
    for _ in range(T_EQ):
        rho = step(rho, gmat, G0, L, SIGMA, rng)
    chir = np.zeros(T_OBS); winner = np.zeros(T_OBS)
    for t in range(T_OBS):
        rp = rho.copy()
        rho = step(rho, gmat, G0, L, SIGMA, rng)
        chir[t] = cyclic_J(rho, rp)
        m = rho.mean(0)                                  # ensemble mean per mode
        winner[t] = (m.max() - m.min()) / (m.mean() + 1e-12)   # symmetry-breaking (competitive exclusion)
    return float(np.mean(chir)), float(np.mean(winner[T_OBS // 2:]))


def jacobian_spectrum(gmat):
    """Coexistence-Jacobian spectrum at the symmetric fixed point (numeric)."""
    def drift(rho):
        S = rho.sum(); gain = G0 / (1.0 + S)
        return (gain - L) * rho - rho * (gmat @ rho) + 1e-3
    c = 0.07
    for _ in range(200):
        r = drift(np.full(3, c))[0]
        dr = (drift(np.full(3, c + 1e-6))[0] - r) / 1e-6
        c = max(c - r / dr, 1e-6)
    rs = np.full(3, c); J = np.zeros((3, 3)); f0 = drift(rs)
    for j in range(3):
        rp = rs.copy(); rp[j] += 1e-6
        J[:, j] = (drift(rp) - f0) / 1e-6
    ev = np.linalg.eigvals(J)
    return float(np.max(np.abs(ev.imag)))


def signed_graph_frustrated(sym_part):
    """Triangle frustration of the SYMMETRIC sign pattern. gamma>0 = competitive
    (anti-align, AFM-like bond). Frustrated iff the product of the 3 competitive
    bond signs is negative (odd # of frustrating bonds)."""
    s = [np.sign(sym_part[0, 1]), np.sign(sym_part[1, 2]), np.sign(sym_part[0, 2])]
    # competitive (gamma>0) = AFM bond (sign -1 in spin convention); cooperative (gamma<0) = FM (+1)
    spin_bonds = [-x for x in s]                          # map competitive(+)->AFM(-1)
    prod = np.prod([b if b != 0 else 1 for b in spin_bonds])
    return prod < 0


def main():
    G = GMAG
    systems = {
        "RPS (antisym cyclic)":      G * CYC,
        "AFM (sym all-competitive)": G * SYM,
        "COOP (sym all-cooperative)": -G * SYM,
        "NR-COOP (coop + antisym)":  -G * SYM + G * CYC,
        "NR-AFM (compet + antisym)":  G * SYM + G * CYC,
    }
    print(f"{'system':>28} | {'|antisym|':>9} {'|sym|':>7} | {'sg-frust':>8} | {'|Im(eig)|':>9} | "
          f"{'J':>11} {'+/-':>9} | {'sym-break':>9}")
    rows = []
    for name, g in systems.items():
        np.fill_diagonal(g, 0.0)
        anti = 0.5 * (g - g.T); sym = 0.5 * (g + g.T)
        a_norm = float(np.linalg.norm(anti)); s_norm = float(np.linalg.norm(sym))
        sgf = signed_graph_frustrated(sym)
        imag = jacobian_spectrum(g)
        Js = np.array([measure_J(g, s) for s in SEEDS])
        J, sd = Js[:, 0].mean(), Js[:, 0].std(ddof=1)
        win = Js[:, 1].mean()
        rows.append(dict(name=name, a=a_norm, s=s_norm, sgf=sgf, imag=imag, J=J, sd=sd, win=win))
        print(f"{name:>28} | {a_norm:>9.3f} {s_norm:>7.3f} | {str(sgf):>8} | {imag:>9.4f} | "
              f"{J:>+11.4e} {sd:>9.1e} | {win:>9.3f}")

    print("\n================ MOVE A VERDICT ================")
    # J should track |antisym| (non-reciprocity), NOT signed-graph frustration
    afm = next(r for r in rows if r["name"].startswith("AFM"))
    nrcoop = next(r for r in rows if r["name"].startswith("NR-COOP"))
    rps = next(r for r in rows if r["name"].startswith("RPS"))
    afm_silent = abs(afm["J"]) < 5e-3
    balanced_circulates = abs(nrcoop["J"]) > 5e-3 and not nrcoop["sgf"]
    if afm_silent and balanced_circulates:
        print("KILL: the cyclic-current meter is BLIND to signed-graph (spin-glass/UNSAT) frustration")
        print(f"  and FIRES on non-reciprocity. The NAMED spin-glass triangle (AFM, sg-frustrated) reads")
        print(f"  J={afm['J']:+.2e} (~0); a BALANCED but non-reciprocal loop (NR-COOP, NOT sg-frustrated)")
        print(f"  reads J={nrcoop['J']:+.2e}. So the campaign's 'k_frust invariant' measures non-reciprocal")
        print("  cyclic dominance (rock-paper-scissors), NOT the spin-glass/UNSAT frustration cdv1 names.")
        print("  -> the §gFDR 'spin-glass loop signature' identification and the cyclic-current meter")
        print("     point at DIFFERENT objects. The naming over-claims; a notion-split is owed.")
    else:
        print(f"  AFM J={afm['J']:+.2e} (silent={afm_silent}); NR-COOP J={nrcoop['J']:+.2e} "
              f"(balanced-circulates={balanced_circulates}). Meter specificity not cleanly broken.")

    # figure: J vs |antisym|, marker = signed-graph frustration
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    for r in rows:
        mk = "X" if r["sgf"] else "o"
        ax[0].errorbar(r["a"], abs(r["J"]), yerr=r["sd"], fmt=mk, ms=11, capsize=3)
        ax[0].annotate(r["name"].split()[0], (r["a"], abs(r["J"])), fontsize=8,
                       xytext=(5, 5), textcoords="offset points")
    ax[0].set_xlabel("|antisymmetric part of gamma| (non-reciprocity)")
    ax[0].set_ylabel("|cyclic current J|")
    ax[0].set_title("J tracks NON-RECIPROCITY (X = signed-graph 'spin-glass' frustrated)")
    ax[0].grid(alpha=0.3)
    labels = [r["name"].split()[0] for r in rows]
    ax[1].bar(range(len(rows)), [abs(r["J"]) for r in rows],
              color=["tab:red" if r["sgf"] else "tab:blue" for r in rows], alpha=0.75)
    ax[1].set_xticks(range(len(rows))); ax[1].set_xticklabels(labels, rotation=20, fontsize=8)
    ax[1].set_ylabel("|cyclic current J|")
    ax[1].set_title("RED = the NAMED spin-glass/UNSAT (sg-frustrated) systems\n(should the meter not fire hardest HERE?)")
    ax[1].grid(alpha=0.3)
    fig.suptitle("Move A: does the k_frust J-meter measure spin-glass frustration, or non-reciprocity?", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    png = OUT / "k_frust_A_specificity.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
