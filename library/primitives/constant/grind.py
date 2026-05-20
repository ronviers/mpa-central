from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from _shared.runtime import run, run_parallel                          # noqa: E402
from constant.measurements import multi_window_fdr_iter, XDOT_KINDS    # noqa: E402

CONTROL = {
    "role": "degenerate_input",
    "claim": "x(t)=c constant. C(τ)=c² (flat), χ(τ)=0, ẋ=0.",
    "purpose": "Rung 0 — the floor below the floor. The test is what the "
               "INVERSION does with a frozen out-of-domain input: NaN, "
               "crash, or a confident hallucinated regime. A domain-policing "
               "pipeline refuses it.",
}
OPERATING_POINTS = [
    {"label": "c1.0", "c": 1.0, "gt": "out_of_domain",
     "control": {**CONTROL, "expected": "refusal / out-of-domain flag"}},
    {"label": "c0.0", "c": 0.0, "gt": "out_of_domain",
     "control": {**CONTROL, "expected": "refusal / out-of-domain flag"}},
]
H_FIELD = 0.05
N_REAL = 256


def tau_env_for(op):
    # No relaxation time exists for a constant; None → fallback time grid.
    return {"value": None, "method": "none_constant_has_no_relaxation",
            "note": "A constant has no τ_env; uses the fallback grid."}


def kwargs_for(op, xdot_kind, schedule, n_real):
    return dict(c=op["c"], t_w=schedule["t_w"], t_obs=schedule["t_obs"],
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
    kwargs = dict(substrate="constant", operating_points=list(OPERATING_POINTS),
                  xdot_kinds=list(XDOT_KINDS), tau_env_for=tau_env_for,
                  primitive_fn=multi_window_fdr_iter, kwargs_for=kwargs_for,
                  primitive_module_name="constant.measurements", n_realizations=N_REAL,
                  fidelity={"L": None, "distance": None}, smoke=a.smoke,
                  only_op_labels=a.only_op, only_xdot=a.only_xdot)
    if not a.serial: kwargs["max_workers"] = a.workers
    runner(**kwargs)


if __name__ == "__main__":
    main()
