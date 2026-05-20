from __future__ import annotations
import argparse, math, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from _shared.runtime import run, run_parallel                              # noqa: E402
from lotka_volterra.measurements import multi_window_fdr_iter, XDOT_KINDS  # noqa: E402

OPERATING_POINTS = [
    {"label": "a0.50", "alpha": 0.5, "beta": 1.0, "gamma": 1.0, "delta": 1.0, "gt": "r"},
    {"label": "a0.80", "alpha": 0.8, "beta": 1.0, "gamma": 1.0, "delta": 1.0, "gt": "s"},
    {"label": "a1.00", "alpha": 1.0, "beta": 1.0, "gamma": 1.0, "delta": 1.0, "gt": "k"},
    {"label": "a1.20", "alpha": 1.2, "beta": 1.0, "gamma": 1.0, "delta": 1.0, "gt": "s"},
    {"label": "a1.60", "alpha": 1.6, "beta": 1.0, "gamma": 1.0, "delta": 1.0, "gt": "c"},
]
H_FIELD = 0.05
N_REAL = 1024


def tau_env_for(op):
    alpha, gamma = float(op["alpha"]), float(op["gamma"])
    period = 2 * math.pi / math.sqrt(max(alpha * gamma, 1e-9))
    val = min(5000.0, period / 0.01)
    return {"value": val, "method": "linearised_cycle_period",
            "note": "τ_env ≈ 2π/√(αγ) in step units, capped 5000."}


def kwargs_for(op, xdot_kind, schedule, n_real):
    return dict(alpha=op["alpha"], beta=op["beta"], gamma=op["gamma"], delta=op["delta"],
                t_w=schedule["t_w"], t_obs=schedule["t_obs"],
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
    kwargs = dict(substrate="lotka_volterra", operating_points=list(OPERATING_POINTS),
                  xdot_kinds=list(XDOT_KINDS), tau_env_for=tau_env_for,
                  primitive_fn=multi_window_fdr_iter, kwargs_for=kwargs_for,
                  primitive_module_name="lotka_volterra.measurements", n_realizations=N_REAL,
                  fidelity={"L": None, "distance": None, "X0": 100, "Y0": 50},
                  smoke=a.smoke, only_op_labels=a.only_op, only_xdot=a.only_xdot)
    if not a.serial: kwargs["max_workers"] = a.workers
    runner(**kwargs)


if __name__ == "__main__":
    main()
