"""Active Brownian Particle (2D, single-particle) streaming primitive.

Overdamped Langevin:
    r(t+dt) = r + v0·(cos θ, sin θ)·dt + sqrt(2·D_t·dt)·ξ
    θ(t+dt) = θ + sqrt(2·D_r·dt)·η + h_extra·dt   (extra bias on θ)

Perturbed branch sees an additional torque h_field on the orientation
angle θ. chi reads the response of mean angular momentum proxy
<sin θ> as a function of the orientational perturbation.

Per-step xdot = v0·n̂(θ) + thermal increment (per-step velocity);
snapshot-relative xdot = r(t) - r(t_snap).
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
DT = 0.05
D_T = 1.0   # translational diffusion
D_R = 1.0   # rotational diffusion


def _init_state(Pe: float):
    def factory(rng: np.random.Generator, n_real: int) -> dict:
        # (n_real, 2): (x, y); theta separate.
        r = np.zeros((n_real, 2), dtype=np.float64)
        theta = rng.uniform(-math.pi, math.pi, size=(n_real,))
        return {
            "unp": r.copy(), "per": r.copy(),
            "unp_prev": r.copy(), "per_prev": r.copy(),
            "theta_unp": theta.copy(), "theta_per": theta.copy(),
            "Pe": float(Pe),
        }
    return factory


def _advance(state: dict, h_extra_per: float, rng: np.random.Generator):
    n_real, _ = state["unp"].shape
    v0 = state["Pe"] * math.sqrt(D_T * D_R)
    s_t = math.sqrt(2.0 * D_T * DT)
    s_r = math.sqrt(2.0 * D_R * DT)
    xi_x = rng.standard_normal(size=(n_real,)) * s_t
    xi_y = rng.standard_normal(size=(n_real,)) * s_t
    eta = rng.standard_normal(size=(n_real,)) * s_r
    state["unp_prev"] = state["unp"].copy()
    state["per_prev"] = state["per"].copy()
    # Update theta first (CRN noise on both branches).
    state["theta_unp"] = state["theta_unp"] + eta
    state["theta_per"] = state["theta_per"] + eta + h_extra_per * DT
    # Propel.
    drx_unp = v0 * np.cos(state["theta_unp"]) * DT + xi_x
    dry_unp = v0 * np.sin(state["theta_unp"]) * DT + xi_y
    drx_per = v0 * np.cos(state["theta_per"]) * DT + xi_x
    dry_per = v0 * np.sin(state["theta_per"]) * DT + xi_y
    state["unp"][:, 0] += drx_unp
    state["unp"][:, 1] += dry_unp
    state["per"][:, 0] += drx_per
    state["per"][:, 1] += dry_per


def _xdot(state: dict, snap_for_xdot: dict | None, xdot_kind: str):
    if xdot_kind == "position-relative":
        ref = snap_for_xdot["unp_snap"]
        return state["unp"] - ref, state["per"] - ref
    return state["unp"] - state["unp_prev"], state["per"] - state["per_prev"]


def _raw_C_chi(state: dict, snap_at_tw: dict, h_field: float):
    return ensemble_C_chi(
        state["unp"], snap_at_tw["unp_snap"], state["per"], h_field,
    )


def _fork(state: dict):
    state["per"] = state["unp"].copy()
    state["per_prev"] = state["unp_prev"].copy()
    state["theta_per"] = state["theta_unp"].copy()


def _snapshot(state: dict) -> dict:
    return {"unp_snap": state["unp"].copy()}


def multi_window_fdr_iter(Pe, t_w, t_obs, tau_windows, h_field,
                           n_realizations, seed, n_sample_times,
                           progress_every=0, xdot_kind="velocity") -> Iterator[dict]:
    return stream_fdr(
        substrate="abp", op_label=f"Pe{Pe:g}",
        op_params={"Pe": float(Pe), "D_t": D_T, "D_r": D_R, "dt": DT},
        t_w=t_w, t_obs=t_obs, tau_windows=tau_windows, h_field=h_field,
        n_realizations=n_realizations, seed=seed,
        n_sample_times=n_sample_times, xdot_kind=xdot_kind,
        xdot_kinds_allowed=XDOT_KINDS, ema_in_phase_a=EMA_IN_PHASE_A,
        init_state=_init_state(Pe), advance_one_sweep=_advance,
        xdot_field=_xdot, raw_C_chi=_raw_C_chi,
        fork_paired_branch=_fork, snapshot_state=_snapshot,
    )
