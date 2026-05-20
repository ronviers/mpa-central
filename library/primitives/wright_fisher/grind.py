from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from _shared.runtime import run, run_parallel                              # noqa: E402
from wright_fisher.measurements import multi_window_fdr_iter, XDOT_KINDS   # noqa: E402

OPERATING_POINTS = [
    {"label": "s-0.050", "s": -0.05, "gt": "r"},
    {"label": "s-0.010", "s": -0.01, "gt": "s"},
    {"label": "s+0.000", "s":  0.00, "gt": "k"},
    {"label": "s+0.010", "s":  0.01, "gt": "s"},
    {"label": "s+0.050", "s":  0.05, "gt": "c"},
]
H_FIELD = 0.005
N_REAL = 1024


def tau_env_for(op):
    s = abs(float(op["s"]))
    if s < 1e-4:
        return {"value": 1000.0, "method": "neutral_drift_N",
                "note": "Neutral Wright-Fisher: τ_drift ≈ N generations."}
    val = min(1000.0, 1.0 / (1000.0 * s * s) + 50.0)
    return {"value": val, "method": "selection_fixation_time",
            "note": "Wright-Fisher with selection: τ ≈ 1/(N·s²), capped at N."}


def kwargs_for(op, xdot_kind, schedule, n_real):
    return dict(s=op["s"], t_w=schedule["t_w"], t_obs=schedule["t_obs"],
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
    kwargs = dict(substrate="wright_fisher", operating_points=list(OPERATING_POINTS),
                  xdot_kinds=list(XDOT_KINDS), tau_env_for=tau_env_for,
                  primitive_fn=multi_window_fdr_iter, kwargs_for=kwargs_for,
                  primitive_module_name="wright_fisher.measurements",
                  n_realizations=N_REAL,
                  fidelity={"L": None, "distance": None, "N_pop": 1000},
                  smoke=a.smoke, only_op_labels=a.only_op, only_xdot=a.only_xdot)
    if not a.serial: kwargs["max_workers"] = a.workers
    runner(**kwargs)


if __name__ == "__main__":
    main()
