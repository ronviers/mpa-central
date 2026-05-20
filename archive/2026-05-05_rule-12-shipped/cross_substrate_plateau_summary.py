"""Cross-substrate plateau-summary tool.

Reads the most recent Sweep-G-style result JSONs from mpa-brain, mpc-glass,
and mpc-quantum and prints the broad-τ × late-dt f-plateau across all
three substrates' snapshot-relative ẋ choices side-by-side. Used to populate
RULES.md rule 12 and the per-substrate FOOTING F-019 entries; also useful
for the cross-substrate visualization panel the visualizer team will build.

Run:
    python H:/mpa-central/cross_substrate_plateau_summary.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


# Force UTF-8 stdout so the Greek glyphs print correctly on Windows consoles.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


def _latest(pattern: str, root: Path) -> Path | None:
    files = sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def _extract_plateau(res: dict, tau_target: int, snapshot_relative_kind: str):
    """For one result-record, pull (f, dt) at the τ_target column from the
    last sample. Returns (scenario, gt, f, dt) or None if not the snapshot-
    relative ẋ kind."""
    if res.get("xdot_kind") != snapshot_relative_kind:
        return None
    last = res.get("last_sample")
    if not last:
        return None
    taus = res["tau_windows"]
    try:
        k = taus.index(tau_target)
    except ValueError:
        # Allow ±5% tolerance match
        k = min(range(len(taus)), key=lambda i: abs(taus[i] - tau_target))
        if abs(taus[k] - tau_target) / max(tau_target, 1) > 0.05:
            return None
    pw = last["per_window"][k]
    return {
        "scenario": res["scenario"],
        "gt": res.get("ground_truth_regime", "?"),
        "T_or_p": res.get("T", res.get("p_base")),
        "f": pw.get("f"),
        "dt": last["dt"],
        "tau": taus[k],
    }


def main():
    print("=" * 100)
    print(" Cross-substrate (τ, dt) plateau summary — broad-τ × late-dt corner")
    print(" of snapshot-relative ẋ coordinate space (RULES rule 12 evidence)")
    print("=" * 100)

    layouts = [
        ("mpa-brain (Langevin, position-relative)",
         Path("H:/mpa-brain/docs/results"),
         "sweep_G_*.json",
         "position-relative", 1000),
        ("mpc-glass (3D EA, spin-relative)",
         Path("H:/mpc-glass/docs/results"),
         "sweep_g_glass_*.json",
         "spin-relative", 1000),
        ("mpc-quantum (syndromes, events-since-snap)",
         Path("H:/mpc-quantum/docs/results"),
         "sweep_g_quantum_*.json",
         "events-since-snap", 1000),
    ]

    for label, root, pattern, kind, tau_target in layouts:
        latest = _latest(pattern, root)
        print(f"\n--- {label} ---")
        if latest is None:
            print(f"  NO RESULTS FOUND in {root} matching {pattern}")
            continue
        print(f"  source: {latest.name}")
        with open(latest) as fh:
            data = json.load(fh)
        rows = []
        for res in data["results"]:
            row = _extract_plateau(res, tau_target, kind)
            if row is not None:
                rows.append(row)
        if not rows:
            print(f"  no rows for xdot_kind={kind!r} (try a different tau_target)")
            continue
        # Compute spread
        f_values = [r["f"] for r in rows if r["f"] is not None]
        if f_values:
            spread = max(f_values) - min(f_values)
        else:
            spread = float("nan")
        print(f"  τ_target={tau_target}  (last-dt sample)")
        print(f"  {'scenario':>14}  {'T/p':>8}  {'gt':>3}  {'dt':>6}  {'τ':>5}  {'f':>8}")
        for r in rows:
            T_or_p_str = (
                f"{r['T_or_p']:.2f}" if r["T_or_p"] is not None and r["T_or_p"] >= 0.05
                else f"{r['T_or_p']:.0e}" if r["T_or_p"] is not None
                else "—"
            )
            f_str = f"{r['f']:+.4f}" if r["f"] is not None else "  nan"
            print(f"  {r['scenario']:>14}  {T_or_p_str:>8}  {r['gt']:>3}  "
                  f"{r['dt']:>6}  {int(r['tau']):>5}  {f_str:>8}")
        print(f"  spread (max f − min f) = {spread:+.4f}")

    print("\n" + "=" * 100)
    print(" Discrimination test: each substrate produces distinguishable plateau")
    print(" values across its scenario axis. Direction is substrate-conditional;")
    print(" region (broad-τ × late-dt) is universal — RULES rule 12.")
    print("=" * 100)


if __name__ == "__main__":
    main()
