"""k_frust frustration-meter -- BULLETPROOF instrument.

The instrument the Wall round-trip test will depend on. It must:
  (1) cleanly distinguish a frustrated loop from a matched non-frustrated one,
  (2) produce only INTERIOR observables (never a NaN: a NaN is either a bad
      test or the asymptotic-closure falsifier -- we trip and diagnose, never
      fallback-fill),
  (3) never manufacture an excluded boundary (no hard-clip at 0; spontaneous
      floor + multiplicative noise keep rho>0 by dynamics, as the r-regime
      "spontaneous emission only" requires).

Matched loops -- identical magnitude, the ONLY difference is reciprocity:
  frustrated: antisymmetric cyclic gamma (NON-reciprocal) -> broken detailed
              balance -> Schnakenberg cyclic current J != 0 -> no P_ss.
  control:    symmetric gamma (reciprocal) -> detailed balance -> J = 0 -> P_ss.

Two meters:
  J   = intrinsic cyclic current (chirality of rho-rotation; OBSERVER-INDEPENDENT
        ground truth: is the loop actually a drain?).
  N_f = negative-response fraction read through the tau_obs kernel
        (OBSERVER-RELATIVE signature; its tau_obs dependence is the invariance test).
  X_v = vertex FDR-slope (regime label; should migrate c->s->r with tau_obs --
        the 'knob is live' bracket).

Run: python H:/mpa-central/library/k_frust_meter.py
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

# ---- kernel params (tuned for amplitude-matched, bounded, interior dynamics) ----
G0, L = 1.20, 1.00          # chit = ln(G0/L) > 0: sustained NESS holding
RHO_SAT = 1.0
G = 0.5                     # coupling magnitude (same for both loops)
S0 = 1.0e-3                 # spontaneous-emission floor (keeps rho>0 by dynamics)
SIGMA = 0.02                # multiplicative-noise coeff (vanishes at rho->0)
RHO_FLOOR = 1.0e-7          # soft positivity guard, NEVER 0
DT = 0.005
N_REAL = 512
T_EQ = 4000
T_OBS = 12000
H = 0.05                    # perturbation: boost mode-0 gain

G_FRUST = G * np.array([[0, 1, -1], [-1, 0, 1], [1, -1, 0]], float)  # antisymmetric (RPS)
G_CTRL = G * np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]], float)      # symmetric competition


def finite(name, x):
    """NaN/inf tripwire. A non-finite value in MPA apparatus is never tolerated:
    it is a bad test or the asymptotic-closure falsifier. Halt and diagnose."""
    x = np.asarray(x, float)
    if not np.all(np.isfinite(x)):
        bad = np.argwhere(~np.isfinite(x))
        raise FloatingPointError(
            f"NON-FINITE in '{name}' (MPA NaN tripwire): {x.ravel()[~np.isfinite(x.ravel())][:5]} "
            f"at {bad[:5].tolist()} -- bad test or boundary (0/1/inf) attainment. Diagnose, do not fill."
        )
    return x


def step(rho, gmat, gain0, rng):
    """One Euler-Maruyama step. No hard-zero clip: spontaneous floor S0 +
    multiplicative sqrt(rho) noise keep rho>0; RHO_FLOOR is a >0 safety only."""
    S = rho.sum(axis=1, keepdims=True)
    gain = gain0[None, :] / (1.0 + S / RHO_SAT)        # saturating gain (bounds growth)
    cross = rho * (rho @ gmat.T) / RHO_SAT             # rho_i * sum_j g_ij rho_j
    drift = (gain - L) * rho - cross + S0
    noise = SIGMA * np.sqrt(np.maximum(rho, 0.0)) * rng.standard_normal(rho.shape) * np.sqrt(DT)
    return np.maximum(rho + drift * DT + noise, RHO_FLOOR)


def simulate(gmat, seed):
    rng = np.random.default_rng(seed)
    rho = np.tile([0.06, 0.03, 0.01], (N_REAL, 1)).astype(float)
    for _ in range(T_EQ):
        rho = step(rho, gmat, np.array([G0, G0, G0]), rng)
    unp = rho.copy(); per = rho.copy()
    g0_per = np.array([G0 * (1.0 + H), G0, G0])

    vel_unp = np.zeros((T_OBS, 3)); vel_per = np.zeros((T_OBS, 3))
    traj = np.zeros((T_OBS, 3))
    floor_hits = 0
    chir = np.zeros(T_OBS)
    for t in range(T_OBS):
        u_prev, p_prev = unp.copy(), per.copy()
        unp = step(unp, gmat, np.array([G0, G0, G0]), rng)
        per = step(per, gmat, g0_per, rng)
        floor_hits += int(np.sum(unp <= RHO_FLOOR * 1.0001))
        vel_unp[t] = ((unp - u_prev) / DT).mean(axis=0)
        vel_per[t] = ((per - p_prev) / DT).mean(axis=0)
        traj[t] = unp.mean(axis=0)
        # intrinsic cyclic current (chirality) per replica, then mean
        m = unp.mean(axis=1, keepdims=True)
        a = unp[:, 0] - m[:, 0]
        b = (unp[:, 1] - unp[:, 2]) / np.sqrt(3.0)
        adot = (unp[:, 0] - u_prev[:, 0]) / DT - ((unp.mean(1) - u_prev.mean(1)) / DT)
        bdot = ((unp[:, 1] - unp[:, 2]) - (u_prev[:, 1] - u_prev[:, 2])) / (np.sqrt(3.0) * DT)
        r2 = a * a + b * b
        good = r2 > 1e-10
        chir[t] = float(np.mean((a[good] * bdot[good] - b[good] * adot[good]) / r2[good])) if good.any() else 0.0
    J = float(np.mean(chir))
    finite("cyclic_current_J", J)
    return vel_unp, vel_per, traj, J, floor_hits


def trap(y, x):
    """Version-safe trapezoidal integral (np.trapz renamed to np.trapezoid)."""
    y = np.asarray(y, float); x = np.asarray(x, float)
    return float(np.sum((y[1:] + y[:-1]) * 0.5 * np.diff(x)))


def ema(vel, tau):
    a = np.exp(-DT / tau)
    d = np.zeros_like(vel); acc = np.zeros(vel.shape[1])
    for t in range(vel.shape[0]):
        acc = a * acc + vel[t]
        d[t] = acc
    return d


def analyze(vel_unp, vel_per, tau_grid):
    lags = np.unique(np.geomspace(1, vel_unp.shape[0] - 1, 50).astype(int))
    rows = []
    for tau in tau_grid:
        du = finite("trail_unp", ema(vel_unp, tau))
        dp = finite("trail_per", ema(vel_per, tau))
        chi = (dp - du) / H
        chi_loop = finite("chi_loop", chi.sum(axis=1)[lags])
        denom = float(np.sum(np.abs(chi_loop)))
        if denom < 1e-9:
            raise FloatingPointError(
                f"N_f denominator ~0 at tau_obs={tau:.3g}: no loop response -- "
                f"window too short OR vertex driven to a boundary. Diagnose."
            )
        N_f = float(np.sum(np.clip(-chi_loop, 0, None)) / denom)
        # vertex-0 FDR: X = area(chi) / area(C0 - C), interior because noise
        # guarantees decorrelation (denominator > 0); tripwire if not.
        d0 = du[:, 0]
        C0 = float(np.mean(d0 * d0))
        C = np.array([float(np.mean(d0[:-lag] * d0[lag:])) for lag in lags])
        dC = C0 - C
        chi0 = chi[:, 0][lags]
        area_dC = trap(np.clip(dC, 0, None), lags)
        if area_dC < 1e-9:
            raise FloatingPointError(
                f"vertex locus degenerate at tau_obs={tau:.3g}: trail never "
                f"decorrelated (area(C0-C)~0) -- window too short OR vertex at c-boundary."
            )
        X_v = float(trap(chi0, lags) / area_dC)
        finite("X_vertex", X_v); finite("N_f", N_f)
        rows.append({"tau_obs": float(tau), "N_f": N_f, "X_v": X_v})
    return rows


def main():
    tau_grid = np.geomspace(0.05, 50.0, 12)
    print("simulating matched loops (frustrated=antisymmetric, control=symmetric)...")
    vu_f, vp_f, traj_f, J_f, fh_f = simulate(G_FRUST, seed=1)
    vu_c, vp_c, traj_c, J_c, fh_c = simulate(G_CTRL, seed=1)
    print(f"  amplitudes: <rho> frust={traj_f.mean():.4f}  control={traj_c.mean():.4f}  (matched?)")
    print(f"  intrinsic cyclic current J: frust={J_f:+.4e}  control={J_c:+.4e}  (frust!=0, ctrl~0?)")
    print(f"  floor hits (should be ~0): frust={fh_f}  control={fh_c}")
    res_f = analyze(vu_f, vp_f, tau_grid)
    res_c = analyze(vu_c, vp_c, tau_grid)

    print(f"\n{'tau_obs':>9} | {'N_f frust':>9} {'X_v frust':>9} | {'N_f ctrl':>9} {'X_v ctrl':>9}")
    for rf, rc in zip(res_f, res_c):
        print(f"{rf['tau_obs']:>9.3f} | {rf['N_f']:>9.4f} {rf['X_v']:>9.4f} | {rc['N_f']:>9.4f} {rc['X_v']:>9.4f}")

    fig, ax = plt.subplots(2, 2, figsize=(14, 9))
    tt = np.arange(T_OBS) * DT
    for i in range(3):
        ax[0, 0].plot(tt, traj_f[:, i], lw=0.6, label=f"mode {i}")
    ax[0, 0].set_title(f"frustrated (antisym): rho_i(t) -- cyclic drain | J={J_f:+.3e}")
    ax[0, 0].set_xlabel("time"); ax[0, 0].set_ylabel("<rho_i>"); ax[0, 0].legend(fontsize=8)
    for i in range(3):
        ax[0, 1].plot(tt, traj_c[:, i], lw=0.6, label=f"mode {i}")
    ax[0, 1].set_title(f"control (sym): rho_i(t) -- stable coexist | J={J_c:+.3e}")
    ax[0, 1].set_xlabel("time"); ax[0, 1].set_ylabel("<rho_i>"); ax[0, 1].legend(fontsize=8)
    tg = [r["tau_obs"] for r in res_f]
    ax[1, 0].semilogx(tg, [r["N_f"] for r in res_f], "o-", color="tab:red", label="frustrated")
    ax[1, 0].semilogx(tg, [r["N_f"] for r in res_c], "s-", color="tab:blue", label="control")
    ax[1, 0].set_title("N_f vs tau_obs (observer-relative frustration signature)")
    ax[1, 0].set_xlabel("tau_obs"); ax[1, 0].set_ylabel("N_f"); ax[1, 0].legend(fontsize=8); ax[1, 0].grid(alpha=0.3)
    ax[1, 1].semilogx(tg, [r["X_v"] for r in res_f], "o-", color="tab:red", label="frustrated")
    ax[1, 1].semilogx(tg, [r["X_v"] for r in res_c], "s-", color="tab:blue", label="control")
    ax[1, 1].axhline(0, color="gray", lw=0.6); ax[1, 1].axhline(1, color="gray", lw=0.6, ls="--")
    ax[1, 1].set_title("vertex X vs tau_obs (regime label -- should migrate)")
    ax[1, 1].set_xlabel("tau_obs"); ax[1, 1].set_ylabel("X_vertex"); ax[1, 1].legend(fontsize=8); ax[1, 1].grid(alpha=0.3)
    fig.suptitle("k_frust bulletproof meter: matched loops, interior observables, NaN-tripwired", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    png = OUT / "k_frust_meter.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
