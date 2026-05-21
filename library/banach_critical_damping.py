"""Banach-substrate damping check: does the s-regime sit at critical DAMPING
(zeta=1, the framework's §Stability claim), or is it the critical-SLOWING /
overdamped limit? Physics-as-oracle, MPA's own closed form as the weapon.

The Banach substrate (mpa-conform/docs/banach-substrate-reference.md) is the
canonical reference instance of the cdv1 kernel: every parameter at its default
(gamma_s = L = rho_sat = tau_c = 1, D_noise = 0, beta_mem = 1). Deterministic,
closed-form -> NO estimator noise (unlike the sk swing-and-miss). So MPA's own
§Stability relaxation-oscillation formulas, evaluated here, referee MPA's own
§Stability damping table.

cdv1 §Stability (closed form):
    omega_RO = sqrt(2 gamma_s L (e^chit - 1)),   gamma_RO = gamma_s/2 (constant),
    Q = omega_RO / (2 gamma_RO),                 zeta = gamma_RO / omega_RO = 1/(2Q).
§Stability table claims:   c | zeta<1 underdamped ;  s | zeta->1 CRITICAL ;  r | zeta>1 overdamped.

PHYSICS ORACLE (textbook damped oscillator): critical DAMPING (zeta=1) is the
FASTEST non-oscillatory return; critical SLOWING (omega->0 at a gap-closing) is
the SLOWEST (relaxation time diverges). They are opposite ends and must not be
fused.

Pre-registered findings to check:
  F1  zeta=1 (critical damping) sits at chit* = ln(1 + gamma_s/(8L)) > 0 -- the
      c/s boundary, NOT the s-regime body.
  F2  s-regime body (chit->0+) has zeta->infinity (overdamped) and settling
      time -> infinity (critical SLOWING). So labeling s "zeta->1 critical" fuses
      critical slowing (slow) with critical damping (fast) -- physically opposite.
  F3  on Banach (beta_mem=1) the s settling is slow-EXPONENTIAL, not algebraic;
      "algebraic settling" requires beta_mem<1 (memory), which is OFF Banach. So
      the table's "s = algebraic settling" is substrate-conditional, not universal.

Run: python H:/mpa-central/library/banach_critical_damping.py
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path("H:/mpa-central/library/output/diagnostics")
OUT.mkdir(parents=True, exist_ok=True)

GAMMA_S, L = 1.0, 1.0          # Banach canonical defaults


def ro(chit):
    """Relaxation-oscillation observables at chit (Banach canonical). Returns
    omega_RO, zeta, Q, slow relaxation rate, settling time. For chit<=0 the
    above-threshold RO does not exist (sub-threshold r: pure decay)."""
    gamma_RO = GAMMA_S / 2.0
    e = np.exp(chit) - 1.0
    if e <= 0:
        return 0.0, np.inf, 0.0, np.nan, np.nan        # r-regime: no RO
    w = np.sqrt(2.0 * GAMMA_S * L * e)
    zeta = gamma_RO / w
    Q = w / (2.0 * gamma_RO)
    # 2D RO eigenvalues: -gamma_RO +/- sqrt(gamma_RO^2 - w^2)
    disc = gamma_RO**2 - w**2
    if disc >= 0:                                       # overdamped: slow real root
        slow_rate = gamma_RO - np.sqrt(disc)            # |slow root|, ->0 as w->0
    else:                                               # underdamped: envelope rate gamma_RO
        slow_rate = gamma_RO
    settle = 1.0 / slow_rate if slow_rate > 1e-12 else np.inf
    return w, zeta, Q, slow_rate, settle


def main():
    chit_star = np.log(1.0 + GAMMA_S / (8.0 * L))       # zeta=1 prediction
    print(f"Banach canonical gamma_s=L=1.  gamma_RO=gamma_s/2=0.5 (constant).")
    print(f"Predicted critical-damping point: chit* = ln(1+gamma_s/8L) = {chit_star:.4f}\n")
    print(f"{'chit':>6} {'regime':>8} | {'omega_RO':>9} {'zeta':>9} {'Q':>7} | {'settle time':>11} | reading")
    grid = [1.50, 0.80, 0.40, chit_star, 0.05, 0.01, 0.001, -0.20]
    rows = []
    for chit in grid:
        w, zeta, Q, slow, settle = ro(chit)
        if chit <= 0:
            regime, reading = "r", "sub-threshold: pure decay (no RO)"
        elif zeta < 0.999:
            regime, reading = "c", "underdamped (rings)"
        elif abs(zeta - 1.0) < 0.05:
            regime, reading = "c/s edge", "** CRITICAL DAMPING (zeta=1, fastest) **"
        else:
            regime, reading = "s", "OVERDAMPED + slowing"
        rows.append((chit, w, zeta, Q, settle, regime))
        zs = f"{zeta:>9.3f}" if np.isfinite(zeta) else f"{'inf':>9}"
        ss = f"{settle:>11.2f}" if np.isfinite(settle) else f"{'inf':>11}"
        print(f"{chit:>6.3f} {regime:>8} | {w:>9.4f} {zs} {Q:>7.3f} | {ss} | {reading}")

    print("\n================ BANACH DAMPING VERDICT ================")
    print(f"F1: critical damping (zeta=1, Q=0.5, FASTEST return) is at chit*={chit_star:.3f} > 0 --")
    print("    the c/s BOUNDARY, inside the c-band. NOT the s-regime body.")
    print("F2: the s-regime body (chit->0+) is zeta->INFINITY (heavily OVERDAMPED) with settling")
    print("    time -> INFINITY (critical SLOWING). The §Stability table's 's | zeta->1 critical'")
    print("    fuses critical SLOWING (s; slowest; aging) with critical DAMPING (zeta=1; fastest) --")
    print("    physically OPPOSITE ends. Same single-name-for-two-objects pattern as spin-glass.")
    print("F3: on Banach (beta_mem=1) the slow s-settling is EXPONENTIAL (slow root e^{-slow_rate t}),")
    print("    not algebraic. Power-law/CK 'algebraic settling' needs beta_mem<1 (memory) = OFF Banach.")
    print("    So 's = algebraic settling' is substrate-conditional, not a universal s-property.")
    print("Refinement (harder-to-vary): s is the critical-SLOWING / overdamped limit (zeta->inf,")
    print("    omega_RO->0); critical DAMPING (zeta=1) is the c/s edge; algebraic aging is the")
    print("    beta_mem<1 memory-substrate refinement, not the Markovian-Banach default.")

    # ---- figure: zeta and settling-time vs chit, marking the conflation ----
    # fine, log-spaced sampling toward chit->0 so the divergence is fully shown
    # (the interesting blow-up lives in the last decade before threshold).
    cc_pos = np.geomspace(2e-4, 1.6, 700)          # positive chit, dense near 0
    cc_neg = np.linspace(-0.3, -1e-3, 60)          # sub-threshold r
    zp = np.array([ro(c)[1] for c in cc_pos]); sp = np.array([ro(c)[4] for c in cc_pos])

    fig, ax = plt.subplots(1, 2, figsize=(14, 5.5))
    ax[0].plot(cc_pos, zp, color="tab:red", lw=2, label="zeta (damping ratio)")
    ax[0].axhline(1.0, color="k", ls="--", lw=1, label="zeta=1 (critical DAMPING, fastest)")
    ax[0].axvline(chit_star, color="tab:green", lw=1.2, label=f"chit*={chit_star:.3f} (zeta=1)")
    ax[0].axvspan(-0.3, 0.0, color="gray", alpha=0.12, label="r (sub-threshold)")
    ax[0].set_yscale("log")                         # zeta -> inf at s; log shows the full climb
    ax[0].annotate("s-regime body:\nzeta -> inf (OVERDAMPED)\n= critical SLOWING", xy=(2.5e-3, 12),
                   fontsize=8, color="tab:red")
    ax[0].annotate("table says 's = zeta->1 critical'\n(the s body is overdamped, not zeta=1)",
                   xy=(0.02, 1.25), fontsize=8, color="tab:purple")
    ax[0].set_xlim(-0.3, 1.6); ax[0].set_ylim(0.1, 60)
    ax[0].set_xlabel("chit (c >> 0  ->  s ~ 0  ->  r < 0)"); ax[0].set_ylabel("zeta (log)")
    ax[0].set_title("Damping ratio along c->s->r (Banach canonical)")
    ax[0].legend(fontsize=8, loc="upper right"); ax[0].grid(alpha=0.3, which="both")

    ax[1].semilogy(cc_pos, sp, color="tab:blue", lw=2, label="RO settling time")
    ax[1].axhline(2.0, color="gray", ls="--", lw=1, label="fast floor = 1/gamma_RO = 2")
    ax[1].axvline(chit_star, color="tab:green", lw=1.2, label=f"critical damping (FASTEST) chit*={chit_star:.3f}")
    ax[1].axvline(0.0, color="k", ls=":", lw=1, label="threshold chit=0")
    ax[1].annotate("critical SLOWING:\nsettling -> inf as chit->0\n(THIS is the s-regime)",
                   xy=(3e-4, sp.max() * 0.25), fontsize=8, color="tab:blue")
    ax[1].set_xlim(-0.3, 1.6); ax[1].set_ylim(1.5, sp.max() * 1.5)
    ax[1].set_xlabel("chit"); ax[1].set_ylabel("settling time (log)")
    ax[1].set_title("Critical DAMPING (fast, chit*) vs critical SLOWING (slow, chit->0) -- opposite ends")
    ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3, which="both")
    fig.suptitle("Banach substrate: the s-regime is critical SLOWING (overdamped), NOT critical DAMPING (zeta=1)",
                 fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    png = OUT / "banach_critical_damping.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
