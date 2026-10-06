from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from .config import load_config
from .fetcher import FinanceDataReaderClient
from .render import render_html
from .report import build_report


ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the daily market summary.")
    parser.add_argument("--config", type=Path, default=ROOT / "config" / "markets.toml")
    parser.add_argument("--template", type=Path, default=ROOT / "templates" / "summary.html.j2")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--as-of", type=date.fromisoformat, help="Run date in YYYY-MM-DD format.")
    parser.add_argument(
        "--target-date",
        type=date.fromisoformat,
        help="Market date to summarize in YYYY-MM-DD format.",
    )
    args = parser.parse_args(argv)

    config = load_config(args.config)
    output_dir = args.output_dir or ROOT / config.output_dir
    data_dir = args.data_dir or ROOT / config.data_dir

    report = build_report(
        config,
        FinanceDataReaderClient(),
        as_of=args.as_of,
        target_date=args.target_date,
    )
    html = render_html(report, args.template)

    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    report_date = report.as_of_date
    html_path = output_dir / f"{report_date}.html"
    json_path = data_dir / f"{report_date}.json"

    html_path.write_text(html, encoding="utf-8")
    (output_dir / "latest.html").write_text(html, encoding="utf-8")
    (output_dir / "index.html").write_text(html, encoding="utf-8")
    json_path.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {html_path}")
    print(f"Wrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
