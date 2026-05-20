# PSP-Draft-00
## Persistence Specification Protocol
**Designator:** `psp-draft-00`
**Status:** Research draft. Schema and vocabulary subject to revision between drafts.
**Upstream:** Substrate Synthesizer specification document; MPA v8.
**Downstream:** Realizer search across substrate classes.
PSP defines an interchange format for persistence profiles: typed claims about which objects in a Substrate Synthesizer specification must survive coarse-graining, at what contraction cost, under what observation window, and with what failure modes. A profile is the document a realizer search consumes. Conformant tools issue and read profiles in this format.
---
## Conventions
Normative language (MUST, SHOULD, MAY) follows RFC 2119 / RFC 8174 and applies to schema and interchange behavior.
Throughout: *spec* is a Substrate Synthesizer specification document; *realizer* is a downstream substrate-search process; *object* is a typed element of the spec graph (vertex, edge, subgraph, composite); *ascent* is one application of the coarse-graining contraction $\mathcal{C}$ in the meta-ledger tower; *signature* is a measurable response shape attached to an object type; *event* is a typed protocol outcome reported during compilation or realization.
The shorthand $\Phi^\*$, $\kappa$, $\tau_{obs}$, $\gamma_{AB}$, $k_{\text{frust}}$, $\mathcal{M}_2$, $\epsilon$ refers to MPA v8 quantities. The schema treats them as opaque names; realizers ground them numerically when the substrate class binds.
---
## 1. Scope
PSP-Draft-00 specifies:
- Persistence profile schema (§2)
- Signature vocabulary (§3)
- Failure events (§4)
- Coarse-graining checkpoints (§5)
- Conformance levels (§6)
Items deferred to future drafts are listed in §7.
---
## 2. Persistence Profile Schema
### 2.1 Top-level structure

