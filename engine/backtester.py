from __future__ import annotations

from typing import List

from engine.models import BacktestResult, PriceBar
from engine.portfolio import Portfolio
from metrics.performance import compute_performance_metrics
from strategies.base import Strategy
from strategies.buy_and_hold import BuyAndHoldStrategy


class Backtester:
    def __init__(self, initial_cash: float = 10_000.0) -> None:
        self.initial_cash = initial_cash

    def run(self, bars: List[PriceBar], strategy: Strategy) -> BacktestResult:
        if not bars:
            raise ValueError("Backtester requires at least one price bar.")

        # Run the requested strategy first to capture its signals, trades, and equity curve.
        signals = strategy.generate_signals(bars)
        if len(signals) != len(bars):
            raise ValueError(
                f"Strategy returned {len(signals)} signals for {len(bars)} price bars."
            )

        portfolio = Portfolio(initial_cash=self.initial_cash)
        history, trades = portfolio.run(bars, signals)
        metrics = compute_performance_metrics(history, trades, self.initial_cash)
        # Build a buy-and-hold baseline so the final result includes a simple benchmark.
        benchmark_strategy = BuyAndHoldStrategy(liquidate_on_last_bar=True)
        benchmark_signals = benchmark_strategy.generate_signals(bars)
        benchmark_portfolio = Portfolio(initial_cash=self.initial_cash)
        benchmark_history, benchmark_trades = benchmark_portfolio.run(bars, benchmark_signals)
        benchmark_metrics = compute_performance_metrics(
            benchmark_history,
            benchmark_trades,
            self.initial_cash,
        )
        # Add benchmark comparisons directly into the main metrics payload for easy reporting.
        metrics["benchmark_total_return"] = benchmark_metrics["total_return"]
        metrics["benchmark_final_equity"] = benchmark_metrics["final_equity"]
        metrics["excess_return"] = metrics["total_return"] - benchmark_metrics["total_return"]

        return BacktestResult(
            initial_cash=self.initial_cash,
            bars=bars,
            signals=signals,
            history=history,
            trades=trades,
            metrics=metrics,
            benchmark_history=benchmark_history,
            benchmark_trades=benchmark_trades,
            benchmark_metrics=benchmark_metrics,
        )
