"""Voter model with time-fluctuating external bias — streaming primitive.

Mean-field (fully connected) noisy voter on N agents in {-1, +1}. An
external bias field h_ext(t) flips between +h_amp and -h_amp at switching
rate ν (operating-point parameter). Each Monte-Carlo sweep = N single-
agent updates; each update picks a random pair (i, j), agent i copies
agent j's opinion with a bias-tilted rule:

    P(s_i ← s_j) = (1 + tanh(beta_link * s_j + h_ext(t) + h_extra)) / 2

For zero h_extra this reduces to the standard noisy-voter limit. The
paired protocol uses the same noise stream on (unp, per) branches; the
perturbed branch has h_extra = h_field.

Ensemble-stacked: N_real replicas advance simultaneously through numpy
broadcasting on the leading axis. SEM is computed at sample time across
the replica axis.

Event shape per `_shared/runtime.py` (init / sample / complete; phase_a /
phase_b / snapshot suppressed for brevity).

Per-step xdot:
  opinion-flip:     ẋ_i(t) = s_i(t) - s_i(t-1)   ∈ {-2, 0, +2}
  opinion-relative: ẋ_i(t) = s_i(t) - s_i(t_snap)  ∈ {-2, 0, +2}
"""
from __future__ import annotations

import math
from typing import Iterator, Sequence

import numpy as np

XDOT_KINDS = ("opinion-flip", "opinion-relative")
EMA_IN_PHASE_A = {"opinion-flip": True, "opinion-relative": False}
N_AGENTS = 200
BETA_LINK = 1.0         # link coupling strength; bias-tilt amplitude
H_AMP = 0.4             # amplitude of the switching external bias


def _snapshot_offset(xdot_kind: str, tau_max: float) -> int:
    return 0 if EMA_IN_PHASE_A[xdot_kind] else int(5 * tau_max)


