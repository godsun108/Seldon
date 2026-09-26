"""Classical baseline for SELDON v0.1."""
from dataclasses import dataclass
from math import sqrt
from typing import Mapping, Sequence

@dataclass(frozen=True)
class Observation:
    time: int
    available_at: int
    values: Mapping[str, float]

@dataclass(frozen=True)
class Forecast:
    cutoff: int
    horizon: int
    target: str
    analogue_times: tuple[int, ...]
    outcomes: tuple[float, ...]

    @property
    def mean(self): return sum(self.outcomes)/len(self.outcomes)
    def probability_above(self, x=0.0):
        return sum(v>x for v in self.outcomes)/len(self.outcomes)


def _distance(a, b, features):
    return sqrt(sum((a.values[f]-b.values[f])**2 for f in features))


def analogue_forecast(history: Sequence[Observation], cutoff: int, target: str,
                       features: Sequence[str], horizon: int=1, k: int=5):
    """Nearest-analogue forecast with an explicit information-time firewall."""
    if horizon < 1 or k < 1: raise ValueError("horizon and k must be positive")
    by_time={x.time:x for x in history}
    now=by_time.get(cutoff)
    if now is None or now.available_at>cutoff: raise ValueError("cutoff unavailable")
    candidates=[]
    for past in history:
        future=by_time.get(past.time+horizon)
        if past.time>=cutoff or future is None: continue
        if past.available_at>cutoff or future.available_at>cutoff: continue
        if target not in past.values or target not in future.values: continue
        if any(f not in past.values or f not in now.values for f in features): continue
        base=past.values[target]
        if base == 0: continue
        ret=future.values[target]/base-1.0
        candidates.append((_distance(now,past,features),past.time,ret))
    candidates.sort(key=lambda x:(x[0],x[1]))
    chosen=candidates[:k]
    if not chosen: raise ValueError("no leakage-safe analogues")
    return Forecast(cutoff,horizon,target,tuple(x[1] for x in chosen),tuple(x[2] for x in chosen))


def brier_up(forecast: Forecast, actual_return: float):
    p=forecast.probability_above(0.0); y=float(actual_return>0)
    return (p-y)**2


def seldon_deviation(forecast: Forecast, actual_return: float):
    """Absolute standardized surprise; larger means farther from forecast distribution."""
    xs=forecast.outcomes; mu=forecast.mean
    if len(xs)<2: return 0.0 if actual_return==mu else float("inf")
    sd=sqrt(sum((x-mu)**2 for x in xs)/(len(xs)-1))
    return abs(actual_return-mu)/sd if sd else (0.0 if actual_return==mu else float("inf"))
