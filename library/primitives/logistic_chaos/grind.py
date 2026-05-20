from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from _shared.runtime import run, run_parallel                              # noqa: E402
from logistic_chaos.measurements import multi_window_fdr_iter, XDOT_KINDS  # noqa: E402

INVALIDATOR = {
    "prediction_under_test": "Deterministic chaos: no thermal bath; parameter "
                             "perturbation diverges at the Lyapunov rate, χ does "
                             "not relax. MPA's stochastic-FDR premise is violated.",
    "falsifier": "MPA returns a confident, finite, FDT-respecting regime "
                 "(c/s/k/r with sensible X) instead of flagging out-of-domain "
                 "or showing a manifestly broken FDT signature.",
}
OPERATING_POINTS = [
    {"label": "r3.6", "r": 3.6, "gt": "k", "invalidator": INVALIDATOR},
    {"label": "r3.7", "r": 3.7, "gt": "k", "invalidator": INVALIDATOR},
    {"label": "r3.8", "r": 3.8, "gt": "k", "invalidator": INVALIDATOR},
    {"label": "r3.9", "r": 3.9, "gt": "k", "invalidator": INVALIDATOR},
    {"label": "r4.0", "r": 4.0, "gt": "k", "invalidator": INVALIDATOR},
]
H_FIELD = 1e-4   # tiny: Lyapunov divergence amplifies it
N_REAL = 1024


def tau_env_for(op):
    # No relaxation timescale (deterministic chaos). Use a small fixed
    # reference so the grid is well-formed; the point is the apparatus
    # should NOT find a clean τ_env here.
    return {"value": 10.0, "method": "no_relaxation_fixed_reference",
            "note": "Deterministic chaos has no thermal relaxation time; "
                    "fixed reference only so the time grid is well-formed."}


def kwargs_for(op, xdot_kind, schedule, n_real):
    return dict(r=op["r"], t_w=schedule["t_w"], t_obs=schedule["t_obs"],
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
    kwargs = dict(substrate="logistic_chaos", operating_points=list(OPERATING_POINTS),
                  xdot_kinds=list(XDOT_KINDS), tau_env_for=tau_env_for,
                  primitive_fn=multi_window_fdr_iter, kwargs_for=kwargs_for,
                  primitive_module_name="logistic_chaos.measurements", n_realizations=N_REAL,
                  fidelity={"L": None, "distance": None}, smoke=a.smoke,
                  only_op_labels=a.only_op, only_xdot=a.only_xdot)
    if not a.serial: kwargs["max_workers"] = a.workers
    runner(**kwargs)


if __name__ == "__main__":
    main()
