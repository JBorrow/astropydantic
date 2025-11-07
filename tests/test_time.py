"""
Astropy time integration
"""

import datetime

import pytest
from astropy import time as t
from pydantic import BaseModel

from astropydantic import AstroPydanticTime


def test_unit_string():
    class TestModel(BaseModel):
        x: AstroPydanticTime

    m = TestModel(x=t.Time.now())

    assert isinstance(m.x, t.TimeBase)

    serialized = m.model_dump()
    TestModel.model_validate(serialized)

    json = m.model_dump_json()
    TestModel.model_validate_json(json)


def test_unit_datetime(monkeypatch):
    import astropydantic

    monkeypatch.setattr(astropydantic, "TIME_OUTPUT_FORMAT", "datetime")

    class TestModel(BaseModel):
        x: AstroPydanticTime

    m = TestModel(x=datetime.datetime.now())

    assert isinstance(m.x, t.TimeBase)

    serialized = m.model_dump()
    TestModel.model_validate(serialized)

    assert isinstance(serialized["x"], datetime.datetime)

    json = m.model_dump_json()
    TestModel.model_validate_json(json)

    # since TIME_OUTPUT_FORMAT is datetime, also an mjd format datetime should
    # be converted to datetime
    m = TestModel(x=t.Time(58000, format="mjd"))
    serialized = m.model_dump()
    assert isinstance(serialized["x"], datetime.datetime)


def test_unit_mjd(monkeypatch):
    import astropydantic

    monkeypatch.setattr(astropydantic, "TIME_OUTPUT_FORMAT", "mjd")

    class TestModel(BaseModel):
        t: AstroPydanticTime

    now = t.Time.now()
    m = TestModel(t=now)
    serialized = m.model_dump()
    assert serialized["t"] == now.utc.mjd


def test_scale(monkeypatch):
    import astropydantic

    monkeypatch.setattr(astropydantic, "TIME_OUTPUT_SCALE", "tai")

    class TestModel(BaseModel):
        t: AstroPydanticTime

    now = t.Time.now()
    m = TestModel(t=now.utc)
    serialized = m.model_dump()

    now.precision = 9
    assert serialized["t"] == now.tai.isot


def test_unit_disallowed():
    import astropydantic

    astropydantic.TIME_OUTPUT_FORMAT = "asdfasdgasdgas"

    class TestModel(BaseModel):
        x: AstroPydanticTime

    m = TestModel(x=datetime.datetime.now())

    assert isinstance(m.x, t.TimeBase)

    with pytest.raises(ValueError):
        m.model_dump()
