"""White noise — CONTROL primitive (memoryless dissipative floor).

x(t) = σ·ξ(t), ξ ~ N(0,1) fresh every step. C(t,t_w)=0 for t>t_w. The
trivial-r character. Perturbed branch adds a DC bias h_field on the same
noise draw (CRN). Amplitude σ is the operating axis and must not change
the regime.
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


def _init_state(sigma: float):
    def factory(rng: np.random.Generator, n_real: int) -> dict:
        x = sigma * rng.standard_normal((n_real, 1))
        return {
            "unp": x.copy(), "per": x.copy(),
            "unp_prev": x.copy(), "per_prev": x.copy(),
            "sigma": float(sigma),
        }
    return factory


def _advance(state: dict, h_extra_per: float, rng: np.random.Generator):
    n_real = state["unp"].shape[0]
    state["unp_prev"] = state["unp"].copy()
    state["per_prev"] = state["per"].copy()
    xi = state["sigma"] * rng.standard_normal((n_real, 1))  # CRN shared
    state["unp"] = xi
    state["per"] = xi + h_extra_per


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


def multi_window_fdr_iter(sigma, t_w, t_obs, tau_windows, h_field,
                           n_realizations, seed, n_sample_times,
                           progress_every=0, xdot_kind="velocity") -> Iterator[dict]:
    return stream_fdr(
        substrate="white_noise", op_label=f"sigma{sigma:g}",
        op_params={"sigma": float(sigma)},
        t_w=t_w, t_obs=t_obs, tau_windows=tau_windows, h_field=h_field,
        n_realizations=n_realizations, seed=seed,
        n_sample_times=n_sample_times, xdot_kind=xdot_kind,
        xdot_kinds_allowed=XDOT_KINDS, ema_in_phase_a=EMA_IN_PHASE_A,
        init_state=_init_state(sigma), advance_one_sweep=_advance,
        xdot_field=_xdot, raw_C_chi=_raw_C_chi,
        fork_paired_branch=_fork, snapshot_state=_snapshot,
    )
