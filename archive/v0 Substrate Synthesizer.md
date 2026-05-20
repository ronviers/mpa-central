# Substrate Synthesizer
## A behavior compiler for resource-bounded inference systems
---
## Premise
Specify dynamical behavior at the universality-class layer. Realizer search produces physical arrangements — atomic, molecular, circuit, network, biological — whose collective dynamics match the spec.
The synthesizer is upstream of substrate choice. Output is a substrate-neutral behavioral spec in Metastable Propositional Algebra (MPA) primitives. Realization is delegated to substrate-specific search.
## Core: structured persistence under repeated coarse-graining
The synthesizer is built on a theory of **inference-preserving renormalization**. Specifying behavior means specifying what survives the flow.
The Compression Axiom defines an RG-like contraction $\epsilon = \|\mathcal{C}\|_{op} < 1$ at each ascent of the meta-ledger tower. Trail vectors are equivalence classes under this flow. Vertex regimes are the flow's universality classes. $\mathcal{M}_2 = \{c, r\}$ is the terminal attractor. $k_{\text{frust}}$ is a topological invariant. Boolean is the degenerate fixed point where the flow collapses every level to identity.
A spec is a structure that *persists* under repeated $\mathcal{C}$ — at the regime, edge, and subgraph layers — within bounded $\epsilon$. The artist designs persistence; the engineer characterizes its shape; the compiler emits realizer targets that hit the persistence profile.
This is the load-bearing inversion: the synthesizer is not a viewer of MPA. It is an instrument for specifying **which structures carry through the flow and at what contraction cost**.
## Two registers, one medium
**Composite catalogue — artist register.** Hebbian, mentor, Lotka–Volterra, Kuramoto, gridlock as named composites. Behavioral modules with target dynamics. Composing a spec is composing modules.
**Operators — engineer register.** $C, S, K, R$ as constructive protocols. Try-merge, hold-both, distinguish, erase. Verbs that act on trail structure with measurable success/fail/strand-at-$s$ outcomes governed by $\Phi^*$ and $\gamma$.
The boundary is permeable. Every composite decomposes to operator sequences; every operator sequence composes to a named or unnamed composite. The artist drills into engineer view to see why a Hebbian module strands at $s$ in a given budget; the engineer pulls back to artist view to see the composite shape an operator chain produces. Same medium, two readings.
Permeability is the synthesizer's defining surface property.
## Spec object
A typed configuration $(V, E, \Gamma, \Phi^*, \tau_{obs})$:
- **Vertices** with target regime ($c$/$s$/$r$) and trail properties
- **Edges** with signed shear $\gamma_{AB}$
- **Subgraphs** flagged for $k_{\text{frust}}$ (prescribed) or for frustration-free closure (forbidden)
- **Flux budget** $\Phi^*$ global, with local distributions for mentor pumping and focused gardens
- **Observer kernel** $\tau_{obs}$ band — the timescales at which the spec must read
- **Persistence profile** — the contraction $\epsilon$ tolerated at each ledger ascent, and which structural objects must survive
Each element carries target FDR signatures, capacity envelopes, deformation tolerances. Falsifiable per element.
## Realizer interface
Standardized signature-target document:
- Required signatures per object type — unit slope for $r$, suppressed locus for $c$, aging diagonal for $s$, transient negative response for $k_{\text{frust}}$
- Timescale band(s) — $\tau_{obs}$ window the spec must hold across
- Capacity envelopes — sustainable subgraph size at given flux
- Deformation tolerances — admissible associator and distributivity drift
- Persistence profile — invariants required to survive coarse-graining at specified contraction rates
- Forbidden regions — configurations the spec must not produce under specified noise models
Substrate-class-tagged. Versioned against MPA's empirical status.
## Architecture
### Spec layer
MPA primitives. Invisible field, typed graph, kernel-relative reading. Three-times architecture: clock-time of trail evolution, $\lambda$-time of stability, RG-time of coarse-graining ascent. Tumble as dimensional re-slicing across non-coordinated axes. Coarse-graining as primitive operation — the artist takes flow steps as design moves, watching what carries and what dissolves.
### Compiler layer
Translates spec into realizer-tractable targets:
- Timescale grounding (dimensionless ratios → physical units once realizer class binds)
- Realizability constraints flowing upstream as soft warnings, dead zones, rejected configurations
- Multi-substrate compilation — same spec, parallel realizer targets
- Stress profile generation — perturbations the realizer must survive under
- Persistence verification — computed survival of spec invariants across simulated $\mathcal{C}$ ascents
### Realizer interface layer
Third-party-consumable signature-target format. Substrate-class-tagged. Synthesizer's responsibility ends here.
## Carve-outs
**Composite catalogue is the artist's parts library.** Each row a target dynamic. Composing a spec from catalogue elements is composing behavioral modules with known persistence properties.
**Operators are the engineer's verbs.** $C, S, K, R$ act on trail structure. Failure modes (Theorem 9: merge fails when $\Phi^* < \kappa\gamma_{AB}$, $\gamma_{AB} > 0$) surface during specification, not after. Productive failure is information.
**FDR signatures are the spec language's measurement vocabulary.** Active probe: "if I perturb here, what response shape do I require?" The synthesizer reads back signatures from compiler-side simulation as the artist edits.
**$k_{\text{frust}}$ is a first-class design feature.** Prescribed topological obstruction. Memory hysteresis, computation in unsatisfiable regimes, deliberate gridlock as stability mechanism. Survives the flow by topology, not by flux. Distinct surface area.
**Capacity scaling is binding constraint.** $\sqrt{\Phi^*}$ dense, $\Phi^*$ sparse. Density commits flux. Trade-off surfaces as the spec is built.
**Boolean export retained.** $\mathcal{M}_2$ projection ships to legacy-system targets that cannot consume MPA-native specs. Boolean is the persistence profile's degenerate case — the spec where only $c/r$ survive arbitrary ascent.
**Three faces of falloff are spec dimensions.** Longitudinal ($\Phi^*$), lateral (other commitments), scale ($\tau_{obs}$). The artist works in all three; the compiler emits targets across the relevant slices.
## Carry-overs
Entities as trail vectors with regime-textured ghost trails. Edges as felt tension. $k_{\text{frust}}$ inhabitable. Tumble multi-axis. Playhead bivalent: $\tau_{obs}$ sweep and $\Phi^*$ modulation as orthogonal first-class controls. Honest complexity. Substrate invisible — both because the meta-ledger tower forbids visualization and because committing to a visualizable substrate violates the spec layer's neutrality.
## Open design
- **Tumble axis identities.** Multi-axis confirmed; specific axes open. Candidates: $\tau_{obs}$ band, possible/actual, local/global, abstraction level, RG-step depth.
- **Permeability surface.** How artist↔engineer view-switching is presented. Probably continuous, not modal.
- **Realizer-class defaults.** Default realizer integration vs. purely upstream stance.
- **Multi-substrate composition.** Hybrid specs realizing across substrate classes.
- **Validation feedback.** Compilation failures surface as substrate constraints or stay at compiler layer.
- **Persistence profile UI.** How the artist specifies and reads the survival of structure across $\mathcal{C}$ ascents.
- **Φ\* as physical dial.** Drive rate is flux budget directly; accessible behavior class scales with available drive, possibly through critical thresholds. Design-space access becomes a thermodynamic constraint rather than a licensing one.
## Position in tool ecosystem
Upstream of:
- Inverse design for materials, molecules, metamaterials
- Programmable matter and soft-robotics behavioral specification
- Neuromorphic circuit design at functional level
- Synthetic biology dynamics specification
- Quantum error correction code design
The layer all of these need: substrate-neutral spec medium grounded in measurable dynamical signatures and persistence under coarse-graining.
## Status
| Status | Item |
|---|---|
| **Load-bearing** | structured persistence under repeated coarse-graining; permeable artist/engineer boundary; MPA universality |
| **Ready** | spec primitives, composite catalogue, operator algebra, FDR-signature targets, capacity envelopes |
| **Architectural** | spec / compiler / realizer-interface separation; three-times architecture |
| **Aesthetic** | substrate invisibility, multi-axis tumble, productive failure, honest complexity |
| **Open** | tumble axes, permeability surface, realizer defaults, multi-substrate composition, validation feedback, persistence profile UI |
| **Frontier** | $k_{\text{frust}}$ as prescriptive feature, coarse-graining as design move, persistence specification as primary artifact |
| **Out of scope** | renderer/input/platform, specific realizer integrations, MPA validation logic |
---
## Position
Behavioral specification at the universality-class layer. Substrate-neutral. Falsifiable per element. Composable from named composites with permeable access to operator-level construction. Output consumable by realizer search across substrate classes.
The synthesizer's heart is a theory of inference-preserving renormalization: structure designed to persist under repeated coarse-graining at bounded contraction cost. Composites and operators are the two registers; the spec medium is what makes the boundary between them permeable. Realizer search downstream finds atoms.

Note for future revision: The categorization of κ in this document treats it as a substrate-determined property — something the realizer search produces rather than something the spec layer controls. A counter-possibility: that Φ* and κ enter the formalism symmetrically (only their ratio governs dynamics), and treating one as user-facing while the other is downstream may be an artifact of habit rather than principle. If κ is in fact a tunable bath-coupling that a realizer could expose, the spec/compiler/realizer-interface boundary shifts. Worth revisiting in a future pass: is κ properly upstream, properly downstream, or split (substrate sets a κ envelope, the spec dials within it).