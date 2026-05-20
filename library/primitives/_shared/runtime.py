"""Shared runtime for in-library substrate primitives.

Two run modes:
- `run(...)`          serial; useful for --smoke and debugging.
- `run_parallel(...)` per-cell ProcessPoolExecutor; default for full
                      grinds. Mirrors grind_library.py's external-loop
                      pattern, but parallelizing across cells rather
                      than across realizations.

Each in-library primitive (`primitives/<name>/`) is a thin self-contained
adapter/simulator. They differ in physics but share the same grind loop:
sweep operating points × xdot_kinds, call the primitive once per cell,
write a library-spec-v1.0 JSON cell to `library/data/<name>/`.

This module centralizes that loop so each primitive's `grind.py` is a
few lines of substrate-specific config plus a single `run()` call.

Contract for a primitive's `multi_window_fdr_iter(...)`:

  - Yields events with shape:
      {"type": "init",   ..., "t_kw", "t_snap", "h_field", ...}
      {"type": "sample", "t", "dt",
                          "C", "C_sem",
                          "chi", "chi_sem",
                          "per_window": [
                              {"tau_window", "C_d", "C_d_sem",
                               "C_d_diag", "C_d_diag_sem",
                               "chi_d", "chi_d_sem",
                               "d_norm", "d_norm_sem",
                               "sigma_d", "sigma_d_sem",
                               "f", "f_sem"},
                              ...
                          ],
                          "n_realizations": int}
      {"type": "complete", ...}

  - Does its own ensemble averaging across `n_realizations` (numpy-vectorized
    leading-axis stacking is the canonical move). SEM = std / sqrt(n_real).
  - Accepts at minimum:
      t_w, t_obs, tau_windows, h_field, n_realizations, seed,
      progress_every, xdot_kind
    plus whatever operating-point parameter is substrate-specific (T, p, nu, ...).

  - Returns SEM ON THE INTERNAL AGGREGATE. This is structurally different
    from brain (which emits *_sem = None) and is the chi-convention
    direction that brain owes per `H:/mpa-conform/docs/papers/chi_convention_lock_in.md`.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Callable, Iterator, Sequence

# Pin BLAS/OpenMP to a single thread *before* numpy imports its math
# backends. Each ProcessPoolExecutor worker pinned this way avoids
# oversubscribing the 13900KF's 32 logical processors when running
# many cells in parallel. Set as defaults so a user export takes
# precedence if they really want multithreaded BLAS for some reason.
for _k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


LIBRARY_SPEC_VERSION = "1.0"
LIBRARY_ROOT = Path("H:/mpa-central/library")
DATA_ROOT = LIBRARY_ROOT / "data"


# ─── τ_env-anchored time grids (copied from grind_library.py) ───────────────

LIB_FALLBACK_T_W = 500
LIB_FALLBACK_T_OBS = 30000
LIB_FALLBACK_TAU_WINDOWS = tuple(
    round(x, 3) for x in np.geomspace(1.0, 1000.0, 31).tolist()
)
LIB_N_SAMPLE_TIMES = 31

LIB_TAU_OBS_LO_FRAC = 0.05
LIB_TAU_OBS_HI_FRAC = 2.0
LIB_TAU_OBS_HI_CAP = 5000
LIB_T_OBS_AGING_FACTOR = 30
LIB_T_OBS_RULE8_FACTOR = 10
LIB_T_OBS_CAP = 200_000
LIB_T_W_FACTOR = 5
LIB_T_W_FLOOR = 500
LIB_T_W_CAP = 5000

# Smoke-mode budgets — enough to verify imports + primitive signatures, no more
SMOKE_TAU_WINDOWS = (3.0, 30.0, 300.0)
SMOKE_T_W = 50
SMOKE_T_OBS = 500
SMOKE_N_SAMPLE_TIMES = 6
SMOKE_N_REAL = 8


def time_grids_for(tau_env: float | None, smoke: bool = False):
    """Per-operating-point τ-grid scaling per LIBRARY_SPEC §τ_env-anchored
    sampling. Returns (tau_windows, t_w, t_obs, n_sample_times).
    """
    if smoke:
        return SMOKE_TAU_WINDOWS, SMOKE_T_W, SMOKE_T_OBS, SMOKE_N_SAMPLE_TIMES
    if tau_env is None or tau_env <= 0 or not math.isfinite(tau_env):
        return (
            LIB_FALLBACK_TAU_WINDOWS,
            LIB_FALLBACK_T_W,
            LIB_FALLBACK_T_OBS,
            LIB_N_SAMPLE_TIMES,
        )
    tw_lo = max(1.0, LIB_TAU_OBS_LO_FRAC * tau_env)
    tw_hi = min(LIB_TAU_OBS_HI_CAP, LIB_TAU_OBS_HI_FRAC * tau_env)
    if tw_hi <= tw_lo:
        tw_hi = tw_lo * 10
    tau_windows = tuple(
        round(x, 3) for x in np.geomspace(tw_lo, tw_hi, 31).tolist()
    )
    rule8_floor = LIB_T_OBS_RULE8_FACTOR * max(tau_windows)
    aging_target = LIB_T_OBS_AGING_FACTOR * tau_env
    t_obs = int(min(LIB_T_OBS_CAP, max(rule8_floor, aging_target)))
    t_w = int(min(LIB_T_W_CAP, max(LIB_T_W_FLOOR, LIB_T_W_FACTOR * tau_env)))
    return tau_windows, t_w, t_obs, LIB_N_SAMPLE_TIMES


def log_sample_times(t_snap: int, t_max: int, n: int) -> list[int]:
    """Log-spaced absolute sample times in (t_snap, t_max]. Unique ints,
    sorted, with at least one sample at t_max."""
    n = max(2, int(n))
    lo = max(1, t_snap + 1)
    hi = max(lo + 1, t_max)
    grid = np.geomspace(1.0, float(hi - t_snap), n)
    out = sorted({t_snap + int(round(x)) for x in grid})
    out = [t for t in out if lo <= t <= hi]
    if not out or out[-1] != hi:
        out.append(hi)
    return out


# ─── Atomic JSON writer ───────────────────────────────────────────────────

def write_json_atomic(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, default=float)
    os.replace(tmp, path)


# ─── Cell builder ─────────────────────────────────────────────────────────

def _sample_event_to_cell_row(ev: dict) -> dict:
    """Convert a primitive sample event to the cell schema's per-row shape."""
    per_window = []
    for w in ev["per_window"]:
        per_window.append({
            "tau_window": w["tau_window"],
            "C_d_mean": w.get("C_d"),       "C_d_sem":      w.get("C_d_sem"),
            "C_d_diag_mean": w.get("C_d_diag"), "C_d_diag_sem": w.get("C_d_diag_sem"),
            "chi_d_mean": w.get("chi_d"),   "chi_d_sem":    w.get("chi_d_sem"),
            "d_norm_mean": w.get("d_norm"), "d_norm_sem":   w.get("d_norm_sem"),
            "sigma_d_mean": w.get("sigma_d"), "sigma_d_sem": w.get("sigma_d_sem"),
            "f_mean": w.get("f"),           "f_sem":        w.get("f_sem"),
            "n_realizations": w.get("n_realizations", ev.get("n_realizations")),
        })
    return {
        "t": int(ev["t"]),
        "dt": int(ev["dt"]),
        "C_mean": ev.get("C"),
        "C_sem":  ev.get("C_sem"),
        "chi_mean": ev.get("chi"),
        "chi_sem":  ev.get("chi_sem"),
        "per_window": per_window,
        "n_realizations": ev.get("n_realizations"),
    }


