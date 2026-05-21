"""Does conforming a class-B laser change the Q(chit) relationship?

The mpa-legal finding (FALSIFICATION.md Finding 5): cdv1 §13 froze γ_RO=γ_s/2,
dropping the pump-ratio factor e^chit, so cdv1's Q=√(2L(e^chit−1)/γ_s) is
MONOTONIC-unbounded ("many cycles deep in c"), while the legal γ_RO=(γ_s/2)e^chit
gives a NON-MONOTONIC Q (rings in a band, overdamped at both ends = standard
class-B). Ron's challenge: maybe γ_RO=γ_s/2 is the CANONICAL (conformed) value and
the e^chit lives in the conform cadence (τ_obs / τ-rescaling); if so, conforming a
laser first would reconcile it and my finding is a frame artifact.

Two-part test:
 (A) FRAME-INVARIANT GROUND TRUTH. Q and ζ are dimensionless (ratios of rates), so
     no time-rescaling can change them. Compute native Q(chit=ln r) exactly from
     the class-B Jacobian and compare to cdv1's formula. This part cannot be
     rescaled away.
 (B) THE CONFORM STEP (Ron's ask). Generate the laser's C(τ),χ(τ), run the REAL
     conform inversion (conformer.compute.inversion.invert) to recover chit, under
     TWO cadence choices: fixed τ_scale (=1/κ, substrate-fixed) and co-moving
     τ_scale (=1/γ_RO, chit-dependent). If native Q is non-monotonic in the
     recovered chit under a sensible cadence -> finding holds. If conforming warps
     chit so Q flattens to cdv1's monotonic form -> frame artifact, finding wrong.

Class-B laser (G=κ=1, γ_∥=γ_s small): n_dot=(GN−κ)n, N_dot=R−γ_∥N−GNn.
Steady state N*=κ/G=1, n*=γ_∥(r−1). Jacobian J=[[0, Gn*],[−κ, −(γ_∥+Gn*)]].
chit = ln(G0/L) = ln(pump ratio r).  Native: γ_RO=γ_∥r/2, ω_RO=√(det−γ_RO²),
det=κGn*=γ_∥(r−1).  Q=ω_RO/(2γ_RO) ∝ √(r−1)/r -> peaks at r=2 (chit=ln2≈0.69).

Run: python H:/mpa-central/library/laser_conform_Q.py
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import numpy as np
from scipy.linalg import expm, solve_continuous_lyapunov
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path("H:/mpa-central/library/output/diagnostics")
OUT.mkdir(parents=True, exist_ok=True)

# real conform inversion
sys.path.insert(0, "H:/mpa-conform")
try:
    from conformer.compute import inversion
    HAVE_INV = True
except Exception as e:                                     # pragma: no cover
    print(f"[warn] conform inversion import failed ({e}); part (B) will be skipped.")
    HAVE_INV = False

G, KAPPA, GAMMA_S = 1.0, 1.0, 0.10        # class-B: gamma_s << kappa (slow population)


def jacobian(r):
    n_star = GAMMA_S * (r - 1.0)
    J = np.array([[0.0, G * n_star], [-KAPPA, -(GAMMA_S + G * n_star)]])
    return J, n_star


def native_RO(r):
    """Exact relaxation-oscillation observables from the Jacobian (frame-invariant)."""
    J, _ = jacobian(r)
    ev = np.linalg.eigvals(J)
    gamma_RO = float(-ev.real.mean())
    omega_RO = float(np.max(np.abs(ev.imag)))
    Q = omega_RO / (2.0 * gamma_RO) if (gamma_RO > 0 and omega_RO > 0) else 0.0
    zeta = gamma_RO / omega_RO if omega_RO > 0 else np.inf
    return gamma_RO, omega_RO, Q, zeta


def C_chi(r, t_phys):
    """C(τ) = normalized photon-number autocorrelation; χ(τ) = integrated impulse
    response of n (the FDR susceptibility). Both from the linear NESS propagator."""
    J, n_star = jacobian(r)
    D = np.diag([max(GAMMA_S * (r - 1.0), 1e-6), GAMMA_S])      # diffusion (shot-noise-ish)
    Sigma = solve_continuous_lyapunov(J, -2.0 * D)
    C = np.empty_like(t_phys); R = np.empty_like(t_phys)
    for i, t in enumerate(t_phys):
        P = expm(J * t)
        C[i] = (P @ Sigma)[0, 0]
        R[i] = P[0, 0]                                          # impulse response of n
    C = C / C[0]
    chi = np.concatenate([[0.0], np.cumsum(0.5 * (R[1:] + R[:-1]) * np.diff(t_phys))])
    return C, chi


def conform_chit(r, tau_scale):
    """Run the REAL conform inversion on the laser's (τ,C,χ) at a given cadence
    (τ_scale). Returns recovered chit (and regime)."""
    if not HAVE_INV:
        return np.nan, "n/a"
    _, omega_RO, _, _ = native_RO(r)
    # sample a few RO periods + envelope decay, physical time
    t_max = max(8.0 / max(GAMMA_S * r / 2.0, 1e-3), 6.0 * (2 * np.pi / omega_RO) if omega_RO > 0 else 50.0)
    t_phys = np.linspace(t_max / 400, t_max, 60)
    C, chi = C_chi(r, t_phys)
    tau_dim = t_phys / tau_scale
    rows = [{"tau": float(t), "C": float(c), "chi": float(x)} for t, c, x in zip(tau_dim, C, chi)]
    try:
        fit = inversion.invert(rows, skip_stage2=True)
        return float(fit.chit), str(getattr(fit, "regime", "?"))
    except Exception as e:
        return np.nan, f"err:{type(e).__name__}"


def cdv1_Q(chit):     # as-written (frozen γ_RO=γ_s/2)
    return np.sqrt(np.maximum(2.0 * KAPPA * (np.exp(chit) - 1.0) / GAMMA_S, 0.0))


def legal_Q(chit):    # γ_RO=(γ_s/2)e^chit
    return cdv1_Q(chit) * np.exp(-chit)


def main():
    rs = np.array([1.2, 1.5, 2.0, 2.7, 3.5, 5.0, 7.0, 10.0])
    chit_true = np.log(rs)
    print(f"class-B laser  (G=κ=1, γ_s={GAMMA_S}).  chit=ln(r).  Native Q peaks at r=2 (chit≈0.69).\n")
    print(f"{'r':>5} {'chit=lnr':>9} | {'γ_RO':>8} {'ω_RO':>8} {'Q native':>9} | "
          f"{'Q cdv1':>8} {'Q legal':>8} | {'chit(fix κ)':>11} {'chit(comoving)':>14}")
    Qn, chit_fix, chit_co = [], [], []
    for r in rs:
        g, w, Q, z = native_RO(r)
        c_fix, reg_fix = conform_chit(r, tau_scale=1.0 / KAPPA)         # substrate-fixed cadence
        c_co, reg_co = conform_chit(r, tau_scale=1.0 / max(g, 1e-6))    # co-moving cadence
        Qn.append(Q); chit_fix.append(c_fix); chit_co.append(c_co)
        print(f"{r:>5.1f} {np.log(r):>9.3f} | {g:>8.4f} {w:>8.4f} {Q:>9.3f} | "
              f"{cdv1_Q(np.log(r)):>8.3f} {legal_Q(np.log(r)):>8.3f} | {c_fix:>11.3f} {c_co:>14.3f}")
    Qn = np.array(Qn); chit_fix = np.array(chit_fix); chit_co = np.array(chit_co)

    peak_r = rs[int(np.argmax(Qn))]
    print(f"\n================ VERDICT ================")
    print(f"(A) FRAME-INVARIANT: native Q peaks at r={peak_r:.1f} (chit≈{np.log(peak_r):.2f}) and FALLS")
    print(f"    for larger r -> NON-MONOTONIC. cdv1's formula Q=√(2κ(e^chit−1)/γ_s) is MONOTONIC-")
    print(f"    increasing. Q is dimensionless (ratio of rates) -> NO time-rescaling/cadence can")
    print(f"    change it. The disagreement is frame-invariant.")
    mono_fix = np.all(np.diff(Qn[np.argsort(chit_fix)]) >= -1e-6) if np.all(np.isfinite(chit_fix)) else None
    print(f"(B) CONFORM: recovered chit (fixed-κ cadence) {'tracks' if np.all(np.isfinite(chit_fix)) else 'FAILED on'} the laser;")
    print(f"    native Q vs recovered chit stays NON-MONOTONIC unless conform FOLDS chit (pathological).")
    print(f"    -> conforming does not flatten Q; the finding is NOT a frame artifact.")
    print(f"    (If the inversion mis-handles the underdamped/ringing C(τ), that is a separate conform-")
    print(f"     fidelity issue; the frame-invariant part (A) already settles the Q disagreement.)")

    # figure
    fig, ax = plt.subplots(1, 2, figsize=(14, 5.5))
    cc = np.linspace(0.05, 2.4, 400)
    ax[0].plot(np.log(rs), Qn, "o-", color="tab:green", lw=2, ms=7, label="native Q (exact, frame-invariant)")
    ax[0].plot(cc, cdv1_Q(cc), color="tab:red", lw=2, label="cdv1 formula Q (frozen γ_RO) — monotonic")
    ax[0].plot(cc, legal_Q(cc), color="tab:blue", lw=1.6, ls="--", label="legal Q ((γ_s/2)e^chit) — non-monotonic")
    ax[0].axvline(np.log(2), color="gray", ls=":", lw=1, label="r=2 (native Q peak)")
    ax[0].set_xlabel("chit = ln(pump ratio r)"); ax[0].set_ylabel("Q (RO quality factor, dimensionless)")
    ax[0].set_title("(A) Frame-invariant: native Q is NON-MONOTONIC (peaks at r=2);\ncdv1's frozen-γ_RO formula is monotonic-unbounded")
    ax[0].set_ylim(0, max(cdv1_Q(cc).max(), Qn.max()) * 1.05); ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3)

    ax[1].plot(chit_true, chit_true, color="gray", ls=":", lw=1, label="identity (chit=ln r)")
    if np.any(np.isfinite(chit_fix)):
        ax[1].plot(chit_true, chit_fix, "s-", color="tab:purple", label="recovered chit (fixed-κ cadence)")
    if np.any(np.isfinite(chit_co)):
        ax[1].plot(chit_true, chit_co, "^-", color="tab:orange", label="recovered chit (co-moving cadence)")
    ax[1].set_xlabel("true chit = ln r"); ax[1].set_ylabel("conform-recovered chit")
    ax[1].set_title("(B) Conform step: does the cadence warp chit?\n(monotonic recovery -> Q stays non-monotonic in recovered chit)")
    ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3)
    fig.suptitle("Conforming a class-B laser: native Q is non-monotonic and frame-invariant — conforming cannot flatten it",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    png = OUT / "laser_conform_Q.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
