from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, Tuple


def _ensure_decimal(value: float | int | Decimal) -> Decimal:
    """Convert incoming numeric values to ``Decimal`` preserving precision."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def round_jpy(value: float | Decimal) -> int:
    """Round to the nearest yen using 四捨五入 (ROUND_HALF_UP)."""
    decimal_value = _ensure_decimal(value)
    return int(decimal_value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def round_rate(value: float | Decimal) -> Decimal:
    """Round rates to four decimal places (0.0001) using 四捨五入."""
    decimal_value = _ensure_decimal(value)
    return decimal_value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def generate_price_patterns(unit_cost_per_kg: float | Decimal) -> Iterable[Tuple[Decimal, int, int]]:
    """Yield predefined price patterns calculated with ``Decimal`` precision."""
    cost = _ensure_decimal(unit_cost_per_kg)
    for margin_rate in (
        Decimal("0.10"),
        Decimal("0.15"),
        Decimal("0.20"),
        Decimal("0.25"),
        Decimal("0.30"),
    ):
        price = cost / (Decimal("1") - margin_rate)
        profit = price - cost
        yield margin_rate, round_jpy(price), round_jpy(profit)
