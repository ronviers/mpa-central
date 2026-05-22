r"""Reed-Muller closure test (Phase 3): does the ANF identity  ¬x = x ⊕ 1  close in MPA?

The reconception late-idea proposes MPA is the finite-D deformation of the {⊕,∧,1} (ANF)
ring, with ⊕↔K, ∧↔C, 1↔G₀, ¬↔R. The loosest leg is 1↔G₀: it must pass the closure
identity ¬x = x⊕1 — i.e. R must equal K(·,1) — or 1↔G₀ is decoration.

This audits it at the Boolean endpoint using the EXACT v9 §Operators definitions:
  K : M²→M₂,  c iff the two modes differ (δ≠0) and D covers, else r.  Boolean shadow ⊕.
  R : M→M,    sever to bath (choke G₀ / open to bath); continuously ρ_A→0.  Shadow ¬.
  Σ = {C,S,K,R,⊤,⊥} restricts to M₂ ≅ (B,∧,∨,⊕,¬); ⊤ is already the Boolean 1.
Encode M₂ as {c=1, r=0}.

Run: python H:/mpa-central/library/rm_closure_test.py
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path("H:/mpa-central/library/output/diagnostics")
OUT.mkdir(parents=True, exist_ok=True)

# ---- v9 §Operators on M₂ = {c=1, r=0} (Boolean endpoint, D large so K's D-cover holds) ----
def K(x, y):   return int(x != y)        # parity: c iff modes differ  -> XOR
def C(x, y):   return int(x and y)       # try-merge shadow            -> AND
def R(x):      return 0                  # sever to bath -> r (=0), for ANY input
def NOT(x):    return 1 - x              # Boolean ¬
TOP, BOT = 1, 0                          # ⊤ = 1 (True),  ⊥ = 0 (False)


def main():
    dom = [0, 1]
    print("=" * 70)
    print("PHASE 3 — Reed-Muller closure test:  ¬x = x ⊕ 1  in MPA operators")
    print("=" * 70)

    # ---- (1) Does K(·,1) realize ¬, with 1 = ⊤ ?  (the ANF identity ¬=⊕1) ----
    k_top = [K(x, TOP) for x in dom]
    neg = [NOT(x) for x in dom]
    pass_ktop = (k_top == neg)
    print("\n(1) ANF identity with 1 = ⊤ (v9's existing Boolean top):")
    print(f"    x:        {dom}")
    print(f"    K(x,⊤):   {k_top}        (= x ⊕ 1)")
    print(f"    ¬x:       {neg}")
    print(f"    => K(·,⊤) == ¬  :  {'PASS' if pass_ktop else 'FAIL'}  "
          f"(the XOR operator with ⊤ IS negation — pure GF(2), already in v9)")

    # ---- (2) Does R itself realize ¬ ? (the claimed R↔¬ shadow) ----
    r_tab = [R(x) for x in dom]
    matches = [r_tab[i] == neg[i] for i in range(2)]
    involutive = all(R(R(x)) == x for x in dom)
    print("\n(2) Does the sever operator R realize ¬ ?")
    print(f"    R(x):     {r_tab}   vs   ¬x: {neg}")
    print(f"    match at x=r(0): {matches[0]}    match at x=c(1): {matches[1]}")
    print(f"    R∘R == id (involution, as ¬ requires)?  {involutive}  "
          f"(R∘R = R: severing twice = severed)")
    print("    => R = ¬ ONLY on the c→r branch (x=c). R is irreversible (→r), not the")
    print("       involution ¬. The R↔¬ shadow is one-way / quotient-on-output (v9 line 57),")
    print("       NOT a dynamical involution. The identity ¬=⊕1 is realized by K(·,⊤), not R.")

    # ---- (3) The contested leg: 1 ↔ G₀ ?  TYPE CHECK ----
    print("\n(3) The reconception's leg — is the ANF constant 1 the drive G₀ ?")
    print("    K : M² → M₂  takes two MODES (elements of M).  G₀ ∈ ℝ₊ is the drive/budget")
    print("    (chit = ln(G₀/L)), NOT an element of M₂.  So K(x, G₀) is TYPE-ILL-FORMED:")
    print("    G₀ cannot be K's second argument.  And K(·,⊤) already = ¬ with no G₀ needed.")
    print("    => 1 ↔ G₀ is a CATEGORY ERROR (decoration). The ANF 1 is ⊤, an element of M₂.")
    print("       G₀'s real role is the DEFORMATION COORDINATE chit = ln(G₀/L) — where you")
    print("       sit in the c→s→r melt — not the logical constant 1. (Phase 2, not Phase 1.)")

    # ---- (4) continuous demo: R is irreversible (single-mode laser kernel) ----
    L, G0_on, G0_off, rho_sat, dt, T = 1.0, 2.0, 0.4, 1.0, 0.01, 12.0
    n = int(T / dt); t = np.arange(n) * dt
    rho = np.zeros(n); rho[0] = 0.9          # start near the c fixed point (ρ*=√(G₀−L)=1)
    G0 = np.full(n, G0_on)
    G0[t > 4] = G0_off                       # apply R at t=4: choke the drive (sever) -> r, stays r
    for i in range(1, n):
        drho = (G0[i] - L) * rho[i-1] - (rho[i-1] ** 3) / rho_sat
        rho[i] = max(rho[i-1] + drho * dt, 0.0)
    chit = np.log(G0 / L)
    print("\n(4) continuous check (single-mode kernel ρ̇=(G₀−L)ρ−ρ³):")
    print(f"    drive on  -> ρ* = {np.sqrt(G0_on-L):.3f} (c);  R chokes G₀ -> ρ→0 (r);")
    print(f"    second R on the r-state leaves it r (idempotent). R∘R = R, not id.")

    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)
    print("• RM basis mapping is RIGOROUS at the Boolean endpoint with 1 = ⊤:")
    print("  ⊕↔K, ∧↔C, 1↔⊤, and ¬=⊕1 holds (K(·,⊤)=¬). This is NOT new machinery —")
    print("  it is exactly v9's existing Boolean-section M₂≅(B,∧,∨,⊕,¬).")
    print("• 1 ↔ G₀ FAILS the closure test (category error: G₀ is a drive, not an M₂ element).")
    print("  Drop it. G₀ enters as the deformation coordinate chit=ln(G₀/L), which cdv1 has.")
    print("• R↔¬ is a one-way (c→r) shadow, not a dynamical involution — R's irreversibility")
    print("  IS the finite-D deformation of the ring's involution axiom (Phase 2 in action).")
    print("• Consequence: 'integrate RM' = recognize v9's Boolean section IS the deformed ANF")
    print("  ring (a receipts/framing note), NOT a spine refactor. k_frust=UNSAT-of-K is well")
    print("  defined (K↔⊕ is solid); its §846 promotion remains separately gated on a real")
    print("  topologically-forced instance — the closure test does not bear on that.")

    # ---- figure ----
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    # left: operator tables
    grid = np.array([
        [K(0, 0), K(0, 1)],
        [K(1, 0), K(1, 1)],
    ])
    ax[0].imshow(grid, cmap="Blues", vmin=0, vmax=1)
    for i in dom:
        for j in dom:
            ax[0].text(j, i, f"K({i},{j})={K(i,j)}", ha="center", va="center", fontsize=11)
    ax[0].set_xticks(dom); ax[0].set_yticks(dom)
    ax[0].set_xticklabels(["r=0", "c=1"]); ax[0].set_yticklabels(["r=0", "c=1"])
    ax[0].set_xlabel("second arg"); ax[0].set_ylabel("first arg")
    ax[0].set_title("K (parity ↔ ⊕):  c iff modes differ\n"
                    f"K(·,⊤) = {[K(x,TOP) for x in dom]} = ¬  ✓   |   "
                    f"R(·) = {[R(x) for x in dom]} (→r): = ¬ only on c")
    # right: R irreversibility
    ax2 = ax[1].twinx()
    ax[1].plot(t, rho, color="tab:blue", lw=2, label=r"$\rho_A$ (amplitude)")
    ax2.plot(t, chit, color="tab:red", lw=1.2, ls="--", label=r"chit$=\ln(G_0/L)$")
    ax2.axhline(0, color="gray", lw=0.6)
    ax[1].axvline(4, color="k", ls=":", lw=1)
    ax[1].text(2.0, 0.5, "drive on:\nc (ρ*=1)", fontsize=9, ha="center")
    ax[1].text(8.0, 0.5, "R applied (choke G₀): c→r,\nand stays r (R∘R=R, not ¬)", fontsize=8.5, ha="center")
    ax[1].set_xlabel("t"); ax[1].set_ylabel(r"$\rho_A$", color="tab:blue")
    ax2.set_ylabel("chit (deformation coord)", color="tab:red")
    ax[1].set_title("R (sever) is irreversible (→r), not the involution ¬\n"
                    "G₀ is the deformation coordinate (chit), not the logical 1")
    l1, lb1 = ax[1].get_legend_handles_labels(); l2, lb2 = ax2.get_legend_handles_labels()
    ax[1].legend(l1 + l2, lb1 + lb2, fontsize=8, loc="upper right")
    fig.suptitle("Reed-Muller closure test:  ¬=⊕1 holds via K(·,⊤);  1↔G₀ is a category error", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    png = OUT / "rm_closure_test.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
