from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from _shared.runtime import run, run_parallel                       # noqa: E402
from heston.measurements import multi_window_fdr_iter, XDOT_KINDS   # noqa: E402

OPERATING_POINTS = [
    {"label": "bull", "gt": "c", "regime_params": {
        "regime": "bull", "mu": 0.10, "kappa": 4.0, "theta": 0.02,
        "xi": 0.15, "rho": -0.3, "lam": 0.5, "sJ": 0.005,
    }},
    {"label": "mid",  "gt": "s", "regime_params": {
        "regime": "mid",  "mu": 0.05, "kappa": 2.5, "theta": 0.04,
        "xi": 0.30, "rho": -0.5, "lam": 1.0, "sJ": 0.010,
    }},
    {"label": "bear", "gt": "s", "regime_params": {
        "regime": "bear", "mu": -0.05, "kappa": 1.5, "theta": 0.08,
        "xi": 0.50, "rho": -0.7, "lam": 2.0, "sJ": 0.015,
    }},
    {"label": "crisis_low", "gt": "k", "regime_params": {
        "regime": "crisis_low", "mu": -0.15, "kappa": 0.8, "theta": 0.20,
        "xi": 0.80, "rho": -0.8, "lam": 5.0, "sJ": 0.025,
    }},
    {"label": "crisis_high", "gt": "r", "regime_params": {
        "regime": "crisis_high", "mu": -0.30, "kappa": 0.4, "theta": 0.40,
        "xi": 1.20, "rho": -0.9, "lam": 20.0, "sJ": 0.04,
    }},
]
H_FIELD = 0.05
N_REAL = 1024


def tau_env_for(op):
    rp = op["regime_params"]
    kappa = float(rp["kappa"])
    val = 252.0 / kappa
    return {"value": val, "method": "variance_mean_reversion_inverse_kappa",
            "note": "τ_env ≈ 1/κ in step units (1 step = DT = 1/252 yr)."}


def kwargs_for(op, xdot_kind, schedule, n_real):
    return dict(regime_params=op["regime_params"],
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
    kwargs = dict(substrate="heston", operating_points=list(OPERATING_POINTS),
                  xdot_kinds=list(XDOT_KINDS), tau_env_for=tau_env_for,
                  primitive_fn=multi_window_fdr_iter, kwargs_for=kwargs_for,
                  primitive_module_name="heston.measurements", n_realizations=N_REAL,
                  fidelity={"L": None, "distance": None}, smoke=a.smoke,
                  only_op_labels=a.only_op, only_xdot=a.only_xdot)
    if not a.serial: kwargs["max_workers"] = a.workers
    runner(**kwargs)


if __name__ == "__main__":
    main()