# ─── Grind loop ──────────────────────────────────────────────────────────

def run(
    *,
    substrate: str,
    operating_points: list[dict],
    xdot_kinds: list[str],
    tau_env_for: Callable[[dict], dict],
    primitive_fn: Callable[..., Iterator[dict]],
    kwargs_for: Callable[[dict, str, dict, int], dict],
    primitive_module_name: str,
    n_realizations: int,
    fidelity: dict | None = None,
    smoke: bool = False,
    only_op_labels: list[str] | None = None,
    only_xdot: list[str] | None = None,
):
    """Run the grind loop for one in-library substrate.

    operating_points: list of dicts; each MUST carry "label" and "gt"
        plus substrate-specific parameter fields (T, nu, R0, ...).
    xdot_kinds: list of ẋ choice names the primitive understands.
    tau_env_for(op) -> {value, method, note}: analytic τ_env per op.
    primitive_fn: the substrate's multi_window_fdr_iter generator.
    kwargs_for(op, xdot_kind, schedule, n_real) -> kwargs for primitive_fn.
    primitive_module_name: dotted module path written into the cell.
    n_realizations: cell-level realisation count (smoke override).
    fidelity: optional substrate-fidelity dict (L, N, distance, ...).
    only_op_labels / only_xdot: optional filters for partial reruns.

    Cells land in `data/<substrate>/<substrate>__<op.label>__<xdot>.json`.
    """
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    (DATA_ROOT / substrate).mkdir(parents=True, exist_ok=True)

    n_real = SMOKE_N_REAL if smoke else int(n_realizations)
    print(f"[grind:{substrate}] start  smoke={smoke}  n_real={n_real}", flush=True)

    total = len(operating_points) * len(xdot_kinds)
    done = 0
    t_overall = time.time()

    for op in operating_points:
        if only_op_labels and op["label"] not in only_op_labels:
            done += len(xdot_kinds)
            continue

        tau_env_block = tau_env_for(op)
        tau_env_value = tau_env_block.get("value")
        tau_windows, t_w, t_obs, n_sample_times = time_grids_for(
            tau_env_value, smoke=smoke,
        )

        for xdot_kind in xdot_kinds:
            done += 1
            if only_xdot and xdot_kind not in only_xdot:
                continue

            task_id = f"{substrate}__{op['label']}__{xdot_kind}"
            out_path = DATA_ROOT / substrate / f"{task_id}.json"
            print(f"[grind:{substrate}] [{done:>3}/{total}] RUN  {task_id}  "
                  f"(τ_env={tau_env_value}, t_w={t_w}, t_obs={t_obs}, "
                  f"n_real={n_real})", flush=True)

            schedule = {
                "t_w": int(t_w),
                "t_obs": int(t_obs),
                "tau_windows": list(tau_windows),
                "n_sample_times": int(n_sample_times),
            }

            t0 = time.time()
            try:
                kwargs = kwargs_for(op, xdot_kind, schedule, n_real)
                init_ev = None
                all_samples: list[dict] = []
                for ev in primitive_fn(**kwargs):
                    et = ev.get("type")
                    if et == "init":
                        init_ev = ev
                    elif et == "sample":
                        all_samples.append(_sample_event_to_cell_row(ev))
                wall = time.time() - t0
            except Exception as e:
                wall = time.time() - t0
                tb = traceback.format_exc()
                print(f"[grind:{substrate}] [{done:>3}/{total}] FAIL {task_id}  "
                      f"wall={wall:.1f}s  err={e}", flush=True)
                print(tb, file=sys.stderr, flush=True)
                continue

            payload = {
                "library_spec_version": LIBRARY_SPEC_VERSION,
                "substrate": substrate,
                "operating_point": op,
                "xdot_kind": xdot_kind,
                "fidelity": fidelity or {"L": None, "distance": None},
                "schedule": {**schedule, "n_realizations": n_real},
                "tau_env_analytic": tau_env_block,
                "tau_env_measured": None,
                "results": {
                    "init_event_t_kw":    (init_ev or {}).get("t_kw"),
                    "init_event_t_snap":  (init_ev or {}).get("t_snap"),
                    "init_event_h_field": (init_ev or {}).get("h_field"),
                    "all_samples": all_samples,
                    "sem_available": True,
                    "sem_unavailable_reason": None,
                },
                "wall_seconds": wall,
                "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "primitive_module": primitive_module_name,
            }
            if not smoke:
                write_json_atomic(out_path, payload)
            print(f"[grind:{substrate}] [{done:>3}/{total}] DONE {task_id}  "
                  f"wall={wall:.1f}s  samples={len(all_samples)}",
                  flush=True)

    elapsed = time.time() - t_overall
    print(f"[grind:{substrate}] COMPLETE  total_wall={elapsed:.1f}s  smoke={smoke}",
          flush=True)


