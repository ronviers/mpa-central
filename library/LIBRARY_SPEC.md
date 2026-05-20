# MPA Library Specification

The MPA library is a *characterized lightfield* of the framework's
multi-window FDR observable across the program's three production
substrates: Langevin (mpa-brain), 3D EA Ising glass (mpc-glass), and
surface-code syndromes (mpc-quantum). One library file per
(substrate, operating-point, ẋ-choice) triple. Once produced, every
test in [`H:/mpa-central/ONE_TRUE_TEST_ROADMAP.md`](../ONE_TRUE_TEST_ROADMAP.md)
that doesn't require new substrate runs (Tests 1, 3, 4, 5) becomes a
query against the library.

This spec defines the contract: what the substrate must produce for a
result to be library-grade, what the library file looks like, and what
*isn't* in the library and why.

## Philosophy — DVD, not Polaroid

The current dial-in regime: cheap exploratory sweeps, redo if you need
something different. Acceptable while you're discovering primitives;
load-bearing once rule 12 lands. The library moves the program from
"sample sparsely, hope" to "characterize completely, query."

The DVD analogy: 44.1 kHz × 16-bit captures the human-audible envelope
exhaustively, so the receiver / source / listener triangle is no longer
a question for the recording. The MPA library does the same for the
multi-window FDR observable: dense τ_obs grid, dense (t, dt) grid,
n_real high enough that σ < 0.005, full operating-point coverage,
both ẋ choices. After that, "what does MPA say about scenario X
through ẋ Y at scale Z" is a JSON read, not a substrate run.

## Per-substrate axes

| Axis | Brain | Glass | Quantum |
|---|---|---|---|
| Operating-point parameter | scenario name (4 categorical) | T (continuous) | p_base (continuous) |
| Operating-point grid | committed, suspended, conflict, reset | 11 logspace pts spanning Tc≈0.95: {0.20, 0.30, 0.50, 0.70, 0.85, 0.95, 1.00, 1.10, 1.30, 1.50, 1.80} | 11 logspace pts spanning threshold: logspace(-4, -1.3, 11) |
| ẋ choices | velocity, position-relative, position-displacement, boundary-cross | spin-flip, spin-relative | detection-event, events-since-snap |
| τ_obs grid | **τ_env-anchored per operating point** (see below) | same | same |
| t_obs | **τ_env-anchored per operating point** (see below) | same | same |
| n_sample_times | 31 log-spaced t-points in [t_w, t_w + t_obs] | same | same |
| Realizations | n_real = 4096 | n_real = 1024 | n_seeds × n_shots = 16 × 1024 = 16384 |
| Substrate fidelity | (Langevin is exact; integrator step DT is fixed) | L = 16 | distance d = 3 |

**L and d are not library axes.** They are substrate-fidelity choices.
A separate one-off cross-check at L=24 / d=5 verifies the rule-12
plateau is L/d-independent; that's a confirmation pass, not a routine
library axis.

**Realization counts** target σ_f < 0.005 on each cell. Brain's primitive
does internal replica averaging — n_real=4096 is one call. Glass and
quantum loop externally; their realizations × shots are tuned per
substrate's per-realization wall.

## τ_env-anchored sampling — the central design choice

**Physics insight (load-bearing):** every finite-flux structure decays
to *r* at infinity. The maintenance bookkeeping budget runs out for
any *c* and *s* trail given enough time. So the *interesting* time
window for any operating point is bounded above by the substrate's
own relaxation timescale τ_env — sampling much beyond it is sampling
the trivial r-asymptote. Sampling much before it is sampling
pre-relaxation. Either way, no MPA observable signal lives there.

A library that uses a single fixed time grid across all operating
points wastes ~half its realizations confirming r-asymptote at
fast-relaxing operating points, and *misses* the aging window
entirely at slow-relaxing operating points (e.g., quantum at p=1e-4
with τ_env≈10000 has its plateau at dt > 30000 — outside a fixed
[1, 30000] grid). The library catches what it should catch, only by
matching its time grids to each operating point's τ_env.

### Per-operating-point time-grid scaling

For each task, schedule is computed by `time_grids_for(τ_env_analytic)`:

```
if τ_env_analytic is finite:
  τ_obs grid:  31 log-spaced from 0.05·τ_env to min(2·τ_env, 5000)
  t_obs:       max(10·τ_obs_max [rule 8], 30·τ_env [aging coverage]),
                capped at 200,000
  t_w:         max(500, 5·τ_env), capped at 5,000

if τ_env_analytic is None or unbounded:
  Fallback to fixed defaults: τ_obs ∈ [1, 1000], t_obs = 30,000, t_w = 500.
  (Used for glass below Tc, where the substrate ages on the experiment
  timescale itself; the fixed grid characterizes as much aging as
  fits in the budget.)
```

