from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from _shared.runtime import run, run_parallel                          # noqa: E402
from mm1_queue.measurements import multi_window_fdr_iter, XDOT_KINDS    # noqa: E402

INVALIDATOR = {
    "prediction_under_test": "substrate-classes.json ck-glassy common-exponent: "
                             "FDR aging-diagonal slope α_s should equal the "
                             "heavy-traffic queueing exponent (1/2) as ρ→1.",
    "falsifier": "α_s measured on heavy-traffic cells (ρ=0.95,0.99,0.999) "
                 "differs from 1/2 while in sustained s-regime backlog. "
                 "This is the corpus's own stated falsification condition.",
    "expected_heavy_traffic_exponent": 0.5,
}
OPERATING_POINTS = [
    {"label": "rho0.5",   "rho": 0.5,   "gt": "r", "invalidator": INVALIDATOR},
    {"label": "rho0.8",   "rho": 0.8,   "gt": "r", "invalidator": INVALIDATOR},
    {"label": "rho0.95",  "rho": 0.95,  "gt": "s", "invalidator": INVALIDATOR},
    {"label": "rho0.99",  "rho": 0.99,  "gt": "s", "invalidator": INVALIDATOR},
    {"label": "rho0.999", "rho": 0.999, "gt": "s", "invalidator": INVALIDATOR},
]
H_FIELD = 0.05
N_REAL = 1024


def tau_env_for(op):
    rho = float(op["rho"])
    # M/M/1 relaxation time ~ 1/(1-sqrt(ρ))² in heavy traffic (step units, /DT).
    val = min(5000.0, 1.0 / max((1.0 - rho ** 0.5) ** 2, 1e-4) / 0.5)
    return {"value": val, "method": "mm1_relaxation_heavy_traffic",
            "note": "M/M/1 relaxation ~ 1/(1-√ρ)²; diverges as ρ→1 "
                    "(the heavy-traffic limit under test)."}


def kwargs_for(op, xdot_kind, schedule, n_real):
    return dict(rho=op["rho"], t_w=schedule["t_w"], t_obs=schedule["t_obs"],
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
    kwargs = dict(substrate="mm1_queue", operating_points=list(OPERATING_POINTS),
                  xdot_kinds=list(XDOT_KINDS), tau_env_for=tau_env_for,
                  primitive_fn=multi_window_fdr_iter, kwargs_for=kwargs_for,
                  primitive_module_name="mm1_queue.measurements", n_realizations=N_REAL,
                  fidelity={"L": None, "distance": None}, smoke=a.smoke,
                  only_op_labels=a.only_op, only_xdot=a.only_xdot)
    if not a.serial: kwargs["max_workers"] = a.workers
    runner(**kwargs)


if __name__ == "__main__":
    main()
