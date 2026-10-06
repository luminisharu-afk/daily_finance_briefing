from __future__ import annotations

from datetime import date
from pathlib import Path
import unittest

import pandas as pd

from market_summary.config import AppConfig, MarketItem, MarketSection
from market_summary.report import build_report, snapshot_from_frame


class FakeClient:
    def __init__(self) -> None:
        self.calls = []

    def read(self, symbol: str, start: date, end: date) -> pd.DataFrame:
        self.calls.append((symbol, start, end))
        return pd.DataFrame(
            {"Close": [100.0, 110.0]},
            index=pd.to_datetime(["2024-01-04", "2024-01-05"]),
        )


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


class BuildReportTest(unittest.TestCase):
    def test_target_date_defaults_report_date_to_following_day(self) -> None:
        client = FakeClient()

        report = build_report(_config(), client, target_date=date(2024, 1, 5))

        self.assertEqual(report.target_date, "2024-01-05")
        self.assertEqual(report.as_of_date, "2024-01-06")
        self.assertEqual(client.calls, [("TEST", date(2024, 1, 2), date(2024, 1, 6))])

    def test_target_date_controls_data_window_when_as_of_is_provided(self) -> None:
        client = FakeClient()

        report = build_report(
            _config(),
            client,
            as_of=date(2024, 2, 1),
            target_date=date(2024, 1, 5),
        )

        self.assertEqual(report.as_of_date, "2024-02-01")
        self.assertEqual(report.target_date, "2024-01-05")
        self.assertEqual(client.calls, [("TEST", date(2024, 1, 2), date(2024, 1, 6))])


def _config() -> AppConfig:
    item = MarketItem(label="테스트", symbol="TEST")
    return AppConfig(
        title="테스트",
        timezone="Asia/Seoul",
        lookback_days=3,
        output_dir=Path("reports"),
        data_dir=Path("data"),
        sections=(MarketSection(name="국내", columns=1, items=(item,)),),
    )


if __name__ == "__main__":
    unittest.main()
