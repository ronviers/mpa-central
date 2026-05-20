"""M/M/1 queue — INVALIDATOR primitive (heavy-traffic exponent target).

Discrete-time per-step Bernoulli approximation of M/M/1: at each step,
an arrival occurs w.p. λ·dt (N += 1) and a departure w.p. μ·dt if N>0
(N -= 1). ρ = λ/μ. Stationary mean queue = ρ/(1-ρ). Heavy traffic
(ρ→1): (1-ρ)N → reflected Brownian motion, exponent 1/2.

Perturbed branch boosts the arrival rate: λ → λ·(1 + h_field). χ reads
the response of mean queue length to the arrival-rate boost.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator, Sequence

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.protocol import stream_fdr
from _shared.runtime import ensemble_C_chi  # noqa: F401

XDOT_KINDS = ("queue-increment", "queue-relative")
EMA_IN_PHASE_A = {"queue-increment": True, "queue-relative": False}
MU = 1.0
DT = 0.5   # per-step rate scaling so λ·dt, μ·dt are valid probabilities


def _init_state(rho: float):
    lam = float(rho) * MU
    def factory(rng: np.random.Generator, n_real: int) -> dict:
        mean_q = rho / (1.0 - rho) if rho < 1 else 1000.0
        # Initialize near stationary (geometric-ish): round of exponential.
        N0 = rng.exponential(max(mean_q, 1.0), size=(n_real, 1))
        N = np.maximum(np.round(N0), 0.0)
        return {
            "unp": N.copy(), "per": N.copy(),
            "unp_prev": N.copy(), "per_prev": N.copy(),
            "lam": lam,
        }
    return factory


def _step_branch(N, lam_eff, rng):
    n_real = N.shape[0]
    arrive = (rng.random((n_real, 1)) < lam_eff * DT).astype(np.float64)
    serve = (rng.random((n_real, 1)) < MU * DT).astype(np.float64) * (N > 0)
    return np.maximum(N + arrive - serve, 0.0)


def _advance(state: dict, h_extra_per: float, rng: np.random.Generator):
    state["unp_prev"] = state["unp"].copy()
    state["per_prev"] = state["per"].copy()
    state["unp"] = _step_branch(state["unp"], state["lam"], rng)
    state["per"] = _step_branch(state["per"], state["lam"] * (1.0 + h_extra_per), rng)


def _xdot(state: dict, snap_for_xdot: dict | None, xdot_kind: str):
    if xdot_kind == "queue-relative":
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


def multi_window_fdr_iter(rho, t_w, t_obs, tau_windows, h_field,
                           n_realizations, seed, n_sample_times,
                           progress_every=0, xdot_kind="queue-increment") -> Iterator[dict]:
    return stream_fdr(
        substrate="mm1_queue", op_label=f"rho{rho:g}",
        op_params={"rho": float(rho), "mu": MU, "dt": DT},
        t_w=t_w, t_obs=t_obs, tau_windows=tau_windows, h_field=h_field,
        n_realizations=n_realizations, seed=seed,
        n_sample_times=n_sample_times, xdot_kind=xdot_kind,
        xdot_kinds_allowed=XDOT_KINDS, ema_in_phase_a=EMA_IN_PHASE_A,
        init_state=_init_state(rho), advance_one_sweep=_advance,
        xdot_field=_xdot, raw_C_chi=_raw_C_chi,
        fork_paired_branch=_fork, snapshot_state=_snapshot,
    )
