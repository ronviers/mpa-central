"""Standalone grinder for the voter in-library primitive.

Writes cells to H:/mpa-central/library/data/voter/.

Usage (PowerShell):
  python H:/mpa-central/library/primitives/voter/grind.py             # parallel default
  python H:/mpa-central/library/primitives/voter/grind.py --workers 12
  python H:/mpa-central/library/primitives/voter/grind.py --serial    # one-core, debug
  python H:/mpa-central/library/primitives/voter/grind.py --smoke     # tiny, no writes
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]   # primitives/
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from _shared.runtime import run, run_parallel  # noqa: E402
from voter.measurements import multi_window_fdr_iter, XDOT_KINDS  # noqa: E402


OPERATING_POINTS = [
    {"label": "nu0.001", "nu": 0.001, "gt": "s"},
    {"label": "nu0.01",  "nu": 0.01,  "gt": "s"},
    {"label": "nu0.1",   "nu": 0.1,   "gt": "k"},
    {"label": "nu1.0",   "nu": 1.0,   "gt": "r"},
    {"label": "nu10.0",  "nu": 10.0,  "gt": "r"},
]

H_FIELD = 0.10
N_REAL = 1024


def tau_env_for(op: dict) -> dict:
    nu = float(op["nu"])
    return {
        "value": 1.0 / nu if nu > 0 else None,
        "method": "inverse_nu_mean_field",
        "note": "Mean-field placeholder: τ_env ≈ 1/ν.",
    }


def kwargs_for(op: dict, xdot_kind: str, schedule: dict, n_real: int) -> dict:
    return dict(
        nu=op["nu"],
        t_w=schedule["t_w"],
        t_obs=schedule["t_obs"],
        tau_windows=schedule["tau_windows"],
        h_field=H_FIELD,
        n_realizations=n_real,
        seed=0,
        n_sample_times=schedule["n_sample_times"],
        progress_every=0,
        xdot_kind=xdot_kind,
    )


def main():
    ap = argparse.ArgumentParser(description="Voter substrate grinder")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--serial", action="store_true",
                    help="Run one cell at a time (debugging). Default is parallel.")
    ap.add_argument("--workers", type=int, default=None,
                    help="Worker count (default: cpu_count - 2).")
    ap.add_argument("--only-op", action="append")
    ap.add_argument("--only-xdot", action="append")
    args = ap.parse_args()

    runner = run if args.serial else run_parallel
    kwargs = dict(
        substrate="voter",
        operating_points=list(OPERATING_POINTS),
        xdot_kinds=list(XDOT_KINDS),
        tau_env_for=tau_env_for,
        primitive_fn=multi_window_fdr_iter,
        kwargs_for=kwargs_for,
        primitive_module_name="voter.measurements",
        n_realizations=N_REAL,
        fidelity={"L": None, "distance": None, "N": 200},
        smoke=args.smoke,
        only_op_labels=args.only_op,
        only_xdot=args.only_xdot,
    )
    if not args.serial:
        kwargs["max_workers"] = args.workers
    runner(**kwargs)


if __name__ == "__main__":
    main()
