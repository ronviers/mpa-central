"""East model streaming primitive — 1D KCM.

Length-L chain of spins ∈ {0, 1}. Each MC sweep proposes L random sites;
site i flips only if neighbor i−1 is 1. Acceptance: Glauber/Metropolis at
inverse temperature β. Energy of "up" spin = 1; "down" = 0. Equilibrium
up-density c_eq = 1/(1+exp(β)).

Perturbed branch: small uniform tilt h_field on the "up" energy.
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
L_CHAIN = 200


def _init_state(T: float):
    def factory(rng: np.random.Generator, n_real: int) -> dict:
        c_eq = 1.0 / (1.0 + math.exp(1.0 / T))
        s = (rng.random(size=(n_real, L_CHAIN)) < c_eq).astype(np.int8)
        # Force first site (boundary) to be up so chain is unfrozen.
        s[:, 0] = 1
        return {
            "unp": s, "per": s.copy(),
            "unp_prev": s.copy(), "per_prev": s.copy(),
            "T": float(T),
        }
    return factory


def _advance(state: dict, h_extra_per: float, rng: np.random.Generator):
    beta = 1.0 / state["T"]
    n_real, L = state["unp"].shape
    state["unp_prev"] = state["unp"].copy()
    state["per_prev"] = state["per"].copy()
    # One sweep = L random updates.
    idx = rng.integers(1, L, size=(L, n_real))   # i in [1, L-1]; site 0 fixed
    u = rng.random(size=(L, n_real))
    row = np.arange(n_real)
    for step in range(L):
        i = idx[step]
        for s, h_extra in (("unp", 0.0), ("per", h_extra_per)):
            sp = state[s]
            # East constraint: facilitator is i-1.
            fac = sp[row, i - 1]
            si = sp[row, i]
            # Energy diff to flip: ΔE = (1 - 2*s_i) * (1 + h_extra)
            #  - if s_i = 0 (down), flipping to up costs (1 + h_extra)
            #  - if s_i = 1 (up), flipping to down releases (1 + h_extra)
            dE = (1.0 - 2.0 * si.astype(np.float64)) * (1.0 + h_extra)
            # Glauber: P(accept) = 1 / (1 + exp(beta*dE))
            p_acc = 1.0 / (1.0 + np.exp(beta * dE))
            do = (fac == 1) & (u[step] < p_acc)
            new_si = np.where(do, 1 - si, si).astype(np.int8)
            sp[row, i] = new_si


def _xdot(state: dict, snap_for_xdot: dict | None, xdot_kind: str):
    u = state["unp"].astype(np.float64)
    p = state["per"].astype(np.float64)
    if xdot_kind == "spin-relative":
        ref = snap_for_xdot["unp_snap"]
        return u - ref, p - ref
    return u - state["unp_prev"].astype(np.float64), p - state["per_prev"].astype(np.float64)


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


def multi_window_fdr_iter(T, t_w, t_obs, tau_windows, h_field,
                           n_realizations, seed, n_sample_times,
                           progress_every=0, xdot_kind="spin-flip") -> Iterator[dict]:
    return stream_fdr(
        substrate="east", op_label=f"T{T:.2f}",
        op_params={"T": float(T), "L": L_CHAIN},
        t_w=t_w, t_obs=t_obs, tau_windows=tau_windows, h_field=h_field,
        n_realizations=n_realizations, seed=seed,
        n_sample_times=n_sample_times, xdot_kind=xdot_kind,
        xdot_kinds_allowed=XDOT_KINDS, ema_in_phase_a=EMA_IN_PHASE_A,
        init_state=_init_state(T), advance_one_sweep=_advance,
        xdot_field=_xdot, raw_C_chi=_raw_C_chi,
        fork_paired_branch=_fork, snapshot_state=_snapshot,
    )
