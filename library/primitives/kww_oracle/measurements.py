"""KWW oracle — CONTROL primitive (rung 5: full 5-vector).

A genuine two-timescale relaxation built as a SUM of independent OU modes.
A non-negative spectrum of exponential modes reproduces a stretched
(Kohlrausch–Williams–Watts) alpha-relaxation; a single fast mode carries
the beta-relaxation. Each mode gets its own FDT-violation drift, so the
substrate realizes a prescribed (q_EA, tau_alpha, beta_KWW, tau_beta, X):

    C(tau) = (1-q_EA)*exp(-tau/tau_beta) + q_EA*exp(-(tau/tau_alpha)^beta_KWW)
    chi(tau) = dC_beta(tau) + X*dC_alpha(tau)

The beta-relaxation respects FDT (X=1); the alpha-relaxation is violated at
ratio X. With a decade+ of timescale separation (tau_beta << tau_alpha) this
reproduces the generator's piecewise FDT form (gfdr_model.
generate_kww_glass_locus): FDT slope 1 until dC reaches 1-q_EA, then slope X.

Unlike two_temp_ou (pure exponential C — only X is identifiable), this
substrate's C is genuinely two-timescale, so the inversion's full 5-vector
(q_EA, tau_alpha, beta_KWW, tau_beta) is non-degenerate. This is the rung
that proves identifiability, not just X-recovery.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Iterator

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.protocol import stream_fdr
from _shared.runtime import ensemble_C_chi  # noqa: F401

XDOT_KINDS = ("velocity", "position-relative")
EMA_IN_PHASE_A = {"velocity": True, "position-relative": False}

# Mode-spectrum resolution (validated: max |mode-sum - KWW| < 0.025 over the
# sampled lag range even at beta=0.4; ~0.004 at beta=0.6 — below the ladder's
# ±0.03–0.09 resolution floor).
N_ALPHA_MODES = 48
ALPHA_SPAN_DECADES = 3.0


def build_kww_modes(q_EA: float, tau_alpha: float, beta_KWW: float,
                    tau_beta: float, X: float):
    """Mode spectrum realizing the prescribed two-timescale KWW + FDT-violation.

    Returns (tau_i, w_i, X_i) arrays over n_modes = N_ALPHA_MODES + 1. The
    fast beta mode is index 0 (weight 1-q_EA, X_i=1); the rest are the alpha
    spectrum (total weight q_EA, X_i=X). Each mode is an independent OU process
    of stationary variance w_i; the observable is their sum (variance Σw_i=1).
    """
    from scipy.optimize import nnls

    # Alpha: non-negative sum of exponentials matching exp(-(tau/tau_alpha)^beta).
    tau_grid = np.geomspace(
        tau_alpha * 10 ** (-ALPHA_SPAN_DECADES),
        tau_alpha * 10 ** (ALPHA_SPAN_DECADES),
        N_ALPHA_MODES,
    )
    tau_fit = np.geomspace(1e-3 * tau_alpha, 50 * tau_alpha, 400)
    A = np.exp(-tau_fit[:, None] / tau_grid[None, :])
    target = np.exp(-(tau_fit / tau_alpha) ** beta_KWW)
    v, _ = nnls(A, target)
    if v.sum() <= 0:
        raise ValueError("degenerate alpha spectrum (nnls returned all zeros)")
    v = v / v.sum()  # enforce alpha autocorrelation = 1 at tau=0

    tau_i = np.concatenate([[tau_beta], tau_grid])
    w_i = np.concatenate([[1.0 - q_EA], q_EA * v])
    X_i = np.concatenate([[1.0], np.full(N_ALPHA_MODES, float(X))])
    return tau_i, w_i, X_i


def kww_C_chi(tau, q_EA, tau_alpha, beta_KWW, tau_beta, X):
    """Substrate ground-truth C(tau), chi(tau) from the actual mode spectrum
    (the honest 'red' curve — the substrate's true correlator, which the mode
    sum reproduces to within the NNLS tolerance above)."""
    tau = np.asarray(tau, dtype=float)
    tau_i, w_i, X_i = build_kww_modes(q_EA, tau_alpha, beta_KWW, tau_beta, X)
    decay = np.exp(-tau[:, None] / tau_i[None, :])  # (n_tau, n_modes)
    C = decay @ w_i
    chi = (1.0 - decay) @ (w_i * X_i)
    return C, chi


def _init_state(q_EA, tau_alpha, beta_KWW, tau_beta, X):
    tau_i, w_i, X_i = build_kww_modes(q_EA, tau_alpha, beta_KWW, tau_beta, X)
    a = np.exp(-1.0 / tau_i)                       # (n_modes,)
    sig = np.sqrt(np.maximum(0.0, w_i * (1.0 - a * a)))
    sqrt_w = np.sqrt(np.maximum(0.0, w_i))

    def factory(rng: np.random.Generator, n_real: int) -> dict:
        m = rng.standard_normal((n_real, a.size)) * sqrt_w  # stationary, var w_i
        s = m.sum(axis=1, keepdims=True)
        return {
            "modes_unp": m.copy(), "modes_per": m.copy(),
            "modes_unp_prev": m.copy(), "modes_per_prev": m.copy(),
            "unp": s.copy(), "per": s.copy(),
            "unp_prev": s.copy(), "per_prev": s.copy(),
            "a": a, "w": w_i, "Xvec": X_i, "sig": sig,
        }
    return factory


def _advance(state: dict, h_extra_per: float, rng: np.random.Generator):
    a = state["a"]; sig = state["sig"]
    n_real = state["modes_unp"].shape[0]
    xi = rng.standard_normal((n_real, a.size)) * sig
    # Per-mode drift realizing chi_i(tau) = w_i * X_i * (1 - a_i^tau):
    #   b_i = w_i * X_i * h * (1 - a_i).
    b = state["w"] * state["Xvec"] * float(h_extra_per) * (1.0 - a)
    state["modes_unp_prev"] = state["modes_unp"].copy()
    state["modes_per_prev"] = state["modes_per"].copy()
    state["modes_unp"] = a * state["modes_unp"] + xi
    state["modes_per"] = a * state["modes_per"] + xi + b
    state["unp_prev"] = state["modes_unp_prev"].sum(axis=1, keepdims=True)
    state["per_prev"] = state["modes_per_prev"].sum(axis=1, keepdims=True)
    state["unp"] = state["modes_unp"].sum(axis=1, keepdims=True)
    state["per"] = state["modes_per"].sum(axis=1, keepdims=True)


def _xdot(state: dict, snap_for_xdot: dict | None, xdot_kind: str):
    if xdot_kind == "position-relative":
        ref = snap_for_xdot["unp_snap"]
        return state["unp"] - ref, state["per"] - ref
    return state["unp"] - state["unp_prev"], state["per"] - state["per_prev"]


def _raw_C_chi(state: dict, snap_at_tw: dict, h_field: float):
    return ensemble_C_chi(state["unp"], snap_at_tw["unp_snap"], state["per"], h_field)


def _fork(state: dict):
    state["modes_per"] = state["modes_unp"].copy()
    state["modes_per_prev"] = state["modes_unp_prev"].copy()
    state["per"] = state["unp"].copy()
    state["per_prev"] = state["unp_prev"].copy()


def _snapshot(state: dict) -> dict:
    return {"unp_snap": state["unp"].copy()}


def multi_window_fdr_iter(q_EA, tau_alpha, beta_KWW, tau_beta, X,
                          t_w, t_obs, tau_windows, h_field,
                          n_realizations, seed, n_sample_times,
                          progress_every=0, xdot_kind="velocity") -> Iterator[dict]:
    return stream_fdr(
        substrate="kww_oracle",
        op_label=(f"qEA{q_EA:g}_ta{tau_alpha:g}_b{beta_KWW:g}"
                  f"_tb{tau_beta:g}_X{X:g}"),
        op_params={
            "q_EA": float(q_EA), "tau_alpha": float(tau_alpha),
            "beta_KWW": float(beta_KWW), "tau_beta": float(tau_beta),
            "X": float(X), "n_modes": int(N_ALPHA_MODES + 1),
        },
        t_w=t_w, t_obs=t_obs, tau_windows=tau_windows, h_field=h_field,
        n_realizations=n_realizations, seed=seed,
        n_sample_times=n_sample_times, xdot_kind=xdot_kind,
        xdot_kinds_allowed=XDOT_KINDS, ema_in_phase_a=EMA_IN_PHASE_A,
        init_state=_init_state(q_EA, tau_alpha, beta_KWW, tau_beta, X),
        advance_one_sweep=_advance,
        xdot_field=_xdot, raw_C_chi=_raw_C_chi,
        fork_paired_branch=_fork, snapshot_state=_snapshot,
    )