# ─── Ensemble-stacked simulation helpers ──────────────────────────────────

def per_window_observables(
    d_unp: np.ndarray,     # (n_w, n_real, dim) or (n_w, n_real)
    d_per: np.ndarray,
    d_at_tw: np.ndarray,
    h_field: float,
    tau_windows: Sequence[float],
) -> list[dict]:
    """Compute C_d, C_d_diag, chi_d, d_norm, sigma_d, f per τ window from
    ensemble-stacked trail vectors. d_unp[k, r, ...] is window k, replica r.

    Returns one dict per window with both mean and SEM across replicas.
    """
    n_w = d_unp.shape[0]
    n_real = d_unp.shape[1]
    rows: list[dict] = []
    for k in range(n_w):
        u  = d_unp[k]
        p  = d_per[k]
        d0 = d_at_tw[k]
        # Per-replica scalars: reduce ALL non-replica axes (axis 0 is the
        # replica axis). Handles 1D (n_real,1), vector (n_real,2), and
        # field (n_real,L,L) substrate shapes uniformly.
        if u.ndim > 1:
            ax = tuple(range(1, u.ndim))
            ud0  = (u * d0).mean(axis=ax)             # (n_real,)
            uu   = (u * u).mean(axis=ax)
            umean = u.mean(axis=ax)
            pmean = p.mean(axis=ax)
        else:
            ud0 = u * d0; uu = u * u
            umean = u; pmean = p

        C_d_mean   = float(np.mean(ud0))
        C_d_sem    = float(np.std(ud0, ddof=0) / math.sqrt(n_real))
        Cdd_mean   = float(np.mean(uu))
        Cdd_sem    = float(np.std(uu, ddof=0) / math.sqrt(n_real))
        chi_per_r  = (pmean - umean) / h_field
        chi_d_mean = float(np.mean(chi_per_r))
        chi_d_sem  = float(np.std(chi_per_r, ddof=0) / math.sqrt(n_real))
        d_norm_per_r = np.sqrt(np.maximum(uu, 0.0))
        d_norm_mean  = float(np.mean(d_norm_per_r))
        d_norm_sem   = float(np.std(d_norm_per_r, ddof=0) / math.sqrt(n_real))
        sigma_d_per_r = np.sqrt(np.maximum(uu - umean * umean, 0.0))
        sigma_d_mean  = float(np.mean(sigma_d_per_r))
        sigma_d_sem   = float(np.std(sigma_d_per_r, ddof=0) / math.sqrt(n_real))
        if abs(Cdd_mean) > 1e-12:
            f_per_r = (uu - ud0) / np.maximum(uu, 1e-12)
            f_mean  = float(np.mean(f_per_r))
            f_sem   = float(np.std(f_per_r, ddof=0) / math.sqrt(n_real))
        else:
            f_mean = None; f_sem = None

        rows.append({
            "tau_window": float(tau_windows[k]),
            "C_d": C_d_mean, "C_d_sem": C_d_sem,
            "C_d_diag": Cdd_mean, "C_d_diag_sem": Cdd_sem,
            "chi_d": chi_d_mean, "chi_d_sem": chi_d_sem,
            "d_norm": d_norm_mean, "d_norm_sem": d_norm_sem,
            "sigma_d": sigma_d_mean, "sigma_d_sem": sigma_d_sem,
            "f": f_mean, "f_sem": f_sem,
            "n_realizations": n_real,
        })
    return rows


