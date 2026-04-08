from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import List

from engine.models import PriceBar


def load_price_data(csv_path: str | Path) -> List[PriceBar]:
    # Normalize the incoming path early so file checks and reads are consistent.
    path = _resolve_csv_path(csv_path)

    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV file is missing a header row.")

        # Map header names case-insensitively so slightly different CSV formats still work.
        normalized = {name.strip().lower(): name for name in reader.fieldnames}
        if "date" not in normalized or "close" not in normalized:
            raise ValueError("CSV must contain 'date' and 'close' columns.")

        date_column = normalized["date"]
        close_column = normalized["close"]

        bars: List[PriceBar] = []
        for row in reader:
            date_value = row.get(date_column, "").strip()
            close_value = row.get(close_column, "").strip()
            # Skip rows that are missing either required field.
            if not date_value or not close_value:
                continue

            bars.append(
                PriceBar(
                    date=datetime.strptime(date_value, "%Y-%m-%d").date(),
                    close=float(close_value),
                )
            )

    if not bars:
        raise ValueError("No valid price rows were loaded from the CSV.")

    # Sort by date so downstream logic always receives bars in chronological order.
    bars.sort(key=lambda bar: bar.date)
    return bars


def _resolve_csv_path(csv_path: str | Path) -> Path:
    path = Path(csv_path).expanduser()
    if path.exists():
        return path

    project_root = Path(__file__).resolve().parent.parent
    project_relative_path = project_root / path
    if project_relative_path.exists():
        return project_relative_path

    available_csvs = sorted(candidate.relative_to(project_root).as_posix() for candidate in project_root.rglob("*.csv"))
    available_csv_list = ", ".join(available_csvs) if available_csvs else "none found"
    raise FileNotFoundError(
        f"CSV file not found: {csv_path}. "
        f"Tried '{path}' and '{project_relative_path}'. "
        f"Available CSV files in this project: {available_csv_list}"
    )
