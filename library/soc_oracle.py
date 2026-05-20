"""SOC oracle — POSITIVE CONTROL for the avalanche apparatus (cdv1 §Pattern formation).

cdv1 predicts that a feedback-coupled NESS substrate self-organizes to the
chit=0 critical limit and there shows power-law fraying avalanches with
mean-field exponent tau ~ 3/2 (Galton-Watson critical branching, mu=e^chit->1).
Receipts §18 falsifier: "a feedback-coupled NESS substrate with clearly
separated timescales exhibiting a robust stable avalanche exponent tau != 3/2
... falsifies SOC universality at the framework level."

This is the POSITIVE CONTROL, not the test: a mean-field random-neighbor
sandpile is *known* to be SOC with tau=3/2, so building it and recovering 3/2
validates (a) the avalanche-measurement apparatus and (b) the framework's
mean-field prediction on a known-answer system. The real MPA test is later:
point the validated apparatus at a real substrate and ask whether it lands in
the SOC class.

cdv1 mapping (faithful, not decorative):
  toppling (h_i >= z_c -> release)  = a holding crossing chit=0 and dumping
                                      stress to coupled holdings (heat-tax tower)
  slow drive (one grain at a time)  = load accumulation
  dissipation (grain lost, prob eps)= loss to bath L; sets the finite-size cutoff
  branching ratio sigma -> 1        = mu = e^chit -> 1, i.e. self-organization
                                      to the chit=0 critical limit
  avalanche size s                  = number of fraying events in one cascade
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

OUT = Path("H:/mpa-central/library/output/diagnostics/soc_oracle_avalanche.png")


def run_sandpile(N=10000, z_c=2, eps=1e-3, warmup=20000, n_record=200000, seed=0):
    """Mean-field (random-neighbor) abelian sandpile, synchronous toppling.

    Returns (sizes, branching_ratios, mean_height). `sizes[k]` = total topplings
    in avalanche k; `branching_ratios[k]` = sigma for that avalanche (mean
    generation-to-generation toppling ratio); mean_height = stationary <h>.
    """
    rng = np.random.default_rng(seed)
    h = np.zeros(N, dtype=np.int64)
    sizes = []
    branch = []

    def one_avalanche():
        s = 0
        gens = []  # topplings per generation
        while True:
            unstable = np.flatnonzero(h >= z_c)
            ng = unstable.size
            if ng == 0:
                break
            gens.append(ng)
            s += ng
            h[unstable] -= z_c
            n_grains = ng * z_c
            keep = rng.random(n_grains) >= eps          # survive dissipation
            tgt = rng.integers(0, N, n_grains)[keep]
            np.add.at(h, tgt, 1)
        # branching ratio sigma: mean of gens[g+1]/gens[g] over g with gens[g]>0
        if len(gens) >= 2:
            g = np.asarray(gens, float)
            ratios = g[1:] / g[:-1]
            sigma = float(np.mean(ratios))
        else:
            sigma = 0.0
        return s, sigma

    total = warmup + n_record
    t0 = time.time()
    for k in range(total):
        site = int(rng.integers(0, N))
        h[site] += 1
        s, sigma = one_avalanche()
        if k >= warmup and s > 0:
            sizes.append(s)
            branch.append(sigma)
        if (k + 1) % 50000 == 0:
            print(f"  drive {k+1}/{total}  <h>={h.mean():.3f}  "
                  f"avalanches_recorded={len(sizes)}  ({time.time()-t0:.1f}s)",
                  flush=True)
    return np.asarray(sizes), np.asarray(branch), float(h.mean())


def fit_tau_logbin(sizes, s_min=3, s_max_frac=0.2, nbins=24):
    """Log-binned P(s) and a log-log slope fit over [s_min, s_max_frac*max]."""
    s_max = sizes.max()
    edges = np.geomspace(1, s_max + 1, nbins + 1)
    counts, _ = np.histogram(sizes, bins=edges)
    widths = np.diff(edges)
    centers = np.sqrt(edges[:-1] * edges[1:])
    P = counts / widths / counts.sum()
    fit_hi = s_max_frac * s_max
    m = (centers >= s_min) & (centers <= fit_hi) & (P > 0)
    slope, intercept = np.polyfit(np.log10(centers[m]), np.log10(P[m]), 1)
    return centers, P, -slope, (s_min, fit_hi), (slope, intercept)


def mle_tau(sizes, s_min=3):
    s = sizes[sizes >= s_min].astype(float)
    n = s.size
    tau = 1.0 + n / np.sum(np.log(s / (s_min - 0.5)))   # discrete CSN approx
    err = (tau - 1.0) / np.sqrt(n)
    return tau, err, n


def main():
    print("[soc_oracle] running mean-field sandpile (positive control)...", flush=True)
    sizes, branch, mean_h = run_sandpile()
    print(f"[soc_oracle] {sizes.size} avalanches; <h>={mean_h:.3f}; "
          f"size range [{sizes.min()}, {sizes.max()}]", flush=True)

    sigma_mean = float(np.mean(branch[branch > 0]))
    chit_implied = float(np.log(sigma_mean)) if sigma_mean > 0 else float("nan")
    centers, P, tau_fit, (s_lo, s_hi), (slope, icpt) = fit_tau_logbin(sizes)
    tau_mle, tau_err, n_mle = mle_tau(sizes)

    print("\n===== SOC ORACLE — verdict =====")
    print(f"  self-organized branching ratio sigma = {sigma_mean:.4f}  "
          f"(=> mu, chit = ln(sigma) = {chit_implied:+.4f})")
    print(f"  predicted (cdv1 §Pattern formation): sigma->1 (chit->0), tau = 3/2")
    print(f"  measured tau (log-bin slope, s in [{s_lo:.0f},{s_hi:.0f}]) = {tau_fit:.3f}")
    print(f"  measured tau (MLE, s>=3, n={n_mle})                 = {tau_mle:.3f} +/- {tau_err:.3f}")
    print(f"  consistent with 3/2? {'YES' if abs(tau_mle-1.5) < 3*tau_err+0.1 else 'NO -- look hard'}")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.loglog(centers, P, "o", color="black", ms=5, label="measured P(s)")
    sref = np.geomspace(s_lo, s_hi, 50)
    Pref = 10 ** icpt * sref ** (-1.5)
    ax.loglog(sref, Pref, "C3-", lw=2, label="τ = 3/2 (cdv1 mean-field prediction)")
    Pfit = 10 ** icpt * sref ** slope
    ax.loglog(sref, Pfit, "C0--", lw=1.5, label=f"fit τ = {tau_fit:.2f}")
    ax.axvspan(s_lo, s_hi, color="gray", alpha=0.08, label="fit range")
    ax.set_xlabel("avalanche size s (fraying events per cascade)")
    ax.set_ylabel("P(s)")
    ax.set_title(f"SOC ORACLE (positive control) — mean-field fraying cascade\n"
                 f"σ={sigma_mean:.3f} (chit={chit_implied:+.3f}); "
                 f"τ_MLE={tau_mle:.3f}±{tau_err:.3f}  vs  cdv1 prediction 3/2")
    ax.legend(); ax.grid(True, which="both", alpha=0.2)
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=140); plt.close(fig)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
