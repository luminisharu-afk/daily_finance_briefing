from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from math import isclose
from zoneinfo import ZoneInfo

import pandas as pd

from .config import AppConfig, MarketItem


@dataclass(frozen=True)
class MarketSnapshot:
    label: str
    symbol: str
    status: str
    value: float | None
    previous_value: float | None
    change: float | None
    change_percent: float | None
    direction: str
    trade_date: str | None
    previous_trade_date: str | None
    value_text: str
    percent_text: str
    arrow: str
    error: str | None = None


@dataclass(frozen=True)
class SectionSnapshot:
    name: str
    columns: int
    items: tuple[MarketSnapshot, ...]


@dataclass(frozen=True)
class MarketReport:
    title: str
    generated_at: str
    as_of_date: str
    target_date: str
    timezone: str
    sections: tuple[SectionSnapshot, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def build_report(config: AppConfig, client, as_of: date | None = None) -> MarketReport:
    zone = ZoneInfo(config.timezone)
    today = as_of or datetime.now(zone).date()
    target_date = today - timedelta(days=1)
    start_date = target_date - timedelta(days=config.lookback_days)
    end_date = target_date + timedelta(days=1)

    sections = []
    for section in config.sections:
        snapshots = []
        for item in section.items:
            try:
                frame = client.read(item.symbol, start_date, end_date)
                snapshots.append(snapshot_from_frame(item, frame, target_date))
            except Exception as exc:  # noqa: BLE001 - one failed symbol should not stop the report
                snapshots.append(error_snapshot(item, exc))

        sections.append(
            SectionSnapshot(
                name=section.name,
                columns=section.columns,
                items=tuple(snapshots),
            )
        )

    return MarketReport(
        title=config.title,
        generated_at=datetime.now(zone).isoformat(timespec="seconds"),
        as_of_date=today.isoformat(),
        target_date=target_date.isoformat(),
        timezone=config.timezone,
        sections=tuple(sections),
    )


def snapshot_from_frame(
    item: MarketItem,
    frame: pd.DataFrame,
    target_date: date,
) -> MarketSnapshot:
    close = _close_series(frame, target_date)
    if len(close) < 2:
        raise ValueError("not enough closing prices before the target date")

    previous_date, previous_value = close.index[-2], float(close.iloc[-2])
    trade_date, value = close.index[-1], float(close.iloc[-1])

    change = value - previous_value
    change_percent = 0.0 if isclose(previous_value, 0.0) else change / previous_value * 100
    direction = _direction(change)

    return MarketSnapshot(
        label=item.label,
        symbol=item.symbol,
        status="ok",
        value=value,
        previous_value=previous_value,
        change=change,
        change_percent=change_percent,
        direction=direction,
        trade_date=trade_date.date().isoformat(),
        previous_trade_date=previous_date.date().isoformat(),
        value_text=_format_number(value, item.precision),
        percent_text=_format_percent(change_percent, item.percent_precision),
        arrow=_arrow(direction),
    )


def error_snapshot(item: MarketItem, exc: Exception) -> MarketSnapshot:
    return MarketSnapshot(
        label=item.label,
        symbol=item.symbol,
        status="error",
        value=None,
        previous_value=None,
        change=None,
        change_percent=None,
        direction="flat",
        trade_date=None,
        previous_trade_date=None,
        value_text="-",
        percent_text="-",
        arrow="",
        error=str(exc),
    )


def _close_series(frame: pd.DataFrame, target_date: date) -> pd.Series:
    if frame.empty:
        raise ValueError("data frame is empty")
    if "Close" not in frame.columns:
        raise ValueError("data frame does not contain a Close column")

    normalized = frame.copy()
    normalized.index = pd.to_datetime(normalized.index)
    normalized = normalized.sort_index()
    normalized = normalized.loc[normalized.index.normalize() <= pd.Timestamp(target_date)]

    close = pd.to_numeric(normalized["Close"], errors="coerce").dropna()
    return close


def _direction(change: float) -> str:
    if isclose(change, 0.0):
        return "flat"
    return "up" if change > 0 else "down"


def _arrow(direction: str) -> str:
    return {"up": "▲", "down": "▼", "flat": "■"}[direction]


def _format_number(value: float, precision: int) -> str:
    return f"{value:,.{precision}f}"


def _format_percent(value: float, precision: int) -> str:
    return f"{abs(value):.{precision}f}%"
