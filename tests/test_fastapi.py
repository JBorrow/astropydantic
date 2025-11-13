"""
Run a test where you try to send our models throuh a FastAPI App.
"""

from astropy import time as t
from astropy import units as u
from astropy.coordinates import ICRS
from pydantic import BaseModel
from pytest import fixture

from astropydantic import (
    AstroPydanticICRS,
    AstroPydanticQuantity,
    AstroPydanticTime,
    AstroPydanticUnit,
)


@fixture
def app():
    from fastapi import FastAPI

    app = FastAPI()

    class AstroPydanticAllModel(BaseModel):
        time: AstroPydanticTime
        quantity: AstroPydanticQuantity
        unit: AstroPydanticUnit
        icrs: AstroPydanticICRS

    @app.post("/ingest/")
    async def ingest_data(item: AstroPydanticAllModel):
        assert isinstance(item.time, t.TimeBase)
        assert isinstance(item.quantity, u.Quantity)
        assert isinstance(item.unit, u.UnitBase)
        assert isinstance(item.icrs, ICRS)

        return item

    return app


@fixture
def test_client(app):
    from fastapi.testclient import TestClient

    return TestClient(app)


def test_fastapi_ingest(test_client):
    payload = {
        "time": "2024-01-01T00:00:00.000000000",
        "quantity": {"value": 10, "unit": "m.s**-1"},
        "unit": "km.s**-1",
        "icrs": {
            "ra": {"value": 180.0, "unit": "deg"},
            "dec": {"value": 45.0, "unit": "deg"},
        },
    }

    response = test_client.post("/ingest/", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["time"] == payload["time"]
    assert data["quantity"] == payload["quantity"]
    assert data["unit"] == payload["unit"]
    assert data["icrs"] == payload["icrs"]
