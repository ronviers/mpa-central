# mpa-central

The cross-project coordination point for the MPA (Metastable Propositional
Algebra, v8) program. Not a parent project — siblings do not depend on it
at runtime. A *known place* where shared rules, the framework paper, and
the cross-substrate state index live.

## What's here

- **[`RULES.md`](RULES.md)** — concise implementation rules. Cross-substrate
  discipline only; substrate-specific findings live in each project's
  `docs/journey/FOOTING.md`. Rewrite-on-your-way-out: when a session locks
  a cross-substrate truth, edit `RULES.md` before signing off.
- **[`ONE_TRUE_TEST_ROADMAP.md`](ONE_TRUE_TEST_ROADMAP.md)** — five
  candidate one-true-tests for MPA (ξ=1 scale-relativity crossover;
  engineered k-frust on syndromes; hysteresis-gap-as-regime-invariant;
  c-s mentor lag asymmetry; Wall-cusp universality), ordered by
  evidential power vs implementation cost. Tracks what's compelling vs
  what's invalidating for each. With the library in place (below), Tests
  1, 3, 4, 5 reduce to library queries rather than new substrate runs.
- **[`library/`](library/)** — the **MPA characterized lightfield**: the
  long-term canonical record of the multi-window FDR observable
  across substrates, operating points, and ẋ choices. See
  [`library/LIBRARY_SPEC.md`](library/LIBRARY_SPEC.md) for the contract,
  [`library/grind_library.py`](library/grind_library.py) for the
  resumable producer. Sample times are **τ_env-anchored per operating
  point** (RULES rule 13) — the library concentrates compute where the
  substrate has structure to read, not on the post-aging r-asymptote.
- **[`pre_registered/`](pre_registered/)** — pre-registrations and
  findings for the roadmap's candidate tests. Pattern: write the
  prediction *before* touching the data so any agreement is honest;
  pair with a findings doc per substrate result. Currently holds Test 1
  (ξ=1 crossover) pre-registration and first-pass findings against
  pre-library data.
- *Rule-12 evidence script archived 2026-05-18 after the rule landed:
  [`archive/2026-05-05_rule-12-shipped/cross_substrate_plateau_summary.py`](archive/2026-05-05_rule-12-shipped/cross_substrate_plateau_summary.py).
  A future library-aware analogue would query `library/data/` directly.*
- **the foundational v9 framework document and the MPA protocols** now live in [`../mpa-atlas/`](../mpa-atlas/). v9 is at [`mpa-atlas/framework/`](../mpa-atlas/framework/); RFC-1 (spec object) and RFC-S (scale management) are at [`mpa-atlas/rfcs/`](../mpa-atlas/rfcs/); the architectural block-in is at [`mpa-atlas/architecture/`](../mpa-atlas/architecture/). mpa-atlas is now the sole source of truth for the framework document and the RFC sequence.
- **the authoring environment** (formerly "Substrate Synthesizer") moved to [`../mpa-character/`](../mpa-character/).

## What's *not* here, and where it is

- **Substrate state.** Each substrate owns its `docs/journey/FOOTING.md`
  (locked items), `docs/journey/MAPPINGS.md` (mapping ledger), and
  `docs/manual/09-discoveries.md` (free-form journal). See sibling index
  below.
