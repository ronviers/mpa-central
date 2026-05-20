# mm1_queue — INVALIDATOR substrate (the corpus's own named falsifier)

**Role:** The single most direct falsification target in the MPA corpus.
M/M/1 queue (Poisson arrivals rate λ, exponential service rate μ,
ρ = λ/μ). Queue length N(t). As ρ → 1 (heavy traffic), (1−ρ)·N(t)
converges to **reflected Brownian motion** — a process with a known
diffusion exponent of **½**.

**No dataset.** Pure construction.

## The framework-named prediction under test

`H:/mpa-auditor/corpus/substrate-classes.json`, class **ck-glassy**,
class-condition **common-exponent**:

> "Substrate's slow-resource memory kernel and load-arrival process share
> a single anomalous-diffusion exponent (so α_s = β_mem = heavy-traffic
> exponent)."
>
> Falsifier (verbatim): "α_s (FDR aging-diagonal slope) and the
> heavy-traffic queueing exponent measured to differ while the substrate
> is in sustained s-regime holding."

So MPA predicts the FDR **aging-diagonal slope α_s** measured on these
cells should equal the **heavy-traffic exponent (½)** as ρ → 1.

## Falsifier

**MPA is invalidated here if α_s measured from the heavy-traffic cells
(ρ = 0.95, 0.99, 0.999) differs from ½ while the queue is in sustained
s-regime backlog.** This is the framework's own stated falsification
condition — it wrote the check; the queue substrate runs it.

## Operating points

ρ ∈ {0.5, 0.8, 0.95, 0.99, 0.999}, μ = 1. Queue initialized near its
stationary mean ρ/(1−ρ). `gt`: "r" for light traffic (fast relaxation),
"s" for heavy traffic (sustained backlog). The invalidator block carries
`expected_heavy_traffic_exponent = 0.5`.

## ẋ choices

`queue-increment` (ΔN per step), `queue-relative` (N − N_snap).
