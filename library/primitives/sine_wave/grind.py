from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from _shared.runtime import run, run_parallel                          # noqa: E402
from sine_wave.measurements import multi_window_fdr_iter, XDOT_KINDS    # noqa: E402

CONTROL = {
    "role": "character_zero_pure_tone",
    "claim": "Single-frequency driven signal; C(τ)=cos(2π τ/P), never relaxes. "
             "Smooth sibling of square_wave (cosine vs triangle = pure tone vs harmonics).",
    "purpose": "Test how far a monotone-relaxation cdv1 fit follows an "
               "oscillating (recurring) C. Where it peels off is diagnostic.",
    "analytic_C": "cos(2*pi*tau/P)",
}
OPERATING_POINTS = [
    {"label": "P10",   "P": 10.0,   "gt": "r", "control": CONTROL},
    {"label": "P30",   "P": 30.0,   "gt": "r", "control": CONTROL},
    {"label": "P100",  "P": 100.0,  "gt": "r", "control": CONTROL},
    {"label": "P300",  "P": 300.0,  "gt": "r", "control": CONTROL},
    {"label": "P1000", "P": 1000.0, "gt": "r", "control": CONTROL},
]
H_FIELD = 0.5
N_REAL = 1024


def tau_env_for(op):
    return {"value": float(op["P"]), "method": "sine_wave_period",
            "note": "EXACT: the period P is the only timescale (no relaxation)."}


def kwargs_for(op, xdot_kind, schedule, n_real):
    return dict(P=op["P"], t_w=schedule["t_w"], t_obs=schedule["t_obs"],
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
    kwargs = dict(substrate="sine_wave", operating_points=list(OPERATING_POINTS),
                  xdot_kinds=list(XDOT_KINDS), tau_env_for=tau_env_for,
                  primitive_fn=multi_window_fdr_iter, kwargs_for=kwargs_for,
                  primitive_module_name="sine_wave.measurements", n_realizations=N_REAL,
                  fidelity={"L": None, "distance": None}, smoke=a.smoke,
                  only_op_labels=a.only_op, only_xdot=a.only_xdot)
    if not a.serial: kwargs["max_workers"] = a.workers
    runner(**kwargs)


if __name__ == "__main__":
    main()
