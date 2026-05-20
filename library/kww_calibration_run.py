"""kww_oracle X-recovery CALIBRATION run (background, long-form).

Purpose: turn the 10-second 3-point check into a high-resolution
validation. NOT 'same test, more realizations' -- a redesign:

  * estimator   = fit_kww5 (segmented 5-vector), NEVER a single slope.
                  (single-slope is biased UP on aging loci -- compute
                  cannot fix a method bias, only the estimator can.)
  * X grid      = fine sweep (default 20 points 0.05..1.0), so the
                  output is a recovered-vs-prescribed CALIBRATION CURVE.
  * reps        = independent sim seeds per X -> honest CIs (mean +/- std).
  * realizations/sample-density = where the long wall-clock goes; shrinks
                  statistical scatter ~1/sqrt(N).

Deliverable: results JSON + calibration PNG (recovered X vs prescribed X
with error bars). Puts X-recovery to rest, or isolates a residual bias
as generator-vs-fitter rather than noise.

Does NOT touch the canonical data/kww_oracle/ cells -- writes to a
separate substrate folder data/kww_calib_<tag>/.

Verify wiring fast:   python kww_calibration_run.py --smoke
Real background run:  python kww_calibration_run.py --x-steps 20 --reps 8 \
                          --n-real 16384 --n-sample 80 --tag run1
(launch in its own terminal; it prints progress and a final artifact path.)
"""
from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

LIB = Path("H:/mpa-central/library")
PRIM = LIB / "primitives"
for p in (str(PRIM), "H:/mpa-conform"):
    if p not in sys.path:
        sys.path.insert(0, p)

import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from _shared import runtime
from _shared.runtime import run_parallel
from kww_oracle.measurements import XDOT_KINDS
from kww_oracle import grind as kg
from conformer.compute.five_vector import fit_kww5

OUT_DIR = LIB / "output" / "kww_calibration"
DATA_ROOT = runtime.DATA_ROOT  # data/<substrate>/


def build_ops(x_grid, reps):
    """One op per (X, rep). gt label is cosmetic here."""
    ops = []
    for X in x_grid:
        for rep in range(reps):
            op = kg._op(float(X), "s")
            op = {**op, "label": f"X{X:.4f}_r{rep}", "rep": rep, "X": float(X)}
            ops.append(op)
    return ops


def kwargs_for_seeded(op, xdot_kind, schedule, n_real):
    """Like kww grind kwargs_for but seed varies by rep (independent batches)."""
    kw = kg.kwargs_for(op, xdot_kind, schedule, n_real)
    kw["seed"] = int(op.get("rep", 0)) * 100003 + 7
    return kw


