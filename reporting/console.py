from __future__ import annotations

import math
from argparse import Namespace

from engine.models import PortfolioSnapshot, PriceBar, Signal, Trade


def print_summary(title: str, metrics: dict[str, float]) -> None:
    print(title)
    print("-" * 40)
    print(f"Initial Equity   : ${metrics['initial_equity']:,.2f}")
    print(f"Final Equity     : ${metrics['final_equity']:,.2f}")
    print(f"Total Return     : {metrics['total_return'] * 100:.2f}%")
    print(f"Annualized Return: {metrics['annualized_return'] * 100:.2f}%")
    print(f"Max Drawdown     : {metrics['max_drawdown'] * 100:.2f}%")
    print(f"Volatility       : {metrics['volatility'] * 100:.2f}%")
    print(f"Sharpe Ratio     : {_format_ratio(metrics['sharpe_ratio'])}")
    print(f"Calmar Ratio     : {_format_ratio(metrics['calmar_ratio'])}")
    print(f"Avg Daily Return : {metrics['avg_daily_return'] * 100:.2f}%")
    print(f"Best Day         : {metrics['best_day'] * 100:.2f}%")
    print(f"Worst Day        : {metrics['worst_day'] * 100:.2f}%")
    print(f"Positive Days    : {metrics['positive_day_rate'] * 100:.2f}%")
    print(f"Exposure         : {metrics['exposure_rate'] * 100:.2f}%")
    print(f"Trade Count      : {int(metrics['trade_count'])}")
    print(f"Closed Trades    : {int(metrics['closed_trade_count'])}")
    print(f"Win Rate         : {metrics['win_rate'] * 100:.2f}%")
    print(f"Avg Trade Return : {metrics['avg_trade_return'] * 100:.2f}%")
    print(f"Avg Win          : {metrics['avg_win'] * 100:.2f}%")
    print(f"Avg Loss         : {metrics['avg_loss'] * 100:.2f}%")
    print(f"Profit Factor    : {_format_ratio(metrics['profit_factor'])}")


def _format_ratio(value: float) -> str:
    if math.isinf(value):
        return "inf"
    return f"{value:.2f}"


def print_strategy_details(args: Namespace) -> None:
    print(f"Strategy         : {args.strategy}")
    if args.strategy == "ma_crossover":
        print(f"Short Window     : {args.short_window}")
        print(f"Long Window      : {args.long_window}")
    elif args.strategy == "mean_reversion":
        print(f"Lookback Window  : {args.lookback_window}")
        print(f"Entry Threshold  : {args.entry_threshold * 100:.2f}%")
        print(f"Exit Threshold   : {args.exit_threshold * 100:.2f}%")


def print_comparison(excess_return: float) -> None:
    print("Comparison")
    print("-" * 40)
    print(f"Excess Return    : {excess_return * 100:.2f}%")


def print_trades(trades: list[Trade]) -> None:
    print("Trades")
    print("-" * 40)
    for trade in trades:
        print(
            f"{trade.date.isoformat()} | {trade.action:<4} | "
            f"Price ${trade.price:,.2f} | Shares {trade.shares:.6f}"
        )


def print_debug_table(
    bars: list[PriceBar],
    signals: list[Signal],
    history: list[PortfolioSnapshot],
    limit: int,
) -> None:
    print(f"Debug View (first {min(limit, len(bars))} bars)")
    print("-" * 80)
    print(
        f"{'Date':<12} {'Close':>10} {'Signal':>8} {'Shares':>12} "
        f"{'Cash':>14} {'Value':>14}"
    )
    for bar, signal, snapshot in zip(bars[:limit], signals[:limit], history[:limit]):
        print(
            f"{bar.date.isoformat():<12} "
            f"{bar.close:>10.2f} "
            f"{signal.action:>8} "
            f"{snapshot.shares:>12.6f} "
            f"{snapshot.cash:>14.2f} "
            f"{snapshot.equity:>14.2f}"
        )
