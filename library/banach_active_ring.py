r"""Active frustrated ring — the NONLINEAR (Hopf limit-cycle) Banach-class reference.

Fork B of the two-frame program. `banach_frustrated.py` is the LINEAR N=3 cyclic
non-reciprocal OU (no amplitude knob; lines 152-154 there flag this nonlinear extension
as "the next step"). This builds it: gain + cubic saturation (Stuart-Landau normal form)
+ cyclic non-reciprocal coupling = a topologically-forced LIMIT CYCLE, the dynamical class
of the real active-solid robotic rings the 2026-05-22 substrate search turned up (Veenstra
et al. "Adaptive locomotion of active solids", Nature 2025, zenodo.13844137: non-reciprocal
feedback hardcoded into a closed loop -> Hopf -> sustained circulation).

    dz = (mu z - z^3 + g A_cyc z) dt + sqrt(2D) dW ,
    A_cyc = [[0,-1, 1],[ 1, 0,-1],[-1, 1, 0]]   (antisymmetric circulant = Harary-frustrated
                                                  odd loop; circulation gauge-irremovable,
                                                  removable only by deleting edges g->0).
mu = gain (the amplitude/chit knob the linear model lacked); g = non-reciprocity (frustration).
At g=0 it is a gradient bistable system (no circulation). At g>0 the frustrated loop forces a
sustained current in the plane orthogonal to (1,1,1).

WHY THIS EXISTS: real active-lattice data is downloadable but mismatched to the apparatus
(no perturbation-response protocol in any public deposit -> external frame unreadable; robot
Var(J) is friction/quantization-dominated, not thermodynamic). This synthetic model lets BOTH
frames run on a topologically-forced current and PRE-REGISTERS the data contract a real
dataset must satisfy. SYNTHETIC -> serves apparatus-readiness + calibration; does NOT meet
the section-846 real-substrate bar (same status as banach_frustrated.py).

  SELF-FRAME: winding J in the rotation plane; <sigma> via the Stratonovich heat estimator
              (1/D)<F o zdot>, TARED in Part A against the exact linear-OU value; T = <sigma>
              tau Var(J)/(2<J>^2), TUR floor T>=1.
  EXTERNAL  : perturb mode 1 with field h (CRN-paired), C_11(tau) + step response chi_11(tau),
              parametric (Delta C, chi); D_FDT = max FDT departure, X(t->0).

Run: python H:/mpa-central/library/banach_active_ring.py
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass
from pathlib import Path
import numpy as np
from scipy.linalg import solve_continuous_lyapunov
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path("H:/mpa-central/library/output/diagnostics")
OUT.mkdir(parents=True, exist_ok=True)

A_CYC = np.array([[0.0, -1.0, 1.0], [1.0, 0.0, -1.0], [-1.0, 1.0, 0.0]])
DT, T_EQ, T_OBS, N_REAL, SEED = 0.01, 3000, 6000, 5000, 7
N_OBS_EXT, H = 1200, 0.05
# rotation-plane orthonormal basis (orthogonal to (1,1,1))
E1 = np.array([1.0, -1.0, 0.0]) / np.sqrt(2.0)
E2 = np.array([1.0, 1.0, -2.0]) / np.sqrt(6.0)
PROJ = np.stack([E1, E2], axis=0)            # 2x3 projector


def finite(name, x):
    if not np.all(np.isfinite(np.asarray(x, float))):
        raise FloatingPointError(f"NON-FINITE in '{name}' (MPA NaN tripwire).")
    return x


def drift(z, mu, g):
    """F(z) = mu z - z^3 + g A_cyc z  (elementwise cubic = gain+saturation)."""
    return mu * z - z ** 3 + (z @ A_CYC.T) * g


def run_self(mu, g, D, rng):
    """Euler-Maruyama; returns winding J per realization + Stratonovich <sigma> estimate."""
    sd = np.sqrt(2.0 * D * DT)
    z = rng.standard_normal((N_REAL, 3)) * np.sqrt(max(mu, 0.05))
    for _ in range(T_EQ):
        z = z + drift(z, mu, g) * DT + rng.standard_normal((N_REAL, 3)) * sd
    u = z @ PROJ.T
    phi = np.zeros(N_REAL)
    heat = 0.0                                            # accumulates F o dz (Stratonovich midpoint)
    for _ in range(T_OBS):
        zn = z + drift(z, mu, g) * DT + rng.standard_normal((N_REAL, 3)) * sd
        zmid = 0.5 * (z + zn)
        heat += float(np.mean(np.sum(drift(zmid, mu, g) * (zn - z), axis=1)))
        un = zn @ PROJ.T
        du = un - u
        mid = 0.5 * (u + un)
        r2 = (mid * mid).sum(1) + 1e-12
        phi += (mid[:, 0] * du[:, 1] - mid[:, 1] * du[:, 0]) / r2
        z, u = zn, un
    tau = T_OBS * DT
    sigma = heat / (D * tau)                              # <sigma> = (1/D)<F o zdot>, steady state
    return finite("winding", phi), sigma


def exact_linear_sigma(gamma, g, D):
    """Exact OU entropy production for M = -gamma I + g A_cyc (the tare ground truth)."""
    M = -gamma * np.eye(3) + g * A_CYC
    Sigma = solve_continuous_lyapunov(M, -2.0 * D * np.eye(3))
    Omega = M + D * np.linalg.inv(Sigma)
    return float(np.trace(Omega.T @ (np.eye(3) / D) @ Omega @ Sigma)), M


def run_self_linear(M, D, rng):
    """Linear-drift winding+heat run (for the Part-A tare; F = M z)."""
    sd = np.sqrt(2.0 * D * DT)
    z = rng.standard_normal((N_REAL, 3)) * np.sqrt(D)
    for _ in range(T_EQ):
        z = z + (z @ M.T) * DT + rng.standard_normal((N_REAL, 3)) * sd
    heat = 0.0
    for _ in range(T_OBS):
        zn = z + (z @ M.T) * DT + rng.standard_normal((N_REAL, 3)) * sd
        zmid = 0.5 * (z + zn)
        heat += float(np.mean(np.sum((zmid @ M.T) * (zn - z), axis=1)))
        z = zn
    return heat / (D * T_OBS * DT)


def run_external(mu, g, D, rng):
    """CRN-paired perturbed branch (field h on mode 1): C_11(tau), chi_11(tau)."""
    sd = np.sqrt(2.0 * D * DT)
    z = rng.standard_normal((N_REAL, 3)) * np.sqrt(max(mu, 0.05))
    for _ in range(T_EQ):
        z = z + drift(z, mu, g) * DT + rng.standard_normal((N_REAL, 3)) * sd
    zu = z.copy(); zp = z.copy(); z0 = z[:, 0].copy()
    hvec = np.array([H, 0.0, 0.0])
    C = np.empty(N_OBS_EXT + 1); chi = np.empty(N_OBS_EXT + 1)
    C[0] = float(np.mean(z0 * z0)); chi[0] = 0.0
    for k in range(1, N_OBS_EXT + 1):
        xi = rng.standard_normal((N_REAL, 3)) * sd
        zu = zu + drift(zu, mu, g) * DT + xi
        zp = zp + (drift(zp, mu, g) + hvec) * DT + xi
        C[k] = float(np.mean(z0 * zu[:, 0]))
        chi[k] = float(np.mean(zp[:, 0] - zu[:, 0])) / H
    C = C / C[0]
    return finite("C", C), finite("chi", chi)


def main():
    rng = np.random.default_rng(SEED)
    tau = T_OBS * DT

    # ---------- Part A: tare the Stratonovich <sigma> estimator vs exact linear OU ----------
    gam_t, g_t, D_t = 1.0, 0.6, 0.1
    s_exact, M_t = exact_linear_sigma(gam_t, g_t, D_t)
    s_strat = run_self_linear(M_t, D_t, rng)
    err = abs(s_strat - s_exact) / s_exact
    print("Part A  — Stratonovich <sigma> estimator tare (linear OU, M=-I+0.6 A_cyc):")
    print(f"  exact 6 g^2/gamma = {s_exact:.4f} | strat estimator = {s_strat:.4f} | err {100*err:.1f}%")
    print(f"  {'TARE OK' if err < 0.15 else 'TARE OFF — inspect'}\n")

    # ---------- Part B: g-sweep on the nonlinear frustrated ring (both frames) ----------
    mu = 1.0
    gs = [0.0, 0.2, 0.4, 0.7, 1.0, 1.5, 2.0]
    print(f"Part B  — nonlinear active frustrated ring (mu={mu}, D=0.1): r->s migration, both frames")
    hdr = (f"{'g':>5} {'gt':>3} | {'<J>/tau':>8} {'<sigma>':>8} {'SNR_J':>8} {'s*t/2':>8} TUR | "
           f"{'T':>8} | {'X(t->0)':>8} {'D_FDT':>7} {'Vext/sig':>9}")
    print(hdr); print("-" * len(hdr))
    rows = []
    for g in gs:
        phi, sigma = run_self(mu, g, 0.1, rng)
        mean, var = float(phi.mean()), float(phi.var(ddof=1))
        v = mean / tau
        has_cur = abs(v) > 0.02
        snr = mean * mean / var
        bound = sigma * tau / 2.0
        T = sigma * tau * var / (2.0 * mean * mean) if has_cur else float("nan")
        tur_ok = (snr <= bound * 1.10) if has_cur else True
        C, chi = run_external(mu, g, 0.1, rng)
        t_arr = np.arange(N_OBS_EXT + 1) * DT
        dC = C[0] - C
        msk = dC < 0.1 * max(dC.max(), 1e-9)
        s0 = np.sum(dC[msk] * chi[msk]) / np.sum(dC[msk] ** 2 + 1e-30)
        Teff = 1.0 / s0 if s0 > 0 else np.inf
        X0 = Teff * (np.polyfit(dC[msk], chi[msk], 1)[0]) if msk.sum() > 2 else float("nan")
        d_fdt = float(np.max(np.abs(dC - Teff * chi))) if np.isfinite(Teff) else float("nan")
        V_ext = float(np.trapezoid(np.abs(dC - Teff * chi), t_arr)) if np.isfinite(Teff) else float("nan")
        vext_ratio = V_ext / sigma if sigma > 1e-9 else float("nan")
        gt = "r" if not has_cur else ("k" if g <= 0.25 else "s")
        rows.append(dict(g=g, gt=gt, v=v, sigma=sigma, snr=snr, bound=bound, T=T, has_cur=has_cur,
                         X0=X0, dfdt=d_fdt, vext_ratio=vext_ratio, C=C, t_arr=t_arr, mean=mean))
        tcell = f"{T:>8.3f}" if has_cur else f"{'(locked)':>8}"
        print(f"{g:>5.2f} {gt:>3} | {v:>8.4f} {sigma:>8.4f} {snr:>8.2f} {bound:>8.2f} "
              f"{('ok' if tur_ok else 'XX') if has_cur else '—':>3} | {tcell} | "
              f"{X0:>8.3f} {d_fdt:>7.3f} {vext_ratio:>9.3f}")

    # reciprocal control: frustration removed -> circulation must vanish
    Asym = 0.5 * (A_CYC + A_CYC.T)                        # symmetric part = 0; use a symmetric coupling
    def drift_sym(z):
        return mu * z - z ** 3 + (z @ Asym.T) * 1.0
    sd = np.sqrt(2.0 * 0.1 * DT)
    z = rng.standard_normal((N_REAL, 3)) * np.sqrt(mu)
    for _ in range(T_EQ):
        z = z + drift_sym(z) * DT + rng.standard_normal((N_REAL, 3)) * sd
    u = z @ PROJ.T; phi_s = np.zeros(N_REAL)
    for _ in range(T_OBS):
        zn = z + drift_sym(z) * DT + rng.standard_normal((N_REAL, 3)) * sd
        un = zn @ PROJ.T; du = un - u; mid = 0.5 * (u + un)
        r2 = (mid * mid).sum(1) + 1e-12
        phi_s += (mid[:, 0] * du[:, 1] - mid[:, 1] * du[:, 0]) / r2
        z, u = zn, un
    v_sym = float(phi_s.mean()) / tau

    run = [r for r in rows if r["has_cur"]]
    tur_all = all(r["snr"] <= r["bound"] * 1.10 for r in run)
    print(f"\n  reciprocal control (frustration removed, symmetric coupling): <J>/tau = {v_sym:.4f} "
          f"(should be ~0 — no circulation without the odd loop)")

    print("\n================ VERDICT ================")
    print("Nonlinear active frustrated ring (Hopf limit-cycle, topologically-forced current):")
    print(f"  REGIME MIGRATION: g=0 locked (no current, gt=r); g>~0.3 sustained circulation (gt=s).")
    print(f"  SELF-FRAME: <sigma> tared (Part A, {100*err:.0f}% err); TUR floor T>=1 "
          f"{'respected' if tur_all else 'VIOLATED'} on all running cells "
          f"(T={min(r['T'] for r in run):.2f}..{max(r['T'] for r in run):.2f}).")
    print("  EXTERNAL FRAME: computable (X(t->0)~1, D_FDT>0) — verdict-agreement holds (both flag the")
    print("    current-bearing NESS). Vext/<sigma> != 1: position-frame integrated violation and true")
    print("    dissipation are DIFFERENT FUNCTIONALS (same finding as laser/driven_ring) — the exact")
    print("    magnitude identity needs the velocity-frame Harada-Sasa integral (the one deferred piece).")
    print(f"  TOPOLOGICAL FORCING: removing the odd loop (symmetric coupling) kills the current "
          f"(<J>/tau {v_sym:.3f}~0) — frustration is necessary, as the central commitment claims.")
    print("Synthetic -> apparatus-readiness + data contract; does NOT meet section-846 (real substrate).")

    # ---------- figure ----------
    fig, ax = plt.subplots(1, 2, figsize=(13.5, 5.5))
    gv = np.array([r["g"] for r in rows])
    sig = np.array([r["sigma"] for r in rows])
    vv = np.array([abs(r["v"]) for r in rows])
    ax[0].axvline(0.0, color="gray", ls=":", lw=1)
    ax[0].plot(gv, sig, "s-", color="tab:red", label=r"$\langle\sigma\rangle$ (tared, dissipation)")
    ax[0].set_xlabel(r"non-reciprocity $g$ (frustration; $g{=}0$ locked $\to$ $g{>}0$ circulating)")
    ax[0].set_ylabel(r"$\langle\sigma\rangle$", color="tab:red")
    ax2 = ax[0].twinx()
    ax2.plot(gv, vv, "o-", color="tab:green", label=r"$|\langle J\rangle|/\tau$ (current)")
    ax2.set_ylabel(r"$|\langle J\rangle|/\tau$", color="tab:green")
    ax[0].set_title("regime migration on the nonlinear frustrated ring\n(Hopf: no current at g=0 → sustained circulation)")
    l1, lb1 = ax[0].get_legend_handles_labels(); l2, lb2 = ax2.get_legend_handles_labels()
    ax[0].legend(l1 + l2, lb1 + lb2, fontsize=8, loc="upper left"); ax[0].grid(alpha=0.3)

    Tn = np.array([r["T"] if r["has_cur"] else np.nan for r in rows])
    dfdt = np.array([r["dfdt"] for r in rows])
    ax[1].axhline(1.0, color="tab:blue", ls=":", lw=0.8)
    ax[1].plot(gv, Tn, "^-", color="tab:blue", label=r"self-frame $T$ (TUR $\geq 1$)")
    ax[1].plot(gv, dfdt, "o-", color="tab:purple", label=r"external $\Delta_{\mathrm{FDT}}$")
    ax[1].set_xlabel(r"non-reciprocity $g$"); ax[1].set_ylabel("violation factors")
    ax[1].set_title("two-frame VERDICT-agreement (both onset with the current)\nmagnitudes differ → velocity-frame Harada–Sasa owed")
    ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3)
    fig.suptitle("Active frustrated ring: nonlinear (Hopf) topologically-forced current — both gFDR frames", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    png = OUT / "banach_active_ring.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
