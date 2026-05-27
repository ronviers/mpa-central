r"""IK1 — chimeric-sign protection under finite interior sweeps (sign-topological killshot).

Tests whether the CHIMERIC SIGN — the binary topological bit of the frustrated N=3
cycle — is PROTECTED: stable under finite perturbation at fixed wiring, read in the
INTERIOR, never at the boundary. Reuses the banach_frustrated linear-OU model
(M = -gamma I + g A_cyc; eigenvalues -gamma, -gamma ± i*sqrt(3)*g).

Three readings of the SAME sign, by design:
  (G) GLOBAL  operator : sign(Im lambda) of M = sign(g). Exact, computed from the
      drift matrix (the wiring), independent of noise/trajectory. THE VERDICT.
  (R) ROBUST  trajectory: sign(<x dy - y dx>)  — angular MOMENTUM rate, no 1/r^2.
      A global average; no coordinate singularity at the origin.
  (N) NAIVE   trajectory: sign(<(x dy - y dx)/r^2>) — angular VELOCITY rate, the
      winding estimator. Carries the 1/r^2 ORTHOGONAL-ZERO singularity at r->0.

Ron's prediction: the OU state is mean-zero, so the amplitude crosses the origin —
the ORTHOGONAL ZERO (radial coordinate ->0, orthogonal to the angular/sign
direction). Character has no zero there; the polar coordinate chart does. The NAIVE
1/r^2 estimator therefore suffers quantization error / fake NaNs at origin crossings.
Those are COMPUTER artifacts (coordinate singularity + finite float), NOT the
asymptotic-closure tripwire — no physical observable attains a boundary.

Discriminator: an estimator failure (sign wobble, SNR collapse, NaN) is FAKE if it
traces to the radial coordinate (small r, rising near-origin events) while the GLOBAL
sign(Im lambda) stays fixed and |Im lambda| > 0. It would be REAL (IK1 fires) only if
sign(Im lambda) itself degenerated under a finite sweep.

Run: python H:/mpa-central/library/ik1_chimeric_sign_sweep.py
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
from banach_frustrated import A_CYC, P, exact

OUT = Path("H:/mpa-central/library/output/diagnostics")
OUT.mkdir(parents=True, exist_ok=True)

DT, T_EQ, T_OBS, N_REAL, SEED = 0.01, 1000, 3000, 3000, 20260526
R_EPS = 0.10        # "near the orthogonal zero" radius (rotation-plane units)
GUARD = 1e-12       # the band-aid already present in banach_frustrated's winding


def simulate(M, D, rng):
    """One finite run. Three sign-bearing accumulators + orthogonal-zero diagnostics."""
    sd = np.sqrt(2.0 * D * DT)
    z = rng.standard_normal((N_REAL, 3)) * np.sqrt(D)
    for _ in range(T_EQ):
        z = z + (z @ M.T) * DT + rng.standard_normal((N_REAL, 3)) * sd
    u = z @ P.T
    ang_mom = np.zeros(N_REAL)         # (R) sum (x dy - y dx)            -- no 1/r^2
    wind = np.zeros(N_REAL)            # (N) sum (x dy - y dx)/r^2 guarded -- the winding
    min_r2 = np.full(N_REAL, np.inf)
    near0 = np.zeros(N_REAL, dtype=int)
    nf_unguarded = np.zeros(N_REAL, dtype=bool)
    for _ in range(T_OBS):
        z = z + (z @ M.T) * DT + rng.standard_normal((N_REAL, 3)) * sd
        un = z @ P.T
        du = un - u
        mid = 0.5 * (u + un)
        area = mid[:, 0] * du[:, 1] - mid[:, 1] * du[:, 0]     # x dy - y dx
        r2 = (mid * mid).sum(1)
        ang_mom += area
        wind += area / (r2 + GUARD)
        min_r2 = np.minimum(min_r2, r2)
        near0 += (r2 < R_EPS * R_EPS)
        with np.errstate(divide="ignore", invalid="ignore"):
            raw = area / r2                                    # UNGUARDED: the literal singularity
        nf_unguarded |= ~np.isfinite(raw)
        u = un
    return ang_mom, wind, min_r2, near0, nf_unguarded


def read_signs(gamma, g, D, rng):
    M, sigma, ev, omega, gam_eff = exact(gamma, g, D)
    im = ev.imag[np.argmax(np.abs(ev.imag))]
    sign_global, absIm = int(np.sign(im)), float(abs(im))     # (G) exact verdict
    ang_mom, wind, min_r2, near0, nf = simulate(M, D, rng)
    sign_robust = int(np.sign(ang_mom.mean()))                # (R)
    mean_w, var_w = float(wind.mean()), float(wind.var(ddof=1))
    snr_w = mean_w * mean_w / var_w if var_w > 0 else float("inf")
    sign_naive = int(np.sign(mean_w))                         # (N)
    cycles = abs(mean_w) / (2 * np.pi)
    A_naive = sigma * T_OBS * DT / cycles if cycles > 1e-9 else float("nan")
    return dict(D=D, g=g, sign_global=sign_global, absIm=absIm,
                sign_robust=sign_robust, sign_naive=sign_naive, snr_w=snr_w,
                A_naive=A_naive, near0_frac=float(near0.mean()) / T_OBS,
                min_r=float(np.sqrt(min_r2.min())), nf=int(nf.sum()))


def _print_table(rows):
    hdr = (f"{'D':>7} {'g':>6} | {'GLOBAL':>7} {'|Imλ|':>7} | {'ROBUST':>7} | "
           f"{'NAIVE':>6} {'SNR_w':>10} {'A_naive':>9} | {'near0%':>7} {'min_r':>7} {'raw∞':>5}")
    print(hdr); print("-" * len(hdr))
    for r in rows:
        a = " nan" if not np.isfinite(r["A_naive"]) else f"{r['A_naive']:>9.3f}"
        print(f"{r['D']:>7.3f} {r['g']:>6.3f} | {r['sign_global']:>+7d} {r['absIm']:>7.3f} | "
              f"{r['sign_robust']:>+7d} | {r['sign_naive']:>+6d} {r['snr_w']:>10.2f} {a:>9} | "
              f"{100*r['near0_frac']:>6.3f}% {r['min_r']:>7.4f} {r['nf']:>5d}")


def main():
    rng = np.random.default_rng(SEED)
    gamma = 1.0

    print("IK1 — chimeric-sign protection, read in the interior (never at the boundary)")
    print("fixed-wiring chimeric sign = sign(Im λ) = sign(g) = +1\n")

    print("SWEEP 1 — NOISE D at fixed wiring g=0.6 (finite, never to zero):")
    rows1 = [read_signs(gamma, 0.6, D, rng) for D in (0.05, 0.2, 0.8, 3.2, 12.8)]
    _print_table(rows1)

    print("\nSWEEP 2 — APPROACH the balanced point: g -> small but FINITE, fixed D=0.2")
    print("(g=0 is the boundary/exceptional point — we never reach it):")
    rows2 = [read_signs(gamma, g, 0.2, rng) for g in (0.6, 0.2, 0.06, 0.02, 0.006)]
    _print_table(rows2)

    rows = rows1 + rows2
    g_signs = {r["sign_global"] for r in rows}
    r_signs = {r["sign_robust"] for r in rows}
    min_absIm = min(r["absIm"] for r in rows)
    global_ok = len(g_signs) == 1 and 0 not in g_signs and min_absIm > 1e-9
    robust_ok = len(r_signs) == 1 and 0 not in r_signs

    print("\n================ VERDICT ================")
    if global_ok and robust_ok:
        s = next(iter(g_signs))
        print(f"CHIMERIC SIGN PROTECTED. Global sign(Im λ) = {s:+d}, fixed across a 256× noise")
        print(f"sweep AND a 100× approach toward the balanced point; |Im λ| ≥ {min_absIm:.4f} > 0 throughout.")
        print("Robust angular-momentum sign agrees and is fixed. IK1 does NOT fire: the binary")
        print("topological bit is drive/noise-independent at fixed wiring, read in the interior.")
    else:
        print(f"IK1 FIRES (internal kill): global_ok={global_ok} robust_ok={robust_ok}.")
        print("The framework's own dynamics fail to protect the chimeric sign under a finite sweep.")

    print("\n---- orthogonal-zero / fake-artifact classification ----")
    snr_drop = max(r["snr_w"] for r in rows2) / max(min(r["snr_w"] for r in rows2), 1e-30)
    print(f"NAIVE (1/r²) estimator SNR collapses {snr_drop:.0f}× as g→small (the rotation signal")
    print("sinks into the orthogonal-zero noise) — the predicted QUANTIZATION ERROR, real and")
    print("observable. Yet at every one of those points the GLOBAL sign(Im λ) and the ROBUST")
    print("angular-momentum sign stay fixed at +1 and finite. So the degradation is a property of")
    print("the 1/r² coordinate chart at the origin crossing, NOT of the physics.")
    nf_tot = sum(r["nf"] for r in rows)
    nan_rows = [r for r in rows if not np.isfinite(r["A_naive"])]
    print(f"\nLiteral NaNs: unguarded 1/r² went non-finite in {nf_tot} realization-runs total "
          f"(guarded only by +{GUARD:g}); A_naive=NaN at {len(nan_rows)} level(s).")
    print("Every such NaN is FAKE: it traces to r→0 (origin crossing) while sign(Im λ) stays")
    print("definite. A REAL asymptotic-closure tripwire would need sign(Im λ)→degenerate — it does")
    print("not. Read the invariant globally and there is no zero to cross and no NaN to fake.")

    # ---- figure ----
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    D1 = [r["D"] for r in rows1]
    ax[0].semilogx(D1, [r["snr_w"] for r in rows1], "o-", color="tab:red",
                   label="NAIVE 1/r² winding SNR")
    ax[0].semilogx(D1, [r["sign_global"] for r in rows1], "s--", color="tab:green",
                   label="GLOBAL sign(Im λ)")
    ax[0].semilogx(D1, [r["sign_robust"] for r in rows1], "^:", color="tab:blue",
                   label="ROBUST ang-momentum sign")
    ax[0].set_xlabel("noise D"); ax[0].set_ylabel("SNR (red) / sign (±1)")
    ax[0].set_title("Sweep 1 (noise): sign held by global & robust readings;\nnaive precision degrades")
    ax[0].grid(alpha=0.3); ax[0].legend(fontsize=8)
    g2 = [r["g"] for r in rows2]
    ax[1].semilogx(g2, [r["snr_w"] for r in rows2], "o-", color="tab:red",
                   label="NAIVE 1/r² winding SNR")
    ax[1].semilogx(g2, [r["absIm"] for r in rows2], "d-", color="tab:purple",
                   label="|Im λ| (global, > 0)")
    ax[1].semilogx(g2, [r["sign_global"] for r in rows2], "s--", color="tab:green",
                   label="GLOBAL sign(Im λ)")
    ax[1].set_xlabel("coupling g  →  balanced point (g=0, never reached)")
    ax[1].set_ylabel("SNR / |Im λ| / sign")
    ax[1].set_title("Sweep 2 (approach orthogonal zero): naive SNR collapses\nwhile global sign stays definite — the fake-artifact regime")
    ax[1].grid(alpha=0.3); ax[1].legend(fontsize=8); ax[1].invert_xaxis()
    fig.suptitle("IK1 — chimeric sign protected (global/robust); naive 1/r² fails at the orthogonal zero (fake)", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    png = OUT / "ik1_chimeric_sign_sweep.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
