"""k_frust Wall round-trip -- OPTION 2, PRIMARY-C: DERIVED reformation.

Goal of THIS file: drive a frustrated loop through the Complexity Wall (eps->1,
forced NRT chaos) and back, and ask whether the topological invariant (cyclic
current J) reforms -- with the reformation DERIVED from the framework's flow,
not imposed by a hand-picked rule (option-1's grave) and not left wherever a
random scramble pushed gamma (the BLOCK-IN's crude annealed arm).

The seven masses of the silhouette (all present + runnable):
  1. TOWER          -- N levels; level 0 = the frustrated loop (rho, gamma).
  2. LEVEL MAP       -- coupled Stuart-Landau generators; mu = MU_SCALE*(eps-1).
  3. WALL DRIVE      -- eps(t): <1 (converging) -> >=1 (Wall, tower diverges) -> <1.
  4. CHAOS@eps>=1    -- >=3 incommensurate rotators + chain coupling -> NRT route;
                        soft-saturated so it is BOUNDED turbulence, not a blowup.
  5. DOWNWARD COUPLE -- top-of-tower activity feeds back to level 0 (heat-tax
                        raises L_0; if ANNEALED, also corrupts the represented
                        invariant). This is how meta-Wall-chaos reaches k_frust.
  6. J METER         -- level-0 cyclic current J (chirality), the invariant.
  7. QUENCHED/ANNEAL -- switch: is level-0 wiring fixed (topology given) or free
                        to be reshaped by the represented invariant? -- the test.

DERIVED reformation (PRIMARY-C, the load-bearing mass this file refines):
  The frustration is the (1,1,1)-chirality of the 3-cycle: gamma = a_rep * CYC.
  a_rep is the meta-ledger's REPRESENTATION of the invariant. It is transported
  by two competing forces:
    * SERVO (re-trapping physics): a_rep relaxes toward C_REP * <loop chirality>,
      where <loop chirality> is the loop's OWN emergent cyclic current measured
      from rho (source-of-truth, NOT the reconstructed gamma -- decouple observer
      from process). C_REP is calibrated so the canonical frustrated loop is a
      fixed point (tied to the bulletproof meter J_REF=+5.87e-2), so faithful
      transport at eps<1 holds BY CONSTRUCTION -- not by tuning the verdict.
    * WALL CHAOS (the threat): the chaotic tower kicks a_rep, gated by the SAME
      tower 'excess' that drives the amplitude destruction (no separate dial).
  ANNEALED: gamma is reconstructed each step from a_rep (the invariant has no
  existence apart from its representation -> chaos can destroy it). QUENCHED:
  gamma fixed (topology given -> servo always re-traps -> near-trivial survival).

  The frustrated state is an ATTRACTING fixed point only if the loop's emergent
  chirality does not vanish as gamma weakens -- that is the limit-cycle frequency
  being amplitude/coupling-robust. Whether it is, is an EMPIRICAL property read
  off the BRACKET below; if the bracket fails it is a tower bug, not a verdict.

ESSENTIAL BRACKET (the option-2 analog of option-1's sustain control):
  annealed + NO Wall must hold a_rep ~ G and J ~ J_REF. If frustration decays
  with no Wall, the apparatus bleeds the invariant on its own (option-1's bug)
  and NO annealed verdict can be read until it is fixed.

ONE free knob: K_REP (how hard the Wall corrupts the wiring), defaulted to the
DOWN_COUPLE scale ('Wall hits wiring as hard as it hits loss'). A single point
is weaker than the survival-vs-K_REP transition; sweep it as the next move if the
default point is ambiguous.

SECONDARY (deferred; none change the silhouette): exact Mori-Zwanzig projection,
Landauer constants alpha_sigma(eps)=alpha_0(1-eps), rigorous NRT 3-torus / +ve
Lyapunov demo, Harada-Sasa sigma. The N>3 'generic frustration elsewhere'
knife-edge (sec.6 of the handoff) needs a larger graph than a single 3-cycle and
is a separate move, not PRIMARY-C.

Run: python H:/mpa-central/library/k_frust_wall_tower.py
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

# ---- level-0 loop (reused shape from the bulletproof meter) ----
G0, L0 = 1.20, 1.00
RHO_SAT, G, S0, SIGMA, RHO_FLOOR, DT = 1.0, 0.5, 1.0e-3, 0.02, 1.0e-7, 0.005
N_REAL = 256
CYC = np.array([[0, 1, -1], [-1, 0, 1], [1, -1, 0]], float)   # the frustration generator
G_FRUST = G * CYC                                              # canonical frustrated wiring

# ---- tower (coupled Stuart-Landau = canonical Hopf->torus->chaos) ----
N_LEVELS = 4                    # 3 meta-ledger oscillators above the substrate (>=3 for NRT)
OMEGA = np.array([0.7, 1.13, 1.7])  # incommensurate meta-ledger frequencies
MU_SCALE = 3.0                  # mu = MU_SCALE*(eps-1): eps<1 contract, eps>1 oscillate/chaos
K_COUPLE = 0.5                  # diffusive inter-level coupling (drives the NRT route)
Z_NOISE = 0.03                  # meta-ledger spontaneous floor (so mu>0 ignites it; nothing sits at 0)
HEATTAX_UP = 0.6                # level-0 sigma forces the bottom of the tower
DOWN_COUPLE = 2.5               # EXCESS top activity -> level-0 heat-tax loss (raises L_0)
QUIET_FLOOR = 0.20              # quiescent tower activity; only EXCESS above this couples down (clean quiet loop)

# ---- DERIVED reformation (PRIMARY-C): the represented invariant a_rep ----
CHIR_EMA_TAU = 2.0              # time-average the loop's emergent current (per-step /r2 is noise-inflated --
                               #   the bulletproof meter averages over its whole window; same discipline here)
KAPPA = 1.5                     # servo rate (slow vs the loop's re-equilibration after a gamma change)
K_REP = DOWN_COUPLE             # Wall-chaos corruption of the invariant; ONE free knob (tied to loss scale)
BETA_DISC = 3.0                 # discrete-lens saturation: target = G*tanh(BETA * chir/chir_quiet) -> +/-G pinned
REP_NOISE = 5.0e-3              # representation spontaneous floor (nothing sits exactly at a_rep=0)
A_REP_CLAMP = 2.0 * G           # interior guard on the representation (NaN tripwire still catches blowups)
# C_REP is calibrated in main() to the tower's IN-SITU quiet current so the canonical
# frustrated loop is an exact fixed point (faithful transport), not the meter's value.


def finite(name, x):
    x = np.asarray(x, float)
    if not np.all(np.isfinite(x)):
        raise FloatingPointError(f"NON-FINITE in '{name}' (MPA NaN tripwire): bad test or boundary attainment.")
    return x


def loop_step(rho, gamma, L_eff, rng):
    """Level-0 step with INJECTABLE loss L_eff (the downward heat-tax). No
    hard-zero clip (spontaneous floor + multiplicative noise keep rho>0)."""
    S = rho.sum(axis=1, keepdims=True)
    gain = G0 / (1.0 + S / RHO_SAT)
    cross = rho * (rho @ gamma.T) / RHO_SAT
    drift = (gain - L_eff) * rho - cross + S0
    noise = SIGMA * np.sqrt(np.maximum(rho, 0.0)) * rng.standard_normal(rho.shape) * np.sqrt(DT)
    return np.maximum(rho + drift * DT + noise, RHO_FLOOR)


def cyclic_current(rho, rp):
    """PRIMARY-B: ensemble angular velocity <a*bdot-b*adot>/<a*a+b*b>. Stable
    radius-squared denominator (NOT speed -> not noise-inflated); time-averaging
    extracts the slow coherent rotation from the per-step noise. Read only in the
    QUIET before/after phases (loop at normal amplitude) -- the verdict is
    J_after/J_before. Destruction is confirmed separately via amplitude collapse.
    den>0 via spontaneous floor; NaN -> tripwire."""
    m = rho.mean(1); mp = rp.mean(1)
    a = rho[:, 0] - m; b = (rho[:, 1] - rho[:, 2]) / np.sqrt(3.0)
    adot = ((rho[:, 0] - m) - (rp[:, 0] - mp)) / DT
    bdot = ((rho[:, 1] - rho[:, 2]) - (rp[:, 1] - rp[:, 2])) / (np.sqrt(3.0) * DT)
    r2 = a * a + b * b
    good = r2 > 1e-10                            # quiet-phase: healthy r2, no spikes
    if not good.any():
        return 0.0
    return float(np.mean((a[good] * bdot[good] - b[good] * adot[good]) / r2[good]))


def sigma0_of(rho, gamma):
    """Level-0 entropy-production proxy = maintenance/dissipation activity.
    SECONDARY: replace with Harada-Sasa integrated FDR violation."""
    cross = rho * (rho @ gamma.T) / RHO_SAT
    return float(np.mean(np.abs(cross).sum(axis=1)))


def epsilon_schedule(t, total, wall=True):
    """eps(t): converge -> Wall (>=1) -> converge. The round trip.
    wall=False holds eps=0.60 throughout -> the no-Wall BRACKET (sustain control)."""
    if not wall:
        return 0.60
    f = t / total
    if f < 0.20:   return 0.60
    if f < 0.35:   return 0.60 + (1.08 - 0.60) * (f - 0.20) / 0.15   # ramp up
    if f < 0.55:   return 1.08                                       # at the Wall
    if f < 0.70:   return 1.08 - (1.08 - 0.60) * (f - 0.55) / 0.15   # ramp back
    return 0.60                                                      # recover


def calibrate_quiet_chirality(seed=1, steps=12000):
    """In-situ quiet current of the canonical frustrated loop at the tower's
    operating point (gamma=G_FRUST, no heat-tax). EMA-smoothed -> the value the
    servo must reproduce so that a_rep=G is an exact fixed point (faithful
    transport by construction, NOT by tuning the verdict)."""
    rng = np.random.default_rng(seed)
    rho = np.tile([0.06, 0.03, 0.01], (N_REAL, 1)).astype(float)
    a = np.exp(-DT / CHIR_EMA_TAU)
    chir_ema = 0.0
    for t in range(steps):
        rp = rho.copy()
        rho = loop_step(rho, G_FRUST, L0, rng)
        chir_ema = a * chir_ema + (1.0 - a) * cyclic_current(rho, rp)
    return chir_ema


def run_tower(annealed: bool, seed: int, c_rep: float, wall: bool = True,
              transport: str = "continuous", k_rep: float = K_REP):
    """transport lens:
      'continuous' -- a_rep tracks the loop current MAGNITUDE (servo to C_REP*chir);
                      R1 shows the current is ~linear in coupling, so the only
                      stable fixed point is 0 -> magnitude is NOT a preserved invariant.
      'discrete'   -- a_rep tracks the topological SIGN-class: target=G*tanh(...) ->
                      +/-G are pinned attractors, 0 is repelling. Frustration-as-such
                      (no-P_ss) is orientation-independent; the Wall can at most FLIP
                      the sign (still frustrated), not continuously bleed it away."""
    rng = np.random.default_rng(seed)
    rho = np.tile([0.06, 0.03, 0.01], (N_REAL, 1)).astype(float)
    gamma = G_FRUST.copy()
    a_rep = G                                              # represented invariant; starts at the canonical loop
    a_ema = np.exp(-DT / CHIR_EMA_TAU)                     # EMA weight for the loop's slow emergent current
    chir_ema = G / c_rep                                   # init = quiet chirality (start on the fixed point)
    z = np.full(N_LEVELS - 1, 0.05 + 0.0j)                 # coupled Stuart-Landau generators
    total = 24000
    rec = {"J": np.zeros(total), "eps": np.zeros(total), "tower": np.zeros(total),
           "Leff": np.zeros(total), "rho": np.zeros(total), "a_rep": np.zeros(total)}
    for t in range(total):
        eps = epsilon_schedule(t, total, wall=wall)
        # --- ascend: coupled Stuart-Landau. mu=MU_SCALE*(eps-1) is the Wall knob:
        #     mu<0 (eps<1) -> contract to quiet fixed point; mu>0 (eps>1) -> Hopf
        #     into bounded oscillation; incommensurate OMEGA + coupling -> chaos. ---
        mu = MU_SCALE * (eps - 1.0)
        sig0 = sigma0_of(rho, gamma)
        F = np.zeros(N_LEVELS - 1, dtype=complex)
        F[0] = HEATTAX_UP * sig0                            # level-0 dissipation forces tower base
        dz = ((mu + 1j * OMEGA) * z - (np.abs(z) ** 2) * z
              + K_COUPLE * (z.mean() - z) + F)
        z = z + dz * DT + Z_NOISE * (rng.standard_normal(N_LEVELS - 1)
                                     + 1j * rng.standard_normal(N_LEVELS - 1)) * np.sqrt(DT)
        tower_activity = float(np.sum(np.abs(z)))           # bounded by the cubic term
        excess = max(0.0, tower_activity - QUIET_FLOOR)     # only EXCESS (chaotic) activity couples down
        # --- downward heat-tax: EXCESS raises level-0 loss; quiet loop stays clean ---
        L_eff = L0 + DOWN_COUPLE * excess
        # --- DERIVED reformation: reconstruct the wiring from the represented
        #     invariant (annealed); quenched keeps the topology given. ---
        if annealed:
            gamma = a_rep * CYC                             # invariant lives only in its representation
        # --- advance level 0 under the (heat-taxed) loss ---
        rp = rho.copy()
        rho = loop_step(rho, gamma, L_eff, rng)
        # loop's OWN emergent current (source of truth), EMA-smoothed: per-step /r2
        # is noise-inflated; the servo must see the slow equilibrated rotation.
        chir_ema = a_ema * chir_ema + (1.0 - a_ema) * cyclic_current(rho, rp)
        # --- transport the invariant: servo to the loop's emergent chirality
        #     (re-trapping physics) vs Wall-chaos corruption (gated by excess) ---
        chaos_kick = float(np.real(z).mean())               # chaotic, sign-random at the Wall; ~0 when quiet
        if transport == "discrete":
            target = G * np.tanh(BETA_DISC * c_rep * chir_ema / G)   # sign-class: +/-G pinned, 0 repelling
        else:
            target = c_rep * chir_ema                               # magnitude: only fixed point is 0
        da_rep = (KAPPA * (target - a_rep) + k_rep * excess * chaos_kick) * DT
        a_rep = float(np.clip(a_rep + da_rep + REP_NOISE * rng.standard_normal() * np.sqrt(DT),
                              -A_REP_CLAMP, A_REP_CLAMP))
        rec["J"][t] = chir_ema                              # loop's slow emergent current = the invariant readout
        rec["eps"][t] = eps
        rec["tower"][t] = tower_activity
        rec["Leff"][t] = L_eff
        rec["rho"][t] = float(rho.mean())
        rec["a_rep"][t] = a_rep
    for k, v in rec.items():
        finite(k, v)
    return rec, total


def phase_mean(x, lo, hi):
    return float(np.mean(x[lo:hi]))


def main():
    total = 24000
    seed = 1
    chir_quiet = calibrate_quiet_chirality(seed=seed)            # in-situ canonical-loop current
    c_rep = G / chir_quiet                                       # -> a_rep=G is an exact fixed point
    settle = (int(0.10 * total), int(0.20 * total))
    during = (int(0.42 * total), int(0.52 * total))
    recover = (int(0.90 * total), total)
    print(f"  [calibration] quiet chirality={chir_quiet:+.4e} -> C_REP={c_rep:.2f}; KAPPA={KAPPA} "
          f"anchor K_REP={K_REP} (= DOWN_COUPLE: Wall hits wiring as hard as loss)\n")

    # --- the four named arms (seed 1): quenched control + dual-lens brackets + discrete Wall ---
    rec_q = run_tower(annealed=False, seed=seed, c_rep=c_rep, wall=True)[0]                       # topology given
    rec_cb = run_tower(annealed=True, seed=seed, c_rep=c_rep, wall=False, transport="continuous")[0]  # cont. bracket
    rec_db = run_tower(annealed=True, seed=seed, c_rep=c_rep, wall=False, transport="discrete")[0]    # disc. bracket
    rec_dw = run_tower(annealed=True, seed=seed, c_rep=c_rep, wall=True, transport="discrete")[0]     # disc + Wall

    print(f"{'arm':>26}: {'J settle->recover':>26} | {'a_rep settle->recover':>24} | destruction")
    arms = [("QUENCHED (control)", rec_q), ("BRACKET continuous, NO Wall", rec_cb),
            ("BRACKET discrete, NO Wall", rec_db), ("ANNEALED discrete + Wall", rec_dw)]
    for tag, rec in arms:
        Jb = phase_mean(rec["J"], *settle); Jr = phase_mean(rec["J"], *recover)
        ab = phase_mean(rec["a_rep"], *settle); ar = phase_mean(rec["a_rep"], *recover)
        rho_b = phase_mean(rec["rho"], *settle); rho_d = phase_mean(rec["rho"], *during)
        print(f"{tag:>26}: {Jb:+.3e}->{Jr:+.3e} | {ab:+.3f}->{ar:+.3f} (G={G}) | "
              f"rho {rho_b:.4f}->{rho_d:.4f} ({rho_d/rho_b:.2f}x)")

    # --- K_REP scan (discrete annealed + Wall): survival vs Wall-corruption strength ---
    krep_grid = [0.0, 1.0, 2.5, 5.0, 10.0, 20.0]
    scan_seeds = [1, 2, 3, 4]
    print(f"\n  K_REP scan (discrete, annealed, +Wall) -- post-Wall a_rep over seeds {scan_seeds}:")
    print(f"  {'K_REP':>6} | {'<a_rep>_recover':>16} {'sd':>7} | {'flips':>6} {'dead':>5} | verdict")
    scan = []
    for kr in krep_grid:
        ars = []
        for s in scan_seeds:
            r = run_tower(annealed=True, seed=s, c_rep=c_rep, wall=True, transport="discrete", k_rep=kr)[0]
            ars.append(phase_mean(r["a_rep"], *recover))
        ars = np.array(ars)
        flips = int(np.sum(ars < -0.5 * G))                  # reformed with REVERSED chirality (still frustrated)
        dead = int(np.sum(np.abs(ars) < 0.3 * G))            # frustration destroyed (near the repelling 0)
        survived = int(np.sum(np.abs(ars) > 0.5 * G))
        verdict = "DESTROYED (kill)" if dead > len(scan_seeds) // 2 else (
            "frustration survives (some sign-flips)" if flips else "frustration survives (chirality kept)")
        scan.append((kr, ars.mean(), ars.std(), flips, dead, survived))
        print(f"  {kr:>6.1f} | {ars.mean():>+16.3f} {ars.std():>7.3f} | {flips:>6} {dead:>5} | {verdict}")

    print("\n================ RUNG 2 VERDICT (dual lens) ================")
    print("CONTINUOUS lens (current magnitude): bracket bleeds to ~0 with NO Wall -> the magnitude")
    print("  is NOT a preserved invariant (only fixed point is 0; trivially, weak wiring = weak current).")
    print("DISCRETE lens (topological sign-class): bracket holds at +/-G; the Wall can at most FLIP")
    print("  the sign (a reversed loop is STILL frustrated). Destruction (a_rep->0) requires landing on")
    print("  the repelling separatrix -> see scan for whether any K_REP achieves it at/below the anchor.")

    # ---- figure ----
    tt = np.arange(total) * DT
    def smooth(x, w=600):
        return np.convolve(x, np.ones(w) / w, mode="same")
    fig, ax = plt.subplots(4, 1, figsize=(14, 13))
    ax[0].plot(tt, rec_q["eps"], color="k", lw=1.2); ax[0].axhline(1.0, color="red", ls="--", lw=1.0, label="Wall")
    ax[0].plot(tt, rec_q["tower"], color="tab:purple", lw=0.5, alpha=0.7, label="tower activity")
    ax[0].set_ylabel("eps / tower"); ax[0].legend(fontsize=8)
    ax[0].set_title("k_frust Wall round-trip R2 -- dual lens (continuous magnitude vs discrete sign-class)")
    ax[1].plot(tt, smooth(rec_q["J"]), color="tab:blue", lw=1.8, label="J quenched (control)")
    ax[1].plot(tt, smooth(rec_dw["J"]), color="tab:red", lw=1.8, label="J discrete annealed + Wall")
    ax[1].plot(tt, smooth(rec_db["J"]), color="tab:green", lw=1.2, ls="--", label="J discrete, NO Wall (bracket)")
    ax[1].plot(tt, smooth(rec_cb["J"]), color="tab:orange", lw=1.2, ls=":", label="J continuous, NO Wall (bracket)")
    ax[1].axhline(0, color="k", lw=0.6); ax[1].set_ylim(-0.10, 0.10)
    ax[1].set_ylabel("cyclic current J"); ax[1].legend(fontsize=8)
    ax[2].plot(tt, rec_q["a_rep"], color="tab:blue", lw=0.8, label="quenched")
    ax[2].plot(tt, rec_dw["a_rep"], color="tab:red", lw=0.8, label="discrete annealed + Wall")
    ax[2].plot(tt, rec_db["a_rep"], color="tab:green", lw=0.8, ls="--", label="discrete, NO Wall (bracket)")
    ax[2].plot(tt, rec_cb["a_rep"], color="tab:orange", lw=0.8, ls=":", label="continuous, NO Wall (bracket)")
    ax[2].axhline(G, color="k", lw=0.6, ls=":"); ax[2].axhline(-G, color="k", lw=0.6, ls=":"); ax[2].axhline(0, color="k", lw=0.6)
    ax[2].set_ylabel("represented invariant a_rep"); ax[2].set_xlabel("time"); ax[2].legend(fontsize=8)
    for a_ in ax[:3]:
        a_.axvspan(0.35 * total * DT, 0.55 * total * DT, color="red", alpha=0.07)
    krs = [s[0] for s in scan]
    ax[3].errorbar(krs, [s[1] for s in scan], yerr=[s[2] for s in scan], fmt="o-", color="tab:red", capsize=3,
                   label="<a_rep> post-Wall (discrete)")
    ax[3].axhline(G, color="k", lw=0.6, ls=":"); ax[3].axhline(-G, color="k", lw=0.6, ls=":"); ax[3].axhline(0, color="k", lw=0.6)
    ax[3].axvline(K_REP, color="tab:purple", lw=1.2, label=f"anchor K_REP={K_REP} (=destruction level)")
    ax[3].set_xlabel("K_REP (Wall corruption of the wiring)"); ax[3].set_ylabel("post-Wall a_rep")
    ax[3].set_title("survival vs Wall-corruption strength (sign-flip = still frustrated; |a_rep|->0 = destroyed)")
    ax[3].legend(fontsize=8); ax[3].grid(alpha=0.3)
    fig.tight_layout()
    png = OUT / "k_frust_wall_tower_r2.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
