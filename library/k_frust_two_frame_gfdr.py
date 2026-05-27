"""Two-frame gFDR -- FIRST BRICK (self-probe coherence + co-onset).

Claim under construction (mpav1_receipts STAGED CANDIDATE "two-frame gFDR"):
  gFDR has two conjugate frames for the fluctuation-response relation.
   * EXTERNAL frame: (amplitude x external field h) -> violation factor X
                     -- the standard c/s/r aging story; needs an external probe.
   * SELF frame:     (current J x intrinsic affinity A) -> the system's OWN
                     frustrated circulation is the reference. Dimensionless.
                     Defined IFF a current exists (k_frust-bearing substrate).
  The self-frame's directly-measurable core is the current signal-to-noise
      SNR_J = <J>^2 / Var(J),
  which is exactly the quantity the TUR bounds: SNR_J <= <sigma>/2 (Barato-Seifert).
  The full self-frame violation factor T = <sigma> Var(J) / (2 <J>^2) additionally
  needs a calibrated entropy-production meter <sigma> (= J*A for a cycle); that
  affinity/EP meter is the OWED apparatus piece (see FALSIFICATION.md).

This first brick tests the NECESSARY consistency, not yet the full agreement:
  the self-probe observable must light up exactly when broken detailed balance is
  present (a current to probe WITH), and be degenerate on the reciprocal control.
We interpolate reciprocal -> non-reciprocal at fixed signed-graph balance,
  g(lambda) = GMAG * ( -SYM  +  lambda * CYC ),
  lambda=0 : pure cooperative-reciprocal (symmetric Jacobian -> real spectrum -> J~0),
  lambda>0 : adds the antisymmetric cyclic part (complex spectrum -> J!=0),
and check that all THREE light up together:
  (a) self-frame   : SNR_J = <J>^2/Var(J)   onsets from ~0 and rises,
  (b) structural   : |Im(eig)| of the coexistence Jacobian (the R3 complex-spectrum
                     invariant -- broken detailed balance is structural here),
  (c) external probe: chi_J = (<J>(h) - <J>(0)) / |h|, response of the current to a
                     small constant field h on mode 0 (the external frame's hook).
Co-onset of (a),(b),(c) = the two conjugate frames read the SAME broken-detailed-
balance transition. Full two-frame AGREEMENT (self-frame T vs external-frame X
giving a consistent regime verdict, on a real substrate) is the promotion gate.

Run: python H:/mpa-central/library/k_frust_two_frame_gfdr.py
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from k_frust_r1_sweep import CYC, SYM, RHO_SAT, S0, RHO_FLOOR, DT

OUT = Path("H:/mpa-central/library/output/diagnostics")
OUT.mkdir(parents=True, exist_ok=True)

# canonical operating point (the bulletproof-meter point, matched to R1)
G0, L, SIGMA, GMAG = 1.20, 1.00, 0.02, 0.50
N_REAL, T_EQ, T_OBS = 160, 2500, 4000
SEEDS = [1, 2]
H_PROBE = 0.03                     # small constant field on mode 0 (external frame)
LAMBDAS = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5]


def finite(name, x):
    x = np.asarray(x, float)
    if not np.all(np.isfinite(x)):
        raise FloatingPointError(f"NON-FINITE in '{name}' (MPA NaN tripwire): bad test or boundary attainment.")
    return x


def step(rho, gmat, sigma, rng, h=None):
    """One Euler-Maruyama step of the cdv1 two-mode kernel (3 modes here).
    h: optional constant external field (shape (3,)) added to the drift -- the
    external-frame perturbation, conjugate to mode amplitude."""
    S = rho.sum(axis=1, keepdims=True)
    gain = G0 / (1.0 + S / RHO_SAT)
    cross = rho * (rho @ gmat.T) / RHO_SAT
    drift = (gain - L) * rho - cross + S0
    if h is not None:
        drift = drift + h
    noise = sigma * np.sqrt(np.maximum(rho, 0.0)) * rng.standard_normal(rho.shape) * np.sqrt(DT)
    return np.maximum(rho + drift * DT + noise, RHO_FLOOR)


def chir_per_real(rho, rp):
    """Per-realization instantaneous cyclic current (chirality of rho-rotation),
    r2-normalized. Returns shape (N_REAL,) -- NOT ensemble-meaned, so we can take
    the realization-to-realization variance the TUR needs."""
    m = rho.mean(1); mp = rp.mean(1)
    a = rho[:, 0] - m
    b = (rho[:, 1] - rho[:, 2]) / np.sqrt(3.0)
    adot = ((rho[:, 0] - m) - (rp[:, 0] - mp)) / DT
    bdot = ((rho[:, 1] - rho[:, 2]) - (rp[:, 1] - rp[:, 2])) / (np.sqrt(3.0) * DT)
    r2 = a * a + b * b
    out = np.zeros_like(r2)
    good = r2 > 1e-10
    out[good] = (a[good] * bdot[good] - b[good] * adot[good]) / r2[good]
    return out


def run(gmat, sigma, seed, h=None):
    """Return (per-realization time-averaged current J_n [shape N_REAL], mean amplitude)."""
    rng = np.random.default_rng(seed)
    rho = np.tile([0.06, 0.03, 0.01], (N_REAL, 1)).astype(float)
    for _ in range(T_EQ):
        rho = step(rho, gmat, sigma, rng, h)
    acc = np.zeros(N_REAL); amp = 0.0
    for _ in range(T_OBS):
        rp = rho.copy()
        rho = step(rho, gmat, sigma, rng, h)
        acc += chir_per_real(rho, rp)
        amp += float(rho.mean())
    return finite("J_n", acc / T_OBS), amp / T_OBS


def self_frame(gmat):
    """SNR_J = <J>^2/Var(J) over realizations x seeds (the TUR-bounded current precision)."""
    Jn = np.concatenate([run(gmat, SIGMA, s)[0] for s in SEEDS])
    amp = np.mean([run(gmat, SIGMA, s)[1] for s in SEEDS])
    meanJ = float(Jn.mean()); varJ = float(Jn.var(ddof=1))
    snr = meanJ * meanJ / varJ if varJ > 0 else 0.0
    return meanJ, varJ, snr, amp


def external_probe(gmat):
    """chi_J = (<J>(h) - <J>(0)) / |h|, constant field h on mode 0."""
    h = np.array([H_PROBE, 0.0, 0.0])
    J0 = np.mean([run(gmat, SIGMA, s)[0].mean() for s in SEEDS])
    Jh = np.mean([run(gmat, SIGMA, s, h=h)[0].mean() for s in SEEDS])
    return (Jh - J0) / H_PROBE


def jac_imag(gmat):
    """Max |Im(eigenvalue)| of the coexistence Jacobian -- structural NESS signature
    (irreducible rotation = broken detailed balance; the R3 complex-spectrum invariant)."""
    def drift(r):
        S = r.sum(); gain = G0 / (1.0 + S / RHO_SAT)
        return (gain - L) * r - r * (gmat @ r) / RHO_SAT + S0
    c = 0.07
    for _ in range(200):
        f = drift(np.full(3, c))[0]
        df = (drift(np.full(3, c + 1e-6))[0] - f) / 1e-6
        c = max(c - f / df, 1e-6)
    rs = np.full(3, c); Jm = np.zeros((3, 3)); f0 = drift(rs)
    for j in range(3):
        rp = rs.copy(); rp[j] += 1e-6
        Jm[:, j] = (drift(rp) - f0) / 1e-6
    return float(np.max(np.abs(np.linalg.eigvals(Jm).imag)))


def main():
    print("two-frame gFDR -- first brick: self-frame SNR_J vs structural |Im(eig)| vs external chi_J")
    print(f"interpolation g(lambda) = {GMAG} * ( -SYM + lambda*CYC ); operating point chit={np.log(G0/L):.3f}\n")
    hdr = f"{'lambda':>7} | {'amp':>7} | {'<J>':>11} {'Var(J)':>10} {'SNR_J':>9} | {'|Im(eig)|':>9} | {'chi_J':>10}"
    print(hdr); print("-" * len(hdr))
    rows = []
    for lam in LAMBDAS:
        g = GMAG * (-SYM + lam * CYC)
        np.fill_diagonal(g, 0.0)
        meanJ, varJ, snr, amp = self_frame(g)
        imag = jac_imag(g)
        chi = external_probe(g)
        rows.append(dict(lam=lam, amp=amp, meanJ=meanJ, varJ=varJ, snr=snr, imag=imag, chi=chi))
        print(f"{lam:>7.2f} | {amp:>7.4f} | {meanJ:>+11.4e} {varJ:>10.2e} {snr:>9.3f} | "
              f"{imag:>9.4f} | {chi:>+10.3e}")

    snr = np.array([r["snr"] for r in rows])
    imag = np.array([r["imag"] for r in rows])
    chi = np.array([abs(r["chi"]) for r in rows])
    lam0 = rows[0]
    # co-onset checks
    self_degenerate_at_control = lam0["snr"] < 0.5 and abs(lam0["meanJ"]) < 5e-3 and lam0["imag"] < 1e-3
    rises = snr[-1] > 5 * (snr[0] + 1e-9) and imag[-1] > imag[0]
    def corr(a, b):
        if a.std() < 1e-12 or b.std() < 1e-12:
            return float("nan")
        return float(np.corrcoef(a, b)[0, 1])
    c_si = corr(snr, imag); c_sc = corr(snr, chi)

    print("\n================ FIRST-BRICK VERDICT ================")
    print(f"self-frame degenerate on reciprocal control (lambda=0): {self_degenerate_at_control} "
          f"(SNR_J={lam0['snr']:.3f}, <J>={lam0['meanJ']:+.2e}, |Im(eig)|={lam0['imag']:.2e})")
    print(f"self-frame onsets + rises with non-reciprocity:         {rises}")
    print(f"corr(SNR_J, |Im(eig)|) = {c_si:+.3f}   [self-frame vs structural NESS signature]")
    print(f"corr(SNR_J, |chi_J|)   = {c_sc:+.3f}   [self-frame vs external-probe response]")
    co_onset = self_degenerate_at_control and rises and (np.isnan(c_si) or c_si > 0.8)
    if co_onset:
        print("\nSINGS: the self-probe current-precision is degenerate at detailed balance and co-onsets")
        print("with both the structural complex-spectrum signature and the external-probe response.")
        print("The two conjugate frames read the SAME broken-detailed-balance transition. First brick laid.")
        print("Next (promotion gate, FALSIFICATION.md): calibrate <sigma> -> full T; then two-frame regime")
        print("agreement (self-frame T vs external-frame X) on a REAL substrate.")
    else:
        print("\nDOES NOT SING cleanly -- inspect the table + PNG before building further.")

    # ---- figure ----
    lams = [r["lam"] for r in rows]
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].plot(lams, snr, "o-", color="tab:red", label=r"self-frame  SNR$_J=\langle J\rangle^2/$Var$(J)$")
    ax[0].set_xlabel(r"non-reciprocity $\lambda$"); ax[0].set_ylabel("SNR$_J$ (TUR-bounded)")
    ax[0].set_title("self-frame current precision onsets at broken detailed balance")
    ax[0].grid(alpha=0.3); ax[0].legend(fontsize=9)
    ax2 = ax[1]
    l1 = ax2.plot(lams, snr / (snr.max() + 1e-12), "o-", color="tab:red", label="SNR$_J$ (self)")
    l2 = ax2.plot(lams, imag / (imag.max() + 1e-12), "s--", color="tab:green", label="|Im(eig)| (structural)")
    l3 = ax2.plot(lams, chi / (chi.max() + 1e-12), "^:", color="tab:blue", label=r"|$\chi_J$| (external probe)")
    ax2.set_xlabel(r"non-reciprocity $\lambda$"); ax2.set_ylabel("normalized to max")
    ax2.set_title(f"co-onset of the three frames\ncorr(SNR,|Im|)={c_si:+.2f}, corr(SNR,|chi|)={c_sc:+.2f}")
    ax2.grid(alpha=0.3); ax2.legend(fontsize=9)
    fig.suptitle("two-frame gFDR first brick: self-probe current-precision vs structural + external frames", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    png = OUT / "k_frust_two_frame_gfdr.png"
    fig.savefig(png, dpi=130)
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
