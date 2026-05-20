"""Logistic-map deterministic chaos — INVALIDATOR primitive.

x(t+1) = r·x(t)·(1 - x(t)). Deterministic; the ONLY randomness is the
initial condition (ensemble over ICs). No thermal noise. The perturbed
branch uses r → r + h_field; the two trajectories diverge at the
Lyapunov rate, so χ does NOT relax (it saturates at O(1/h)).

This probes whether MPA's stochastic-FDR machinery manufactures a regime
classification on a system with no bath.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator, Sequence

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.protocol import stream_fdr
from _shared.runtime import ensemble_C_chi  # noqa: F401

XDOT_KINDS = ("velocity", "position-relative")
EMA_IN_PHASE_A = {"velocity": True, "position-relative": False}
BURN_IN = 200


def _init_state(r: float):
    def factory(rng: np.random.Generator, n_real: int) -> dict:
        x = rng.uniform(0.0, 1.0, size=(n_real, 1))
        # Burn in the transient so we sample on the attractor.
        for _ in range(BURN_IN):
            x = r * x * (1.0 - x)
        return {
            "unp": x.copy(), "per": x.copy(),
            "unp_prev": x.copy(), "per_prev": x.copy(),
            "r": float(r),
        }
    return factory


def _advance(state: dict, h_extra_per: float, rng: np.random.Generator):
    r = state["r"]
    state["unp_prev"] = state["unp"].copy()
    state["per_prev"] = state["per"].copy()
    xu = state["unp"]
    xp = state["per"]
    state["unp"] = r * xu * (1.0 - xu)
    state["per"] = (r + h_extra_per) * xp * (1.0 - xp)
    # Clamp to the unit interval (r+h slightly >4 can eject points).
    np.clip(state["per"], 0.0, 1.0, out=state["per"])


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


def multi_window_fdr_iter(r, t_w, t_obs, tau_windows, h_field,
                           n_realizations, seed, n_sample_times,
                           progress_every=0, xdot_kind="velocity") -> Iterator[dict]:
    return stream_fdr(
        substrate="logistic_chaos", op_label=f"r{r:g}",
        op_params={"r": float(r), "deterministic": True, "burn_in": BURN_IN},
        t_w=t_w, t_obs=t_obs, tau_windows=tau_windows, h_field=h_field,
        n_realizations=n_realizations, seed=seed,
        n_sample_times=n_sample_times, xdot_kind=xdot_kind,
        xdot_kinds_allowed=XDOT_KINDS, ema_in_phase_a=EMA_IN_PHASE_A,
        init_state=_init_state(r), advance_one_sweep=_advance,
        xdot_field=_xdot, raw_C_chi=_raw_C_chi,
        fork_paired_branch=_fork, snapshot_state=_snapshot,
    )
