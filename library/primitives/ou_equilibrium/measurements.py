"""Ornstein-Uhlenbeck in exact equilibrium — INVALIDATOR primitive.

Exact discrete OU normalized to stationary variance 1:
    x(t+1) = a·x(t) + sqrt(1 - a²)·ξ,    a = exp(-1/τ)
    x(0) ~ N(0, 1)   (drawn from the stationary distribution — no quench)

Stationary, time-translation-invariant. C(t,t_w) = a^(t-t_w) = exp(-(t-t_w)/τ).
FDT holds exactly: X = 1 everywhere. Perturbed branch adds a constant
drift b = h·(1-a) so steady-state mean shift = h, giving χ(t) = 1 - a^t
= 1 - C(t), i.e. FDT slope 1 (T_eff = 1).
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

XDOT_KINDS = ("velocity", "position-relative")
EMA_IN_PHASE_A = {"velocity": True, "position-relative": False}


def _init_state(tau: float):
    a = math.exp(-1.0 / float(tau))
    def factory(rng: np.random.Generator, n_real: int) -> dict:
        x = rng.standard_normal((n_real, 1))  # stationary N(0,1) — no quench
        return {
            "unp": x.copy(), "per": x.copy(),
            "unp_prev": x.copy(), "per_prev": x.copy(),
            "a": a,
        }
    return factory


def _advance(state: dict, h_extra_per: float, rng: np.random.Generator):
    a = state["a"]
    n_real = state["unp"].shape[0]
    xi = rng.standard_normal((n_real, 1)) * math.sqrt(max(0.0, 1.0 - a * a))
    state["unp_prev"] = state["unp"].copy()
    state["per_prev"] = state["per"].copy()
    # Common random numbers (same xi) on both branches.
    state["unp"] = a * state["unp"] + xi
    state["per"] = a * state["per"] + xi + h_extra_per * (1.0 - a)


def _xdot(state: dict, snap_for_xdot: dict | None, xdot_kind: str):
    if xdot_kind == "position-relative":
        ref = snap_for_xdot["unp_snap"]
        return state["unp"] - ref, state["per"] - ref
    return state["unp"] - state["unp_prev"], state["per"] - state["per_prev"]


def _raw_C_chi(state: dict, snap_at_tw: dict, h_field: float):
    return ensemble_C_chi(state["unp"], snap_at_tw["unp_snap"], state["per"], h_field)


def _fork(state: dict):
    state["per"] = state["unp"].copy()
    state["per_prev"] = state["unp_prev"].copy()


def _snapshot(state: dict) -> dict:
    return {"unp_snap": state["unp"].copy()}


def multi_window_fdr_iter(tau, t_w, t_obs, tau_windows, h_field,
                           n_realizations, seed, n_sample_times,
                           progress_every=0, xdot_kind="velocity") -> Iterator[dict]:
    return stream_fdr(
        substrate="ou_equilibrium", op_label=f"tau{tau:g}",
        op_params={"tau": float(tau), "T_eff": 1.0},
        t_w=t_w, t_obs=t_obs, tau_windows=tau_windows, h_field=h_field,
        n_realizations=n_realizations, seed=seed,
        n_sample_times=n_sample_times, xdot_kind=xdot_kind,
        xdot_kinds_allowed=XDOT_KINDS, ema_in_phase_a=EMA_IN_PHASE_A,
        init_state=_init_state(tau), advance_one_sweep=_advance,
        xdot_field=_xdot, raw_C_chi=_raw_C_chi,
        fork_paired_branch=_fork, snapshot_state=_snapshot,
    )
