from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from _shared.runtime import run, run_parallel                           # noqa: E402
from white_noise.measurements import multi_window_fdr_iter, XDOT_KINDS   # noqa: E402

CONTROL = {
    "role": "dissipative_floor",
    "claim": "Memoryless stochastic: C(t,t_w)=0 for t>t_w. Trivial-r character.",
    "purpose": "Pipeline must read no-structure and must NOT turn amplitude (σ) "
               "into a regime walk.",
    "analytic_C": "0 for all lags > 0",
}
OPERATING_POINTS = [
    {"label": "sigma0.5", "sigma": 0.5, "gt": "r", "control": CONTROL},
    {"label": "sigma1",   "sigma": 1.0, "gt": "r", "control": CONTROL},
    {"label": "sigma2",   "sigma": 2.0, "gt": "r", "control": CONTROL},
    {"label": "sigma5",   "sigma": 5.0, "gt": "r", "control": CONTROL},
    {"label": "sigma10",  "sigma": 10.0, "gt": "r", "control": CONTROL},
]
H_FIELD = 0.10
N_REAL = 1024


def tau_env_for(op):
    return {"value": 5.0, "method": "memoryless_fixed_reference",
            "note": "White noise has no relaxation time; fixed reference so the "
                    "grid is compact. C should be ~0 already at the first lag."}


def kwargs_for(op, xdot_kind, schedule, n_real):
    return dict(sigma=op["sigma"], t_w=schedule["t_w"], t_obs=schedule["t_obs"],
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
    kwargs = dict(substrate="white_noise", operating_points=list(OPERATING_POINTS),
                  xdot_kinds=list(XDOT_KINDS), tau_env_for=tau_env_for,
                  primitive_fn=multi_window_fdr_iter, kwargs_for=kwargs_for,
                  primitive_module_name="white_noise.measurements", n_realizations=N_REAL,
                  fidelity={"L": None, "distance": None}, smoke=a.smoke,
                  only_op_labels=a.only_op, only_xdot=a.only_xdot)
    if not a.serial: kwargs["max_workers"] = a.workers
    runner(**kwargs)


if __name__ == "__main__":
    main()
