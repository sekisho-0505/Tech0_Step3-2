from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class PricePattern(BaseModel):
    margin_rate: float = Field(gt=0, lt=0.9)
    price_per_kg: int
    profit_per_kg: int


class PriceSimulationRequest(BaseModel):
    product_name: str
    unit_cost_per_kg: float = Field(gt=0)
    target_margin_rate: float = Field(gt=0, lt=0.9)
    quantity_kg: Optional[float] = Field(default=None, ge=0)


class PriceSimulationResponse(BaseModel):
    recommended_price_per_kg: int
    gross_profit_per_kg: int
    gross_profit_total: Optional[int]
    margin_rate: float
    price_patterns: List[PricePattern]
    guard: dict


class BreakEvenResponse(BaseModel):
    year_month: str
    fixed_costs: int
    current_revenue: int
    variable_cost_rate: float
    gross_margin_rate: float
    break_even_revenue: int
    achievement_rate: float
    delta_revenue: int
    status: str


class ExcelImportWarning(BaseModel):
    row: int
    field: str
    reason: str


class ExcelImportResponse(BaseModel):
    imported: int
    skipped: int
    warnings: List[ExcelImportWarning]
