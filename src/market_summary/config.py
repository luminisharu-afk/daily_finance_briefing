from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class MarketItem:
    label: str
    symbol: str
    precision: int = 2
    percent_precision: int = 2


@dataclass(frozen=True)
class MarketSection:
    name: str
    items: tuple[MarketItem, ...]
    columns: int = 2


@dataclass(frozen=True)
class AppConfig:
    title: str
    timezone: str
    lookback_days: int
    output_dir: Path
    data_dir: Path
    sections: tuple[MarketSection, ...]


def load_config(path: Path) -> AppConfig:
    with path.open("rb") as file:
        raw = tomllib.load(file)

    sections = tuple(_parse_section(section) for section in raw.get("sections", []))
    if not sections:
        raise ValueError("config must contain at least one section")

    return AppConfig(
        title=str(raw.get("title", "전일 시장 요약")),
        timezone=str(raw.get("timezone", "Asia/Seoul")),
        lookback_days=int(raw.get("lookback_days", 30)),
        output_dir=Path(raw.get("output_dir", "reports")),
        data_dir=Path(raw.get("data_dir", "data")),
        sections=sections,
    )


def _parse_section(raw: dict) -> MarketSection:
    items = tuple(_parse_item(item) for item in raw.get("items", []))
    if not items:
        raise ValueError(f"section {raw.get('name', '<unnamed>')} must contain items")

    columns = int(raw.get("columns", 2))
    if columns < 1:
        raise ValueError("section columns must be 1 or greater")

    return MarketSection(
        name=str(raw["name"]),
        columns=columns,
        items=items,
    )


def _parse_item(raw: dict) -> MarketItem:
    return MarketItem(
        label=str(raw["label"]),
        symbol=str(raw["symbol"]),
        precision=int(raw.get("precision", 2)),
        percent_precision=int(raw.get("percent_precision", 2)),
    )
