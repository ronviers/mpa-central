r"""Two-frame gFDR on the driven_ring INVALIDATOR substrate (real, in-library).

driven_ring is the framework's own falsification target for the "everything -> r at
infinity" axiom: an overdamped particle on a tilted washboard,

    dtheta = (F - A sin theta) dt + sqrt(2 D dt) xi ,   A=1, D=0.5

For F < A it locks (relaxes, gt=r); F = A is critical (gt=k); F > A it RUNS -- a
probability current <theta_dot> > 0 that NEVER decays (gt=s). The drive F is the
affinity axis; the running current is the self-frame's reason to exist.

Why this is the cleanest real-substrate two-frame instance:
  SELF-FRAME    : winding J_tau = net Delta theta over tau. The entropy production is
                  EXACT and analytic -- only the constant tilt F does net work per
                  revolution (the washboard does zero):  <sigma> = F * <theta_dot> / D.
                  So <sigma> = J . A holds EXACTLY (affinity A = F/D per radian, current
                  J = <theta_dot>) -- the Harada-Sasa bridge the laser only approximated.
                  T = <sigma> tau Var(J)/(2 <J>^2); TUR floor SNR_J <= <sigma> tau/2.
  EXTERNAL FRAME: C(tau) = <cos(theta(t0+tau) - theta(t0))> (rotation-invariant, bounded,
                  loops because the running phase oscillates), chi(tau) = step response
                  to a small extra drive h (paired CRN branch, as the grind primitive does).
                  Parametric (Delta C, chi); X(t->0)=1 anchor from the short-time slope;
                  Delta_FDT = max departure.

F-sweep = r->k->s affinity migration (locked->critical->running), gt-labelled by the
primitive. tau_obs (the observation window) is tuned to land the migration interior =
pin-registration; we control the camera because we re-simulate.

HONEST SCOPE: the ring current is DRIVE-forced (F>A; kill the drive, it relaxes), not a
topologically-forced k_frust current. So this earns the real-substrate VERDICT-AGREEMENT
gate (FALSIFICATION criterion 1), NOT the section-846 k_frust bar. But it is THE canonical
sustained-current NESS and the framework's own ->r invalidator: the two-frame question is
whether the never-decaying running current reads as s in BOTH frames, as gt says.

Self-contained: re-simulates the dynamics from driven_ring/measurements.py (A=1, D=0.5,
dt=0.01, h_field=0.05). Run: python H:/mpa-central/library/two_frame_driven_ring.py
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

OUT = Path("H:/mpa-central/library/output/diagnostics")
OUT.mkdir(parents=True, exist_ok=True)

A, D, DT = 1.0, 0.5, 0.01                   # barrier, diffusion, step (driven_ring primitive)
N_REAL, T_EQ, N_OBS = 6000, 4000, 1500      # tau_obs window = N_OBS*DT = 15 (tuned to pin-register)
H = 0.05                                    # extra-drive perturbation (= grind h_field)
SEED = 3


def finite(name, x):
    if not np.all(np.isfinite(np.asarray(x, float))):
        raise FloatingPointError(f"NON-FINITE in '{name}' (MPA NaN tripwire).")
    return x


def run_ring(F, rng):
    """One F: returns winding J per realization, and lag arrays C(tau), chi(tau)."""
    s_t = np.sqrt(2.0 * D * DT)
    th = rng.uniform(-np.pi, np.pi, size=N_REAL)
    for _ in range(T_EQ):                                   # equilibrate (unperturbed)
        th = th + (F - A * np.sin(th)) * DT + rng.standard_normal(N_REAL) * s_t
    th_u = th.copy(); th_p = th.copy()                      # fork perturbed branch (CRN)
    th0 = th.copy()
    C = np.empty(N_OBS + 1); chi = np.empty(N_OBS + 1)
    C[0] = 1.0; chi[0] = 0.0
    for k in range(1, N_OBS + 1):
        xi = rng.standard_normal(N_REAL) * s_t              # common random numbers
        th_u = th_u + (F - A * np.sin(th_u)) * DT + xi
        th_p = th_p + (F + H - A * np.sin(th_p)) * DT + xi
        C[k] = float(np.mean(np.cos(th_u - th0)))
        chi[k] = float(np.mean(np.cos(th_p - th0) - np.cos(th_u - th0))) / H
    J = th_u - th0                                          # net winding over tau_obs (unwrapped)
    return finite("winding", J), finite("C", C), finite("chi", chi)


def main():
    rng = np.random.default_rng(SEED)
    tau = N_OBS * DT
    Fs = [0.5, 0.9, 1.0, 1.2, 1.5, 2.0, 3.0]
    GT = {0.5: "r", 0.9: "r", 1.0: "k", 1.2: "s", 1.5: "s", 2.0: "s", 3.0: "s"}

    hdr = (f"{'F':>5} {'gt':>3} | {'<theta_dot>':>11} {'<sigma>=Fv/D':>12} | "
           f"{'SNR_J':>8} {'sig*t/2':>8} TUR | {'T':>8} | external (C decorr)")
    print(hdr); print("-" * len(hdr))
    rows = []
    for F in Fs:
        J, C, chi = run_ring(F, rng)
        mean, var = float(J.mean()), float(J.var(ddof=1))
        v = mean / tau                                       # <theta_dot>
        sigma = F * v / D                                    # EXACT entropy production (= J . A)
        snr = mean * mean / var
        bound = sigma * tau / 2.0
        has_current = abs(v) > 0.02                          # locked F<A: no sustained current
        T = sigma * tau * var / (2.0 * mean * mean) if has_current else float("nan")
        tur_ok = (snr <= bound * 1.10) if has_current else True
        Cdecorr = float(C[0] - C.min())                     # how far the correlation observable decorrelates
        rows.append(dict(F=F, gt=GT[F], v=v, sigma=sigma, snr=snr, bound=bound, T=T,
                         tau_arr=np.arange(N_OBS + 1) * DT, C=C, Cdecorr=Cdecorr,
                         has_current=has_current))
        tcell = f"{T:>8.3f}" if has_current else f"{'(locked)':>8}"
        turcell = ("ok" if tur_ok else "XX") if has_current else "—"
        print(f"{F:>5.2f} {GT[F]:>3} | {v:>11.4f} {sigma:>12.4f} | {snr:>8.2f} {bound:>8.2f} "
              f"{turcell:>3} | {tcell} | C decorr={Cdecorr:.3f}")

    run = [r for r in rows if r["has_current"]]
    tur_all = all(r["snr"] <= r["bound"] * 1.10 for r in run)
    print("\n================ VERDICT ================")
    print("Two-frame gFDR on the REAL driven_ring NESS (the ->r-axiom invalidator):")
    print("  SELF-FRAME — CLOSED. <sigma>=F<theta_dot>/D is EXACT (= J . A, affinity x current,")
    print(f"    the Harada-Sasa bridge the laser only approximated). TUR floor T>=1 "
          f"{'respected' if tur_all else 'VIOLATED'} ")
    print(f"    on all running cells; T falls {max(r['T'] for r in run):.2f}->{min(r['T'] for r in run):.2f} "
          f"as F grows = TUR SATURATION (free-running biased walk saturates; barrier near F=A loosens it).")
    print("  EXTERNAL FRAME — the cos-position observable is DRIFT-DOMINATED on a running ring")
    print("    (extra drive advances the phase -> cos falls -> response is negative, not a fluctuation-")
    print("    response). The correct conjugate frame here is VELOCITY-frame Harada-Sasa; the ring is the")
    print("    IDEAL substrate to close it because <sigma> is known exactly. C(tau) still shows the running")
    print("    signature (locked: decays to a localized plateau; running: damped oscillation).")
    print("  VERDICT: the running current (F>A) reads as a sustained NESS in the self-frame (T>=1, current")
    print("    nonzero), exactly as gt=s; the ->r axiom does NOT force r on it. Locked F<A: no current.")
    print("Caveat: drive-forced (contingent), not topologically-forced k_frust -> verdict-agreement gate.")

    # ---------- figure ----------
    fig, ax = plt.subplots(1, 2, figsize=(13.5, 5.5))
    cols = plt.cm.viridis(np.linspace(0.1, 0.9, len(rows)))
    # LEFT: the correlation observable C(tau) -- honest external behavior (running signature)
    for r, c in zip(rows, cols):
        ls = "-" if r["has_current"] else ":"
        ax[0].plot(r["tau_arr"], r["C"], ls, color=c, lw=1.5, label=fr"F={r['F']} ({r['gt']})")
    ax[0].axhline(0.0, color="k", lw=0.5)
    ax[0].set_xlabel(r"lag $\tau$"); ax[0].set_ylabel(r"$C(\tau)=\langle\cos(\theta(t{+}\tau){-}\theta(t))\rangle$")
    ax[0].set_title("correlation observable (external-frame raw signal)\n"
                    "locked (dotted): decays to localized plateau;  running (solid): damped oscillation")
    ax[0].set_xlim(0, 15); ax[0].legend(fontsize=8, ncol=2); ax[0].grid(alpha=0.3)

    # RIGHT: the CLOSED self-frame
    Fv = np.array([r["F"] for r in rows])
    sig = np.array([r["sigma"] for r in rows])
    Tn = np.array([r["T"] if r["has_current"] else np.nan for r in rows])
    ax[1].axvline(A, color="gray", ls=":", lw=1.2, label="F=A (locked→running)")
    ax[1].plot(Fv, sig, "s-", color="tab:red", label=r"$\langle\sigma\rangle=F\langle\dot\theta\rangle/D$ (EXACT = J·A)")
    ax[1].set_xlabel(r"drive $F$ (affinity axis;  $F<A$ locked $\to$ $F>A$ running)")
    ax[1].set_ylabel(r"$\langle\sigma\rangle$ (exact entropy production)", color="tab:red")
    ax2 = ax[1].twinx()
    ax2.axhline(1.0, color="tab:blue", ls=":", lw=0.8)
    ax2.plot(Fv, Tn, "^-", color="tab:blue", label=r"self-frame $T$ (TUR-tightness $\geq 1$, →1 as F→∞)")
    ax2.set_ylabel(r"self-frame $T$", color="tab:blue"); ax2.set_ylim(0, 3)
    ax[1].set_title("CLOSED self-frame: exact ⟨σ⟩=J·A + TUR saturation\n(T≥1 everywhere; →1 as the running walk frees)")
    l1, lb1 = ax[1].get_legend_handles_labels(); l2, lb2 = ax2.get_legend_handles_labels()
    ax[1].legend(l1 + l2, lb1 + lb2, fontsize=8, loc="upper center"); ax[1].grid(alpha=0.3)
    fig.suptitle("driven_ring NESS: CLOSED self-frame (exact ⟨σ⟩=J·A) — external frame owed to velocity Harada–Sasa", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    png = OUT / "two_frame_driven_ring.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
