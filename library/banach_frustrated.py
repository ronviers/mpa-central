r"""Noisy frustrated Banach-class reference — instancing the dimensionless dream.

The deterministic Banach substrate (banach-substrate-reference.md) is D_noise=0 and two-mode:
no current, so the self-frame T is degenerate. The two-frame gFDR supplied the missing
ingredient — a dimensionless, intrinsic (probe-free) violation observable. This builds the
minimal NOISY (D>0) TOPOLOGICALLY-FORCED (N=3 obstructive cycle) Banach-class reference and
asks whether it carries a dimensionless canonical quantity.

Model — 3 modes, cyclic non-reciprocal coupling (rock-paper-scissors):
    dz = M z dt + sqrt(2D) dW ,   M = -gamma I + g A_cyc ,
    A_cyc = [[0,-1, 1],[ 1, 0,-1],[-1, 1, 0]]   (antisymmetric circulant).
Eigenvalues of M: -gamma (real), -gamma ± i*sqrt(3)*g (complex pair = the k_frust signature).
Topologically forced: detailed balance is unreachable by tuning any continuous drive — only
g=0 removes it, and that deletes the edges (rewiring). Contrast the driven_ring (drive-forced:
F->0 restores DB without rewiring).

Exact (linear OU):  Sigma = (D/gamma) I ;  Omega = M + D Sigma^-1 = g A_cyc ;
    <sigma> = Tr[Omega^T D^-1 Omega Sigma] = 6 g^2 / gamma   (independent of D).
Self-frame: winding J in the rotation plane (⊥ to (1,1,1)); affinity A = <sigma> / (cycle rate)
in nats; T = <sigma> tau Var(J)/(2 <J>^2), TUR floor T>=1.

Canonical claim under test: the AFFINITY A (nats) and spectral ratio omega/gamma are
DIMENSIONLESS and NOISE-INDEPENDENT (set by the structure g/gamma) — candidate canonical
quantities with identity translation field. T is the bounded violation factor.

Run: python H:/mpa-central/library/banach_frustrated.py
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
DT, T_EQ, T_OBS, N_REAL, SEED = 0.01, 3000, 6000, 5000, 5
# rotation plane orthonormal basis (⊥ to (1,1,1))
E1 = np.array([1.0, -1.0, 0.0]) / np.sqrt(2.0)
E2 = np.array([1.0, 1.0, -2.0]) / np.sqrt(6.0)
P = np.stack([E1, E2], axis=0)            # 2x3 projector onto the rotation plane


def finite(name, x):
    if not np.all(np.isfinite(np.asarray(x, float))):
        raise FloatingPointError(f"NON-FINITE in '{name}'.")
    return x


def exact(gamma, g, D):
    M = -gamma * np.eye(3) + g * A_CYC
    Sigma = solve_continuous_lyapunov(M, -2.0 * D * np.eye(3))
    Omega = M + D * np.linalg.inv(Sigma)
    sigma = float(np.trace(Omega.T @ (np.linalg.inv(D * np.eye(3))) @ Omega @ Sigma))
    ev = np.linalg.eigvals(M)
    omega = float(np.max(np.abs(ev.imag)))
    gam_eff = float(-np.mean(ev.real[np.abs(ev.imag) > 1e-9])) if omega > 1e-9 else gamma
    return M, sigma, ev, omega, gam_eff


def simulate_winding(M, D, rng):
    sd = np.sqrt(2.0 * D * DT)
    z = rng.standard_normal((N_REAL, 3)) * np.sqrt(D)
    for _ in range(T_EQ):
        z = z + (z @ M.T) * DT + rng.standard_normal((N_REAL, 3)) * sd
    u = z @ P.T                                            # project to rotation plane
    phi = np.zeros(N_REAL)
    for _ in range(T_OBS):
        z = z + (z @ M.T) * DT + rng.standard_normal((N_REAL, 3)) * sd
        un = z @ P.T
        du = un - u
        mid = 0.5 * (u + un)
        r2 = (mid * mid).sum(1) + 1e-12
        phi += (mid[:, 0] * du[:, 1] - mid[:, 1] * du[:, 0]) / r2
        u = un
    return finite("winding", phi)


def measure(gamma, g, D, rng):
    M, sigma, ev, omega, gam_eff = exact(gamma, g, D)
    tau = T_OBS * DT
    phi = simulate_winding(M, D, rng)
    mean, var = float(phi.mean()), float(phi.var(ddof=1))
    snr = mean * mean / var
    bound = sigma * tau / 2.0
    T = sigma * tau * var / (2.0 * mean * mean)
    cycles = abs(mean) / (2.0 * np.pi)                      # cycles completed over tau
    A = sigma * tau / cycles if cycles > 1e-9 else float("nan")   # affinity per cycle (nats)
    return dict(gamma=gamma, g=g, D=D, sigma=sigma, omega=omega, gam_eff=gam_eff,
                ratio=omega / gam_eff, mean=mean, var=var, snr=snr, bound=bound, T=T,
                A=A, tur_ok=snr <= bound * 1.10, ev=ev)


def main():
    rng = np.random.default_rng(SEED)
    g0, gam0 = 0.6, 1.0

    print("Noisy frustrated Banach-class reference: N=3 cyclic non-reciprocal OU")
    print(f"base: gamma={gam0}, g={g0};  M eigenvalues (complex pair = k_frust):")
    _, _, ev, _, _ = exact(gam0, g0, 0.1)
    for e in ev:
        print(f"    {e:.4f}")

    # ---- NOISE SWEEP: is the affinity (and omega/gamma) noise-independent? ----
    print("\nNOISE SWEEP (vary D at fixed structure g/gamma).  Canonical quantities should be FLAT.")
    hdr = f"{'D':>6} | {'<sigma>':>9} {'omega/gam':>10} {'affinity A':>11} | {'SNR_J':>8} {'sig*t/2':>9} TUR | {'T':>7}"
    print(hdr); print("-" * len(hdr))
    Ds = [0.02, 0.05, 0.1, 0.2, 0.4]
    rowsD = []
    for D in Ds:
        m = measure(gam0, g0, D, rng)
        rowsD.append(m)
        print(f"{D:>6.3f} | {m['sigma']:>9.4f} {m['ratio']:>10.4f} {m['A']:>11.4f} | "
              f"{m['snr']:>8.2f} {m['bound']:>9.2f} {'ok' if m['tur_ok'] else 'XX':>3} | {m['T']:>7.3f}")

    A_arr = np.array([m["A"] for m in rowsD])
    ratio_arr = np.array([m["ratio"] for m in rowsD])
    A_spread = float(np.std(A_arr) / np.mean(A_arr))
    ratio_spread = float(np.std(ratio_arr) / np.mean(ratio_arr))
    print(f"\n  affinity A: mean {A_arr.mean():.3f} nats, rel-spread {100*A_spread:.1f}% across the noise sweep")
    print(f"  omega/gamma: mean {ratio_arr.mean():.3f}, rel-spread {100*ratio_spread:.1f}%")

    # ---- STRUCTURE SWEEP: affinity should track g/gamma (the fingerprint) ----
    print("\nSTRUCTURE SWEEP (vary g at fixed D, gamma).  Affinity should TRACK g/gamma.")
    print(f"{'g/gam':>6} | {'omega/gam':>10} {'affinity A':>11} | {'T':>7}")
    rowsG = []
    for g in [0.3, 0.6, 1.0, 1.6]:
        m = measure(gam0, g, 0.1, rng)
        rowsG.append(m); print(f"{g/gam0:>6.2f} | {m['ratio']:>10.4f} {m['A']:>11.4f} | {m['T']:>7.3f}")

    tur_all = all(m["tur_ok"] for m in rowsD + rowsG)
    print("\n================ VERDICT ================")
    canonical = (A_spread < 0.10) and (ratio_spread < 0.05)
    if tur_all and canonical:
        print("INSTANCED. The noisy frustrated N=3 cycle carries a DIMENSIONLESS, NOISE-INDEPENDENT")
        print(f"canonical quantity: affinity A = {A_arr.mean():.2f} nats (spread {100*A_spread:.1f}%),")
        print(f"spectral ratio omega/gamma = {ratio_arr.mean():.3f} (spread {100*ratio_spread:.1f}%) — both")
        print("set by the structure g/gamma, flat across noise. TUR floor T>=1 holds throughout.")
        print("=> A dimensionless intrinsic canonical quantity EXISTS on a noisy Banach-class cycle.")
        print("   The deterministic Banach lacked it (no current); the two-frame self-frame supplies it.")
    else:
        print(f"NOT clean: TUR_ok={tur_all}, A-spread={100*A_spread:.1f}% (want <10%), "
              f"ratio-spread={100*ratio_spread:.1f}% (want <5%). Read honestly.")
    print("\nHonest scope: 'drive-independence' shown here is NOISE-independence + structure-set affinity.")
    print("The cdv1 'J flows with chit, affinity fixed' needs the NONLINEAR (gain+saturation, Stuart-")
    print("Landau-cyclic) extension — the linear model has no chit/amplitude knob. Next step if this holds.")
    print("Synthetic reference: serves the dimensionless dream + calibration; does NOT meet 846 (real substrate).")

    # ---- figure ----
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    # left: eigenvalue spectrum (complex pair = k_frust)
    _, _, ev0, _, _ = exact(gam0, g0, 0.1)
    ax[0].axhline(0, color="gray", lw=0.6); ax[0].axvline(0, color="gray", lw=0.6)
    ax[0].scatter(ev0.real, ev0.imag, s=120, c="tab:red", zorder=3, edgecolor="k")
    ax[0].set_xlabel("Re(eig)"); ax[0].set_ylabel("Im(eig)")
    ax[0].set_title("M spectrum: a complex pair (Im≠0) = the k_frust signature\n"
                    "rotation forced by the cyclic structure (topological, not drive)")
    ax[0].grid(alpha=0.3)
    # right: noise sweep — canonical quantities flat
    Dv = np.array([m["D"] for m in rowsD])
    ax[1].plot(Dv, [m["A"] for m in rowsD], "o-", color="tab:purple", label=r"affinity $A$ (nats) — CANONICAL")
    ax[1].plot(Dv, [m["ratio"] for m in rowsD], "s-", color="tab:green", label=r"$\omega/\gamma$ — CANONICAL")
    ax[1].plot(Dv, [m["T"] for m in rowsD], "^--", color="tab:blue", label=r"self-frame $T$ (violation factor)")
    ax2 = ax[1].twinx()
    ax2.plot(Dv, [m["sigma"] for m in rowsD], "x:", color="tab:red", label=r"$\langle\sigma\rangle$ (dimensionful)")
    ax2.set_ylabel(r"$\langle\sigma\rangle$", color="tab:red")
    ax[1].set_xlabel("noise D"); ax[1].set_ylabel("dimensionless quantities")
    ax[1].set_title("noise sweep: affinity & ω/γ FLAT (noise-independent canonical)\n⟨σ⟩ set by structure (also flat here); T is the bounded violation")
    l1, lb1 = ax[1].get_legend_handles_labels(); l2, lb2 = ax2.get_legend_handles_labels()
    ax[1].legend(l1 + l2, lb1 + lb2, fontsize=8, loc="center right"); ax[1].grid(alpha=0.3)
    fig.suptitle("Noisy frustrated Banach-class reference — dimensionless affinity as canonical quantity", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    png = OUT / "banach_frustrated.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
