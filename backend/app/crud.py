from __future__ import annotations

from datetime import date
from typing import Iterable, Optional

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from .models import FixedCost, Product, SalesData


def get_fixed_cost_total(session: Session, month: date) -> float:
    stmt: Select = select(func.coalesce(func.sum(FixedCost.amount), 0)).where(
        FixedCost.year_month == month
    )
    return float(session.execute(stmt).scalar_one())


def get_sales_summary(session: Session, start: date, end: date) -> tuple[float, float]:
    revenue_stmt: Select = select(
        func.coalesce(func.sum(SalesData.quantity_kg * SalesData.unit_price_per_kg), 0)
    ).where(SalesData.sale_date >= start, SalesData.sale_date < end)
    variable_cost_stmt: Select = select(
        func.coalesce(func.sum(SalesData.quantity_kg * SalesData.unit_cost_per_kg), 0)
    ).where(SalesData.sale_date >= start, SalesData.sale_date < end)
    revenue = float(session.execute(revenue_stmt).scalar_one())
    variable_cost = float(session.execute(variable_cost_stmt).scalar_one())
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
