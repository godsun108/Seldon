# Experiments

## World State v1 — United States annual macro state

**Question:** using only earlier macro states, do inflation, unemployment and population growth contain useful analogue information about the direction/distribution of next-year real GDP growth?

**Target:** World Bank real GDP growth (`NY.GDP.MKTP.KD.ZG`).

**Features:** CPI inflation, total unemployment, population growth.

**Method:** nearest historical analogues; chronological walk-forward; probability of positive next-year GDP growth; Brier score, directional accuracy, mean absolute forecast error, and Seldon Deviation.

**Important limitation:** the World Bank API exposes historical observations but this first adapter does not reconstruct the exact data vintage that a forecaster possessed on each historical date. The experiment therefore uses a conservative one-year availability proxy and is a pipeline test, **not yet a vintage-grade proof of forecasting skill**. A later experiment must use release/vintage data (for example ALFRED-style vintages) before strong predictive claims are allowed.

Run: `python experiments/world_state_v1.py`

A model earns promotion only from genuinely unseen evidence. Failed experiments remain evidence and should not be hidden.
