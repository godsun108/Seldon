import unittest

from seldon.market import MarketBar, market_observations
from seldon.core import analogue_forecast


class TestMarketAdapter(unittest.TestCase):
    def bars(self):
        return [
            MarketBar(i, i, 100.0 + i, 1000.0 + i * 10)
            for i in range(8)
        ]

    def test_builds_only_after_minimum_history(self):
        rows = market_observations(self.bars())
        self.assertEqual([x.time for x in rows], [5, 6, 7])
        self.assertIn("momentum_1", rows[0].values)
        self.assertIn("momentum_5", rows[0].values)
        self.assertIn("volatility_5", rows[0].values)
        self.assertIn("volume_ratio_5", rows[0].values)
        self.assertEqual(rows[0].values["close"], 105.0)

    def test_preserves_provider_availability_time(self):
        bars = self.bars()
        bars[-1] = MarketBar(7, 99, 107.0, 1070.0)
        rows = market_observations(bars)
        self.assertEqual(rows[-1].available_at, 99)
        # The observation is retained, but SELDON must not use it at cutoff 6.
        self.assertEqual(rows[-1].time, 7)

    def test_rejects_unsorted_bars(self):
        with self.assertRaises(ValueError):
            market_observations([MarketBar(2, 2, 10, 1), MarketBar(1, 1, 11, 1)])

    def test_rejects_invalid_prices(self):
        with self.assertRaises(ValueError):
            market_observations([MarketBar(i, i, 0, 1) for i in range(6)])

    def test_minimum_history_must_be_valid(self):
        with self.assertRaises(ValueError):
            market_observations(self.bars(), min_history=1)


if __name__ == "__main__":
    unittest.main()
