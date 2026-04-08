from __future__ import annotations

import csv
import io
from datetime import datetime
import os
from pathlib import Path
from typing import List
from urllib.parse import urlencode
from urllib.request import urlopen

from engine.models import PriceBar

ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"


def load_price_data(csv_path: str | Path) -> List[PriceBar]:
    # Normalize the incoming path early so file checks and reads are consistent.
    path = _resolve_csv_path(csv_path)

    with path.open("r", newline="", encoding="utf-8") as handle:
        return _load_price_data_from_handle(handle)


def load_price_data_from_api(
    symbol: str,
    api_key: str | None = None,
    outputsize: str = "compact",
) -> List[PriceBar]:
    resolved_api_key = api_key or os.getenv("ALPHAVANTAGE_API_KEY") or _load_api_key_from_env_file()
    if not resolved_api_key:
        raise ValueError(
            "An Alpha Vantage API key is required. "
            "Pass --api-key, set ALPHAVANTAGE_API_KEY, or add it to a local .env file."
        )
    if outputsize not in {"compact", "full"}:
        raise ValueError("outputsize must be either 'compact' or 'full'.")

    query = urlencode(
        {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": outputsize,
            "datatype": "csv",
            "apikey": resolved_api_key,
        }
    )
    url = f"{ALPHA_VANTAGE_URL}?{query}"

    with urlopen(url) as response:
        response_text = response.read().decode("utf-8")

    if "Error Message" in response_text or "Note" in response_text or "Information" in response_text:
        preview = response_text.strip().replace("\n", " ")
        raise ValueError(f"Alpha Vantage API request failed for symbol '{symbol}': {preview}")

    return _load_price_data_from_handle(io.StringIO(response_text))


def _load_price_data_from_handle(handle: io.TextIOBase) -> List[PriceBar]:
    reader = csv.DictReader(handle)
    if reader.fieldnames is None:
        raise ValueError("CSV file is missing a header row.")

    # Map header names case-insensitively so slightly different CSV formats still work.
    normalized = {name.strip().lower(): name for name in reader.fieldnames}
    date_column = normalized.get("date") or normalized.get("timestamp")
    close_column = normalized.get("close")

    if date_column is None or close_column is None:
        available_columns = ", ".join(reader.fieldnames)
        raise ValueError(
            "CSV must contain a date-like column ('date' or 'timestamp') and a 'close' column. "
            f"Found columns: {available_columns}"
        )

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


def _load_api_key_from_env_file() -> str | None:
    project_root = Path(__file__).resolve().parent.parent
    env_path = project_root / ".env"
    if not env_path.exists():
        return None

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        if key.strip() == "ALPHAVANTAGE_API_KEY":
            return value.strip().strip("'\"")

    return None
