"""
Test that (de)serialization works
"""

import pytest
from astropy import units as u
from pydantic import BaseModel, ValidationError

from astropydantic import AstroPydanticQuantity


def test_quantity_core():
    class TestModel(BaseModel):
        x: AstroPydanticQuantity

    m = TestModel(x={"value": 1.0, "unit": "m"})

    assert isinstance(m.x, u.Quantity)

    serialized = m.model_dump()
    TestModel.model_validate(serialized)

    json = m.model_dump_json()
    TestModel.model_validate_json(json)


def test_quantity_from_string():
    class TestModel(BaseModel):
        x: AstroPydanticQuantity

    m = TestModel(x="1.0 m")

    assert isinstance(m.x, u.Quantity)

    serialized = m.model_dump()
    TestModel.model_validate(serialized)

    json = m.model_dump_json()
    TestModel.model_validate_json(json)


def test_quantity_obj():
    class TestModel(BaseModel):
        x: AstroPydanticQuantity

    m = TestModel(x=u.Quantity(value=0.1, unit="km"))

    assert isinstance(m.x, u.Quantity)

    serialized = m.model_dump()
    TestModel.model_validate(serialized)

    json = m.model_dump_json()
    TestModel.model_validate_json(json)


def test_quantity_arr():
    class TestModel(BaseModel):
        x: AstroPydanticQuantity

    m = TestModel(x=u.Quantity(value=[0.1, 0.2, 0.3], unit="km"))

    assert isinstance(m.x, u.Quantity)

    serialized = m.model_dump()
    TestModel.model_validate(serialized)

    json = m.model_dump_json()
    TestModel.model_validate_json(json)


def test_quantity_ndarr():
    class TestModel(BaseModel):
        x: AstroPydanticQuantity

    m = TestModel(x=u.Quantity(value=[[0.1, 0.2, 0.3], [0.1, 0.2, 0.3]], unit="km"))

    assert isinstance(m.x, u.Quantity)

    serialized = m.model_dump()
    TestModel.model_validate(serialized)

    json = m.model_dump_json()
    TestModel.model_validate_json(json)


def test_quantity_arr_from_dict():
    class TestModel(BaseModel):
        x: AstroPydanticQuantity

    m = TestModel(x={"value": [0.1, 0.1, 0.2], "unit": "A"})

    assert isinstance(m.x, u.Quantity)

    serialized = m.model_dump()
    TestModel.model_validate(serialized)

    json = m.model_dump_json()
    TestModel.model_validate_json(json)


def test_indexed_units():
    class TestModel(BaseModel):
        x: AstroPydanticQuantity[u.km]

    m = TestModel(x={"value": [0.1, 0.1, 0.2], "unit": "m"})

    assert isinstance(m.x, u.Quantity)

    serialized = m.model_dump()
    TestModel.model_validate(serialized)

    json = m.model_dump_json()
    TestModel.model_validate_json(json)


def test_fail_compare_units():
    class TestModel(BaseModel):
        x: AstroPydanticQuantity[u.g]

    with pytest.raises(ValidationError):
        TestModel(x={"value": [0.1, 0.1, 0.2], "unit": "m"})
