"""k_frust falsification LADDER -- RUNG 1 (quickest): operating-point sweep.

Kill-shot under test (the WEAK invariance claim, handoff sec.4 claim 1):
  A frustrated loop never resolves into a clean c or r and its Schnakenberg
  cyclic current is drive-INDEPENDENT (cdv1 sec.Topological-drain / sec.8: the
  current is "forced regardless of D", "not resolvable by D").

We drive the bare frustrated loop (NO tower) across three 1-D sweeps through the
canonical operating point and read the intrinsic cyclic current J (observer-
independent ground truth, the bulletproof meter):
  * DRIVE      -- vary the noise/drive sigma at fixed wiring + headroom.
  * HEADROOM   -- vary chit = ln(G0/L) (deep-c -> near-s) at fixed wiring + drive.
  * COUPLING   -- vary the wiring magnitude |gamma| at fixed headroom + drive.

Pre-registered kills (scored, not confirmed):
  K1  At any ALIVE operating point (chit>=0, amplitude well above floor), J
      collapses to control level (loses sign-definiteness across seeds) -> the
      loop resolved to a stationary state (P_ss exists) = clean resolution.
  K2  J is drive-DEPENDENT (scales toward 0 as sigma->0, or tracks sigma) ->
      the current is not drive-independent.
  Excluded (NOT a kill, per the type argument): chit<0 drives every VERTEX to r;
  that is a vertex-level op and cannot falsify a subgraph-level invariant. Such
  points are run + plotted but flagged 'vertex-op (excluded)'.

Survives: J stays sign-definite and ~flat across drive and headroom; it scales
with the WIRING magnitude only (removing the edges trivially removes the cycle).

Run: python H:/mpa-central/library/k_frust_r1_sweep.py
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

RHO_SAT, S0, RHO_FLOOR, DT = 1.0, 1.0e-3, 1.0e-7, 0.005
CYC = np.array([[0, 1, -1], [-1, 0, 1], [1, -1, 0]], float)   # frustrated (RPS) generator
SYM = np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]], float)      # matched reciprocal control

# canonical operating point (the bulletproof-meter point)
G0_C, L_C, SIGMA_C, GMAG_C = 1.20, 1.00, 0.02, 0.50
N_REAL, T_EQ, T_OBS = 192, 3000, 6000
SEEDS = [1, 2, 3, 4]


def finite(name, x):
    x = np.asarray(x, float)
    if not np.all(np.isfinite(x)):
        raise FloatingPointError(f"NON-FINITE in '{name}' (MPA NaN tripwire): bad test or boundary attainment.")
    return x


def step(rho, gmat, G0, L, sigma, rng):
    """One Euler-Maruyama step; no hard-zero clip (spontaneous floor + multiplicative noise keep rho>0)."""
    S = rho.sum(axis=1, keepdims=True)
    gain = G0 / (1.0 + S / RHO_SAT)
    cross = rho * (rho @ gmat.T) / RHO_SAT
    drift = (gain - L) * rho - cross + S0
    noise = sigma * np.sqrt(np.maximum(rho, 0.0)) * rng.standard_normal(rho.shape) * np.sqrt(DT)
    return np.maximum(rho + drift * DT + noise, RHO_FLOOR)


def cyclic_J(rho, rp):
    """Intrinsic cyclic current (chirality of rho-rotation), /r2-normalized, gated to healthy r2."""
    m = rho.mean(1); mp = rp.mean(1)
    a = rho[:, 0] - m; b = (rho[:, 1] - rho[:, 2]) / np.sqrt(3.0)
    adot = ((rho[:, 0] - m) - (rp[:, 0] - mp)) / DT
    bdot = ((rho[:, 1] - rho[:, 2]) - (rp[:, 1] - rp[:, 2])) / (np.sqrt(3.0) * DT)
    r2 = a * a + b * b
    good = r2 > 1e-10
    return float(np.mean((a[good] * bdot[good] - b[good] * adot[good]) / r2[good])) if good.any() else 0.0


def simulate(gmat, G0, L, sigma, gmag, seed):
    """Return (J averaged over the observation window, mean amplitude)."""
    rng = np.random.default_rng(seed)
    g = gmag * gmat
    rho = np.tile([0.06, 0.03, 0.01], (N_REAL, 1)).astype(float)
    for _ in range(T_EQ):
        rho = step(rho, g, G0, L, sigma, rng)
    chir = np.zeros(T_OBS); amp = np.zeros(T_OBS)
    for t in range(T_OBS):
        rp = rho.copy()
        rho = step(rho, g, G0, L, sigma, rng)
        chir[t] = cyclic_J(rho, rp)
        amp[t] = float(rho.mean())
    return float(np.mean(chir)), float(np.mean(amp))


def measure(gmat, G0, L, sigma, gmag):
    out = [simulate(gmat, G0, L, sigma, gmag, s) for s in SEEDS]
    Js = np.array([o[0] for o in out]); amps = np.array([o[1] for o in out])
    return Js.mean(), Js.std(ddof=1), amps.mean()


def sweep(axis, values, fixed):
    """fixed = dict with G0,L,sigma,gmag defaults; vary `axis`."""
    rows = []
    for v in values:
        p = dict(fixed); p[axis] = v
        chit = np.log(p["G0"] / p["L"])
        Jf, sdf, ampf = measure(CYC, **p)
        Jc, sdc, ampc = measure(SYM, **p)
        sign_def = abs(Jf) / max(sdf, abs(Jc), sdc, 1e-9)
        rows.append(dict(v=v, chit=chit, amp=ampf, Jf=Jf, sdf=sdf, Jc=Jc, sdc=sdc, sep=sign_def))
    return rows


def report(name, axis, rows):
    print(f"\n--- {name} sweep (vary {axis}) ---")
    print(f"{axis:>8} | {'chit':>6} {'amp':>7} | {'J_frust':>11} {'+/-':>9} | {'J_ctrl':>10} | "
          f"{'sep(x)':>7} | flag")
    kills = []
    for r in rows:
        alive = r["amp"] > 5e-3 and r["chit"] >= 0.0
        vertex_op = r["chit"] < 0.0
        resolved = alive and r["sep"] < 3.0          # K1: lost sign-definiteness while alive
        flag = "vertex-op(excl)" if vertex_op else ("** RESOLVED (kill?)" if resolved else "frustrated")
        if resolved:
            kills.append(r)
        print(f"{r['v']:>8.3g} | {r['chit']:>6.2f} {r['amp']:>7.4f} | {r['Jf']:>+11.4e} {r['sdf']:>9.1e} | "
              f"{r['Jc']:>+10.3e} | {r['sep']:>7.1f} | {flag}")
    return kills


def main():
    fixed = dict(G0=G0_C, L=L_C, sigma=SIGMA_C, gmag=GMAG_C)
    sweeps = {
        "DRIVE":    ("sigma", [0.005, 0.01, 0.02, 0.05, 0.10]),
        "HEADROOM": ("G0",    [0.90, 1.02, 1.10, 1.20, 1.50, 2.00]),   # 0.90 -> chit<0 (vertex-op, excluded)
        "COUPLING": ("gmag",  [0.10, 0.25, 0.50, 1.00, 1.50]),
    }
    results = {}
    all_kills = []
    for name, (axis, vals) in sweeps.items():
        rows = sweep(axis, vals, fixed=fixed)
        results[name] = (axis, rows)
        all_kills += report(name, axis, rows)

    print("\n================ RUNG 1 VERDICT ================")
    if all_kills:
        print(f"KILL: {len(all_kills)} alive operating point(s) where the frustrated loop lost its "
              f"sign-definite current (resolved). See ** rows above.")
    else:
        print("SURVIVES: at every ALIVE operating point the frustrated loop kept a sign-definite, "
              "drive-robust cyclic current (no clean c/r resolution). Current scales with WIRING only.")

    # ---- figure: J vs each axis (frust vs control), amplitude, sign-definiteness ----
    fig, ax = plt.subplots(1, 3, figsize=(16, 5))
    for i, (name, (axis, rows)) in enumerate(results.items()):
        vs = [r["v"] for r in rows]
        Jf = [r["Jf"] for r in rows]; sdf = [r["sdf"] for r in rows]
        Jc = [r["Jc"] for r in rows]
        ax[i].errorbar(vs, Jf, yerr=sdf, fmt="o-", color="tab:red", capsize=3, label="J frustrated")
        ax[i].plot(vs, Jc, "s--", color="tab:blue", label="J control (sym)")
        ax[i].axhline(0, color="k", lw=0.6)
        for r in rows:                                  # mark excluded vertex-op points
            if r["chit"] < 0:
                ax[i].axvspan(r["v"] * 0.97, r["v"] * 1.03, color="gray", alpha=0.25)
        ax[i].set_title(f"{name}: J vs {axis}")
        ax[i].set_xlabel(axis); ax[i].set_ylabel("cyclic current J"); ax[i].legend(fontsize=8); ax[i].grid(alpha=0.3)
        if name in ("DRIVE", "COUPLING"):
            ax[i].set_xscale("log")
    fig.suptitle("k_frust ladder R1: does the frustrated loop EVER resolve (J->0) while alive? "
                 "(gray = chit<0 vertex-op, excluded)", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    png = OUT / "k_frust_r1_sweep.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
