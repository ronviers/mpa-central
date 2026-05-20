# Deferred — cross-repo parking lot

Dated entries of work that's deliberately deferred — *not* a ticket tracker.
One short paragraph each. Grouped by where the work lives. Sorted newest-first
within each group.

When a session lands one of these, delete the entry (don't mark "done" —
this file decays naturally as work moves through it).

When in doubt where something belongs: per-repo `ROADMAP.md` for sequenced
session-shaped work; this file for ambient items that don't fit a roadmap
cleanly yet.

---

## mpa-central

### Library data + grind_library.py refresh for RFC-S / conform / solver / auditor process *(flagged 2026-05-16)*

`H:/mpa-central/library/data/{glass,quantum,brain}/*.json` is stale —
predates the RFC-S scale-management framework, the curator path, the
scale-solver, and the v0.2 bundle audit_delta. Specifically: quantum
cells emit unnormalized `chi` (range [4, 12]); brain cells emit
identically-zero `C` and `chi`; glass cells have `tau_env_analytic =
null` below Tc (aging-unbounded) without a substrate-default fallback.
Companion `library/grind_library.py` needs corresponding updates so
re-grinds emit data compatible with the new pipeline (Onsager-normalized
observables, RFC-S-aware `tau_obs` window selection, populated brain
substrate).

The v0.2 audit surfaces these issues honestly — every quantum bundle
shows `in_gamut: false`, every brain bundle shows `locus_residual >> 1`.
Fixing the library + grind makes the audit signal meaningful instead of
"library is wrong" noise.

This is a foundational refresh of the seed corpus, not a curator bug.
Probably a multi-session arc: (a) extend LIBRARY_SPEC for the new
normalization/conventions, (b) update grind_library.py, (c) re-grind
the 60 cells, (d) re-run mpa-conform walk_library + verify audit_delta
sanity. Auditor-side update follows from the conform output.

---

## mpa-conform

### 5-vector inversion (X-recovery fitter) — demonstrated-owed *(flagged 2026-05-19)*

`conformer.compute.gfdr_model.generate_kww_glass_locus` exists as a
*generator* of the substrate-thermodynamic 5-vector (q_EA, τ_α, β_KWW,
τ_β, X), but the *fitter* that recovers those from a cell does not — the
production inversion (`inversion.invert`) only fits the 1-param chit. The
`two_temp_ou` positive control (known prescribed X) demonstrated and
quantified the gap: a dialed-in X=0.5 is read back by the 1-param
inversion as effective ~0.95, X=0.1 as ~0.92, because the 1-param cdv1
family couples C-shape to χ-slope and can't represent r-like-C +
reduced-χ-slope. Consequence: the production pipeline currently cannot
recover FDT-violation X on *any* substrate (glass/quantum/brain
included). Interim policy: X read at the raw FDR-locus-slope layer
(faithful — recovers X to ~2%). **BLOCKED-IN 2026-05-19**: first-cut
scaffold `conformer/compute/five_vector.py::fit_kww5` exists and recovers
X on two_temp_ou to ~1–2% (residual ~0.02 vs 1-param 0.25). Design +
punch list:
[`H:/mpa-conform/docs/five_vector_inversion_blockin.md`](../mpa-conform/docs/five_vector_inversion_blockin.md).
What's left: build `kww_oracle` (full identifiability), seeding/T
handling, integrate into `invert()` + bundle schema, and the residual
domain gate (closes FALSIFICATION.md FINDING 2). See FALSIFICATION.md
"KEY FINDING" + "Owed work".

---

## (other repos — add sections as items appear)
