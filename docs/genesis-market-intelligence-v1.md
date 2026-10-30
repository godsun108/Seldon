# Genesis Market Intelligence — v1 integration boundary

## Purpose

Genesis should be able to discuss markets using traceable evidence and Seldon's
probabilistic forecasting machinery. This change is the first small building
block: a deterministic adapter from supplied OHLCV bars into Seldon observations.

## What this adds

- `seldon.market.MarketBar` represents a completed bar with both event time and
  provider availability time.
- `market_observations()` derives trailing one-bar and five-bar momentum,
  five-bar realized volatility, and a five-bar volume ratio.
- The output uses the existing `Observation` type and keeps `available_at`
  intact, allowing `seldon.core.analogue_forecast()` to apply its existing
  information-time firewall.
- Standard-library-only tests cover feature construction and input validation.

## Intended Genesis research flow

1. Obtain market data from a named provider, including source, instrument,
   interval, timezone, event timestamps, availability timestamps, and any
   corporate-action adjustments.
2. Validate freshness, missing bars, duplicate timestamps, symbol identity,
   currency, and market session.
3. Convert completed bars with `market_observations()`.
4. Generate a time-locked forecast using the existing classical Seldon baseline.
5. Present probabilities, historical analogue count, forecast horizon,
   uncertainty, source timestamps, and known data limitations to Genesis.
6. Score the forecast only after the outcome becomes observable. Preserve the
   original forecast and score it with the existing evaluation machinery.

## Explicit non-goals

This adapter does not fetch market data, authenticate to a broker, calculate
fundamental valuation, produce a complete investment recommendation, or place
orders. It does not establish that any provider feed is real-time or suitable
for trading. The current analogue model is a small experimental baseline, not
a validated professional trading model.

## Next integration stages

- Add a provider-neutral market-data contract and one read-only provider adapter.
- Add data-quality and freshness checks before any forecast can be shown as
  current.
- Add a research-brief schema for bull/base/bear cases, catalysts, risks,
  thesis invalidation, and explicit confidence limitations.
- Add walk-forward evaluation, transaction-cost/slippage assumptions, and
  benchmark comparisons before interpreting strategy performance.
- Connect the existing Seldon agent arena only after its implementation and
  paper-trading boundaries are verified.
- Keep brokerage execution out of scope. Any future order path must be a
  separate, opt-in system with position/risk limits and explicit human approval.

## Data and safety rules

Never fabricate a quote or silently substitute delayed data for live data.
Every market claim should identify its source and as-of time. Missing or stale
inputs must result in an explicit unavailable/uncertain state, not a confident
guess. Paper results must be labeled simulated and must include fees, spread,
slippage, and fill assumptions. Forecasts are opinions under uncertainty, not
guarantees or personalized financial advice.
