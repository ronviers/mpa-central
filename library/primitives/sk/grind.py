from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from _shared.runtime import run, run_parallel                  # noqa: E402
from sk.measurements import multi_window_fdr_iter, XDOT_KINDS  # noqa: E402

OPERATING_POINTS = [
    {"label": "T0.400", "T": 0.4, "gt": "c"},
    {"label": "T0.700", "T": 0.7, "gt": "s"},
    {"label": "T1.000", "T": 1.0, "gt": "k"},
    {"label": "T1.300", "T": 1.3, "gt": "r"},
    {"label": "T1.600", "T": 1.6, "gt": "r"},
]
H_FIELD = 0.10
H_AMP = 0.0
N_REAL = 1024
TC = 1.0
ZNU = 4.0


def tau_env_for(op):
    T = float(op["T"])
    if T <= TC:
        return {"value": None, "method": "below_Tc_aging_unbounded",
                "note": "Mean-field SK below Tc: aging on experiment timescale."}
    return {"value": (abs(T - TC) + 0.05) ** (-ZNU),
            "method": "critical_slowing_zν4_meanfield",
            "note": "Mean-field SK slowing-down placeholder."}


def kwargs_for(op, xdot_kind, schedule, n_real):
    return dict(T=op["T"], h_amp=H_AMP, t_w=schedule["t_w"], t_obs=schedule["t_obs"],
                tau_windows=schedule["tau_windows"], h_field=H_FIELD,
                n_realizations=n_real, seed=0, n_sample_times=schedule["n_sample_times"],
                xdot_kind=xdot_kind)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--serial", action="store_true")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--only-op", action="append")
    ap.add_argument("--only-xdot", action="append")
    a = ap.parse_args()
    runner = run if a.serial else run_parallel
    kwargs = dict(substrate="sk", operating_points=list(OPERATING_POINTS),
                  xdot_kinds=list(XDOT_KINDS),
                  tau_env_for=tau_env_for, primitive_fn=multi_window_fdr_iter,
                  kwargs_for=kwargs_for, primitive_module_name="sk.measurements",
                  n_realizations=N_REAL, fidelity={"L": None, "distance": None, "N": 100},
                  smoke=a.smoke, only_op_labels=a.only_op, only_xdot=a.only_xdot)
    if not a.serial: kwargs["max_workers"] = a.workers
    runner(**kwargs)


if __name__ == "__main__":
    main()
