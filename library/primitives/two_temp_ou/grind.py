from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from _shared.runtime import run, run_parallel                            # noqa: E402
from two_temp_ou.measurements import multi_window_fdr_iter, XDOT_KINDS    # noqa: E402

CONTROL = {
    "role": "known_fdt_violation",
    "claim": "C(τ)=exp(-τ/τ_relax); χ(τ)=X·(1-C); FDR locus is a line of slope X.",
    "purpose": "First rung with a non-trivial known answer. Grinder must "
               "produce slope=X; inversion (next move) must recover X.",
}
TAU_RELAX = 20.0
OPERATING_POINTS = [
    {"label": "X1.0", "X": 1.0, "tau_relax": TAU_RELAX, "gt": "r", "control": {**CONTROL, "expected_X": 1.0}},
    {"label": "X0.7", "X": 0.7, "tau_relax": TAU_RELAX, "gt": "s", "control": {**CONTROL, "expected_X": 0.7}},
    {"label": "X0.5", "X": 0.5, "tau_relax": TAU_RELAX, "gt": "s", "control": {**CONTROL, "expected_X": 0.5}},
    {"label": "X0.3", "X": 0.3, "tau_relax": TAU_RELAX, "gt": "k", "control": {**CONTROL, "expected_X": 0.3}},
    {"label": "X0.1", "X": 0.1, "tau_relax": TAU_RELAX, "gt": "c", "control": {**CONTROL, "expected_X": 0.1}},
]
H_FIELD = 0.05
N_REAL = 1024


def tau_env_for(op):
    return {"value": float(op["tau_relax"]), "method": "exact_ou_relaxation_time",
            "note": "EXACT: OU relaxation time τ_relax in step units."}


def kwargs_for(op, xdot_kind, schedule, n_real):
    return dict(tau_relax=op["tau_relax"], X=op["X"],
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
    kwargs = dict(substrate="two_temp_ou", operating_points=list(OPERATING_POINTS),
                  xdot_kinds=list(XDOT_KINDS), tau_env_for=tau_env_for,
                  primitive_fn=multi_window_fdr_iter, kwargs_for=kwargs_for,
                  primitive_module_name="two_temp_ou.measurements", n_realizations=N_REAL,
                  fidelity={"L": None, "distance": None}, smoke=a.smoke,
                  only_op_labels=a.only_op, only_xdot=a.only_xdot)
    if not a.serial: kwargs["max_workers"] = a.workers
    runner(**kwargs)


if __name__ == "__main__":
    main()