**Why these specific constants:**
- `0.05·τ_env to 2·τ_env` — broad enough span across τ_env to walk
  the v8 §5 regime hierarchy (narrow → c-like, mid → s, broad → r-like
  in either substrate-class direction).
- `30·τ_env` for t_obs — enough to span 1.5 decades past τ_env, capturing
  the aging window's tail without sampling deep into r-asymptote.
- Cap at `200,000` — a hard compute-budget cap. Quantum p=1e-4
  hits this; t_obs there is short of 30·τ_env but still spans 1.3
  decades past τ_env — adequate.
- Cap τ_obs_max at `5,000` — kernel widths much larger than this
  generate kernel-warmup budgets (10·τ_obs_max) that exceed the t_obs
  cap. Bounding τ_obs_max keeps rule 8 compatible with the cap.

### What the substrate emits

Each task records the actual `(tau_windows, t_w, t_obs, n_sample_times)`
used in its schedule block, so every library file is self-describing.
Cross-substrate analyses join by τ_env-rescaled coordinates, not by
absolute t / τ_obs values.

### τ_env_analytic placeholder values used today

Until substrate-side raw-readout autocorrelation emission lands
(see "What the library does not contain"), τ_env is set per operating
point from the analytic table:

| Substrate | Method | Values |
|---|---|---|
| Brain | scenario table | committed=1000, suspended=300, conflict=500, reset=50 |
| Glass | critical-slowing zν=6 around Tc≈1.1 | finite for T > Tc; None (fallback grid) for T ≤ Tc |
| Quantum | 1/p_base | p_base ∈ [1e-4, 5e-2] → τ_env ∈ [20, 10000] |

A factor-of-2 wobble in τ_env_analytic shifts the time grid by half a
log-decade — well within the 31-point grid's resolution. The library
remains robust to placeholder error of this magnitude.

## Library file format

One JSON file per (substrate, operating-point, ẋ-choice) triple. Filename
convention:

- brain: `brain_<scenario>_<xdot_kind>.json`
- glass: `glass_T<T:.3f>_<xdot_kind>.json`
- quantum: `quantum_p<p_base:.0e>_<xdot_kind>.json`

Schema:

```json
{
  "library_spec_version": "1.0",
  "substrate": "brain|glass|quantum",
  "operating_point": {
    "label": "committed",
    "scenario": "committed",
    "h_field": null,
    "T": null,
    "p_base": null,
    "delta_p": null
  },
  "xdot_kind": "position-relative",
  "fidelity": {"L": null, "distance": 3},
  "schedule": {
    "t_w": 500, "t_obs": 30000,
    "tau_windows": [...31 floats...],
    "n_sample_times": 31,
    "n_realizations": 4096,
    "n_shots": null, "n_seeds": null
  },
  "tau_env_analytic": {
    "value": 1000.0,
    "method": "scenario_table|inverse_p_base|critical_slowing_zν6",
    "note": "Analytic placeholder. Real measurement is owed and will populate tau_env_measured when substrate-side raw-readout autocorrelation emission lands."
  },
  "tau_env_measured": null,
  "results": {
    "all_samples": [
      {
        "t": 1500, "dt": 1000,
        "C_mean": ..., "C_sem": ...,    // SEM only available where the substrate
        "chi_mean": ..., "chi_sem": ..., // primitive supports external aggregation
        "per_window": [
          {
            "tau_window": 100,
            "C_d_mean": ..., "C_d_sem": ...,
            "C_d_diag_mean": ..., "C_d_diag_sem": ...,
            "chi_d_mean": ..., "chi_d_sem": ...,
            "d_norm_mean": ..., "d_norm_sem": ...,
            "sigma_d_mean": ..., "sigma_d_sem": ...,
            "f_mean": ..., "f_sem": ...,
            "n_realizations": 1024
          }
        ]
      }
    ]
  },
  "wall_seconds": 312.4,
  "completed_at": "2026-05-05T16:42:11Z",
  "git_sha": null,
  "primitive_module": "mpc_glass_packs.measurements",
  "primitive_version": null
}
```

Where SEM = std(values across realizations) / sqrt(n). Brain's primitive
doesn't expose per-realization values, so brain's library files have
`*_sem = null` and a top-level note. Adding SEM to brain is a
substrate-side upgrade owed alongside the raw-readout autocorrelation
emission that would populate `tau_env_measured` (see next section).

## What the library *does not* contain (and why)

