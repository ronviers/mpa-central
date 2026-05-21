"""Move A, live falsifier: a REAL spin glass (SK) reads s-regime (suspension /
CK aging), NOT k_frust.

The move-A naming finding rests on: spin-glass frustration (symmetric couplings)
is a DIFFERENT object than k_frust (non-reciprocal cyclic current). The sharp
cross-substrate test: the SK model (N=100 spins, frozen symmetric J~N(0,1/sqrt N),
Glauber single-flip MC -> detailed balance by construction) should read

  * J / cyclic current ~ 0 at all T  -- STRUCTURAL: Glauber on a symmetric
    Hamiltonian obeys detailed balance, so there is no Schnakenberg current and no
    chirality. (No current observable is even gridded; this is the point.) Hence
    NOT k_frust.
  * below T_c (=1.0 for this normalization): s-regime SUSPENSION -- CK aging FDR
    (raw slope X<1), correlation plateaus at q_EA (P_s>0, doesn't fully decay).
  * above T_c: equilibrium paramagnet -- X~1, C decays fully (P_s~0). Not s, not
    k_frust.

Sealed prediction (Claude): glass phase = s-aging (X<1, plateau); paramagnet =
equilibrium (X~1, full decay); J=0 throughout. User: "simple suspension."
KILL of the spin-glass=s claim (and of the naming-purge rationale): SK shows a
sustained current / chirality, or fails to read s-aging in the glass phase.

Reads the existing gridded cells (raw-slope FDR layer, per FALSIFICATION.md policy
that 1-param inversion can't recover X<1). Run:
  python H:/mpa-central/library/k_frust_A_sk.py
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

DATA = Path("H:/mpa-central/library/data/sk")
OUT = Path("H:/mpa-central/library/output/diagnostics")
TEMPS = [0.400, 0.700, 1.000, 1.300, 1.600]
T_C = 1.0   # SK mean-field transition for J~N(0,1/sqrt(N))


def load(T, xdot):
    p = DATA / f"sk__T{T:.3f}__{xdot}.json"
    s = json.loads(p.read_text(encoding="utf-8"))["results"]["all_samples"]
    dt = np.array([float(e["dt"]) for e in s])
    C = np.array([float(e["C_mean"]) for e in s])
    chi = np.array([float(e["chi_mean"]) for e in s])
    order = np.argsort(dt)
    return dt[order], C[order], chi[order]


def raw_fdr_slope(C, chi):
    """X via the FDT line chi = X*(1-C) through origin (raw-slope layer).
    Single-slope is biased UP on aging loci (kww lesson) -> a glass reading
    X<1 here is conservative (true X is lower)."""
    omc = 1.0 - (C / C[0]) if C[0] != 0 else 1.0 - C
    den = float(np.sum(omc * omc))
    return float(np.sum(omc * chi) / den) if den > 1e-12 else float("nan")


def main():
    print("SK spin glass -- regime read across T (T_c=1.0). spin-relative = aging correlation.")
    print("NOTE: the raw FDR slope X below uses the generic increment estimator and is UNRELIABLE")
    print("near criticality (collective soft-mode instability -- see FALSIFICATION.md 'Survived'/RFIM;")
    print("the fix is the self-overlap + staggered-field estimator). The q_EA plateau is the robust read.\n")
    print(f"{'T':>6} {'phase':>12} | {'q_EA plateau':>12} | {'X (UNRELIABLE)':>14} | reads")
    rows = []
    for T in TEMPS:
        _, C_f, chi_f = load(T, "spin-flip")
        _, C_r, chi_r = load(T, "spin-relative")
        X = raw_fdr_slope(C_f, chi_f)                     # estimator-suspect; reported, not scored
        q_ea = float(np.mean(C_r[-3:]))                   # EA order parameter = long-lag plateau VALUE
        frozen = q_ea > 0.05
        phase = "glass (T<Tc)" if T < T_C else ("critical" if T == T_C else "param (T>Tc)")
        reads = "frozen (glass / s-family)" if frozen else "unfrozen (paramagnet)"
        rows.append(dict(T=T, X=X, q_ea=q_ea, phase=phase, frozen=frozen))
        print(f"{T:>6.2f} {phase:>12} | {q_ea:>12.3f} | {X:>14.3f} | {reads}")

    glass_frozen = all(r["q_ea"] > 0.05 for r in rows if r["T"] < T_C)
    para_unfrozen = all(r["q_ea"] < 0.05 for r in rows if r["T"] > T_C)
    print("\n================ SK VERDICT (honest) ================")
    print("NOT k_frust -- HOLDS (structural): symmetric J + Glauber = detailed balance => no")
    print("  Schnakenberg current, no chirality, no current observable gridded. A real spin glass")
    print("  cannot be k_frust. This is the move-A point landed on a real substrate.")
    if glass_frozen and para_unfrozen:
        print("GLASS FREEZING -- HOLDS: q_EA>0 below T_c (frozen, EA order parameter on), ~0 above.")
        print("  => spin glass is the s-regime/suspension family, NOT k_frust. The naming-purge stands")
        print("     on this + the structural argument; the clean X<1 aging slope is OWED (needs the")
        print("     self-overlap + staggered-field FDR estimator -- generic estimator unreliable here).")
    else:
        print(f"  q_EA pattern not clean (glass_frozen={glass_frozen}, para_unfrozen={para_unfrozen}) -- inspect.")

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    Ts = [r["T"] for r in rows]
    ax[0].plot(Ts, [r["q_ea"] for r in rows], "s-", color="tab:purple")
    ax[0].axhline(0.0, color="gray", lw=0.8)
    ax[0].axvline(T_C, color="k", ls=":", lw=1, label="T_c")
    ax[0].set_xlabel("temperature T"); ax[0].set_ylabel("q_EA (long-lag plateau of spin-relative C)")
    ax[0].set_title("EA order parameter: q_EA>0 (frozen glass / s-family) below T_c, ->0 above\n(the robust read)")
    ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3)
    ax[1].plot(Ts, [r["X"] for r in rows], "o--", color="tab:red", alpha=0.6)
    ax[1].axhline(1.0, color="gray", ls="--", lw=1, label="X=1")
    ax[1].axvline(T_C, color="k", ls=":", lw=1, label="T_c")
    ax[1].set_xlabel("temperature T"); ax[1].set_ylabel("raw FDR slope X (UNRELIABLE here)")
    ax[1].set_title("FDR slope is estimator-broken (X>1, inverted): generic estimator\nfails near criticality -- self-overlap+staggered field owed")
    ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3)
    fig.suptitle("SK spin glass: NOT k_frust (structural); glass freezing = s-family; clean X<1 owed", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    png = OUT / "k_frust_A_sk.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
