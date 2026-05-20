# In-library substrate primitives

This directory holds **lightweight substrate primitives** — thin
adapters that read a public-domain dataset (or run a simple in-process
simulation) and emit the streaming-primitive event shape per
[`H:/mpa-central/RULES.md`](../../RULES.md) §3, for consumption by
[`grind_library.py`](../grind_library.py).

## Why in-library rather than per-substrate H:\ repo

Two homes by design:

| Home | When to use |
|---|---|
| **External H:\ repo** (`H:/mpa-brain/`, `H:/mpc-glass/`, `H:/mpc-quantum/`) | Substrate has non-trivial dependencies (C++ build, large vendored libraries), accumulated per-repo discipline (CLAUDE.md, FOOTING.md, journey docs), or is a citable standalone artifact. |
| **In-library primitive** (`primitives/<name>/`) | Substrate is a thin reader of a public dataset, has no non-stdlib dependencies beyond numpy / a parser library, and doesn't need its own dev cycle separate from `mpa-central`. |

Adding a new external-repo substrate requires editing
`grind_library.py::SUBSTRATE_PATHS_EXTERNAL`. Adding an in-library
primitive is "drop in a folder" — `grind_library.py` auto-discovers
each subdirectory of this directory as a substrate package via
`discover_in_library_substrates()`. The substrate's name is its
directory name; the directory IS the importable Python package.

## Per-primitive directory layout

```
primitives/<substrate>/
├── __init__.py                 # makes the directory an importable package
├── measurements.py             # the streaming-primitive entry point
│                               # exports `multi_window_fdr_iter(...)` and `XDOT_KINDS`
├── data_loader.py              # reads the public dataset (or runs a small sim)
├── README.md                   # what dataset, license, OP axis, ẋ choices,
│                               # any caveats. Required.
└── FOOTING.md                  # optional. Substrate-specific findings per
                                # RULES §9. Mirrors the per-repo FOOTING pattern.
```

The `measurements.py` interface must expose at minimum:

```python
XDOT_KINDS: tuple[str, ...]  # the substrate's ẋ-choice names

def multi_window_fdr_iter(
    operating_point: dict,        # {label, <param>, gt, ...}
    xdot_kind: str,
    schedule: dict,                # {t_w, t_obs, tau_windows, n_sample_times, n_realizations}
    *,
    rng_seed: int = 0,
) -> Iterator[dict]:
    """Yields streaming-primitive events per RULES §3:
    {kind: 'init', ...}
    {kind: 'phase_a', ...}    # optional, sparse
    {kind: 'snapshot', ...}
    {kind: 'phase_b', ...}    # optional, sparse
    {kind: 'sample', t, dt, C_mean, C_sem, chi_mean, chi_sem, per_window: [...]}
    ...
    {kind: 'complete', ...}
    """
```

