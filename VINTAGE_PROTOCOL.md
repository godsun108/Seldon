# Vintage-grade SELDON protocol

The central historical test is: **what could SELDON actually have known then?**

For revision-prone indicators, final revised history is forbidden as a substitute for historical information. Each datum carries both an observation date and a release/vintage date. At forecast cutoff T, SELDON selects only releases available by T and reconstructs the latest vintage then known.

## Promotion standard

A world-state model is not called predictive merely because it fits history. Before promotion it must have a frozen target, horizon, features, preprocessing and scoring rule; chronological walk-forward evaluation; vintage-safe inputs; simple baseline comparisons; uncertainty/calibration reporting; and a final untouched holdout or prospective ledger.

## Quantum rule

Quantum and quantum-inspired models use **exactly the same historical cutoffs and scoring** as the classical baseline. They are promoted only on reproducible out-of-sample improvement, with compute cost reported. Quantum novelty is not evidence of forecasting skill.

## Current state

The code can now reconstruct historical information sets from ALFRED/FRED-style vintage CSV exports and fingerprints the evidence. Real vintage exports still need to be supplied/fetched before a vintage-grade score exists. Until then, no claim of predictive skill is warranted.
