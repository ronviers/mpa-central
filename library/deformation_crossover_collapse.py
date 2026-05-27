r"""Finite-D merge-crossover sandbox + scaling-collapse test (deformation calculus, Test B').

WHAT THIS IS
------------
An apparatus to run the scaling-collapse falsifier that replaced the original Test B
("recover a 1/D coefficient series") after the 2026-05-26 characterification rounds.
See H:/mpa-atlas/docs/deformation_calculus_sharpening_notes.md (esp. §8.4) and the
receipts §Deformation calculus note.

It simulates the merge operator C's Boolean-deviation defect
    Delta_C(A,B) = sigma(C(A,B)) XOR (sigma(A) AND sigma(B))
for two committed propositions under conflicting shear gamma_AB > 0, at finite drive D.
Boolean (D->inf) says the merge survives (1 AND 1 = 1); at finite D it collapses to r when
the budget can't cover the shear. Theorem 9: defect=1 iff gamma>0 and D<gamma. The crossover
sits at gamma ~ D. E[Delta_C](gamma,D) = P(merge collapses).

The merge survival is modeled by the framework's own two-mode kernel reduced to its
near-threshold normal form (pitchfork/transcritical; Lamb cubic saturation), with a STATED,
SWAPPABLE noise closure:
    d(rho)/dt = (D - gamma) rho - eta rho^3 + noise.
For gamma<D the nonzero fixed point is stable (survive, sigma=1); for gamma>D only rho=0 is
stable (collapse, sigma=0). Finite-D noise softens the survival probability across gamma=D.

WHAT THIS IS NOT
----------------
NOT a derivation of MPA's operators. Every closure (noise model, its D-scaling exponent q,
the saturation eta, the survival threshold) is an explicit, labeled knob. The scientific
content is the ROBUSTNESS of the result to those knobs:
  - if E[Delta_C] collapses onto one universal profile F(z), z=(gamma-g50)/w(D), with a width
    exponent alpha (w ~ D^alpha) that is STABLE across closures  -> the crossover scaling is
    forced (structural);
  - if alpha and the profile swing with the closure  -> fitted, not forced (the verdict the
    chat rounds reached).
So the sandbox MEASURES forced-vs-fitted instead of asserting it.

DISCIPLINE NOTE: rho is never clipped at 0 (clipping manufactures excluded zeros -- the
asymptotic-closure NaN tripwire). The additive closure uses a signed order parameter
(survive = |rho|>thresh); the multiplicative closure keeps rho>=0 natively (noise ~ rho).

Run: python H:/mpa-central/library/deformation_crossover_collapse.py
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path("H:/mpa-central/library/output/diagnostics")
OUT.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Closure:
    """A stated, swappable closure for the finite-D merge dynamics. Every field is a knob."""
    name: str
    noise: str          # 'additive' (signed rho) | 'multiplicative' (rho>=0, noise ~ rho)
    q: float            # noise scales as sigma0 * D**(-q)  (framework hint: intrinsic noise ~ 1/D)
    sigma0: float = 1.0
    eta: float = 1.0    # cubic saturation strength
    rho0: float = 0.1   # initial amplitude
    thresh: float = 0.3 # survival threshold on |rho(T)|
    dt: float = 0.02
    nsteps: int = 1500  # T = nsteps*dt
    n_traj: int = 400


def delta_c_curve(D: float, gammas: np.ndarray, c: Closure, rng) -> np.ndarray:
    """E[Delta_C](gamma) = P(merge collapses) at drive D, via Euler-Maruyama ensemble.

    Vectorized over (gamma, trajectory). Returns one probability per gamma.
    """
    ng = len(gammas)
    N = c.n_traj
    rho = np.full((ng, N), c.rho0, dtype=float)
    mu = (D - gammas)[:, None]                 # linear drift coeff, shape (ng,1)
    sigma = c.sigma0 * D ** (-c.q)             # closure: noise amplitude's D-scaling
    sqdt = np.sqrt(c.dt)
    for _ in range(c.nsteps):
        xi = rng.standard_normal((ng, N))
        if c.noise == "additive":
            incr = sigma * xi                  # signed order parameter; rho may be +/-
        elif c.noise == "multiplicative":
            incr = sigma * np.abs(rho) * xi    # vanishes at 0; keeps rho>=0 region absorbing
        else:
            raise ValueError(c.noise)
        rho = rho + (mu * rho - c.eta * rho ** 3) * c.dt + incr * sqdt
        # NO clipping at 0 (asymptotic-closure discipline).
    survive = np.abs(rho) > c.thresh
    p_survive = survive.mean(axis=1)
    return 1.0 - p_survive                     # defect = P(collapse)


def center_and_width(gammas: np.ndarray, E: np.ndarray):
    """g50 (E=0.5 crossing) and width = gamma(0.84)-gamma(0.16), via interpolation.

    E is monotone increasing in gamma (collapse prob rises with shear). Returns
    (g50, width, resolved) where resolved is False if the window didn't bracket 0.16..0.84.
    """
    order = np.argsort(E)
    Es, gs = E[order], gammas[order]
    resolved = (Es[0] <= 0.16) and (Es[-1] >= 0.84)
    g16 = np.interp(0.16, Es, gs)
    g50 = np.interp(0.50, Es, gs)
    g84 = np.interp(0.84, Es, gs)
    return g50, max(g84 - g16, 1e-9), resolved


def measure_crossover(D: float, c: Closure, rng, Wabs: float, npts: int):
    """Pilot scan at gamma=D +/- Wabs, then adaptively refine to gamma_50 +/- 5*width
    until the crossover is resolved (width >> grid spacing). Guards the alpha estimate
    against grid-floored widths."""
    gammas = D + np.linspace(-Wabs, Wabs, npts)
    E = delta_c_curve(D, gammas, c, rng)
    g50, w, ok = center_and_width(gammas, E)
    for _ in range(3):
        span = 5.0 * w
        gammas = g50 + np.linspace(-span, span, 121)
        E = delta_c_curve(D, gammas, c, rng)
        g50, w, ok = center_and_width(gammas, E)
        if w > 4.0 * (2.0 * span / 120):       # width >= ~4 grid cells: resolved
            break
    return gammas, E, g50, w, ok


def analyze(c: Closure, D_list, Wabs: float, npts: int, rng):
    curves, widths, centers = {}, {}, {}
    resolved_all = True
    for D in D_list:
        gammas, E, g50, w, ok = measure_crossover(D, c, rng, Wabs, npts)
        resolved_all &= ok
        curves[D] = (gammas, E)
        widths[D] = w
        centers[D] = g50

    # width exponent: w ~ D^alpha  (slope of log w vs log D)
    Ds = np.array(D_list, dtype=float)
    ws = np.array([widths[D] for D in D_list], dtype=float)
    alpha, logc = np.polyfit(np.log(Ds), np.log(ws), 1)

    # collapse quality: overlay E vs z=(gamma-g50)/w on a common z-grid, measure spread
    zgrid = np.linspace(-2.5, 2.5, 81)
    stacked = []
    for D in D_list:
        gammas, E = curves[D]
        z = (gammas - centers[D]) / widths[D]
        o = np.argsort(z)
        stacked.append(np.interp(zgrid, z[o], E[o]))
    stacked = np.array(stacked)
    core = np.abs(zgrid) <= 1.5
    collapse_resid = float(stacked[:, core].std(axis=0).mean())  # mean cross-D std in core
    mean_profile = stacked.mean(axis=0)

    # profile family: fit erf and logistic (1-param scale) to the collapsed mean
    def rmse(model):
        return float(np.sqrt(np.mean((mean_profile - model) ** 2)))
    from scipy.special import erf  # noqa
    # erf: 0.5(1+erf(z/(s*sqrt2))); logistic: 1/(1+exp(-z/s))
    ss = np.linspace(0.2, 1.5, 60)
    erf_rmse = min(rmse(0.5 * (1 + erf(zgrid / (s * np.sqrt(2))))) for s in ss)
    log_rmse = min(rmse(1.0 / (1.0 + np.exp(-zgrid / s))) for s in ss)

    return {
        "curves": curves, "widths": widths, "centers": centers,
        "alpha": alpha, "collapse_resid": collapse_resid,
        "mean_profile": mean_profile, "zgrid": zgrid,
        "erf_rmse": erf_rmse, "log_rmse": log_rmse, "resolved": resolved_all,
    }


def main():
    rng = np.random.default_rng(20260526)
    D_list = [8, 16, 32, 64]
    Wabs, npts = 10.0, 61

    closures = [
        Closure("additive q=0.5", "additive", q=0.5, sigma0=1.0),
        Closure("additive q=1.0", "additive", q=1.0, sigma0=1.0),
        Closure("multiplicative q=0.5", "multiplicative", q=0.5, sigma0=1.2),
    ]

    print("=" * 74)
    print("FINITE-D MERGE-CROSSOVER SCALING-COLLAPSE TEST  (deformation calculus, Test B')")
    print("=" * 74)
    print(f"D sweep: {D_list}   gamma window: D +/- {Wabs}   ({npts} pts)")
    print("Boolean (D->inf): merge survives (1^1=1). Defect E[Delta_C] = P(collapse).")
    print("Thm 9 sharp threshold: defect=1 iff gamma>D.  Crossover measured at gamma~D.\n")

    results = {}
    for c in closures:
        r = analyze(c, D_list, Wabs, npts, rng)
        results[c.name] = r
        wtxt = "  ".join(f"D={D}:w={r['widths'][D]:.2f}" for D in D_list)
        print(f"[{c.name}]")
        print(f"   widths:           {wtxt}")
        print(f"   width exponent:   alpha = {r['alpha']:+.3f}   (w ~ D^alpha)")
        print(f"   collapse residual: {r['collapse_resid']:.4f}   (cross-D std in |z|<1.5; "
              f"<~0.03 = clean collapse)")
        print(f"   profile RMSE:     erf={r['erf_rmse']:.4f}  logistic={r['log_rmse']:.4f}  "
              f"-> {'erf' if r['erf_rmse']<r['log_rmse'] else 'logistic'}")
        if not r["resolved"]:
            print("   WARNING: window did not bracket 0.16..0.84 at some D (widen Wabs).")
        print()

    alphas = np.array([results[c.name]["alpha"] for c in closures])
    resids = np.array([results[c.name]["collapse_resid"] for c in closures])
    print("=" * 74)
    print("VERDICT")
    print("=" * 74)
    clean = bool(np.all(resids < 0.03))
    print(f"- Clean within-closure collapse (each closure overlays onto one F(z))?  "
          f"{'YES' if clean else 'PARTIAL/NO'}  (resids {np.round(resids,4)})")
    print(f"- Width exponent alpha across closures: {np.round(alphas,3)}  "
          f"spread={alphas.max()-alphas.min():.3f}")
    forced = (alphas.max() - alphas.min()) < 0.15
    print(f"  -> alpha {'STABLE across closures (scaling exponent forced)' if forced else 'SWINGS with closure (FITTED, not forced)'}.")
    print("- Reading: the INNER SCALING STRUCTURE (collapse exists) is the near-tautological")
    print("  forced part; the contentful invariant (alpha + profile class) is what these knobs")
    print("  probe. This run is the apparatus, not evidence: closures are stated, not derived,")
    print("  and nothing here has met a real substrate. (no-post-conform-evidence discipline)")

    # ---- figure: raw crossovers (top) + collapsed overlays (bottom) ----
    fig, ax = plt.subplots(2, len(closures), figsize=(5 * len(closures), 8))
    colors = plt.cm.viridis(np.linspace(0, 0.85, len(D_list)))
    for j, c in enumerate(closures):
        r = results[c.name]
        for k, D in enumerate(D_list):
            gammas, E = r["curves"][D]
            ax[0, j].plot(gammas - D, E, color=colors[k], lw=1.6, label=f"D={D}")
            z = (gammas - r["centers"][D]) / r["widths"][D]
            ax[1, j].plot(z, E, color=colors[k], lw=1.4, alpha=0.85)
        ax[0, j].axvline(0, color="gray", lw=0.6, ls=":")
        ax[0, j].set_title(f"{c.name}\nraw: E[$\\Delta_C$] vs $\\gamma-D$")
        ax[0, j].set_xlabel(r"$\gamma_{AB}-D$"); ax[0, j].set_ylabel(r"E[$\Delta_C$]")
        ax[0, j].legend(fontsize=8)
        # overlay best erf on collapsed
        zg = r["zgrid"]
        ax[1, j].plot(zg, r["mean_profile"], "k--", lw=1.0, label="mean")
        ax[1, j].set_title(f"collapsed: $z=(\\gamma-g_{{50}})/w(D)$\n"
                           f"$\\alpha$={r['alpha']:+.2f}  resid={r['collapse_resid']:.3f}")
        ax[1, j].set_xlabel("z"); ax[1, j].set_ylabel(r"E[$\Delta_C$]")
        ax[1, j].set_xlim(-2.5, 2.5); ax[1, j].legend(fontsize=8)
    fig.suptitle("Merge-crossover scaling collapse (Test B'): does $\\Delta_C$ collapse, and is "
                 "$\\alpha$ closure-robust?", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    png = OUT / "deformation_crossover_collapse.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
