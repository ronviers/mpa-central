from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from _shared.runtime import run, run_parallel                            # noqa: E402
from ou_equilibrium.measurements import multi_window_fdr_iter, XDOT_KINDS  # noqa: E402

INVALIDATOR = {
    "prediction_under_test": "Equilibrium OU: FDT holds, X=1 everywhere, "
                             "C(t)=exp(-(t-t_w)/tau) analytic.",
    "falsifier": "Any cell shows |X-1| > 3*SEM in steady state, or a c/s/k "
                 "regime classification. Equilibrium has no aging.",
    "expected_X": 1.0,
}
OPERATING_POINTS = [
    {"label": "tau1",   "tau": 1.0,   "gt": "r", "invalidator": INVALIDATOR},
    {"label": "tau5",   "tau": 5.0,   "gt": "r", "invalidator": INVALIDATOR},
    {"label": "tau20",  "tau": 20.0,  "gt": "r", "invalidator": INVALIDATOR},
    {"label": "tau50",  "tau": 50.0,  "gt": "r", "invalidator": INVALIDATOR},
    {"label": "tau100", "tau": 100.0, "gt": "r", "invalidator": INVALIDATOR},
]
H_FIELD = 0.05
N_REAL = 1024


def tau_env_for(op):
    return {"value": float(op["tau"]), "method": "exact_ou_relaxation_time",
            "note": "EXACT (not placeholder): OU relaxation time τ in step units."}


def kwargs_for(op, xdot_kind, schedule, n_real):
    return dict(tau=op["tau"], t_w=schedule["t_w"], t_obs=schedule["t_obs"],
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
    kwargs = dict(substrate="ou_equilibrium", operating_points=list(OPERATING_POINTS),
                  xdot_kinds=list(XDOT_KINDS), tau_env_for=tau_env_for,
                  primitive_fn=multi_window_fdr_iter, kwargs_for=kwargs_for,
                  primitive_module_name="ou_equilibrium.measurements", n_realizations=N_REAL,
                  fidelity={"L": None, "distance": None}, smoke=a.smoke,
                  only_op_labels=a.only_op, only_xdot=a.only_xdot)
    if not a.serial: kwargs["max_workers"] = a.workers
    runner(**kwargs)


if __name__ == "__main__":
    main()
