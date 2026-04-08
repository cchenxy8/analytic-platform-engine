from __future__ import annotations

from pathlib import Path
from typing import List

from engine.models import PortfolioSnapshot


def render_equity_curve_svg(
    history: List[PortfolioSnapshot],
    benchmark_history: List[PortfolioSnapshot],
    output_path: str | Path,
) -> Path:
    if not history:
        raise ValueError("Cannot render an equity curve with no portfolio history.")

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    width = 900
    height = 420
    padding = 50

    equities = [point.equity for point in history]
    benchmark_equities = [point.equity for point in benchmark_history] if benchmark_history else []
    all_equities = equities + benchmark_equities
    min_equity = min(all_equities)
    max_equity = max(all_equities)
    equity_range = max(max_equity - min_equity, 1.0)

    step_x = (width - (padding * 2)) / max(len(history) - 1, 1)

    def scale_x(index: int) -> float:
        return padding + (index * step_x)

    def scale_y(equity: float) -> float:
        normalized = (equity - min_equity) / equity_range
        return height - padding - (normalized * (height - (padding * 2)))

    strategy_points = " ".join(
        f"{scale_x(index):.2f},{scale_y(snapshot.equity):.2f}"
        for index, snapshot in enumerate(history)
    )
    benchmark_points = " ".join(
        f"{scale_x(index):.2f},{scale_y(snapshot.equity):.2f}"
        for index, snapshot in enumerate(benchmark_history)
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#f8fafc" />
  <text x="{padding}" y="30" font-family="Arial, sans-serif" font-size="20" fill="#0f172a">Equity Curve</text>
  <line x1="{padding}" y1="{height - padding}" x2="{width - padding}" y2="{height - padding}" stroke="#94a3b8" stroke-width="1" />
  <line x1="{padding}" y1="{padding}" x2="{padding}" y2="{height - padding}" stroke="#94a3b8" stroke-width="1" />
  <polyline fill="none" stroke="#2563eb" stroke-width="3" points="{strategy_points}" />
  <polyline fill="none" stroke="#f97316" stroke-width="3" points="{benchmark_points}" />
  <text x="{padding}" y="{height - 15}" font-family="Arial, sans-serif" font-size="12" fill="#475569">{history[0].date.isoformat()}</text>
  <text x="{width - padding - 85}" y="{height - 15}" font-family="Arial, sans-serif" font-size="12" fill="#475569">{history[-1].date.isoformat()}</text>
  <text x="{padding + 5}" y="{padding + 15}" font-family="Arial, sans-serif" font-size="12" fill="#475569">Max: {max_equity:,.2f}</text>
  <text x="{padding + 5}" y="{height - padding - 10}" font-family="Arial, sans-serif" font-size="12" fill="#475569">Min: {min_equity:,.2f}</text>
  <text x="{width - 220}" y="30" font-family="Arial, sans-serif" font-size="12" fill="#2563eb">Strategy</text>
  <text x="{width - 220}" y="48" font-family="Arial, sans-serif" font-size="12" fill="#f97316">Benchmark</text>
</svg>
"""
    path.write_text(svg, encoding="utf-8")
    return path
