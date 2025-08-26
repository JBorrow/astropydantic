"""
Test that (de)serialization works
"""

from astropy import units as u
from pydantic import BaseModel

from astropydantic import AstroPydanticUnit


def test_unit_string():
    class TestModel(BaseModel):
        x: AstroPydanticUnit

    m = TestModel(x="m")

    assert isinstance(m.x, u.core.UnitBase)

    serialized = m.model_dump()
    TestModel.model_validate(serialized)

    json = m.model_dump_json()
    TestModel.model_validate_json(json)


def test_unit_type():
    class TestModel(BaseModel):
        x: AstroPydanticUnit

    m = TestModel(x=u.m)

    assert isinstance(m.x, u.core.UnitBase)

    serialized = m.model_dump()

    reconstructed = TestModel.model_validate(serialized)

    assert isinstance(reconstructed.x, u.core.UnitBase)

    json = m.model_dump_json()
    TestModel.model_validate_json(json)


def test_unit_string_format():
    class TestModel(BaseModel):
        x: AstroPydanticUnit

    m = TestModel(x=u.km / u.s**2)

    assert m.model_dump_json() == '{"x":"km.s**-2"}'

    import astropydantic

    astropydantic.UNIT_STRING_FORMAT = "fits"

    class TestModel(BaseModel):
        x: AstroPydanticUnit

    m = TestModel(x=u.km / u.s**2)

    assert m.model_dump_json() != '{"x":"km.s**-2"}'
