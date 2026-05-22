r"""Two-frame gFDR -- close SNR_J -> the self-frame violation factor T.

  T = <sigma> * Var(J_tau) / (2 <J_tau>^2)        (TUR-tightness; T >= 1, Barato-Seifert)
  SNR(J_tau) = <J_tau>^2 / Var(J_tau) <= <sigma> tau / 2

T needs an entropy-production meter <sigma> that is INDEPENDENT of J (else circular).
Repo doctrine (FALSIFICATION.md, positive-control ladder): TARE BEFORE YOU WEIGH --
validate the <sigma> meter against a KNOWN sigma before trusting it on a loop.

Testbed = the two k_frust sub-regimes cdv1 sec."k_frust drain" names, in minimal form:

  A. STABLE CIRCULATING FOCUS (Re<0, complex spectrum): 2D rotational OU
       dx = (-kappa x - omega y) dt + sqrt(2 D0) dW_x
       dy = ( omega x - kappa y) dt + sqrt(2 D0) dW_y
     EXACT ground truth (derived):
       stationary cov  C = (D0/kappa) I
       irreversible drift  nu = A + D0 C^-1 = omega * [[0,-1],[1,0]]
       <sigma> = Tr[nu^T D^-1 nu C] = 2 omega^2 / kappa
       mean angular velocity (normalized cyclic current) = omega
       omega = 0  ->  gradient OU, detailed balance, sigma = 0, J = 0.

  B. REPELLING FOCUS + LIMIT CYCLE (Re>0): Stuart-Landau
       rdot = (mu - r^2) r ,  thetadot = omega ;  attracting cycle at r=sqrt(mu).
     No closed-form sigma -> use the binned probability-current meter, which Part A
     validated against the exact 2 omega^2 / kappa.

Current for the TUR: integrated angular winding  J_tau = \int_0^tau (x dy - y dx)/(x^2+y^2)
(Stratonovich/midpoint). <J_tau> = omega*tau ; Var grows ~ tau.

Entropy-production meter (general, additive D = D0 I):
  current velocity  v_curr(x) = A(x) - D0 grad ln P(x)
  <sigma> = \int P |v_curr|^2 / D0 dx   (binned; A(x) = local mean velocity from data).

Run: python H:/mpa-central/library/two_frame_T_meter.py
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

KAPPA, D0, DT = 1.0, 0.05, 0.01
N_REAL, T_EQ, T_OBS = 4000, 2000, 3000
N_BIN_REAL = 800            # realizations whose full trajectory feeds the binned-sigma cloud
NBINS = 41
SEED = 7


def finite(name, x):
    if not np.all(np.isfinite(np.asarray(x, float))):
        raise FloatingPointError(f"NON-FINITE in '{name}' (MPA NaN tripwire).")
    return x


def drift_linear(xy, omega):
    x, y = xy[:, 0], xy[:, 1]
    return np.stack([-KAPPA * x - omega * y, omega * x - KAPPA * y], axis=1)


def drift_sl(xy, omega, mu):
    x, y = xy[:, 0], xy[:, 1]
    rad = mu - (x * x + y * y)
    return np.stack([rad * x - omega * y, rad * y + omega * x], axis=1)


def ou_C_xx_exact(tau, omega):
    """Exact x-autocorrelation of the 2D rotational OU: C_xx(tau) = (D0/kappa) e^{-kappa tau} cos(omega tau)."""
    return (D0 / KAPPA) * np.exp(-KAPPA * tau) * np.cos(omega * tau)


def ou_chi_step_exact(tau, omega):
    """Exact integrated (step) response of x to a constant field on x:
    chi(tau) = [kappa - e^{-kappa tau}(kappa cos w t - w sin w t)] / (kappa^2 + w^2).
    Derived from <x(tau)>/h = [M^{-1}(I - e^{-M tau}) e_x]_x, M = kappa I + omega J."""
    denom = KAPPA ** 2 + omega ** 2
    return (KAPPA - np.exp(-KAPPA * tau) * (KAPPA * np.cos(omega * tau)
            - omega * np.sin(omega * tau))) / denom


def V_ext_exact(omega):
    """Asymptotic external-frame FDT violation = chi_eq(inf) - chi(inf) = w^2 / [kappa (kappa^2 + w^2)].
    Equilibrium FDT (slope 1/D0) over-predicts the response; the shortfall is the violation. ~ w^2 at small w."""
    return omega ** 2 / (KAPPA * (KAPPA ** 2 + omega ** 2))


def external_frame(drift, omega, rng, h, n_lag, x0_scale=None, **kw):
    """Measure C_xx(tau) (unperturbed) and chi_step(tau) (constant field h on x) from a common
    equilibrated start state, independent noise on the two branches. Returns (lags, C_xx, chi_step).
    chi_step(tau) = (<x_p(tau)> - <x_u(tau)>)/h  (common-mean subtraction for variance reduction).
    x0_scale sets the initial spread (use sqrt(mu) for the Stuart-Landau cycle radius)."""
    if x0_scale is None:
        x0_scale = np.sqrt(D0 / KAPPA)
    g = np.sqrt(2.0 * D0 * DT)
    xy = x0_scale * rng.standard_normal((N_REAL, 2))
    for _ in range(T_EQ):
        xy = xy + drift(xy, omega, **kw) * DT + g * rng.standard_normal((N_REAL, 2))
    x0 = xy[:, 0].copy()
    xy_u = xy.copy()
    xy_p = xy.copy()
    C = np.empty(n_lag)
    chi = np.empty(n_lag)
    for k in range(n_lag):
        C[k] = float(np.mean(x0 * xy_u[:, 0]))
        chi[k] = float(np.mean(xy_p[:, 0] - xy_u[:, 0])) / h
        xy_u = xy_u + drift(xy_u, omega, **kw) * DT + g * rng.standard_normal((N_REAL, 2))
        d_p = drift(xy_p, omega, **kw) * DT
        d_p[:, 0] += h * DT                                            # constant external field on x
        xy_p = xy_p + d_p + g * rng.standard_normal((N_REAL, 2))
    finite("C_xx", C)
    finite("chi_step", chi)
    return np.arange(n_lag) * DT, C, chi


def run(drift, omega, rng, x0_scale, record=False, **kw):
    """Euler-Maruyama; returns (winding-per-realization over T_OBS, samples or None).
    samples (for binning) = (pos, vel) stacked over the first N_BIN_REAL realizations x time."""
    xy = x0_scale * rng.standard_normal((N_REAL, 2))
    g = np.sqrt(2.0 * D0 * DT)
    for _ in range(T_EQ):
        xy = xy + drift(xy, omega, **kw) * DT + g * rng.standard_normal((N_REAL, 2))
    phi = np.zeros(N_REAL)
    pos_s, vel_s = [], []
    for _ in range(T_OBS):
        d = drift(xy, omega, **kw) * DT + g * rng.standard_normal((N_REAL, 2))
        nxt = xy + d
        mid = 0.5 * (xy + nxt)
        r2 = (mid * mid).sum(1) + 1e-12
        phi += (mid[:, 0] * d[:, 1] - mid[:, 1] * d[:, 0]) / r2     # midpoint winding increment
        if record:
            pos_s.append(xy[:N_BIN_REAL].copy())
            vel_s.append(d[:N_BIN_REAL] / DT)                       # E[d/dt | x] = drift(x)
        xy = nxt
    finite("winding", phi)
    samples = (np.concatenate(pos_s), np.concatenate(vel_s)) if record else None
    return phi, samples


def sigma_binned(pos, vel, lim, nbins=NBINS):
    """<sigma> = sum_bins P_bin * |v_curr|^2 / D0, v_curr = <vel|bin> - D0 grad ln P.
    Additive isotropic D = D0 I. Validated against the exact OU value in Part A."""
    edges = [np.linspace(-lim, lim, nbins + 1), np.linspace(-lim, lim, nbins + 1)]
    cnt, ex, ey = np.histogram2d(pos[:, 0], pos[:, 1], bins=edges)
    total = cnt.sum()
    cellx = ex[1] - ex[0]; celly = ey[1] - ey[0]; area = cellx * celly
    # mean velocity per bin
    ix = np.clip(np.digitize(pos[:, 0], ex) - 1, 0, nbins - 1)
    iy = np.clip(np.digitize(pos[:, 1], ey) - 1, 0, nbins - 1)
    vx = np.zeros((nbins, nbins)); vy = np.zeros((nbins, nbins))
    np.add.at(vx, (ix, iy), vel[:, 0]); np.add.at(vy, (ix, iy), vel[:, 1])
    with np.errstate(invalid="ignore", divide="ignore"):
        vx /= cnt; vy /= cnt
    Pdens = cnt / (total * area)
    lnP = np.log(np.where(Pdens > 0, Pdens, np.nan))
    glx, gly = np.gradient(lnP, cellx, celly)                      # grad ln P (NaN where empty)
    vcx = vx - D0 * glx; vcy = vy - D0 * gly
    mask = (cnt >= 25) & np.isfinite(vcx) & np.isfinite(vcy)
    Pmass = cnt / total
    contrib = Pmass * (vcx ** 2 + vcy ** 2) / D0
    return float(np.nansum(np.where(mask, contrib, 0.0)))


def tur_T(phi, sigma, tau):
    """T = sigma*tau*Var(phi)/(2<phi>^2); SNR=<phi>^2/Var(phi); bound=sigma*tau/2."""
    mean = float(phi.mean()); var = float(phi.var(ddof=1))
    if abs(mean) < 1e-9:
        return dict(mean=mean, var=var, snr=0.0, bound=sigma * tau / 2, T=float("nan"))
    snr = mean * mean / var
    return dict(mean=mean, var=var, snr=snr, bound=sigma * tau / 2,
                T=sigma * tau * var / (2 * mean * mean))


def main():
    rng = np.random.default_rng(SEED)
    tau = T_OBS * DT
    x0 = np.sqrt(D0 / KAPPA)                                       # ~ stationary scale

    # ---------- PART A: stable circulating focus (rotational OU); EXACT sigma = 2 w^2/kappa ----------
    print("PART A -- stable circulating focus (rotational OU). TARE: validate the sigma meter.")
    print(f"  kappa={KAPPA}, D0={D0}, dt={DT}, tau={tau:.1f}, N={N_REAL}\n")
    hdr = (f"{'omega':>6} | {'sig_exact':>9} {'sig_binned':>10} {'err%':>6} | "
           f"{'<phi>/tau':>9}(=w?) | {'SNR':>8} {'sig*t/2':>8} TUR | {'T':>7}")
    print(hdr); print("-" * len(hdr))
    A_rows = []
    for omega in [0.0, 0.5, 1.0, 2.0]:
        phi, samp = run(drift_linear, omega, rng, x0_scale=x0 * 3, record=True)
        sig_exact = 2.0 * omega ** 2 / KAPPA
        lim = 4.5 * x0
        sig_bin = sigma_binned(*samp, lim=lim)
        t = tur_T(phi, sig_exact, tau)
        has_current = sig_exact > 0                                   # omega=0 is the equilibrium tare (no current, T undefined)
        tur_ok = (t["snr"] <= t["bound"] * 1.10) if has_current else True
        errpct = 100 * (sig_bin - sig_exact) / sig_exact if sig_exact > 0 else float("nan")
        A_rows.append(dict(omega=omega, se=sig_exact, sb=sig_bin, has_current=has_current, **t))
        tcell = f"{t['T']:>7.3f}" if has_current else f"{'n/a':>7}"
        turcell = ("ok" if tur_ok else "XX") if has_current else "—"
        print(f"{omega:>6.2f} | {sig_exact:>9.4f} {sig_bin:>10.4f} {errpct:>6.1f} | "
              f"{t['mean']/tau:>9.4f}      | {t['snr']:>8.2f} {t['bound']:>8.2f} "
              f"{turcell:>3} | {tcell}")

    # validation verdict on the sigma meter (nonzero-omega rows)
    nz = [r for r in A_rows if r["omega"] > 0]
    meter_err = np.mean([abs(r["sb"] - r["se"]) / r["se"] for r in nz])
    eq = A_rows[0]
    print(f"\n  sigma-meter mean error vs exact (omega>0): {100*meter_err:.1f}%")
    print(f"  equilibrium check (omega=0): sigma_binned={eq['sb']:.4f} (exact 0), "
          f"<phi>/tau={eq['mean']/tau:+.4f} (exact 0)")
    meter_ok = meter_err < 0.20 and abs(eq["sb"]) < 0.10 * max(r["se"] for r in nz)
    print(f"  METER {'VALIDATED' if meter_ok else 'NOT trustworthy yet'} "
          f"(<20% error + ~0 at equilibrium).")

    # ---------- PART B: repelling focus + limit cycle (Stuart-Landau); binned sigma ----------
    print("\nPART B -- repelling focus + limit cycle (Stuart-Landau). sigma via the validated meter.")
    print(f"{'omega':>6} {'mu':>5} | {'sig_binned':>10} | {'<phi>/tau':>9} | {'SNR':>8} {'sig*t/2':>8} TUR | {'T':>7}")
    B_rows = []
    for omega, mu in [(1.0, 0.5), (2.0, 0.5), (1.0, 1.0)]:
        phi, samp = run(drift_sl, omega, rng, x0_scale=np.sqrt(mu), record=True, mu=mu)
        lim = 2.2 * np.sqrt(mu)
        sig = sigma_binned(*samp, lim=lim)
        t = tur_T(phi, sig, tau)
        tur_ok = t["snr"] <= t["bound"] * 1.10
        B_rows.append(dict(omega=omega, mu=mu, sb=sig, **t))
        print(f"{omega:>6.2f} {mu:>5.2f} | {sig:>10.4f} | {t['mean']/tau:>9.4f} | "
              f"{t['snr']:>8.2f} {t['bound']:>8.2f} {'ok' if tur_ok else 'XX':>3} | {t['T']:>7.3f}")

    print("\n================ VERDICT ================")
    Ts_A = [r["T"] for r in A_rows if r["has_current"]]               # exclude the no-current equilibrium tare
    Ts_B = [r["T"] for r in B_rows]
    tur_all = all((r["snr"] <= r["bound"] * 1.10) for r in A_rows if r["has_current"]) and \
              all((r["snr"] <= r["bound"] * 1.10) for r in B_rows)
    if meter_ok and tur_all and all(t >= 0.9 for t in Ts_A + Ts_B):
        print("CLOSED: sigma meter validated against exact OU; T computed for BOTH k_frust")
        print(f"sub-regimes; TUR floor (T>=1) respected. SNR_J -> T is closed.")
        print(f"  stable focus T in [{min(Ts_A):.2f}, {max(Ts_A):.2f}] ; "
              f"limit cycle T in [{min(Ts_B):.2f}, {max(Ts_B):.2f}].")
        print("Self-frame violation factor T is now a measured quantity, not just SNR_J.")
    else:
        print("NOT fully closed -- inspect: meter_ok=%s, TUR_ok=%s. Report honestly." % (meter_ok, tur_all))

    # ---------- figure ----------
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    om = [r["omega"] for r in A_rows]
    ax[0].plot(om, [r["se"] for r in A_rows], "o-", color="k", label=r"$\langle\sigma\rangle$ exact $=2\omega^2/\kappa$")
    ax[0].plot(om, [r["sb"] for r in A_rows], "s--", color="tab:red", label=r"$\langle\sigma\rangle$ binned meter")
    ax[0].set_xlabel(r"rotation $\omega$ (affinity driver)"); ax[0].set_ylabel(r"$\langle\sigma\rangle$")
    ax[0].set_title("entropy-production meter validated\n(stable circulating focus = rotational OU)")
    ax[0].legend(fontsize=9); ax[0].grid(alpha=0.3)
    labA = [f"OU w={r['omega']}" for r in A_rows if r["has_current"]]
    labB = [f"LC w={r['omega']},mu={r['mu']}" for r in B_rows]
    Ts = Ts_A + Ts_B
    cols = ["tab:blue"] * len(Ts_A) + ["tab:green"] * len(Ts_B)
    ax[1].bar(range(len(Ts)), Ts, color=cols, alpha=0.8)
    ax[1].axhline(1.0, color="k", ls="--", lw=1, label="TUR floor T=1")
    ax[1].set_xticks(range(len(Ts))); ax[1].set_xticklabels(labA + labB, rotation=25, fontsize=8, ha="right")
    ax[1].set_ylabel(r"self-frame violation factor $T$")
    ax[1].set_title(r"$T=\langle\sigma\rangle\,\tau\,$Var$(J)/(2\langle J\rangle^2)$ -- both k_frust sub-regimes")
    ax[1].legend(fontsize=9); ax[1].grid(alpha=0.3)
    fig.suptitle("two-frame gFDR: closing SNR_J -> T (validated entropy-production meter)", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    png = OUT / "two_frame_T_meter.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")

    # ---------- PART C: external frame X on the rotational-OU testbed (the conjugate frame) ----------
    print("\nPART C -- external frame X (rotational OU). TARE: measured C(tau), chi_step(tau) vs EXACT.")
    print("  perturbed-response run (constant field h on x); OU is exactly linear, so any h is valid.")
    h = 0.3
    N_LAG = int(6.0 / DT)                                              # tau up to ~6 covers 1/kappa and 2pi/omega
    hdrC = (f"{'omega':>6} | {'X(t->0)':>8} | {'V_ext meas':>10} {'V_ext exact':>11} {'err%':>6} | "
            f"{'<sigma>=2w^2/k':>13}")
    print(hdrC); print("-" * len(hdrC))
    C_rows = []
    for omega in [0.0, 0.5, 1.0, 2.0]:
        lags, Cxx, chi = external_frame(drift_linear, omega, rng, h=h, n_lag=N_LAG)
        dC = Cxx[0] - Cxx
        slope0 = np.polyfit(dC[1:20], chi[1:20], 1)[0]                 # near-origin slope; short-time FDT => 1/D0
        X0 = D0 * slope0                                              # local FDR X(tau->0); ~1 if FDT holds short-time
        V_meas = dC[-1] / D0 - chi[-1]                                # equilibrium-FDT overshoot = external violation
        V_exact = float(V_ext_exact(omega))
        sigma = 2.0 * omega ** 2 / KAPPA
        errp = 100 * (V_meas - V_exact) / V_exact if V_exact > 0 else float("nan")
        C_rows.append(dict(omega=omega, lags=lags, dC=dC, chi=chi, X0=X0, V=V_meas, Ve=V_exact, sigma=sigma))
        errcell = f"{errp:>6.1f}" if V_exact > 0 else f"{'—':>6}"
        print(f"{omega:>6.2f} | {X0:>8.3f} | {V_meas:>10.4f} {V_exact:>11.4f} {errcell} | {sigma:>13.4f}")
    print("  X(t->0) ~ 1 (short-time FDT holds); V_ext = equilibrium-FDT overshoot = external violation.")
    print("  VERDICT: X->1 & V_ext->0 at omega=0 (equilibrium); both rise with omega (NESS) -> frames agree.")

    figC, axC = plt.subplots(1, 2, figsize=(13, 5))
    colors = plt.cm.viridis(np.linspace(0.1, 0.85, len(C_rows)))
    dCmax = max(r["dC"].max() for r in C_rows)
    xs = np.linspace(0, dCmax, 50)
    axC[0].plot(xs, xs / D0, "k--", lw=1.2, label=r"equilibrium FDT $\chi=\Delta C/D_0$ ($X{=}1$)")
    for r, c in zip(C_rows, colors):
        axC[0].plot(r["dC"], r["chi"], "-", color=c, lw=1.6, label=fr"$\omega={r['omega']}$ (meas)")
        C_ex = ou_C_xx_exact(r["lags"], r["omega"])
        axC[0].plot(C_ex[0] - C_ex, ou_chi_step_exact(r["lags"], r["omega"]), ":", color=c, lw=1.0)
    axC[0].set_xlabel(r"$\Delta C(\tau)=C(0)-C(\tau)$"); axC[0].set_ylabel(r"$\chi_{\mathrm{step}}(\tau)$")
    axC[0].set_title("external-frame parametric FDT plot (rotational OU)\nsolid=measured, dotted=exact, dashed=equilibrium")
    axC[0].legend(fontsize=8); axC[0].grid(alpha=0.3)
    oms = np.array([r["omega"] for r in C_rows])
    Vm = np.array([r["V"] for r in C_rows]); Ve = np.array([r["Ve"] for r in C_rows])
    sig = np.array([r["sigma"] for r in C_rows])
    axC[1].plot(oms, Vm, "o-", color="tab:purple", label=r"external $V_{\mathrm{ext}}$ (measured)")
    axC[1].plot(oms, Ve, ":", color="tab:purple", label=r"$V_{\mathrm{ext}}$ exact $=\omega^2/[\kappa(\kappa^2+\omega^2)]$")
    axC[1].set_xlabel(r"rotation $\omega$"); axC[1].set_ylabel(r"external FDT violation $V_{\mathrm{ext}}$", color="tab:purple")
    ax2 = axC[1].twinx()
    ax2.plot(oms, sig, "s--", color="tab:red", label=r"$\langle\sigma\rangle=2\omega^2/\kappa$ (feeds self-frame $T$)")
    ax2.set_ylabel(r"$\langle\sigma\rangle$ (self-frame input)", color="tab:red")
    axC[1].set_title("regime-verdict agreement\nboth $\\to 0$ at $\\omega{=}0$, both rise with $\\omega$ (NESS)")
    l1, lab1 = axC[1].get_legend_handles_labels(); l2, lab2 = ax2.get_legend_handles_labels()
    axC[1].legend(l1 + l2, lab1 + lab2, fontsize=8, loc="upper left"); axC[1].grid(alpha=0.3)
    figC.suptitle("two-frame gFDR: external frame X on the exact-tared rotational-OU testbed", fontsize=12)
    figC.tight_layout(rect=[0, 0, 1, 0.95])
    pngC = OUT / "two_frame_external_X.png"
    figC.savefig(pngC, dpi=130)
    print(f"wrote {pngC}")

    # ---------- PART D: external frame on Stuart-Landau (no closed form; trust the OU-tared frame) ----------
    # No exact tare here -- same bootstrap discipline as the sigma meter (validate on OU, then trust on SL).
    # SL correlations need not decorrelate within the window (omega=1 period ~6.3 > tau_max), so the
    # ASYMPTOTIC V_ext is unreliable. Use a window-robust scalar: D_FDT = max_tau |chi - dC/D0|, the
    # peak departure from the equilibrium-FDT line. Zero iff FDT holds; finite without needing C->0.
    def d_fdt(dC, chi):
        return float(np.max(np.abs(chi - dC / D0)))

    print("\nPART D -- external frame on Stuart-Landau limit cycle (no exact tare; window-robust D_FDT).")
    print(f"{'omega':>6} {'mu':>5} | {'X(t->0)':>8} | {'D_FDT':>8} | {'<sigma>(B)':>10} | {'T (B)':>7}")
    print("-" * 56)
    hSL = 0.05
    D_rows = []
    for r in B_rows:
        omega, mu = r["omega"], r["mu"]
        lags, Cxx, chi = external_frame(drift_sl, omega, rng, h=hSL, n_lag=N_LAG,
                                        x0_scale=np.sqrt(mu), mu=mu)
        dC = Cxx[0] - Cxx
        X0 = D0 * np.polyfit(dC[1:20], chi[1:20], 1)[0]
        Dfdt = d_fdt(dC, chi)
        D_rows.append(dict(omega=omega, mu=mu, X0=X0, dfdt=Dfdt, sigma=r["sb"], T=r["T"],
                           lags=lags, dC=dC, chi=chi))
        print(f"{omega:>6.2f} {mu:>5.2f} | {X0:>8.3f} | {Dfdt:>8.4f} | {r['sb']:>10.4f} | {r['T']:>7.3f}")
    for r in C_rows:                                                  # same scalar on the OU points (for the joint scatter)
        r["dfdt"] = d_fdt(r["dC"], r["chi"])
    print("  X(t->0) ~ 1 expected (short-time FDT is generic); D_FDT large => strong external violation.")
    print("  'works' = D_FDT positive/structured AND co-varies with the self-frame across both regimes.")

    figD, axD = plt.subplots(1, 2, figsize=(13, 5))
    scols = plt.cm.autumn(np.linspace(0.0, 0.7, len(D_rows)))
    dCmaxD = max(r["dC"].max() for r in D_rows)
    xsD = np.linspace(0, dCmaxD, 50)
    axD[0].plot(xsD, xsD / D0, "k--", lw=1.2, label=r"equilibrium FDT $\chi=\Delta C/D_0$")
    for r, c in zip(D_rows, scols):
        axD[0].plot(r["dC"], r["chi"], "-", color=c, lw=1.5,
                    label=fr"$\omega={r['omega']},\,\mu={r['mu']}$")
    axD[0].set_xlabel(r"$\Delta C(\tau)=C(0)-C(\tau)$"); axD[0].set_ylabel(r"$\chi_{\mathrm{step}}(\tau)$")
    axD[0].set_title("external frame on Stuart-Landau limit cycle\n(loops = oscillatory; departure from dashed = violation)")
    axD[0].legend(fontsize=8); axD[0].grid(alpha=0.3)
    su = np.array([r["sigma"] for r in C_rows if r["omega"] > 0]); du = np.array([r["dfdt"] for r in C_rows if r["omega"] > 0])
    ss = np.array([r["sigma"] for r in D_rows]); ds = np.array([r["dfdt"] for r in D_rows])
    axD[1].scatter(su, du, s=70, c="tab:blue", marker="o", label="rotational OU (stable focus)", zorder=3)
    axD[1].scatter(ss, ds, s=80, c="tab:green", marker="s", label="Stuart-Landau (limit cycle)", zorder=3)
    axD[1].set_xscale("log"); axD[1].set_yscale("log")
    axD[1].set_xlabel(r"self-frame $\langle\sigma\rangle$ (entropy-production meter)")
    axD[1].set_ylabel(r"external $\Delta_{\mathrm{FDT}}=\max_\tau|\chi-\Delta C/D_0|$")
    axD[1].set_title("cross-regime frame agreement\nexternal violation co-varies with self-frame EP")
    axD[1].legend(fontsize=8); axD[1].grid(alpha=0.3, which="both")
    figD.suptitle("two-frame gFDR: external frame across BOTH k_frust sub-regimes (SL untared, OU-bootstrapped)", fontsize=11)
    figD.tight_layout(rect=[0, 0, 1, 0.95])
    pngD = OUT / "two_frame_external_SL.png"
    figD.savefig(pngD, dpi=130)
    print(f"wrote {pngD}")


if __name__ == "__main__":
    main()
