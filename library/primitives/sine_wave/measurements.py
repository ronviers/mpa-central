"""Sine wave — CONTROL primitive (pure-tone character zero).

x(t) = sqrt(2)·sin(2π·(t + φ_r)/P),  φ_r ~ Uniform[0, P) per replica.

Phase-randomized → phase-stationary ensemble. sqrt(2) normalizes variance
to 1 (C(0)=1). Phase-averaged autocorrelation C(τ)=cos(2π·τ/P). Smooth,
deterministic, driven, NO bath — never relaxes.

Perturbed branch is phase-shifted by h_field steps. The clock t is carried
in state and advances every sweep so the tone oscillates continuously.
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
SQRT2 = math.sqrt(2.0)


def _sine(t: float, phi: np.ndarray, P: float) -> np.ndarray:
    return SQRT2 * np.sin(2.0 * math.pi * (t + phi) / P)


def _init_state(P: float):
    def factory(rng: np.random.Generator, n_real: int) -> dict:
        phi = rng.uniform(0.0, float(P), size=(n_real, 1))
        x0 = _sine(0.0, phi, float(P))
        return {
            "unp": x0.copy(), "per": x0.copy(),
            "unp_prev": x0.copy(), "per_prev": x0.copy(),
            "phi": phi, "P": float(P), "t": 0,
        }
    return factory


def _advance(state: dict, h_extra_per: float, rng: np.random.Generator):
    state["unp_prev"] = state["unp"].copy()
    state["per_prev"] = state["per"].copy()
    state["t"] += 1
    t = state["t"]
    P = state["P"]; phi = state["phi"]
    state["unp"] = _sine(t, phi, P)
    state["per"] = _sine(t + h_extra_per, phi, P)


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


def multi_window_fdr_iter(P, t_w, t_obs, tau_windows, h_field,
                           n_realizations, seed, n_sample_times,
                           progress_every=0, xdot_kind="velocity") -> Iterator[dict]:
    return stream_fdr(
        substrate="sine_wave", op_label=f"P{P:g}",
        op_params={"P": float(P), "phase_randomized": True},
        t_w=t_w, t_obs=t_obs, tau_windows=tau_windows, h_field=h_field,
        n_realizations=n_realizations, seed=seed,
        n_sample_times=n_sample_times, xdot_kind=xdot_kind,
        xdot_kinds_allowed=XDOT_KINDS, ema_in_phase_a=EMA_IN_PHASE_A,
        init_state=_init_state(P), advance_one_sweep=_advance,
        xdot_field=_xdot, raw_C_chi=_raw_C_chi,
        fork_paired_branch=_fork, snapshot_state=_snapshot,
    )
