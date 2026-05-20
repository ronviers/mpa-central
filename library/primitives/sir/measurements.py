"""Stochastic SIR epidemic streaming primitive.

Tau-leap step: per replica, draw Binomial(S, 1-exp(-β·I/N)) infections
and Binomial(I, 1-exp(-γ)) recoveries. State per replica: (S, I, R)
counts plus a running cumulative-incidence scalar.

Perturbed branch: scales β by (1 + h_extra). chi reads the response of
mean incidence rate to a small transmission-rate boost.
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

XDOT_KINDS = ("incidence", "cumulative-relative")
EMA_IN_PHASE_A = {"incidence": True, "cumulative-relative": False}
POP_N = 10_000
GAMMA = 0.1
I0_FRAC = 0.001


def _init_state(R0: float):
    beta = float(R0) * GAMMA
    def factory(rng: np.random.Generator, n_real: int) -> dict:
        S = np.full((n_real,), int(POP_N * (1.0 - I0_FRAC)), dtype=np.int64)
        I = np.full((n_real,), int(POP_N * I0_FRAC), dtype=np.int64)
        # Incidence "trail" observable per replica.
        unp = np.zeros((n_real, 1), dtype=np.float64)
        per = np.zeros((n_real, 1), dtype=np.float64)
        return {
            "unp": unp, "per": per,
            "unp_prev": unp.copy(), "per_prev": per.copy(),
            "S_unp": S.copy(), "I_unp": I.copy(),
            "S_per": S.copy(), "I_per": I.copy(),
            "cum_unp": np.zeros((n_real, 1), dtype=np.float64),
            "cum_per": np.zeros((n_real, 1), dtype=np.float64),
            "beta": beta, "gamma": GAMMA,
        }
    return factory


def _advance(state: dict, h_extra_per: float, rng: np.random.Generator):
    n_real = state["S_unp"].shape[0]
    state["unp_prev"] = state["unp"].copy()
    state["per_prev"] = state["per"].copy()
    for branch in ("unp", "per"):
        S = state["S_" + branch]
        I = state["I_" + branch]
        beta_eff = state["beta"] * (1.0 + (h_extra_per if branch == "per" else 0.0))
        # Per-replica infection probability.
        p_inf = 1.0 - np.exp(-beta_eff * I.astype(np.float64) / POP_N)
        p_rec = 1.0 - math.exp(-state["gamma"])
        # Binomial draws (use numpy's vectorized).
        new_inf = rng.binomial(S, p_inf)
        new_rec = rng.binomial(I, p_rec)
        S2 = S - new_inf
        I2 = I + new_inf - new_rec
        np.clip(S2, 0, POP_N, out=S2)
        np.clip(I2, 0, POP_N, out=I2)
        state["S_" + branch] = S2
        state["I_" + branch] = I2
        # Per-capita incidence rate goes into the trail observable.
        inc = (new_inf.astype(np.float64) / POP_N).reshape(-1, 1)
        state[branch] = inc.copy()
        state["cum_" + branch] = state["cum_" + branch] + inc


def _xdot(state: dict, snap_for_xdot: dict | None, xdot_kind: str):
    if xdot_kind == "cumulative-relative":
        ref = snap_for_xdot["cum_snap"]
        return state["cum_unp"] - ref, state["cum_per"] - ref
    # incidence — per-step rate is itself the ẋ.
    return state["unp"], state["per"]


def _raw_C_chi(state: dict, snap_at_tw: dict, h_field: float):
    return ensemble_C_chi(
        state["unp"], snap_at_tw["unp_snap"], state["per"], h_field,
    )


def _fork(state: dict):
    state["S_per"] = state["S_unp"].copy()
    state["I_per"] = state["I_unp"].copy()
    state["cum_per"] = state["cum_unp"].copy()
    state["per"] = state["unp"].copy()
    state["per_prev"] = state["unp_prev"].copy()


def _snapshot(state: dict) -> dict:
    return {
        "unp_snap": state["unp"].copy(),
        "cum_snap": state["cum_unp"].copy(),
    }


def multi_window_fdr_iter(R0, t_w, t_obs, tau_windows, h_field,
                           n_realizations, seed, n_sample_times,
                           progress_every=0, xdot_kind="incidence") -> Iterator[dict]:
    return stream_fdr(
        substrate="sir", op_label=f"R0_{R0:.2f}",
        op_params={"R0": float(R0), "gamma": GAMMA, "N": POP_N},
        t_w=t_w, t_obs=t_obs, tau_windows=tau_windows, h_field=h_field,
        n_realizations=n_realizations, seed=seed,
        n_sample_times=n_sample_times, xdot_kind=xdot_kind,
        xdot_kinds_allowed=XDOT_KINDS, ema_in_phase_a=EMA_IN_PHASE_A,
        init_state=_init_state(R0), advance_one_sweep=_advance,
        xdot_field=_xdot, raw_C_chi=_raw_C_chi,
        fork_paired_branch=_fork, snapshot_state=_snapshot,
    )
