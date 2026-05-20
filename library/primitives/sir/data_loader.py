"""Self-contained stochastic SIR simulator.

Reference: CDC Gostic et al. cfa-gam-rt stochastic SIR; Figshare
Stochastic Zika Epidemic Trajectories. Both are public-domain / Figshare
Standard. We re-simulate the SIR Markov chain directly with a tau-leap
step (binomial draws per dt = 1) for trajectory ensembles.
"""
