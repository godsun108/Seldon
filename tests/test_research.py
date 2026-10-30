import unittest

from seldon.research import (
    Evidence, ResearchBrief, Scenario, validate_research_brief,
)


def valid_brief():
    return ResearchBrief(
        instrument="EXAMPLE",
        as_of=100,
        horizon="5 trading days",
        stance="mixed",
        confidence=0.55,
        data_status="delayed",
        evidence=(Evidence("Price trend is positive", "sample-feed", 99),),
        scenarios=(
            Scenario("bull", 0.25, 0.06, "Momentum continues",
                     ("earnings",), ("breaks support",)),
            Scenario("base", 0.50, 0.01, "Range-bound trade",
                     ("stable rates",), ("range breaks",)),
            Scenario("bear", 0.25, -0.08, "Risk-off repricing",
                     ("weak guidance",), ("reclaims resistance",)),
        ),
        key_risks=("volatility",),
        thesis_invalidation=("material guidance change",),
        limitations=("sample data only",),
    )


class TestResearchBrief(unittest.TestCase):
    def test_valid_brief_passes(self):
        validate_research_brief(valid_brief())

    def test_probabilities_must_sum_to_one(self):
        brief = valid_brief()
        scenarios = list(brief.scenarios)
        scenarios[0] = Scenario("bull", 0.40, 0.06, "Momentum continues",
                                ("earnings",), ("breaks support",))
        with self.assertRaises(ValueError):
            validate_research_brief(ResearchBrief(**{
                **brief.__dict__, "scenarios": tuple(scenarios)
            }))

    def test_future_evidence_is_rejected(self):
        brief = valid_brief()
        evidence = (Evidence("future claim", "sample-feed", 101),)
        with self.assertRaises(ValueError):
            validate_research_brief(ResearchBrief(**{
                **brief.__dict__, "evidence": evidence
            }))

    def test_missing_invalidation_is_rejected(self):
        brief = valid_brief()
        scenarios = list(brief.scenarios)
        scenarios[1] = Scenario("base", 0.50, 0.01, "Range-bound trade",
                                ("stable rates",), ())
        with self.assertRaises(ValueError):
            validate_research_brief(ResearchBrief(**{
                **brief.__dict__, "scenarios": tuple(scenarios)
            }))

    def test_unknown_data_status_is_rejected(self):
        brief = valid_brief()
        with self.assertRaises(ValueError):
            validate_research_brief(ResearchBrief(**{
                **brief.__dict__, "data_status": "live"
            }))


if __name__ == "__main__":
    unittest.main()
