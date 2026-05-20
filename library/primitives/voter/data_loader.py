"""Self-contained simulator; no external dataset to load.

The voter substrate is a thin reproduction of Mobilia 2023 (Leeds 1080,
CC-BY 4.0) at the agent-level: 1D fully-connected voter with a
time-fluctuating external bias of switching rate ν.

If a future session wants to ingest the deposited summary statistics
from `archive.researchdata.leeds.ac.uk/1080/`, that loader goes here.
For now the empirical contract is the simulator itself; treat the
operating-point axis (ν) as the substrate-conditional measurement
control.
"""
