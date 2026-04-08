from __future__ import annotations

from typing import List

from engine.models import PriceBar, Signal
from strategies.base import Strategy


class MeanReversionStrategy(Strategy):
    def __init__(
        self,
        lookback_window: int = 5,
        entry_threshold: float = 0.03,
        exit_threshold: float = 0.01,
        liquidate_on_last_bar: bool = True,
        debug: bool = False,
        debug_limit: int = 10,
    ) -> None:
        if lookback_window <= 0:
            raise ValueError("lookback_window must be a positive integer.")
        if entry_threshold < 0 or exit_threshold < 0:
            raise ValueError("Thresholds must be non-negative.")
        if debug_limit <= 0:
            raise ValueError("debug_limit must be a positive integer.")

        self.lookback_window = lookback_window
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.liquidate_on_last_bar = liquidate_on_last_bar
        self.debug = debug
        self.debug_limit = debug_limit

    def generate_signals(self, bars: List[PriceBar]) -> List[Signal]:
        closes = [bar.close for bar in bars]
        signals: List[Signal] = []
        in_position = False
        debug_rows_printed = 0

        for index, bar in enumerate(bars):
            action = "HOLD"
            moving_average = self._moving_average(closes, index, self.lookback_window)

            if moving_average is not None:
                lower_band = moving_average * (1.0 - self.entry_threshold)
                upper_band = moving_average * (1.0 + self.exit_threshold)

                if bar.close <= lower_band and not in_position:
                    action = "BUY"
                    in_position = True
                elif bar.close >= upper_band and in_position:
                    action = "SELL"
                    in_position = False

            if self.liquidate_on_last_bar and index == len(bars) - 1 and in_position:
                action = "SELL"
                in_position = False

            signals.append(Signal(date=bar.date, action=action))

            if self.debug and moving_average is not None and debug_rows_printed < self.debug_limit:
                self._print_debug_row(
                    bar.date.isoformat(),
                    bar.close,
                    moving_average,
                    action,
                )
                debug_rows_printed += 1

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
        moving_average: float,
        action: str,
    ) -> None:
        percent_deviation = ((close - moving_average) / moving_average) * 100.0

        print(
            f"MR Debug | {date_text} | Close {close:>7.2f} | "
            f"Mean {moving_average:>7.2f} | Deviation {percent_deviation:>7.2f}% | "
            f"Signal {action}"
        )
