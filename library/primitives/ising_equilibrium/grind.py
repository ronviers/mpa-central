from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from _shared.runtime import run, run_parallel                                 # noqa: E402
from ising_equilibrium.measurements import multi_window_fdr_iter, XDOT_KINDS  # noqa: E402

INVALIDATOR = {
    "prediction_under_test": "Equilibrium 2D Ising: FDT holds, X=1 at every T "
                             "including Tc. Critical slowing ≠ aging.",
    "falsifier": "Persistent X<1 in the equilibrated system (esp. near Tc) "
                 "would mean MPA mistakes critical slowing-down for aging.",
    "expected_X": 1.0,
}
TC = 2.269
OPERATING_POINTS = [
    {"label": "T1.500", "T": 1.5,   "gt": "r", "invalidator": INVALIDATOR},
    {"label": "T2.000", "T": 2.0,   "gt": "r", "invalidator": INVALIDATOR},
    {"label": "T2.269", "T": 2.269, "gt": "r", "invalidator": INVALIDATOR},
    {"label": "T2.600", "T": 2.6,   "gt": "r", "invalidator": INVALIDATOR},
    {"label": "T3.500", "T": 3.5,   "gt": "r", "invalidator": INVALIDATOR},
]
H_FIELD = 0.05
N_REAL = 1024


def tau_env_for(op):
    T = float(op["T"])
    # Equilibrium correlation time: critical slowing near Tc (z≈2.17 for
    # 2D Ising Glauber). Placeholder power-law, capped.
    eps = abs(T - TC) + 0.05
    val = min(2000.0, 5.0 * eps ** (-2.17))
    return {"value": val, "method": "critical_slowing_z2.17_equilibrium",
            "note": "Equilibrium correlation time placeholder; the point is "
                    "X=1 should hold regardless of how long τ_env gets."}


def kwargs_for(op, xdot_kind, schedule, n_real):
    return dict(T=op["T"], t_w=schedule["t_w"], t_obs=schedule["t_obs"],
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
    kwargs = dict(substrate="ising_equilibrium", operating_points=list(OPERATING_POINTS),
                  xdot_kinds=list(XDOT_KINDS), tau_env_for=tau_env_for,
                  primitive_fn=multi_window_fdr_iter, kwargs_for=kwargs_for,
                  primitive_module_name="ising_equilibrium.measurements", n_realizations=N_REAL,
                  fidelity={"L": 32, "distance": None}, smoke=a.smoke,
                  only_op_labels=a.only_op, only_xdot=a.only_xdot)
    if not a.serial: kwargs["max_workers"] = a.workers
    runner(**kwargs)


if __name__ == "__main__":
    main()
