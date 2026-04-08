from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from engine.models import PriceBar, Signal


class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, bars: List[PriceBar]) -> List[Signal]:
        """Return one signal per bar."""
