
## Setting 
Boolean = $\Phi^* \to \infty$ limit. MPA is the finite-flux generalization. Maintaining a proposition costs work; cut the work, structure dissolves.
**Primitives**: trail vector (kernel-weighted history while proposition active), flux budget $\Phi^*$, dissipation $\kappa$, observer kernel $\tau_{obs}$.
## Three typed objects
**Vertex regime** (single trail, stability axis $\lambda_A$):
- $c$ committed: $\lambda_A \ll -\kappa^{-1}\Phi^*$ — self-sustaining, ≈ 1
- $s$ suspended: $|\lambda_A| \lesssim \kappa^{-1}\Phi^*$ — true-while-pumped
- $r$ reset: $\lambda_A \gg \kappa^{-1}\Phi^*$ — decayed, ≈ 0
**Edge** (signed shear $\gamma_{AB}$):
- $\gamma<0$ cooperative · $\gamma\approx 0$ orthogonal · $\gamma>0$ conflicting (cost $\kappa\gamma_{AB}$, resolvable by flux)
**Subgraph** ($k_{\text{frust}}$): cycle of $c$-edges with obstructive shear-product. Topological. Not resolvable by $\Phi^*$.
## Scale-relativity
Vertex label depends on $\tau_{obs}$ (same trail reads $c$/$s$/$r$ at narrow/mid/wide window). Hierarchy itself is substrate-fixed. $\gamma$ scales with $\tau_{obs}$. $k_{\text{frust}}$ is invariant.
## Operators
$\mathcal{M}=\{c,s,r\}$, $\mathcal{M}_2=\{c,r\}$.
| Op | Signature | Action | $\Phi^*\to\infty$ limit |
|---|---|---|---|
| $C$ | $\mathcal{M}^2\to\mathcal{M}$ | try to merge: $d_{A\oplus B}=w_A d_A + w_B d_B$, evaluate $\lambda_{A\oplus B}$ | $\land$ |
| $S$ | $\mathcal{M}^2\to\mathcal{M}$ | hold both: $\kappa(|\lambda_A|+|\lambda_B|)+\max(0,\kappa\gamma_{AB})\le\Phi^*$ | $\lor$ |
| $K$ | $\mathcal{M}^2\to\mathcal{M}_2$ | distinguishability: $\delta(A,B)=\hat d_A - \hat d_B$; $c$ if $\delta\ne 0$ and flux covers, else $r$ | $\oplus$ |
| $R$ | $\mathcal{M}\to\mathcal{M}$ | sever to bath: $W_R \ge k_BT\ln 2\cdot H(A\mid\text{rest})$ | $\neg$ |
$K$ is unique: codomain restricted to $\mathcal{M}_2$; quotient acts on its inputs (not outputs).
## Boolean section ($\mathcal{M}_2$)
Three identifications of the same set:
1. Codomain of $K$
2. Fixed-point set of coarse-graining flow
3. Section on which limit-equivalence quotient is bijective
Restriction of $\Sigma=\{C,S,K,R,\top,\bot\}$ to $\mathcal{M}_2 \cong (\mathbb{B},\land,\lor,\oplus,\neg)$. Closure at $\sigma$-shadow level (regime can stray to $s$ but shadow holds).
**Boundary rules** at $\mathcal{M}_2\times\{s\}$: $\bot$ not global annihilator, $\top$ not global identity — shear and flux remain active. (Full table: §3.6.)
## Composite catalogue (molecular layer)
| Pair | Edge | Composite | Field-name |
|---|---|---|---|
| $c$–$c$ aligned | $\gamma<0$ | $c$ deepened | Hebbian; force chains |
| $c$–$c$ orthogonal | $\gamma\approx 0$ | $s$ | independent memory |
| $c$–$c$ opposed | $\gamma>0$ | $s$ if covered, else one→$r$ | competing hypotheses |
| $c$–$s$ | $\gamma<0$ | $s$ (mentor) | synaptic tagging; pilot-light |
| $s$–$s$ | $\gamma>0$ | $s$ or competitive dropout | Lotka–Volterra |
| $c$–$c$–$c$ cycle | obstructive product | $k_{\text{frust}}$ | gridlock; UNSAT |
| oscillatory–$c$ | limit cycle, $\lambda_B\ll 0$ | entrainment / quench | Kuramoto; circadian |
## Capacity
On classically consistent (frustration-free) graph:
$$|\Gamma^*| \le \sqrt{\frac{2\Phi^*}{\kappa\,\alpha\,\gamma_{min}\,d_{avg}}}$$
Sparse: $\sim\Phi^*$. Dense: $\sim\sqrt{\Phi^*}$. Predicts modular sparsification of densely-coupled substrates. $k_{\text{frust}}$ marks where structure is unsustainable at any flux.
## Fluctuation-dissipation signatures
Parametric plot $\chi(\tau)$ vs $C(0)-C(\tau)$:
- $r$: unit slope (FDT)
- $c$: $X\ll 1$, suppressed response, narrow horizontal locus
- $s$: aging diagonal, plateaus at long times
- $k_{\text{frust}}$: transient **negative** response (loop-level)
Signatures attach to objects of distinct type. $s$-aging transfers cross-substrate (Langevin → surface code).
## Compression Axiom / meta-ledger flow
Ledger tracks substrate. Who tracks ledger? Tower of meta-ledgers converges iff each ascent contracts: $\epsilon=\|\mathcal{C}\|_{op}<1$.
Flow is RG-like:
- $c$, $r$ fixed points; $s$ metastable (→$c$ if reinforced, →$r$ if not)
- $\mathcal{M}_2$ = terminal attractor
- $k_{\text{frust}}$ invariant of the flow on substrates carrying it
- edges follow endpoints (shear-positive edges with both endpoints→$r$ vanish)
- Boolean is degenerate limit (every level collapses to identity)
Trail vectors = equivalence classes under this flow. Substrate-neutrality at vertex = same flow class. Substrate-specificity at subgraph = topology of interaction graph.
## Falloff profile (three faces)
- **Longitudinal** (along $\Phi^*$, fixed everything else): polynomial-in-$1/\Phi^*$ / critical-scaling / exponential-with-power-law-correction
- **Lateral** (other commitments: scalar trail, single kernel, reciprocal coupling, continuous time): smooth or cusps?
- **Scale** ($\tau_{obs}$): kernel sweep walks $c\to s\to r$ on vertex; $k_{\text{frust}}$ doesn't migrate
Conjecture: Boolean is codimension-$N$ singular point, $N$ = relaxable commitments producing non-perturbative structure.
## Extension axes (§8 candidates — exist only at $\Phi^*<\infty$ + at least one commitment relaxed)
- **Limit-cycle trail** → rhythm primitive, oscillator-$c$ composites, closed-loop FDR
- **Hierarchical kernel** → multi-timescale, fragile-here-stable-there, multi-scale aging FDR
- **Non-reciprocal coupling** → dominance/inhibition, no symmetric truth-table shadow, turbulent FDR
- **Higher-order frustration** (hypergraph) → multi-plateau aging, full glassy taxonomy
- **Finite-population discreteness** → flickering $c\leftrightarrow r$, native probabilistic logic
Each = candidate operator with no Boolean limit. Two further deferred: transfer operator $T(A\to A')$, latent ledgers.
## Deformation calculus (finite-flux interior)
| Theorem | Bound | Limit |
|---|---|---|
| 6 (associator) | $\|\alpha_C\|\lesssim(\kappa/\Phi^*)\sum\|\gamma\|$ | $\to 0$ |
| 7 (distributivity defect) | $\|\delta_{dist}\|\lesssim(\kappa/\Phi^*)[\max(0,\gamma_{YZ})-\max(0,\gamma_{XY},\gamma_{XZ})]^+$ | $\to 0$ |
| 9 (Boolean deviation) | $\Delta_C(A,B)=1$ iff $\gamma_{AB}>0$ ∧ $\Phi^*<\kappa\gamma_{AB}$ | sharp threshold |

