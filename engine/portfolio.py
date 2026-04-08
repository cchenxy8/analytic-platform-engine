from __future__ import annotations

from typing import List, Tuple

from engine.models import PortfolioSnapshot, PriceBar, Signal, Trade


class Portfolio:
    def __init__(self, initial_cash: float) -> None:
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.shares = 0.0

    def run(self, bars: List[PriceBar], signals: List[Signal]) -> Tuple[List[PortfolioSnapshot], List[Trade]]:
        if len(bars) != len(signals):
            raise ValueError("Bars and signals must have the same length.")

        history: List[PortfolioSnapshot] = []
        trades: List[Trade] = []

        for bar, signal in zip(bars, signals):
            if signal.action == "BUY" and self.shares == 0.0:
                self.shares = self.cash / bar.close
                self.cash = 0.0
                trades.append(
                    Trade(
                        date=bar.date,
                        action="BUY",
                        price=bar.close,
                        shares=self.shares,
                        cash_after=self.cash,
                    )
                )
            elif signal.action == "SELL" and self.shares > 0.0:
                shares_to_sell = self.shares
                self.cash = shares_to_sell * bar.close
                self.shares = 0.0
                trades.append(
                    Trade(
                        date=bar.date,
                        action="SELL",
                        price=bar.close,
                        shares=shares_to_sell,
                        cash_after=self.cash,
                    )
                )

            equity = self.cash + (self.shares * bar.close)
            history.append(
                PortfolioSnapshot(
                    date=bar.date,
                    close=bar.close,
                    cash=self.cash,
                    shares=self.shares,
                    equity=equity,
                )
            )

        return history, trades
