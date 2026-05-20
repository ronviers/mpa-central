from __future__ import annotations
import argparse, math, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from _shared.runtime import run, run_parallel                    # noqa: E402
from east.measurements import multi_window_fdr_iter, XDOT_KINDS  # noqa: E402

OPERATING_POINTS = [
    {"label": "T0.40", "T": 0.4, "gt": "c"},
    {"label": "T0.70", "T": 0.7, "gt": "s"},
    {"label": "T1.00", "T": 1.0, "gt": "k"},
    {"label": "T1.50", "T": 1.5, "gt": "s"},
    {"label": "T2.00", "T": 2.0, "gt": "r"},
]
H_FIELD = 0.10
N_REAL = 1024


def tau_env_for(op):
    T = float(op["T"])
    val = min(5000.0, math.exp(1.0 / T) * 5.0)
    return {"value": val, "method": "kcm_arrhenius_5_exp",
            "note": "East KCM super-Arrhenius placeholder τ_env ≈ 5·exp(1/T)."}


def kwargs_for(op, xdot_kind, schedule, n_real):
    return dict(T=op["T"], t_w=schedule["t_w"], t_obs=schedule["t_obs"],
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
    kwargs = dict(substrate="east", operating_points=list(OPERATING_POINTS),
                  xdot_kinds=list(XDOT_KINDS), tau_env_for=tau_env_for,
                  primitive_fn=multi_window_fdr_iter, kwargs_for=kwargs_for,
                  primitive_module_name="east.measurements", n_realizations=N_REAL,
                  fidelity={"L": 200, "distance": None}, smoke=a.smoke,
                  only_op_labels=a.only_op, only_xdot=a.only_xdot)
    if not a.serial: kwargs["max_workers"] = a.workers
    runner(**kwargs)


if __name__ == "__main__":
    main()
