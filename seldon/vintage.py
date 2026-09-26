"""Vintage-data primitives: preserve what was actually knowable at a cutoff."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class VintagePoint:
    observation_time:int
    available_at:int
    value:float
    series:str
    source:str=""
    vintage:str=""

def as_known(points:Iterable[VintagePoint], cutoff:int):
    """Latest release for each observation whose release existed by cutoff."""
    best={}
    for p in points:
        if p.available_at>cutoff: continue
        key=(p.series,p.observation_time)
        if key not in best or p.available_at>best[key].available_at: best[key]=p
    return best

def fingerprint(points:Iterable[VintagePoint]):
    import hashlib
    payload="\n".join(f"{p.series}|{p.observation_time}|{p.available_at}|{p.value:.17g}|{p.vintage}|{p.source}" for p in sorted(points,key=lambda x:(x.series,x.observation_time,x.available_at,x.vintage)))
    return hashlib.sha256(payload.encode()).hexdigest()
