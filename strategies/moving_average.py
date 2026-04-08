from __future__ import annotations

from typing import List

from engine.models import PriceBar, Signal
from strategies.base import Strategy


class MovingAverageStrategy(Strategy):
    def __init__(
        self,
        short_window: int = 3,
        long_window: int = 5,
        liquidate_on_last_bar: bool = True,
        debug: bool = False,
    ) -> None:
        if short_window <= 0 or long_window <= 0:
            raise ValueError("short_window and long_window must be positive integers.")
        if short_window >= long_window:
            raise ValueError("short_window must be smaller than long_window.")

        self.short_window = short_window
        self.long_window = long_window
        self.liquidate_on_last_bar = liquidate_on_last_bar
        self.debug = debug

    def generate_signals(self, bars: List[PriceBar]) -> List[Signal]:
        closes = [bar.close for bar in bars]
        signals: List[Signal] = []
        in_position = False
        previous_short_ma: float | None = None
        previous_long_ma: float | None = None

        for index, bar in enumerate(bars):
            action = "HOLD"
            short_ma = self._moving_average(closes, index, self.short_window)
            long_ma = self._moving_average(closes, index, self.long_window)

            if (
                short_ma is not None
                and long_ma is not None
            ):
                first_eligible_bar = previous_short_ma is None or previous_long_ma is None
                crossed_above = (
                    short_ma > long_ma
                    and (
                        first_eligible_bar
                        or previous_short_ma <= previous_long_ma
                    )
                )
                crossed_below = (
                    short_ma < long_ma
                    and not first_eligible_bar
                    and previous_short_ma >= previous_long_ma
                )

                if crossed_above and not in_position:
                    action = "BUY"
                    in_position = True
                elif crossed_below and in_position:
                    action = "SELL"
                    in_position = False

            if self.liquidate_on_last_bar and index == len(bars) - 1 and in_position:
                action = "SELL"
                in_position = False

            signals.append(Signal(date=bar.date, action=action))

            if self.debug:
                self._print_debug_row(bar.date.isoformat(), bar.close, short_ma, long_ma, action)

            if short_ma is not None:
                previous_short_ma = short_ma
            if long_ma is not None:
                previous_long_ma = long_ma

        return signals

    @staticmethod
    def _moving_average(closes: List[float], index: int, window: int) -> float | None:
        if index + 1 < window:
            return None

        window_values = closes[index - window + 1 : index + 1]
        return sum(window_values) / window

    @staticmethod
    def _print_debug_row(
        date_text: str,
        close: float,
        short_ma: float | None,
        long_ma: float | None,
        action: str,
    ) -> None:
        short_ma_text = f"{short_ma:.2f}" if short_ma is not None else "n/a"
        long_ma_text = f"{long_ma:.2f}" if long_ma is not None else "n/a"
        print(
            f"MA Debug | {date_text} | Close {close:>7.2f} | "
            f"Short MA {short_ma_text:>7} | Long MA {long_ma_text:>7} | Signal {action}"
        )
