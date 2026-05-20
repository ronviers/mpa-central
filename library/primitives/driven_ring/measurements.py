"""Driven overdamped particle on a ring — INVALIDATOR primitive (NESS).

Tilted washboard:  dθ = (F - A·sinθ)·dt + sqrt(2·D·dt)·ξ.
For F > A: running solution, sustained current ⟨θ̇⟩ > 0 forever.
For F < A: locked near a minimum (relaxes normally — control).

State tracks UNWRAPPED θ so the velocity ẋ = Δθ captures the current.
Raw C uses the embedded observable (cos θ, sin θ): C(t,t_w) =
⟨cos(θ(t) − θ(t_w))⟩. Perturbed branch adds extra drive h_field.
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
DT = 0.01
A_BARRIER = 1.0
D_DIFF = 0.5


def _init_state(F: float):
    def factory(rng: np.random.Generator, n_real: int) -> dict:
        theta = rng.uniform(-math.pi, math.pi, size=(n_real, 1))
        return {
            "unp": theta.copy(), "per": theta.copy(),
            "unp_prev": theta.copy(), "per_prev": theta.copy(),
            "F": float(F),
        }
    return factory


def _advance(state: dict, h_extra_per: float, rng: np.random.Generator):
    n_real = state["unp"].shape[0]
    s_t = math.sqrt(2.0 * D_DIFF * DT)
    xi = rng.standard_normal((n_real, 1)) * s_t  # CRN shared
    state["unp_prev"] = state["unp"].copy()
    state["per_prev"] = state["per"].copy()
    F = state["F"]
    th_u = state["unp"]; th_p = state["per"]
    state["unp"] = th_u + (F - A_BARRIER * np.sin(th_u)) * DT + xi
    state["per"] = th_p + (F + h_extra_per - A_BARRIER * np.sin(th_p)) * DT + xi


def _embed(theta):
    return np.concatenate([np.cos(theta), np.sin(theta)], axis=1)  # (n_real, 2)


def _xdot(state: dict, snap_for_xdot: dict | None, xdot_kind: str):
    if xdot_kind == "position-relative":
        ref = snap_for_xdot["unp_snap"]
        return state["unp"] - ref, state["per"] - ref
    return state["unp"] - state["unp_prev"], state["per"] - state["per_prev"]


def _raw_C_chi(state: dict, snap_at_tw: dict, h_field: float):
    # Embedded-angle correlation; C = <cos(θ(t)-θ(tw))>.
    return ensemble_C_chi(_embed(state["unp"]), snap_at_tw["emb_snap"],
                          _embed(state["per"]), h_field)


def _fork(state: dict):
    state["per"] = state["unp"].copy()
    state["per_prev"] = state["unp_prev"].copy()


def _snapshot(state: dict) -> dict:
    return {"unp_snap": state["unp"].copy(), "emb_snap": _embed(state["unp"])}


def multi_window_fdr_iter(F, t_w, t_obs, tau_windows, h_field,
                           n_realizations, seed, n_sample_times,
                           progress_every=0, xdot_kind="velocity") -> Iterator[dict]:
    return stream_fdr(
        substrate="driven_ring", op_label=f"F{F:g}",
        op_params={"F": float(F), "A": A_BARRIER, "D": D_DIFF, "dt": DT},
        t_w=t_w, t_obs=t_obs, tau_windows=tau_windows, h_field=h_field,
        n_realizations=n_realizations, seed=seed,
        n_sample_times=n_sample_times, xdot_kind=xdot_kind,
        xdot_kinds_allowed=XDOT_KINDS, ema_in_phase_a=EMA_IN_PHASE_A,
        init_state=_init_state(F), advance_one_sweep=_advance,
        xdot_field=_xdot, raw_C_chi=_raw_C_chi,
        fork_paired_branch=_fork, snapshot_state=_snapshot,
    )
