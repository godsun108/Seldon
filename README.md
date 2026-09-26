# SELDON

A falsifiable world-state forecasting laboratory inspired by the idea of psychohistory.

SELDON does **not** claim to predict destiny. It estimates probability distributions from time-locked historical information, records what was knowable at prediction time, scores forecasts against later observations, and measures surprise.

## Scientific rule

> Predict forward. Preserve what was known at the time. Score the prediction. Never rewrite history.

## v0.1

- World-state vectors from timestamped indicators
- Time-lock snapshots to prevent future leakage
- Historical analogue search
- Probabilistic trajectory forecasts
- Calibration/scoring with Brier score
- **Seldon Deviation**: standardized forecast surprise
- Quantum Lab: experimental methods must be compared against a classical baseline

## Quick start

```bash
python -m seldon.demo
python -m unittest discover -s tests
```

The demo uses synthetic data so the scientific machinery can be tested before real-world datasets are added.

## Architecture

```
OBSERVE -> TIME LOCK -> STATE -> ANALOGUES -> TRAJECTORIES
        -> PROBABILITIES -> REALITY -> SCORE -> DEVIATION -> UPDATE
```

SELDON reports uncertainty. A surprising event is evidence for model revision, not proof of a hidden cause.
