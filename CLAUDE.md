# mpa-central — session discipline

Stub. Established 2026-05-17 alongside the character test framework
integration. mpa-central is the program-wide reference repo:
SUITE_BLOCK_IN, METHODOLOGY, DEFERRED, RULES, and the substrate
library that everything downstream consumes.

## Authority documents

- [`SYSTEM_OVERVIEW.md`](SYSTEM_OVERVIEW.md) — **read first.** What
  MPA is, how the repos connect, end-to-end data flow from substrate
  physics to auditor verdict. Carries the per-repo reading order for
  new contributors and is the doc to point a confused future session
  at.
- [`SUITE_BLOCK_IN.md`](SUITE_BLOCK_IN.md) — structural commitment for
  the MPA suite (compute layer vs viewer layer). Upstream of every
  sibling repo's CLAUDE.md.
- [`METHODOLOGY.md`](METHODOLOGY.md) — what counts as MPA testing
  (four cuts: substrate / evidence / artifact / infrastructure scope).
- [`DEFERRED.md`](DEFERRED.md) — cross-repo parking lot. Not a ticket
  tracker; ambient deferred work. Sessions that land an item delete
  the entry.
- [`RULES.md`](RULES.md) — v8 MPA framework rules of the road.
- [`POSITION.md`](POSITION.md) — the program's Lakatosian stance.
  Pre-worked rebuttals to common attacks (data, methodology, AI
  collaboration, scope, neatness). Read when the legitimacy question
  comes up; not required for technical work.
- [`FALSIFICATION.md`](FALSIFICATION.md) — **the invalidation program's
  session entry point.** Living ledger: the positive-control ladder, the
  open invalidator attack fronts, and the standing finding that the
  1-param inversion can't recover FDT-violation X (so X-verdicts are read
  at the raw-slope layer). Operational complement to POSITION.md. Open it
  first when working on validation/falsification.

## Substrate library

- [`library/data/`](library/data/) — 60 grind cells across glass,
  quantum, brain. The empirical input to mpa-conform's curator path.
- [`library/grind_library.py`](library/grind_library.py) — the
  grinder that produces them.
- [`library/LIBRARY_SPEC.md`](library/LIBRARY_SPEC.md) — what a
  library cell is supposed to look like; cited by grinder.
- [`library/MANIFEST.json`](library/MANIFEST.json) — per-task status;
  the grinder reads/writes this on resume.

## Character test suite — library-input contract

The substrate library is the **empirical input** to the character
test framework owned by mpa-conform. Canonical doc:
[`H:/mpa-conform/conformer/tests/character/README.md`](../mpa-conform/conformer/tests/character/README.md).

Character tests use `library/data/<class>/*.json` cells as the
substrate measurements that get rendered into shots. The grind
cell's per-sample-time `all_samples[]` carries the temporal
structure the shot animates.

**Library refresh + grinder updates must re-pass character tests.**
Per [`DEFERRED.md`](DEFERRED.md): the library is overdue for a
refresh (unnormalized quantum chi, zero-filled brain C/χ, null
glass tau_env below Tc). When that refresh ships:
- Delete `library/data/` and `library/MANIFEST.json`, bump
  `LIBRARY_SPEC_VERSION` in the grinder, re-grind.
- Run `python -m conformer.cli test-character` from
  `H:/mpa-conform` and watch the dailies in DJV
  (`C:\Program Files\DJV 3.4.2\bin\djv.exe`).
- The character must round-trip: the library refresh should make
  the shots *more* faithful, not change the substrate's identity.

Grind output is the test input. Test failures here surface as
"the substrate's character changed" in the shot — diagnose
upstream (in this repo's grinder) before chasing it downstream in
mpa-conform.


## Rendering discipline — the water MPA swims in

Canonical doc:
[`H:/mpa-conform/conformer/shot/RENDERING_DISCIPLINE.md`](../mpa-conform/conformer/shot/RENDERING_DISCIPLINE.md).
Established 2026-05-17. Every visual property in every shot maps to
framework data; differentiation, not decoration. The discipline is not
a feature -- it is the medium every visualization in the MPA suite
operates in, and it does not get re-litigated per session.

This repo's contribution to shot rendering is whatever its
character-test contract above already names. Any addition that would
violate the two rules (every property maps to data; differentiation
not decoration) does not land; the discipline does not bend.
