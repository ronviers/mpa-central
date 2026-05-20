from __future__ import annotations
import argparse, math, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from _shared.runtime import run, run_parallel                             # noqa: E402
from driven_ring.measurements import multi_window_fdr_iter, XDOT_KINDS    # noqa: E402

INVALIDATOR = {
    "prediction_under_test": "Running NESS (F>A) sustains a current forever; "
                             "tests the 'everything → r at infinity' axiom.",
    "falsifier": "MPA forces an r-classification on the running NESS, or its "
                 "regime vocabulary cannot represent a sustained non-decaying "
                 "current. Locked cells (F<A) are the relaxing control.",
}
A = 1.0
OPERATING_POINTS = [
    {"label": "F0.5", "F": 0.5, "gt": "r", "regime": "locked",  "invalidator": INVALIDATOR},
    {"label": "F0.9", "F": 0.9, "gt": "r", "regime": "locked",  "invalidator": INVALIDATOR},
    {"label": "F1.0", "F": 1.0, "gt": "k", "regime": "critical", "invalidator": INVALIDATOR},
    {"label": "F1.5", "F": 1.5, "gt": "s", "regime": "running", "invalidator": INVALIDATOR},
    {"label": "F3.0", "F": 3.0, "gt": "s", "regime": "running", "invalidator": INVALIDATOR},
]
H_FIELD = 0.05
N_REAL = 1024
DT = 0.01


def tau_env_for(op):
    F = float(op["F"])
    if F > A:
        # Running: period of one revolution ~ 2π/<θ̇>, <θ̇>≈sqrt(F²-A²).
        period = 2 * math.pi / math.sqrt(max(F * F - A * A, 1e-6))
        val = min(5000.0, period / DT)
        return {"value": val, "method": "running_period",
                "note": "Running NESS: τ_env ≈ revolution period in step units."}
    # Locked: relaxation in a well, ~ 1/curvature; placeholder.
    val = min(5000.0, 50.0 / max(A - F, 1e-3))
    return {"value": val, "method": "locked_well_relaxation",
            "note": "Locked: well-relaxation placeholder."}


def kwargs_for(op, xdot_kind, schedule, n_real):
    return dict(F=op["F"], t_w=schedule["t_w"], t_obs=schedule["t_obs"],
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
    kwargs = dict(substrate="driven_ring", operating_points=list(OPERATING_POINTS),
                  xdot_kinds=list(XDOT_KINDS), tau_env_for=tau_env_for,
                  primitive_fn=multi_window_fdr_iter, kwargs_for=kwargs_for,
                  primitive_module_name="driven_ring.measurements", n_realizations=N_REAL,
                  fidelity={"L": None, "distance": None}, smoke=a.smoke,
                  only_op_labels=a.only_op, only_xdot=a.only_xdot)
    if not a.serial: kwargs["max_workers"] = a.workers
    runner(**kwargs)


if __name__ == "__main__":
    main()