```persistence-profile := profile-header
                       object-record+
                       checkpoint-record*
                       signature-binding*
                       failure-binding*
                       open-marker*
```
### 2.2 Profile header
```
profile-header := {
    schema:        "psp-draft-00"           # MUST match this draft's designator
    spec-id:       <opaque-string>           # MUST be unique within the issuing source
    spec-version:  <semver or opaque>        # MUST be present
    mpa-version:   <reference>               # SHOULD identify the upstream theoretical version
    issuer:        <identifier>              # SHOULD identify the synthesizer instance
    created:       <iso-8601>                # MUST be present
    conformance:   <profile-id>              # see §6
}
```
### 2.3 Object record
Every object carrying a persistence claim appears as an `object-record`. Objects without persistence claims may be omitted from the profile.
```
object-record := {
    object-id:     <opaque-string>
    object-type:   vertex | edge | subgraph | composite | other:<label>
    target:        <type-specific target>           # §2.3.1
    survival:      <survival-block>                 # §2.3.2 — REQUIRED
    contraction:   <contraction-block>              # §2.3.3 — REQUIRED
    deformation:   <deformation-block>              # §2.3.4 — OPTIONAL
    window:        <window-block>                   # §2.3.5 — REQUIRED
    failure-bindings: [<event-id : action> ...]     # §2.3.6 — OPTIONAL
}
```
#### 2.3.1 Type-specific target
| object-type | target fields |
|---|---|
| vertex     | `target-regime` ∈ {c, s, r}; `lambda-band` (optional) |
| edge       | `gamma-sign` ∈ {negative, ≈zero, positive}; `gamma-magnitude` (optional) |
| subgraph   | `frustration` ∈ {prescribed-k, frustration-free}; `topology` (optional) |
| composite  | `composite-name` (e.g. "hebbian", "mentor", "lotka-volterra", "kuramoto-entrainment"); `module-fingerprint` (free-form) |
| other      | implementation-defined; MUST carry a `label` |
Composite names are opaque tags. The catalogue is not protocolized in this draft.
#### 2.3.2 Survival block
```
survival := {
    criterion:        <invariant-id>           # vocabulary §3 or local extension
    minimum-ascents:  <non-negative integer>
    survival-level:   structural | shadow | regime-only | regime-and-edge | full
    notes:            <free-form>               # OPTIONAL
}
```
`survival-level` semantics:
- **structural** — the object's typed identity must survive the named number of ascents
- **shadow** — only the $\mathcal{M}_2$ shadow must survive; intermediate-scale regime drift to $s$ is permitted
- **regime-only** — vertex regime must survive; edges may restructure
- **regime-and-edge** — vertex regime and incident edge signs must survive
- **full** — all declared fields must persist
Implementations MAY emit `level: extension:<label>` and document the extension via `open-marker` (§6.2).
#### 2.3.3 Contraction block
```
contraction := {
    epsilon-max:    <float in [0,1)>            # bound on ||C||_op per ascent
    norm:           operator | spectral | other:<label>
    profile:        uniform | per-ascent-list:[<float>...]
    confidence:     declared | measured-at-source | unverified
}
```
`confidence` advises the realizer on the source of the bound. The protocol does not specify validation procedure.
#### 2.3.4 Deformation block
```
deformation := {
    admissible:                    [<deformation-class-id>...]
    forbidden:                     [<deformation-class-id>...]
    associator-drift-bound:        <numeric or symbolic>
    distributivity-drift-bound:    <numeric or symbolic>
    shear-tolerance:               <numeric or symbolic>
}
```
Drift bounds reference the upstream deformation calculus by name; their numeric interpretation is fixed by the `mpa-version` declared in the header.
#### 2.3.5 Window block
```
window := {
    tau-obs:        [<tau-min>, <tau-max>]      # observer kernel band
    three-times: {
        clock:      <band or "any">              # trail-evolution timescales
        lambda:     <band or "any">              # stability timescales
        rg:         <ascent-range, e.g. [0, n]>
    }
}
```
`tau-obs` is dimensionless at the spec layer and acquires units when the realizer class binds. Realizers MAY collapse three-times axes when the substrate makes them coincident.
#### 2.3.6 Failure bindings
```
failure-bindings := [
    { event: <event-id>, action: reject | warn | record | substitute:<id> | escalate }
    ...
]
```
Default action when no binding is present: `record`. Realizers MUST honor `reject`. Other actions are advisory.
### 2.4 Example
```
{
    "schema": "psp-draft-00",
    "spec-id": "ex/hebbian-pair-001",
    "spec-version": "0.1.0",
    "mpa-version": "v8",
    "issuer": "synth/local-test",
    "created": "2026-05-06T12:00:00Z",
    "conformance": "core-minimal",
    "objects": [
        {
            "object-id": "v.A",
            "object-type": "vertex",
            "target": { "target-regime": "c" },
            "survival": {
                "criterion": "regime-stability",
                "minimum-ascents": 2,
                "survival-level": "regime-only"
            },
            "contraction": {
                "epsilon-max": 0.6,
                "norm": "operator",
                "profile": "uniform",
                "confidence": "declared"
            },
            "window": {
                "tau-obs": ["short", "mid"],
                "three-times": { "clock": "any", "lambda": "any", "rg": [0, 2] }
            }
        },
        {
            "object-id": "e.AB",
            "object-type": "edge",
            "target": { "gamma-sign": "negative" },
            "survival": {
                "criterion": "edge-sign-preservation",
                "minimum-ascents": 1,
                "survival-level": "regime-and-edge"
            },
            "contraction": { "epsilon-max": 0.7, "norm": "operator",
                             "profile": "uniform", "confidence": "declared" },
            "window": { "tau-obs": ["short", "mid"],
                        "three-times": { "clock": "any", "lambda": "any", "rg": [0, 1] } }
        }
    ]
}
```
A Hebbian-style $c$–$c$ pair under cooperative shear: both vertices survive 2 ascents at the regime level; the cooperative edge sign survives 1 ascent.
---
## 3. Signature Vocabulary
A signature is a measurable response shape attached to an object type. Signatures are referenced from `survival.criterion`, from profile-level `signature-binding` records, and from realizer validation reports.
### 3.1 Status tiers
| Tier | Meaning |
|---|---|
| **early-stable** | Stable name and definition; safe to reference |
| **candidate**    | Name stable; definition may shift; profiles SHOULD record assumed parameters in-band |
| **experimental** | Reserved name; semantics underspecified |
### 3.2 Vocabulary
#### `fdt-unit-slope` — early-stable
- **Object association:** vertex regime $r$
- **Observable:** parametric plot $\chi(\tau)$ vs $C(0) - C(\tau)$
- **Required shape:** unit slope
- **Falsification:** measured slope departs from unity beyond declared tolerance over the object's window
#### `fdt-suppressed-locus` — early-stable
- **Object association:** vertex regime $c$
- **Observable:** as above
- **Required shape:** $X \ll 1$; suppressed response; narrow, near-horizontal locus
- **Falsification:** locus opens; slope rises toward unity; or response amplitude crosses declared threshold
#### `fdt-aging-diagonal` — early-stable
- **Object association:** vertex regime $s$
- **Observable:** as above, with explicit age dependence
- **Required shape:** aging diagonal with plateau structure at long times
- **Falsification:** absence of age dependence; collapse to unit slope; collapse to suppressed locus
#### `fdr-negative-transient` — early-stable
- **Object association:** subgraph with prescribed $k_{\text{frust}}$
- **Observable:** loop-level response under coordinated perturbation
- **Required shape:** transient negative response window at loop scale
- **Falsification:** absence of negative transient over declared window; or appearance at vertex/edge level rather than loop level
#### `fdt-slope-class` — candidate
- **Object association:** any object with a declared FDT regime
- **Observable:** classified slope category (unit, suppressed, aging, indeterminate, negative)
- **Parameters:** classifier thresholds; profiles SHOULD record threshold values via `open-marker`
#### `capacity-envelope` — candidate
- **Object association:** subgraph
- **Observable:** sustainable subgraph size at given flux
- **Required shape (sparse):** $|\Gamma^\*| \sim \Phi^\*$
- **Required shape (dense):** $|\Gamma^\*| \sim \sqrt{\Phi^\*}$
- **Falsification:** measured scaling departs from declared regime
#### `falloff-longitudinal` — candidate
- **Object association:** any
- **Observable:** declared invariant under variation of $\Phi^\*$ alone
- **Permitted forms:** polynomial-in-$1/\Phi^\*$; critical-scaling; exponential-with-power-law-correction
- **Profile requirement:** declared form
#### `falloff-lateral` — experimental
- **Object association:** any
- **Observable:** behavior under relaxation of one lateral commitment (scalar trail, single kernel, reciprocal coupling, continuous time)
#### `falloff-scale` — candidate
- **Object association:** vertex (primary); subgraph (for $k_{\text{frust}}$ invariance)
- **Observable:** regime label as $\tau_{obs}$ sweeps
- **Required shape (vertex):** monotonic walk along $c \to s \to r$ as window broadens
- **Required shape ($k_{\text{frust}}$ subgraph):** invariance — no migration
- **Falsification:** non-monotonic regime walk on vertices; $k_{\text{frust}}$ migration on subgraphs
### 3.3 Extensions
Implementations MAY introduce signatures with identifiers under a namespace prefix (e.g. `x/<issuer>/<name>`) and MUST emit an `open-marker` describing observable, required shape, and falsification test.
---
## 4. Failure Events
A failure event is a typed protocol outcome reported during compilation or realization. Events carry information; severity is set by binding (§2.3.6) or by default.
### 4.1 Event record
```
failure-event := {
    event-id:        <vocabulary entry, §4.2>
    object-id:       <reference to object-record, or "global">
    ascent:          <integer or "pre-ascent">
    severity:        info | warn | reject
    context:         <free-form>
    measurements:    [<measurement-tuple>...]      # OPTIONAL
}
```
### 4.2 Vocabulary
#### `strand-at-s` — early-stable
- An operator chain or composite intended to yield $c$ or $r$ produces $s$.
- Diagnostic: identifies the stranded object and the attempted construction.
#### `merge-failure` — early-stable
- $C$ fails on a typed pair. Per current MPA characterization (Theorem 9), this occurs when $\Phi^\* < \kappa\gamma_{AB}$ and $\gamma_{AB} > 0$. Threshold semantics tied to the declared `mpa-version`.
#### `frustration-persistence` — early-stable
- A $k_{\text{frust}}$ subgraph fails to dissolve under flux pumping.
- Default severity: `info` if frustration is prescribed in the spec; `reject` if frustration-free closure is required.
#### `capacity-collapse` — early-stable
- Subgraph size exceeds the sustainable envelope at declared $\Phi^\*$.
- Reports measured size, declared envelope, scaling regime in `measurements`.
#### `persistence-loss-at-checkpoint` — candidate
- Object failed its survival criterion at a specific ascent (§5).
#### `signature-drift` — candidate
- Measured signature departs from declared shape beyond tolerance, without changing regime label.
#### `deformation-overflow` — candidate
- Associator or distributivity drift exceeds declared bound.
#### `kernel-misalignment` — candidate
- Realizer's accessible $\tau_{obs}$ band does not cover the spec's declared window.
#### `regime-flicker` — experimental
- Object oscillates between regimes at a rate not predicted by the declared dynamics.
#### `shadow-lift` — experimental
- An $\mathcal{M}_2$-shadow claim survives but the underlying regime trajectory differs from declared.
### 4.3 Reporting
Realizers consuming a profile SHOULD return a failure-event log with the realization attempt. Empty logs are permitted.
---
## 5. Coarse-Graining Checkpoints
A checkpoint designates an ascent at which a declared invariant must hold. Checkpoints turn the Compression Axiom into measurable points.
### 5.1 Checkpoint record
```
checkpoint-record := {
    checkpoint-id:     <opaque-string>
    ascent:            <non-negative integer>
    epsilon-bound:     <float in [0,1)>
    survival-set:      [<object-id>...]
    observable-set:    [<signature-id>...]
    drift-bound:       <numeric or symbolic>
    notes:             <free-form>
}
```
### 5.2 Semantics
A checkpoint at ascent $n$ asserts four conditions:
1. **Contraction.** $\|\mathcal{C}\|_{op}$ at this ascent does not exceed `epsilon-bound`.
2. **Survival.** Every object in `survival-set` retains its declared survival level.
3. **Observability.** Every signature in `observable-set` remains measurable on the post-ascent representation, possibly with rescaled parameters.
4. **Equivalence drift.** Equivalence-class membership of trail vectors does not drift beyond `drift-bound`.
Conformance is reported as a four-tuple of pass / fail / indeterminate. Indeterminate indicates the realizer could not measure; it is not a failure.
### 5.3 Sequences
Profiles MAY declare an ordered sequence of checkpoints. Gaps are permitted: a profile making claims at ascents 0, 2, 5 makes no claim at 1, 3, 4. Where the per-ascent contraction profile (§2.3.3) overlaps with checkpoint `epsilon-bound` values, the two SHOULD agree; disagreement is reported as `info`-severity event by default.
### 5.4 Boolean projection
A profile MAY declare a terminal checkpoint:
```
boolean-projection := {
    checkpoint-id:    "psp/boolean-projection"
    ascent:           "terminal"
    survival-set:     [<object-id>...]
    semantics:        "M_2 attractor; only c/r preserved"
}
```
Terminal checkpoint for $\mathcal{M}_2$ projection. Survival set declares which objects' shadows must persist.
---
## 6. Conformance
### 6.1 Profiles
| Profile id | Required content |
|---|---|
| `core-minimal`             | header; ≥1 object-record with required blocks |
| `core-with-checkpoints`    | core-minimal; ≥1 checkpoint-record |
| `core-with-signatures`     | core-minimal; signature-bindings using early-stable vocabulary only |
| `full-research`            | all sections; candidate and experimental items permitted |
A profile MUST declare its conformance level in the header. A realizer MUST support `core-minimal`. Support for higher profiles is advertised by the realizer.
### 6.2 Open markers
Any field whose semantics the issuer wishes to qualify locally MAY carry an open-marker:
```
open-marker := {
    field:           <dotted path into the profile>
    status:          provisional | experimental | extension
    rationale:       <free-form>
    issuer-binding:  <free-form>
}
```
Open markers are first-class. Their absence on an experimental field is itself non-conforming.
---
## 7. Deferred to future drafts
- Operator algebra ($C$, $S$, $K$, $R$): names referenced as opaque labels; semantics not protocolized
- Deformation calculus: drift bounds carried as targets, interpreted via `mpa-version`
- Extension axes (limit-cycle trail, hierarchical kernel, non-reciprocal coupling, higher-order frustration, finite-population discreteness): no schema commitments
- Composite catalogue: external; names opaque
- Cross-profile composition: no join algebra
- Cross-substrate signature transfer: validation procedure unspecified
- Realizer→synthesizer feedback channel
- Continuous RG-time parameter (current draft: integer ascents)
---
## 8. Versioning

