"""Stochastic Lotka-Volterra streaming primitive.

State per replica: (X, Y) integer counts of prey/predator. Per step,
draw Poisson counts for each reaction channel (births, predation,
predator deaths). Perturbed branch sees prey reproduction rate
α → α + h_extra·α (multiplicative bump).

Trail observable: 2D (Δprey, Δpred) per step.
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

XDOT_KINDS = ("pop-velocity", "pop-relative")
EMA_IN_PHASE_A = {"pop-velocity": True, "pop-relative": False}
X0 = 100   # initial prey
Y0 = 50    # initial predator
DT = 0.01
N_MAX = 5000


def _init_state(alpha: float, beta: float, gamma: float, delta: float):
    def factory(rng: np.random.Generator, n_real: int) -> dict:
        X = np.full((n_real,), X0, dtype=np.int64)
        Y = np.full((n_real,), Y0, dtype=np.int64)
        pop = np.stack([X.astype(np.float64), Y.astype(np.float64)], axis=1)
        return {
            "unp": pop.copy(), "per": pop.copy(),
            "unp_prev": pop.copy(), "per_prev": pop.copy(),
            "X_unp": X.copy(), "Y_unp": Y.copy(),
            "X_per": X.copy(), "Y_per": Y.copy(),
            "alpha": float(alpha), "beta": float(beta),
            "gamma": float(gamma), "delta": float(delta),
        }
    return factory


def _advance(state: dict, h_extra_per: float, rng: np.random.Generator):
    n_real = state["X_unp"].shape[0]
    state["unp_prev"] = state["unp"].copy()
    state["per_prev"] = state["per"].copy()
    for branch in ("unp", "per"):
        X = state["X_" + branch]
        Y = state["Y_" + branch]
        alpha_eff = state["alpha"] * (1.0 + (h_extra_per if branch == "per" else 0.0))
        # Tau-leap Poisson approximation.
        births  = rng.poisson(np.maximum(alpha_eff * X * DT, 0.0))
        deaths_prey = rng.poisson(np.maximum(state["beta"] * X * Y * DT / N_MAX, 0.0))
        births_pred = rng.poisson(np.maximum(state["delta"] * X * Y * DT / N_MAX, 0.0))
        deaths_pred = rng.poisson(np.maximum(state["gamma"] * Y * DT, 0.0))
        X2 = X + births - deaths_prey
        Y2 = Y + births_pred - deaths_pred
        np.clip(X2, 0, 10 * N_MAX, out=X2)
        np.clip(Y2, 0, 10 * N_MAX, out=Y2)
        state["X_" + branch] = X2
        state["Y_" + branch] = Y2
        state[branch] = np.stack([X2.astype(np.float64),
                                  Y2.astype(np.float64)], axis=1)


def _xdot(state: dict, snap_for_xdot: dict | None, xdot_kind: str):
    if xdot_kind == "pop-relative":
        ref = snap_for_xdot["unp_snap"]
        return state["unp"] - ref, state["per"] - ref
    return state["unp"] - state["unp_prev"], state["per"] - state["per_prev"]


def _raw_C_chi(state: dict, snap_at_tw: dict, h_field: float):
    return ensemble_C_chi(state["unp"], snap_at_tw["unp_snap"], state["per"], h_field)


def _fork(state: dict):
    state["per"] = state["unp"].copy()
    state["per_prev"] = state["unp_prev"].copy()
    state["X_per"] = state["X_unp"].copy()
    state["Y_per"] = state["Y_unp"].copy()


def _snapshot(state: dict) -> dict:
    return {"unp_snap": state["unp"].copy()}


def multi_window_fdr_iter(alpha, beta, gamma, delta, t_w, t_obs,
                           tau_windows, h_field, n_realizations, seed,
                           n_sample_times, progress_every=0,
                           xdot_kind="pop-velocity") -> Iterator[dict]:
    return stream_fdr(
        substrate="lotka_volterra", op_label=f"a{alpha:.2f}",
        op_params={"alpha": float(alpha), "beta": float(beta),
                   "gamma": float(gamma), "delta": float(delta),
                   "X0": X0, "Y0": Y0, "dt": DT},
        t_w=t_w, t_obs=t_obs, tau_windows=tau_windows, h_field=h_field,
        n_realizations=n_realizations, seed=seed,
        n_sample_times=n_sample_times, xdot_kind=xdot_kind,
        xdot_kinds_allowed=XDOT_KINDS, ema_in_phase_a=EMA_IN_PHASE_A,
        init_state=_init_state(alpha, beta, gamma, delta),
        advance_one_sweep=_advance, xdot_field=_xdot,
        raw_C_chi=_raw_C_chi, fork_paired_branch=_fork,
        snapshot_state=_snapshot,
    )