def _cell_worker(payload: dict) -> dict:
    """Top-level worker for ProcessPoolExecutor (Windows spawn requires
    pickle-safe top-level callables). Each worker runs ONE library cell
    end-to-end and writes its JSON file.

    Payload (all picklable):
      task_id           — for logging
      substrate         — directory name under primitives/
      primitive_module  — dotted import path (e.g. "voter.measurements")
      kwargs            — fully-built kwargs dict for multi_window_fdr_iter
      out_path          — string path where the cell JSON is written
      base_cell         — partially-filled cell template; the worker
                          fills in results.all_samples, init_event_*,
                          wall_seconds, completed_at.
      smoke             — bool; if True, skip the write
      primitives_dir    — string; prepended to sys.path so the substrate
                          module is importable in the worker process.
    """
    import importlib
    import time as _time
    import traceback as _tb

    pdir = payload["primitives_dir"]
    if pdir not in sys.path:
        sys.path.insert(0, pdir)
    # Reconfigure stdio for UTF-8 in the worker (Windows console gotcha).
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    # Pin each worker to a single BLAS/OpenMP thread. The pool already
    # parallelizes across cells; letting numpy spawn threads inside each
    # cell would oversubscribe a 32-thread CPU. Must happen BEFORE any
    # numpy import inside the worker process.
    for _k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
               "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ.setdefault(_k, "1")

    task_id = payload["task_id"]
    try:
        mod = importlib.import_module(payload["primitive_module"])
        fn = getattr(mod, "multi_window_fdr_iter")
        t0 = _time.time()
        init_ev = None
        all_samples: list[dict] = []
        for ev in fn(**payload["kwargs"]):
            et = ev.get("type")
            if et == "init":
                init_ev = ev
            elif et == "sample":
                all_samples.append(_sample_event_to_cell_row(ev))
        wall = _time.time() - t0
    except Exception as e:
        return {
            "status": "failed", "task_id": task_id,
            "error": str(e), "traceback": _tb.format_exc(),
            "wall": _time.time() - t0 if "t0" in dir() else 0.0,
        }

    cell = dict(payload["base_cell"])
    cell["wall_seconds"] = wall
    cell["completed_at"] = _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime())
    cell["results"] = dict(cell["results"])
    cell["results"]["init_event_t_kw"]    = (init_ev or {}).get("t_kw")
    cell["results"]["init_event_t_snap"]  = (init_ev or {}).get("t_snap")
    cell["results"]["init_event_h_field"] = (init_ev or {}).get("h_field")
    cell["results"]["all_samples"]        = all_samples

    if not payload.get("smoke"):
        write_json_atomic(Path(payload["out_path"]), cell)

    return {
        "status": "done", "task_id": task_id,
        "wall": wall, "n_samples": len(all_samples),
    }


