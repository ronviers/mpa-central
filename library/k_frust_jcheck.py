"""Robustness of the J meter: is frustrated-vs-control separation stable across
seeds, and is control J consistent with ~0? Bulletproofs the instrument the
Wall round-trip will depend on."""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "H:/mpa-central/library")
import numpy as np
from k_frust_meter import simulate, G_FRUST, G_CTRL

SEEDS = [1, 2, 3, 4, 5, 6]
Jf, Jc = [], []
for s in SEEDS:
    *_, J_f, _ = simulate(G_FRUST, seed=s)
    *_, J_c, _ = simulate(G_CTRL, seed=s)
    Jf.append(J_f); Jc.append(J_c)
    print(f"seed {s}: J_frust={J_f:+.4e}  J_control={J_c:+.4e}")

Jf = np.array(Jf); Jc = np.array(Jc)
print(f"\nfrust   J = {Jf.mean():+.4e} +/- {Jf.std(ddof=1):.2e}")
print(f"control J = {Jc.mean():+.4e} +/- {Jc.std(ddof=1):.2e}")
sep = abs(Jf.mean()) / max(abs(Jc.mean()), Jc.std(ddof=1), 1e-12)
print(f"separation |J_frust| / max(|J_control|, sd) = {sep:.1f}x")
print(f"control consistent with 0? |mean|/sd = {abs(Jc.mean())/max(Jc.std(ddof=1),1e-12):.2f} (sigma)")
