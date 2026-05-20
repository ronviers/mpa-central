from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from _shared.runtime import run, run_parallel                   # noqa: E402
from fbm.measurements import multi_window_fdr_iter, XDOT_KINDS  # noqa: E402

OPERATING_POINTS = [
    {"label": "H0.20", "H": 0.20, "gt": "r"},
    {"label": "H0.35", "H": 0.35, "gt": "r"},
    {"label": "H0.50", "H": 0.50, "gt": "k"},
    {"label": "H0.65", "H": 0.65, "gt": "s"},
    {"label": "H0.85", "H": 0.85, "gt": "c"},
]
H_FIELD = 0.10
N_REAL = 1024


def tau_env_for(op):
    return {"value": 100.0, "method": "scale_free_fixed_reference",
            "note": "fBM is scale-free; τ_env_analytic is a fixed reference (100 steps)."}


def kwargs_for(op, xdot_kind, schedule, n_real):
    return dict(H=op["H"], t_w=schedule["t_w"], t_obs=schedule["t_obs"],
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
    kwargs = dict(substrate="fbm", operating_points=list(OPERATING_POINTS),
                  xdot_kinds=list(XDOT_KINDS), tau_env_for=tau_env_for,
                  primitive_fn=multi_window_fdr_iter, kwargs_for=kwargs_for,
                  primitive_module_name="fbm.measurements", n_realizations=N_REAL,
                  fidelity={"L": None, "distance": None}, smoke=a.smoke,
                  only_op_labels=a.only_op, only_xdot=a.only_xdot)
    if not a.serial: kwargs["max_workers"] = a.workers
    runner(**kwargs)


if __name__ == "__main__":
    main()
