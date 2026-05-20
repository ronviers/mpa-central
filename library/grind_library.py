#!/usr/bin/env python
"""MPA library grinder.

Produces the characterized lightfield of the multi-window FDR observable
across (substrate, operating-point, ẋ-choice) triples per
H:/mpa-central/library/LIBRARY_SPEC.md (v1.0).

Resumable: a manifest at library/MANIFEST.json tracks task status; killing
and restarting the script picks up where it stopped. One JSON result file
per task lands in library/data/<substrate>/.

Designed for a graphics workstation that grinds for days unattended:
flushed printing, atomic writes, per-task isolation (one failure does
not abort the run), and ETA estimation from completed walls.

Usage:
  python grind_library.py                      # full library
  python grind_library.py --smoke              # tiny sanity-check, no writes
  python grind_library.py --dry-run            # print task list + ETA, do not run
  python grind_library.py --substrate brain    # one substrate only
  python grind_library.py --resume-only        # do not start new tasks; only retry
                                                #   tasks marked 'in_progress' or 'failed'
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Iterator
import concurrent.futures
import multiprocessing
import traceback

import numpy as np

# UTF-8 for Greek glyphs (CLAUDE.md Windows console gotcha)
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


# ─── Paths and library spec ───────────────────────────────────────────────

LIBRARY_SPEC_VERSION = "1.0"
H = Path("H:/")

# Substrates split into two homes by design:
#   - SUBSTRATE_PATHS_EXTERNAL: substrates with their own H:\ repo. They
#     have non-trivial dependencies (mpc-glass C++ Ising sim, mpc-quantum
#     Stim, mpa-brain ensemble averager), per-repo CLAUDE.md / FOOTING.md
#     discipline, and citable standalone git histories. Adding one
#     requires an explicit entry here.
#   - SUBSTRATE_PRIMITIVES_DIR: lightweight substrates that live in-
#     library, typically thin adapters that read a public dataset and
#     emit FDR observables. Each subdirectory IS an importable Python
#     package; auto-discovered. Adding one is "drop in a folder and run."
# See LIBRARY_SPEC.md §"Primitives" for the in-library pattern.
SUBSTRATE_PATHS_EXTERNAL = {
    "brain":   H / "mpa-brain",
    "glass":   H / "mpc-glass",
    "quantum": H / "mpc-quantum",
}

LIBRARY_ROOT = H / "mpa-central" / "library"
DATA_ROOT = LIBRARY_ROOT / "data"
MANIFEST_PATH = LIBRARY_ROOT / "MANIFEST.json"
LOG_PATH = LIBRARY_ROOT / "grind.log"
SUBSTRATE_PRIMITIVES_DIR = LIBRARY_ROOT / "primitives"


# Per-task τ_obs and t_obs grids are τ_env-anchored, not global. See
# time_grids_for() below. The fixed defaults here are fallback for
# operating points where τ_env is unbounded (e.g., glass below Tc).
LIB_FALLBACK_TAU_WINDOWS = tuple(
    round(x, 3) for x in np.geomspace(1.0, 1000.0, 31).tolist()
)
LIB_FALLBACK_T_W = 500
LIB_FALLBACK_T_OBS = 30000
LIB_N_SAMPLE_TIMES = 31

# τ_env-anchored sampling parameters
LIB_TAU_OBS_LO_FRAC = 0.05    # τ_obs grid lo bound = 0.05·τ_env
LIB_TAU_OBS_HI_FRAC = 2.0     # τ_obs grid hi bound = 2.0·τ_env
LIB_TAU_OBS_HI_CAP = 5000     # but never exceed this (compute-budget cap)
LIB_T_OBS_AGING_FACTOR = 30   # t_obs ≥ 30·τ_env to span the aging window
LIB_T_OBS_RULE8_FACTOR = 10   # rule 8: t_obs ≥ 10·τ_obs_max
LIB_T_OBS_CAP = 200_000       # global t_obs cap (don't burn compute on pure asymptote)
LIB_T_W_FACTOR = 5            # substrate equilibration: t_w ≥ 5·τ_env
LIB_T_W_FLOOR = 500
LIB_T_W_CAP = 5000


def time_grids_for(tau_env: float | None, smoke: bool = False):
    """Per-operating-point τ-grid scaling.

    Returns (tau_windows, t_w, t_obs, n_sample_times).

    The library's central design choice (per the user's "everything → r at
    infinity" insight): sample times concentrate where the substrate has
    *something happening* — the aging window around τ_env. Outside it,
    sampling just confirms the trivial asymptote.

    For τ_env=None (e.g., glass below Tc, unbounded aging on accessible
    timescales): fall back to the fixed default grid. The substrate is
    in its aging regime across the whole grid, so a fixed wide grid
    characterizes as much of that regime as fits in budget.

    For τ_env finite:
    - τ_obs grid: 31 log-spaced from 0.05·τ_env to min(2·τ_env, 5000).
      Spans 1.6 decades across τ_env, enough to walk the regime
      hierarchy v8 §5 predicts (narrow-τ → c-like through broad-τ → r-like
      or its rule-7-inverted reading per substrate).
    - t_obs: max(10·τ_obs_max [rule 8 kernel-warmup floor],
                  30·τ_env [aging-window coverage]),
              capped at 200000 (global compute-budget cap).
    - t_w: max(500, 5·τ_env), capped at 5000 (substrate equilibration).
    """
    if smoke:
        return (
            SMOKE_TAU_WINDOWS,
            SMOKE_T_W,
            SMOKE_T_OBS,
            SMOKE_N_SAMPLE_TIMES,
        )

    if tau_env is None or tau_env <= 0 or not math.isfinite(tau_env):
        return (
            LIB_FALLBACK_TAU_WINDOWS,
            LIB_FALLBACK_T_W,
            LIB_FALLBACK_T_OBS,
            LIB_N_SAMPLE_TIMES,
        )

    # τ_obs grid centered on τ_env
    tw_lo = max(1.0, LIB_TAU_OBS_LO_FRAC * tau_env)
    tw_hi = min(LIB_TAU_OBS_HI_CAP, LIB_TAU_OBS_HI_FRAC * tau_env)
    if tw_hi <= tw_lo:
        tw_hi = tw_lo * 10  # ensure non-degenerate range
    tau_windows = tuple(
        round(x, 3) for x in np.geomspace(tw_lo, tw_hi, 31).tolist()
    )

    # t_obs: rule-8 floor (10·τ_obs_max) + aging-window coverage (30·τ_env)
    rule8_floor = LIB_T_OBS_RULE8_FACTOR * max(tau_windows)
    aging_target = LIB_T_OBS_AGING_FACTOR * tau_env
    t_obs = int(min(LIB_T_OBS_CAP, max(rule8_floor, aging_target)))

    # t_w: substrate equilibration
    t_w = int(min(LIB_T_W_CAP, max(LIB_T_W_FLOOR, LIB_T_W_FACTOR * tau_env)))

    return (tau_windows, t_w, t_obs, LIB_N_SAMPLE_TIMES)

# Realization counts per substrate (target σ_f < 0.005)
BRAIN_N_REAL = 4096
GLASS_N_REAL = 1024            # external loop; per-realization wall is large
QUANTUM_N_SHOTS = 1024
QUANTUM_N_SEEDS = 16

# Substrate-fidelity choices (not library axes; cross-checked separately)
GLASS_L = 16
QUANTUM_DISTANCE = 3
QUANTUM_DELTA_P = 1e-3
GLASS_H_FIELD = 0.10

# Operating-point grids
BRAIN_SCENARIOS = [
    {"label": "committed", "scenario": "committed", "h_field": None, "gt": "c"},
    {"label": "suspended", "scenario": "suspended", "h_field": None, "gt": "s"},
    {"label": "conflict",  "scenario": "conflict",  "h_field": None, "gt": "k"},
    {"label": "reset",     "scenario": "reset",     "h_field": None, "gt": "r"},
]

GLASS_T_GRID = [0.20, 0.30, 0.50, 0.70, 0.85, 0.95, 1.00, 1.10, 1.30, 1.50, 1.80]

QUANTUM_P_GRID = [round(p, 6) for p in np.logspace(-4, -1.3, 11).tolist()]

# Smoke-mode budgets — enough to verify imports + primitive signatures, no more
SMOKE_TAU_WINDOWS = (3.0, 30.0, 300.0)
SMOKE_T_W = 50
SMOKE_T_OBS = 500
SMOKE_N_SAMPLE_TIMES = 6
SMOKE_BRAIN_N_REAL = 4
SMOKE_GLASS_N_REAL = 2
SMOKE_GLASS_L = 8
SMOKE_QUANTUM_N_SHOTS = 32
SMOKE_QUANTUM_N_SEEDS = 2


# ─── Substrate package imports (via sys.path injection) ───────────────────

# External-repo substrates: each repo dir goes on sys.path so its
# top-level package (e.g. mpa_brain_packs, mpc_glass_packs) is importable.
for p in SUBSTRATE_PATHS_EXTERNAL.values():
    sp = str(p)
    if p.is_dir() and sp not in sys.path:
        sys.path.insert(0, sp)

# In-library primitives: the primitives/ directory itself goes on
# sys.path so each subdirectory (e.g. primitives/polymer/) is
# importable as its name (`import polymer.measurements`). New
# substrates appear by creating a subdirectory; no edit here required.
if SUBSTRATE_PRIMITIVES_DIR.is_dir():
    sp = str(SUBSTRATE_PRIMITIVES_DIR)
    if sp not in sys.path:
        sys.path.insert(0, sp)


def discover_in_library_substrates() -> list[str]:
    """Return the names of substrates living under primitives/. Each
    subdirectory with an __init__.py is treated as a substrate package.
    Names must not collide with SUBSTRATE_PATHS_EXTERNAL keys."""
    if not SUBSTRATE_PRIMITIVES_DIR.is_dir():
        return []
    out: list[str] = []
    for entry in sorted(SUBSTRATE_PRIMITIVES_DIR.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        if not (entry / "__init__.py").is_file():
            continue
        if entry.name in SUBSTRATE_PATHS_EXTERNAL:
            print(f"[warn] in-library primitive {entry.name!r} collides with "
                  f"external repo SUBSTRATE_PATHS_EXTERNAL[{entry.name!r}]; "
                  f"external repo wins. Rename the in-library primitive.",
                  file=sys.stderr, flush=True)
            continue
        out.append(entry.name)
    return out


def all_substrate_names() -> list[str]:
    """Union of external + in-library substrate names. Stable order:
    external first (in their declared order), then in-library
    (alphabetical)."""
    return list(SUBSTRATE_PATHS_EXTERNAL.keys()) + discover_in_library_substrates()

# These imports are deferred to first use so import errors per substrate
# don't block the others.
def _import_brain():
    from mpa_brain_packs.measurements import multi_window_fdr_iter as fn
    from mpa_brain_packs.physics_primitives import XDOT_KINDS as kinds
    return fn, list(kinds)

def _import_glass():
    from mpc_glass_packs.measurements import multi_window_fdr_iter as fn, XDOT_KINDS as kinds
    return fn, list(kinds)

def _import_quantum():
    from mpc_quantum_packs.measurements import multi_window_fdr_iter as fn, XDOT_KINDS as kinds
    return fn, list(kinds)


# ─── Logging ──────────────────────────────────────────────────────────────

def log(msg: str, also_print: bool = True):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    if also_print:
        print(line, flush=True)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


# ─── Atomic JSON writer ───────────────────────────────────────────────────

def write_json_atomic(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, default=float)
    os.replace(tmp, path)


def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


# ─── Analytic τ_env placeholders (until substrate-side raw-autocorr lands) ─

def tau_env_brain(scenario: str) -> dict:
    table = {"committed": 1000.0, "suspended": 300.0, "conflict": 500.0, "reset": 50.0}
    return {
        "value": table.get(scenario),
        "method": "scenario_table",
        "note": "Hand-calibrated placeholder; raw-readout autocorrelation fit owed.",
    }


def tau_env_glass(T: float) -> dict:
    Tc, zν, eps = 1.1, 6.0, 0.05
    if T <= Tc:
        return {
            "value": None,
            "method": "below_Tc_aging_unbounded",
            "note": "Below Tc the substrate ages on the experiment timescale; "
                    "τ_env > t_obs by construction. Real measurement requires "
                    "the substrate to emit raw spin-overlap autocorrelation.",
        }
    return {
        "value": abs(T - Tc + eps) ** (-zν),
        "method": "critical_slowing_zν6",
        "note": "Standard 3D EA Ising slowing-down power-law placeholder; "
                "raw-readout fit owed.",
    }


def tau_env_quantum(p_base: float) -> dict:
    return {
        "value": 1.0 / p_base,
        "method": "inverse_p_base",
        "note": "Leading-order analytic estimate (1/p_base). "
                "Geometric / code-distance corrections deferred to "
                "raw-readout autocorr emission.",
    }


# ─── Task-list construction ───────────────────────────────────────────────

def build_tasks(substrates: list[str], smoke: bool) -> list[dict]:
    tasks = []
    if "brain" in substrates:
        try:
            _, brain_xdot = _import_brain()
        except ImportError as e:
            log(f"WARN: brain import failed: {e}; skipping brain")
            brain_xdot = []
        for op in BRAIN_SCENARIOS:
            for xk in brain_xdot:
                tasks.append({
                    "substrate": "brain",
                    "task_id": f"brain__{op['label']}__{xk}",
                    "operating_point": {
                        "label": op["label"],
                        "scenario": op["scenario"],
                        "h_field": op["h_field"],
                        "T": None, "p_base": None, "delta_p": None,
                        "gt": op["gt"],
                    },
                    "xdot_kind": xk,
                    "fidelity": {"L": None, "distance": None},
                    "tau_env_analytic": tau_env_brain(op["scenario"]),
                })
    if "glass" in substrates:
        try:
            _, glass_xdot = _import_glass()
        except ImportError as e:
            log(f"WARN: glass import failed: {e}; skipping glass")
            glass_xdot = []
        T_grid = [0.30, 1.50] if smoke else GLASS_T_GRID
        for T in T_grid:
            for xk in glass_xdot:
                tasks.append({
                    "substrate": "glass",
                    "task_id": f"glass__T{T:.3f}__{xk}",
                    "operating_point": {
                        "label": f"T={T:.3f}",
                        "scenario": None,
                        "h_field": GLASS_H_FIELD,
                        "T": T, "p_base": None, "delta_p": None,
                        "gt": _glass_gt(T),
                    },
                    "xdot_kind": xk,
                    "fidelity": {"L": SMOKE_GLASS_L if smoke else GLASS_L, "distance": None},
                    "tau_env_analytic": tau_env_glass(T),
                })
    if "quantum" in substrates:
        try:
            _, quantum_xdot = _import_quantum()
        except ImportError as e:
            log(f"WARN: quantum import failed: {e}; skipping quantum")
            quantum_xdot = []
        p_grid = [1e-4, 2e-2] if smoke else QUANTUM_P_GRID
        for p in p_grid:
            for xk in quantum_xdot:
                tasks.append({
                    "substrate": "quantum",
                    "task_id": f"quantum__p{p:.0e}__{xk}",
                    "operating_point": {
                        "label": f"p_base={p:.4g}",
                        "scenario": None,
                        "h_field": None,
                        "T": None, "p_base": p, "delta_p": QUANTUM_DELTA_P,
                        "gt": _quantum_gt(p),
                    },
                    "xdot_kind": xk,
                    "fidelity": {"L": None, "distance": QUANTUM_DISTANCE},
                    "tau_env_analytic": tau_env_quantum(p),
                })
    return tasks


def _glass_gt(T: float) -> str:
    if T < 0.5: return "c"
    if T < 0.95: return "s"
    if T < 1.1: return "k"
    return "r"


def _quantum_gt(p: float) -> str:
    if p < 5e-4: return "r"
    if p < 7e-3: return "s"
    if p < 1.5e-2: return "s"
    return "k"


# ─── External aggregator (glass and quantum) ──────────────────────────────

def _aggregator_init(template_event: dict) -> dict:
    """Initialize an aggregator from a sample event template."""
    return {
        "t": template_event["t"],
        "dt": template_event["dt"],
        "n": 0,
        "C_sum": 0.0, "C_sum2": 0.0,
        "chi_sum": 0.0, "chi_sum2": 0.0,
        "per_window": [
            {
                "tau_window": w["tau_window"],
                "C_d_sum": 0.0, "C_d_sum2": 0.0,
                "C_d_diag_sum": 0.0, "C_d_diag_sum2": 0.0,
                "chi_d_sum": 0.0, "chi_d_sum2": 0.0,
                "d_norm_sum": 0.0, "d_norm_sum2": 0.0,
                "sigma_d_sum": 0.0, "sigma_d_sum2": 0.0,
                "f_sum": 0.0, "f_sum2": 0.0, "f_n": 0,
            }
            for w in template_event["per_window"]
        ],
    }


def _aggregator_accumulate(agg: dict, ev: dict):
    agg["n"] += 1
    if ev.get("C") is not None:
        agg["C_sum"] += ev["C"]; agg["C_sum2"] += ev["C"] * ev["C"]
    if ev.get("chi") is not None:
        agg["chi_sum"] += ev["chi"]; agg["chi_sum2"] += ev["chi"] * ev["chi"]
    for k, w in enumerate(ev["per_window"]):
        a = agg["per_window"][k]
        for key in ("C_d", "C_d_diag", "chi_d", "d_norm", "sigma_d"):
            v = w.get(key)
            if v is None: continue
            a[f"{key}_sum"] += v
            a[f"{key}_sum2"] += v * v
        cd = w.get("C_d"); cdd = w.get("C_d_diag")
        if cd is not None and cdd is not None and abs(cdd) > 1e-12:
            f = (cdd - cd) / cdd
            a["f_sum"] += f
            a["f_sum2"] += f * f
            a["f_n"] += 1


def _aggregator_finalize(agg: dict) -> dict:
    n = max(agg["n"], 1)
    def mean_sem(s, s2, count):
        if count <= 0: return None, None
        m = s / count
        if count < 2: return m, None
        var = max(s2 / count - m * m, 0.0)
        sem = math.sqrt(var) / math.sqrt(count)
        return m, sem
    C_m, C_sem = mean_sem(agg["C_sum"], agg["C_sum2"], n)
    chi_m, chi_sem = mean_sem(agg["chi_sum"], agg["chi_sum2"], n)
    per_window = []
    for a in agg["per_window"]:
        cdm, cdsem = mean_sem(a["C_d_sum"], a["C_d_sum2"], n)
        cddm, cddsem = mean_sem(a["C_d_diag_sum"], a["C_d_diag_sum2"], n)
        chidm, chidsem = mean_sem(a["chi_d_sum"], a["chi_d_sum2"], n)
        dnm, dnsem = mean_sem(a["d_norm_sum"], a["d_norm_sum2"], n)
        sdm, sdsem = mean_sem(a["sigma_d_sum"], a["sigma_d_sum2"], n)
        fm, fsem = mean_sem(a["f_sum"], a["f_sum2"], a["f_n"])
        per_window.append({
            "tau_window": a["tau_window"],
            "C_d_mean": cdm, "C_d_sem": cdsem,
            "C_d_diag_mean": cddm, "C_d_diag_sem": cddsem,
            "chi_d_mean": chidm, "chi_d_sem": chidsem,
            "d_norm_mean": dnm, "d_norm_sem": dnsem,
            "sigma_d_mean": sdm, "sigma_d_sem": sdsem,
            "f_mean": fm, "f_sem": fsem,
            "n_realizations": a["f_n"],
        })
    return {
        "t": agg["t"], "dt": agg["dt"],
        "C_mean": C_m, "C_sem": C_sem,
        "chi_mean": chi_m, "chi_sem": chi_sem,
        "per_window": per_window,
        "n_realizations": n,
    }


# ─── Per-task runners ─────────────────────────────────────────────────────

def run_brain_task(task: dict, schedule: dict, n_real: int, smoke: bool) -> dict:
    """Brain primitive does internal aggregation; one call returns averaged events."""
    fn, _ = _import_brain()
    op = task["operating_point"]
    init_event = None
    sample_events = []
    for ev in fn(
        scenario=op["scenario"],
        t_w=schedule["t_w"], t_obs=schedule["t_obs"],
        tau_windows=schedule["tau_windows"],
        h_field=op["h_field"],
        seed=0,
        n_realizations=n_real,
        progress_every=0,
        n_sample_times=schedule["n_sample_times"],
        xdot_kind=task["xdot_kind"],
    ):
        et = ev["type"]
        if et == "init":
            init_event = ev
        elif et == "sample":
            sample_events.append(ev)
    # Brain emits already-averaged values; SEM not available without primitive update.
    all_samples = []
    for ev in sample_events:
        per_window = []
        for w in ev["per_window"]:
            cd = w.get("C_d"); cdd = w.get("C_d_diag")
            f = ((cdd - cd) / cdd) if (cd is not None and cdd is not None and abs(cdd) > 1e-12) else None
            per_window.append({
                "tau_window": w["tau_window"],
                "C_d_mean": cd, "C_d_sem": None,
                "C_d_diag_mean": cdd, "C_d_diag_sem": None,
                "chi_d_mean": w.get("chi_d"), "chi_d_sem": None,
                "d_norm_mean": w.get("d_norm"), "d_norm_sem": None,
                "sigma_d_mean": w.get("sigma_d"), "sigma_d_sem": None,
                "f_mean": f, "f_sem": None,
                "n_realizations": n_real,
            })
        all_samples.append({
            "t": ev["t"], "dt": ev["dt"],
            "C_mean": ev.get("C"), "C_sem": None,
            "chi_mean": ev.get("chi"), "chi_sem": None,
            "per_window": per_window,
            "n_realizations": n_real,
        })
    return {
        "init_event_t_kw": (init_event or {}).get("t_kw"),
        "init_event_t_snap": (init_event or {}).get("t_snap"),
        "init_event_h_field": (init_event or {}).get("h_field"),
        "all_samples": all_samples,
        "sem_available": False,
        "sem_unavailable_reason": "Brain primitive aggregates internally; per-realization values not exposed.",
    }


import concurrent.futures
import multiprocessing
import traceback

def _external_worker(payload: dict) -> dict:
    """
    Top-level worker function for Windows spawn pickling.
    Re-imports the primitive inside the process to bypass GIL.
    Captures its own exceptions to prevent task-wide failure.
    """
    sub = payload["substrate"]
    r = payload["r"]
    seed_step = payload["seed_step"]
    kwargs = payload["kwargs"]
    kwargs["seed"] = r * seed_step

    result = {"r": r, "events": [], "error": None}

    try:
        # Substrate dispatch consolidated here to avoid maintenance traps
        if sub == "glass":
            from mpc_glass_packs.measurements import multi_window_fdr_iter as fn
        elif sub == "quantum":
            from mpc_quantum_packs.measurements import multi_window_fdr_iter as fn
        else:
            raise ValueError(f"Unknown substrate for external loop: {sub}")

        for ev in fn(**kwargs):
            # FUTURE-PROOFING: Currently filters to 'init' and 'sample'. 
            # When Test 3 / D.2 lands with reverse_replay=True, extend this 
            # tuple to include 'reverse_sample'.
            if ev["type"] in ("init", "sample"):
                result["events"].append(ev)
                
    except Exception as e:
        result["error"] = f"Realization {r} failed: {str(e)}\n{traceback.format_exc()}"

    return result


def run_external_loop_task(
    task: dict,
    schedule: dict,
    n_real: int,
    primitive_kwargs_for_realization,
    seed_step: int = 1000,
) -> dict:
    """Glass and quantum: external loop over seeds, parallelized and fault-tolerant."""
    init_event = None
    sample_index: dict[int, int] = {}
    aggs: list[dict] = []
    
    payloads = [
        {
            "substrate": task["substrate"],
            "r": r,
            "seed_step": seed_step,
            "kwargs": primitive_kwargs_for_realization(r)
        }
        for r in range(n_real)
    ]

    # Leave 2 logical processors for the OS and main thread
    max_workers = max(1, multiprocessing.cpu_count() - 2)
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Using submit for robust, per-realization error tolerance
        futures = {executor.submit(_external_worker, p): p for p in payloads}
        
        for future in concurrent.futures.as_completed(futures):
            res = future.result() 
            
            if res["error"]:
                log(f"WARN: Worker failed on seed {res['r']} - {res['error']}", also_print=True)
                continue  # Skip this realization's contribution rather than killing the task
            
            for ev in res["events"]:
                et = ev["type"]
                if et == "init" and init_event is None:
                    init_event = ev
                elif et == "sample":
                    t_abs = ev["t"]
                    if t_abs not in sample_index:
                        sample_index[t_abs] = len(aggs)
                        aggs.append(_aggregator_init(ev))
                    _aggregator_accumulate(aggs[sample_index[t_abs]], ev)

    aggs.sort(key=lambda a: a["t"])
    all_samples = [_aggregator_finalize(a) for a in aggs]
    
    return {
        "init_event_t_kw": (init_event or {}).get("t_kw"),
        "init_event_t_snap": (init_event or {}).get("t_snap"),
        "init_event_h_field": (init_event or {}).get("h_field"),
        "all_samples": all_samples,
        "sem_available": True,
        "sem_unavailable_reason": None,
    }


def run_glass_task(task: dict, schedule: dict, n_real: int, smoke: bool) -> dict:
    op = task["operating_point"]
    fid = task["fidelity"]
    def kwargs_for(r):
        return dict(
            L=fid["L"], T=op["T"],
            t_w=schedule["t_w"], t_obs=schedule["t_obs"],
            tau_windows=schedule["tau_windows"],
            h_field=op["h_field"],
            progress_every=0,
            xdot_kind=task["xdot_kind"],
        )
    return run_external_loop_task(task, schedule, n_real, kwargs_for)


def run_quantum_task(task: dict, schedule: dict, n_real: int, n_shots: int, smoke: bool) -> dict:
    op = task["operating_point"]
    fid = task["fidelity"]
    def kwargs_for(r):
        return dict(
            distance=fid["distance"],
            p_base=op["p_base"], delta_p=op["delta_p"],
            n_shots=n_shots,
            t_w=schedule["t_w"], t_obs=schedule["t_obs"],
            tau_windows=schedule["tau_windows"],
            progress_every=0,
            xdot_kind=task["xdot_kind"],
        )
    return run_external_loop_task(task, schedule, n_real, kwargs_for)


# ─── Manifest management ──────────────────────────────────────────────────

def load_manifest() -> dict:
    m = read_json(MANIFEST_PATH)
    return m or {"library_spec_version": LIBRARY_SPEC_VERSION, "tasks": {}}


def save_manifest(manifest: dict):
    write_json_atomic(MANIFEST_PATH, manifest)


def output_path_for(task: dict) -> Path:
    return DATA_ROOT / task["substrate"] / f"{task['task_id']}.json"


# ─── Main grind loop ──────────────────────────────────────────────────────

def grind(args):
    smoke = args.smoke
    substrates = (
        [args.substrate] if args.substrate else
        ["brain", "glass", "quantum"]
    )

    log(f"Library grinder starting. smoke={smoke} substrates={substrates}")
    log(f"Library root: {LIBRARY_ROOT}")
    log(f"Spec version: {LIBRARY_SPEC_VERSION}")
    log("Time grids are τ_env-anchored per operating point "
        "(time_grids_for; see LIBRARY_SPEC.md).")

    tasks = build_tasks(substrates, smoke=smoke)
    log(f"Built {len(tasks)} tasks.")

    # Compute per-task schedule once and attach
    for t in tasks:
        tau_env = t["tau_env_analytic"]["value"]
        tw, twindow, t_obs, nst = time_grids_for(tau_env, smoke=smoke)
        t["schedule"] = {
            "t_w": twindow, "t_obs": t_obs,
            "tau_windows": list(tw),
            "n_sample_times": nst,
        }

    if args.dry_run:
        for i, t in enumerate(tasks):
            sch = t["schedule"]
            tw = sch["tau_windows"]
            log(f"  [{i+1:>3}/{len(tasks)}] {t['task_id']}  "
                f"(gt={t['operating_point']['gt']}, "
                f"τ_env_analytic={t['tau_env_analytic']['value']})  "
                f"τ∈[{tw[0]:.1f}, {tw[-1]:.1f}]  "
                f"t_w={sch['t_w']}  t_obs={sch['t_obs']}",
                also_print=True)
        log("Dry run complete; no tasks executed.")
        return

    manifest = load_manifest()
    manifest.setdefault("tasks", {})

    # Cull manifest entries no longer in the task list (if substrate filter changed)
    # but only on a non-resume run. Resume keeps everything.
    if not args.resume_only:
        active_ids = {t["task_id"] for t in tasks}
        for tid in list(manifest["tasks"].keys()):
            if tid not in active_ids:
                # Keep the entry; do not delete. Just ignore on this run.
                pass
    save_manifest(manifest)

    completed_walls = []
    skipped = 0
    failed = 0
    succeeded = 0

    for i, task in enumerate(tasks):
        tid = task["task_id"]
        entry = manifest["tasks"].get(tid, {})
        status = entry.get("status", "pending")

        if status == "done":
            skipped += 1
            log(f"[{i+1:>3}/{len(tasks)}] SKIP done: {tid}")
            continue
        if args.resume_only and status not in ("in_progress", "failed"):
            skipped += 1
            log(f"[{i+1:>3}/{len(tasks)}] SKIP (resume-only): {tid}")
            continue

        # Per-substrate runner + n_real selection (uses task-attached schedule)
        sub = task["substrate"]
        task_schedule = task["schedule"]
        if sub == "brain":
            n_real = SMOKE_BRAIN_N_REAL if smoke else BRAIN_N_REAL
            runner = lambda t=task, s=task_schedule, n=n_real: run_brain_task(t, s, n, smoke)
            run_meta = {"n_realizations": n_real}
        elif sub == "glass":
            n_real = SMOKE_GLASS_N_REAL if smoke else GLASS_N_REAL
            runner = lambda t=task, s=task_schedule, n=n_real: run_glass_task(t, s, n, smoke)
            run_meta = {"n_realizations": n_real}
        elif sub == "quantum":
            n_seeds = SMOKE_QUANTUM_N_SEEDS if smoke else QUANTUM_N_SEEDS
            n_shots = SMOKE_QUANTUM_N_SHOTS if smoke else QUANTUM_N_SHOTS
            runner = lambda t=task, s=task_schedule, ns=n_seeds, nsh=n_shots: run_quantum_task(t, s, ns, nsh, smoke)
            run_meta = {"n_seeds": n_seeds, "n_shots": n_shots,
                        "n_realizations": n_seeds * n_shots}
        else:
            log(f"[{i+1:>3}/{len(tasks)}] FAIL unknown substrate: {sub}")
            manifest["tasks"][tid] = {"status": "failed",
                                       "error": f"unknown substrate {sub}"}
            save_manifest(manifest)
            failed += 1
            continue

        # Mark in_progress and persist before starting
        manifest["tasks"][tid] = {
            "status": "in_progress",
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "task": {k: task[k] for k in ("substrate", "operating_point",
                                            "xdot_kind", "fidelity",
                                            "tau_env_analytic")},
            "run_meta": run_meta,
        }
        save_manifest(manifest)

        log(f"[{i+1:>3}/{len(tasks)}] RUN  {tid}  "
            f"(n_real={run_meta['n_realizations']})")

        t0 = time.time()
        try:
            result_data = runner()
            wall = time.time() - t0
            payload = {
                "library_spec_version": LIBRARY_SPEC_VERSION,
                "substrate": task["substrate"],
                "operating_point": task["operating_point"],
                "xdot_kind": task["xdot_kind"],
                "fidelity": task["fidelity"],
                "schedule": {**task_schedule, **run_meta, "tau_windows": list(task_schedule["tau_windows"])},
                "tau_env_analytic": task["tau_env_analytic"],
                "tau_env_measured": None,
                "results": result_data,
                "wall_seconds": wall,
                "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "primitive_module": {
                    "brain": "mpa_brain_packs.measurements",
                    "glass": "mpc_glass_packs.measurements",
                    "quantum": "mpc_quantum_packs.measurements",
                }[task["substrate"]],
            }
            out_path = output_path_for(task)
            if not smoke:
                write_json_atomic(out_path, payload)
            manifest["tasks"][tid] = {
                "status": "done",
                "started_at": manifest["tasks"][tid].get("started_at"),
                "completed_at": payload["completed_at"],
                "wall_seconds": wall,
                "task": manifest["tasks"][tid]["task"],
                "run_meta": run_meta,
                "output": str(out_path) if not smoke else None,
            }
            save_manifest(manifest)
            completed_walls.append(wall)
            succeeded += 1
            mean_wall = sum(completed_walls) / len(completed_walls)
            remaining = sum(1 for t in tasks
                            if manifest["tasks"].get(t["task_id"], {}).get("status") != "done"
                            and t["task_id"] != tid)
            eta_s = mean_wall * remaining
            log(f"[{i+1:>3}/{len(tasks)}] DONE {tid}  "
                f"wall={wall:.1f}s  (mean={mean_wall:.1f}s  "
                f"remaining={remaining}  ETA={eta_s/3600:.1f}h)")
        except KeyboardInterrupt:
            log(f"[{i+1:>3}/{len(tasks)}] INTERRUPTED {tid}")
            manifest["tasks"][tid] = {
                **manifest["tasks"][tid],
                "status": "interrupted",
            }
            save_manifest(manifest)
            log("Manifest saved; exiting.")
            return
        except Exception as e:
            wall = time.time() - t0
            tb = traceback.format_exc()
            log(f"[{i+1:>3}/{len(tasks)}] FAIL {tid}  wall={wall:.1f}s  err={e}")
            log(tb, also_print=False)
            manifest["tasks"][tid] = {
                **manifest["tasks"][tid],
                "status": "failed",
                "wall_seconds": wall,
                "error": str(e),
                "traceback": tb,
            }
            save_manifest(manifest)
            failed += 1

    log(f"GRIND COMPLETE.  succeeded={succeeded}  failed={failed}  skipped={skipped}")
    if completed_walls:
        log(f"  total wall on succeeded: {sum(completed_walls)/3600:.2f}h")
        log(f"  mean wall per task: {sum(completed_walls)/len(completed_walls):.1f}s")


# ─── CLI ──────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="MPA library grinder")
    ap.add_argument("--smoke", action="store_true",
                    help="Tiny config to verify primitives import + run; no writes.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print task list and exit; no execution.")
    ap.add_argument("--substrate", choices=["brain", "glass", "quantum"],
                    help="Run one substrate only.")
    ap.add_argument("--resume-only", action="store_true",
                    help="Only retry in_progress / failed tasks; do not start new ones.")
    args = ap.parse_args()

    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    grind(args)


if __name__ == "__main__":
    main()
