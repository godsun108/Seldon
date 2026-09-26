# Data contract v0.1

Every real observation must preserve **observation_time**, **available_at**, source provenance, value/units, and—when applicable—the historical vintage/revision. Backtests may use a value only when `available_at <= forecast_cutoff`.

Every forecast must preserve its cutoff, model/spec version, features, horizon, analogue IDs or model state, probability output, and a fingerprint of source data. Later outcomes and scores are appended rather than rewriting the original forecast.

## Guardrail

SELDON models aggregate measurable systems. It is not for telling people how to vote, ranking candidates, targeting individuals, or political persuasion. Political data must remain sourced, descriptive, aggregate, and uncertainty-aware.
