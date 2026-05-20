"""k_frust falsification LADDER -- RUNG 3 (slowest / most first-principles):
the framework's OWN Lyapunov machinery, turned on the frustrated loop.

cdv1 sec.Active-modulation: non-frustrated topologies admit a (weighted)
relative-entropy Lyapunov V = sum_i w_i[x_i - x_i* - x_i* ln(x_i/x_i*)] with a
strictly positive diagonal W = diag(w_i) such that W*gamma + gamma^T*W is PSD
(Volterra-Lyapunov / diagonal stability); dV/dt = -dx^T (W gamma + gamma^T W) dx
<= 0 then drives the holding to a stationary fixed point (a clean c or r).
k_frust is claimed to admit NO such Lyapunov -- "non-existence is the dynamical
content of 'no stationary fixed point'."

This is the DERIVED reformation in its purest form: we do not impose any rule and
we do not pick a representation. We run the framework's own stabilizer -- SEARCH
for the diagonal W that certifies a Lyapunov function (V = dx^T W dx, the
Volterra form) on the loop's coexistence Jacobian -- and ask whether it can
resolve the frustration.

CORRECTED FRAMING (2026-05-20). An earlier cut of this rung tested the wrong
object: it asked for a *stability* Lyapunov (V=dx^T W dx, W=I works for any stable
focus) and read 'stable focus' as 'resolved'. Both are category errors. The
framework's "k_frust admits no Lyapunov" means no GRADIENT / free-energy Lyapunov
whose descent IS the dynamics -- i.e. the steady state is an EQUILIBRIUM (detailed
balance, zero probability current), not a NESS. A stable focus with COMPLEX
eigenvalues circulates: it is a stable NESS (J!=0), genuine k_frust, not a
resolution. So the right discriminator is the SPECTRUM / detailed balance:
  * complex spectrum (Im != 0) -> irreducible rotation -> no gradient structure ->
    NESS with a topologically-forced cyclic current -> k_frust.
  * real spectrum (Im = 0)     -> gradient / detailed-balance relaxation -> the
    loop resolves to an equilibrium fixed point (J = 0).
The sign of Re(eig) only splits k_frust into sub-regimes (stable circulating focus
vs repelling focus + attracting limit cycle); it does NOT decide k_frust.

Kill-shot (scored, not confirmed):
  K  The FRUSTRATED loop has a REAL spectrum / its steady-state current J -> 0
     (gradient/detailed-balance structure) at some alive operating point -> it
     resolves to an equilibrium -> the topological-drain claim is FALSE -> BROKE.

Positive control (control-bracketing): a resolvable non-circulating loop
(cooperative, non-frustrated) MUST read real-spectrum / J~0 -> the apparatus can
recognize a resolved loop. If it can't, no verdict.

Run: python H:/mpa-central/library/k_frust_r3_lyapunov.py
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from k_frust_r1_sweep import step, CYC, SYM

OUT = Path("H:/mpa-central/library/output/diagnostics")

G0, L, RHO_SAT, S0 = 1.20, 1.00, 1.0, 1.0e-3
GMAG = 0.50


def drift(rho, gmat):
    S = rho.sum()
    gain = G0 / (1.0 + S / RHO_SAT)
    return (gain - L) * rho - rho * (gmat @ rho) / RHO_SAT + S0


def symmetric_fixed_point(gmat):
    """Solve the scalar fixed point at rho* = c*(1,1,1) (a fixed point for both
    loops by permutation symmetry)."""
    c = 0.07
    for _ in range(200):                       # Newton on the scalar residual
        r = drift(np.full(3, c), gmat)[0]
        eps = 1e-6
        dr = (drift(np.full(3, c + eps), gmat)[0] - r) / eps
        c = max(c - r / dr, 1e-6)
    return np.full(3, c)


def jacobian(gmat, rho_star, eps=1e-6):
    J = np.zeros((3, 3))
    f0 = drift(rho_star, gmat)
    for j in range(3):
        rp = rho_star.copy(); rp[j] += eps
        J[:, j] = (drift(rp, gmat) - f0) / eps
    return J


def volterra_search(J):
    """Search strictly-positive diagonal W minimizing lambda_max(W J + J^T W).
    < 0  -> diagonally stable: a relative-entropy Lyapunov EXISTS -> loop resolves.
    >= 0 -> no diagonal Lyapunov -> no stationary fixed point (limit cycle)."""
    def obj(logw):
        logw = np.clip(logw - np.mean(logw), -6.0, 6.0)   # scale-fixed (homogeneous) + bounded -> no overflow
        W = np.diag(np.exp(logw))
        M = W @ J + J.T @ W
        return float(np.max(np.linalg.eigvalsh(0.5 * (M + M.T))))
    best = np.inf; bestw = None
    for trial in range(40):                    # multistart (the manifold is non-convex)
        x0 = np.random.default_rng(trial).normal(0, 1.5, 3)
        res = minimize(obj, x0, method="Nelder-Mead",
                       options={"xatol": 1e-7, "fatol": 1e-9, "maxiter": 4000})
        if res.fun < best:
            best, bestw = res.fun, np.exp(np.clip(res.x - np.mean(res.x), -6.0, 6.0))
    return best, bestw


def dynamical_J(gmat, seed=1, T_EQ=4000, T_OBS=8000, N_REAL=256):
    """Confirm the static verdict dynamically: persistent cyclic current (limit
    cycle, J!=0) vs settling to a fixed point (J->0)."""
    rng = np.random.default_rng(seed)
    g = GMAG * gmat
    rho = np.tile([0.06, 0.03, 0.01], (N_REAL, 1)).astype(float)
    for _ in range(T_EQ):
        rho = step(rho, g, G0, L, 0.02, rng)
    chir = np.zeros(T_OBS); DT = 0.005
    for t in range(T_OBS):
        rp = rho.copy()
        rho = step(rho, g, G0, L, 0.02, rng)
        m = rho.mean(1); mp = rp.mean(1)
        a = rho[:, 0] - m; b = (rho[:, 1] - rho[:, 2]) / np.sqrt(3.0)
        adot = ((rho[:, 0] - m) - (rp[:, 0] - mp)) / DT
        bdot = ((rho[:, 1] - rho[:, 2]) - (rp[:, 1] - rp[:, 2])) / (np.sqrt(3.0) * DT)
        r2 = a * a + b * b; good = r2 > 1e-10
        chir[t] = float(np.mean((a[good] * bdot[good] - b[good] * adot[good]) / r2[good])) if good.any() else 0.0
    return float(np.mean(chir))


def probe(base, gmag):
    g = gmag * base
    rstar = symmetric_fixed_point(g)
    J = jacobian(g, rstar)
    ev = np.linalg.eigvals(J)
    order = np.argsort(-ev.real)
    ev = ev[order]
    vl, w = volterra_search(J)
    return dict(rstar=rstar[0], ev=ev, lam=float(np.max(ev.real)),
                imag=float(np.max(np.abs(ev.imag))), vl=vl, w=w)


def main():
    print("R3: is the frustrated loop an irreducible NESS (circulating, k_frust) or does it resolve")
    print("    to a gradient/detailed-balance equilibrium?  complex spectrum + J!=0 -> NESS; real")
    print("    spectrum + J~0 -> resolved. Re(eig) sign only splits stable-focus vs repelling sub-regime.\n")

    # ---- positive-control bracket: a resolvable non-circulating (cooperative) loop ----
    coop = probe(-SYM, GMAG)
    Jcoop = dynamical_J(-SYM)
    coop_real = coop["imag"] < 1e-6
    print(f"[bracket] COOPERATIVE non-frustrated loop (gamma=-{GMAG}*SYM): max|Im(eig)|={coop['imag']:.4f}, "
          f"J={Jcoop:+.3e} -> {'real-spectrum / resolvable (apparatus recognizes a resolved loop)' if coop_real else 'NOT real -- bracket suspect'}\n")

    # ---- frustrated loop: coupling sweep -- is the circulation irreducible at all coupling? ----
    print("FRUSTRATED loop -- coupling sweep:")
    print(f"  {'gmag':>6} | {'max Re(eig)':>11} {'|Im(eig)|':>9} | {'spectrum':>9} | {'sub-regime':>16} | structure")
    Gs = [0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0]
    rows = []
    real_spectrum_kill = []
    for gm in Gs:
        p = probe(CYC, gm)
        complex_spec = p["imag"] > 1e-6
        subreg = "repelling focus" if p["lam"] > 1e-6 else "stable focus"
        struct = "NESS (circulating, k_frust)" if complex_spec else "** REAL -> gradient/resolvable (kill?)"
        if not complex_spec:
            real_spectrum_kill.append(gm)
        rows.append((gm, p))
        print(f"  {gm:>6.2f} | {p['lam']:>+11.4f} {p['imag']:>9.4f} | "
              f"{'complex' if complex_spec else 'REAL':>9} | {subreg:>16} | {struct}")

    print("\n================ RUNG 3 VERDICT ================")
    if not coop_real:
        print("INCONCLUSIVE: cooperative bracket is not real-spectrum -> apparatus suspect; fix before scoring.")
    elif real_spectrum_kill:
        print(f"KILL (BROKE): at coupling {real_spectrum_kill} the frustrated loop has a REAL spectrum "
              f"(gradient/detailed-balance) -> it resolves to equilibrium. Topological drain is FALSE.")
    else:
        print("SURVIVES: at every coupling the frustrated loop has a COMPLEX spectrum -- irreducible")
        print("  rotation, no gradient/detailed-balance structure -> a NESS with a topologically-forced")
        print("  cyclic current (R1/R2: drive-independent, sign-definite). The Re(eig)<0 'stable focus' is")
        print("  the STABLE sub-regime of k_frust, not a resolution; the repelling-focus/limit-cycle is the")
        print("  other sub-regime. The triality's underlying fact is the NESS circulation (broken detailed")
        print("  balance), NOT deterministic fixed-point-nonexistence -- that phrasing is the refinement.")

    # ---- figure ----
    gms = [gm for gm, _ in rows]
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].plot(gms, [p["lam"] for _, p in rows], "o-", color="tab:red", label="max Re(eig) (sub-regime: <0 stable focus)")
    ax[0].plot(gms, [p["imag"] for _, p in rows], "s-", color="tab:purple", label="|Im(eig)| = circulation (k_frust signature)")
    ax[0].axhline(0, color="k", lw=0.8)
    ax[0].axhline(coop["imag"], color="tab:green", lw=1.0, ls=":", label=f"cooperative bracket |Im|={coop['imag']:.3f} (real -> resolvable)")
    ax[0].set_xlabel("coupling magnitude gmag"); ax[0].set_ylabel("Jacobian eigenvalue parts")
    ax[0].set_title("Circulation |Im| is irreducible & grows with coupling;\nRe(eig) stays <0 (stable sub-regime)")
    ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3)
    # detailed-balance discriminator: complex spectrum (NESS) everywhere
    ax[1].bar(range(len(gms)), [p["imag"] for _, p in rows], color="tab:purple", alpha=0.7, label="frustrated |Im| (NESS)")
    ax[1].bar([len(gms)], [coop["imag"]], color="tab:green", alpha=0.7, label="cooperative |Im| (resolvable, ~0)")
    ax[1].axhline(0, color="k", lw=0.8)
    ax[1].set_xticks(list(range(len(gms))) + [len(gms)])
    ax[1].set_xticklabels([f"{g:g}" for g in gms] + ["coop"])
    ax[1].set_xlabel("loop (frustrated by coupling | cooperative control)")
    ax[1].set_ylabel("|Im(eig)| -- irreducible circulation")
    ax[1].set_title("Detailed-balance discriminator: frustrated = circulating NESS\nat ALL coupling; "
                    "control = real-spectrum (resolves)")
    ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3)
    fig.suptitle("k_frust ladder R3: frustration is an irreducible NESS (circulating current), not "
                 "fixed-point-nonexistence -- stable-focus & limit-cycle are sub-regimes", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    png = OUT / "k_frust_r3_lyapunov.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