def run_parallel(
    *,
    substrate: str,
    operating_points: list[dict],
    xdot_kinds: list[str],
    tau_env_for: Callable[[dict], dict],
    primitive_fn=None,   # not used in parallel; kept for API compat
    kwargs_for: Callable[[dict, str, dict, int], dict],
    primitive_module_name: str,
    n_realizations: int,
    fidelity: dict | None = None,
    smoke: bool = False,
    only_op_labels: list[str] | None = None,
    only_xdot: list[str] | None = None,
    max_workers: int | None = None,
):
    """Per-cell ProcessPoolExecutor grind. Default for full library runs.

    Builds (op × xdot_kind) tasks, dispatches each to a worker that runs
    the primitive once (ensemble-stacked, so all replicas live inside one
    worker) and writes the cell JSON. Workers are independent — one
    failure does not poison the rest.
    """
    import concurrent.futures
    import multiprocessing

    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    (DATA_ROOT / substrate).mkdir(parents=True, exist_ok=True)

    n_real = SMOKE_N_REAL if smoke else int(n_realizations)
    if max_workers is None:
        max_workers = max(1, multiprocessing.cpu_count() - 2)

    primitives_dir = str(Path(__file__).resolve().parents[1])

    payloads: list[dict] = []
    for op in operating_points:
        if only_op_labels and op["label"] not in only_op_labels:
            continue
        tau_env_block = tau_env_for(op)
        tau_env_value = tau_env_block.get("value")
        tau_windows, t_w, t_obs, n_sample_times = time_grids_for(
            tau_env_value, smoke=smoke,
        )
        schedule = {
            "t_w": int(t_w),
            "t_obs": int(t_obs),
            "tau_windows": list(tau_windows),
            "n_sample_times": int(n_sample_times),
        }
        for xdot_kind in xdot_kinds:
            if only_xdot and xdot_kind not in only_xdot:
                continue
            task_id = f"{substrate}__{op['label']}__{xdot_kind}"
            out_path = str(DATA_ROOT / substrate / f"{task_id}.json")
            base_cell = {
                "library_spec_version": LIBRARY_SPEC_VERSION,
                "substrate": substrate,
                "operating_point": op,
                "xdot_kind": xdot_kind,
                "fidelity": fidelity or {"L": None, "distance": None},
                "schedule": {**schedule, "n_realizations": n_real},
                "tau_env_analytic": tau_env_block,
                "tau_env_measured": None,
                "results": {
                    "init_event_t_kw": None,
                    "init_event_t_snap": None,
                    "init_event_h_field": None,
                    "all_samples": [],
                    "sem_available": True,
                    "sem_unavailable_reason": None,
                },
                "wall_seconds": None,
                "completed_at": None,
                "primitive_module": primitive_module_name,
            }
            kwargs = kwargs_for(op, xdot_kind, schedule, n_real)
            payloads.append({
                "task_id": task_id,
                "substrate": substrate,
                "primitive_module": primitive_module_name,
                "kwargs": kwargs,
                "out_path": out_path,
                "base_cell": base_cell,
                "smoke": bool(smoke),
                "primitives_dir": primitives_dir,
            })

    total = len(payloads)
    if total == 0:
        print(f"[grind:{substrate}] no tasks (filters left nothing).", flush=True)
        return

    print(f"[grind:{substrate}] parallel start  workers={max_workers}  "
          f"tasks={total}  n_real={n_real}  smoke={smoke}", flush=True)
    t_overall = time.time()

    done_count = 0
    failed_count = 0
    walls: list[float] = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(_cell_worker, p): p["task_id"] for p in payloads}
        for fut in concurrent.futures.as_completed(futures):
            tid = futures[fut]
            done_count += 1
            try:
                res = fut.result()
            except Exception as e:
                print(f"[grind:{substrate}] [{done_count:>3}/{total}] "
                      f"FUTURE-FAILED {tid}  err={e}", flush=True)
                failed_count += 1
                continue
            if res["status"] == "done":
                walls.append(res["wall"])
                print(f"[grind:{substrate}] [{done_count:>3}/{total}] DONE "
                      f"{tid}  wall={res['wall']:.1f}s  samples={res['n_samples']}",
                      flush=True)
            else:
                failed_count += 1
                print(f"[grind:{substrate}] [{done_count:>3}/{total}] FAIL "
                      f"{tid}  err={res.get('error')}", flush=True)
                tb = res.get("traceback")
                if tb:
                    print(tb, file=sys.stderr, flush=True)

    elapsed = time.time() - t_overall
    print(f"[grind:{substrate}] COMPLETE  wall={elapsed:.1f}s  "
          f"done={done_count - failed_count}/{total}  failed={failed_count}  "
          f"workers={max_workers}", flush=True)


