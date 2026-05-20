"""Constant — CONTROL primitive (rung 0: degenerate input, zero dynamics).

x(t) = c for all t. No fluctuation, no relaxation, no response:
    C(τ) = c²   (flat — never decays)
    χ(τ) = 0    (perturbation does nothing; ẋ = 0)

This is the floor below the floor. cdv1's domain is dissipative/relaxing
systems; a frozen constant is out of domain by construction. The rung-0
question is NOT "does the grinder reproduce a flat line" (trivially yes) —
it's what the *inversion* does with it: NaN/garbage, crash, or a confident
hallucinated regime. A pipeline that polices its own domain refuses it.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.protocol import stream_fdr
from _shared.runtime import ensemble_C_chi  # noqa: F401

XDOT_KINDS = ("velocity", "position-relative")
EMA_IN_PHASE_A = {"velocity": True, "position-relative": False}


def _init_state(c: float):
    def factory(rng: np.random.Generator, n_real: int) -> dict:
        x = np.full((n_real, 1), float(c))
        return {"unp": x.copy(), "per": x.copy(),
                "unp_prev": x.copy(), "per_prev": x.copy(), "c": float(c)}
    return factory


def _advance(state: dict, h_extra_per: float, rng: np.random.Generator):
    # Zero dynamics: x stays c. A constant ignores the perturbation entirely
    # (no update rule for it to act on) → χ = 0.
    state["unp_prev"] = state["unp"].copy()
    state["per_prev"] = state["per"].copy()
    # unp, per unchanged.


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


def multi_window_fdr_iter(c, t_w, t_obs, tau_windows, h_field,
                          n_realizations, seed, n_sample_times,
                          progress_every=0, xdot_kind="velocity") -> Iterator[dict]:
    return stream_fdr(
        substrate="constant", op_label=f"c{c:g}",
        op_params={"c": float(c)},
        t_w=t_w, t_obs=t_obs, tau_windows=tau_windows, h_field=h_field,
        n_realizations=n_realizations, seed=seed,
        n_sample_times=n_sample_times, xdot_kind=xdot_kind,
        xdot_kinds_allowed=XDOT_KINDS, ema_in_phase_a=EMA_IN_PHASE_A,
        init_state=_init_state(c), advance_one_sweep=_advance,
        xdot_field=_xdot, raw_C_chi=_raw_C_chi,
        fork_paired_branch=_fork, snapshot_state=_snapshot,
    )
