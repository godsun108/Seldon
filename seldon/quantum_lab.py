"""SELDON Quantum Lab.

Quantum methods are challengers, not privileged models. A challenger is promoted
only when it beats the same time-locked classical baseline out of sample.
"""
from dataclasses import dataclass
from math import exp
from random import Random

@dataclass(frozen=True)
class Benchmark:
    challenger: str
    challenger_score: float
    classical_score: float
    @property
    def beats_classical(self): return self.challenger_score < self.classical_score


def boltzmann_sampler(distances, shots=1024, temperature=1.0, seed=0):
    """Quantum-inspired sampler usable before a simulator/hardware provider is connected."""
    if not distances or shots<1 or temperature<=0: raise ValueError("invalid sampler parameters")
    w=[exp(-d/temperature) for d in distances]
    return Random(seed).choices(range(len(w)),weights=w,k=shots)
