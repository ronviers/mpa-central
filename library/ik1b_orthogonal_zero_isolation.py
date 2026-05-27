r"""IK1b — isolating the orthogonal-zero coordinate artifact from genuine signal.

IK1 showed the chimeric sign is protected (global + robust) and that the naive 1/r^2
winding degrades near the balanced point — but that degradation conflated genuine
signal-weakening (omega = sqrt(3) g -> 0) with the 1/r^2 coordinate noise. This
isolates the PURE coordinate artifact at FIXED wiring (fixed signal), so nothing here
is signal-weakening:

  (1) naive-vs-robust SNR GAP at fixed g: both estimators see the same systematic
      rotation; only the naive one carries 1/r^2. The gap IS the coordinate penalty.
  (2) FLUCTUATION-BUDGET PARTITION: fraction of the sum-of-squared per-step
      increments contributed by near-origin steps (r<R_EPS) vs far, per estimator.
      The naive budget is dominated by the rare near-origin steps; the robust budget
      is not. That is the orthogonal zero, isolated.

Literal NaN: area = (x dy - y dx) ~ r*du near the origin, so naive = area/r^2 ~ du/r
-> large but FINITE unless r = 0 exactly. The continuous dynamics never attain r = 0
(origin polar for the planar diffusion; Ito-McKean skew-product). A literal NaN needs
the discrete grid to land exactly on r=0 -- a computer artifact, fake by construction.

Established math this re-instantiates (import, not discovery): Kolmogorov (1936,
reversibility/cycle criterion), Spitzer (1958, planar-BM winding -> Cauchy,
near-origin domination), Ito-McKean (1965, skew-product; angular clock int dt/r^2
diverges = this exact 1/r^2), Levy (stochastic area = the robust reading; rough-path
foundation, Lyons 1998), Schnakenberg (1976) / Gallavotti-Cohen (1995) drive-robust
affinity, Kato (1966) / Heiss / Berry exceptional points.

Run: python H:/mpa-central/library/ik1b_orthogonal_zero_isolation.py
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
from banach_frustrated import P, exact

OUT = Path("H:/mpa-central/library/output/diagnostics")
OUT.mkdir(parents=True, exist_ok=True)

DT, T_EQ, T_OBS, N_REAL, SEED = 0.01, 1000, 3000, 4000, 20260526
R_EPS, GUARD = 0.10, 1e-12


def simulate_partition(M, D, rng):
    sd = np.sqrt(2.0 * D * DT)
    z = rng.standard_normal((N_REAL, 3)) * np.sqrt(D)
    for _ in range(T_EQ):
        z = z + (z @ M.T) * DT + rng.standard_normal((N_REAL, 3)) * sd
    u = z @ P.T
    ang_mom = np.zeros(N_REAL)        # robust: sum area  (Levy area rate)
    wind = np.zeros(N_REAL)           # naive:  sum area/r^2  (angular clock)
    sq_rob_near = sq_rob_far = sq_nai_near = sq_nai_far = 0.0
    near_steps = total = 0
    min_r2, nf = np.inf, 0
    for _ in range(T_OBS):
        z = z + (z @ M.T) * DT + rng.standard_normal((N_REAL, 3)) * sd
        un = z @ P.T
        du = un - u
        mid = 0.5 * (u + un)
        area = mid[:, 0] * du[:, 1] - mid[:, 1] * du[:, 0]
        r2 = (mid * mid).sum(1)
        naive = area / (r2 + GUARD)
        ang_mom += area
        wind += naive
        near = r2 < R_EPS * R_EPS
        sq_rob_near += float((area[near] ** 2).sum())
        sq_rob_far += float((area[~near] ** 2).sum())
        sq_nai_near += float((naive[near] ** 2).sum())
        sq_nai_far += float((naive[~near] ** 2).sum())
        near_steps += int(near.sum()); total += N_REAL
        min_r2 = min(min_r2, float(r2.min()))
        with np.errstate(divide="ignore", invalid="ignore"):
            raw = area / r2
        nf += int((~np.isfinite(raw)).sum())
        u = un
    return dict(ang_mom=ang_mom, wind=wind,
                rob_near=sq_rob_near / (sq_rob_near + sq_rob_far),
                nai_near=sq_nai_near / (sq_nai_near + sq_nai_far),
                step_near=near_steps / total, min_r=float(np.sqrt(min_r2)), nf=nf)


def measure(gamma, g, D, rng):
    M, sigma, ev, omega, gam_eff = exact(gamma, g, D)
    s = simulate_partition(M, D, rng)
    rm, rv = float(s["ang_mom"].mean()), float(s["ang_mom"].var(ddof=1))
    nm, nv = float(s["wind"].mean()), float(s["wind"].var(ddof=1))
    rob_snr = rm * rm / rv if rv > 0 else float("inf")
    nai_snr = nm * nm / nv if nv > 0 else float("inf")
    return dict(D=D, g=g, rob_snr=rob_snr, nai_snr=nai_snr,
                gap=rob_snr / nai_snr if nai_snr > 0 else float("inf"),
                nai_near=s["nai_near"], rob_near=s["rob_near"],
                step_near=s["step_near"], min_r=s["min_r"], nf=s["nf"])


def main():
    rng = np.random.default_rng(SEED)
    gamma, g = 1.0, 0.6     # FIXED wiring -> FIXED signal (omega = sqrt(3)*0.6); no signal-weakening here
    print("IK1b — isolating the orthogonal-zero coordinate artifact (fixed signal, fixed g=0.6)")
    print("Both estimators see the same rotation; only NAIVE carries 1/r^2.\n")
    hdr = (f"{'D':>7} | {'ROBUST SNR':>11} {'NAIVE SNR':>10} {'gap(R/N)':>9} | "
           f"{'step<Reps%':>10} {'NAIVE fluc<Reps%':>16} {'ROBUST fluc<Reps%':>17} | {'min_r':>7} {'raw∞':>5}")
    print(hdr); print("-" * len(hdr))
    rows = [measure(gamma, g, D, rng) for D in (0.02, 0.05, 0.2, 0.8, 3.2)]
    for r in rows:
        print(f"{r['D']:>7.3f} | {r['rob_snr']:>11.2f} {r['nai_snr']:>10.2f} {r['gap']:>9.1f} | "
              f"{100*r['step_near']:>9.3f}% {100*r['nai_near']:>15.2f}% {100*r['rob_near']:>16.3f}% | "
              f"{r['min_r']:>7.4f} {r['nf']:>5d}")

    nf_tot = sum(r["nf"] for r in rows)
    print("\n================ ISOLATION VERDICT ================")
    print(f"(1) SNR GAP at fixed signal: robust/naive = {min(r['gap'] for r in rows):.0f}–"
          f"{max(r['gap'] for r in rows):.0f}×. Same rotation in both; the gap is the PURE")
    print("    coordinate penalty of the 1/r^2 angular clock — no signal-weakening (g fixed).")
    print(f"(2) FLUCTUATION BUDGET: near-origin steps are {100*min(r['step_near'] for r in rows):.2f}–"
          f"{100*max(r['step_near'] for r in rows):.2f}% of all steps, but carry "
          f"{100*min(r['nai_near'] for r in rows):.0f}–{100*max(r['nai_near'] for r in rows):.0f}% of the")
    print(f"    NAIVE fluctuation budget vs only {100*max(r['rob_near'] for r in rows):.2f}% of the ROBUST")
    print("    budget. The orthogonal zero IS the naive estimator's noise; the robust (Levy-area)")
    print("    reading is immune. Artifact isolated, clean of signal-weakening.")
    print(f"(3) LITERAL NaN: unguarded 1/r^2 non-finite {nf_tot} times across all runs. area~r*du so")
    print("    naive~du/r is finite unless r=0 exactly — never attained by the continuous dynamics")
    print("    (origin polar; Ito-McKean). A NaN here would require the grid to land on r=0 exactly:")
    print("    a discretization artifact, FAKE by construction. The real artifact is variance, not NaN.")
    print("\nThis re-instantiates Spitzer(1958)/Ito-McKean(1965)/Levy: read the global winding (Levy")
    print("area), not the local angular clock (1/r^2). MPA imports it; the reading is the contribution.")

    # ---- figure ----
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    Dv = [r["D"] for r in rows]
    ax[0].loglog(Dv, [r["rob_snr"] for r in rows], "^-", color="tab:blue", label="ROBUST (Lévy area) SNR")
    ax[0].loglog(Dv, [r["nai_snr"] for r in rows], "o-", color="tab:red", label="NAIVE (1/r²) SNR")
    ax[0].set_xlabel("noise D (fixed wiring g=0.6 → fixed signal)")
    ax[0].set_ylabel("SNR"); ax[0].grid(alpha=0.3, which="both"); ax[0].legend(fontsize=9)
    ax[0].set_title("(1) SNR gap at fixed signal = pure coordinate penalty\n(robust ≫ naive; same rotation in both)")
    ax[1].semilogx(Dv, [100 * r["nai_near"] for r in rows], "o-", color="tab:red",
                   label="NAIVE fluctuation from r<Rε")
    ax[1].semilogx(Dv, [100 * r["rob_near"] for r in rows], "^-", color="tab:blue",
                   label="ROBUST fluctuation from r<Rε")
    ax[1].semilogx(Dv, [100 * r["step_near"] for r in rows], "s:", color="gray",
                   label="share of steps with r<Rε")
    ax[1].set_xlabel("noise D"); ax[1].set_ylabel("% of fluctuation budget / steps")
    ax[1].grid(alpha=0.3, which="both"); ax[1].legend(fontsize=9)
    ax[1].set_title("(2) the orthogonal zero, isolated: few near-origin steps\ncarry the NAIVE noise, ~none of the ROBUST")
    fig.suptitle("IK1b — orthogonal-zero coordinate artifact isolated from signal (Spitzer/Itô–McKean/Lévy)", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    png = OUT / "ik1b_orthogonal_zero_isolation.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
