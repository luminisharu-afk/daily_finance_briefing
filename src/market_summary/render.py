from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .report import MarketReport


def render_html(report: MarketReport, template_path: Path) -> str:
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=select_autoescape(("html", "xml")),
    )
    template = env.get_template(template_path.name)
    return template.render(report=report.to_dict())
