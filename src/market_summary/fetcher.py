from __future__ import annotations

from datetime import date

import pandas as pd


class FinanceDataReaderClient:
    """Thin adapter around FinanceDataReader so report logic stays testable."""

    def read(self, symbol: str, start: date, end: date) -> pd.DataFrame:
        try:
            import FinanceDataReader as fdr
        except ImportError as exc:
            raise RuntimeError(
                "FinanceDataReader is not installed. Run `pip install -e .` first."
            ) from exc

        return fdr.DataReader(symbol, start.isoformat(), end.isoformat())
