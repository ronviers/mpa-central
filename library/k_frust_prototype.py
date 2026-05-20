"""k_frust topological-invariance trap -- PROTOTYPE (physics + observable check).

Falsification target (v9 Scale-relativity / cdv1 Topological drain):
  "tau_obs sweep walks vertex labels c->s->r, but k_frust does NOT migrate
   (topological). A frustrated loop never resolves into a clean c or r."

This prototype establishes, fast, BEFORE a full primitive build:
  (1) ground truth: frustrated (cyclic RPS gamma) loops perpetually / shows
      negative loop-response; control (symmetric cooperative) is stable, no
      negative response.
  (2) the tau_obs sweep: does the frustration signature survive it, and does
      the control's vertex label migrate (knob is live)?

Falsifier (no-escape form): the frustrated loop reads a CLEAN c or r at some
tau_obs. Mere fade of the negative lobe is NOT a falsification.

3-mode kernel (cdv1 universal two-mode kernel, N=3):
  rho_i' = (G0/(1+S/rho_sat) - L) rho_i  - (1/rho_sat) rho_i * sum_j g_ij rho_j + noise
  frustrated: g antisymmetric cyclic [[0,1,-1],[-1,0,1],[1,-1,0]]*g  (RPS, no P_ss)
  control:    g symmetric cooperative -g*[[0,1,1],[1,0,1],[1,1,0]]    (stable coexist)

Run: python H:/mpa-central/library/k_frust_prototype.py
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

rng = np.random.default_rng(0)

# kernel params
G0, L = 1.20, 1.00            # chit = ln(G0/L) > 0 : sustained NESS holding
RHO_SAT = 1.0
G = 0.9                        # coupling strength
SIGMA = 0.03                   # noise
DT = 0.01
N_REAL = 512
T_EQ = 4000                    # equilibration steps
T_OBS = 8000                   # measurement steps
H = 0.05                       # perturbation: boost mode-0 gain

G_FRUST = G * np.array([[0, 1, -1], [-1, 0, 1], [1, -1, 0]], dtype=float)
G_CTRL = -G * np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]], dtype=float)


def step(rho, gmat, gain0, rng):
    """One Euler-Maruyama step. rho: (n_real,3). gain0: (3,) per-mode G0."""
    S = rho.sum(axis=1, keepdims=True)                  # (n_real,1)
    gain = gain0[None, :] / (1.0 + S / RHO_SAT)          # saturating gain
    cross = rho * (rho @ gmat.T) / RHO_SAT               # (n_real,3) sum_j g_ij rho_j
    drift = (gain - L) * rho - cross
    noise = SIGMA * rng.standard_normal(rho.shape) * np.sqrt(DT)
    rho2 = rho + drift * DT + noise
    return np.clip(rho2, 0.0, 50.0)


def simulate(gmat, label):
    """Equilibrate, snapshot, fork unperturbed/perturbed (boost mode-0 gain),
    evolve paired, record per-step velocity (rho') for both branches."""
    rho = np.tile(np.array([0.6, 0.3, 0.1]), (N_REAL, 1)).astype(float)
    g0 = np.array([G0, G0, G0])
    for _ in range(T_EQ):
        rho = step(rho, gmat, g0, rng)
    unp = rho.copy()
    per = rho.copy()
    g0_per = g0.copy(); g0_per[0] = G0 * (1.0 + H)        # perturb mode-0 gain
    vel_unp = np.zeros((T_OBS, 3))
    vel_per = np.zeros((T_OBS, 3))
    rho_unp_traj = np.zeros((T_OBS, 3))
    for t in range(T_OBS):
        u_prev, p_prev = unp.copy(), per.copy()
        unp = step(unp, gmat, g0, rng)
        per = step(per, gmat, g0_per, rng)
        vel_unp[t] = ((unp - u_prev) / DT).mean(axis=0)
        vel_per[t] = ((per - p_prev) / DT).mean(axis=0)
        rho_unp_traj[t] = unp.mean(axis=0)
    return vel_unp, vel_per, rho_unp_traj


def ema_trail(vel, tau_obs):
    """EMA of the velocity series with time constant tau_obs (real-time)."""
    a = np.exp(-DT / tau_obs)
    d = np.zeros_like(vel)
    acc = np.zeros(vel.shape[1])
    for t in range(vel.shape[0]):
        acc = a * acc + vel[t]
        d[t] = acc
    return d


def analyze(vel_unp, vel_per, tau_grid):
    """For each tau_obs: response chi_j(lag) = (d_per - d_unp)/H per mode;
    N_f = negative fraction of the loop response; vertex FDR-slope proxy."""
    lags = np.unique(np.geomspace(1, vel_unp.shape[0] - 1, 40).astype(int))
    out = []
    for tau in tau_grid:
        du = ema_trail(vel_unp, tau)
        dp = ema_trail(vel_per, tau)
        chi = (dp - du) / H                              # (T,3) response per mode
        # loop response = sum over modes (loop-odd combination carries sign)
        chi_loop = chi.sum(axis=1)
        chi_l = chi_loop[lags]
        # N_f: fraction of |response| that is negative (transient-negative)
        denom = np.sum(np.abs(chi_l))
        nf = float(np.sum(np.clip(-chi_l, 0, None)) / denom) if denom > 1e-12 else 0.0
        # vertex proxy: autocorr-vs-response slope on mode-0 trail (FDR X)
        d0 = du[:, 0]
        C = np.array([np.mean(d0[:-lag] * d0[lag:]) if lag > 0 else np.mean(d0*d0)
                      for lag in lags])
        C0 = np.mean(d0 * d0)
        chi0 = chi[:, 0][lags]
        dC = C0 - C
        m = dC > 1e-9
        Xslope = float(np.polyfit(dC[m], chi0[m], 1)[0]) if m.sum() > 2 else np.nan
        out.append({"tau_obs": tau, "N_f": nf, "X_vertex": Xslope,
                    "chi_loop": chi_l, "lags": lags})
    return out


def main():
    tau_grid = np.geomspace(0.05, 30.0, 10)
    print("simulating frustrated (RPS) and control (cooperative)...")
    vu_f, vp_f, traj_f = simulate(G_FRUST, "frustrated")
    vu_c, vp_c, traj_c = simulate(G_CTRL, "control")
    res_f = analyze(vu_f, vp_f, tau_grid)
    res_c = analyze(vu_c, vp_c, tau_grid)

    print(f"{'tau_obs':>8} | {'N_f frust':>9} {'X_vtx frust':>11} | {'N_f ctrl':>9} {'X_vtx ctrl':>11}")
    for rf, rc in zip(res_f, res_c):
        print(f"{rf['tau_obs']:>8.3f} | {rf['N_f']:>9.3f} {rf['X_vertex']:>11.3f} | "
              f"{rc['N_f']:>9.3f} {rc['X_vertex']:>11.3f}")

    fig, ax = plt.subplots(2, 2, figsize=(14, 9))
    # rho trajectories (ground-truth: frustrated cycles, control stabilizes)
    tt = np.arange(T_OBS) * DT
    for i in range(3):
        ax[0, 0].plot(tt, traj_f[:, i], lw=0.8, label=f"mode {i}")
    ax[0, 0].set_title("frustrated (RPS): rho_i(t) -- should cycle (no P_ss)")
    ax[0, 0].set_xlabel("time"); ax[0, 0].set_ylabel("<rho_i>"); ax[0, 0].legend(fontsize=8)
    for i in range(3):
        ax[0, 1].plot(tt, traj_c[:, i], lw=0.8, label=f"mode {i}")
    ax[0, 1].set_title("control (coop): rho_i(t) -- should stabilize (coexist)")
    ax[0, 1].set_xlabel("time"); ax[0, 1].set_ylabel("<rho_i>"); ax[0, 1].legend(fontsize=8)
    # N_f vs tau_obs (the invariance test)
    tg = [r["tau_obs"] for r in res_f]
    ax[1, 0].semilogx(tg, [r["N_f"] for r in res_f], "o-", color="tab:red", label="frustrated N_f")
    ax[1, 0].semilogx(tg, [r["N_f"] for r in res_c], "s-", color="tab:blue", label="control N_f")
    ax[1, 0].set_title("N_f (negative-response fraction) vs tau_obs\n(frust flat>0 = invariant; ->0 = resolves)")
    ax[1, 0].set_xlabel("tau_obs (observer kernel)"); ax[1, 0].set_ylabel("N_f"); ax[1, 0].legend(fontsize=8)
    ax[1, 0].grid(alpha=0.3)
    # vertex X vs tau_obs (knob-live bracket: control should migrate)
    ax[1, 1].semilogx(tg, [r["X_vertex"] for r in res_f], "o-", color="tab:red", label="frustrated X_vtx")
    ax[1, 1].semilogx(tg, [r["X_vertex"] for r in res_c], "s-", color="tab:blue", label="control X_vtx")
    ax[1, 1].axhline(0, color="gray", lw=0.6); ax[1, 1].axhline(1, color="gray", lw=0.6, ls="--")
    ax[1, 1].set_title("vertex FDR-slope vs tau_obs (knob-live: should migrate)")
    ax[1, 1].set_xlabel("tau_obs"); ax[1, 1].set_ylabel("X_vertex (mode-0)"); ax[1, 1].legend(fontsize=8)
    ax[1, 1].grid(alpha=0.3)
    fig.suptitle("k_frust trap PROTOTYPE: does frustration survive the tau_obs sweep?", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    png = OUT / "k_frust_prototype.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
