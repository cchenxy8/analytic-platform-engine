from __future__ import annotations

import argparse

from data.loader import load_price_data
from engine.backtester import Backtester
from reporting.console import (
    print_comparison,
    print_debug_table,
    print_strategy_details,
    print_summary,
    print_trades,
)
from reporting.plotting import render_equity_curve_svg
from strategies.base import Strategy
from strategies.buy_and_hold import BuyAndHoldStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.moving_average_crossover import MovingAverageCrossoverStrategy

DEBUG_ROW_LIMIT = 10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a simple backtest with one of the available strategies.")
    parser.add_argument(
        "--strategy",
        choices=["buy_and_hold", "ma_crossover", "mean_reversion"],
        default="buy_and_hold",
        help="Strategy to run.",
    )
    parser.add_argument(
        "--csv",
        default="data/sample_prices.csv",
        help="Path to a CSV with at least 'date' and 'close' columns.",
    )
    parser.add_argument(
        "--initial-cash",
        type=float,
        default=10_000.0,
        help="Starting cash for the backtest.",
    )
    parser.add_argument(
        "--plot",
        default="equity_curve.svg",
        help="Output path for the generated equity curve SVG.",
    )
    parser.add_argument(
        "--short-window",
        type=int,
        default=3,
        help="Short moving average window for ma_crossover.",
    )
    parser.add_argument(
        "--long-window",
        type=int,
        default=5,
        help="Long moving average window for ma_crossover.",
    )
    parser.add_argument(
        "--lookback-window",
        type=int,
        default=5,
        help="Lookback window for mean_reversion.",
    )
    parser.add_argument(
        "--entry-threshold",
        type=float,
        default=0.03,
        help="Buy when price is this fraction below the moving average for mean_reversion.",
    )
    parser.add_argument(
        "--exit-threshold",
        type=float,
        default=0.01,
        help="Sell when price is this fraction above the moving average for mean_reversion.",
    )
    return parser.parse_args()


def build_strategy(args: argparse.Namespace) -> Strategy:
    if args.strategy == "buy_and_hold":
        return BuyAndHoldStrategy(liquidate_on_last_bar=True)
    if args.strategy == "ma_crossover":
        return MovingAverageCrossoverStrategy(
            short_window=args.short_window,
            long_window=args.long_window,
            liquidate_on_last_bar=True,
        )

    return MeanReversionStrategy(
        lookback_window=args.lookback_window,
        entry_threshold=args.entry_threshold,
        exit_threshold=args.exit_threshold,
        liquidate_on_last_bar=True,
    )


def main() -> None:
    args = parse_args()
    bars = load_price_data(args.csv)
    strategy = build_strategy(args)
    backtester = Backtester(initial_cash=args.initial_cash)
    result = backtester.run(bars, strategy)
    plot_path = render_equity_curve_svg(result.history, result.benchmark_history, args.plot)

    print_debug_table(result.bars, result.signals, result.history, DEBUG_ROW_LIMIT)
    print()
    print_summary("Strategy Summary", result.metrics)
    print_strategy_details(args)
    print()
    print_summary("Benchmark Summary", result.benchmark_metrics)
    print()
    print_comparison(result.metrics["excess_return"])
    print()
    print_trades(result.trades)
    print()
    print(f"Equity curve written to: {plot_path}")


if __name__ == "__main__":
    main()
