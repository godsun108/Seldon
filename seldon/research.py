"""Structured, evidence-carrying market opinions for Genesis.

This is a presentation/validation contract, not a market-data provider or
investment recommendation engine. It forces scenario probabilities, evidence
timestamps, and uncertainty to be explicit before a brief is rendered.
"""
from dataclasses import dataclass
from math import isfinite
from typing import Sequence


@dataclass(frozen=True)
class Evidence:
    claim: str
    source: str
    observed_at: int
    detail: str = ""


@dataclass(frozen=True)
class Scenario:
    name: str
    probability: float
    expected_return: float
    rationale: str
    catalysts: tuple[str, ...]
    invalidation: tuple[str, ...]


@dataclass(frozen=True)
class ResearchBrief:
    instrument: str
    as_of: int
    horizon: str
    stance: str
    confidence: float
    data_status: str
    evidence: tuple[Evidence, ...]
    scenarios: tuple[Scenario, ...]
    key_risks: tuple[str, ...]
    thesis_invalidation: tuple[str, ...]
    limitations: tuple[str, ...]


def validate_research_brief(brief: ResearchBrief) -> None:
    """Raise ValueError unless the brief is complete and internally coherent.

    Probability values are estimates, not guarantees. This validator checks
    arithmetic and required disclosures; it cannot verify source truthfulness.
    """
    if not brief.instrument.strip() or not brief.horizon.strip():
        raise ValueError("instrument and horizon are required")
    if brief.as_of < 0:
        raise ValueError("as_of must be non-negative")
    if brief.stance not in {"bullish", "neutral", "bearish", "mixed"}:
        raise ValueError("unsupported stance")
    if not isfinite(brief.confidence) or not 0.0 <= brief.confidence <= 1.0:
        raise ValueError("confidence must be between 0 and 1")
    if brief.data_status not in {"fresh", "delayed", "stale", "unknown"}:
        raise ValueError("data_status must disclose freshness")
    if not brief.evidence:
        raise ValueError("at least one evidence item is required")
    for item in brief.evidence:
        if not item.claim.strip() or not item.source.strip():
            raise ValueError("each evidence item needs a claim and source")
        if item.observed_at < 0 or item.observed_at > brief.as_of:
            raise ValueError("evidence timestamp must not be after brief as_of")
    names = {scenario.name.lower() for scenario in brief.scenarios}
    if names != {"bull", "base", "bear"} or len(brief.scenarios) != 3:
        raise ValueError("exactly bull, base, and bear scenarios are required")
    total = 0.0
    for scenario in brief.scenarios:
        if not isfinite(scenario.probability) or not 0.0 <= scenario.probability <= 1.0:
            raise ValueError("scenario probabilities must be between 0 and 1")
        if not isfinite(scenario.expected_return):
            raise ValueError("scenario expected_return must be finite")
        if not scenario.rationale.strip():
            raise ValueError("each scenario needs a rationale")
        if not scenario.catalysts or not scenario.invalidation:
            raise ValueError("each scenario needs catalysts and invalidation conditions")
        total += scenario.probability
    if abs(total - 1.0) > 1e-8:
        raise ValueError("bull/base/bear probabilities must sum to 1")
    if not brief.key_risks or not brief.thesis_invalidation or not brief.limitations:
        raise ValueError("risks, thesis invalidation, and limitations are required")