def _step_paired(
    s_unp: np.ndarray,       # (n_real, N) ∈ {-1, +1} int8
    s_per: np.ndarray,
    h_ext: np.ndarray,       # (n_real,)
    h_extra_per: float,      # additive bias on perturbed branch
    beta_link: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Run one sweep (N single-agent updates) on n_real replicas, with
    matched noise across (unp, per). Returns updated (s_unp, s_per)."""
    n_real, N = s_unp.shape
    # Pre-sample sweep-worth of indices and uniform draws (CRN: shared
    # across unp and per branches).
    idx_i = rng.integers(0, N, size=(N, n_real))     # target agent
    idx_j = rng.integers(0, N, size=(N, n_real))     # source agent
    u     = rng.random(size=(N, n_real))             # acceptance draw
    for step in range(N):
        i = idx_i[step]; j = idx_j[step]
        row = np.arange(n_real)
        sj_unp = s_unp[row, j]
        sj_per = s_per[row, j]
        # P(adopt s_j) = (1 + tanh(beta·s_j + h)) / 2
        p_unp = 0.5 * (1.0 + np.tanh(beta_link * sj_unp + h_ext))
        p_per = 0.5 * (1.0 + np.tanh(beta_link * sj_per + h_ext + h_extra_per))
        # Same acceptance draw on both branches (CRN variance reduction).
        accept_unp = u[step] < p_unp
        accept_per = u[step] < p_per
        # Adopt +1 if accepted else -1, when there's an actual update;
        # otherwise keep current opinion. We treat the rule as: with prob
        # p, set s_i = +1; with prob 1−p, set s_i = −1. (The Mobilia rule
        # is "copy s_j with bias", which under symmetric tanh has this
        # equivalent representation.)
        new_unp = np.where(accept_unp, 1, -1).astype(s_unp.dtype)
        new_per = np.where(accept_per, 1, -1).astype(s_per.dtype)
        s_unp[row, i] = new_unp
        s_per[row, i] = new_per
    return s_unp, s_per


def multi_window_fdr_iter(
    nu: float,
    t_w: int,
    t_obs: int,
    tau_windows: Sequence[float],
    h_field: float = 0.10,
    n_realizations: int = 256,
    seed: int = 0,
    sample_times: Sequence[int] | None = None,
    n_sample_times: int = 31,
    progress_every: int = 0,
    xdot_kind: str = "opinion-flip",
) -> Iterator[dict]:
    if xdot_kind not in XDOT_KINDS:
        raise ValueError(f"unknown xdot_kind: {xdot_kind!r}")

    tau_windows = list(map(float, tau_windows))
    n_w = len(tau_windows)
    tau_max = max(tau_windows)
    alphas = np.array([math.exp(-1.0 / t) for t in tau_windows])

    t_kw = _snapshot_offset(xdot_kind, tau_max)
    t_snap = int(t_w) + int(t_kw)
    t_max = t_snap + int(t_obs)

    if sample_times is None:
        from _shared.runtime import log_sample_times
        sample_times = log_sample_times(t_snap, t_max, n_sample_times)
    sample_lookup = set(int(t) for t in sample_times)

    n_real = max(1, int(n_realizations))
    rng = np.random.default_rng(int(seed))

    # Initial state: random ±1.
    s_unp = rng.choice(np.array([-1, 1], dtype=np.int8),
                       size=(n_real, N_AGENTS))
    s_unp_prev = s_unp.copy()

    # External-bias state per replica (independent switches).
    h_state = rng.choice(np.array([-1, 1], dtype=np.int8), size=(n_real,))

    d_unp = np.zeros((n_w, n_real, N_AGENTS), dtype=np.float64)

    yield {
        "type": "init",
        "substrate": "voter",
        "nu": float(nu),
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

    ema_in_a = EMA_IN_PHASE_A[xdot_kind]
    snap_for_xdot = None
    snap_at_tw = None

    # ── Phase A: equilibrate (no perturbation, no perturbed branch yet) ──
    s_per = s_unp.copy()
    s_per_prev = s_unp.copy()
    for t_pre in range(1, int(t_w) + 1):
        # External-bias switches: per replica, flip with prob 1 - exp(-ν)
        flip_prob = 1.0 - math.exp(-float(nu))
        flips = rng.random(size=(n_real,)) < flip_prob
        h_state = np.where(flips, -h_state, h_state).astype(np.int8)
        h_ext_now = H_AMP * h_state.astype(np.float64)

        s_unp, _ = _step_paired(s_unp, s_per, h_ext_now, 0.0, BETA_LINK, rng)
        if ema_in_a:
            ds = (s_unp.astype(np.float64) - s_unp_prev.astype(np.float64))
            for k in range(n_w):
                d_unp[k] = alphas[k] * d_unp[k] + ds
        s_unp_prev = s_unp.copy()
        s_per = s_unp.copy()           # not forked yet
        s_per_prev = s_per.copy()

    # Substrate snapshot at t_w.
    snap_at_tw = s_unp.astype(np.float64).copy()
    if xdot_kind == "opinion-relative":
        snap_for_xdot = s_unp.astype(np.float64).copy()

    # ── Kernel warmup [t_w, t_w + t_kw) for opinion-relative ──
    for t_kw_step in range(1, int(t_kw) + 1):
        flip_prob = 1.0 - math.exp(-float(nu))
        flips = rng.random(size=(n_real,)) < flip_prob
        h_state = np.where(flips, -h_state, h_state).astype(np.int8)
        h_ext_now = H_AMP * h_state.astype(np.float64)
        s_unp, _ = _step_paired(s_unp, s_per, h_ext_now, 0.0, BETA_LINK, rng)
        if xdot_kind == "opinion-relative":
            ds = (s_unp.astype(np.float64) - snap_for_xdot)
            for k in range(n_w):
                d_unp[k] = alphas[k] * d_unp[k] + ds
        s_unp_prev = s_unp.copy()
        s_per = s_unp.copy()
        s_per_prev = s_per.copy()

    d_at_tw = d_unp.copy()
    d_per = d_unp.copy()
    s_per = s_unp.copy()
    s_per_prev = s_unp.copy()

    yield {
        "type": "snapshot",
        "t": int(t_snap), "t_w": int(t_w),
        "t_kw": int(t_kw), "t_snap": int(t_snap),
    }

    # ── Measurement window: paired evolution, perturbation on perturbed ──
    from _shared.runtime import per_window_observables, ensemble_C_chi
    for t_after in range(1, int(t_obs) + 1):
        flip_prob = 1.0 - math.exp(-float(nu))
        flips = rng.random(size=(n_real,)) < flip_prob
        h_state = np.where(flips, -h_state, h_state).astype(np.int8)
        h_ext_now = H_AMP * h_state.astype(np.float64)

        s_unp, s_per = _step_paired(
            s_unp, s_per, h_ext_now, float(h_field), BETA_LINK, rng,
        )
        if xdot_kind == "opinion-relative":
            ds_unp = (s_unp.astype(np.float64) - snap_for_xdot)
            ds_per = (s_per.astype(np.float64) - snap_for_xdot)
        else:
            ds_unp = (s_unp.astype(np.float64) - s_unp_prev.astype(np.float64))
            ds_per = (s_per.astype(np.float64) - s_per_prev.astype(np.float64))
        for k in range(n_w):
            d_unp[k] = alphas[k] * d_unp[k] + ds_unp
            d_per[k] = alphas[k] * d_per[k] + ds_per
        s_unp_prev = s_unp.copy()
        s_per_prev = s_per.copy()

        t_abs = t_snap + t_after
        if t_abs in sample_lookup:
            C_m, C_s, chi_m, chi_s = ensemble_C_chi(
                s_unp.astype(np.float64),
                snap_at_tw,
                s_per.astype(np.float64),
                float(h_field),
            )
            per_window = per_window_observables(
                d_unp, d_per, d_at_tw,
                float(h_field), tau_windows,
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
