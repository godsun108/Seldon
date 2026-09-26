"""Leakage-safe walk-forward evaluation for SELDON."""
from dataclasses import dataclass
from typing import Sequence
from .core import Observation, analogue_forecast, brier_up, seldon_deviation

@dataclass(frozen=True)
class WalkRecord:
    cutoff:int; actual_return:float; mean_forecast:float; p_up:float; brier:float; deviation:float

def walk_forward(history:Sequence[Observation], target:str, features:Sequence[str], horizon:int=1,k:int=5,min_cutoff:int=5):
    by_time={x.time:x for x in history}; out=[]
    for cutoff in sorted(t for t in by_time if t>=min_cutoff):
        future=by_time.get(cutoff+horizon)
        if future is None: continue
        try: f=analogue_forecast(history,cutoff,target,features,horizon,k)
        except ValueError: continue
        base=by_time[cutoff].values[target]
        actual=future.values[target]/base-1.0
        out.append(WalkRecord(cutoff,actual,f.mean,f.probability_above(),brier_up(f,actual),seldon_deviation(f,actual)))
    return out

def summary(records):
    if not records:return {"n":0}
    n=len(records); correct=sum((r.p_up>=.5)==(r.actual_return>0) for r in records)
    return {"n":n,"mean_brier":sum(r.brier for r in records)/n,"direction_accuracy":correct/n,
            "mean_abs_error":sum(abs(r.mean_forecast-r.actual_return) for r in records)/n,
            "mean_seldon_deviation":sum(r.deviation for r in records if r.deviation!=float("inf"))/max(1,sum(r.deviation!=float("inf") for r in records))}