See [`H:/mpa-brain`](https://github.com/ronviers/mpa-brain) /
[`H:/mpc-glass`](https://github.com/ronviers/mpc-glass) /
[`H:/mpc-quantum`](https://github.com/ronviers/mpc-quantum) for
external-repo worked instances. The same interface applies in-library.

## Promotion to its own repo

A primitive **graduates** out of `primitives/` and into its own H:\
repo only when one of these triggers:

- Dependencies grow beyond what fits cleanly in `mpa-central`'s footprint.
- The substrate accumulates discipline of its own (a RULES §10 / §11
  worked-instance style entry pointing at it).
- The substrate's community wants a citable standalone artifact (DOI).
- The substrate needs its own CI / release cycle independent of `mpa-central`.

Until then, in-library is the default. Most public-dataset-derived
substrates will stay here permanently — they're adapters, not full
substrate engines.

## Existing in-library primitives

Ten thin self-contained simulators landed 2026-05-19 from the
substrate-source research at
[`H:/mpa-central/substrate source research.md`](../../substrate source research.md):

| Name | Domain | OP axis | Reference dataset |
|---|---|---|---|
| [`voter`](voter/) | Network dynamics / opinion | switching rate ν | Leeds 1080 (CC-BY 4.0) |
| [`sk`](sk/) | Mean-field spin glass | T | Zenodo 4318983 (CC-BY 4.0) |
| [`abp`](abp/) | Active matter / colloids | Péclet Pe | amep (BSD-3) |
| [`fbm`](fbm/) | Anomalous diffusion | Hurst H | AnDi (CC-BY) |
| [`sir`](sir/) | Epidemic dynamics | R₀ | CDC `cfa-gam-rt` (public domain) |
| [`east`](east/) | Kinetically constrained model | T | KCM literature |
| [`wright_fisher`](wright_fisher/) | Population genetics | selection s | Dryad wdbrv162z (CC0) |
| [`heston`](heston/) | Financial / regime-switching | regime pack | Kaggle fsynth (MIT) |
| [`lotka_volterra`](lotka_volterra/) | Predator-prey ecology | prey α | SLV literature |
| [`levy_flight`](levy_flight/) | Lévy CTRW / heavy tails | tail α | AnDi (CC-BY) |

### Invalidator battery (falsification targets, 2026-05-19)

Five substrates built **to make MPA fail**, not to add coverage. Each
has a known ground truth (analytic or framework-named) and a stated
falsifier; each operating point carries an `invalidator` block in its
`operating_point` dict. The substrate's own ground truth is verified
before it counts as a valid test (e.g. `ou_equilibrium` is confirmed to
honor FDT, X≈1, so any aging MPA reports there is a real false positive).

| Name | Attack | Falsifier |
|---|---|---|
| [`ou_equilibrium`](ou_equilibrium/) | analytic FDT null (exact `C=e^{-t/τ}`, X=1) | MPA reports X≠1 or aging |
| [`ising_equilibrium`](ising_equilibrium/) | critical-slowing ≠ aging (2D Ising at Tc) | persistent X<1 in equilibrium |
| [`driven_ring`](driven_ring/) | sustained NESS current — attacks "everything → r" axiom | r forced on a perpetual current |
| [`mm1_queue`](mm1_queue/) | corpus's own named falsifier (common-exponent triality) | α_s ≠ heavy-traffic exponent ½ |
| [`logistic_chaos`](logistic_chaos/) | attacks the stochasticity premise (deterministic, no bath) | finite FDT-respecting regime on a Lyapunov-divergent system |

These are read the same way as any cell, but the *point* is the
interpretation: does X stay 1 where it must, does a regime walk falsely
appear, does α_s match the named exponent. A "pass" here is MPA
surviving; a "fail" is the program's most valuable possible result.

Each is run by `python primitives/<name>/grind.py [--smoke]`. All emit
SEM (chi-convention improvement over brain). Each has 5 operating
points × 2 ẋ choices = 10 cells. Shared protocol in
[`_shared/protocol.py`](_shared/protocol.py); shared time-grid /
atomic-write / aggregator in [`_shared/runtime.py`](_shared/runtime.py).
The 10 primitives sit alongside the three external production
substrates (brain, glass, quantum) — not a replacement, a wider
substrate-class basis for cross-substrate work.

## Why this matters for adding substrates fast

The outbound-research prompt for new substrates expects the workflow:

1. Find a dataset (research channel returns candidates).
2. `mkdir primitives/<name>/`; drop in `__init__.py`, `measurements.py`,
   `data_loader.py`, `README.md`.
3. `python grind_library.py --substrate <name>` — auto-discovered;
   produces cells in `data/<name>/`.
4. `python -m conformer.curator.walk_library` over in mpa-conform —
   produces v0.4 bundles.
5. `python -m conformer.cli compare-all --class <new-class>` — produces
   comparison PNGs; reveals whether any framework piece needed
   substrate-specific extension.

No edits to `grind_library.py` for new substrates that fit the
existing schema. No new top-level H:\ directory. The substrate just
appears.
