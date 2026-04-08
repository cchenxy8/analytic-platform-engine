from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List


@dataclass(frozen=True)
class PriceBar:
    date: date
    close: float


@dataclass(frozen=True)
class Signal:
    date: date
    action: str


@dataclass(frozen=True)
class Trade:
    date: date
    action: str
    price: float
    shares: float
    cash_after: float


@dataclass(frozen=True)
class PortfolioSnapshot:
    date: date
    close: float
    cash: float
    shares: float
    equity: float


@dataclass
class BacktestResult:
    initial_cash: float
    bars: List[PriceBar]
    signals: List[Signal]
    history: List[PortfolioSnapshot]
    trades: List[Trade]
    metrics: Dict[str, float] = field(default_factory=dict)
    benchmark_history: List[PortfolioSnapshot] = field(default_factory=list)
    benchmark_trades: List[Trade] = field(default_factory=list)
    benchmark_metrics: Dict[str, float] = field(default_factory=dict)
