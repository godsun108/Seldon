"""Market-data adapter for SELDON's time-locked analogue forecaster.

This module deliberately does not fetch data or place orders. Callers supply
timestamped OHLCV bars from a separately validated provider.
"""
from dataclasses import dataclass
from math import sqrt
from statistics import mean
from typing import Sequence

from .core import Observation


@dataclass(frozen=True)
class MarketBar:
    """One completed bar. Times are Unix seconds (or another consistent unit)."""
    time: int
    available_at: int
    close: float
    volume: float


def market_observations(
    bars: Sequence[MarketBar], *, min_history: int = 5
) -> list[Observation]:
    """Convert bars to leakage-conscious SELDON observations.

    Features at time t use only bars at or before t:
      momentum_1, momentum_5, volatility_5, volume_ratio_5.
    The target is close, so core.analogue_forecast computes forward returns.
    A bar is not usable before its available_at time. The returned observations
    retain that time so the core information-time firewall can enforce cutoffs.
    """
    if min_history < 2:
        raise ValueError("min_history must be at least 2")
    if not bars:
        return []
    ordered = list(bars)
    if any(b.close <= 0 or b.volume < 0 for b in ordered):
        raise ValueError("close must be positive and volume non-negative")
    if any(b.available_at < b.time for b in ordered):
        raise ValueError("available_at cannot precede bar time")
    if any(ordered[i].time >= ordered[i + 1].time for i in range(len(ordered) - 1)):
        raise ValueError("bars must have unique, increasing times")

    out: list[Observation] = []
    for i, bar in enumerate(ordered):
        if i < min_history:
            continue
        window = ordered[max(0, i - 5):i + 1]
        previous = ordered[i - 1]
        five_back = ordered[max(0, i - 5)]
        returns = [
            window[j].close / window[j - 1].close - 1.0
            for j in range(1, len(window))
        ]
        avg_volume = mean(x.volume for x in window[:-1])
        vol_mean = mean(returns) if returns else 0.0
        volatility = (
            sqrt(sum((r - vol_mean) ** 2 for r in returns) / (len(returns) - 1))
            if len(returns) > 1 else 0.0
        )
        features = {
            "momentum_1": bar.close / previous.close - 1.0,
            "momentum_5": bar.close / five_back.close - 1.0,
            "volatility_5": volatility,
            "volume_ratio_5": bar.volume / avg_volume if avg_volume > 0 else 0.0,
        }
        values = {"close": bar.close, **features}
        out.append(Observation(bar.time, bar.available_at, values))
    return out
