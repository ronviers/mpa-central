"""Lévy flight CTRW streaming primitive.

Per step: x(t+1) = x(t) + ε  where ε ~ symmetric α-stable, scale 1.
Chambers–Mallows–Stuck algorithm; α = 2.0 reduces to a Gaussian. The
perturbed branch adds a small constant drift h_field per step.
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


def _stable_sample(alpha: float, n: int, rng: np.random.Generator) -> np.ndarray:
    """Symmetric α-stable variate via Chambers–Mallows–Stuck."""
    a = float(alpha)
    if abs(a - 2.0) < 1e-9:
        return rng.standard_normal(n) * math.sqrt(2.0)
    U = rng.uniform(-math.pi / 2, math.pi / 2, size=n)
    W = -np.log(rng.uniform(size=n))
    if abs(a - 1.0) < 1e-9:
        return np.tan(U)
    factor = np.sin(a * U) / np.power(np.cos(U), 1.0 / a)
    tail   = np.power(np.cos(U - a * U) / W, (1.0 - a) / a)
    return factor * tail


def _init_state(alpha: float):
    def factory(rng: np.random.Generator, n_real: int) -> dict:
        x = np.zeros((n_real, 1), dtype=np.float64)
        return {
            "unp": x.copy(), "per": x.copy(),
            "unp_prev": x.copy(), "per_prev": x.copy(),
            "alpha": float(alpha),
        }
    return factory


def _advance(state: dict, h_extra_per: float, rng: np.random.Generator):
    n_real = state["unp"].shape[0]
    eps = _stable_sample(state["alpha"], n_real, rng).reshape(-1, 1)
    state["unp_prev"] = state["unp"].copy()
    state["per_prev"] = state["per"].copy()
    state["unp"] = state["unp"] + eps
    state["per"] = state["per"] + eps + h_extra_per


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


def multi_window_fdr_iter(alpha, t_w, t_obs, tau_windows, h_field,
                           n_realizations, seed, n_sample_times,
                           progress_every=0, xdot_kind="velocity") -> Iterator[dict]:
    return stream_fdr(
        substrate="levy_flight", op_label=f"alpha{alpha:.2f}",
        op_params={"alpha": float(alpha)},
        t_w=t_w, t_obs=t_obs, tau_windows=tau_windows, h_field=h_field,
        n_realizations=n_realizations, seed=seed,
        n_sample_times=n_sample_times, xdot_kind=xdot_kind,
        xdot_kinds_allowed=XDOT_KINDS, ema_in_phase_a=EMA_IN_PHASE_A,
        init_state=_init_state(alpha), advance_one_sweep=_advance,
        xdot_field=_xdot, raw_C_chi=_raw_C_chi,
        fork_paired_branch=_fork, snapshot_state=_snapshot,
    )
