from __future__ import annotations

from datetime import date
from io import BytesIO

from fastapi.testclient import TestClient
from openpyxl import Workbook

from app.utils import round_jpy


def test_price_simulation_endpoint(client: TestClient):
    response = client.post(
        "/api/price-simulations/calculate",
        json={
            "product_name": "商品A",
            "unit_cost_per_kg": 620,
            "target_margin_rate": 0.20,
            "quantity_kg": 1000,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["recommended_price_per_kg"] == 775
    assert data["gross_profit_per_kg"] == 155
    assert data["gross_profit_total"] == 155000
    assert data["guard"]["min_allowed_price_per_kg"] == 775


def test_break_even_endpoint(client: TestClient, seeded_db):
    response = client.get("/api/break-even/current", params={"year_month": "2025-08"})
    assert response.status_code == 200
    data = response.json()
    assert data["year_month"] == "2025-08"
    assert data["fixed_costs"] == 38_277_000
    assert data["status"] == "safe"
    assert data["break_even_revenue"] > 0


def test_excel_import(client: TestClient, seeded_db):
    workbook = Workbook()
    sheet = workbook.active
    sheet["C1"] = "product_code"
    sheet["D1"] = "product_name"
    sheet["F1"] = "unit_cost"
    sheet["G1"] = "unit_price"
    sheet["H1"] = "target_margin"

    sheet["C2"] = "SKU-002"
    sheet["D2"] = "新商品"
    sheet["F2"] = 0.620
    sheet["G2"] = 0.775
    sheet["H2"] = 0.2

    sheet["C3"] = "SKU-003"
    sheet["D3"] = "欠損"
    sheet["F3"] = "not-a-number"

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    response = client.post(
        "/api/import/excel",
        files={"file": ("import.xlsx", buffer.getvalue(), "application/vnd.ms-excel")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["imported"] == 1
    assert data["skipped"] == 1
    assert len(data["warnings"]) == 1
