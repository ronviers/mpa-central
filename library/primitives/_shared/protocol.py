"""Generic paired-trajectory FDR protocol loop for in-library primitives.

The substrate-agnostic skeleton:

    phase A (t_w steps, no perturbation, no fork)
    snapshot at t_w
    kernel warmup (only for snapshot-relative ẋ; t_kw = 5·τ_max)
    fork unperturbed/perturbed branches
    measurement window (t_obs paired steps, h_field on perturbed branch,
                        sample at log-spaced t_abs)

Differs across substrates only in the state-update step and the raw-
readout C/chi formula. Each substrate's measurements.py provides those
two callbacks and calls `stream_fdr(...)`.
"""
from __future__ import annotations

import math
from typing import Callable, Iterator, Sequence

import numpy as np

from .runtime import log_sample_times, per_window_observables, ensemble_C_chi


def stream_fdr(
    *,
    substrate: str,
    op_label: str,
    op_params: dict,
    t_w: int,
    t_obs: int,
    tau_windows: Sequence[float],
    h_field: float,
    n_realizations: int,
    seed: int,
    n_sample_times: int,
    xdot_kind: str,
    xdot_kinds_allowed: tuple[str, ...],
    ema_in_phase_a: dict[str, bool],
    init_state: Callable[[np.random.Generator, int], dict],
    advance_one_sweep: Callable[[dict, float, np.random.Generator], None],
    xdot_field: Callable[[dict, dict | None, str], tuple[np.ndarray, np.ndarray]],
    raw_C_chi: Callable[[dict, dict, float], tuple[float, float, float, float]],
    fork_paired_branch: Callable[[dict], None],
    snapshot_state: Callable[[dict], dict],
    extra_init_fields: dict | None = None,
) -> Iterator[dict]:
    """Stream init / snapshot / sample / complete events for one cell.

    Callbacks:
      init_state(rng, n_real) -> state dict
          Required keys: 'unp' (any ndarray with leading axis = n_real),
                         'per' (set equal to 'unp' initially),
                         'unp_prev' (copy of 'unp'),
                         'per_prev' (copy of 'per').
          May carry substrate-specific scratch (e.g. couplings, h_ext_state).

      advance_one_sweep(state, h_extra_per, rng)
          Advance both branches one sweep in-place. h_extra_per is the
          additive perturbation on the perturbed branch (0 during phase A;
          h_field during measurement). The unperturbed branch sees no
          extra bias either way.

      xdot_field(state, snap_for_xdot, xdot_kind) -> (ds_unp, ds_per)
          Per-replica xdot fields. ds shape: (n_real, ...) consistent
          across calls. For "*-flip" kinds use state['unp'] - state['unp_prev'].
          For "*-relative" kinds use state['unp'] - snap_for_xdot['unp'].

      raw_C_chi(state, snap_at_tw, h_field) -> (C, C_sem, chi, chi_sem)
          Compute raw-readout substrate observables.

      fork_paired_branch(state)
          At t_snap, ensure state['per'] is a fresh copy of state['unp'].
          (For most substrates: state['per'] = state['unp'].copy().)

      snapshot_state(state) -> dict
          Deep snapshot of state for the *_relative ẋ reference and for
          raw_C_chi at sample time.
    """
    if xdot_kind not in xdot_kinds_allowed:
        raise ValueError(f"unknown xdot_kind: {xdot_kind!r}")

    tau_windows = list(map(float, tau_windows))
    n_w = len(tau_windows)
    tau_max = max(tau_windows)
    alphas = np.array([math.exp(-1.0 / t) for t in tau_windows])

    ema_in_a = ema_in_phase_a[xdot_kind]
    t_kw = 0 if ema_in_a else int(5 * tau_max)
    t_snap = int(t_w) + int(t_kw)
    t_max = t_snap + int(t_obs)

    sample_times = log_sample_times(t_snap, t_max, n_sample_times)
    sample_lookup = set(int(t) for t in sample_times)

    n_real = max(1, int(n_realizations))
    rng = np.random.default_rng(int(seed))
    state = init_state(rng, n_real)

    init_payload = {
        "type": "init",
        "substrate": substrate,
        "op_label": op_label,
        "op_params": op_params,
        "t_w": int(t_w), "t_kw": int(t_kw),
        "t_snap": int(t_snap), "t_obs": int(t_obs),
        "tau_windows": tau_windows,
        "h_field": float(h_field),
        "n_realizations": n_real,
        "seed": int(seed),
        "xdot_kind": xdot_kind,
        "sample_times": sorted(sample_lookup),
        "n_samples_planned": len(sample_lookup),
    }
    if extra_init_fields:
        init_payload.update(extra_init_fields)
    yield init_payload

    # Determine trail-field shape from a probe step.
    # Phase A: equilibrate. EMA only if ẋ reference is available.
    # During phase A, the perturbed branch tracks the unperturbed (no fork).
    d_unp = None

    for t_pre in range(1, int(t_w) + 1):
        advance_one_sweep(state, 0.0, rng)
        if ema_in_a:
            ds_unp, _ = xdot_field(state, None, xdot_kind)
            if d_unp is None:
                d_unp = np.zeros((n_w,) + ds_unp.shape, dtype=np.float64)
            for k in range(n_w):
                d_unp[k] = alphas[k] * d_unp[k] + ds_unp
        # Keep per = unp (no perturbation yet).
        state["per"] = state["unp"].copy()
        state["per_prev"] = state["unp_prev"].copy()

    snap_at_tw = snapshot_state(state)
    snap_for_xdot = snap_at_tw if not ema_in_a else None

    # Kernel warmup (only for *_relative ẋ).
    for t_kw_step in range(1, int(t_kw) + 1):
        advance_one_sweep(state, 0.0, rng)
        ds_unp, _ = xdot_field(state, snap_for_xdot, xdot_kind)
        if d_unp is None:
            d_unp = np.zeros((n_w,) + ds_unp.shape, dtype=np.float64)
        for k in range(n_w):
            d_unp[k] = alphas[k] * d_unp[k] + ds_unp
        state["per"] = state["unp"].copy()
        state["per_prev"] = state["unp_prev"].copy()

    # If phase A had no EMA *and* t_kw=0, init d_unp with zeros after we
    # know the shape from one probe (rare; guard).
    if d_unp is None:
        ds_unp, _ = xdot_field(state, snap_for_xdot, xdot_kind)
        d_unp = np.zeros((n_w,) + ds_unp.shape, dtype=np.float64)

    d_at_tw = d_unp.copy()
    d_per = d_unp.copy()
    fork_paired_branch(state)

    yield {
        "type": "snapshot",
        "t": int(t_snap), "t_w": int(t_w),
        "t_kw": int(t_kw), "t_snap": int(t_snap),
    }

    # Measurement window.
    for t_after in range(1, int(t_obs) + 1):
        advance_one_sweep(state, float(h_field), rng)
        ds_unp, ds_per = xdot_field(state, snap_for_xdot, xdot_kind)
        for k in range(n_w):
            d_unp[k] = alphas[k] * d_unp[k] + ds_unp
            d_per[k] = alphas[k] * d_per[k] + ds_per

        t_abs = t_snap + t_after
        if t_abs in sample_lookup:
            C_m, C_s, chi_m, chi_s = raw_C_chi(state, snap_at_tw, float(h_field))
            per_window = per_window_observables(
                d_unp, d_per, d_at_tw, float(h_field), tau_windows,
            )
            yield {
                "type": "sample",
                "t": int(t_abs),
                "t_w": int(t_w),
                "t_snap": int(t_snap),
                "dt": int(t_after),
                "xdot_kind": xdot_kind,
                "C": C_m, "C_sem": C_s,
                "chi": chi_m, "chi_sem": chi_s,
                "per_window": per_window,
                "n_realizations": n_real,
            }

    yield {
        "type": "complete",
        "t_w": int(t_w), "t_kw": int(t_kw),
        "t_snap": int(t_snap), "t_obs": int(t_obs),
        "xdot_kind": xdot_kind,
    }
