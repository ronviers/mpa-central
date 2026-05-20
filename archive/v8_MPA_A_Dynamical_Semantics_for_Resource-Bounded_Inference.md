# Metastable Propositional Algebra
## A Dynamical Semantics for Resource-Bounded Inference (v8)

**Abstract.** Boolean logic is the infinite-flux limit of inference. At finite energy budgets, propositions are dynamical objects — trail vectors moving along a one-dimensional stability axis through one of three regimes between two endpoints, stably maintained or dissolved into noise. The framework also tracks two non-vertex structural objects: signed pairwise shear $\gamma_{AB}$ as an edge property of the interaction graph, and topological frustration $k_{\text{frust}}$ as a subgraph property. Metastable Propositional Algebra (MPA) specifies the deviation profile from the Boolean asymptote at three layers: vertex regimes — candidate universality classes under coarse-graining flow, with labels read at observation scale — a typed operator algebra ($C, S, K, R$, taking the operational role of AND/OR/XOR/NOT as $\Phi^* \to \infty$, with $K$'s codomain restricted to the two-cell Boolean section $\mathcal{M}_2 \subset \mathcal{M}$), and a molecular catalogue of composite regimes that emerge under coupling — recovering independently-named phenomena across neuroscience, ecology, statistical mechanics, combustion, and organisational dynamics under one rule set. Sustainable graph capacity for classically consistent structure scales as $\sqrt{\Phi^*}$ on dense interaction graphs; this scaling is the reason dissipative structures sparsify rather than fully connect. Each vertex regime carries a distinct fluctuation-dissipation signature, and the topologically-frustrated subgraph carries its own; the suspended-regime signature transfers cleanly from Langevin substrate to surface-code syndrome streams — a measured cross-substrate transfer of an MPA observable, and the framework's strongest evidence to date for the universality-class reading. The Compression Axiom on the meta-ledger ladder takes the form of a renormalization-group flow whose Convergent Tower is its convergence theorem; trail vectors are identified with their classes under this flow, the two-cell subspace $\mathcal{M}_2 = \{c, r\}$ is the flow's fixed-point set, and $k_{\text{frust}}$ is an invariant of the flow on substrates that carry it. The same equivalence-class quotient that makes cross-substrate transfer well-posed makes the structural Boolean homomorphism (Theorem 8, Appendix C) hold algebraically; for $C, S, R$ the quotient acts on outputs, for $K$ it acts on inputs, and the Boolean section $\mathcal{M}_2$ is what makes a single quotient application per operator suffice. Restricted to $\mathcal{M}_2$, the operator signature is itself a Boolean algebra isomorphic to $(\mathbb{B}, \land, \lor, \oplus, \neg)$ (§3.6); finite-flux deformations of associativity, distributivity, and Boolean shadow are bounded by Theorems 6, 7, 9 of Appendix J, which recover Boolean structure as $\Phi^* \to \infty$ and characterise resource-induced instabilities at finite flux. The MPA-to-Boolean falloff has three faces: longitudinal along $\Phi^*$, lateral across the framework's other dynamical commitments, and the scale dimension fixed by kernel width. We conjecture that Boolean is a singular point in the inference landscape, with non-perturbative regions populated by candidate operators that have no Boolean limit at all. Bifurcation theory, spin-glass landscape theory, and non-reciprocal active matter supply the existing mathematics.

---

## §1 — Boolean as the asymptote

Boolean logic tells you what follows from what. It does not tell you what it costs to keep the premises standing. Maintaining a proposition against environmental noise — in neural tissue, a processor, a factory cell, a quantum codeblock — requires work; if the work stops, the structure dissolves. Boolean's silence on this cost is exactly its idealisation. It is the limit reached as the available flux $\Phi^* \to \infty$.

MPA is the finite-flux generalisation. Its content is the *shape of the deviation* from the Boolean asymptote: the wedge of state space where shear exceeds budget, the dense-graph capacity that closes off below the Boolean ceiling, the fluctuation-dissipation signatures that distinguish dynamical regimes from one another even before the system's truth values resolve, and the scale-relativity of regime labels under varying observation kernels. Each operator-level theorem (Appendix C) shows the framework's operators reducing to the operational role of a Boolean connective in the infinite-flux limit; at finite flux they are dynamical actions on trail structure, not truth-functional connectives, and the framework's predictive content lives entirely in that finite-flux interior.[^1]

The framework's reach across substrates rests on an unusual property: the formal mathematics and the intuitive framing are the same content. *Trails*, *regimes*, *flux budget*, *frustrated cycle* are not metaphors layered over equations — they are the equations stated in a vocabulary that ports without distortion across factories, cognitive systems, surface codes, and classical channel codes. Falsification does not require specialists in proof theory or replica methods; an autocorrelation and a step-response function suffice.

[^1]: MPA sits in a populated landscape of thermodynamic-frame approaches: Landauer's bound and stochastic thermodynamics of computation; statistical-mechanical mappings of error-correcting codes (Dennis–Kitaev–Landahl–Preskill 2002 and successors); finite-blocklength information theory; active inference; renormalization-group methods in critical phenomena. MPA's specific commitments — trail vectors as history-bearing objects, a typed regime structure (vertex / edge / subgraph), $\Phi_{book}$ as a peer of $\Phi^*$, the Compression Axiom on meta-ledger ladders — yield the testable observables developed below. Appendix I gives the substantive differentiation against the closest neighbours; Appendix H gives the calibration discipline used when applying the framework to substrates with developed prior art.

---

## §2 — Trails, regimes, and the structural objects of the framework

A *trail vector* is the kernel-weighted history of how the system has moved while a proposition was active (Appendix A). When two propositions conflict, their trails push the system in incompatible directions, and that destructive interference is the physical substrate of logical contradiction.

Truth values are endpoints. A proposition stably maintained is approximating $1$; a proposition decayed into the bath is approximating $0$. The framework distinguishes three kinds of structure between those endpoints, classified by their type.

### Vertex regimes

The single-proposition state lies on a one-dimensional stability axis read off the Lyapunov rate $\lambda_A$ of a single trail. The classifier $\rho: \mathcal{M}(\Phi^*) \to \{c, s, r\}$ is unary — it reads a vertex and returns a regime label.

| Regime | Symbol | Condition | Trajectory |
|---|---|---|---|
| **Committed** | $c$ | $\lambda_A \ll -\kappa^{-1}\Phi^*$ | Self-sustaining. Approximating $1$ with minimal external work. Closer to the Boolean ideal. |
| **Suspended** | $s$ | $|\lambda_A| \lesssim \kappa^{-1}\Phi^*$ | True-while-pumped. Marginal; held against decay by active maintenance; would dissolve if the pump stopped. |
| **Reset** | $r$ | $\lambda_A \gg \kappa^{-1}\Phi^*$ | Decayed. Approximating $0$. No structure, no maintenance cost. |

A proposition migrates between vertex regimes as the system's flux budget and its couplings change. Forgetting is not a separate operation: an unreinforced trail simply shrinks until its projections onto neighbours fall below the noise floor, and the cross-dissipations that tied it to the graph evaporate into the bath. (Phase boundaries: Appendix B.)

### The edge property

The interaction graph $G = (V, E)$ carries signed edge weights $\gamma_{AB}$ encoding the geometric shear between trails:

- $\gamma_{AB} < 0$ — *cooperative*. Trails reinforce; merging deepens.
- $\gamma_{AB} \approx 0$ — *orthogonal*. Independent; no cross-dissipation.
- $\gamma_{AB} > 0$ — *conflicting*. Destructive interference; local incompatibility.

Shear is local and thermodynamic. Given sufficient $\Phi^*$, both endpoints of a positive-shear edge can be pumped and maintained — the edge contributes a dissipation cost $\kappa\gamma_{AB}$ to the joint flux ledger, but the structure is sustainable. Positive shear is *resolvable by flux*, and edges follow their endpoints under coarse-graining: an edge whose endpoints flow to $r$ ceases to exist.

### The subgraph property

A subgraph $\Gamma \subseteq G$ is **frustrated** ($k_{\text{frust}}$) if it contains a cycle of $c$-edges whose geometric shear product around the cycle is obstructive — pairwise-stable propositions arranged in a globally unresolvable loop. This is *topological*. It is not resolvable by increasing $\Phi^*$, and it survives coarse-graining as long as the substrate's interaction graph carries the obstruction. The classic informal cases — approach–avoidance arrangements, traffic gridlock, k-SAT-style unsatisfiable cores — sit here.

### The labels are scale-relative

The regime classifier reads the trail vector through a kernel of width $\tau_{obs}$. The same dynamical history can register as $c$, $s$, or $r$ depending on $\tau_{obs}$: short windows resolve residual structure and read it as committed, mid-windows resolve the active maintenance work and read it as suspended, long windows wash both away and read it as reset. The labels are scale-relative; the *hierarchy itself* — that a substrate has a $c$-shelf at one scale, an $s$-shelf at another, and an $r$-plain at a third — is not. Substrate timescales fix the hierarchy; the observer's window picks which rung is read. (Operational consequences: §5, §6, §7.) The scale-relativity acts on the vertex regimes — what flips under kernel-width change is the label assigned to a single trail. Edge shear $\gamma_{AB}$ is read from the same trails through the same kernels, so its magnitude scales with $\tau_{obs}$; the topological obstruction encoded in $k_{\text{frust}}$ is invariant under kernel choice because it is a property of the interaction graph, not of any particular trail.

### The vertex regimes are universality classes; $k_{\text{frust}}$ is a topological invariant

Under the equivalence-class reading of Appendix A — where a trail is identified with its class under coarse-graining flow rather than with any one microscopic representative — each vertex regime is a candidate universality class: $c$ a stable attractive structure under the flow, $s$ a metastable transient basin, $r$ the high-entropy trivial phase. The cross-substrate transfer of §5 — the s-regime aging diagonal appearing on substrates with no shared microphysics — is what universality of this kind looks like in practice: substrates differing in microscopic detail flow to the same coarse-grained response structure. Identifying the formal invariants that pick out each vertex class is open work (Appendix A).

The frustration object $k_{\text{frust}}$ is an invariant of a different type. It is preserved by the flow on substrates whose interaction graph carries it — pairwise misalignment can dissolve into reset on a wide enough kernel, but a non-contractible cycle of $c$-edges does not — but it is a topological property of the substrate, not a universality class of response shape. The framework's substrate-neutrality at the vertex level (universality across microphysics) and its substrate-specificity at the subgraph level (topology of the interaction graph determines which graphs admit frustration) are the same fact stated at two layers.

A thermodynamic distinction survives the scale-relativity. Self-sustaining structure, with internal coupling closure, is energetically distinct from flux-pumped structure regardless of the kernel width through which either is read. The §3.5 mentor pairing turns on this distinction at the substrate level even when the labels at any single $\tau_{obs}$ do not.

The three vertex regimes are exhaustive for the framework's current dynamical commitments — a scalar trail under a single memory kernel, with reciprocal pairwise couplings, evolving continuously in time. Relaxing any of those commitments opens regions of phase space the present formulation cannot reach (§8). The two structural objects above — signed shear and topological frustration — are the framework's complete account of *between-trail* structure on classically consistent graphs and on graphs that fail consistency.

---

## §3 — The four operators

Each operator is a constructive protocol whose infinite-flux limit reduces to the operational role of a Boolean connective (Appendix C). The arrows $C \to$ AND, $S \to$ OR, $K \to$ XOR, $R \to$ NOT below denote that operational reduction in the idealisation $\Phi^* \to \infty$; at finite flux the operators are dynamical actions on trail structure, not truth-functional connectives. They act at the equivalence-class level (Appendix A), which is what makes the limit theorems substrate-neutral.

The signature is typed. Write $\mathcal{M} = \{c, s, r\}$ for the vertex regime space, and define
$$\mathcal{M}_2 \;=\; \{c, r\} \;\subset\; \mathcal{M}.$$
The two-cell subspace $\mathcal{M}_2$ has three independent characterisations that turn out to identify the same set: it is the fixed-point set of the coarse-graining flow ($c \to c$, $r \to r$; $s$ is metastable and migrates to one or the other); it is the section of the limit-equivalence quotient $q: \mathcal{M}(\infty) \to \mathbb{B}$ on which $q$ restricts to a bijection; and it is the codomain of the operator $K$. The same two-cell algebra is read three ways. The four operators carry codomain types

$$C, S \,:\, \mathcal{M}^2 \to \mathcal{M}, \qquad K \,:\, \mathcal{M}^2 \to \mathcal{M}_2, \qquad R \,:\, \mathcal{M} \to \mathcal{M},$$

and $K$ is the unique signature operator whose codomain is restricted to $\mathcal{M}_2$. The asymmetry between $K$'s Boolean limit and the limits of $C, S, R$ — direct in the latter, requiring the limit-equivalence quotient to act on $K$'s inputs in the former — is the typed-signature shadow of this codomain restriction; the quotient's location (output-side for $C, S, R$, input-side for $K$) is determined by which side of the operator signature touches the metastable regime $s$. The structural homomorphism this yields is Theorem 8 of Appendix C.

**Commitment** $C : \mathcal{M}^2 \to \mathcal{M}$ — *try to merge.* Constructs the joint trail $d_{A \oplus B} = w_A d_A + w_B d_B$ and evaluates its stability $\lambda_{A \oplus B}$. Aligned trails deepen ($c$); orthogonal trails coexist ($s$); opposed trails fight, going to $s$ if flux covers the shear and to $r$ otherwise. As $\Phi^* \to \infty$, all shear is suppressible and $C \to$ AND.

**Suspension** $S : \mathcal{M}^2 \to \mathcal{M}$ — *hold both without merging.* Possible when the joint maintenance cost fits the budget: $\kappa(|\lambda_A| + |\lambda_B|) + \max(0, \kappa\gamma_{AB}) \leq \Phi^*$. As $\Phi^* \to \infty$ the inequality is trivial and $S \to$ OR.

**Difference** $K : \mathcal{M}^2 \to \mathcal{M}_2$ — *detect distinguishability.* Define the unnormalised difference vector $\delta(A, B) := \hat{d}_A - \hat{d}_B$, with the convention that dissolved trails contribute $\hat{d}_X = 0$, so that $\delta(A,B) = 0$ precisely when the two trails share an orientation or both have dissolved. $K$ outputs $c$ when $\delta(A,B) \neq 0$ and $\Phi^*$ covers the diagnostic shear required to maintain the distinction; $r$ otherwise. The codomain $\mathcal{M}_2$ is structural: $K$ reads membership in the nullspace of the trail-difference relation. At finite flux the configurations $\delta$ records — parallel, anti-parallel, oblique — are dynamically distinct, each carrying its own stability and dissipation profile; Boolean parity does not see these distinctions, MPA does. As $\Phi^* \to \infty$, the limit-equivalence quotient on $\mathcal{M}(\infty)$ collapses every non-zero $\delta$ onto a single distinguishability class while leaving the nullspace fixed, and $K \to$ XOR (Theorem 8, Appendix C). The input-side action of the quotient is the structural signature of MPA's dynamical semantics: logical parity is not primitive but the coarse-grained shadow of a richer finite-flux distinction operator, and $K$'s asymmetric typing among $\{C, S, K, R\}$ is the coordinate-free expression of that depth. In the cavity-method vocabulary on random constraint satisfaction, $K$ is the parity-check operator over $\mathbb{F}_2$ — the same object class that distinguishes XOR-SAT from $k$-SAT.

**Reset** $R : \mathcal{M} \to \mathcal{M}$ — *erase.* Severs the proposition's couplings into the bath; the work bound is $W_R \geq k_B T \ln 2 \cdot H(A \mid \text{rest})$. Classical logic brackets this dissipation; in the infinite-flux limit, $R \to$ NOT.

---

## §3.5 — Composite regimes from pairings

The vertex regimes of §2 are atomic (single-proposition states); the four operators of §3 are pair-actions. The framework also has a *molecular* layer: when two propositions in specified vertex regimes are coupled with specified edge condition, the joint structure occupies a composite regime determined by trail alignment, kernel depth, and flux availability. The catalogue below gives the elementary pairings, organised by vertex-regime endpoints and edge condition. The frustrated-cycle row sits at the graph level, not the pair level — that distinction is the molecular layer's structural type.

| Pairing | Edge condition | Composite | Empirical example |
|---|---|---|---|
| **$c$–$c$ aligned** | $\gamma_{AB} < 0$ | $c$ (deepened basin) | Reinforced synapses; aligned force chains in granular matter |
| **$c$–$c$ orthogonal** | $\gamma_{AB} \approx 0$ | $s$ (coexistence) | Independent memory items held simultaneously; non-interacting product lines in a factory |
| **$c$–$c$ opposed** | $\gamma_{AB} > 0$ | $s$ if $\Phi^*$ covers shear; one to $r$ otherwise | Two competing hypotheses held under active scrutiny; coexisting metastable phases under driving |
| **$c$–$s$** | $\gamma_{AB} < 0$ | $s$ (mentor: $c$ stabilises $s$, $s$ pumps $c$) | Teacher–student synaptic tagging; mentor–mentee in organisations; pilot-light combustion |
| **$s$–$s$** | $\gamma_{AB} > 0$ | $s$ if joint cost $\leq \Phi^*$; competitive dropout otherwise | Two tasks competing for working memory; two species competing for the same nutrient |
| **$c$–$c$–$c$ frustrated cycle** | shear product obstructive around the loop | $k_{\text{frust}}$ (subgraph-level) | Approach–avoidance in reinforcement learning; gridlock in traffic networks; unsatisfiable Horn clauses |
| **Oscillatory–$c$** | $d_A$ a limit cycle, $\lambda_B \ll 0$ | Entrainment or quenched oscillation | Pacemaker forcing a cardiac cell; circadian clock gating cortical excitability |

Each row has independent prior art in some field — Hebbian co-firing, synaptic tagging-and-capture (Frey & Morris 1997), Lotka–Volterra competition, Kuramoto entrainment, k-SAT frustration, classical extinction dynamics. At the level of a single pairing, MPA's contribution is *adheres / named*: the field already has the phenomenon, the framework supplies a unifying vocabulary. At the level of the table, the contribution is sharper. The same vertex-regime + edge-condition rule set generates phenomena with no shared physical content across neuroscience, ecology, stat mech, combustion, and organisational dynamics. This is the framework's unification claim made specific at the molecular layer.

The frustrated-cycle row sits at a different type than the others: it is a property of three or more trails arranged on a non-contractible loop, not a property of a pair. This is the molecular layer's natural carrier of $k_{\text{frust}}$, and it places the molecular reading on its proper footing — composite regimes are properties of small subgraphs, not of single objects. The two-vertex rows are the simplest case of this; the cycle row is the smallest case where topology matters.

Two further rows cross into the extension territory of §8. The $s$–$s$ composite's switching under flux dial is the longitudinal-falloff slice of §7.1. The oscillatory–$c$ row uses the limit-cycle trail extension directly; entrainment versus quenched oscillation is set by whether the committed basin captures or breaks the cycle.

---

## §3.6 — The Boolean section

§3 introduced the typed signature with the two-cell Boolean section $\mathcal{M}_2 = \{c, r\} \subset \mathcal{M}$ identified three ways: as the codomain of $K$, as the fixed-point set of the coarse-graining flow, and as the section on which the limit-equivalence quotient $q: \mathcal{M}(\infty) \to \mathbb{B}$ is bijective. This section develops the algebraic content of that section: the Boolean isomorphism it carries, the dynamical boundary rules at its interface with the metastable interior, and its role as the terminal attractor of the Compression Axiom flow.

The constants of the signature, $\top$ and $\bot$, denote the two limit classes of maintained and dissolved propositions at infinite flux,
$$\mathcal{M}(\infty) \;=\; \{[\top], [\bot]\} \;\cong\; \mathbb{B},$$
with finite-flux representatives $c \in [\top]$ and $r \in [\bot]$ in $\mathcal{M}_2 \subset \mathcal{M}$.

> **Theorem (Boolean section).** The restriction of the MPA operator signature $\Sigma_{\Phi^*} = \{C, S, K, R, \top, \bot\}$ to $\mathcal{M}_2$ is a Boolean algebra isomorphic to $(\mathbb{B}, \land, \lor, \oplus, \neg)$.

*Proof sketch.* By Theorem 8 (Appendix C), each operator's σ-shadow reduces to its Boolean counterpart as $\Phi^* \to \infty$. With $\mathcal{M}_2$-inputs the limit is reached at the σ-shadow level identically at finite flux, since the metastable input $s$ has been eliminated from the domain. The case tables collapse:

| MPA operator | $\mathcal{M}_2$-restriction | Boolean role |
|---|---|---|
| $C$ | $C\big|_{\mathcal{M}_2^2}$ | $\land$ |
| $S$ | $S\big|_{\mathcal{M}_2^2}$ | $\lor$ |
| $K$ | $K\big|_{\mathcal{M}_2^2}$ | $\oplus$ |
| $R$ | $R\big|_{\mathcal{M}_2}$ | $\neg$ |

Closure on $\mathcal{M}_2$ holds at the level of the Boolean shadow σ, not necessarily at the regime label. With $\mathcal{M}_2$-inputs, $C$ can produce $s$: orthogonal or opposed-with-flux-covering merges give $\lambda_{A \oplus B} \approx 0$, the joint trail is metastable but maintained, and $\sigma(s) = 1 = \sigma(c) \land \sigma(c)$, so the σ-homomorphism is preserved even though the regime label has strayed from $\mathcal{M}_2$. The distinct case where σ disagrees — $C(c, c) \to r$ when shear exceeds budget, $\sigma(r) = 0$ — is the Boolean deviation $\Delta_C$ of Theorem 9 (Appendix J). Both deviations vanish as $\Phi^* \to \infty$: $\gamma \to 0$ collapses orthogonality, and Theorem 9's threshold $\Phi^* < \kappa\gamma_{AB}$ recedes. $K$ maps into $\mathcal{M}_2$ by construction (no closure deviation possible); $R$ maps $c \leftrightarrow r$. Associativity, commutativity, and the De Morgan dualities follow from the trail-vector definitions and Theorem 8. ∎

**Boundary rules at $\mathcal{M}_2 \times \{s\}$.** When one input lies in $\mathcal{M}_2$ and the other in the metastable interior $\{s\}$, the operators do not reduce to Boolean identities — $\bot$ is not a global annihilator for $C$, $\top$ is not a global identity for $S$, because the edge shear and flux budget remain active constraints. The dynamical rules:

| Operator | Input | Output condition |
|---|---|---|
| $C(\top, s)$ | $c$–$s$, edge $\gamma$ | $c$ if $\gamma < 0$ and alignment deepens the joint basin; $s$ if $\gamma \approx 0$; $s$ or $r$ if $\gamma > 0$ depending on whether $\Phi^*$ covers the shear. |
| $C(\bot, s)$ | $r$–$s$, any edge | Pass-through: output is $s$ if $\Phi^*$ covers $\kappa\|\lambda_s\|$, else $r$. The dissolved proposition contributes no maintenance cost and no shear. |
| $S(\top, s)$ | $c$–$s$, any edge | $s$ if joint cost $\kappa\|\lambda_s\| + \max(0,\kappa\gamma) \leq \Phi^*$; else competitive dropout to $r$. |
| $S(\bot, s)$ | $r$–$s$, any edge | Pass-through: cost is $\kappa\|\lambda_s\|$; output is $s$ or $r$ as flux permits. |
| $K(\top, s)$ | $c$–$s$ | $c$ if the $s$-trail retains residual structure non-parallel to $\top$ and $\Phi^*$ covers the diagnostic shear; $r$ if the $s$-trail has collapsed to parallel or dissolved. |
| $K(\bot, s)$ | $r$–$s$ | $c$ if the $s$-trail is non-zero; $r$ if dissolved. |

These rules are dynamical, not equational: they govern how the Boolean section interfaces with the finite-flux interior, and they are the operator-level shadow of the §3.5 composite-pairing catalogue. The mentor pairing — c–s with $\gamma < 0$, sustained — appears in §3.5 as a stable composite in regime $s$; here it appears as $C(\top, s) \to c$ when the operator action is taken at a single timestep. The two readings are compatible: §3.5 describes the equilibrium that emerges from sustained coupling; the boundary rules above describe the operator action.

**Terminal-attractor reading.** Under the Compression Axiom of §6, every ascent in the meta-ledger tower applies a contraction $\mathcal{C}$ with $\|\mathcal{C}\|_{op} = \epsilon < 1$. The trail classes of level $n$ are equivalence classes of level-$(n-1)$ trajectories under this flow. The two-cell subspace $\mathcal{M}_2$ is the **terminal attractor** of the flow: repeated compression drives every proposition to either $c$ or $r$, and the information distance to $\mathcal{M}_2$ contracts geometrically. The Convergent Tower of Appendix G converges precisely because the ledger entries are drawn toward this two-element fixed-point set; $\epsilon$ measures the residual information mass outside $\mathcal{M}_2$ after each coarse-graining step. In this sense $\top$ and $\bot$ are the algebraic as well as dynamical fixed points of resource-bounded inference: they are the only regime labels that survive arbitrary meta-level ascent.

The properties of the constants are summarised:

| Property | $\top$ ($c$) | $\bot$ ($r$) |
|---|---|---|
| Flux limit | $[\top] \in \mathcal{M}(\infty)$ | $[\bot] \in \mathcal{M}(\infty)$ |
| Flow behaviour | Fixed point: $c \to c$ | Fixed point: $r \to r$ |
| Maintenance cost | Self-sustaining; minimal $\Phi$ | Zero |
| Quotient image | $q(c) = 1$ | $q(r) = 0$ |
| Meta-ledger fate | Terminal attractor | Terminal attractor |
| Boolean role | Identity for $\land$; dualiser for $\neg$ | Annihilator for $\land$; fixpoint for $\neg$ |

The $\mathcal{M}_2$ section is therefore neither a separate algebra grafted onto MPA nor a classical prejudice imported from the Boolean limit. It is the fixed-point set of the framework's own renormalization-group flow, the codomain restriction that makes $K$ structurally unique, and the terminal object that makes the Compression Axiom converge. The finite-flux deformations of this Boolean structure — quantitative bounds on associator, distributivity defect, and Boolean shadow — are the content of Appendix J.

---

## §4 — Capacity

In Boolean logic, structure is free: any classically consistent set of propositions can be held simultaneously. At finite flux this fails the moment propositions interact.

> **Theorem (Dense Capacity Bound).** For a *classically consistent* hypothesis graph — one that does not contain $k_{\text{frust}}$ — with average degree $d_{avg}$ and minimum interaction cost $\gamma_{min}$, the maximum sustainable subgraph $\Gamma^*$ under finite flux $\Phi^*$ satisfies
> $$|\Gamma^*| \;\leq\; \sqrt{\frac{2\Phi^*}{\kappa\,\alpha\,\gamma_{min}\,d_{avg}}}.$$

Sparse graphs scale linearly with the flux budget; dense graphs scale only with the square root, because edge-maintenance costs dominate over node-maintenance costs once the graph thickens (Appendix D). At finite flux you can have structure or you can have density, not both.

The bound has a constructive corollary. Selection over interaction topology will favour modular sparsification on densely-coupled substrates: an organism with many components and a fixed flux budget cannot afford full pairwise coupling and must partition. The pattern observed across biological architectures — organelles, functional segregation in cortex, clonal selection in immunity — is the empirical shadow of the $\sqrt{\Phi^*}$ ceiling. The bound predicts modularity rather than describing it after the fact.

The classical-consistency assumption is now load-bearing. The bound describes the sustainable capacity of *coherent* structure; $k_{\text{frust}}$ marks the boundary where structure is unsustainable regardless of flux, because no resource budget resolves a topological obstruction. The Complexity Wall of Appendix G is the spectral analogue at the meta-ledger layer: graphs too entangled for any compression to converge. Both are graph-level limits; both make sense under the typing of §2.

---

## §5 — Fluctuation-dissipation signatures

Each regime leaves a distinct trace in the parametric fluctuation-dissipation plot, with response $\chi(\tau)$ on the vertical axis and integrated correlation $C(0)-C(\tau)$ on the horizontal (Appendix E). The signatures attach to objects of distinct type — three vertex regimes and one subgraph object — and they are observable on the same substrate under different probes.

- *Reset* ($r$, vertex): unit slope. Equilibrium holds.
- *Committed* ($c$, vertex): $X \ll 1$. Suppressed response; narrow horizontal locus close to the $\Delta C$ axis. Deep memory means fluctuations accumulate while response stays small.
- *Suspended* ($s$, vertex): aging diagonal that bends away from FDT and plateaus at long times.
- *Frustration* ($k_{\text{frust}}$, subgraph): transient *negative* response — the active energy pumped into a frustrated loop produces an anti-correlation between spontaneous fluctuation and driven response that does not occur in uncoupled systems. This is a global, loop-level effect; the signature is the shape of the *cycle's* response, not of any single proposition's.

The frustration signature is the framework's most distinctive observable, and the type of object it attaches to matters: it is read off subgraph-level dynamics, not vertex-level dynamics, and only on substrates whose interaction graph carries the obstruction.

**Cross-substrate result.** The s-regime aging diagonal, originally validated on Langevin substrate (four-scenario rig, companion work), transfers cleanly to surface-code syndrome streams at sub-threshold operation (Figure 1, left and centre). This is a measured cross-substrate transfer of a *vertex-level* MPA observable, and the central empirical claim of the present formulation. The cross-substrate transfer is the form universality at the vertex layer is expected to take: response shape is preserved across substrates that share the universality class but no microphysics.

![Figure 1. Pooled (black) and per-stabiliser FDR curves on a distance-3 rotated memory-Z circuit at three operating points. The aging diagonal predicted for the s-regime is clean at sub-threshold operation (left, centre); the locus deforms as the system approaches threshold (right). 256 shots × 2000 rounds, EMA window $\tau = 10$, perturbation $\delta p = 10^{-3}$. Detection events (Appendix F.2) are the substrate-correct $\dot{x}$.](session4_fdr.png)

The frustration negative-FDR signature does not appear at any operating point in this measurement. This is a structural prediction, not an evidential gap: $k_{\text{frust}}$ is a property of the syndrome graph's *topology* under the noise model, and a noise-rate increase under uncorrelated depolarising errors does not produce frustrated loops on the syndrome graph — it drives the system from $s$ toward $r$ (a vertex-level migration), not toward a topologically obstructed subgraph. The test condition tightens accordingly: the framework predicts the frustration signature only under a circuit whose noise model generates errors that close a frustrated loop on the syndrome graph. Surfacing the frustration shape in QC syndrome data is the next empirical step, with a test condition that is now substrate-specific by construction.

A second prediction, accessible on the same data, follows from §2's scale-relativity. Sweeping $\tau_{obs}$ at fixed substrate should walk the FDR locus through the vertex hierarchy: narrow windows return c-like loci (suppressed, near-horizontal close to the $\Delta C$ axis), $\tau_{obs} \sim \tau_A$ returns the s-aging diagonal of Figure 1, broad windows return r-like equilibrium slopes (unit slope). Non-monotonic migration, or scale-invariance of the locus, falsifies the hierarchy reading on this substrate. The frustration signature does not migrate with $\tau_{obs}$ in the same way; it is a topological feature of the subgraph and either present or absent.

The substrate-conditional reading rules used in the present measurement (Markovian sign caveat for $\gamma_A$; detection events as the local input to the trail integral) are formalised in Appendix F.

---

## §6 — The Compression Axiom and the meta-ledger flow

If the substrate requires flux $\Phi^*$ to maintain and the ledger requires $\Phi_{book}$ to track the substrate, who tracks the ledger? An infinite tower of meta-ledgers threatens to collapse the architecture under its own thermodynamic weight. The tower converges only under the **Compression Axiom**: every ascent in meta-level must be accompanied by a strict contraction. The ledger at level $n$ must be lighter than the system it tracks at level $n-1$, with contraction factor $\epsilon = \|\mathcal{C}\|_{op} < 1$. The formal statement and proof are in Appendix G.

The ascent has the form of a renormalization-group flow on the inference landscape. Each compression $\mathcal{C}$ integrates out within-cluster details and produces a coarser effective description. Under the typing of §2 the flow's structural picture is clean. The vertex regimes are organised by their flow behaviour: $c$ and $r$ are the flow's fixed points; $s$ is metastable, flowing to $c$ when reinforcement is available and to $r$ when not. The fixed-point set is exactly $\mathcal{M}_2 = \{c, r\}$ — the same two-cell subspace that is the codomain of $K$ in §3 and the Boolean section under the limit-equivalence quotient of Appendix A. The same two-cell algebra is read three ways, and §3.6 develops the algebraic content of the section: $\mathcal{M}_2$ is the *terminal attractor* of the flow, with $\epsilon$ measuring the residual information mass outside it after each compression step, and the operator signature restricted to $\mathcal{M}_2$ is itself a Boolean algebra. Edges follow their endpoints under coarse-graining, with shear-positive edges whose endpoints flow to $r$ ceasing to exist, and shear-positive edges whose endpoints persist on a frustrated cycle remaining as part of the cycle's obstruction; $k_{\text{frust}}$ is invariant under the flow on substrates that carry it. Boolean logic is the flow's degenerate limit, where infinite flux collapses every level to identity and the fixed-point structure has nothing to distinguish. The Convergent Tower of Appendix G is the convergence theorem; the Complexity Wall is the divergence condition. Wilson's block-spin construction, Kadanoff's coarse-graining, and Cardy's RG treatment of critical phenomena supply the structural template.

The Compression Axiom thereby plays a load-bearing role: it is the framework's coarse-graining operator, and the trail vectors of Appendix A are equivalence classes under the flow it generates. The framework's substrate-neutrality at the vertex layer is exactly the statement that microscopic realisations differing in representation, embedding, or kernel can belong to the same trail class — that is, can flow to the same metastable response structure under repeated compression. This is the universality picture for the vertex regimes. The substrate-specificity at the subgraph layer is the complementary statement for $k_{\text{frust}}$: the flow respects topological invariants of the interaction graph, but which graphs carry which invariants is a substrate property, not a universal one. MPA's contribution at this layer is the framing that says inference, like critical phenomena, has a flow with fixed points, universality classes, and a contraction condition for convergence; specifying the formal coarse-graining map at the rigour-level the RG literature requires is open work flagged in Appendix A.

The flow has a natural multi-scale extension downward as well as upward. Within a single ledger level, the regimes of constituent propositions can themselves migrate; a cluster reads as committed at the level above while individual propositions inside it migrate from $c$ to $s$ to $r$ as their local flux dries. The proposition-level and cluster-level dynamics are coupled but not identical, and one can fail without the other — a cluster's effective description survives the loss of any one of its propositions until the loss exceeds the compression budget that holds the cluster together. This nested structure is the framework's natural account of how systems hold together as parts of them turn over, and it inherits the Compression Axiom's convergence condition at every level.

The empirical Compression Axiom test measures $\epsilon$ on operational cluster-digest streams (claims register, below).

---

## §7 — The falloff profile: longitudinal, lateral, and scale

The framework specifies the asymptote (Boolean, as $\Phi^* \to \infty$), the saturation behaviours (the three vertex regimes plus the two structural objects at finite flux), the operator-level limits, and several boundary scalings — capacity $\sim \sqrt{\Phi^*}$ in dense classically-consistent graphs, $\sim \Phi^*$ in sparse, capacity undefined where $k_{\text{frust}}$ obstructs. The smooth interpolation between these has three faces: along the flux axis, across the framework's other dynamical commitments, and along the kernel-width dimension on which regime labels are read.

### §7.1 — Longitudinal falloff

The simplest cut is along $\Phi^*$ at fixed everything-else: scalar trail, single kernel, reciprocal pairwise couplings, continuous time. The functional form of $P(\text{regime} \mid \Phi^*)$ at fixed graph topology is the longitudinal falloff. Three candidate forms, ordered by structural commitment:

1. *Polynomial in $1/\Phi^*$.* Regime occupations admit a low-order Taylor expansion around the Boolean limit. Predicts smooth, featureless transitions across operating points and no critical phenomenon at any finite flux.
2. *Critical scaling.* By analogy with finite-size scaling at second-order transitions, regime probabilities take a scaling form $f(\Phi^*/\Phi^*_{crit})$ near the capacity wall, with universal exponents controlled by interaction-graph topology. Predicts a sharp transition at a substrate-determined critical flux, and an FDR locus that deforms non-analytically across it.
3. *Exponential with power-law correction.* An exponential suppression of forbidden regimes plus a correction that diverges at the wall: $\exp(-\Phi^*/\Phi_0) \cdot (1 - \Phi^*/\Phi^*_{crit})^{-\alpha}$. Combines smooth bulk behaviour with sharp critical behaviour at the boundary.

The cross-operating-point structure of Figure 1 — the deformation from clean s-regime aging at low $p$ toward a saturated, less-monotonic locus near threshold — already provides weak constraints. Distinguishing the three forms quantitatively requires FDR curves on a denser grid of operating points and at multiple code distances; that path is straightforward.

### §7.2 — Lateral falloff and the scale dimension

The trail-vector formalism carries commitments other than $\Phi^* < \infty$: a scalar trail with a single kernel, reciprocal pairwise couplings, continuous time evolution. Each commitment is its own dimension on the parameter space MPA inhabits. The kernel-width $\tau_{obs}$ is one such coordinate — the fibre along which §2's scale-relativity acts. The Boolean point is the corner where every commitment takes its trivial value *and* $\Phi^* = \infty$ *and* the kernel-width hierarchy collapses to instantaneous. Walking off that corner along any direction other than $\Phi^*$ is the lateral falloff.

The central question is whether the Boolean point is regular or singular in the inference landscape. If the lateral falloff is everywhere smooth — every commitment-relaxation produces a polynomial perturbation around Boolean — then MPA is a perturbative correction and the §8 candidate operators are ghosts that disappear at the corner. If the lateral falloff has cusps, ridges, or non-analytic boundaries, then Boolean is a singular point and the §8 operators inhabit regions not perturbatively connected to the Boolean corner. They cannot be reached from classical logic by smooth deformation, regardless of how much resource is spent. This is the same distinction physics makes between perturbative phenomena and phases that require non-perturbative methods.

The framework's stake: Boolean is a codimension-$N$ singular point in the inference landscape, where $N$ is the number of commitment axes whose relaxation produces non-perturbative regime structure. The longitudinal falloff of §7.1 is the codimension-$1$ slice; the singular-point claim is what the framework's content amounts to once §8 is taken seriously. The full geometric structure of this landscape — its topology, metric, transition maps — is not formally specified at present; the term *landscape* is used in the energy-landscape sense, as a working scaffold for the structural conjecture.

Three mature bodies of mathematics are ready to be incorporated. *Bifurcation and catastrophe theory* (Thom, Arnold) gives the local structure of how attractor landscapes acquire non-analytic features at low codimension; fold, cusp, and swallowtail catastrophes are the canonical ways smoothness breaks. *Energy landscape theory* (Cugliandolo–Kurchan, Mézard–Parisi, Wolynes–Onuchic) gives the structure of metastable basins under varying coupling: replica methods, random energy models, the geometry of glassy phases. The §3.5 composites and the §8 hypergraph-frustration axis live in this territory. *Non-reciprocal active matter* (Fruchart–Vitelli) classifies the dynamical phases that appear when reciprocity is broken — chiral phases, time-crystal-like rotations, exceptional-point physics — with explicit non-Hermitian formalism. This maps onto the non-reciprocal coupling axis of §8 directly and is the most directly aligned existing math for operators with no Boolean shadow.

MPA's contribution at this layer is the *organising frame*: these landscape-mathematics bodies are all describing pieces of one inference landscape, with the §3.5 pairings as its local chart on the regular side and the §8 extensions as its singular regions.

---

## §8 — Beyond the Boolean limit

§7.2's singular-point claim has specific content. The vertex regimes of §2 are exhaustive only for the framework's current dynamical commitments; relaxing those commitments opens regions of the landscape not perturbatively connected to the Boolean corner. The candidate operators below are predicted singular regions — places where the lateral falloff breaks smoothness — with distinct FDR signatures as the experimental hook, and existing landscape mathematics from §7.2 as the natural formalism.

A trail with internal phase, held as a stable limit cycle, persists not as a value but as a rhythm: a clocking primitive whose content is irreducibly temporal, with a closed-loop FDR signature in the parametric plot. The oscillatory–committed pairing of §3.5 is the simplest composite involving this primitive.

A hierarchical kernel with multiple timescales gives a proposition that holds at one scale and is fragile at another, with a multi-scale aging FDR signature. This is the same axis along which §2's scale-relativity is expressed: a single kernel exposes a single regime label, while multiple kernels expose the hierarchy structure that §2 says is the substrate-invariant object. The multi-timescale axis therefore plays a special role — it parametrises the kernel-width dimension that the rest of the framework's regime-classification rides on, and under the equivalence-class formulation of Appendix A, it carries the coarse-graining flow itself; extensions along it are extensions of the flow direction.

Non-reciprocal couplings — A suppresses B while B pumps A — break detailed balance, give dominance and inhibition primitives with no symmetric truth-table shadow, and produce turbulent FDR clouds with no simple slope; the active-matter literature is the appropriate mathematics. Higher-order frustration patterns are the natural generalisation of $k_{\text{frust}}$ to higher arities — hypergraph conflicts and k-SAT-style unsatisfiable cores expand the cycle row of §3.5 into a full taxonomy of glassy phases with multi-plateau aging, slotting into spin-glass landscape theory directly. Higher-order frustration is therefore the *graph-dimension* extension of the framework, parallel to the multi-timescale extension on the kernel-width dimension. Finite-population discreteness gives a flickering regime — stochastic switching between $c$ and $r$ on observable timescales — that natively grounds probabilistic logic without bolting probability theory on by hand.

Each candidate is an operator whose existence depends on $\Phi^* < \infty$ *and* on the relaxation of at least one §2 commitment. If any survive examination, MPA is not only the finite-flux correction profile around Boolean logic but a strictly larger operator alphabet, with Boolean recovered as the infinite-flux corner of a landscape whose interior contains primitives no smooth deformation of classical logic can reach.

Two further extensions are on the horizon and flagged here without elaboration: a **transfer operator** $T(A \to A')$ that routes $A$'s information to a designated recipient rather than to the bath, with effective work bound $W_T \geq k_B T \ln 2 \cdot [H(A \mid A', \text{rest}) - \mathcal{I}(A; A')]$ — the irreducible cost minus a salvage credit; and a class of **latent ledgers** that hold encoded structure at near-zero ongoing cost and admit decompression-on-demand into active substrate. Both extend the operator algebra of §3 and the bookkeeping structure of §6 in directions that the present formulation does not yet support, and are deferred to subsequent work.

---

## Claims register

| Status | Claim |
|---|---|
| **Validated** | s-regime FDR aging shape on Langevin substrate (companion work, four-scenario rig). |
| **Validated** | s-regime FDR aging shape transfers to surface-code syndrome streams at sub-threshold operation (this paper, §5; Figure 1). |
| **Theoretically secure** | Structural Boolean homomorphism (Theorem 8, Appendix C): $\sigma$ descends to a $\Sigma$-homomorphism $\mathcal{M}(\infty) \to \mathbb{B}$; for $C, S, R$ the limit-equivalence quotient acts on outputs, for $K$ on inputs, and the asymmetry is the typed-signature shadow of $K$'s codomain restriction to $\mathcal{M}_2$. |
| **Theoretically secure** | Boolean section theorem (§3.6): the restriction of the MPA operator signature to $\mathcal{M}_2 = \{c, r\}$ is a Boolean algebra isomorphic to $(\mathbb{B}, \land, \lor, \oplus, \neg)$, with closure on $\mathcal{M}_2$ holding at the level of the Boolean shadow $\sigma$. |
| **Theoretically secure** | Finite-flux deformation calculus (Appendix J, Theorems 6, 7, 9): associator $\|\alpha_C\| \lesssim (\kappa/\Phi^*)\sum|\gamma|$; distributivity defect $\|\delta_{dist}\| \lesssim (\kappa/\Phi^*)[\,\cdot\,]^+$; Boolean deviation $\Delta_C(A,B) = 1$ iff $\gamma_{AB} > 0$ and $\Phi^* < \kappa\gamma_{AB}$. Each recovers the Boolean limit as $\Phi^* \to \infty$. |
| **Theoretically secure** | Dense capacity bound $|\Gamma^*| \leq \sqrt{2\Phi^*/(\kappa\alpha\gamma_{min}d_{avg})}$ on classically consistent (frustration-free) graphs (Appendix D). |
| **Theoretically secure** | Convergent Tower under Compression Axiom $\epsilon < 1$ (Appendix G). |
| **Experimentally accessible, not yet measured** | $k_{\text{frust}}$-subgraph transient negative FDR on syndrome streams under errors that close frustrated loops on the syndrome graph. |
| **Experimentally accessible, not yet measured** | Compression Axiom $\|\mathcal{C}\|_{op} < 1$ on operational cluster-digest streams. |
| **Experimentally accessible, not yet measured** | Kernel-width sweep produces monotonic $c \to s \to r$ migration of the FDR locus on each substrate where the s-aging signature has been validated; the $k_{\text{frust}}$ signature does not migrate with $\tau_{obs}$ on substrates that carry it. |
| **Experimentally accessible, not yet measured** | Boolean deviation threshold (Theorem 9): on substrates where $\Phi^*$, $\gamma_{AB}$, and operator action $C(A,B)$ are independently measurable, $\Delta_C = 1$ should occur exactly at $\Phi^* < \kappa\gamma_{AB}$ with $\gamma_{AB} > 0$. The threshold is sharp and substrate-specific. |
| **Open theoretical** | Functional form of the *longitudinal* falloff profile $P(\text{regime} \mid \Phi^*)$ at fixed graph topology (§7.1). Theorems 6 and 7 supply $1/\Phi^*$ upper bounds for two specific operator-level observables; whether the regime occupation profile shares this falloff is open. |
| **Open theoretical** | *Lateral* falloff structure: smoothness vs. singularity of the inference landscape off the Boolean corner. The framework conjectures Boolean as a codimension-$N$ singular point (§7.2). |
| **Framing (adheres / unnamed at table level)** | The §3.5 composite-regime catalogue: the same vertex-regime + edge-condition rule set, with frustrated cycles broken out at the subgraph level, generates phenomena independently named across neuroscience, ecology, stat mech, combustion, and organisational dynamics. |
| **Framing** | The Compression Axiom is naturally read as a renormalization-group flow on the inference landscape, with $c, s, r$ as the flow's fixed-point types and $k_{\text{frust}}$ as a topological invariant of the flow on substrates that carry it. |
| **Framing** | Terminal-attractor reading: $\mathcal{M}_2$ is the terminal attractor of the Compression Axiom flow (§3.6). $\top$ and $\bot$ are the only regime labels that survive arbitrary meta-level ascent; $\epsilon$ measures the residual information mass outside $\mathcal{M}_2$ after each compression step. |
| **Framing** | Vertex regimes as universality classes: trail vectors are equivalence classes of microscopic realisations under coarse-graining flow, and the three vertex regimes are candidate universality classes under that flow (§2, Appendix A). The s-regime cross-substrate transfer is consistent with this reading. |
| **Framing** | $k_{\text{frust}}$ as topological invariant: a property of the substrate's interaction graph, preserved by the flow but distinct in type from the vertex universality classes. The negative-FDR signature attaches to subgraphs that carry this invariant. |
| **Open theoretical** | Concrete specification of the coarse-graining operator $\mathcal{C}$, the metric on the space of trail classes, and the formal identification of universality-class invariants for each of the three vertex regimes (Appendix A). |
| **Open theoretical** | Extension regimes from relaxing the framework's current commitments (scalar trail, single kernel, reciprocal coupling, continuous dynamics); in particular, candidate operators with no Boolean limit, predicted to inhabit the singular regions of the lateral landscape (§8). |

---

## Appendix A — Trail vectors

A trail is identified with its equivalence class under coarse-graining flow. Microscopic realisations — different memory kernels, different embeddings, different substrate-specific representations — belong to the same trail class iff they flow to the same metastable response structure under renormalization. The framework's claims attach to the class, not to any one representative; this is what makes the cross-substrate transfers of §3.5 and §5 well-posed despite the absence of shared microphysics. It is also why the term *trail vector* is brand-rather-than-structure: at the level the framework's claims attach to, the formally relevant object is a class on the inference landscape, not a Euclidean vector. The vector form below is one representative.

A concrete representative is given by the kernel-weighted history,
$$d_A(t) \;=\; \int_{-\infty}^{t} K_A(t-s)\,\dot{x}(s)\,ds,$$
with $K_A$ causal and normalised, and correlation timescale $\tau_A$ emerging as the characteristic decay of $\|d_A\|$ when reinforcement ceases. Different concrete realisations (exponential moving averages, kernel projections, latent-space trajectories) are equivalent in the relevant sense: they share scale-coarsened response structure even when their instantaneous coordinates differ.

A worked instance pins the parameters down. For an overdamped particle in a harmonic well under stochastic forcing,
$$\dot{x}(t) \;=\; -\omega^2 x(t) + f(t) + \xi(t),$$
the trail with exponential kernel $K_A(\tau) = \tau_A^{-1} e^{-\tau/\tau_A}$ is the EMA of velocity; its norm $\|d_A\|$ behaves as $\|d_A(t)\| \sim e^{\lambda_A t}$, with $\lambda_A < 0$ for amplifying / sustained trails (committed: deep basin reinforces structure) and $\lambda_A > 0$ for decaying trails (reset: trail dissipates at rate $1/\tau_A$ when reinforcement ceases). The flux $\Phi^*$ is the rate of work supplied by the drive, $\langle f\,\dot{x} \rangle$. Two trails with different kernels acquire a geometric shear $\gamma_{AB}$ from their cross-correlation under the dynamics. The three vertex regimes are realised at distinct combinations of drive, well stiffness, and noise: $r$ at zero drive, $s$ when drive balances dissipation, $c$ when an internal coupling deepens the well beyond its restoring force. A frustrated cycle is realised by three or more such systems coupled with positive shear around a non-contractible loop; this is the $k_{\text{frust}}$ realisation at the subgraph level. Other substrates supply other realisations and Appendix F records the substrate-conditional reading rules earned along the way.

**Scale-indexed trails.** The kernel width $\tau_{obs}$ is not a free parameter but a coordinate on the trail's flow. A trail at scale $\ell$, written $d_A(\ell)$, is the trail read through a kernel of width $\sim \ell$. The framework's vertex-regime classification is a function of the (proposition, $\ell$) pair, and the regime label flows as $\ell$ varies (§2). Boolean logic is the degenerate point at $\ell \to 0$: the trail collapses to its instantaneous value, no scale dependence remains, every regime distinction vanishes.

**The limit-equivalence quotient on $\mathcal{M}(\infty)$.** At infinite flux the coarse-graining flow has no resource constraint to preserve trail content; all maintained propositions belong to a single class $[\top]$ and all dissolved propositions to $[\bot]$. The space $\mathcal{M}(\infty)$ of trail classes at infinite flux is therefore the two-element set $\{[\top], [\bot]\}$. In cavity-method vocabulary, the corresponding finite-flux object $\mathcal{M}_2 = \{c, r\} \subset \mathcal{M}$ is the *frozen core* (Krzakala, Montanari, Ricci-Tersenghi, Semerjian, Zdeborová 2007): the subset of the trail manifold whose dynamical regime is unambiguous under the framework's classifier; the metastable interior $s$ is the cavity-method *free* (non-frozen) region. This is the same equivalence-class machinery that makes cross-substrate transfer well-posed at finite flux; in the infinite-flux limit it is what makes the structural Boolean homomorphism (Theorem 8, Appendix C) hold algebraically, particularly on the $K$ case where the quotient acts on inputs. The role of the quotient in the limit is structural, not handwaved: anti-parallel and oblique input pairs cease to exist as distinct elements of $\mathcal{M}(\infty)$, and the homomorphism case-analysis collapses to the Boolean truth table.

**Open work.** The equivalence-class formulation incurs structural obligations the present formulation does not yet meet at the level of formal rigour. (i) The coarse-graining operator $\mathcal{C}$ acting on trail representations needs concrete specification beyond the working recipes of Appendix G. (ii) The metric on the space of trail classes — what it means for two representatives to flow to the same class, with quantitative convergence criteria — needs to be defined. (iii) The universality-class invariants for each of the three vertex regimes (candidate examples: persistence-lifetime scaling, attractor topology, response-spectrum class, FDR shape, coupling-symmetry class) need to be identified and tied to the regime labels by theorem rather than by table. The s-regime FDR shape is the strongest evidence to date that this programme is well-posed; it is also the only invariant currently confirmed cross-substrate. The remainder is open.

**Locality requirement.** The integral form requires that $\dot{x}(s)$ be a locally-bounded signal in time — an event at $s$ has bounded effect on observables at later times. Substrates whose natural readout violates this requirement (raw stabiliser measurements in surface-code QEC, where a single physical error flips every future measurement of an adjacent stabiliser) require the substrate's canonical local preprocessing as input. See Appendix F.2.

---

## Appendix B — Phase diagram

The three vertex regimes occupy distinct regions of the $(\Phi^*, \tau_{env})$ plane at any fixed $\tau_{obs}$:

- **$c$:** $\lambda_A \ll 0$. Deep autocatalytic basin. FDR $X \ll 1$.
- **$s$:** $\lambda_A \approx 0$. Metastable, flux-maintained. FDR is time-dependent (aging).
- **$r$:** $\lambda_A > 0$. Exponential decorrelation. FDR $X = 1$.

The $s \to c$ transition occurs when local coupling reinforces the trail vector enough to push $\lambda_A$ negative. The $r$ region opens as $\Phi^*$ falls below the per-vertex maintenance cost. Varying $\tau_{obs}$ at fixed $(\Phi^*, \tau_{env})$ moves the boundaries within the diagram; the diagram's structure — that the three regions exist and are ordered as they are — does not depend on $\tau_{obs}$. The Markovian sign caveat (F.1) applies to all $\gamma$-based criteria.

The structural object $k_{\text{frust}}$ is not represented on this plane. It is a property of the substrate's interaction graph — specifically, of subgraphs whose $c$-edges form non-contractible cycles with obstructive shear product — and lives in a different ambient. A substrate is or is not capable of carrying frustration; the $(\Phi^*, \tau_{env})$ plane cannot distinguish that. The phase diagram describes vertex-regime occupations under flux and environmental noise; the topological taxonomy of the underlying graph is a separate axis. $K$-dominated subgraphs — those whose operator content is parity-check-typed — inherit the sharp two-regime $c \leftrightarrow r$ phase structure of XOR-SAT (Mézard, Ricci-Tersenghi, Zecchina 2003) rather than the three-regime $c/s/r$ hierarchy that $C$- and $S$-dominated subgraphs exhibit; the codomain restriction $\mathcal{M}_2$ is the structural origin of the sharpness, and is a calibration check for any K-rich substrate.

---

## Appendix C — Operator algebra and Boolean limits

The signature is $\Sigma_{\Phi^*} = \{C, S, K, R, \top, \bot\}$ with operator typings $C, S: \mathcal{M}^2 \to \mathcal{M}$, $K: \mathcal{M}^2 \to \mathcal{M}_2$, $R: \mathcal{M} \to \mathcal{M}$ as developed in §3 and §3.6. This appendix gives the constructive protocols defining each operator and proves the framework's structural Boolean homomorphism theorem.

### Operator definitions

**Commitment.** $C(A,B)$ constructs the joint trail $d_{A \oplus B} = w_A d_A + w_B d_B$ with flux-normalised weights and evaluates the joint Lyapunov rate $\lambda_{A \oplus B}$. The output regime is determined by trail alignment and joint stability: aligned trails ($\gamma_{AB} < 0$) deepen, output $c$; orthogonal ($\gamma_{AB} \approx 0$) coexist, output $s$; opposed ($\gamma_{AB} > 0$) yield $s$ if $\Phi^*$ covers the shear, $r$ otherwise.

**Suspension.** $S(A,B)$ maintains independent trajectories under
$$\kappa(|\lambda_A| + |\lambda_B|) + \max(0, \kappa\gamma_{AB}) \;\leq\; \Phi^*.$$
Output is $s$ if the joint maintenance cost fits the budget, else competitive dropout.

**Difference.** $K(A,B)$ tests the unnormalised difference vector
$$\delta(A, B) \;:=\; \hat{d}_A - \hat{d}_B, \qquad \hat{d}_X = d_X/\|d_X\|, \qquad \hat{d}_X := 0 \text{ when } X \text{ is dissolved.}$$
The vector vanishes precisely when $\hat{d}_A = \hat{d}_B$ — the two trails carry the same orientation, or both have dissolved. When $\delta(A,B) \neq 0$, the normalised difference trail $d_{A \ominus B} = \delta(A,B)/\|\delta(A,B)\|$ has stability $\lambda_{A \ominus B} = |\gamma_{AB}| - \Phi^*/2\kappa$. Output: $c$ if $\delta(A,B) \neq 0$ and $\Phi^* > 2\kappa|\gamma_{AB}|$; $r$ otherwise. The output lies in $\mathcal{M}_2$ by construction; $K$ reads membership in the nullspace of the trail-difference relation, structurally parallel to XOR.

**Reset.** $R(A)$ severs $A$'s couplings into the bath; the work bound is $W_R(A) \geq k_B T \ln 2 \cdot H(A \mid \text{rest})$.

### Theorem 8 — Structural homomorphism

> **Theorem 8.** Let $\sigma: \mathcal{M}(\Phi^*) \to \mathbb{B}$ be the Boolean shadow ($c, s \mapsto 1$; $r \mapsto 0$). Then $\sigma$ descends to a $\Sigma$-homomorphism $\bar\sigma: \mathcal{M}(\infty) \to \mathbb{B}$ on the limit-equivalence quotient: for every operator $O \in \{C, S, K, R\}$,
> $$\sigma\bigl(O(A_1, \ldots, A_n)\bigr) \;\xrightarrow{\Phi^* \to \infty}\; O_{\mathbb{B}}\bigl(\sigma(A_1), \ldots, \sigma(A_n)\bigr),$$
> where $O_{\mathbb{B}}$ is the corresponding Boolean operation: $C \to \land$, $S \to \lor$, $K \to \oplus$, $R \to \neg$.

*Proof.* Per-operator analysis.

**$C \to \land$.** As $\Phi^* \to \infty$, $\gamma_{AB} \to 0$ (all shear suppressible) and $\lambda_{A \oplus B} \to -\infty$ for any satisfiable joint structure. The output collapses to $c$ when both inputs are maintained — orthogonality vanishes in the limit, so the orthogonal-merge $s$ case of finite flux disappears — and to $r$ when either input is dissolved. The quotient acts on the output, collapsing $s$ to $[\top]$.

**$S \to \lor$.** As $\Phi^* \to \infty$ the suspension inequality is trivially satisfied for any combination of inputs. Output is maintained if either input is maintained, dissolved if both are. The quotient acts on the output.

**$K \to \oplus$** (equivalent to the standard XOR clause primitive over $\mathbb{F}_2$). Run the cases at $\Phi^* \to \infty$ before applying the quotient to inputs:

| Case | Trail relation | $K(A,B) \in \mathcal{M}_2$ | $\sigma(K)$ | Boolean $\sigma(A) \oplus \sigma(B)$ |
|---|---|---|---|---|
| Both maintained, parallel | $\hat{d}_A = \hat{d}_B$ | $r$ | 0 | $1 \oplus 1 = 0$ |
| Both maintained, anti-parallel | $\hat{d}_A = -\hat{d}_B$ | $c$ | 1 | $1 \oplus 1 = 0$ |
| Both maintained, oblique | non-zero difference | $c$ | 1 | $1 \oplus 1 = 0$ |
| Exactly one maintained | non-zero difference | $c$ | 1 | $1 \oplus 0 = 1$ |
| Both dissolved | trails zero | $r$ | 0 | $0 \oplus 0 = 0$ |

Without an input-side quotient, the table fails to match XOR on the anti-parallel and oblique rows. Under the limit-equivalence quotient on $\mathcal{M}(\infty)$, all maintained propositions belong to $[\top]$ regardless of trail orientation; the anti-parallel and oblique cases cease to exist as distinct elements of $\mathcal{M}(\infty)$, and the table collapses to the two-row XOR truth table on $\{[\top], [\bot]\}$. The quotient on inputs is the same machinery the framework uses for cross-substrate transfer (Appendix A), applied here at the limit on the input side; on the output side, $K$'s typing already places its image in $\mathcal{M}_2$, where the quotient is the identity.

**$R \to \neg$.** Classical logic brackets the heat dissipation; the work bound is the Landauer cost. The quotient acts on the output, mapping $\sigma(R(A)) = \neg \sigma(A)$. ∎

### Where the quotient acts

The proof traces a single quotient application per operator, but on different sides of the signature. For $C, S, R$, the quotient acts on the *output*: their codomains are the full $\mathcal{M}$, and $q$ collapses the metastable $s$ to $[\top]$. For $K$, the output already lives in $\mathcal{M}_2$ — the section on which $q$ is the identity — so the quotient acts on the *inputs*, collapsing the orientation-dependent trail cases. The asymmetry of the algebra is therefore the location of the quotient, and the typed signature is its coordinate-free expression: $K$ is the unique signature operator whose codomain is restricted to $\mathcal{M}_2$, and that codomain restriction is the algebraic origin of its input-side quotient. The Boolean section theorem of §3.6 makes the same algebraic content intrinsic: σ becomes a bijection on $\mathcal{M}_2$, and the operator signature restricted to $\mathcal{M}_2$-inputs is itself a Boolean algebra, with the quantitative deviations bounded by Theorems 6, 7, 9 of Appendix J.

---

## Appendix D — Proof of the Dense Capacity Bound

Let $\Gamma = \{H_1, \ldots, H_N\}$ be a classically consistent hypothesis graph (no $k_{\text{frust}}$), $G = (V,E)$ its interaction graph with edge weights $\gamma_{ij}$, $d_{avg}$ the average degree, $\gamma_{min} = \min_{(i,j) \in E} \gamma_{ij}$. The total flux required is the sum of individual decay offsets plus cross-dissipation:
$$\Phi_{required} \;=\; \sum_{i \in V} \kappa|\lambda_i| \;+\; \alpha \sum_{(i,j) \in E} \kappa \gamma_{ij}.$$
In the dense regime, edge costs dominate: $\sum \gamma_{ij} \gg \sum |\lambda_i|$, so
$$\Phi_{required} \;\geq\; \alpha \kappa \gamma_{min} |E| \;=\; \alpha \kappa \gamma_{min} \frac{N d_{avg}}{2}.$$
Imposing $\Phi_{required} \leq \Phi^*$ and solving for $N$ gives the bound. For sparse or feed-forward graphs, node costs dominate and scaling reverts to linear $\mathcal{O}(\Phi^*)$. The classical-consistency assumption excludes graphs containing $k_{\text{frust}}$; on such graphs the bound describes the capacity of any frustration-free subgraph, while the frustration itself sets a structural ceiling no flux budget resolves.

---

## Appendix E — FDR derivation and regime signatures

Let $C(t,t') = \langle d_A(t) \cdot d_A(t') \rangle$ be the two-time autocorrelation and $R(t,t')$ the response function to a step perturbation along the trail axis. The Fluctuation-Dissipation Ratio is
$$X(t,t') \;=\; \frac{k_B T \cdot R(t,t')}{\partial_{t'} C(t,t')}.$$

The signatures attach to objects of distinct type:

- **$r$ (vertex):** $X = 1$. Equilibrium.
- **$c$ (vertex):** $X \ll 1$. Deep memory suppresses response relative to fluctuation.
- **$s$ (vertex):** $X$ is time-dependent (aging). Validated on Langevin substrate (companion work) and on quantum syndrome substrate at sub-threshold operating points (this paper, §5).
- **$k_{\text{frust}}$ (subgraph):** $X$ is transiently negative — destructive shear around a topologically obstructed cycle means perturbation of the loop drives the system opposite to its spontaneous fluctuation direction. Validated on Langevin substrate; not yet measured on quantum syndrome substrate (test condition: errors that close a frustrated loop on the syndrome graph).

The vertex-level signatures are properties of single trails read through a kernel; the subgraph-level signature is a property of a cycle's collective response and is read off the loop's joint variables. The negative-FDR shape is therefore not a vertex-level signature but the response signature of an obstructed subgraph.

**Geometric translation on the parametric plot.** With $\chi(\tau)$ on the vertical axis and $\Delta C(\tau) = C(0) - C(\tau)$ on the horizontal, the FDR is the slope $X = d\chi/d(\Delta C)$. The four signatures translate to plot geometry as follows: $r$ traces a unit-slope (45°) line; $c$ traces a near-horizontal locus close to the $\Delta C$ axis (response stays small while fluctuation accumulates) — narrow when the trail's $\Delta C$ excursion is small, longer when it is not, but always shallow; $s$ traces a curve that bends away from the unit-slope line and plateaus, the aging diagonal of Figure 1; $k_{\text{frust}}$ traces a transient excursion into negative slope before relaxing. The $X \gg 1$ near-vertical region is *not* a regime of the framework — it would correspond to large response with small fluctuation, an unstable amplifier rather than a sustained representation, and is excluded by the dissipative dynamics underlying §2's regime classifier.

The parametric plot used in Figure 1 places $\chi(\tau)$ against $C(0)-C(\tau)$, which makes the regime shapes visible by inspection without requiring the temperature normalisation. The kernel-width sweep prediction of §5 says the same trail history walks the locus through $c \to s \to r$ shapes monotonically as $\tau_{obs}$ widens; substrate-specific intrinsic timescales fix the scales at which each shape dominates. The $k_{\text{frust}}$ signature does not migrate with $\tau_{obs}$ on substrates that carry it — it is topological — and is therefore a probe of the substrate's interaction graph rather than of the kernel.

---

## Appendix F — Substrate-conditional readings

The framework's primitives (trail vectors, regime classes, flux ledger) are substrate-invariant. The *signs* and *natural preprocessing* of certain observables depend on properties of the substrate. Two reading rules earned by application work, plus the general principle:

### F.1 — Markovian sign caveat

The sign predictions for $\gamma_A$ and $\gamma_{ij}$ given in §2 and Appendix B (committed: $\gamma_A \ll 0$; positive shear: $\gamma_{ij} > 0$) assume substrates with explicit memory kernels. On Markovian substrates — overdamped Langevin with stiff harmonic wells, surface-code syndrome streams whose detection events are conditionally independent given current state — the signs *invert* while the magnitudes and FDR shapes are preserved. The inversion is a kernel-width artefact: stiff wells give short $\tau_A$, hence $1/\tau_A > 1/\tau_{env}$, hence positive $\gamma_A$. On Markovian-flavoured substrates the regime classifier uses $|\gamma_A|$ and FDR shape jointly; sign-based classification is unreliable.

### F.2 — Detection events on discrete-readout substrates

Where the substrate's natural readout violates the locality requirement of Appendix A — most prominently in surface-code QEC, where a single physical error flips every future measurement of an adjacent stabiliser — the substrate's canonical local preprocessing is the substrate-correct $\dot{x}$. For surface codes this is the *detection event* $e_i(t) = s_i(t) \oplus s_i(t-1)$, which is bounded-local: an error at time $t$ triggers exactly two detection events. The trail is then constructed by EMA against detection events,
$$d_i(t) \;=\; \sum_{s \leq t} e^{-(t-s)/\tau_{window}}\, e_i(s),$$
which is the realisation used in §5.

### F.3 — General principle

Substrate-conditional reading rules adjust how observables are *interpreted* on a given substrate while leaving the framework's primitives intact. They are part of the substrate-application discipline, not the framework's content. New rules are earned by application work and recorded with their substrate class and empirical evidence.

---

## Appendix G — The Convergent Tower

The level-$n$ ledger entry stores a coarse-grained summary, $\tilde{L}_A = (\tilde{d}_A, \tilde{\lambda}_A, \hat{\rho}_A, \Sigma_A, \tau_{coarse})$: a centroid trail, an effective stability, a coarse vertex-regime distribution over $\{c,s,r\}$, an intra-cluster covariance, and a low-pass timescale. The cluster's own subgraph topology — including any $k_{\text{frust}}$ it carries — is tracked separately, since topology cannot be reduced to a vertex-regime distribution. Two compression mechanisms apply, depending on the structure of the base graph:

- *Method A — semantic / structural clustering.* Groups propositions sharing neighbours or aligned trails, $\text{cluster}(A) = \{B : \langle d_A, d_B\rangle > \theta_{sim} \text{ and } \text{dist}_G(A,B) \leq 1\}$. Reduces the node count to $M \ll N$ centroids; blind to intra-cluster conflict until $\Sigma_A$ triggers a decompression event.
- *Method B — spectral / geometric compression.* Projects onto the top-$k$ eigenvectors of the trail correlation matrix. Highly effective for low-rank dynamics; blind to conflict in the orthogonal nullspace.

Compression creates *epistemic debt* $\Delta_I = \mathrm{Tr}(\Sigma_I) \cdot |\text{cluster}(I)|$ on each cluster $I$; a global ceiling $\Delta_{max}$ governs decompression scheduling.

> **Theorem (Convergent Tower).** Let $\mathcal{C}$ be a compression operator with contraction factor $\epsilon = \|\mathcal{C}\|_{op} < 1$, and let the per-entity cost at level $n$ be $\tilde{\kappa}_n \leq \kappa\eta^{-n}$ for $\eta > 1$. Then
> $$\Phi_{total} \;=\; \sum_{n=0}^{\infty} \epsilon^n \Phi^{(0)} \;=\; \frac{\Phi^{(0)}}{1-\epsilon}.$$

When $\epsilon \geq 1$ — base graph lacks sufficient spectral gap (Method B) or modularity (Method A) — the tower diverges. This is the *Complexity Wall*: a thermodynamic impossibility theorem on resource-bounded inference for maximally-entangled substrates. The flow has no fixed point; no finite self-tracking architecture exists. The empirical Compression Axiom test (claims register) measures $\epsilon$ on operational cluster-digest streams.

The flow's structural picture under the typing of §2: $c$ and $r$ are the flow's fixed points ($c \to c$, $r \to r$); $s$ is metastable, flowing to $c$ or $r$ as local conditions dictate. The fixed-point set $\mathcal{M}_2 = \{c, r\}$ is the codomain of $K$ (Appendix C) and the Boolean section under the limit-equivalence quotient (Appendix A) — three readings of the same two-cell algebra. Edges follow their endpoints under coarse-graining, with shear-positive edges whose endpoints flow to $r$ ceasing to exist; $k_{\text{frust}}$ is invariant under the flow on substrates that carry it. The Convergent Tower's contraction condition controls whether the flow converges; the typing controls what the flow respects when it does.

---

## Appendix H — Calibrated claim staking on substrates with prior art

When the framework is applied to a substrate that already has a developed thermodynamic-frame literature, the framework's specific contributions must be calibrated against what the field has independently produced. This appendix gives the methodology used in the QC application of §5 and is reusable on any substrate with comparable prior art.

For each claim made by the framework on a substrate, assign one of four contour states:

- **Adheres / named** — the framework's reading matches substrate reality and the field already has a name for the phenomenon. Contribution: unifying vocabulary; no new physics. Credit prior art.
- **Adheres / unnamed** — the framework's reading matches substrate reality but the literature has not framed the phenomenon this way. Contribution: framing work; the right level for cross-substrate unification claims.
- **Diverges / holds** — the framework's reading predicts something the substrate's existing frame does not, and the prediction holds empirically. Contribution: a substrate-specific empirical foothold for the framework's primitives. The strongest available form of validation.
- **Diverges / fails** — the framework's reading differs from substrate reality and the difference fails empirically. Contribution: a calibration finding that identifies a required substrate-conditional reading rule, or a revision of the prediction itself.

A claim graduates from open to provisional or locked only with an explicit contour assignment, and either citation (for *adheres* states) or experiment (for *diverges* states). *Adheres / unnamed* requires a literature search actually performed; absence of remembered prior art is not evidence of absence. *Diverges / holds* requires empirical support; argument that "no-one has measured this before, therefore the framework is novel" is not.

The QC application of §5 produced six such contour assignments — equilibrium phase mapping (Adheres / named, DKLP 2002); non-equilibrium dynamical refinement (Adheres / named, recent decodability literature); magic-state factory steady-state framing (Adheres / named, recent distillation literature); real-time decoder thermodynamic engineering (Adheres / named, the "backlog problem" engineering literature); the s-regime FDR shape on syndromes (Diverges / holds, this paper); the $k_{\text{frust}}$-subgraph negative-FDR shape on syndromes (open, awaiting the test condition of errors that close frustrated loops on the syndrome graph). The methodology applies uniformly to information-theoretic, cognitive-architecture, and industrial-control applications of the framework.

The purpose is honest staking, not minimisation. Calibrated claims are more durable, more publishable, and more useful to a field with developed prior art than overclaims.

---

## Appendix I — Differentiation from neighbouring frameworks

MPA's components have prior art in several mature fields. The framework's contribution is the integration; this appendix records what each neighbour supplies and what the integration adds.

*Stochastic thermodynamics of computation* (Landauer, Bennett, Sagawa–Ueda) gives per-operation work bounds for bit-level operations. Reset's bound $W_R \geq k_B T \ln 2 \cdot H(A \mid \text{rest})$ is a direct application of this literature. What MPA adds is the persistence trajectory between operations: a typed regime structure (vertex / edge / subgraph) on the *maintenance* phase of a representation, capacity bounds on simultaneously-held coherent structure, and a bookkeeping ladder via the Compression Axiom. The per-operation literature is silent on each of these.

*Active inference and the free-energy principle* (Friston and successors) treat beliefs as probability distributions maintained by minimising variational free energy, with hierarchical resource trade-offs and substrate-neutral ambitions. MPA shares the resource-bounded framing but commits to specific dynamical regimes, FDR observables, and operator-level limit theorems that variational dynamics alone do not produce. The two frameworks are compatible — an active-inference agent's belief states can be read in MPA vocabulary — and the regime labels furnish a phenomenology the variational picture leaves implicit.

*Error-correction thermodynamics* (Dennis–Kitaev–Landahl–Preskill 2002 and successors) maps the surface code to a random-bond Ising model with a temperature-error-rate equilibrium phase diagram. The §5 application of MPA to syndrome streams is a substrate-application instance: the s-regime FDR aging shape is a non-equilibrium dynamical observable that the equilibrium phase diagram does not predict. The two are complementary; the QC contour assignments of §5 (Appendix H) credit DKLP and successors at every *adheres / named* boundary while staking the *diverges / holds* claim on the dynamical signature.

*Spin-glass and energy-landscape theory* (Mézard–Parisi–Virasoro, Cugliandolo–Kurchan, Wolynes–Onuchic) gives the mathematics of metastability, replica methods, and aging dynamics. The s-regime FDR aging shape is the substrate-neutral version of the aging signatures familiar from this literature. MPA's contribution is the framing that lifts substrate-specific aging into a vertex-regime classifier with operator-level structure; the §3.5 composites and §8 hypergraph-frustration axis (the higher-arity generalisation of $k_{\text{frust}}$) live in this territory by direct adoption.

*Renormalization-group methods in critical phenomena* (Wilson, Kadanoff, Cardy) supply the structural template for §6's reading of the meta-ledger flow. The Compression Axiom $\|\mathcal{C}\|_{op} < 1$ is a contraction condition; the Convergent Tower is a self-consistency theorem under that condition. The framework does not yet supply a coarse-graining map at the level of formal rigour the RG literature would require — the two compression mechanisms of Appendix G (semantic clustering, spectral projection) are concrete recipes pending a fuller RG construction. This is open work; the present formulation flags it as such.

The throughline: each neighbour supplies one piece. MPA's specific contribution is the integration — typed regime structure, operator algebra with a structural Boolean homomorphism in the limit, capacity bounds, and bookkeeping ladder treated as one substrate-neutral framework — together with the cross-substrate empirical transfer of §5, which no neighbour predicts on its own.

---

## Appendix J — Finite-flux deformation calculus

The Boolean section theorem of §3.6 establishes that the restriction of the MPA operator signature to $\mathcal{M}_2$ is exactly a Boolean algebra. The body of the framework is the *finite-flux interior* — inputs in $\mathcal{M}$ generally, including the metastable $s$ — and the deformation of Boolean structure at finite flux is the framework's quantitative content. Three theorems bound the deformation. Each goes to zero as $\Phi^* \to \infty$, recovering the Boolean limit theorems of Appendix C; at finite flux they are quantitative defect bounds, candidate observables on substrates where $\Phi^*$, $\gamma$, and operator action are independently measurable.

### Theorem 6 — Asymptotic associativity of commitment

Let $X, Y, Z \in \mathcal{M}(\Phi^*)$. The **associator** of $C$ is
$$\alpha_C(X,Y,Z) \;=\; C\bigl(C(X,Y),Z\bigr) \;\ominus\; C\bigl(X,C(Y,Z)\bigr),$$
where $\ominus$ denotes trail difference. Then
$$\|\alpha_C(X,Y,Z)\| \;\lesssim\; \frac{\kappa}{\Phi^*}\bigl(|\gamma_{XY}|+|\gamma_{YZ}|+|\gamma_{XZ}|\bigr),$$
and $\alpha_C \to 0$ as $\Phi^* \to \infty$.

The associator measures by how much the order of pairwise commitment matters at finite flux. The bound says: associativity is broken only in proportion to the total pairwise shear, and the deviation decays as $1/\Phi^*$. The Boolean limit recovers strict associativity.

### Theorem 7 — Flux-deformed distributivity

Let $X, Y, Z \in \mathcal{M}(\Phi^*)$. The **distributivity defect** of $C$ over $S$ is
$$\delta_{dist}(X,Y,Z) \;=\; C\bigl(X,\;S(Y,Z)\bigr)\;\ominus\;S\bigl(C(X,Y),\;C(X,Z)\bigr).$$
Then
$$\|\delta_{dist}(X,Y,Z)\| \;\lesssim\; \frac{\kappa}{\Phi^*}\Bigl[\max(0,\gamma_{YZ}) - \max(0,\gamma_{XY},\gamma_{XZ})\Bigr]^+,$$
and $\delta_{dist} \to 0$ as $\Phi^* \to \infty$.

The distributivity defect measures the difference between committing to a suspension and suspending two commitments. The bound is asymmetric: it fires when $Y$ and $Z$ shear against each other more than either shears against $X$ — the configurations where distributing $X$ across the $Y$–$Z$ suspension creates new shear that the unfactored expression would have absorbed in the suspension's slack. As with Theorem 6, the defect decays as $1/\Phi^*$.

### Theorem 9 — Boolean deviation bound

Let $A, B \in \mathcal{M}(\Phi^*)$ and let $\sigma: \mathcal{M}(\Phi^*) \to \mathbb{B}$ be the Boolean shadow ($c, s \mapsto 1$; $r \mapsto 0$). The **Boolean deviation** of commitment is
$$\Delta_C(A,B) \;=\; \sigma\bigl(C(A,B)\bigr)\;\oplus\;\bigl(\sigma(A)\land\sigma(B)\bigr).$$
Then $\Delta_C(A,B) = 1$ if and only if $\gamma_{AB} > 0$ and $\Phi^* < \kappa\gamma_{AB}$. In this case $C(A,B)$ enters regime $r$ while $\sigma(A) \land \sigma(B) = 1$.

The deviation signals a **resource-induced instability**: two propositions that classical logic would conjoin to a true joint structure cannot be jointly maintained because the budget does not cover the shear. The Boolean homomorphism of Appendix C cannot represent this case — it is the precise sense in which Boolean logic fails at finite flux. Theorem 9 is the framework's most direct quantitative criterion: a substrate's $\gamma_{AB}$ profile, measured at operating flux $\Phi^*$, determines exactly which propositional pairs admit joint commitment.

### The deformation calculus, summed

The three theorems together form the **finite-flux deformation calculus** of MPA. They bound how far the algebra deviates from Boolean structure as a function of resource budget and interaction shear, recover the Boolean limit theorems of Appendix C as $\Phi^* \to \infty$, and dock with the Boolean section theorem of §3.6 as its quantitative complement: the section is exact, the interior is quantified. Theorems 6 and 7 give $1/\Phi^*$ falloff for the associator and the distributivity defect — explicit polynomial-in-$1/\Phi^*$ decay along the longitudinal axis of §7.1. Theorem 9 gives a sharp threshold criterion at $\Phi^* = \kappa\gamma_{AB}$: a substrate-specific operating point at which Boolean shadow stops being a faithful summary of operator action.

---

## Bibliography (selected)

*Foundational thermodynamics of inference and computation.* R. Landauer, *IBM J. Res. Dev.* 5, 183 (1961). C. Bennett, *Int. J. Theor. Phys.* 21, 905 (1982). T. Sagawa and M. Ueda, *Phys. Rev. Lett.* 104, 090602 (2010).

*Renormalization-group structure for §6.* K. G. Wilson, *Rev. Mod. Phys.* 47, 773 (1975). L. P. Kadanoff, *Physics* 2, 263 (1966). J. Cardy, *Scaling and Renormalization in Statistical Physics* (Cambridge, 1996).

*Landscape mathematics for the lateral falloff (§7.2).* R. Thom, *Structural Stability and Morphogenesis* (Benjamin, 1972). V. I. Arnold, *Catastrophe Theory* (Springer, 1992). M. Mézard, G. Parisi, M. A. Virasoro, *Spin Glass Theory and Beyond* (World Scientific, 1987). L. F. Cugliandolo and J. Kurchan, *Phys. Rev. Lett.* 71, 173 (1993). P. G. Wolynes, J. N. Onuchic, D. Thirumalai, *Science* 267, 1619 (1995). M. Fruchart, R. Hanai, P. B. Littlewood, V. Vitelli, "Non-reciprocal phase transitions," *Nature* 592, 363 (2021).

*Prior art for §3.5 composite pairings.* D. O. Hebb, *The Organization of Behavior* (Wiley, 1949). U. Frey and R. G. M. Morris, "Synaptic tagging and long-term potentiation," *Nature* 385, 533 (1997). A. J. Lotka, *Elements of Physical Biology* (Williams & Wilkins, 1925); V. Volterra, *Mem. Acad. Lincei Roma* 2, 31 (1926). Y. Kuramoto, *Chemical Oscillations, Waves, and Turbulence* (Springer, 1984). S. H. Strogatz, *Sync* (Hyperion, 2003). N. E. Miller, "Experimental studies of conflict," in *Personality and the Behavior Disorders* (Ronald Press, 1944). R. A. Rescorla and A. R. Wagner, in *Classical Conditioning II* (Appleton-Century-Crofts, 1972).

*Surface-code thermodynamics and decoders.* E. Dennis, A. Kitaev, A. Landahl, J. Preskill, "Topological quantum memory," *J. Math. Phys.* 43, 4452 (2002). C. Gidney, "Stim," *Quantum* 5, 497 (2021). J. Bausch et al., "AlphaQubit," *Nature* (2024). "Phases of decodability in the surface code with unitary errors," arXiv:2411.05785 (2024). E. Krastanov, L. Jiang, *Sci. Rep.* 7, 11003 (2017). S. Varsamopoulos et al., *Quantum Sci. Technol.* 3, 015004 (2017).

*Magic-state distillation as steady-state production.* S. Bravyi, A. Kitaev, *Phys. Rev. A* 71, 022316 (2005). D. Litinski, *Quantum* 3, 205 (2019). M. Beverland et al., arXiv:2211.07629 (2022). "Magic Steady State Production," arXiv:2507.08676 (2025). "Orchestrating multi-level magic state distillation," arXiv:2509.24402 (2025).

*Real-time decoder engineering.* QUEKUF (FPGA Union Find), *ACM TRETS*. QASBA (sparse-blossom FPGA), *ACM TRETS*. Real-time superconducting QEC, arXiv:2410.05202 (2024). Network-integrated lattice surgery, arXiv:2504.11805 (2025).

*Sister projects.* Companion work on cognitive-architecture application (the four-scenario Langevin validation rig that grounds the s-regime and $k_{\text{frust}}$-subgraph FDR claims). Companion work on industrial-twin application (the *thermal_envelope* dual-description precedent that grounds the Compression Axiom test on operational ledgers).

*Random Structures & Algorithms* Braunstein, M. Mézard, and R. Zecchina, "Survey propagation: An algorithm for satisfiability," (2005).

*Proc. Natl. Acad. Sci.* Krzakala, A. Montanari, F. Ricci-Tersenghi, G. Semerjian, and L. Zdeborová, "Gibbs states and the set of solutions of random constraint satisfaction problems," (2007).

*Science* Mézard, G. Parisi, and R. Zecchina, "Analytic and Algorithmic Solution of Random Satisfiability Problems," (2002).

*J. Stat. Phys.* Mézard, F. Ricci-Tersenghi, and R. Zecchina, "Two solutions to diluted p-spin models and XORSAT problems," (2003).