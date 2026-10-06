from __future__ import annotations

from datetime import date
import unittest

import pandas as pd

from market_summary.config import MarketItem
from market_summary.report import snapshot_from_frame


class SnapshotFromFrameTest(unittest.TestCase):
    def test_uses_last_two_closes_on_or_before_target_date(self) -> None:
        frame = pd.DataFrame(
            {"Close": [100.0, 110.0, 120.0]},
            index=pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]),
        )
        item = MarketItem(label="테스트", symbol="TEST", precision=2)

        snapshot = snapshot_from_frame(item, frame, date(2024, 1, 3))

        self.assertEqual(snapshot.status, "ok")
        self.assertEqual(snapshot.value, 110.0)
        self.assertEqual(snapshot.previous_value, 100.0)
        self.assertEqual(snapshot.direction, "up")
        self.assertEqual(snapshot.value_text, "110.00")
        self.assertEqual(snapshot.percent_text, "10.00%")
        self.assertEqual(snapshot.trade_date, "2024-01-03")

    def test_requires_close_column(self) -> None:
        frame = pd.DataFrame(
            {"Open": [100.0, 110.0]},
            index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
        )
        item = MarketItem(label="테스트", symbol="TEST")

        with self.assertRaisesRegex(ValueError, "Close"):
            snapshot_from_frame(item, frame, date(2024, 1, 3))


if __name__ == "__main__":
    unittest.main()
