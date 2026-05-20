"""Validate the avalanche-measurement apparatus on an EXACT τ=3/2 source.

The sandpile control gave τ≈1.40, not 1.50 — ambiguous between "measurement
bug" and "model not cleanly critical / wrong size observable." This pins it:
fit the apparatus against critical Galton-Watson branching, whose total-progeny
distribution is P(S)~S^{-3/2} EXACTLY (mean-field, theorem). This is cdv1's own
avalanche model (μ=e^chit→1 critical branching) and the same universality class
as the ABBM mean-field depinning reduction (Brownian first-passage → 3/2).

If the fit recovers 3/2 here → apparatus validated; the sandpile's 1.40 is a
property of the sandpile (off-critical σ≈1.1 and/or topplings-vs-area), not the
measurement. If it does NOT → the estimator itself is the problem.
"""
from __future__ import annotations

import sys, time
from pathlib import Path
import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

OUT = Path("H:/mpa-central/library/output/diagnostics/avalanche_apparatus_check.png")


def gw_total_progeny(n_trees, s_cap=2_000_000, seed=0):
    """Critical Galton-Watson (Poisson(1) offspring). Returns total-progeny sizes.
    Trees exceeding s_cap are censored (they are the finite-size cutoff)."""
    rng = np.random.default_rng(seed)
    sizes = np.empty(n_trees, dtype=np.int64)
    t0 = time.time()
    for i in range(n_trees):
        alive = 1
        size = 0
        while alive > 0 and size < s_cap:
            size += alive
            alive = int(rng.poisson(1.0, alive).sum()) if alive < 100000 \
                else int(rng.poisson(float(alive)))  # CLT shortcut for big gens
        sizes[i] = size
        if (i + 1) % 500000 == 0:
            print(f"  {i+1}/{n_trees} trees ({time.time()-t0:.1f}s)", flush=True)
    return sizes


def fit_tau_logbin(sizes, s_min=2, s_max_frac=0.1, nbins=26):
    s_max = sizes.max()
    edges = np.geomspace(1, s_max + 1, nbins + 1)
    counts, _ = np.histogram(sizes, bins=edges)
    widths = np.diff(edges)
    centers = np.sqrt(edges[:-1] * edges[1:])
    P = counts / widths / counts.sum()
    fit_hi = s_max_frac * s_max
    m = (centers >= s_min) & (centers <= fit_hi) & (P > 0)
    slope, icpt = np.polyfit(np.log10(centers[m]), np.log10(P[m]), 1)
    return centers, P, -slope, (s_min, fit_hi), (slope, icpt)


def mle_tau(sizes, s_min=2):
    s = sizes[sizes >= s_min].astype(float)
    n = s.size
    tau = 1.0 + n / np.sum(np.log(s / (s_min - 0.5)))
    return tau, (tau - 1.0) / np.sqrt(n), n


def main():
    print("[apparatus-check] sampling critical Galton-Watson trees...", flush=True)
    sizes = gw_total_progeny(2_000_000)
    print(f"[apparatus-check] {sizes.size} trees; size range [{sizes.min()}, {sizes.max()}]",
          flush=True)

    centers, P, tau_fit, (s_lo, s_hi), (slope, icpt) = fit_tau_logbin(sizes)
    tau_mle, err, n = mle_tau(sizes)
    print("\n===== APPARATUS CHECK — exact τ=3/2 source =====")
    print(f"  log-bin slope τ (s in [{s_lo:.0f},{s_hi:.0f}]) = {tau_fit:.3f}")
    print(f"  MLE τ (s>=2, n={n})                          = {tau_mle:.3f} ± {err:.3f}")
    verdict = "VALIDATED (recovers 3/2)" if abs(tau_mle - 1.5) < max(0.02, 4*err) \
        else "APPARATUS BIASED — does not recover known 3/2"
    print(f"  → {verdict}")

    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.loglog(centers, P, "o", color="black", ms=5, label="measured P(S)")
    sref = np.geomspace(s_lo, s_hi, 50)
    ax.loglog(sref, 10**icpt * sref**-1.5, "C3-", lw=2, label="τ = 3/2 (exact)")
    ax.loglog(sref, 10**icpt * sref**slope, "C0--", lw=1.5, label=f"fit τ = {tau_fit:.3f}")
    ax.set_xlabel("avalanche size S (total progeny)"); ax.set_ylabel("P(S)")
    ax.set_title(f"APPARATUS CHECK — critical Galton-Watson (exact 3/2)\n"
                 f"MLE τ = {tau_mle:.3f} ± {err:.3f}  → {verdict}")
    ax.legend(); ax.grid(True, which="both", alpha=0.2)
    fig.tight_layout(); OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=140); plt.close(fig)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
