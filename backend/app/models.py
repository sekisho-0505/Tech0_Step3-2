from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def _uuid() -> str:
    return str(uuid4())


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    product_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    unit_cost_per_kg: Mapped[Optional[float]] = mapped_column(Numeric(14, 3))
    unit_price_per_kg: Mapped[Optional[float]] = mapped_column(Numeric(14, 3))
    target_margin_rate: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))
    min_margin_rate: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))
    unit: Mapped[str] = mapped_column(Text, default="JPY/kg", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    sales: Mapped[list["SalesData"]] = relationship(back_populates="product")


class PriceSimulation(Base):
    __tablename__ = "price_simulations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    product_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("products.id"))
    simulation_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    input_cost_per_kg: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    target_margin_rate: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    calculated_price_per_kg: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    selected_price_per_kg: Mapped[Optional[float]] = mapped_column(Numeric(14, 3))
    quantity_kg: Mapped[Optional[float]] = mapped_column(Numeric(14, 3))
    gross_profit_total: Mapped[Optional[float]] = mapped_column(Numeric(16, 2))
    parameters: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product: Mapped[Optional[Product]] = relationship()


class FixedCost(Base):
    __tablename__ = "fixed_costs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    year_month: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="固定費", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SalesData(Base):
    __tablename__ = "sales_data"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    product_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("products.id"))
    sale_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity_kg: Mapped[Optional[float]] = mapped_column(Numeric(14, 3))
    unit_price_per_kg: Mapped[Optional[float]] = mapped_column(Numeric(14, 3))
    unit_cost_per_kg: Mapped[Optional[float]] = mapped_column(Numeric(14, 3))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product: Mapped[Optional[Product]] = relationship(back_populates="sales")
