from __future__ import annotations

from typing import List

from engine.models import PriceBar, Signal
from strategies.base import Strategy


class BuyAndHoldStrategy(Strategy):
    def __init__(self, liquidate_on_last_bar: bool = True) -> None:
        self.liquidate_on_last_bar = liquidate_on_last_bar

    def generate_signals(self, bars: List[PriceBar]) -> List[Signal]:
        signals: List[Signal] = []
        for index, bar in enumerate(bars):
            action = "HOLD"
            if index == 0:
                action = "BUY"
            elif self.liquidate_on_last_bar and index == len(bars) - 1:
                action = "SELL"

            signals.append(Signal(date=bar.date, action=action))

        return signals
