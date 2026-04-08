from __future__ import annotations

import math
from typing import Dict, List

from engine.models import PortfolioSnapshot, Trade


def compute_performance_metrics(
    history: List[PortfolioSnapshot],
    trades: List[Trade],
    initial_cash: float,
) -> Dict[str, float]:
    if not history:
        return {}

    initial_equity = initial_cash
    final_equity = history[-1].equity
    total_return = (final_equity / initial_equity) - 1.0

    day_span = max((history[-1].date - history[0].date).days, 1)
    annualized_return = (final_equity / initial_equity) ** (365 / day_span) - 1.0

    peak_equity = history[0].equity
    max_drawdown = 0.0
    returns: List[float] = []
    positive_days = 0
    negative_days = 0

    for index, snapshot in enumerate(history):
        peak_equity = max(peak_equity, snapshot.equity)
        drawdown = (snapshot.equity / peak_equity) - 1.0
        max_drawdown = min(max_drawdown, drawdown)

        if index == 0:
            continue

        previous_equity = history[index - 1].equity
        if previous_equity == 0:
            period_return = 0.0
        else:
            period_return = (snapshot.equity / previous_equity) - 1.0

        returns.append(period_return)
        if period_return > 0:
            positive_days += 1
        elif period_return < 0:
            negative_days += 1

    volatility = 0.0
    mean_return = 0.0
    if len(returns) > 1:
        mean_return = sum(returns) / len(returns)
        variance = sum((value - mean_return) ** 2 for value in returns) / (len(returns) - 1)
        volatility = math.sqrt(variance) * math.sqrt(252)
    elif len(returns) == 1:
        mean_return = returns[0]

    sharpe_ratio = 0.0
    if volatility > 0:
        sharpe_ratio = (mean_return * 252) / volatility

    calmar_ratio = 0.0
    if max_drawdown < 0:
        calmar_ratio = annualized_return / abs(max_drawdown)
    elif annualized_return > 0:
        calmar_ratio = float("inf")

    best_day = max(returns) if returns else 0.0
    worst_day = min(returns) if returns else 0.0
    avg_daily_return = mean_return
    positive_day_rate = (positive_days / len(returns)) if returns else 0.0

    closed_trade_returns = _compute_closed_trade_returns(trades)
    winning_trades = [value for value in closed_trade_returns if value > 0]
    losing_trades = [value for value in closed_trade_returns if value < 0]
    win_rate = (len(winning_trades) / len(closed_trade_returns)) if closed_trade_returns else 0.0
    avg_trade_return = (
        sum(closed_trade_returns) / len(closed_trade_returns) if closed_trade_returns else 0.0
    )
    avg_win = (sum(winning_trades) / len(winning_trades)) if winning_trades else 0.0
    avg_loss = (sum(losing_trades) / len(losing_trades)) if losing_trades else 0.0
    profit_factor = 0.0
    gross_profit = sum(winning_trades)
    gross_loss = abs(sum(losing_trades))
    if gross_loss > 0:
        profit_factor = gross_profit / gross_loss
    elif gross_profit > 0:
        profit_factor = float("inf")

    exposure_days = sum(1 for snapshot in history if snapshot.shares > 0.0)
    exposure_rate = exposure_days / len(history)

    return {
        "initial_equity": initial_equity,
        "final_equity": final_equity,
        "total_return": total_return,
        "annualized_return": annualized_return,
        "max_drawdown": max_drawdown,
        "volatility": volatility,
        "sharpe_ratio": sharpe_ratio,
        "calmar_ratio": calmar_ratio,
        "avg_daily_return": avg_daily_return,
        "best_day": best_day,
        "worst_day": worst_day,
        "positive_day_rate": positive_day_rate,
        "exposure_rate": exposure_rate,
        "trade_count": float(len(trades)),
        "closed_trade_count": float(len(closed_trade_returns)),
        "win_rate": win_rate,
        "avg_trade_return": avg_trade_return,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_factor": profit_factor,
    }


def _compute_closed_trade_returns(trades: List[Trade]) -> List[float]:
    closed_returns: List[float] = []
    entry_price: float | None = None

    for trade in trades:
        if trade.action == "BUY":
            entry_price = trade.price
        elif trade.action == "SELL" and entry_price is not None and entry_price != 0:
            closed_returns.append((trade.price / entry_price) - 1.0)
            entry_price = None

    return closed_returns
