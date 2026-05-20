from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from _shared.runtime import run, run_parallel                   # noqa: E402
from sir.measurements import multi_window_fdr_iter, XDOT_KINDS  # noqa: E402

OPERATING_POINTS = [
    {"label": "R0_0.50", "R0": 0.5, "gt": "r"},
    {"label": "R0_0.90", "R0": 0.9, "gt": "s"},
    {"label": "R0_1.00", "R0": 1.0, "gt": "k"},
    {"label": "R0_1.50", "R0": 1.5, "gt": "s"},
    {"label": "R0_3.00", "R0": 3.0, "gt": "c"},
]
H_FIELD = 0.10
N_REAL = 1024


def tau_env_for(op):
    r0 = float(op["R0"])
    delta = abs(r0 - 1.0)
    if delta < 0.01:
        return {"value": None, "method": "critical_R0_1_unbounded",
                "note": "Critical R0=1: fallback grid."}
    val = 1.0 / delta * 10.0
    return {"value": val, "method": "critical_slowing_inverse_distance",
            "note": "τ_env ≈ (γ·|R0-1|)^{-1} in step units."}


def kwargs_for(op, xdot_kind, schedule, n_real):
    return dict(R0=op["R0"], t_w=schedule["t_w"], t_obs=schedule["t_obs"],
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
    kwargs = dict(substrate="sir", operating_points=list(OPERATING_POINTS),
                  xdot_kinds=list(XDOT_KINDS), tau_env_for=tau_env_for,
                  primitive_fn=multi_window_fdr_iter, kwargs_for=kwargs_for,
                  primitive_module_name="sir.measurements", n_realizations=N_REAL,
                  fidelity={"L": None, "distance": None, "N_pop": 10000},
                  smoke=a.smoke, only_op_labels=a.only_op, only_xdot=a.only_xdot)
    if not a.serial: kwargs["max_workers"] = a.workers
    runner(**kwargs)


if __name__ == "__main__":
    main()
