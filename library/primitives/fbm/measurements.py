"""Fractional Brownian motion streaming primitive.

Each replica is a 1D fBM trajectory with Hurst exponent H. We generate
the noise sequence (fGn) up-front via the Davies-Harte spectral method
(or fallback to AR-like increments for moderate length) and integrate
incrementally during the paired protocol.

The perturbed branch adds a small constant drift h_field·dt per step.
chi is the response of mean position to this drift.
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


def _fgn_sequence(H: float, n: int, n_real: int, rng: np.random.Generator) -> np.ndarray:
    """Davies-Harte generation of fractional Gaussian noise.
    Returns (n_real, n) increment sequences with H-correlation."""
    k = np.arange(0, n + 1)
    gamma = 0.5 * (np.abs(k - 1) ** (2 * H) - 2 * np.abs(k) ** (2 * H)
                   + np.abs(k + 1) ** (2 * H))
    # Build circulant first row of length 2n.
    c = np.concatenate([gamma, gamma[1:n][::-1]])
    lam = np.fft.fft(c).real
    # Numerical guard against tiny negatives.
    lam = np.maximum(lam, 0.0)
    sqrt_lam = np.sqrt(lam)
    m = 2 * n
    # Generate complex Gaussians; FFT to get real fGn sequences.
    out = np.empty((n_real, n), dtype=np.float64)
    for r in range(n_real):
        Z = (rng.standard_normal(m) + 1j * rng.standard_normal(m)) / math.sqrt(2.0)
        # Hermitian symmetry: real-valued output for the circulant trick.
        W = sqrt_lam * Z
        x = np.fft.fft(W).real / math.sqrt(m)
        out[r] = x[:n]
    return out


def _init_state(H: float, total_steps: int):
    def factory(rng: np.random.Generator, n_real: int) -> dict:
        # Pre-generate the fGn increment sequence (shared base; the
        # perturbed branch adds drift on top — variance-reduction CRN).
        # Cap total_steps for memory safety; if it exceeds 100k, fall
        # back to per-step AR increments (Hurst<-> Brownian limit).
        n = int(total_steps) + 10
        if n <= 200_000:
            fgn = _fgn_sequence(float(H), n, n_real, rng)
        else:
            # Long-range memory unavailable at this scale; treat as Brownian.
            fgn = rng.standard_normal(size=(n_real, n))
        return {
            "unp": np.zeros((n_real, 1), dtype=np.float64),
            "per": np.zeros((n_real, 1), dtype=np.float64),
            "unp_prev": np.zeros((n_real, 1), dtype=np.float64),
            "per_prev": np.zeros((n_real, 1), dtype=np.float64),
            "fgn": fgn, "step_idx": 0, "H": float(H),
        }
    return factory


def _advance(state: dict, h_extra_per: float, rng: np.random.Generator):
    i = state["step_idx"]
    n_real = state["unp"].shape[0]
    if i >= state["fgn"].shape[1]:
        # Out of pre-generated noise; extend by drawing fresh Brownian.
        extra = rng.standard_normal(size=(n_real, 1024))
        state["fgn"] = np.concatenate([state["fgn"], extra], axis=1)
    dx = state["fgn"][:, i:i + 1]
    state["unp_prev"] = state["unp"].copy()
    state["per_prev"] = state["per"].copy()
    state["unp"] = state["unp"] + dx
    state["per"] = state["per"] + dx + h_extra_per
    state["step_idx"] = i + 1


def _xdot(state: dict, snap_for_xdot: dict | None, xdot_kind: str):
    if xdot_kind == "position-relative":
        return state["unp"] - snap_for_xdot["unp_snap"], state["per"] - snap_for_xdot["unp_snap"]
    return state["unp"] - state["unp_prev"], state["per"] - state["per_prev"]


def _raw_C_chi(state: dict, snap_at_tw: dict, h_field: float):
    return ensemble_C_chi(state["unp"], snap_at_tw["unp_snap"], state["per"], h_field)


def _fork(state: dict):
    state["per"] = state["unp"].copy()
    state["per_prev"] = state["unp_prev"].copy()


def _snapshot(state: dict) -> dict:
    return {"unp_snap": state["unp"].copy()}


def multi_window_fdr_iter(H, t_w, t_obs, tau_windows, h_field,
                           n_realizations, seed, n_sample_times,
                           progress_every=0, xdot_kind="velocity") -> Iterator[dict]:
    total = int(t_w) + int(5 * max(tau_windows)) + int(t_obs) + 10
    return stream_fdr(
        substrate="fbm", op_label=f"H{H:.2f}",
        op_params={"H": float(H)},
        t_w=t_w, t_obs=t_obs, tau_windows=tau_windows, h_field=h_field,
        n_realizations=n_realizations, seed=seed,
        n_sample_times=n_sample_times, xdot_kind=xdot_kind,
        xdot_kinds_allowed=XDOT_KINDS, ema_in_phase_a=EMA_IN_PHASE_A,
        init_state=_init_state(H, total),
        advance_one_sweep=_advance, xdot_field=_xdot,
        raw_C_chi=_raw_C_chi,
        fork_paired_branch=_fork, snapshot_state=_snapshot,
    )
