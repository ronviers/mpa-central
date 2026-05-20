from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from _shared.runtime import run, run_parallel                              # noqa: E402
from kww_oracle.measurements import multi_window_fdr_iter, XDOT_KINDS      # noqa: E402

CONTROL = {
    "role": "full_five_vector_oracle",
    "claim": "C(τ)=(1-q_EA)e^{-τ/τ_β}+q_EA e^{-(τ/τ_α)^β}; "
             "χ(τ)=dC_β+X·dC_α (FDT slope 1 then X). Genuine two-timescale.",
    "purpose": "Rung 5. two_temp_ou's pure-exp C only identifies X; this "
               "C is non-degenerate, so the inversion's full 5-vector "
               "(q_EA, τ_α, β_KWW, τ_β, X) must round-trip — not just X.",
}

# Fixed genuine two-timescale C-shape; X swept (parallels two_temp_ou and is
# the axis tied to FALSIFICATION.md's KEY FINDING). The replicated C-shape
# across X also exercises C-shape identifiability.
Q_EA = 0.7
TAU_ALPHA = 20.0
BETA_KWW = 0.6
TAU_BETA = 1.0

def _op(X, gt):
    return {"label": f"X{X:g}", "X": X, "q_EA": Q_EA, "tau_alpha": TAU_ALPHA,
            "beta_KWW": BETA_KWW, "tau_beta": TAU_BETA, "gt": gt,
            "control": {**CONTROL, "expected_X": X, "expected_q_EA": Q_EA,
                        "expected_tau_alpha": TAU_ALPHA,
                        "expected_beta_KWW": BETA_KWW,
                        "expected_tau_beta": TAU_BETA}}

OPERATING_POINTS = [
    _op(1.0, "r"),   # equilibrium aging (FDT holds on the alpha branch too)
    _op(0.5, "s"),   # aging
    _op(0.2, "k"),   # strong aging
]
H_FIELD = 0.05
N_REAL = 1024


def tau_env_for(op):
    return {"value": float(op["tau_alpha"]), "method": "kww_alpha_relaxation_time",
            "note": "alpha-relaxation timescale τ_α in step units (slow mode "
                    "sets the observation window)."}


def kwargs_for(op, xdot_kind, schedule, n_real):
    return dict(q_EA=op["q_EA"], tau_alpha=op["tau_alpha"],
                beta_KWW=op["beta_KWW"], tau_beta=op["tau_beta"], X=op["X"],
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
    kwargs = dict(substrate="kww_oracle", operating_points=list(OPERATING_POINTS),
                  xdot_kinds=list(XDOT_KINDS), tau_env_for=tau_env_for,
                  primitive_fn=multi_window_fdr_iter, kwargs_for=kwargs_for,
                  primitive_module_name="kww_oracle.measurements", n_realizations=N_REAL,
                  fidelity={"L": None, "distance": None}, smoke=a.smoke,
                  only_op_labels=a.only_op, only_xdot=a.only_xdot)
    if not a.serial: kwargs["max_workers"] = a.workers
    runner(**kwargs)


if __name__ == "__main__":
    main()