def fit_cell(cell_path, tau_scale):
    c = json.loads(Path(cell_path).read_text(encoding="utf-8"))
    s = c["results"]["all_samples"]
    rows = [{"tau": float(e["dt"]) / tau_scale,
             "C": float(e["C_mean"]),
             "chi": float(e["chi_mean"])} for e in s]
    fit = fit_kww5(rows, T=1.0)
    return fit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--x-min", type=float, default=0.05)
    ap.add_argument("--x-max", type=float, default=1.0)
    ap.add_argument("--x-steps", type=int, default=20)
    ap.add_argument("--reps", type=int, default=8, help="independent seeds per X (CI width)")
    ap.add_argument("--n-real", type=int, default=16384, help="realizations per cell (~1/sqrt(N) scatter)")
    ap.add_argument("--n-sample", type=int, default=80, help="lag-grid density (denser locus)")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--tag", default="run1")
    ap.add_argument("--smoke", action="store_true", help="tiny budgets to verify wiring in seconds")
    a = ap.parse_args()

    if a.smoke:
        a.x_steps, a.reps, a.n_real, a.n_sample = 4, 2, 64, 16

    x_grid = np.round(np.linspace(a.x_min, a.x_max, a.x_steps), 4)
    substrate = f"kww_calib_{a.tag}"
    tau_scale = float(kg.TAU_ALPHA)

    # densify the lag grid (module-global read at call-time inside time_grids_for)
    runtime.LIB_N_SAMPLE_TIMES = int(a.n_sample)

    ops = build_ops(x_grid, a.reps)
    n_tasks = len(ops) * len(["velocity"])
    print(f"[calib] substrate={substrate}  X-grid={a.x_steps}pts [{a.x_min}..{a.x_max}]  "
          f"reps={a.reps}  n_real={a.n_real}  n_sample={a.n_sample}")
    print(f"[calib] {n_tasks} cells to grind. estimator=fit_kww5 (segmented). "
          f"writing data/{substrate}/ (canonical kww_oracle untouched).")

    t0 = time.time()
    run_parallel(
        substrate=substrate,
        operating_points=ops,
        xdot_kinds=["velocity"],
        tau_env_for=kg.tau_env_for,
        kwargs_for=kwargs_for_seeded,
        primitive_module_name="kww_oracle.measurements",
        n_realizations=a.n_real,
        fidelity={"L": None, "distance": None},
        smoke=False,
        only_xdot=["velocity"],
        max_workers=a.workers,
    )
    print(f"[calib] grind done in {time.time()-t0:.1f}s. fitting fit_kww5 per cell...")

    # fit every cell, group recovered X by prescribed X
    folder = DATA_ROOT / substrate
    by_x: dict[float, list[float]] = {}
    extras: dict[float, list[dict]] = {}
    for X in x_grid:
        by_x[float(X)] = []
        extras[float(X)] = []
        for rep in range(a.reps):
            cell = folder / f"{substrate}__X{X:.4f}_r{rep}__velocity.json"
            if not cell.exists():
                print(f"  [warn] missing {cell.name}")
                continue
            try:
                fit = fit_cell(cell, tau_scale)
                by_x[float(X)].append(float(fit.X))
                extras[float(X)].append({"q_EA": float(fit.q_EA), "beta_KWW": float(fit.beta_KWW),
                                          "tau_alpha": float(fit.tau_alpha), "residual": float(fit.residual),
                                          "success": bool(fit.success)})
            except Exception as e:  # noqa: BLE001
                print(f"  [warn] fit failed {cell.name}: {e}")

    # aggregate
    rows = []
    for X in x_grid:
        vals = np.array(by_x[float(X)], dtype=float)
        if len(vals) == 0:
            continue
        rows.append({"X_prescribed": float(X), "X_recovered_mean": float(vals.mean()),
                     "X_recovered_std": float(vals.std(ddof=1)) if len(vals) > 1 else 0.0,
                     "n": int(len(vals)),
                     "bias": float(vals.mean() - X)})

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    res_path = OUT_DIR / f"calibration_{a.tag}.json"
    res_path.write_text(json.dumps({"config": vars(a), "rows": rows}, indent=2), encoding="utf-8")

    # calibration plot
    xp = np.array([r["X_prescribed"] for r in rows])
    xr = np.array([r["X_recovered_mean"] for r in rows])
    xe = np.array([r["X_recovered_std"] for r in rows])
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(13, 5.5))
    axa.plot([0, 1], [0, 1], "k--", lw=1.2, label="ideal (recovered = prescribed)")
    axa.errorbar(xp, xr, yerr=xe, fmt="o-", color="tab:blue", ms=5, capsize=3,
                 label=f"fit_kww5 (reps={a.reps}, n_real={a.n_real})")
    axa.set_xlabel("prescribed X"); axa.set_ylabel("recovered X (mean +/- std)")
    axa.set_title("X-recovery calibration"); axa.legend(fontsize=9); axa.grid(alpha=0.3)
    axb.axhline(0, color="k", ls="--", lw=1.0)
    axb.errorbar(xp, xr - xp, yerr=xe, fmt="o-", color="tab:red", ms=5, capsize=3)
    axb.set_xlabel("prescribed X"); axb.set_ylabel("recovered - prescribed (bias)")
    axb.set_title("residual bias vs X  (flat-zero => to rest; structured => real)")
    axb.grid(alpha=0.3)
    fig.suptitle(f"kww_oracle X-recovery calibration [{a.tag}]  —  segmented fit_kww5, not single-slope", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    png = OUT_DIR / f"calibration_{a.tag}.png"
    fig.savefig(png, dpi=130)

    print("\n[calib] DONE")
    for r in rows:
        print(f"  X={r['X_prescribed']:.3f}  recovered={r['X_recovered_mean']:.3f} "
              f"+/- {r['X_recovered_std']:.3f}  bias={r['bias']:+.3f}  (n={r['n']})")
    print(f"\n[calib] artifact: {png}")
    print(f"[calib] data:     {res_path}")


if __name__ == "__main__":
    main()