def ensemble_C_chi(
    s_unp: np.ndarray,         # (n_real, ...) substrate state at t (per replica)
    s_snap: np.ndarray,        # (n_real, ...) substrate state at t_w
    s_per: np.ndarray,
    h_field: float,
) -> tuple[float, float, float, float]:
    """Compute raw-readout C and chi means+SEMs across the replica axis.
    Substrate-shape-agnostic: reduces all non-leading axes to a per-replica
    scalar, then averages across replicas.
    """
    # Per-replica reduction: mean over all non-replica axes
    if s_unp.ndim > 1:
        per_r_C = (s_unp * s_snap).mean(axis=tuple(range(1, s_unp.ndim)))
        m_unp   = s_unp.mean(axis=tuple(range(1, s_unp.ndim)))
        m_per   = s_per.mean(axis=tuple(range(1, s_per.ndim)))
    else:
        per_r_C = s_unp * s_snap
        m_unp = s_unp; m_per = s_per
    chi_r = (m_per - m_unp) / h_field
    n_real = per_r_C.shape[0]
    return (
        float(np.mean(per_r_C)),
        float(np.std(per_r_C, ddof=0) / math.sqrt(n_real)),
        float(np.mean(chi_r)),
        float(np.std(chi_r, ddof=0) / math.sqrt(n_real)),
    )
