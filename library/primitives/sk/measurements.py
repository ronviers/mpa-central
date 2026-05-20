"""Sherrington-Kirkpatrick mean-field spin glass — streaming primitive.

N spins on a complete graph; J_ij ~ N(0, 1/sqrt(N)) drawn once per replica
(frozen disorder). Glauber single-spin-flip MC. One sweep = N proposed flips.
The perturbed branch sees an additional uniform field h_field.
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

XDOT_KINDS = ("spin-flip", "spin-relative")
EMA_IN_PHASE_A = {"spin-flip": True, "spin-relative": False}
N_SPINS = 100


def _init_state(T: float, h_amp: float):
    def factory(rng: np.random.Generator, n_real: int) -> dict:
        spins = rng.choice(np.array([-1, 1], dtype=np.int8),
                           size=(n_real, N_SPINS))
        # Frozen disorder: J ~ N(0, 1/sqrt(N)) per replica, symmetric, zero diag.
        J = rng.normal(0.0, 1.0 / math.sqrt(N_SPINS),
                       size=(n_real, N_SPINS, N_SPINS))
        J = 0.5 * (J + np.transpose(J, (0, 2, 1)))
        idx = np.arange(N_SPINS)
        J[:, idx, idx] = 0.0
        return {
            "unp": spins, "per": spins.copy(),
            "unp_prev": spins.copy(), "per_prev": spins.copy(),
            "J": J, "T": float(T), "h_amp": float(h_amp),
        }
    return factory


def _advance(state: dict, h_extra_per: float, rng: np.random.Generator):
    beta = 1.0 / state["T"]
    J = state["J"]
    n_real, N = state["unp"].shape
    state["unp_prev"] = state["unp"].copy()
    state["per_prev"] = state["per"].copy()
    idx_seq = rng.integers(0, N, size=(N, n_real))
    u_seq = rng.random(size=(N, n_real))
    h_const = state["h_amp"]
    row = np.arange(n_real)
    for step in range(N):
        i = idx_seq[step]
        s_unp = state["unp"]; s_per = state["per"]
        # Local field h_i = sum_j J_ij s_j  (+ external h_const for unp,
        # h_const + h_extra_per for per).
        # Vectorized: gather row J[r, i[r], :] for each replica.
        Ji = J[row, i, :]                        # (n_real, N)
        h_unp = (Ji * s_unp.astype(np.float64)).sum(axis=1) + h_const
        h_per = (Ji * s_per.astype(np.float64)).sum(axis=1) + h_const + h_extra_per
        # Glauber: P(s_i = +1 | h) = sigmoid(2*beta*h)
        p_unp = 1.0 / (1.0 + np.exp(-2.0 * beta * h_unp))
        p_per = 1.0 / (1.0 + np.exp(-2.0 * beta * h_per))
        new_unp = np.where(u_seq[step] < p_unp, 1, -1).astype(np.int8)
        new_per = np.where(u_seq[step] < p_per, 1, -1).astype(np.int8)
        s_unp[row, i] = new_unp
        s_per[row, i] = new_per


def _xdot(state: dict, snap_for_xdot: dict | None, xdot_kind: str):
    s_unp = state["unp"].astype(np.float64)
    s_per = state["per"].astype(np.float64)
    if xdot_kind == "spin-relative":
        ref = snap_for_xdot["unp_snap"]
        return (s_unp - ref), (s_per - ref)
    prev_unp = state["unp_prev"].astype(np.float64)
    prev_per = state["per_prev"].astype(np.float64)
    return (s_unp - prev_unp), (s_per - prev_per)


def _raw_C_chi(state: dict, snap_at_tw: dict, h_field: float):
    return ensemble_C_chi(
        state["unp"].astype(np.float64),
        snap_at_tw["unp_snap"],
        state["per"].astype(np.float64),
        h_field,
    )


def _fork(state: dict):
    state["per"] = state["unp"].copy()
    state["per_prev"] = state["unp_prev"].copy()


def _snapshot(state: dict) -> dict:
    return {"unp_snap": state["unp"].astype(np.float64).copy()}


def multi_window_fdr_iter(
    T: float, h_amp: float, t_w: int, t_obs: int,
    tau_windows: Sequence[float], h_field: float,
    n_realizations: int, seed: int, n_sample_times: int,
    progress_every: int = 0, xdot_kind: str = "spin-flip",
) -> Iterator[dict]:
    return stream_fdr(
        substrate="sk",
        op_label=f"T{T:.3f}",
        op_params={"T": T, "h_amp": h_amp},
        t_w=t_w, t_obs=t_obs,
        tau_windows=tau_windows, h_field=h_field,
        n_realizations=n_realizations, seed=seed,
        n_sample_times=n_sample_times, xdot_kind=xdot_kind,
        xdot_kinds_allowed=XDOT_KINDS,
        ema_in_phase_a=EMA_IN_PHASE_A,
        init_state=_init_state(T, h_amp),
        advance_one_sweep=_advance,
        xdot_field=_xdot, raw_C_chi=_raw_C_chi,
        fork_paired_branch=_fork, snapshot_state=_snapshot,
    )
