# MPA testing — thin methodology

Cross-program discipline for what counts as MPA testing. Substrate-neutral, framework-aware, repo-agnostic. Peer to [`RULES.md`](RULES.md) (which handles substrate-implementation discipline) and to the [`mpa-atlas`](https://github.com/ronviers/mpa-atlas) RFCs (which handle protocol contracts).

**Authoritative sources cited.** Framework predictions: [`mpa-atlas/framework/cdv1_compressed.md`](https://github.com/ronviers/mpa-atlas/blob/main/framework/cdv1_compressed.md) (cross-substrate testing surface), [`mpa-atlas/framework/v9_compressed.md`](https://github.com/ronviers/mpa-atlas/blob/main/framework/v9_compressed.md) + [`character_compressed.md`](https://github.com/ronviers/mpa-atlas/blob/main/framework/character_compressed.md) (operational source of truth post-v8). Characterized cross-substrate evidence: [`H:/mpa-central/library/`](H:/mpa-central/library/LIBRARY_SPEC.md) (sealed lightfield, schema frozen at LIBRARY_SPEC v1.0).

## RFC stack — what each governs

The [`mpa-atlas/rfcs/`](https://github.com/ronviers/mpa-atlas/tree/main/rfcs) stack defines protocol contracts. Each RFC governs a specific surface the cuts apply at; the cuts cite the RFCs, the cuts do not duplicate them.

| RFC | Surface it governs | Used by cut |
|---|---|---|
| [RFC-1 Spec-Object](https://github.com/ronviers/mpa-atlas/blob/main/rfcs/MPA-RFC-1_Spec-Object.md) | Test-result artifact shape; emitted JSON conformance | Cut 2 (output shape) |
| [RFC-2 FDR-Signatures](https://github.com/ronviers/mpa-atlas/blob/main/rfcs/MPA-RFC-2_FDR-Signatures.md) | What an FDR / gFDR signature must satisfy to count | Cut 2 (predictive-ness of signature claims) |
| [RFC-3 Consistency-Completeness](https://github.com/ronviers/mpa-atlas/blob/main/rfcs/MPA-RFC-3_Consistency-Completeness.md) | Stack-internal consistency rules | Cut 4 (validator role) |
| [RFC-RI Realizer-Interface](https://github.com/ronviers/mpa-atlas/blob/main/rfcs/MPA-RFC-RI_Realizer-Interface.md) | How a substrate-class connects to the framework | Cut 1 (substrate-scope inclusion) |
| [RFC-S Scale-Management](https://github.com/ronviers/mpa-atlas/blob/main/rfcs/MPA-RFC-S_Scale-Management.md) §4 | Driver-profile shape, gamut, intents | Cut 1 (substrate-class declarations) |
| [RFC-C Calibration](https://github.com/ronviers/mpa-atlas/blob/main/rfcs/MPA-RFC-C-Calibration.md) §2 | Calibration-record shape, seals, retirement triggers | Cut 2 clause (b) |
| [RFC-V Reference-Vocabulary](https://github.com/ronviers/mpa-atlas/blob/main/rfcs/MPA-RFC-V_Reference-Vocabulary.md) | Term pins across substrates and verdict strings | Cuts 1–4 (vocabulary consistency at point-of-use) |

A finding that satisfied a cut against an outdated RFC version still satisfies the cut at the time of writing; bump the RFC version, re-run only the affected cuts at the next sweep (per §Sunset triggers).

---

Four cuts. Apply at point-of-use. Anything failing a cut is flagged in place; flagged items sunset on the next reset trigger. No inventory passes, no per-item deliberation, no policing.

---

## Cut 1 — Substrate scope

A substrate is in scope iff cdv1 currently makes a falsifiable prediction about it that has not been recorded as OUT_OF_SCOPE on dynamical-order, mode-separation, or substrate-class grounds. Substrates that fall outside cdv1's prediction surface do not get test apparatus built around them — they get an OUT_OF_SCOPE entry in their driver profile and stop consuming session time.

## Cut 2 — Evidence scope

A finding is predictive iff it is either:

- **(a) pre-registered** against a falsifier before run (per RFC-2 signature contract), OR
- **(b) derived from an RFC-C calibration record** validating against an RFC-S §4 driver profile, OR
- **(c) computed from sealed library cells** in [`H:/mpa-central/library/`](H:/mpa-central/library/LIBRARY_SPEC.md), whose schema froze at LIBRARY_SPEC v1.0 and whose substrate-side production is sealed in `MANIFEST.json`.

Findings that satisfy none are exploration: they may have taught us something but they do not predict the future. Records existing is a feature; absence of records means the finding does not yet count, not that the methodology bends.

Clause (c) admits library cells as evidence because the substrate side froze the deliverable (per-window `C_d`, `chi_d`, `d_norm`, `sigma_d`, `f`) before any consumer test ran. That is the substrate-side analog of pre-registration: the lightfield is what it is regardless of the question asked of it.

## Cut 3 — Artifact scope

An artifact is load-bearing iff at least one currently-active substrate scope (Cut 1) or finding scope (Cut 2) references it. Driver profiles, kernel modules, experiment scripts, calibration records, datasets — all classified by reference, not by intrinsic merit. Orphans sunset.

## Cut 4 — Infrastructure scope

A repo, package, or script is necessary iff it carries one of five roles:

- **framework** — cdv1, v9, character, RFCs, schemas (`mpa-atlas`, `mpa-central`)
- **library** — substrate measurements at any characterization level: raw deposits *and* the characterized lightfield at [`H:/mpa-central/library/`](H:/mpa-central/library/LIBRARY_SPEC.md)
- **test apparatus** — drivers, experiments, calibration records, batchers (`mpa-relaxation`, `mpa-engine`, `mpa-brain`)
- **viewer** — canonical-reading display, operator-training surface, consumer-side renderers; consumes library cells or substrate streaming primitives, never writes back ([`mpa-view`](https://github.com/ronviers/mpa-view), [`mpa-visualizer`](https://github.com/ronviers/mpa-visualizer), future calibration-stepper UIs)
- **validator** — round-trip discipline per RFC-3 + RFC-S §5

Anything else is exploration. The repo population is allowed to shrink as exploration reveals what survives.

---

## Sunset

Items failing a cut: marked at point-of-use with a one-line `methodology-flag:` annotation in the artifact itself or in its containing index. Archived to `<repo>/archive/<reset-trigger>/<original-relative-path>` at the next reset trigger:

- cdv1 amendment (framework prediction surface changes),
- RFC version bump (protocol contract changes),
- substrate-class addition or retirement,
- scheduled program-level sweep.

No per-item deliberation at sunset. Flagged-and-still-flagged → archive. Items rescued before the trigger (by satisfying the cut they failed) lose the flag silently.

## Self-amendment

This document is allowed to grow only if a cut fails to decide a real case AND the failure repeats. Single-case ambiguity is resolved at point-of-use, not by adding methodology prose. Resist forces that push toward thicker methodology — that is RFC-thickness in a different shirt. ICC v4 was 120 pages because it was forced to be; we are not.

---

## Application surface

The methodology is applied (not duplicated) at three integration points:

- **Per-repo `CLAUDE.md`** cites this document as the source of truth for what counts as in-scope work in that repo.
- **`FOOTING.md`** entries (substrate findings) include a Cut-2 line declaring which clause makes them predictive — pre-registration reference, calibration record reference, or `methodology-flag: not-predictive` if neither.
- **Driver profiles** include a Cut-1 line declaring substrate-class scope and any OUT_OF_SCOPE recordings.

These integration points carry the methodology operationally. The document itself does not need to be re-read on every session — the cuts are short enough to remember.

---

**Versioning.** v0.3 — Cut 4 adds **viewer** as a fifth role (closes orphaning of mpa-view + mpa-visualizer; consumer-side renderers were unrepresented in v0.2's four-role list). v0.2 — Cut 2 gains clause (c) for mpa-central library cells; Cut 4 "library" clarified to include characterized lightfield; RFC stack roles named explicitly. v0.1 — initial. Bump only on cut-text changes. Authority: program-wide; supersedes per-repo improvisations on the same questions.
