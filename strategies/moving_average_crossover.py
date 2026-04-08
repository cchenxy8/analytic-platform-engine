from __future__ import annotations

from typing import List

from engine.models import PriceBar, Signal
from strategies.base import Strategy


class MovingAverageCrossoverStrategy(Strategy):
    def __init__(
        self,
        short_window: int = 3,
        long_window: int = 5,
        liquidate_on_last_bar: bool = True,
    ) -> None:
        if short_window <= 0 or long_window <= 0:
            raise ValueError("Moving average windows must be positive integers.")
        if short_window >= long_window:
            raise ValueError("short_window must be smaller than long_window.")

        self.short_window = short_window
        self.long_window = long_window
        self.liquidate_on_last_bar = liquidate_on_last_bar

    def generate_signals(self, bars: List[PriceBar]) -> List[Signal]:
        closes = [bar.close for bar in bars]
        signals: List[Signal] = []
        in_position = False

        for index, bar in enumerate(bars):
            action = "HOLD"
            short_ma = self._moving_average(closes, index, self.short_window)
            long_ma = self._moving_average(closes, index, self.long_window)

            if short_ma is not None and long_ma is not None:
                if short_ma > long_ma and not in_position:
                    action = "BUY"
                    in_position = True
                elif short_ma < long_ma and in_position:
                    action = "SELL"
                    in_position = False

            if self.liquidate_on_last_bar and index == len(bars) - 1 and in_position:
                action = "SELL"
                in_position = False

            signals.append(Signal(date=bar.date, action=action))

        return signals

    @staticmethod
    def _moving_average(closes: List[float], index: int, window: int) -> float | None:
        if index + 1 < window:
            return None

        window_values = closes[index - window + 1 : index + 1]
        return sum(window_values) / window
