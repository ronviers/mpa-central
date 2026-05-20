"""Heston stochastic-volatility + Poisson-jump streaming primitive.

State per replica: (log_S, V) plus tracked V floor at 1e-8.
Euler-Maruyama step with correlated noise (W1, W2); jump count per step
~ Poisson(λ·dt); jump size ~ N(0, σ_J).

Perturbed branch: drift μ → μ + h_field·dt (linear drift perturbation).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Iterator, Sequence

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.protocol import stream_fdr
from _shared.runtime import ensemble_C_chi  # noqa: F401

XDOT_KINDS = ("log-return", "log-relative")
EMA_IN_PHASE_A = {"log-return": True, "log-relative": False}
DT = 1.0 / 252.0   # one trading day in years


def _init_state(params: dict):
    def factory(rng: np.random.Generator, n_real: int) -> dict:
        log_S = np.zeros((n_real, 1), dtype=np.float64)
        V = np.full((n_real,), float(params["theta"]), dtype=np.float64)
        return {
            "unp": log_S.copy(), "per": log_S.copy(),
            "unp_prev": log_S.copy(), "per_prev": log_S.copy(),
            "V_unp": V.copy(), "V_per": V.copy(),
            **params,
        }
    return factory


def _advance(state: dict, h_extra_per: float, rng: np.random.Generator):
    n_real = state["unp"].shape[0]
    mu = state["mu"]; kappa = state["kappa"]; theta = state["theta"]
    xi = state["xi"]; rho = state["rho"]; lam = state["lam"]; sJ = state["sJ"]
    state["unp_prev"] = state["unp"].copy()
    state["per_prev"] = state["per"].copy()
    # Correlated Brownian increments (CRN across branches).
    z1 = rng.standard_normal(size=(n_real,))
    z_ind = rng.standard_normal(size=(n_real,))
    z2 = rho * z1 + math.sqrt(max(0.0, 1.0 - rho * rho)) * z_ind
    # Jump occurrence and size — shared CRN across branches.
    n_jumps = rng.poisson(lam * DT, size=(n_real,))
    jump_size = rng.normal(0.0, sJ, size=(n_real,)) * (n_jumps > 0)
    sqrt_dt = math.sqrt(DT)
    for branch, h_extra in (("unp", 0.0), ("per", h_extra_per)):
        V = state["V_" + branch]
        S = state[branch]
        sqrt_V = np.sqrt(np.maximum(V, 1e-12))
        d_logS = (mu + h_extra - 0.5 * V) * DT + sqrt_V * z1 * sqrt_dt + jump_size
        dV = kappa * (theta - V) * DT + xi * sqrt_V * z2 * sqrt_dt
        V_new = V + dV
        V_new = np.maximum(V_new, 1e-8)
        state["V_" + branch] = V_new
        state[branch] = S + d_logS.reshape(-1, 1)


def _xdot(state: dict, snap_for_xdot: dict | None, xdot_kind: str):
    if xdot_kind == "log-relative":
        ref = snap_for_xdot["unp_snap"]
        return state["unp"] - ref, state["per"] - ref
    return state["unp"] - state["unp_prev"], state["per"] - state["per_prev"]


def _raw_C_chi(state: dict, snap_at_tw: dict, h_field: float):
    return ensemble_C_chi(state["unp"], snap_at_tw["unp_snap"], state["per"], h_field)


def _fork(state: dict):
    state["per"] = state["unp"].copy()
    state["per_prev"] = state["unp_prev"].copy()
    state["V_per"] = state["V_unp"].copy()


def _snapshot(state: dict) -> dict:
    return {"unp_snap": state["unp"].copy()}


def multi_window_fdr_iter(regime_params, t_w, t_obs, tau_windows, h_field,
                           n_realizations, seed, n_sample_times,
                           progress_every=0, xdot_kind="log-return") -> Iterator[dict]:
    return stream_fdr(
        substrate="heston",
        op_label=regime_params["regime"],
        op_params=dict(regime_params),
        t_w=t_w, t_obs=t_obs, tau_windows=tau_windows, h_field=h_field,
        n_realizations=n_realizations, seed=seed,
        n_sample_times=n_sample_times, xdot_kind=xdot_kind,
        xdot_kinds_allowed=XDOT_KINDS, ema_in_phase_a=EMA_IN_PHASE_A,
        init_state=_init_state(regime_params),
        advance_one_sweep=_advance, xdot_field=_xdot,
        raw_C_chi=_raw_C_chi,
        fork_paired_branch=_fork, snapshot_state=_snapshot,
    )
