from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable

ROUNDING_CONTEXT = Decimal("0")


def round_jpy(value: float | Decimal) -> int:
    """Round to the nearest yen using 四捨五入."""
    return int(Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def round_rate(value: float | Decimal) -> float:
    return float(Decimal(value).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))


def generate_price_patterns(unit_cost_per_kg: float) -> Iterable[tuple[float, int, int]]:
    for margin_rate in [0.10, 0.15, 0.20, 0.25, 0.30]:
        price = unit_cost_per_kg / (1.0 - margin_rate)
        profit = price - unit_cost_per_kg
        yield margin_rate, round_jpy(price), round_jpy(profit)
