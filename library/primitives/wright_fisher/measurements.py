"""Wright-Fisher allele-frequency streaming primitive.

Two-allele haploid Wright-Fisher with selection s. Per generation:
    p_{t+1} ~ Binomial(N, q(p_t)) / N
    q(p) = (1+s)·p / [(1+s)·p + (1-p)]

Perturbed branch sees s_eff = s + h_field (extra selective advantage).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator, Sequence

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.protocol import stream_fdr
from _shared.runtime import ensemble_C_chi  # noqa: F401

XDOT_KINDS = ("frequency-velocity", "frequency-relative")
EMA_IN_PHASE_A = {"frequency-velocity": True, "frequency-relative": False}
POP_N = 1000
P0 = 0.5


def _init_state(s: float):
    def factory(rng: np.random.Generator, n_real: int) -> dict:
        p = np.full((n_real, 1), float(P0), dtype=np.float64)
        return {
            "unp": p.copy(), "per": p.copy(),
            "unp_prev": p.copy(), "per_prev": p.copy(),
            "s": float(s),
        }
    return factory


def _advance(state: dict, h_extra_per: float, rng: np.random.Generator):
    state["unp_prev"] = state["unp"].copy()
    state["per_prev"] = state["per"].copy()
    for branch in ("unp", "per"):
        s_eff = state["s"] + (h_extra_per if branch == "per" else 0.0)
        p = state[branch][:, 0]
        q = (1.0 + s_eff) * p / ((1.0 + s_eff) * p + (1.0 - p) + 1e-12)
        q = np.clip(q, 0.0, 1.0)
        # Binomial draw per replica.
        k = rng.binomial(POP_N, q)
        p_new = k.astype(np.float64) / float(POP_N)
        state[branch] = p_new.reshape(-1, 1)


def _xdot(state: dict, snap_for_xdot: dict | None, xdot_kind: str):
    if xdot_kind == "frequency-relative":
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


def multi_window_fdr_iter(s, t_w, t_obs, tau_windows, h_field,
                           n_realizations, seed, n_sample_times,
                           progress_every=0, xdot_kind="frequency-velocity") -> Iterator[dict]:
    return stream_fdr(
        substrate="wright_fisher", op_label=f"s{s:+.3f}",
        op_params={"s": float(s), "N": POP_N, "p0": P0},
        t_w=t_w, t_obs=t_obs, tau_windows=tau_windows, h_field=h_field,
        n_realizations=n_realizations, seed=seed,
        n_sample_times=n_sample_times, xdot_kind=xdot_kind,
        xdot_kinds_allowed=XDOT_KINDS, ema_in_phase_a=EMA_IN_PHASE_A,
        init_state=_init_state(s), advance_one_sweep=_advance,
        xdot_field=_xdot, raw_C_chi=_raw_C_chi,
        fork_paired_branch=_fork, snapshot_state=_snapshot,
    )
