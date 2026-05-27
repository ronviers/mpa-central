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

### Homochirality as a §846 / central-commitment candidate — evaluate, don't chase *(flagged 2026-05-22)*

Ron's idea: biological homochirality (life's L-amino-acid / D-sugar handedness)
as the topologically-protected direction = the chimeric sign of a Harary triad;
"the triad is the minimal origin story of a bit/chit." **Sharp keeper version:**
a topologically-*protected* bit = the chirality (circulation handedness) of a
△_H — the bit IS the handedness, and 2 modes can't protect it (gauge-removable),
so N=3 is minimal. This is the Central commitment read as bit-genesis; ties the
bit (Boolean D→∞ limit) to the triad-deformation spine. **Stress-test (the
brake):** don't let the word "chirality" do the work (same trap as "frustration"
with SQUIDs). Two different chiralities — Harary = *dynamical circulation*
handedness (𝒜=∮v/D≠0, a sustained NESS current); homochirality = *static
molecular parity*, and the standard Frank model (2-species autocatalysis + mutual
inhibition) is a **bistable fixed point**, not a circulation — the
SQUID-equilibrium-trap kind that FAILS §846. The version that could be a real
△_H: a ≥3-species **cyclic non-reciprocal catalytic network** (hypercycle /
cyclic-LV chemistry) whose chirality rides a sustained circulating catalytic
current; the static molecular handedness is then the frozen bit it wrote.
**Discriminator:** complex Jacobian + 𝒜≠0 + ⟨σ⟩>0 + needs ≥3 cyclic species
(gauge-irremovable) vs real-Jacobian 2-species bistability. Also distinct from the
electroweak parity-violation-bias origin story (NOT the triad story).

**Ron's sharpening (2026-05-22): maintenance, not origin.** Prediction — it is NOT
the historical "chemistry that wrote it" but an *extant, actively-maintaining*
Harary triad ("a little tiny one whose chimeric sign is stuck in one state") that
keeps all life one-handed. This is stronger and more falsifiable: (a) extant →
measurable in living cells *now*, killing the prebiotic-time-series data problem
I'd raised; (b) explains *universality + maintenance*, not just the one-time break.
Key upgrade: **protected ≠ bistable.** A Frank fixed point / frozen accident is
"stuck until kicked hard enough"; a topology-protected triad is "stuck because no
continuous deformation removes it — only rewiring." 4 Gyr with zero exceptions is
macroscopic evidence for protection over bistability. MPA-native reading:
homochirality is a textbook **coherence** maintained against natural dissolution
(racemization) by a continuous **holding** (ATP-driven chiral proofreading, e.g.
DTD / D-aminoacyl-tRNA deacylase editing); the maintenance triad is its k_frust
core, the protected chimeric sign **is** the bit, cut the holding → racemization →
r-collapse. Threads the affinity-vs-magnitude needle: "chimeric sign stuck" = the
gauge-irremovable *sign-topological* face (which hand, drive-independent); the
maintenance *rate* flows with metabolic drive — exactly the k_frust-drain
affinity(topological)/magnitude(drive) split. **Falsification test:** find the
chiral-maintenance coupling graph; is there a Harary-frustrated 3-cycle
(odd-negative, non-reciprocal, complex Jacobian, 𝒜≠0, ⟨σ⟩>0, gauge-irremovable
sign) — vs a 2-component bistable / simple drive-forced (gauge-removable) cycle? If
the latter, homochirality is a deep well, not protection. **Open literature step:**
name the actual triad (candidate: chiral kinetic-proofreading / DTD editing cycle);
not yet done.

**Probe-placement precision (Ron's "place your probe here or MPA is invalid").** This
is a NEW staked falsifier *beyond* the central commitment: the commitment says
protected-circulation⟹triad; here MPA claims homochirality-maintenance *specifically
IS* triad-protected circulation — bolder exposure, more teeth. Precision MPA can
honestly give: HIGH on the *signature* (complex-conjugate Jacobian pair, 𝒜=∮v/D≠0,
broken detailed balance, gauge-irremovable + drive-independent sign, ≥3-node frustrated
core); HIGH on the *kill conditions*; MEDIUM on *subsystem* (the anti-racemization
maintenance network); **LOW on exact molecular identity of the 3 nodes — MPA imports
biochemistry, doesn't derive it; it hands a template to match, not the molecules.**
Sharpest single falsifier = the **drive-sweep:** starve metabolic drive (ATP/GTP) — the
current *magnitude* must collapse toward racemic (r) while the *sign* (hand) stays flat;
if the hand flips, the sign was drive-set not topology-protected → MPA dead. Verify-null
discipline: precise placement makes the null interpretable (fatal if fail / credit if
survive); a vague probe gives a mushy result — so nail placement before staking. If it holds this becomes a *better* §846 candidate than the active
lattices — extant, universal, ancient, data-accessible, and the MPA setting
incarnate. Park; evaluate after the compression fork. See memory
`project_harary_triad_substrate_data`.

---

## mpa-conform

### 5-vector inversion (X-recovery fitter) — LANDED; only production-glass X still owed *(landed 2026-05-25)*

The fitter `conformer/compute/five_vector.py::fit_kww5` LANDED in mpa-conform
(2026-05-25): it recovers FDT-violation X (≤~6% across X=0.1–1.0), round-trips the
full 5-vector (q_EA, τ_α, β_KWW, τ_β) on `kww_oracle`, carries a residual + per-channel
S/N **domain gate** (closes FALSIFICATION.md FINDING 2) and a bootstrap **identifiability**
flag orthogonal to it, is integrated into `inversion.invert` + the CLI bundle (additive,
no schema bump), and ships a result-image library at `docs/five_vector_views/`. This
retires the "production cannot recover X on any substrate" gap for every substrate whose
C is in the KWW-FDT family; out-of-family inputs are gated OUT rather than handed a garbage
X. See [`H:/mpa-conform/docs/five_vector_inversion_blockin.md`](../mpa-conform/docs/five_vector_inversion_blockin.md).

**Still owed (an mpa-central library task, the reason this entry isn't deleted):** production
**aging-glass X** below Tc cannot be validated because the library's glass cells have null
`tau_env` below Tc (camera-scale not placed — the substrate-inversion finding). Recover this
when the library refresh places the glass camera-scale; then run `fit_kww5` on the refreshed
glass cells and confirm X<1 (aging). Until then X for sub-Tc glass stays read at the raw
FDR-locus-slope layer (FALSIFICATION.md standing finding).

### conform→viewer design deferrals — researcher dials *(flagged 2026-05-25)*

mpa-conform's block-in surfaced that some interpretive choices ("which curve is
healthiest?") are researcher **utility-lens / dial** decisions, not conform
computations — they belong to the inert auditor viewport (present + expose, never
infer/correct). The growing pickup-list for the auditor pivot lives at
[`H:/mpa-conform/docs/deferred-for-auditor.md`](../mpa-conform/docs/deferred-for-auditor.md):
the present/expose/lag principle, the freeze-can't-compute **detector** (a verdict the
freeze can't compute is the tell it's a dial, not conform's call), and a two-tier
watch-list/entry discipline (entries born only from organic surfacing). Entry 1 = the
utility-lens over a band, surfaced by `laser_ro_pump_sweep_v2` (2026-05-25). Park until
the auditor pivot.

---

## (other repos — add sections as items appear)