- **Per-substrate-tab contracts** (visualizer↔substrate event shapes).
  Live in `H:\mpc-visualizer\docs\` because the visualizer is the
  consumer; substrates implement to the contract.

## Sibling index

The MPA constellation lives at `H:\mpc-*` (migrating to `H:\mpa-*`). None depends on the others
at runtime; shared physics is vendored with SHA pin (per substrate).

| Project | Role | Live state |
|---|---|---|
| [`mpa-atlas`](../mpa-atlas/) | Protocols + framework (v9, RFC sequence, architectural block-in). Sole source of v9 and RFC-1/RFC-S. | RFC-1 v0.1; RFC-S block-in |
| [`mpa-character`](../mpa-character/) | Authoring environment (formerly Substrate Synthesizer). Emits spec objects against mpa-atlas RFC-1. | pre-implementation |
| [`mpc-foundry`](../mpc-foundry/) | Industrial twin (foundry / thermal cell). Source of vendored kernel modules. | `HANDOFF.md` |
| [`mpc-brain`](../mpc-brain/) | Cognitive architecture. Langevin substrate; v8 Appendix A worked instance. | `docs/journey/FOOTING.md` |
| [`mpc-glass`](../mpc-glass/) | 3D EA Ising glass aging. ẋ rewrite landed `F-011` (2026-05-03); refined CK calibration owed (`P-006`). | `docs/journey/FOOTING.md` |
| [`mpc-quantum`](../mpc-quantum/) | Surface-code syndromes (Stim). v8 multi-window FDR primitive landed `F-018`. | `HANDOFF.md`, `docs/journey/FOOTING.md` |
| [`mpa-visualizer`](../mpa-visualizer/) | Cross-substrate renderer (active, 2026-05-05). Glass / quantum / brain-spectrum / cross 3-way tabs; ẋ-kind selectors per RULES rule 12; SAT tab owed (deferred). | `docs/handoff_next_session.md` |
| [`mpc-visualizer`](../mpc-visualizer/) | Predecessor of mpa-visualizer. Archived 2026-05-05; brain-substrate artifacts moved to mpa-brain, maze demo moved to mpc-brain/_archive. | `docs/archive/MIGRATED_TO_MPA_BRAIN.md` |
| [`mpc-profiles`](../mpc-profiles/) | Substrate calibration profile registry. | — |
| [`mpc-sat`](../mpc-sat/) | SAT proof traces. First real session landed 2026-05-03: F-002 substrate ẋ = WalkSAT variable-flip; streaming primitive built; smoke at α = 4.30 / N = 500 verified. Earned rule 11. | `HANDOFF.md` (post-first-session, 2026-05-03) |

## Cross-substrate state at a glance (2026-05-03)

The current sequence (operator framing) is a 7-step v8 dial-in (revised
2026-05-03 — mpc-sat first real session landed; visualizer SAT-tab
inserted at step 6 so each substrate immediately gets its consumer
counterpart):

1. **mpc-quantum** — v8 multi-window protocol + streaming primitive ✓ (F-018)
2. **mpc-visualizer** — quantum tab driver consuming the new primitive ✓ (rule 8 — kernel warmup — earned at landing)
3. **mpc-glass** — ẋ rewrite (F-011) + first v8 run + canonical CK calibration ✓ (calibration partial — refined run owed per glass `P-006`)
4. **mpc-visualizer** — glass tab update; cross-substrate side-by-side — *next*
5. **mpc-sat** — first real session ✓ (F-001, F-002 locked; streaming primitive built; smoke verified at α = 4.30; rule 11 — Boolean-limit trap is operational — earned). Owed: α-sweep + cavity-method calibration check (P-001, P-002).
6. **mpa-visualizer** — SAT tab integration: consume `mpc_sat_packs.measurements.multi_window_fdr_iter`. Contract at [`H:\mpc-visualizer\docs\sat_tab_event_protocol.md`](../mpc-visualizer/docs/sat_tab_event_protocol.md) (still in mpc-visualizer's docs as a visualizer-side contract; the consumer landing happens in mpa-visualizer).
7. **mpc-brain** — first v8 pass — verification + multi-window re-analysis


Each step is its own session. mpc-quantum's queue is in
[`H:\mpc-quantum\HANDOFF.md`](../mpc-quantum/HANDOFF.md) — the K-operator
extension, the CORRELATED_ERROR k-regime test, and pending P-items.
Other substrates' queues live in their own HANDOFF / FOOTING.

## Discipline

- **Substrate produces, library characterizes, visualizer consumes;
  mpa-central holds shared rules.** Four layers, one direction at each
  interface. Substrates emit raw observables under their primitive's
  contract; the library catalogues the characterized cells; the
  visualizer reads from the library; mpa-central holds the
  cross-substrate rules and the canonical theory. Code stays in
  substrate trees.
- **mpa-atlas is the sole source of the v9 framework document and the MPA protocols.** mpa-central holds the cross-substrate rules and operational artifacts (RULES, library, pre-registrations); the canonical theory and protocols live in [mpa-atlas](../mpa-atlas/).
- **The library is the long-term artifact.** Sweep_*.json files in each
  substrate's docs/results are dial-in records; the library at
  `library/data/` is the canonical produced characterization. New tests
  query the library; new substrate runs append to it.
- **Edit on your way out.** Don't let baggage accumulate here either.
