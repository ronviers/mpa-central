"""2D equilibrium Ising — INVALIDATOR primitive.

L×L torus, checkerboard Metropolis. Equilibrium steady state (no quench;
the protocol's t_w equilibration is sized by τ_env). FDT must hold: X=1
at every T, including near Tc≈2.269. Perturbed branch has a uniform
field h_field; common random numbers shared across branches per color.
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
L_SIDE = 32


def _checkerboard():
    ii, jj = np.indices((L_SIDE, L_SIDE))
    mask0 = ((ii + jj) % 2 == 0)
    return mask0, ~mask0


def _init_state(T: float):
    mask0, mask1 = _checkerboard()
    def factory(rng: np.random.Generator, n_real: int) -> dict:
        s = rng.choice(np.array([-1, 1], dtype=np.int8), size=(n_real, L_SIDE, L_SIDE))
        return {
            "unp": s, "per": s.copy(),
            "unp_prev": s.copy(), "per_prev": s.copy(),
            "T": float(T), "mask": (mask0[None, :, :], mask1[None, :, :]),
        }
    return factory


def _sweep_branch(s, beta, h, mask, u):
    nb = (np.roll(s, 1, 1) + np.roll(s, -1, 1)
          + np.roll(s, 1, 2) + np.roll(s, -1, 2)).astype(np.float64)
    dE = 2.0 * s * (nb + h)
    p = np.exp(-beta * dE)
    flip = (u < p) & mask
    s[flip] = -s[flip]


def _advance(state: dict, h_extra_per: float, rng: np.random.Generator):
    beta = 1.0 / state["T"]
    state["unp_prev"] = state["unp"].copy()
    state["per_prev"] = state["per"].copy()
    for color in (0, 1):
        mask = state["mask"][color]
        u = rng.random(state["unp"].shape)  # CRN shared by both branches
        _sweep_branch(state["unp"], beta, 0.0, mask, u)
        _sweep_branch(state["per"], beta, h_extra_per, mask, u)


def _xdot(state: dict, snap_for_xdot: dict | None, xdot_kind: str):
    u = state["unp"].astype(np.float64)
    p = state["per"].astype(np.float64)
    if xdot_kind == "spin-relative":
        ref = snap_for_xdot["unp_snap"]
        return u - ref, p - ref
    return u - state["unp_prev"].astype(np.float64), p - state["per_prev"].astype(np.float64)


def _raw_C_chi(state: dict, snap_at_tw: dict, h_field: float):
    return ensemble_C_chi(state["unp"].astype(np.float64),
                          snap_at_tw["unp_snap"],
                          state["per"].astype(np.float64), h_field)


def _fork(state: dict):
    state["per"] = state["unp"].copy()
    state["per_prev"] = state["unp_prev"].copy()


def _snapshot(state: dict) -> dict:
    return {"unp_snap": state["unp"].astype(np.float64).copy()}


def multi_window_fdr_iter(T, t_w, t_obs, tau_windows, h_field,
                           n_realizations, seed, n_sample_times,
                           progress_every=0, xdot_kind="spin-flip") -> Iterator[dict]:
    return stream_fdr(
        substrate="ising_equilibrium", op_label=f"T{T:.3f}",
        op_params={"T": float(T), "L": L_SIDE, "Tc": 2.269},
        t_w=t_w, t_obs=t_obs, tau_windows=tau_windows, h_field=h_field,
        n_realizations=n_realizations, seed=seed,
        n_sample_times=n_sample_times, xdot_kind=xdot_kind,
        xdot_kinds_allowed=XDOT_KINDS, ema_in_phase_a=EMA_IN_PHASE_A,
        init_state=_init_state(T), advance_one_sweep=_advance,
        xdot_field=_xdot, raw_C_chi=_raw_C_chi,
        fork_paired_branch=_fork, snapshot_state=_snapshot,
    )