Drafts are numbered `psp-draft-NN`. Profiles declare both `schema` (this protocol's version) and `spec-version` (the issuer's content version). Mismatches are diagnosed at the interchange layer. Translator tooling between drafts is published alongside each subsequent draft.
---
## 9. References
- Substrate Synthesizer specification document
- MPA v8
- RFC 2119 / RFC 8174
---
# PSP-NOTE-001
## Witness, Invariance, and the Cost of Substrate-Neutrality
**Designator:** `psp-note-001`
**Status:** Commentary. Non-normative. Companion to `psp-draft-00`.
PSP-Draft-00 conflates two artifact types with very different cost profiles. This note separates them and sketches the schema delta for `psp-draft-01`.
## 1. Asymmetry
Local realization is cheap: a substrate searching its own configuration space pays thermodynamic cost only, bounded near Landauer. Verifying a single realization against a profile is bounded, scaling with checkpoint count and ascent depth. Establishing that a persistence claim is **invariant across a substrate class** is mining-class — it requires ensembles of substrate simulations across scales and classes. Substrate-neutrality is not free; it is the expensive case.
## 2. Witness vs. invariance
- **Witness** — a single realizer's report: a configuration in one substrate satisfying a profile, with a failure-event log. Pointwise; cheap; abundant.
- **Invariance attestation** — a class-level claim that a profile is satisfied across a substrate class, supported by an ensemble of witnesses. Mining-class; scarce; scientifically load-bearing.
The two are structurally distinct: different consumers, different cost profiles, different validation procedures, different shelf lives.
## 3. Certifier role
A third role alongside synthesizer (issues profiles) and realizer (returns witnesses): **certifier** consumes witnesses across realizers and returns attestations. No substrate of its own; meta-work only.
## 4. Schema delta for `psp-draft-01`
- New record type `witness` formalizing what realizers return.
- New record type `invariance-attestation` referencing a profile, a substrate-class set, a witness ensemble, and a counter-witness retirement policy.
- New optional `certification-ambition` block in `profile-header`: target substrate classes, certification budget (opaque unit), invariance threshold.
- `certifier` documented as a third role.
- No breaking changes: profiles valid under draft-00 remain valid.
## 5. Open
Counter-witness retirement semantics; budget unit (compute-hours, lab-hours, opaque tag); federated or quorum certifiers; cost transparency in attestations.
## References
- `psp-draft-00`
- Substrate Synthesizer specification document
- MPA v8
---
# PSP-NOTE-002
## Quantum Substrates for Realizer-Side Subtasks
**Designator:** `psp-note-002`
**Status:** Commentary. Non-normative. Companion to `psp-draft-00`.
QC fits as a co-processor for specific realizer and certifier subtasks, not as a runtime for the synthesizer. This note locates where the fit holds and where it does not.
## 1. Position
The synthesizer is reflective, interactive, and operates in a multi-timescale image. QC's current programming model — compile circuit, ship to device, read measurements — is batch-mode and stateless across executions. The runtime fit is poor and unlikely to improve at the timescale of synthesizer development. The fit is at the realizer and certifier layers, on subtasks with shapes QC handles well.
## 2. Candidate subtasks
- **Realizer search.** Searching configuration space for arrangements satisfying a persistence profile across multiple ascents is combinatorial-with-amplitudes. Quantum walks and amplitude amplification have real bite where the search space carries hierarchical structure, which is the structure ascents induce.
- **Certifier-side ensemble sampling.** Establishing invariance across a substrate class reduces in part to sampling realization-space distributions and comparing across classes. Quantum-enhanced Monte Carlo has theorem-grade speedups on relevant sampling problem classes.
## 3. Topologically structured specs
$k_{\text{frust}}$ subgraphs are topologically protected — invariant of the coarse-graining flow rather than flux-resolvable. The mathematical home for "topologically protected, robust under local perturbation" overlaps substantially with topological quantum computation. Realizer search for prescribed-$k$ specs is a candidate subdomain where the structural rhyme may translate into engineering advantage.
## 4. Non-fit at the runtime layer
Three synthesizer requirements do not compose with the QC programming model: the three-times architecture, coarse-graining as primitive operation, and substrate-invisibility at the spec layer. QC as synthesizer runtime would require translating each interactive edit into circuit recompilation and device dispatch. Cost dominates.
## 5. Open
Concrete reductions of realizer search to quantum-walk problem instances; whether topological QC realizers admit native PSP witness format; certifier-side sampling cost models; co-processor protocol between classical synthesizer runtime and quantum realizer subroutines.
---
## References
- `psp-draft-00`
- `psp-note-001`
- Substrate Synthesizer specification document
- MPA v8
---
# PSP-NOTE-003
## Analog Hierarchical Media as Native Substrate
**Designator:** `psp-note-003`
**Status:** Commentary. Non-normative. Companion to `psp-draft-00`.
Digital computers can simulate the synthesizer. Analog hierarchical media can be it. The distinction has consequences for cost, faithfulness, and which artifacts are intrinsic to the synthesizer versus introduced by simulation.
## 1. Native fit
- **Continuous primitives.** Trail vectors are kernel-weighted histories, $\Phi^*$ is a continuous resource, $\lambda_A$ is a continuous spectrum the regime labels coarse-grain, $\gamma_{AB}$ is signed and continuous.
- **Three-times architecture.** Clock, $\lambda$, and RG axes run simultaneously — a free property of physical hierarchical systems, a scheduling problem for digital runtimes.
- **Coarse-graining as physics.** A property of slow modes in the substrate; in digital simulation, the most expensive recurring cost.
- **Free-run as default.** The substrate is in a thermalized noise state when not driven. Specifying behavior is selection from noise, not construction from emptiness — a different operation than the digital default, with consequences for what "issuing a profile" means in practice.
- **Capacity as geography.** Spatial heterogeneity makes the $\Phi^*$ distribution physical: high-flux and low-flux regions are places. Capacity envelopes that draft-00 carries as scalar bounds become fields over the substrate.
## 2. Translation cost and false signal
Digital prototypes pay representational cost every cycle: discretization, numerical integration, scheduler interleaving across timescales. Some artifacts of this cost — drift, regime-boundary blurring, simulation-induced aging — are mistakable for genuine MPA phenomena. This complicates validation and biases prototypes toward specs the simulation handles cleanly.
## 3. Substrate class
The required substrate is not a classical analog computer (op-amp networks are flat in scale structure). It is **programmable hierarchical media**: continuous dynamical systems with tunable couplings, observable response functions, and slow modes that correspond to higher RG levels. Candidate classes include spin-glass-like systems with engineered landscapes, certain neuromorphic architectures with explicit multi-timescale plasticity, photonic networks with engineered relaxation hierarchies, and soft-matter systems with controllable aging.
## 4. Implication for the protocol
If the synthesizer is itself analog, PSP becomes a contract between two physical dynamical systems — the synthesizer holding the spec, the realizer instantiating it — about which abstract dynamical structure they share. The persistence profile has a physical instantiation on the synthesizer side, not only a representation. No near-term schema change required; the schema's referent shifts.
## 5. Open
Faithfulness criteria for digital prototypes; what counts as a hierarchical-medium synthesizer demonstrator; non-optical signature readout modalities (acoustic, thermal, electromagnetic); whether protocol-level fields should distinguish digitally-simulated from analog-realized synthesizers; co-design path between protocol stability and hardware research.
---
## References
- `psp-draft-00`
- Substrate Synthesizer specification document
- MPA v8
# PSP-NOTE-004
## Phosphor-Volume Demonstrator
**Designator:** `psp-note-004`
**Status:** Commentary. Non-normative. Companion to `psp-draft-00`.
A 3D phosphor-doped matrix, externally excited and physically tumbled, maps cleanly onto enough synthesizer primitives to be a strong candidate for an early demonstrator substrate. Phosphor is engineering-mature in a way no other candidate substrate is.
## 1. Native mappings
- **Trail vectors** — phosphor afterglow in a region under repeated excitation: kernel-weighted history of commitment.
- **$c$/$s$/$r$ regimes** — high-rate-pumped excited population (committed); low-rate-pumped maintained-while-pumped (suspended); unpumped decaying (reset). Continuous in pump rate; regime labels coarse-grain.
- **$\lambda$-time spectrum** — phosphor decay constants span ~15 orders of magnitude. Multi-population matrices yield multiple coexisting timescales without simulation.
- **Coarse-graining as primitive** — wider $\tau_{obs}$ corresponds to coarser optical resolution; RG ascent is recursive downsampling of read-out. Looking at the ascent, not computing it.
- **Tumble** — physical rotation of the volume is a continuous group action on the artifact, not a metaphor.
- **3D embedding** — distinguishes geometric proximity from interaction; orthogonal edges ($\gamma \approx 0$) become representable.
## 2. Engineering questions
- **$\Phi^*$ as bounded resource.** Flood illumination does not produce a budget. Patterned scanning excitation with limited dwell, or saturating-absorption regimes, are candidate mechanisms.
- **Edge typology.** Cooperative edges (Förster transfer, mutual reabsorption), orthogonal edges (separated spectral channels), and competitive edges (local quencher depletion, photobleaching) need to be deliberately engineered into the matrix.
- **$k_{\text{frust}}$ realization.** Passive phosphor is unlikely to suffice; cyclic upconversion schemes or active medium elements are candidates.
## 3. First demonstrator
Minimal apparatus: centimeter-scale phosphor-doped sol-gel block; two phosphor populations with separated decay constants and clean spectral channels; two-photon point-scanning excitation with programmable dwell; motorized two-axis gimbal; multispectral camera array. Tabletop scale; few-grad-student-years of engineering. The deliverable is evidence that synthesizer primitives have natural physical instantiation in mature substrate. Not a synthesizer.
## 4. Open
Quantitative mapping between MPA quantities and phosphor-matrix observables; matrix chemistry for engineered edge typologies; resolution and throughput limits of 3D excitation patterning; registration and calibration under tumble; whether a demonstrator at this scale can produce reportable witnesses against PSP profiles.
---
## References

- `psp-draft-00`
- `psp-note-003`
- Substrate Synthesizer specification document
- MPA v8