- **Substrate raw state.** Spin fields, particle trajectories, syndrome
  streams. They're huge and reconstructible from substrate seeds. The
  library captures the MPA observable, not the substrate's full lightfield.
- **τ_env measured per operating point.** Owed. The current substrate
  primitives don't emit a raw-readout autocorrelation timescale. Until
  they do, library files carry an *analytic* τ_env placeholder with a
  method tag and a null `tau_env_measured` field. When the substrate-side
  upgrade lands, the schema is unchanged — only the field gets populated.
- **Hysteresis / reverse-replay traces.** Test 3 needs a `reverse_replay`
  flag on each substrate's primitive; once that's added, the library
  schema gains an optional `reverse_results` block. Until then, only
  forward results.
- **Engineered correlated-error data on quantum.** Test 2 needs Stim
  CORRELATED_ERROR circuits; that's a separate noise model and gets its
  own library bucket (`quantum_correlated_*`) when run.
- **Compression-Axiom cluster digests.** Test 5 needs operationalized
  cluster-digest streams per substrate; not in scope until that work
  starts.

## Production discipline

- **Resumable.** The grinder writes a manifest (`MANIFEST.json` at
  library root) tracking each task's status. Killing the script and
  re-running picks up where it left off.
- **Atomic writes.** Result files are written to `*.tmp` and renamed to
  the final name; manifests are written likewise. A killed mid-task
  cannot leave a corrupt JSON behind.
- **Per-task isolation.** A failure in one task is logged and the
  grinder continues; the manifest marks the task `failed` with a
  traceback. Nothing else is affected.
- **One file per cell.** Reading a single library cell is a single JSON
  load, no need to parse 10s of GB. Cross-substrate analysis loads
  N files from N independent paths.
- **No deletion.** The library is append-only. New substrate runs
  produce new files; superseded files stay until a deliberate cleanup
  pass.

## Producer

The script is at [`grind_library.py`](grind_library.py). One file,
single-process, depends only on stdlib + numpy + each substrate's
package being importable from disk. Run with:

```
python H:/mpa-central/library/grind_library.py            # full library
python H:/mpa-central/library/grind_library.py --smoke    # tiny sanity-check
python H:/mpa-central/library/grind_library.py --dry-run  # print task list + ETA
python H:/mpa-central/library/grind_library.py --substrate brain
```

## Where substrate primitives live (two homes by design)

Substrates split into two homes:

| Home | When to use | Discovery |
|---|---|---|
| **External H:\ repo** (`H:/mpa-brain/`, `H:/mpc-glass/`, `H:/mpc-quantum/`) | Non-trivial dependencies (C++ build, large vendored libs), accumulated per-repo discipline (CLAUDE.md, FOOTING.md, journey docs), or citable standalone artifact. | Explicit entry in `grind_library.py::SUBSTRATE_PATHS_EXTERNAL`. |
| **In-library primitive** (`primitives/<name>/`) | Thin adapter that reads a public dataset or runs a small in-process sim. No non-stdlib deps beyond numpy / a parser. No dev cycle separate from mpa-central. | **Auto-discovered.** Drop a subdirectory with `__init__.py` + `measurements.py`; the grinder picks it up. |

Both homes share the same `measurements.py` interface (`XDOT_KINDS`
tuple + `multi_window_fdr_iter(operating_point, xdot_kind, schedule,
*, rng_seed) -> Iterator[event]` per RULES §3). Output cells land in
`data/<substrate>/` regardless of home.

See [`primitives/README.md`](primitives/README.md) for the in-library
pattern (per-directory layout, promotion-to-own-repo criteria, worked
example outline).

**Adding a new external-repo substrate:** edit
`grind_library.py::SUBSTRATE_PATHS_EXTERNAL` and add the operating-
point axis + τ_env_analytic method to the per-substrate axes table
above.

**Adding a new in-library primitive:** create
`primitives/<name>/__init__.py` plus `measurements.py`, `data_loader.py`,
and `README.md`. The grinder's `discover_in_library_substrates()`
picks it up at next run. Add the operating-point axis +
τ_env_analytic method to the per-substrate axes table above
(documentation only — no grinder edit required).

## Consumers

After the library exists:

- **Re-do Test 1** by reading library files and computing ξ-rescaled
  walks across substrates. No substrate runs.
- **Cross-substrate visualizer panels** by joining brain, glass, quantum
  library files at matched (operating-point, ẋ-kind) and rendering.
- **Roadmap Tests 3, 4, 5 first cuts** as analysis-only against the
  existing library, with substrate-side extensions added incrementally.

## Versioning

This is library spec **version 1.0**. Schema changes happen by
incrementing the version field; old library files remain readable.
