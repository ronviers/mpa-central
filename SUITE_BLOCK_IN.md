# MPA Suite — block-in

**2026-05-15. Program-wide structural commitment.** Supersedes any earlier
claim, implicit or explicit, that any single component is "the user-facing
tool". MPA is a **suite** of components in three layers, coordinated by a
small artifact bus.

This file is read-only authority on what lives where. Per-repo `CLAUDE.md`
pointers in. Sequencing / migration plans live in per-repo `ROADMAP.md`,
not here.

---

## Three layers

**Spec layer.**
- `mpa-atlas` — framework spec authority (cdv1, v9, RFC-S, schemas,
  contracts). Read-only by everything downstream.

**Compute layer** — Python / Rust / WASM; LLM- and MCP-using where it
earns its weight.
- `mpa-solver` — forward physics kernel (ODE integration, ensemble,
  correlator math). WASM-built; vendored downstream.
- `mpa-scale-solver` — scale-management kernel: τ_obs projection +
  canonical-frame operations (`apply_translation`, `forward_sweep_invert`,
  `tau_obs_sweep`, `regime_at`, `gamut_classify`, `intent_map`,
  `validate_driver_profile`) plus continuous `flow(canonical_initial, nu,
  field)` in Markovian scope. Python v1.0.0 shipped 2026-05-16
  ([ronviers/mpa-scale-solver](https://github.com/ronviers/mpa-scale-solver)
  @ v1.0.0). Two translation-field shapes (lookup_table v0, tangent_flow
  v1); `BanachSubstrate` calibration reference; inverse-lookup-table
  sidecar dispatch; per-call validation + provenance via seven `*_wrapped`
  variants. Production through v5 in Python; native port at v6 (per-seed
  reproducible against the v5 Python). Sibling to `mpa-solver`, not
  nested under it. Consumed by `mpa-conform`.
- `mpa-conform` — compute hub. Owns: data prep (curator + researcher
  paths); forward physics (vendors solver); inversion fit (delegates to
  `mpa-scale-solver` for canonical-frame inversion); audit
  classification; framework-grid generation. **Produces every artifact
  the viewer layer reads.**
- `mpa-central` — library cells, methodology, cross-program rules
  (this file lives here).

**Viewer layer** — browser-based, pure-static, offline-after-download.
- `mpa-auditor` — predicted-vs-empirical delta viewer.
- `mpa-view` — substrate lightfield viewer (Python server-backed, peer).
- Future viewers as use cases grow past a tab.

---

## The artifact bus

| Artifact | Producer | Consumers | Schema home |
|---|---|---|---|
| `framework-grid.v0.X.json` | mpa-conform | every viewer | mpa-conform/schema (new at v0.2) |
| `declaration_bundle.json` | mpa-conform | every viewer that needs empirical data | mpa-conform/schema |
| `driver-profile.v0.X.json` | mpa-conform | viewers needing translation-field lookups | mpa-atlas/schema |

The bundle is THE input to a viewer. **Singular working-space path** —
not CSVs + bundles + live data; just bundles.

---

## What the viewer layer does NOT do

- No runtime LLM, no MCP, no network.
- No live forward physics. No live inversion. No live audit classification.
- **No "engines" in the original sense.** A viewer holds: bus, layout,
  styles, renderers, bundle/grid loader. Nothing computes.

If a viewer needs to compute, it's not a viewer — it's drifting into
the compute layer. Reset and move the work to mpa-conform.

---

## Per-component scope

### `mpa-auditor` — what's correct, what's drift

**Correct (keep):** conductor, style manager, layout manager, renderers,
contracts (as artifact shape spec), corpus manifests, styles, index.html.

**Drift to retire:**
- `engines/audit-engine.js`, `engines/inversion-engine.js`,
  `engines/character-engine.js`, `engines/discrete-engine.js`,
  `engines/data-engine.js`
- `math/solver-service.js`, `math/ensemble-locus.js`, `math/gfdr-model.js`,
  `math/phase-locking-model.js`, `math/debounce.js`
- `vendor/mpa-solver/`
- Explore mode in its live-dial-ODE form

**Drift to add:** `engines/bundle-loader.js`, `engines/grid-interpolator.js`
(or fold into one `core/data.js`). Data routers, not compute.

The "M-Inversion proper", "M-Corpus", "Audit Library" trajectories in
the current ROADMAP get rehomed: the corpus is a conform-produced
artifact; the Audit Library is a viewer reading the corpus.

### `mpa-conform` — scope expansion ahead

**v0.2 (2026-05-16, landed):** bundles carry empirical observable +
full curator-time inversion fit + predicted_locus + audit_delta +
mpa-scale-solver v1.0.0 stamps (regime_at, gamut_classify) +
version_context. Schema:
`schema/declaration-bundle.v0.2.json`. Inversion fit ported in Phase 1
(2026-05-15); v0.2 wires it into walk_library and tightens
`fit_provenance` to required-shape. Substrate-conditional tau rescaling
applied internally to the fit; bundle's `observable.data` stays
native-frame.

Forward (v0.3+):
- Fit-quality session: address library upstream issues v0.2 audit_delta
  surfaced (quantum chi normalization, brain C/chi zero-fill, glass
  tau_env null fallback).
- Vendor mpa-solver Python bindings (build requires MSVC; conform's
  local `observables.py` / `gfdr_model.py` become thin shims over
  `import mpa_solver`).
- Port audit classification (four-category classifier from auditor).
- New artifact: `framework-grid.v0.1.json` (precomputed manifold over
  chit × γ_AB).
- Researcher path: same compute pipeline, LLM-driven declaration
  upstream.
- v0.3+: `observable.canonical_data` as load-bearing field — re-opens
  when scale-solver v2 lands curve-level operations (per
  `mpa-conform/docs/foundational-questions.md`
  §Q-scale-management-as-compute-scaffolding scope-split note).

---

## Discipline

**Peel, not scrape.** When a component grows past its layer, the work
that doesn't belong gets carved out, not assimilated. We have to keep
doing this.

**Thin at the seams.** The bundle and grid schemas are load-bearing;
everything else lives behind them. Schema bumps are deliberate.

**One repo, one job.** If a component does two distinct jobs, split it.

**Discard early when the discipline tells you to.** The auditor-as-
instrument was a defensible early bet; the suite-with-thin-viewers is
the correct steady state. The cost of switching is real; the cost of
not switching is unbounded.

---

## Sequencing

Lives in per-repo `ROADMAP.md`. This file declares the destination;
each repo plans its own path.

The migration is deliberate, not heroic. No single rewrite. Each
session moves one piece of the load from the auditor's compute footprint
to mpa-conform's, and the seams stay clean as it goes.
