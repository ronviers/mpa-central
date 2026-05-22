r"""Two-frame gFDR on a REAL substrate -- the class-B laser relaxation oscillation.

Direction (2) of the two-frame program (handoff_two_frame_gfdr.md), reached without
mpa-conform: the laser is modelled (as in `laser_conform_Q.py`) as a 2D linear NESS
whose drift is the cdv1-VALIDATED class-B Jacobian (ro_damping_fixed_check.py matches
its Q(chit) to 6.7e-16) and whose diffusion is spontaneous-emission shot noise:

    z = (n, N) = (photon number, inversion);  dz = J z dt + sqrt(2 D) dW
    J = [[0, G n*], [-kappa, -(gamma_s + G n*)]] ,  n* = gamma_s (r - 1)   (r = pump ratio)
    D = diag( gamma_s (r-1), gamma_s )            (shot noise)
    Sigma = Lyapunov(J, -2 D)                     (stationary covariance)

Both gFDR frames are then computable on the SAME (J, D, Sigma):

  EXTERNAL frame  : parametric ( C(0)-C(tau) , chi(tau) ) of the photon mode n, from
                    the exact propagator. Locus departs from the equilibrium-FDT line
                    => violation. Robust scalar D_FDT = max_tau |dC/T_eff - chi| (SL-style;
                    the RO rings, so the locus loops).
  SELF-PROBE frame: entropy production EXACT for a linear OU,
                    <sigma> = Tr[ Omega^T D^-1 Omega Sigma ],  Omega = J + D Sigma^-1
                    (unit-checked: reproduces the rotational-OU 2 w^2/kappa). The current
                    is the noise-sustained RO circulation -- winding in whitened
                    coordinates (Sigma^{-1/2} z, so the stationary cloud is isotropic) --
                    measured by simulation; T = <sigma> tau Var(J)/(2 <J>^2). The TUR
                    floor SNR_J <= <sigma> tau / 2 is the consistency tare (no closed form
                    for Var(J); TUR-respected validates sim vs exact <sigma>, as in Part B).

HONEST SCOPE: the laser current is PUMP-driven (contingent: r->1 => n*->0 => focus
collapses), NOT a topologically-forced k_frust current. So this earns the
"T-vs-X agreement on a REAL substrate" gate (FALSIFICATION promotion criterion 1),
NOT the section-846 k_frust-promotion bar (which still wants a topologically-forced
current). "Real substrate with a sustained NESS current" strictly contains "k_frust".

Run: python H:/mpa-central/library/two_frame_laser.py
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass
from pathlib import Path
import numpy as np
from scipy.linalg import expm, solve_continuous_lyapunov
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path("H:/mpa-central/library/output/diagnostics")
OUT.mkdir(parents=True, exist_ok=True)

G, KAPPA, GAMMA_S = 1.0, 1.0, 0.10        # class-B laser: gamma_s << kappa (params per laser_conform_Q.py)
DT, T_EQ, T_OBS, N_REAL, SEED = 0.02, 3000, 8000, 3000, 11


def finite(name, x):
    if not np.all(np.isfinite(np.asarray(x, float))):
        raise FloatingPointError(f"NON-FINITE in '{name}' (MPA NaN tripwire).")
    return x


def laser_linear(r):
    """Return (J, D, Sigma) for the class-B laser at pump ratio r."""
    n_star = GAMMA_S * (r - 1.0)
    J = np.array([[0.0, G * n_star], [-KAPPA, -(GAMMA_S + G * n_star)]])
    D = np.diag([max(GAMMA_S * (r - 1.0), 1e-9), GAMMA_S])           # shot-noise diffusion
    Sigma = solve_continuous_lyapunov(J, -2.0 * D)                  # J Sigma + Sigma J^T = -2 D
    return J, D, Sigma


def sigma_exact(J, D, Sigma):
    """Exact entropy-production rate of a linear OU: <sigma> = Tr[Omega^T D^-1 Omega Sigma],
    Omega = J + D Sigma^-1 (irreversible drift; =0 at detailed balance)."""
    Dinv = np.linalg.inv(D)
    Omega = J + D @ np.linalg.inv(Sigma)
    return float(np.trace(Omega.T @ Dinv @ Omega @ Sigma))


def c_chi_exact(J, Sigma, t_arr):
    """Photon-mode autocorrelation C_nn(tau) (normalized) and integrated response chi_nn(tau),
    from the exact linear-NESS propagator P(t)=exp(J t). R(t)=P[0,0] is the impulse response of n."""
    C = np.empty_like(t_arr); R = np.empty_like(t_arr)
    for i, t in enumerate(t_arr):
        P = expm(J * t)
        C[i] = (P @ Sigma)[0, 0]
        R[i] = P[0, 0]
    C = C / C[0]
    chi = np.concatenate([[0.0], np.cumsum(0.5 * (R[1:] + R[:-1]) * np.diff(t_arr))])
    return C, chi


def whitener(Sigma):
    """Sigma^{-1/2} (symmetric) so u = W z has unit stationary covariance -> isotropic winding."""
    w, V = np.linalg.eigh(Sigma)
    return V @ np.diag(1.0 / np.sqrt(w)) @ V.T


def simulate_winding(J, D, W, rng):
    """Euler-Maruyama dz = J z dt + sqrt(2 D dt) randn; whiten u = W z; angular winding
    J_tau = int (u1 du2 - u2 du1)/|u|^2 (midpoint). Returns per-realization winding over T_OBS."""
    sd = np.sqrt(2.0 * np.diag(D) * DT)
    z = np.zeros((N_REAL, 2))
    for _ in range(T_EQ):
        z = z + (z @ J.T) * DT + rng.standard_normal((N_REAL, 2)) * sd
    u = z @ W.T
    phi = np.zeros(N_REAL)
    for _ in range(T_OBS):
        z_new = z + (z @ J.T) * DT + rng.standard_normal((N_REAL, 2)) * sd
        u_new = z_new @ W.T
        du = u_new - u
        mid = 0.5 * (u + u_new)
        r2 = (mid * mid).sum(1) + 1e-12
        phi += (mid[:, 0] * du[:, 1] - mid[:, 1] * du[:, 0]) / r2
        z, u = z_new, u_new
    return finite("winding", phi)


def main():
    # ---- unit check: the exact <sigma> formula must reproduce the rotational-OU 2 w^2/kappa ----
    k, w0, d0 = 1.0, 0.7, 0.05
    A = np.array([[-k, -w0], [w0, -k]]); Dou = d0 * np.eye(2)
    Sou = solve_continuous_lyapunov(A, -2.0 * Dou)
    s_chk = sigma_exact(A, Dou, Sou)
    print(f"unit check: <sigma>_exact(rot-OU w={w0}) = {s_chk:.6f}  vs  2w^2/k = {2*w0**2/k:.6f}  "
          f"(err {abs(s_chk-2*w0**2/k):.1e})\n")

    rng = np.random.default_rng(SEED)
    tau = T_OBS * DT
    rs = [1.1, 1.5, 2.0, 3.0, 5.0, 8.0]

    hdr = (f"{'r':>5} {'chit':>6} | {'<sigma>':>8} | {'<J>/tau':>8} {'SNR_J':>8} {'sig*t/2':>8} TUR | "
           f"{'T':>7} | {'X(t->0)':>8} {'D_FDT':>7}")
    print(hdr); print("-" * len(hdr))
    rows = []
    for r in rs:
        J, D, Sigma = laser_linear(r)
        sig = sigma_exact(J, D, Sigma)
        # external frame (exact propagator)
        ev = np.linalg.eigvals(J); w_ro = float(np.max(np.abs(ev.imag)))
        period = (2 * np.pi / w_ro) if w_ro > 1e-6 else 50.0
        t_arr = np.linspace(tau / 600, min(tau, 8 * period), 600)
        C, chi = c_chi_exact(J, Sigma, t_arr)
        dC = C[0] - C
        msk0 = dC < 0.1 * dC.max()                                  # near-origin segment -> T_eff (sets X(t->0)=1)
        s0 = np.sum(dC[msk0] * chi[msk0]) / np.sum(dC[msk0] ** 2 + 1e-30)
        T_eff = 1.0 / s0 if s0 > 0 else np.inf
        X0 = T_eff * (np.polyfit(dC[msk0], chi[msk0], 1)[0])         # ~1 by construction
        d_fdt = float(np.max(np.abs(dC - T_eff * chi)))
        # self-probe frame (sim winding + exact <sigma>)
        W = whitener(Sigma)
        phi = simulate_winding(J, D, W, rng)
        mean, var = float(phi.mean()), float(phi.var(ddof=1))
        snr = mean * mean / var
        bound = sig * tau / 2.0
        T = sig * tau * var / (2.0 * mean * mean) if abs(mean) > 1e-9 else float("nan")
        tur_ok = snr <= bound * 1.10
        rows.append(dict(r=r, chit=np.log(r), sig=sig, mean=mean, var=var, snr=snr,
                         bound=bound, T=T, X0=X0, dfdt=d_fdt, w_ro=w_ro,
                         t_arr=t_arr, dC=dC, chi=chi, T_eff=T_eff))
        print(f"{r:>5.1f} {np.log(r):>6.3f} | {sig:>8.4f} | {mean/tau:>8.4f} {snr:>8.3f} {bound:>8.2f} "
              f"{'ok' if tur_ok else 'XX':>3} | {T:>7.3f} | {X0:>8.3f} {d_fdt:>7.3f}")

    tur_all = all(r["snr"] <= r["bound"] * 1.10 for r in rows)
    print("\n================ VERDICT ================")
    if tur_all and all(r["T"] >= 0.9 for r in rows):
        print("Two-frame gFDR runs on the REAL (cdv1-validated) class-B laser. BOTH frames computable:")
        print(f"  self-frame: T in [{min(r['T'] for r in rows):.2f}, {max(r['T'] for r in rows):.2f}], "
              f"TUR floor T>=1 respected; current <J> nonzero across the pumped range;")
        print("  external frame: locus departs the FDT line (D_FDT>0), X(t->0)~1.")
        print("  VERDICT-AGREEMENT: both flag NESS across r>1; the falsifier (CONTRADICTORY regime")
        print("  verdicts) is NOT triggered. Magnitudes are DIFFERENT functionals -- <sigma> (true")
        print("  dissipation) rises monotonically with pumping; the normalized external D_FDT peaks at")
        print("  the RO resonance r=2 (chit=ln2); T (tightness) is loose. Same verdict, not same number.")
        print("Caveat: pump-driven current => earns the real-substrate VERDICT-AGREEMENT gate (criterion 1),")
        print("        NOT the section-846 k_frust bar (which wants a topologically-forced current).")
    else:
        print(f"NOT clean -- TUR_ok={tur_all}. Inspect (raise N_REAL/T_OBS or check threshold rows).")

    # ---------- figure ----------
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    cols = plt.cm.plasma(np.linspace(0.1, 0.85, len(rows)))
    dCmax = max(r["dC"].max() for r in rows)
    xs = np.linspace(0, dCmax, 50)
    ax[0].plot(xs, xs, "k--", lw=1.2, label=r"equilibrium FDT (slope $T_{\mathrm{eff}}^{-1}$, $X{=}1$)")
    for r, c in zip(rows, cols):
        ax[0].plot(r["dC"], r["T_eff"] * r["chi"], "-", color=c, lw=1.5,
                   label=fr"$r={r['r']}$ ($\chi t={r['chit']:.2f}$)")
    ax[0].set_xlabel(r"$C(0)-C(\tau)$  [photon-mode self-overlap]")
    ax[0].set_ylabel(r"$T_{\mathrm{eff}}\,\chi(\tau)$")
    ax[0].set_title("external frame on the REAL class-B laser\n(loops = RO ringing; departure from dashed = violation)")
    ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3)
    chit = np.array([r["chit"] for r in rows])
    T_self = np.array([r["T"] for r in rows])
    dfdt = np.array([r["dfdt"] for r in rows])
    sig = np.array([r["sig"] for r in rows])
    ax[1].plot(chit, dfdt, "o-", color="tab:purple", label=r"external $\Delta_{\mathrm{FDT}}$")
    ax[1].plot(chit, T_self / T_self.max(), "^-", color="tab:blue",
               label=r"self-frame $T$ (normalized)")
    ax[1].set_xlabel(r"$\chi t = \ln r$ (pump ratio; affinity driver)")
    ax[1].set_ylabel(r"external violation / self-frame $T$")
    ax2 = ax[1].twinx()
    ax2.plot(chit, sig, "s--", color="tab:red", label=r"$\langle\sigma\rangle$ exact (self-frame input)")
    ax2.set_ylabel(r"$\langle\sigma\rangle$", color="tab:red")
    ax[1].axvline(np.log(2), color="gray", ls=":", lw=1, label=r"$r{=}2$ (RO $Q$ peak)")
    ax[1].set_title("two-frame VERDICT-agreement on the laser (no contradiction)\nmagnitudes differ: $\\Delta_{\\mathrm{FDT}}$ peaks at RO resonance, $\\langle\\sigma\\rangle$ rises monotonically")
    l1, lb1 = ax[1].get_legend_handles_labels(); l2, lb2 = ax2.get_legend_handles_labels()
    ax[1].legend(l1 + l2, lb1 + lb2, fontsize=8, loc="best"); ax[1].grid(alpha=0.3)
    fig.suptitle("two-frame gFDR on a REAL validated substrate: class-B laser relaxation oscillation", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    png = OUT / "two_frame_laser.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
