"""Control for the Wall-proxy: can the imposed Hebbian rule even SUSTAIN an
existing frustration (no chaos)? If antisym strength decays from 1 with
plasticity on, the rule is incapable -> the proxy's 'BROKE' is a rule artifact,
not MPA -> the faithful test must be option 2 (derived reformation).
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "H:/mpa-central/library")
import numpy as np
from k_frust_wall_proxy import (step, hebbian_update, antisym_strength, chirality,
                                 G_FRUST, G0, SIGMA, DT, N_REAL)

rng = np.random.default_rng(1)
rho = np.tile([0.06, 0.03, 0.01], (N_REAL, 1)).astype(float)
g0 = np.array([G0, G0, G0])
gmat = G_FRUST.copy()

# establish the cycle with gamma FIXED
for _ in range(6000):
    rho = step(rho, gmat, g0, rng, SIGMA)

print("plasticity ON, NO chaos -- does the frustrated wiring survive the rule?")
print(f"{'t':>7} {'antisym':>9} {'J(chirality)':>13}")
for blk in range(12):
    Js = []
    for _ in range(1000):
        rp = rho.copy()
        rho = step(rho, gmat, g0, rng, SIGMA)
        gmat = hebbian_update(gmat, rho, rp, rng, 0.0)  # plastic, no chaos noise
        Js.append(chirality(rho, rp))
    print(f"{(blk+1)*1000:>7} {antisym_strength(gmat):>9.3f} {np.mean(Js):>13.4e}")

print(f"\nfinal antisym = {antisym_strength(gmat):+.3f} (1=frustrated maintained, ~0=rule destroyed it)")
