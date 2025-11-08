from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional, Tuple

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from .models import FixedCost, Product, SalesData


def _as_decimal(value: object) -> Decimal:
    """Convert DB aggregation results to ``Decimal`` safely."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def get_fixed_cost_total(session: Session, month: date) -> Decimal:
    stmt: Select = select(func.coalesce(func.sum(FixedCost.amount), 0)).where(
        FixedCost.year_month == month
    )
    result = session.execute(stmt).scalar_one()
    return _as_decimal(result)


def get_sales_summary(session: Session, start: date, end: date) -> Tuple[Decimal, Decimal]:
    revenue_stmt: Select = select(
        func.coalesce(func.sum(SalesData.quantity_kg * SalesData.unit_price_per_kg), 0)
    ).where(SalesData.sale_date >= start, SalesData.sale_date < end)
    variable_cost_stmt: Select = select(
        func.coalesce(func.sum(SalesData.quantity_kg * SalesData.unit_cost_per_kg), 0)
    ).where(SalesData.sale_date >= start, SalesData.sale_date < end)
    revenue = _as_decimal(session.execute(revenue_stmt).scalar_one())
    variable_cost = _as_decimal(session.execute(variable_cost_stmt).scalar_one())
    return revenue, variable_cost


def upsert_product(session: Session, data: dict) -> Product:
    product_code = data["product_code"]
    product: Optional[Product] = session.execute(
        select(Product).where(Product.product_code == product_code)
    ).scalar_one_or_none()
    if product is None:
        product = Product(**data)
        session.add(product)
    else:
        for key, value in data.items():
            setattr(product, key, value)
    return product
