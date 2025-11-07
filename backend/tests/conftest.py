from __future__ import annotations

import os
from collections.abc import Generator
from datetime import date
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.main import app
from app.database import Base, get_session
from app.models import FixedCost, Product, SalesData


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture()
def db_session(test_engine) -> Generator[Session, None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection, autoflush=False, autocommit=False, future=True)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def override_session_dependency(db_session):
    def _get_session():
        yield db_session

    app.dependency_overrides[get_session] = _get_session
    yield
    app.dependency_overrides.pop(get_session, None)


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def seeded_db(db_session: Session):
    july = date(2025, 7, 1)
    august = date(2025, 8, 1)
    db_session.add_all(
        [
            FixedCost(year_month=july, amount=34_222_000),
            FixedCost(year_month=august, amount=38_277_000),
        ]
    )
    product = Product(
        product_code="SKU-001",
        product_name="テスト商品",
        category="青果",
        unit_cost_per_kg=620,
        unit_price_per_kg=775,
        target_margin_rate=0.2,
        unit="JPY/kg",
    )
    db_session.add(product)
    db_session.flush()

    db_session.add_all(
        [
            SalesData(
                product_id=product.id,
                sale_date=date(2025, 8, 5),
                quantity_kg=1000,
                unit_price_per_kg=775,
                unit_cost_per_kg=620,
            ),
            SalesData(
                product_id=product.id,
                sale_date=date(2025, 8, 20),
                quantity_kg=500,
                unit_price_per_kg=790,
                unit_cost_per_kg=620,
            ),
        ]
    )
    db_session.commit()
    return db_session
