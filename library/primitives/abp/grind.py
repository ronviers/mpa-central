from __future__ import annotations
import argparse, math, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from _shared.runtime import run, run_parallel                    # noqa: E402
from abp.measurements import multi_window_fdr_iter, XDOT_KINDS   # noqa: E402

OPERATING_POINTS = [
    {"label": "Pe0",   "Pe": 0.0,   "gt": "r"},
    {"label": "Pe1",   "Pe": 1.0,   "gt": "r"},
    {"label": "Pe10",  "Pe": 10.0,  "gt": "s"},
    {"label": "Pe50",  "Pe": 50.0,  "gt": "s"},
    {"label": "Pe200", "Pe": 200.0, "gt": "c"},
]
H_FIELD = 0.10
N_REAL = 1024


def tau_env_for(op):
    pe = float(op["Pe"])
    base = 20.0
    if pe <= 1:
        return {"value": base, "method": "rotational_persistence",
                "note": "τ_r/DT = 20 steps (Pe<=1)."}
    return {"value": base * (1.0 + math.sqrt(pe)),
            "method": "rotational_persistence_motility_boosted",
            "note": "τ_env = (τ_r/DT)·(1 + sqrt(Pe))."}


def kwargs_for(op, xdot_kind, schedule, n_real):
    return dict(Pe=op["Pe"], t_w=schedule["t_w"], t_obs=schedule["t_obs"],
                tau_windows=schedule["tau_windows"], h_field=H_FIELD,
                n_realizations=n_real, seed=0,
                n_sample_times=schedule["n_sample_times"], xdot_kind=xdot_kind)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--serial", action="store_true")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--only-op", action="append")
    ap.add_argument("--only-xdot", action="append")
    a = ap.parse_args()
    runner = run if a.serial else run_parallel
    kwargs = dict(substrate="abp", operating_points=list(OPERATING_POINTS),
                  xdot_kinds=list(XDOT_KINDS), tau_env_for=tau_env_for,
                  primitive_fn=multi_window_fdr_iter, kwargs_for=kwargs_for,
                  primitive_module_name="abp.measurements",
                  n_realizations=N_REAL,
                  fidelity={"L": None, "distance": None, "N_particles": 1},
                  smoke=a.smoke, only_op_labels=a.only_op, only_xdot=a.only_xdot)
    if not a.serial: kwargs["max_workers"] = a.workers
    runner(**kwargs)


if __name__ == "__main__":
    main()
